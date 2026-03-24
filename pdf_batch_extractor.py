import argparse
import logging
import os
import sys
import io
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any, Set

import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image

# --- Logging ---
def setup_logging(log_file: Path, level: str) -> None:
    level_map = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR}
    log_level = level_map.get(level.upper(), logging.INFO)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(log_level)
    for h in list(root.handlers): root.removeHandler(h)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(formatter)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    root.addHandler(fh)
    root.addHandler(ch)

# --- Table Reconstruction Logic ---

class TableReconstructor:
    """Expert table extraction and reconstruction engine."""
    def __init__(self, logger: logging.Logger):
        self.log = logger

    def extract_all(self, pl_page: pdfplumber.page.Page, fitz_page: fitz.Page) -> List[Dict[str, Any]]:
        """
        Main entry point for table extraction.
        Prioritizes Title-Driven Extraction.
        """
        tables = []
        titles = self._detect_table_titles(fitz_page)
        candidates = self._extract_candidates(pl_page, fitz_page)
        
        # Track which candidates are used to avoid duplicates
        used_candidates_idx = set()
        
        for title_info in titles:
            found = False
            self.log.info(f"Processing detected title: {title_info['text']}")
            
            # Pass 1: Match with standard tools (fitz/pdfplumber)
            for i, c in enumerate(candidates):
                if i in used_candidates_idx: continue
                if self._is_near(title_info['bbox'], c['bbox']):
                    if self._is_robust_table(c['rows'], has_title=True):
                        tables.append({'md': self._format_md(c['rows'], title_info['text']), 'bbox': c['bbox']})
                        used_candidates_idx.add(i)
                        found = True
                        self.log.info(f"Found table for {title_info['text']} via standard tools.")
                        break
            
            if not found:
                # Pass 2: Layout search (narrowed to title's horizontal alignment)
                layout_rows = self._search_table_in_region(fitz_page, title_info['bbox'])
                if layout_rows and self._is_robust_table(layout_rows, has_title=True):
                    bbox = (title_info['bbox'][0], title_info['bbox'][3], title_info['bbox'][2], title_info['bbox'][3] + 400)
                    tables.append({'md': self._format_md(layout_rows, title_info['text']), 'bbox': bbox})
                    found = True
                    self.log.info(f"Found table for {title_info['text']} via layout search.")
            
            if not found:
                # Pass 3: OCR (widened region) - CRITICAL for Table 8/9
                ocr_rows = self._extract_from_ocr_region(fitz_page, title_info['bbox'])
                if ocr_rows and self._is_robust_table(ocr_rows, has_title=True):
                    bbox = (title_info['bbox'][0], title_info['bbox'][3], title_info['bbox'][2], title_info['bbox'][3] + 500)
                    tables.append({'md': self._format_md(ocr_rows, title_info['text']), 'bbox': bbox})
                    found = True
                    self.log.info(f"Found table for {title_info['text']} via OCR fallback.")
            
            if not found:
                self.log.warning(f"CRITICAL: Failed to find content for {title_info['text']}")
                    
        # Add standalone high-quality tables (only if they are very robust and structured)
        for i, c in enumerate(candidates):
            if i in used_candidates_idx: continue
            # Standalone tables MUST have high numeric content to be trusted
            if self._is_robust_table(c['rows'], strict=True):
                # Count numeric cells in candidate
                num_cells, tot_cells = 0, 0
                for r in c['rows']:
                    for cell in r:
                        if not cell: continue
                        tot_cells += 1
                        if re.search(r'\d', str(cell)): num_cells += 1
                
                # Standalone table must be >30% numeric to avoid paragraph noise
                if tot_cells > 0 and (num_cells / tot_cells) > 0.3:
                    if not any(self._is_noise_row(r) for r in c['rows']):
                        tables.append({'md': self._format_md(c['rows'], "Table"), 'bbox': c['bbox']})
                    
        return tables

    def _detect_table_titles(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Identify 'TABLE X' titles with high precision."""
        titles = []
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b["type"] == 0:
                text = "".join([s["text"] for l in b["lines"] for s in l["spans"]]).strip()
                # Match TABLE 1, Table 1, Table I, etc.
                if re.match(r'^(TABLE|Table)\s+[IVX\d]+', text, re.IGNORECASE):
                    # Filter out noise that might look like a title but is too long
                    if len(text.split()) < 20:
                        titles.append({'text': text, 'bbox': b['bbox']})
        return titles

    def _extract_candidates(self, pl_page: pdfplumber.page.Page, fitz_page: fitz.Page) -> List[Dict[str, Any]]:
        candidates = []
        try:
            tabs = fitz_page.find_tables()
            for t in tabs.tables: candidates.append({'rows': t.extract(), 'bbox': t.bbox})
        except: pass
        for s in [{"horizontal_strategy": "lines", "vertical_strategy": "lines"}, {"horizontal_strategy": "text", "vertical_strategy": "text"}]:
            try:
                tables = pl_page.extract_tables(table_settings=s)
                for t in tables:
                    if t: candidates.append({'rows': t, 'bbox': (0, 0, 0, 0)})
            except: pass
        return candidates

    def _search_table_in_region(self, page: fitz.Page, title_bbox: Tuple[float, float, float, float]) -> Optional[List[List[str]]]:
        # Narrow horizontal search to title's column
        x0, x1 = max(0, title_bbox[0] - 10), min(page.rect.width, title_bbox[2] + 10)
        rect_below = fitz.Rect(x0, title_bbox[3], x1, title_bbox[3] + 400)
        return self._extract_from_layout(page, rect_below)

    def _extract_from_ocr_region(self, page: fitz.Page, title_bbox: Tuple[float, float, float, float]) -> Optional[List[List[str]]]:
        """
        Extract table data using OCR with dynamic column gap detection.
        Uses x-position clustering to find columns.
        """
        # Search area horizontally aligned with title, vertically below
        x0, x1 = max(0, title_bbox[0] - 100), min(page.rect.width, title_bbox[2] + 100)
        # Increase search height to 800 for larger tables
        rect = fitz.Rect(x0, title_bbox[3], x1, title_bbox[3] + 800)
        
        try:
            for scale in [3, 4]:
                pix = page.get_pixmap(clip=rect, matrix=fitz.Matrix(scale, scale))
                data = pytesseract.image_to_data(Image.open(io.BytesIO(pix.tobytes("png"))), output_type=pytesseract.Output.DICT)
                
                # 1. Row Clustering by Y-coordinates
                rows_dict = {}
                for i in range(len(data['text'])):
                    txt = data['text'][i].strip()
                    if not txt: continue
                    y = round(data['top'][i] / (scale * 1.5)) * (scale * 1.5)
                    if y not in rows_dict: rows_dict[y] = []
                    rows_dict[y].append({
                        'text': txt, 
                        'x0': data['left'][i], 
                        'x1': data['left'][i] + data['width'][i],
                        'y': data['top'][i]
                    })
                
                if not rows_dict: continue
                
                # 2. Dynamic Column Gap Detection using X-clustering
                all_words = []
                for y in rows_dict: all_words.extend(rows_dict[y])
                
                # Cluster x-starts to find potential column origins
                x_starts = sorted([w['x0'] for w in all_words])
                clusters = []
                if x_starts:
                    curr_cluster = [x_starts[0]]
                    for j in range(1, len(x_starts)):
                        # More sensitive clustering: 10 pixels instead of 15
                        if x_starts[j] - x_starts[j-1] < (8 * scale): 
                            curr_cluster.append(x_starts[j])
                        else:
                            clusters.append(sum(curr_cluster) / len(curr_cluster))
                            curr_cluster = [x_starts[j]]
                    clusters.append(sum(curr_cluster) / len(curr_cluster))
                
                # 3. Reconstruct rows using detected column clusters
                final_rows = []
                for y in sorted(rows_dict.keys()):
                    line_words = sorted(rows_dict[y], key=lambda x: x['x0'])
                    row_cells = [[] for _ in range(len(clusters))]
                    
                    for w in line_words:
                        # Find closest cluster
                        best_idx = 0
                        min_dist = float('inf')
                        for idx, c_x in enumerate(clusters):
                            dist = abs(w['x0'] - c_x)
                            if dist < min_dist:
                                min_dist = dist
                                best_idx = idx
                        row_cells[best_idx].append(w['text'])
                    
                    final_rows.append([" ".join(c) for c in row_cells])
                
                if self._is_robust_table(final_rows):
                    return final_rows
            return None
        except Exception as e:
            self.log.debug(f"OCR Extraction error: {e}")
            return None

    def _extract_from_layout(self, page: fitz.Page, rect: fitz.Rect) -> Optional[List[List[str]]]:
        """Layout-aware extraction with dynamic gutter detection."""
        words = page.get_text("words", clip=rect)
        if not words or len(words) < 4: return None
        
        # 1. Row grouping by Y
        words.sort(key=lambda w: (w[1], w[0]))
        rows_data, curr_y, curr_row = [], -1, []
        for w in words:
            if curr_y == -1 or abs(w[1] - curr_y) > 4:
                if curr_row: rows_data.append(sorted(curr_row, key=lambda x: x[0]))
                curr_row, curr_y = [w], w[1]
            else: curr_row.append(w)
        if curr_row: rows_data.append(sorted(curr_row, key=lambda x: x[0]))
        
        # 2. Dynamic Gutter Detection
        # Collect all horizontal gaps between words
        gaps = []
        for rw in rows_data:
            for i in range(1, len(rw)):
                gap = rw[i][0] - rw[i-1][2]
                if gap > 0: gaps.append(gap)
        
        if not gaps: return None
        # Gutters are typically significantly larger than word spaces
        avg_gap = sum(gaps) / len(gaps)
        gutter_threshold = max(10, avg_gap * 2.5)
        
        # 3. Reconstruct rows
        final_rows = []
        for rw in rows_data:
            cells, curr_text = [], [rw[0][4]]
            for i in range(1, len(rw)):
                if rw[i][0] - rw[i-1][2] > gutter_threshold:
                    cells.append(" ".join(curr_text))
                    curr_text = [rw[i][4]]
                else:
                    curr_text.append(rw[i][4])
            cells.append(" ".join(curr_text))
            final_rows.append(cells)
            
        return final_rows

    def _is_noise_row(self, row: List[str]) -> bool:
        """Reject rows that look like paragraph text or academic headers."""
        non_empty = [str(c).strip() for c in row if c and str(c).strip()]
        if not non_empty: return False
        
        text = " ".join(non_empty)
        text_upper = text.upper()
        
        # 1. Academic Keywords Rejection (only if it's the dominant content)
        noise_keywords = ["ABSTRACT", "INTRODUCTION", "FIGURE", "INDEX TERMS", "ACKNOWLEDGMENT", "REFERENCES", "IEEE ACCESS", "VOLUME", "BIOGRAPHY"]
        # If the row is just a noise keyword or starts with one followed by a lot of text
        for kw in noise_keywords:
            if text_upper == kw or text_upper.startswith(kw + " "):
                if len(text.split()) > 5:
                    return True
        
        # 2. Reference Pattern (e.g., [1], [2], [15])
        if re.match(r'^\[\d+\]', text):
            return True
            
        # 3. Paragraph/Sentence Detection
        # Tables rarely have cells with more than 10 words. 
        # If any cell is very long, it's likely a paragraph.
        for cell in non_empty:
            if len(cell.split()) > 15:
                return True
            
        # 3. Section Titles (e.g., I. INTRODUCTION, II. RELATED WORK)
        if re.match(r'^[I|V|X]+\.\s+[A-Z\s]+$', text_upper):
            return True
            
        return False

    def _is_robust_table(self, rows: List[List[str]], strict: bool = False, has_title: bool = False) -> bool:
        """
        Comprehensive table validation logic.
        """
        if not rows: return False
        
        # 1. Basic Structure Check
        valid_rows = []
        for r in rows:
            if not r: continue
            if self._is_noise_row(r): continue
            if any(str(c).strip() for c in r if c):
                valid_rows.append([str(c).strip() if c else "" for c in r])
        
        if len(valid_rows) < 2: return False
        
        # 2. Column Consistency Check
        col_counts = [len(r) for r in valid_rows if any(c for c in r)]
        if not col_counts: return False
        
        max_cols = max(col_counts)
        if max_cols < 2: return False
        
        from collections import Counter
        counts = Counter(col_counts)
        most_common_count, freq = counts.most_common(1)[0]
        consistency = freq / len(valid_rows)
        
        # If we have a title, we can be slightly more lenient on consistency (e.g. 50%)
        threshold = 0.5 if has_title else 0.7
        if consistency < threshold:
            return False
            
        # 3. Content Validation (Numbers/Categorical Pattern)
        numeric_cells = 0
        total_cells = 0
        long_cell_found = False
        
        for r in valid_rows:
            for c in r:
                if not c: continue
                total_cells += 1
                words = c.split()
                
                if len(words) > 12: # Strict paragraph rejection
                    long_cell_found = True
                    break
                
                if re.search(r'\d', c):
                    numeric_cells += 1
            if long_cell_found: break
            
        if long_cell_found: return False
        if total_cells == 0: return False
        
        # A real table usually has numbers or short repeated labels
        numeric_ratio = numeric_cells / total_cells
        # If no numeric content, check for categorical (short cells)
        if numeric_ratio < 0.1:
            avg_word_count = sum(len(str(c).split()) for r in valid_rows for c in r if c) / total_cells
            if avg_word_count > 4: # If cells are mostly words and not short, it's likely not a table
                return False
            
        return True

    def _is_near(self, title_bbox: Tuple[float, float, float, float], table_bbox: Tuple[float, float, float, float]) -> bool:
        if table_bbox == (0, 0, 0, 0): return False
        v_dist = table_bbox[1] - title_bbox[3]
        if -10 < v_dist < 100:
            overlap = min(title_bbox[2], table_bbox[2]) - max(title_bbox[0], table_bbox[0])
            return overlap > -20
        return False

    def _format_md(self, rows: List[List[Optional[str]]], title: str) -> str:
        rows = [r for r in rows if any(c and c.strip() for c in r)]
        if not rows: return ""
        max_cols = max(len(r) for r in rows)
        cleaned = []
        for r in rows:
            row = [(c or "").strip().replace("\n", " ") for c in r]
            while len(row) < max_cols: row.append("")
            cleaned.append(row)
        widths = [max(len(row[i]) for row in cleaned) for i in range(max_cols)]
        res = [f"\n[Table: {title}]\n"]
        res.append("| " + " | ".join(cleaned[0][i].ljust(widths[i]) for i in range(max_cols)) + " |")
        res.append("|-" + "-|-".join("-" * widths[i] for i in range(max_cols)) + "-|")
        for r in cleaned[1:]:
            res.append("| " + " | ".join(r[i].ljust(widths[i]) for i in range(max_cols)) + " |")
        return "\n".join(res)

class TextReconstructor:
    def __init__(self, logger): self.log = logger
    def clean(self, text):
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
        lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
        if not lines: return ""
        merged, current = [], lines[0]
        for next_line in lines[1:]:
            if current and not current[-1] in ".!?:;\"'”" and not re.match(r'^([A-Z\d]+\)|[I|V|X]+\.|[A-Z]\.|\*|\-)\s+', next_line) and not next_line.isupper():
                current += " " + next_line
            else: merged.append(current); current = next_line
        merged.append(current)
        return re.sub(r' +', ' ', "\n\n".join(merged)).strip()

class FigureReconstructor:
    def __init__(self, logger): self.log = logger
    def extract(self, page):
        res = []
        try:
            for i, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                rects = page.get_image_rects(xref)
                if not rects: continue
                rect = rects[0]
                cap = page.get_text("text", clip=fitz.Rect(rect.x0-20, rect.y1, rect.x1+20, rect.y1+60)).strip() or page.get_text("text", clip=fitz.Rect(rect.x0-20, rect.y0-60, rect.x1+20, rect.y0)).strip()
                title = cap if cap else f"Figure {i+1}"
                img_data = page.parent.extract_image(xref)["image"]
                if len(img_data) < 3000: continue
                desc = f"\n[Figure: {title}]\n"
                try:
                    text = pytesseract.image_to_string(Image.open(io.BytesIO(img_data)).convert('RGB')).strip()
                    if text: desc += "\n".join([f"* {ln.strip()}" for ln in text.split('\n') if len(ln.strip()) > 2])
                except: pass
                res.append(desc)
        except: pass
        return "\n".join(res)

class LayoutEngine:
    def __init__(self, logger): self.log = logger
    def extract_ordered_blocks(self, page):
        blocks = [b for b in page.get_text("dict")["blocks"] if b["type"] == 0]
        if not blocks: return []
        mid = page.rect.width / 2
        left = sorted([b for b in blocks if b["bbox"][2] <= mid + 20], key=lambda b: b["bbox"][1])
        right = sorted([b for b in blocks if b["bbox"][0] >= mid - 20], key=lambda b: b["bbox"][1])
        center = sorted([b for b in blocks if b not in left and b not in right], key=lambda b: b["bbox"][1])
        return center + left + right
    def block_to_text(self, block):
        return "\n".join(["".join([s["text"] for s in l["spans"]]) for l in block["lines"]]).strip()

class DocumentReconstructor:
    def __init__(self, pdf_path, output_dir):
        self.pdf_path, self.output_dir, self.name = pdf_path, output_dir, pdf_path.stem
        self.log = logging.getLogger(self.name)
        self.layout_engine = LayoutEngine(self.log)
        self.text_engine = TextReconstructor(self.log)
        self.table_engine = TableReconstructor(self.log)
        self.figure_engine = FigureReconstructor(self.log)
    def run(self) -> bool:
        self.log.info(f"--- RECONSTRUCTING: {self.pdf_path.name} ---")
        full_markdown = []
        try:
            with fitz.open(self.pdf_path) as doc, pdfplumber.open(self.pdf_path) as pl:
                for i, (fitz_page, pl_page) in enumerate(zip(doc, pl.pages)):
                    tables = self.table_engine.extract_all(pl_page, fitz_page)
                    table_bboxes = [t['bbox'] for t in tables if t['bbox'] != (0,0,0,0)]
                    ordered_blocks = self.layout_engine.extract_ordered_blocks(fitz_page)
                    page_text_raw = ""
                    for block in ordered_blocks:
                        if any(self._is_inside(block['bbox'], t_bbox) for t_bbox in table_bboxes): continue
                        if self._is_noise(block, fitz_page.rect.height): continue
                        page_text_raw += self.layout_engine.block_to_text(block) + "\n"
                    cleaned_text = self.text_engine.clean(page_text_raw)
                    rebuilt_text = self._apply_hierarchy(cleaned_text)
                    page_md = []
                    if rebuilt_text: page_md.append(rebuilt_text)
                    for t in tables: page_md.append(t['md'])
                    figures = self.figure_engine.extract(fitz_page)
                    if figures: page_md.append(figures)
                    if page_md: full_markdown.append("\n\n".join(page_md))
            final_md = re.sub(r'([a-z,])\s*\n\n\s*([a-z])', r'\1 \2', "\n\n".join(full_markdown))
            self.output_dir.mkdir(parents=True, exist_ok=True)
            (self.output_dir / f"{self.name}.md").write_text(final_md, encoding="utf-8")
            self.log.info(f"RECONSTRUCTION COMPLETE: {self.name}.md")
            return True
        except Exception as e:
            self.log.error(f"FAILED: {e}", exc_info=True); return False
    def _is_inside(self, block_bbox, table_bbox):
        return (block_bbox[0] >= table_bbox[0] - 5 and block_bbox[1] >= table_bbox[1] - 5 and
                block_bbox[2] <= table_bbox[2] + 5 and block_bbox[3] <= table_bbox[3] + 5)
    def _is_noise(self, block, page_height):
        bbox, text = block["bbox"], "".join([s["text"] for l in block["lines"] for s in l["spans"]]).strip()
        if not text or re.match(r'^\d+$', text) or "VOLUME" in text or "IEEE ACCESS" in text.upper(): return True
        if (bbox[1] < 40 or bbox[3] > page_height - 40) and len(text) < 100: return True
        return False
    def _apply_hierarchy(self, text):
        lines, res = text.split('\n\n'), []
        for ln in lines:
            ln = ln.strip()
            if not ln: continue
            if re.match(r'^[I|V|X]+\.\s+[A-Z\s]+$', ln): res.append(f"## {ln}")
            elif re.match(r'^[A-Z]\.\s+[A-Z]', ln): res.append(f"### {ln}")
            elif ln.upper() in ["ABSTRACT", "INDEX TERMS"]: res.append(f"## {ln.upper()}")
            elif re.match(r'^\d+\)\s+[A-Z]', ln): res.append(f"#### {ln}")
            else: res.append(ln)
        return "\n\n".join(res)

def main():
    parser = argparse.ArgumentParser(description="Expert Table Correction Engine")
    parser.add_argument("--input-dir", default="pdfs")
    parser.add_argument("--output-dir", default="reconstructed_md_expert_final")
    args = parser.parse_args()
    setup_logging(Path("reconstruction.log"), "INFO")
    input_dir, output_dir = Path(args.input_dir).resolve(), Path(args.output_dir).resolve()
    if input_dir.exists():
        for p in list(input_dir.glob("*.pdf")): DocumentReconstructor(p, output_dir).run()

if __name__ == "__main__": main()
