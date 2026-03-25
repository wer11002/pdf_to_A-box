<div align="center">

# PDF Batch Table Extractor

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Dependencies](https://img.shields.io/badge/Deps-PyMuPDF%20%7C%20pdfplumber%20%7C%20pytesseract%20%7C%20Pillow%20%7C%20requests%20%7C%20python--dotenv-6A5ACD)
![Build](https://img.shields.io/badge/Build-Manual-green)

Batch processor that reconstructs multi-column academic PDFs into clean Markdown, with table extraction via Vision AI and OCR fallbacks.

</div>

---

## Table of Contents

- [Part 1 – pdf_batch_extractor_new.py Documentation](#part-1--pdf_batch_extractor_newpy-documentation)
  - [Purpose and Features](#purpose-and-features)
  - [Prerequisites and Installation](#prerequisites-and-installation)
  - [How to Run](#how-to-run)
  - [Configuration Options](#configuration-options)
  - [Input and Output](#input-and-output)
  - [Code Examples](#code-examples)
  - [Troubleshooting](#troubleshooting)
- [Part 2 – Workflow / Flow Documentation](#part-2--workflow--flow-documentation)
  - [Process Flow](#process-flow)
  - [Component Interaction](#component-interaction)
  - [ASCII Workflow Diagram](#ascii-workflow-diagram)
  - [Timing and Resources](#timing-and-resources)
- [Part 3 – Usage Order / Sequence](#part-3--usage-order--sequence)
  - [Pre-Execution Checklist](#pre-execution-checklist)
  - [Step-by-Step Execution](#step-by-step-execution)
  - [Verification Steps](#verification-steps)
  - [Cleanup \& Post-Processing](#cleanup--post-processing)
- [Contribution Guidelines](#contribution-guidelines)
- [License](#license)

---

## Part 1 – pdf_batch_extractor_new.py Documentation

### Purpose and Features

The core entry point is [pdf_batch_extractor_new.py](file:///Users/guide/workspace/univercity/year3_sem2/new_end_project/pdf_batch_extractor_new.py). Its goal is to reconstruct multi-column academic PDFs into readable Markdown while appending properly formatted tables at the end of each page.

Key features:
- Parallel batch processing of all PDFs under a folder.
- Clean, column-aware text extraction (left-to-right column order).
- Table detection via “TABLE X” captions and bounding-box heuristics.
- Multi-pass table reconstruction:
  - Vision AI (LLaMA): image → Markdown table (optional).
  - OCR (Tesseract) clustering by X/Y for column/row alignment.
  - pdfplumber fallback for vector-based tables.
- Structural validation, header merging, and column alignment.
- A summary block at the end of each output listing table counts and errors.

Relevant modules/classes inside the extractor:
- `PDFProcessor` – drives per-page logic, text cleaning, table ROI determination, and orchestration.
- `TableEngine` – validates/cleans/aligns tables and renders Markdown.
- `OCRTableReconstructor`, `ColumnAligner`, `HeaderReconstructor`, `StructuralValidator` – specialized utilities for robust table reconstruction.
- Vision AI client: [llama_client.py](file:///Users/guide/workspace/univercity/year3_sem2/new_end_project/llama_client.py) (OpenRouter/LLM integration).


### Prerequisites and Installation

System requirements:
- macOS/Linux/Windows
- Python 3.9+
- Tesseract OCR runtime installed

Install Tesseract:
- macOS (Homebrew):

```bash
brew install tesseract
```

- Ubuntu/Debian:

```bash
sudo apt update && sudo apt install -y tesseract-ocr
```

Python dependencies (via pip):

```bash
pip3 install PyMuPDF pdfplumber pytesseract Pillow requests python-dotenv pypdf
```

Vision AI (optional):
- Create a `.env` at project root with:

```bash
OPENROUTER_API_KEY=sk-or-...
```


### How to Run

1) Place input files in the default input directory:

```
./pdfs/
  ├─ paper1.pdf
  ├─ paper2.pdf
  └─ paper3.pdf
```

2) Run the batch extractor:

```bash
python3 pdf_batch_extractor_new.py
```

Outputs will be written to:

```
./output/
  ├─ paper1.md
  ├─ paper2.md
  └─ paper3.md
```

To enable Vision AI table extraction, ensure your `.env` is configured and set the `Config.USE_VISION_AI = True` inside [pdf_batch_extractor_new.py](file:///Users/guide/workspace/univercity/year3_sem2/new_end_project/pdf_batch_extractor_new.py#L38-L60) or use the already enabled setting if present.


### Configuration Options

Edit the `Config` class in [pdf_batch_extractor_new.py](file:///Users/guide/workspace/univercity/year3_sem2/new_end_project/pdf_batch_extractor_new.py#L38-L60):
- `USE_VISION_AI`: route tables to Vision AI before OCR/pdfplumber.
- `OCR_SCALE`: DPI scaling for OCR rendering.
- `MIN_OCR_CONFIDENCE`: minimum per-word OCR confidence.
- `TABLE_Y_GAP`, `TABLE_X_GAP`: clustering thresholds for Y/rows and X/columns.
- `HEADER_SCAN_LIMIT`: maximum number of header rows to merge.
- `TEXT_TOP_MARGIN`, `TEXT_BOTTOM_MARGIN`: exclusion margins for headers/footers.
- `DEFAULT_TABLE_HEIGHT`: max table ROI height below a caption.
- `LEFT_COLUMN_MAX_X`, `RIGHT_COLUMN_MIN_X`: 2-column layout heuristics.

Vision AI client: see [llama_client.py](file:///Users/guide/workspace/univercity/year3_sem2/new_end_project/llama_client.py) for API URL, model names, and request payloads.


### Input and Output

- Input: PDFs placed in the `pdfs/` directory (default). No command-line flags are required.
- Output: One Markdown file per input PDF under `output/`. Each page begins with a `## Page N` header, followed by text, then an appended block of detected tables (if any), and a final processing summary.

Example of appended table block:

```
=== DETECTED IMAGE-BASED TABLES ===

Caption: TABLE 8.
| Col1 | Col2 |
|------|------|
| 1.23 | foo  |

===================================
```

Final summary block example:

```
--- PROCESSING SUMMARY ---
Total Tables Detected: 11
OCR/Image-Based Tables Extracted: 3
Issues/Errors: 0
Processing Date: 2026-03-25 02:43:43
```


### Code Examples

Run with Vision AI enabled (ensure `.env` is configured):

```bash
python3 pdf_batch_extractor_new.py
```

Disable Vision AI (edit `Config.USE_VISION_AI = False`):

```bash
python3 pdf_batch_extractor_new.py
```

Programmatically call the Vision AI client for one image (dev/test):

```python
from pathlib import Path
from llama_client import image_to_markdown

img_bytes = Path("table.png").read_bytes()
md = image_to_markdown(img_bytes)
print(md)
```


### Troubleshooting

- Vision AI 401 Unauthorized:
  - Symptom: `❌ OPENROUTER 401: User not found` in logs/terminal.
  - Fix: Set a valid `OPENROUTER_API_KEY` in `.env` (and ensure the file is loaded) or export it in your shell.

- Rate Limited (429):
  - Symptom: Repeated 429s.
  - Fix: The client auto-retries with backoff. Reduce concurrency, wait, or check OpenRouter quota.

- Tesseract not found:
  - Symptom: OCR always empty/throws error.
  - Fix: Install Tesseract and ensure it is on PATH. Confirm with `tesseract --version`.

- LibreSSL Warning (macOS):
  - Symptom: `NotOpenSSLWarning` from urllib3.
  - Fix: Usually harmless. If requests fail due to SSL, use a Python build linked with OpenSSL (e.g., pyenv), or pin urllib3 if necessary.

- No output files generated:
  - Ensure PDFs are in `./pdfs/` and readable.
  - Check logs for exceptions (network, OCR failures).


## Part 2 – Workflow / Flow Documentation

### Process Flow

1. Discover input PDFs under `pdfs/`.
2. Start parallel workers (up to 4) to process files concurrently.
3. For each PDF:
   - Iterate pages; extract clean multi-column text (header/footer suppression).
   - Detect `TABLE X` captions and compute a region-of-interest (ROI) per caption.
   - Attempt table reconstruction in order:
     - Vision AI (if enabled) to produce Markdown directly.
     - OCR engine with X/Y clustering for grid reconstruction.
     - pdfplumber fallback for vector-based tables.
   - Validate/align/merge detected tables and append to page.
   - Append a summary block at the end of the document.

### Component Interaction

- `PDFProcessor` orchestrates page operations and calls `TableEngine` for reconstruction.
- `TableEngine` delegates to `OCRTableReconstructor`, `ColumnAligner`, `HeaderReconstructor`, and `StructuralValidator` for robust, clean tables.
- `llama_client` is called when Vision AI mode is enabled to convert a table image to Markdown.

### ASCII Workflow Diagram

```
+-----------------------+
|  Batch Entrypoint     |
|  pdf_batch_extractor  |
+-----------+-----------+
            |
            v
   Discover PDFs in ./pdfs
            |
            v
  +---------+----------+
  | Parallel Processing |
  +---------+----------+
            |
            v
     Per-PDF Processing
            |
            v
   +--------+--------+
   |  Per Page Loop  |
   +--------+--------+
            |
   Clean text (columns)
            |
            v
  Detect "TABLE X" captions
            |
            v
  Compute ROI per caption
            |
            v
  Try Vision AI  -> success? -> append Markdown table
        |  no
        v
       OCR      -> success? -> align/validate -> append
        |  no
        v
    pdfplumber -> success? -> clean/merge -> append
        |  no
        v
     record failure
            |
            v
   Append page separator
            |
            v
   Append summary block
```

### Timing and Resources

- Workers: `min(#PDFs, 4)` concurrent processes.
- Vision AI calls: network-bound, 60s timeout per request; backoff on 429s; immediate failure on 401s.
- OCR: CPU/memory heavy proportional to ROI size and `OCR_SCALE`.
- pdfplumber fallback: fast for vector-based tables.


## Part 3 – Usage Order / Sequence

### Pre-Execution Checklist

- [ ] Python 3.9+ installed.
- [ ] `pip3 install PyMuPDF pdfplumber pytesseract Pillow requests python-dotenv pypdf`.
- [ ] Tesseract installed and on PATH (`tesseract --version` passes).
- [ ] PDFs placed in `./pdfs/`.
- [ ] For Vision AI: `.env` contains a valid `OPENROUTER_API_KEY`.

### Step-by-Step Execution

1. Configure `Config` options in [pdf_batch_extractor_new.py](file:///Users/guide/workspace/univercity/year3_sem2/new_end_project/pdf_batch_extractor_new.py#L38-L60) (enable/disable Vision AI, adjust OCR thresholds).
2. Run:

```bash
python3 pdf_batch_extractor_new.py
```

3. Monitor console logs for extraction status and errors.
4. Review output Markdown files under `./output/`.

### Verification Steps

- Each output file contains:
  - Ordered page text (`## Page N` headers).
  - Appended `=== DETECTED IMAGE-BASED TABLES ===` blocks per page (if any found).
  - Final `--- PROCESSING SUMMARY ---` showing counts and error totals.
- Spot-check tables against the original PDFs to validate structure and values.

### Cleanup & Post-Processing

- If you created additional temporary assets for debugging, remove them.
- Optional: maintain an archive of the `output/` directory per run timestamp.


## Contribution Guidelines

- Fork the repository and create feature branches from `main`.
- Follow PEP 8 for code style and include docstrings.
- Add tests when adding/changing functionality.
- Open a pull request with a clear description, screenshots (if applicable), and test evidence.


## License

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

