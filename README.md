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
- [Setup & Execution (Git)](#setup--execution-git)
  - [System Requirements](#system-requirements)
  - [Dependency Versions](#dependency-versions)
  - [Clone and Install](#clone-and-install)
  - [Run the Pipeline](#run-the-pipeline)
  - [Troubleshooting Installation \& Runtime](#troubleshooting-installation--runtime)
- [Project Summary](#project-summary)
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

## Part 2 – extract_to_json.py Documentation

The second main component [extract_to_json.py](file:///Users/guide/workspace/univercity/year3_sem2/new_end_project/extract_to_json.py#L1-247) converts the Markdown outputs into structured JSON for downstream analytics.

### Role and Features

- Parses ALL Markdown files under `output/`.
- Pure Python parser scans the entire document for Markdown tables (no LLM influence on numeric data).
- Calls a strictly confined LLM prompt to extract only two metadata fields: paper title and datasets (ignores models/frameworks).
- Merges pure-Python parsed experiment metrics with LLM-provided metadata into a final `final_results.json`.

### JSON Extraction Logic

- `extract_tables_with_python(markdown)`:
  - Iterates through all Markdown tables in the document.
  - Rejects configuration/hardware tables via heuristic keywords.
  - Rejects rows that are purely numeric or known library names.
  - Produces a list of `{ "model": <str>, "results": { <metric>: <float>, ... } }` items.
- `create_metadata_prompt(body_chunk, paper_id)`:
  - Constrains the LLM to extract only the official paper title and explicitly named datasets.
  - Excludes ML model names from datasets by instruction.
- `clean_json_response(text)`:
  - Extracts the first valid JSON object from the LLM output defensively.
- `_build_logical_aliases(raw_names)`:
  - Deduplicates model names by aliasing variants and acronyms to a canonical form.

### Data Transformation and Output

- For each `paperX.md`:
  - Pure-Python parsed tables → experiments list.
  - LLM → `{ "title": "...", "datasets": [...] }` only.
  - Merge logic removes duplicates and keeps numeric data source-of-truth from Python parsing.
  - Writes a single `final_results.json` at project root containing all papers:

```json
[
  {
    "paper_id": "paper1",
    "datasets": ["Official Title", "ImageNet", "KITTI"],
    "experiments": [
      { "model": "ModelA", "results": { "Accuracy": 0.91, "F1": 0.88 } },
      { "model": "ModelB", "results": { "Accuracy": 0.89 } }
    ]
  }
]
```

### Usage and Examples

Assuming Markdown files exist in `./output/` (produced by the extractor):

```bash
python3 extract_to_json.py
```

- The script discovers all `*.md` in `output/`, pauses between files to control API usage, and writes `final_results.json` to the project root.

### Error Handling

- Missing Markdown files:
  - Prints `❌ No .md files found in output/` and exits gracefully.
- LLM failures:
  - If the LLM call fails/times out, the script continues with empty metadata: `{"title": "", "datasets": []}` and still outputs experiments from Python parsing.
- Path sanitation:
  - Filters out path-like strings and citations from dataset and model fields.


## Part 2 – Workflow / Flow Documentation

### Process Flow

1. Discover input PDFs under `pdfs/`.
2. Start parallel workers (up to 4) to process files concurrently.
   - Iterate pages; extract clean multi-column text (header/footer suppression).
   - Detect `TABLE X` captions and compute a region-of-interest (ROI) per caption.
   - Attempt table reconstruction in order:
     - Vision AI (if enabled) to produce Markdown directly.
     - OCR engine with X/Y clustering for grid reconstruction.
     - pdfplumber fallback for vector-based tables.
   - Validate/align/merge detected tables and append to page.
   - Append a summary block at the end of the document.
4. Second-stage JSON extraction:
   - Scan all Markdown outputs in `output/`.
   - Parse ALL tables via pure Python (no LLM on numeric values).
   - Ask LLM only for title and datasets metadata.
   - Merge and write a single consolidated `final_results.json`.

### Component Interaction

- `PDFProcessor` orchestrates page operations and calls `TableEngine` for reconstruction.
- `TableEngine` delegates to `OCRTableReconstructor`, `ColumnAligner`, `HeaderReconstructor`, and `StructuralValidator` for robust, clean tables.
- `llama_client` is called when Vision AI mode is enabled to convert a table image to Markdown.
- `extract_to_json.py` ingests `./output/*.md`, parses tables, and calls `llama_client.call_llama` for minimal metadata only.

### ASCII Workflow Diagram

```
                ┌───────────────────────────┐
                │  pdf_batch_extractor_new  │
                │      (per PDF)            │
                └─────────────┬─────────────┘
                              │
                              v
                 Clean text + Table ROIs
                              │
     ┌───────────────┬────────┴─────────┬───────────────┐
     │               │                  │               │
     v               v                  v               v
 Vision AI      OCR Reconstruction   pdfplumber      Failure note
  (optional)     (X/Y clustering)     Fallback       (logged only)
     │               │                  │
     └─────── Tables (Markdown Grid) ───┘
                              │
                              v
                  Append to Page Output
                              │
                              v
                      ./output/paperX.md
                              │
                              v
                ┌───────────────────────────┐
                │      extract_to_json      │
                │  (batch over output/)     │
                └─────────────┬─────────────┘
                              │
       Parse ALL Markdown tables (Pure Python)
                              │
         + LLM (Title & Datasets ONLY)
                              │
                              v
                    final_results.json
```

### Timing and Resources

- Workers: `min(#PDFs, 4)` concurrent processes.
- Vision AI calls: network-bound, 60s timeout per request; backoff on 429s; immediate failure on 401s.
- OCR: CPU/memory heavy proportional to ROI size and `OCR_SCALE`.
- pdfplumber fallback: fast for vector-based tables.
 - JSON stage: lightweight, dominated by LLM latency for short prompts.


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
5. Convert Markdown to consolidated JSON:

```bash
python3 extract_to_json.py
```
4. Review output Markdown files under `./output/`.

### Verification Steps

- Each output file contains:
  - Ordered page text (`## Page N` headers).
  - Appended `=== DETECTED IMAGE-BASED TABLES ===` blocks per page (if any found).
- `final_results.json` exists and includes entries for all processed `paperX.md` files.
- Spot-check tables against the original PDFs to validate structure and values.
- Spot-check tables against the original PDFs to validate structure and values.

### Cleanup & Post-Processing

- If you created additional temporary assets for debugging, remove them.
- Optional: maintain an archive of the `output/` directory per run timestamp.
## Setup & Execution (Git)

### System Requirements

- OS: macOS 12+ (Monterey) or Ubuntu 22.04+ (Jammy) or Windows 10+
- CPU: Any modern x86_64; OCR performance improves with more cores
- RAM: 8 GB minimum (16 GB recommended for large PDFs)
- Storage: 1 GB free (depends on number/size of PDFs)
- Python: 3.9–3.12 (tested with 3.9)
- Tesseract OCR: 5.5.2+

### Dependency Versions

The pipeline has been tested with:

- PyMuPDF 1.26.5
- pdfplumber 0.11.8
- pytesseract 0.3.13
- Pillow 11.3.0
- requests 2.32.5
- python-dotenv 1.2.1
- pypdf 6.9.2
- Tesseract OCR 5.5.2

### Clone and Install

```bash
git clone <your-repo-url> pdf-extractor
cd pdf-extractor

# macOS (Tesseract)
brew install tesseract

# Ubuntu (Tesseract)
sudo apt update && sudo apt install -y tesseract-ocr

# Python deps
pip3 install PyMuPDF==1.26.5 pdfplumber==0.11.8 pytesseract==0.3.13 \
  Pillow==11.3.0 requests==2.32.5 python-dotenv==1.2.1 pypdf==6.9.2
```

Optional: Vision AI (OpenRouter)
```bash
echo 'OPENROUTER_API_KEY=sk-or-xxxxxxxx' > .env
```

### Run the Pipeline

```bash
# 1) Generate Markdown from PDFs
python3 pdf_batch_extractor_new.py

# 2) Convert Markdown tables to JSON
python3 extract_to_json.py
```

### Troubleshooting Installation & Runtime

- `ModuleNotFoundError: requests` or other library: run the pip install line above again.
- `tesseract: command not found`: install Tesseract and confirm with `tesseract --version`.
- Vision AI `401 Unauthorized`: set a valid `OPENROUTER_API_KEY` in `.env` and restart your shell.
- `NotOpenSSLWarning`: benign; if requests fail due to SSL on macOS system Python, install Python via `pyenv` or use a virtualenv with OpenSSL.
- Empty or missing `output/*.md`: ensure PDFs exist in `pdfs/` and are readable; review console logs for page-level errors.

## Project Summary

- [pdf_batch_extractor_new.py](file:///Users/guide/workspace/univercity/year3_sem2/new_end_project/pdf_batch_extractor_new.py#L1-398)
  - Purpose: Batch process PDFs into Markdown with robust, validated table reconstructions appended per page.
  - Inputs: PDFs under `./pdfs/`.
  - Outputs: Markdown files under `./output/` with text and tables.
  - Key: Multi-pass table extraction (Vision AI → OCR → pdfplumber), caption-based ROI calculation, structural validation.

- [extract_to_json.py](file:///Users/guide/workspace/univercity/year3_sem2/new_end_project/extract_to_json.py#L1-247)
  - Purpose: Parse all Markdown tables and output a consolidated `final_results.json`.
  - Inputs: Markdown files under `./output/`.
  - Outputs: `final_results.json` with experiments per paper plus LLM-provided title/datasets.
  - Key: Pure-Python parsing for numeric fidelity; LLM is strictly constrained to metadata only.

- [llama_client.py](file:///Users/guide/workspace/univercity/year3_sem2/new_end_project/llama_client.py)
  - Purpose: Vision AI and text-only client (OpenRouter). Handles retries, backoff, and 401 detection.
  - Inputs: Image bytes for table screenshots (Vision), prompt strings (text).
  - Outputs: Markdown table strings or JSON text.

Overall: The extraction system converts complex, multi-column academic PDFs into structured Markdown with accurate tables, then produces a clean, consolidated JSON artifact for analytics while keeping numeric data integrity anchored in deterministic Python parsing.


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
