"""
PDF Batch Table Extractor — End-of-Page Table Appending with Vision AI
================================================================
Focus: Extracts continuous 2-column text first to ensure smooth reading,
       then uses LLaMA Vision AI to scan tables and appends them cleanly 
       at the bottom of each page.
"""

import fitz
import pdfplumber
import pytesseract
from PIL import Image
import re
import io
import logging
from collections import Counter
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

# Attempt to import your custom Vision AI client
try:
    import llama_client
    HAS_LLAMA = True
except ImportError:
    HAS_LLAMA = False

# ══════════════════════════════════════════════════════════════
#  SECTION 0 ── CONFIGURATION & LOGGING
# ══════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class Config:
    """Central configuration for extraction parameters."""
    # 🌟 TURNED ON: Now routes tables to llama_client.py 🌟
    USE_VISION_AI = True 
    
    OCR_SCALE = 3.0
    MIN_OCR_CONFIDENCE = 20
    TABLE_Y_GAP = 10
    TABLE_X_GAP = 25
    HEADER_SCAN_LIMIT = 4
    TEXT_TOP_MARGIN = 0.06
    TEXT_BOTTOM_MARGIN = 0.92
    LEFT_COLUMN_MAX_X = 0.45
    RIGHT_COLUMN_MIN_X = 0.55
    DEFAULT_TABLE_HEIGHT = 400
    UNIT_PATTERN = re.compile(
        r'^\(?(percent|%|MB/s|GB/s|ms|s|binary|seconds?|KB|KB/s|per|cent)\)?$', re.I)
    STOP_WORDS = {"the","this","that","with","and","for","are","was",
                  "were","its","our","from","has","have","been","which",
                  "these","also","both","each","such"}


# ══════════════════════════════════════════════════════════════
#  SECTION 1 ── STRUCTURAL VALIDATOR
# ══════════════════════════════════════════════════════════════

class StructuralValidator:
    def _looks_like_sentence(self, row: list) -> bool:
        tokens = [str(c).strip() for c in row if str(c).strip()]
        if len(tokens) < 3: return False
        alpha_ratio = sum(1 for t in tokens if re.fullmatch(r'[A-Za-z\-]+', t)) / len(tokens)
        has_digit   = any(re.search(r'\d', t) for t in tokens)
        stop_hit    = sum(1 for t in tokens if t.lower() in Config.STOP_WORDS)
        if alpha_ratio > 0.85 and not has_digit and stop_hit >= 2: return True
        if alpha_ratio > 0.90 and not has_digit and len(tokens) >= 5: return True
        return False

    def _numeric_density(self, rows: list) -> float:
        cells = [str(c) for row in rows for c in row if str(c).strip()]
        if not cells: return 0.0
        return sum(1 for c in cells if re.search(r'\d', c)) / len(cells)

    def _col_count_consistency(self, rows: list) -> float:
        lengths = [len(r) for r in rows]
        if not lengths: return 0.0
        return sum(1 for l in lengths if l == Counter(lengths).most_common(1)[0][0]) / len(lengths)

    def _has_repeated_structure(self, rows: list) -> bool:
        patterns = [tuple(bool(str(c).strip()) for c in r) for r in rows]
        if not patterns: return False
        return Counter(patterns).most_common(1)[0][1] / len(patterns) >= 0.55

    def is_valid(self, rows: list) -> bool:
        if not rows or len(rows) < 2: return False
        data_rows = rows[1:] if len(rows) > 1 else rows
        if sum(1 for r in data_rows if self._looks_like_sentence(r)) / len(data_rows) > 0.5: return False
        if self._numeric_density(rows) < 0.10: return False
        if self._col_count_consistency(rows) < 0.55: return False
        if not self._has_repeated_structure(rows): return False
        if Counter(len(r) for r in rows).most_common(1)[0][0] < 2: return False
        return True

class HeaderReconstructor:
    def _is_header_row(self, row: list) -> bool:
        tokens = [str(c).strip() for c in row if str(c).strip()]
        if not tokens: return False
        alpha = sum(1 for t in tokens if re.search(r'[A-Za-z]', t))
        digits_only = sum(1 for t in tokens if re.fullmatch(r'[\d.+-]+', t))
        return alpha / len(tokens) >= 0.7 and digits_only == 0

    def detect_and_merge(self, rows: list, n_cols: int):
        if not rows: return [], []
        header_rows, data_start = [], 0
        for idx, row in enumerate(rows[:Config.HEADER_SCAN_LIMIT]):
            if self._is_header_row(row):
                header_rows.append(row)
                data_start = idx + 1
            else: break
        if not header_rows: header_rows, data_start = [rows[0]], 1
        for hr in header_rows:
            while len(hr) < n_cols: hr.append("")
        merged = [" ".join([str(hr[ci]).strip() for hr in header_rows if ci < len(hr) and str(hr[ci]).strip()]).strip() for ci in range(n_cols)]
        return merged, rows[data_start:]

class ColumnAligner:
    def align(self, rows: list):
        if not rows: return 0, []
        lengths = [len(r) for r in rows if r]
        n_cols = Counter(lengths).most_common(1)[0][0] if lengths else 1
        aligned = []
        for row in rows:
            r = list(row)
            if len(r) < n_cols: r += [""] * (n_cols - len(r))
            elif len(r) > n_cols: r = r[:n_cols-1] + [" ".join(str(x) for x in r[n_cols-1:] if x)]
            aligned.append(r)
        return n_cols, aligned

class OCRTableReconstructor:
    def reconstruct(self, ocr_data: dict) -> list:
        words = []
        conf_list = ocr_data.get("conf", [0] * len(ocr_data["text"]))
        for i, txt in enumerate(ocr_data["text"]):
            if not txt.strip() or int(conf_list[i] if conf_list[i] != '-1' else 0) < Config.MIN_OCR_CONFIDENCE: continue
            words.append({"text": txt.strip(), "left": ocr_data["left"][i], "top": ocr_data["top"][i]})
        if not words: return []

        sorted_tops = sorted(set(w["top"] for w in words))
        y_buckets, current = {sorted_tops[0]: sorted_tops[0]}, sorted_tops[0]
        for y in sorted_tops[1:]:
            if y - current > Config.TABLE_Y_GAP: current = y
            y_buckets[y] = current
        
        row_groups = {}
        for w in words: row_groups.setdefault(y_buckets[w["top"]], []).append(w)
        for k in row_groups: row_groups[k].sort(key=lambda w: w["left"])

        sorted_lefts = sorted(set(w["left"] for w in words))
        col_bounds = [sorted_lefts[0]]
        for x in sorted_lefts[1:]:
            if x - col_bounds[-1] > Config.TABLE_X_GAP: col_bounds.append(x)
        
        if len(col_bounds) < 2: return [[" ".join(w["text"] for w in row_groups[rk])] for rk in sorted(row_groups)]

        result = []
        for rk in sorted(row_groups):
            grid_row = {c: [] for c in range(len(col_bounds))}
            for w in row_groups[rk]:
                best, best_dist = 0, abs(w["left"] - col_bounds[0])
                for i, bx in enumerate(col_bounds[1:], 1):
                    if abs(w["left"] - bx) < best_dist: best_dist, best = abs(w["left"] - bx), i
                grid_row[best].append(w["text"])
            result.append([" ".join(grid_row[c]) for c in range(len(col_bounds))])
        return result

class PdfplumberCleaner:
    def clean(self, raw_table: list) -> list:
        rows = [["" if c is None else str(c).strip() for c in row] for row in raw_table]
        rows = [r for r in rows if r and not any(k in " ".join(r).lower() for k in ["figure", "doi", "http", "©", "abstract"])]
        if len(rows) >= 2:
            result = [rows[0]]
            for row in rows[1:]:
                non_empty = [c for c in row if c]
                if non_empty and all(Config.UNIT_PATTERN.match(c) for c in non_empty):
                    for i, cell in enumerate(row):
                        if cell and i < len(result[-1]): result[-1][i] = (result[-1][i] + " " + cell).strip()
                else: result.append(row)
            return result
        return rows

class TableEngine:
    def __init__(self):
        self.validator  = StructuralValidator()
        self.header_rec = HeaderReconstructor()
        self.aligner    = ColumnAligner()
        self.ocr_rec    = OCRTableReconstructor()
        self.pl_cleaner = PdfplumberCleaner()

    def process_pdfplumber(self, raw_table: list):
        rows = self.pl_cleaner.clean(raw_table)
        if not rows: return None
        n_cols, rows = self.aligner.align(rows)
        if n_cols < 2 or not self.validator.is_valid(rows): return None
        header, data = self.header_rec.detect_and_merge(rows, n_cols)
        return [header] + data if data else None

    def process_ocr(self, page, rect):
        raw_data = self._render_and_ocr(page, rect)
        if not raw_data: return None
        rows = self.ocr_rec.reconstruct(raw_data)
        if not rows: return None
        n_cols, rows = self.aligner.align(rows)
        rows = [r for r in rows if r]
        if n_cols < 2 or not self.validator.is_valid(rows): return None
        header, data = self.header_rec.detect_and_merge(rows, n_cols)
        return [header] + data if data else None

    def _render_and_ocr(self, page, rect):
        if rect is None: return None
        clipped = fitz.Rect(max(rect.x0, page.rect.x0), max(rect.y0, page.rect.y0),
                            min(rect.x1, page.rect.x1), min(rect.y1, page.rect.y1))
        if clipped.is_empty or clipped.width < 10 or clipped.height < 10: return None
        try:
            pix = page.get_pixmap(matrix=fitz.Matrix(Config.OCR_SCALE, Config.OCR_SCALE), clip=clipped)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            return pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config='--psm 6')
        except Exception as e:
            logger.debug(f"OCR Error: {e}")
            return None

    def to_markdown(self, grid: list) -> str:
        if not grid: return ""
        n_cols = max(len(r) for r in grid)
        padded = [ [str(c).replace('\n', ' ').strip() for c in r] + [""] * (n_cols - len(r)) for r in grid ]
        col_widths = [max(len(padded[ri][ci]) for ri in range(len(padded))) for ci in range(n_cols)]
        def fmt(row): return "| " + " | ".join(row[ci].ljust(col_widths[ci]) for ci in range(n_cols)) + " |"
        sep = "|" + "|".join("-" * (col_widths[ci] + 2) for ci in range(n_cols)) + "|"
        return "\n".join([fmt(padded[0]), sep] + [fmt(r) for r in padded[1:]])


class PDFProcessor:
    def __init__(self, path):
        self.doc    = fitz.open(path)
        self.path   = path
        self.engine = TableEngine()

    def extract_clean_text(self, page) -> str:
        clean_blocks = [
            b for b in page.get_text("blocks")
            if b[6] == 0 and not (b[1] < page.rect.height * Config.TEXT_TOP_MARGIN or b[3] > page.rect.height * Config.TEXT_BOTTOM_MARGIN)
        ]
        clean_blocks.sort(key=lambda b: (0 if b[0] < page.rect.width * 0.5 else 1, b[1]))
        
        text_output = []
        for b in clean_blocks:
            cleaned = re.sub(r'-\n', '', b[4]).replace('\n', ' ').strip()
            if cleaned: text_output.append(re.sub(r'\s+', ' ', cleaned))
        return "\n\n".join(text_output)

    def find_captions(self, page) -> list:
        captions = []
        pattern  = re.compile(r'^(TABLE|Table)\s+\d+', re.I)
        for b in page.get_text("dict")["blocks"]:
            if "lines" not in b: continue
            for line in b["lines"]:
                for span in line["spans"]:
                    if pattern.match(span["text"].strip()):
                        captions.append({"text": span["text"].strip(), "bbox": span["bbox"]})
        return sorted(captions, key=lambda x: x["bbox"][1])

    def _build_rect(self, page_idx, cap_bbox, next_cap_bbox=None):
        page = self.doc[page_idx]
        mid_x = (cap_bbox[0] + cap_bbox[2]) / 2
        
        x0 = 0 if mid_x < page.rect.width * Config.LEFT_COLUMN_MAX_X else (page.rect.width * Config.LEFT_COLUMN_MAX_X if mid_x > page.rect.width * Config.RIGHT_COLUMN_MIN_X else 0)
        x1 = page.rect.width * Config.RIGHT_COLUMN_MIN_X if mid_x < page.rect.width * Config.LEFT_COLUMN_MAX_X else page.rect.width
        y0 = cap_bbox[3] + 2 
        
        if next_cap_bbox and next_cap_bbox[1] > y0 + 20 and abs(next_cap_bbox[0] - cap_bbox[0]) < 100:
            y1 = next_cap_bbox[1] - 5
        else:
            y1 = min(y0 + Config.DEFAULT_TABLE_HEIGHT, page.rect.height * Config.TEXT_BOTTOM_MARGIN)

        if y0 >= y1 or y0 >= page.rect.height: return None
        return fitz.Rect(x0, y0, x1, y1)

    def _pl_tables_in_region(self, pl_page, rect):
        ts = {
            "vertical_strategy": "text", 
            "horizontal_strategy": "text",
            "intersection_y_tolerance": 10
        }
        if rect is None: return pl_page.extract_tables(table_settings=ts)
        try: return pl_page.crop((rect.x0, rect.y0, rect.x1, rect.y1)).extract_tables(table_settings=ts)
        except Exception: return pl_page.extract_tables(table_settings=ts)

    def process(self) -> str:
        output = []
        with pdfplumber.open(self.path) as pl:
            for page_idx, fitz_page in enumerate(self.doc):
                
                # 1. First, append all the clean text from the page
                output.append(f"## Page {page_idx + 1}\n")
                output.append(self.extract_clean_text(fitz_page))

                # 2. Collect tables for this page into a separate list
                captions = self.find_captions(fitz_page)
                page_tables = []

                for j, cap in enumerate(captions):
                    title = cap["text"]
                    next_bbox = captions[j+1]["bbox"] if j+1 < len(captions) else None
                    rect = self._build_rect(page_idx, cap["bbox"], next_bbox)
                    
                    table_content = None

                    # Path A: Vision AI "Scan"
                    if Config.USE_VISION_AI and HAS_LLAMA and rect:
                        try:
                            logger.info(f"Scanning {title} with Vision AI...")
                            pix = fitz_page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=rect)
                            
                            # Passes the screenshot directly to the new llama_client function
                            ai_markdown = llama_client.image_to_markdown(pix.tobytes("png"))
                            if ai_markdown:
                                table_content = ai_markdown
                        except Exception as e:
                            logger.error(f"Vision AI failed for {title}: {e}")

                    # Path B: Fallback OCR / rule-based scan
                    if not table_content:
                        grid = None
                        if rect: grid = self.engine.process_ocr(fitz_page, rect)
                            
                        if not grid:
                            for raw_t in self._pl_tables_in_region(pl.pages[page_idx], rect):
                                if candidate := self.engine.process_pdfplumber(raw_t):
                                    grid = candidate
                                    break

                        if grid:
                            table_content = self.engine.to_markdown(grid)

                    # Store the result
                    if table_content:
                        page_tables.append({'caption': title, 'content': table_content})
                    else:
                        page_tables.append({'caption': title, 'content': f"[Could not reconstruct table data]"})

                # 3. Append the tables cleanly at the bottom of the page
                if page_tables:
                    output.append("\n\n=== DETECTED IMAGE-BASED TABLES ===")
                    for t in page_tables:
                        output.append(f"\n**Caption:** {t['caption']}\n")
                        output.append(t['content'])
                        output.append("\n===================================")
                        
                output.append("\n---\n")
                
        return "\n".join(output)

# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════

def process_single_pdf(pdf_path: Path, output_dir: Path):
    start_time = time.time()
    try:
        processor = PDFProcessor(pdf_path)
        result = processor.process()
        out_file = output_dir / f"{pdf_path.stem}.md"
        out_file.write_text(result, encoding="utf-8")
        duration = time.time() - start_time
        logger.info(f"  SUCCESS {pdf_path.name} ({duration:.1f}s) -> {out_file.name}")
        return pdf_path.name, True, duration
    except Exception as e:
        logger.error(f"  FAILED {pdf_path.name}: {e}")
        return pdf_path.name, False, 0

def main():
    input_dir, output_dir = Path("pdfs"), Path("output")
    output_dir.mkdir(exist_ok=True)
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in ./pdfs/")
        return

    logger.info(f"Starting batch processing with {min(len(pdf_files), 4)} workers...")
    total_start_time = time.time()
    results = []
    
    with ProcessPoolExecutor(max_workers=min(len(pdf_files), 4)) as executor:
        futures = {executor.submit(process_single_pdf, pdf, output_dir): pdf for pdf in pdf_files}
        for future in as_completed(futures): results.append(future.result())

    success_count = sum(1 for _, success, _ in results if success)
    logger.info(f"Batch Processing Complete! Processed {success_count}/{len(pdf_files)} files in {time.time() - total_start_time:.2f}s.")

if __name__ == "__main__":
    main()