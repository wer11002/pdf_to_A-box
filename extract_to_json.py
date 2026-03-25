"""
extract_to_json.py
==================
The "Air-Gap" Pipeline:
1. Pure Python parses ALL Markdown tables across the entire document.
2. The LLM is strictly confined to extracting the Title and Datasets from the text.
3. Python securely merges them together.
"""

import json
import time
import re
from pathlib import Path

try:
    from llama_client import call_llama
except ImportError:
    raise RuntimeError("❌ llama_client.py not found in directory.")

# ---------------------------------------------------------------------------
# 1. PURE PYTHON TABLE PARSER (100% Immutable)
# ---------------------------------------------------------------------------

def extract_tables_with_python(full_markdown: str) -> list:
    """
    Physically reads ALL Markdown tables in the entire document.
    """
    experiments = []
    lines = full_markdown.strip().split('\n')
    
    current_headers = []
    in_table = False
    
    for line in lines:
        line = line.strip()
        # Look for standard Markdown table rows
        if line.startswith('|') and line.endswith('|'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            
            if not parts:
                continue
                
            if not in_table:
                current_headers = parts
                in_table = True
            elif all(re.match(r'^:?-+:?$', p) for p in parts):
                continue
            else:
                if not current_headers or len(parts) != len(current_headers): 
                    continue
                
                # Filter out Config/Hardware tables
                first_col_lower = current_headers[0].lower()
                if any(x in first_col_lower for x in ['parameter', 'hyperparameter', 'hardware', 'library', 'software', 'adjusted']):
                    continue
                    
                model_name = parts[0].replace('*', '').replace('_', '').strip()
                
                # Filter out pure numbers (e.g., "0.186") and software packages
                if re.match(r'^[\d\.\-]+$', model_name) or model_name.lower() in ['tensorflow', 'tersonflow', 'cudatoolkit', 'cudnn', 'pytorch']:
                    continue
                    
                results = {}
                for i in range(1, len(parts)):
                    val_str = parts[i].replace('*', '').replace('_', '').replace(',', '').strip()
                    try:
                        results[current_headers[i]] = float(val_str)
                    except ValueError:
                        pass 
                        
                if results:
                    experiments.append({
                        "model": model_name,
                        "results": results
                    })
        else:
            in_table = False
            
    return experiments


# ---------------------------------------------------------------------------
# 2. CONFINED LLM PROMPT (Only Title & Datasets)
# ---------------------------------------------------------------------------

def create_metadata_prompt(body_chunk: str, paper_id: str) -> str:
    """
    The LLM is now strictly limited to reading the text to find the Title and Datasets.
    """
    return f"""
You are an expert data extractor. Read the following academic paper text.

CRITICAL INSTRUCTIONS:
1. Find the EXACT OFFICIAL TITLE of the paper.
2. Identify explicitly named external DATASETS used for training/testing (e.g., "ImageNet", "BDD100K", "KITTI").
3. DO NOT include machine learning models, algorithms, or framework names (like YOLOv8, DeepSORT, TensorFlow, Inception, ResNet, MobileNet, CNNs) in the datasets array. Neural Networks are NOT datasets.
4. Return ONLY a valid JSON object. Do not include markdown formatting.

EXPECTED JSON SCHEMA:
{{
  "paper_id": "{paper_id}",
  "title": "<EXACT PAPER TITLE HERE>",
  "datasets": ["<Dataset 1>", "<Dataset 2>"]
}}

[PAPER TEXT]
{body_chunk}
"""

# ---------------------------------------------------------------------------
# 3. POST-PROCESSING (Logical Aliasing & Cleanup)
# ---------------------------------------------------------------------------

_PATH_RE = re.compile(r"^/(?:Users|home|var|tmp|mnt)/", re.IGNORECASE)

def _build_logical_aliases(raw_names: list) -> dict:
    unique_names = list(set(name.strip() for name in raw_names if name.strip()))
    unique_names.sort(key=len, reverse=True)
    alias_map = {}
    
    for name in unique_names:
        name_lower = name.lower()
        name_singular = re.sub(r's$', '', name_lower)
        best_canonical = name
        
        for parent in unique_names:
            if name == parent: continue
            parent_lower = parent.lower()
            parent_singular = re.sub(r's$', '', parent_lower)
            
            if name_singular == parent_singular:
                if not parent_lower.endswith('s'): best_canonical = parent
                break
                
            words = re.split(r'\W+', parent_lower)
            acronym = "".join(w[0] for w in words if w).lower()
            if name_lower == acronym and len(acronym) >= 2:
                best_canonical = parent[:-1] if parent.lower().endswith('s') else parent
                break
        alias_map[name_lower] = best_canonical
    return alias_map

def clean_json_response(text: str) -> dict:
    start = text.find("{")
    end   = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in LLM response.")
    return json.loads(text[start : end + 1])

# ---------------------------------------------------------------------------
# 4. MAIN PIPELINE
# ---------------------------------------------------------------------------

def process_markdown_file(md_path: Path) -> dict | None:
    paper_id = md_path.stem
    markdown = md_path.read_text(encoding="utf-8")
    
    # Send the first ~12,000 characters to the LLM to find the title/datasets
    body_chunk = markdown[:12000]

    # 1. PYTHON PARSING (Untouchable by LLM)
    print(f"    -> Running pure Python extraction on ALL tables in the document...")
    # Pass the ENTIRE document to the python parser, no splitting!
    python_extracted_experiments = extract_tables_with_python(markdown)
    print(f"       [+] Python extracted {len(python_extracted_experiments)} models exactly as written.")

    # 2. LLM METADATA EXTRACTION (Title & Datasets ONLY)
    print(f"    -> Asking LLM for Title and Datasets...")
    prompt = create_metadata_prompt(body_chunk, paper_id)
    
    try:
        # User Requested: 3 Second Delay before hitting the API
        print(f"       ⏳ Waiting 3 seconds before shooting API to AI...")
        time.sleep(3)
        llm_json = clean_json_response(call_llama(prompt))
    except Exception as e:
        print(f"    [!] LLM parsing failed: {e}. Using empty metadata.")
        llm_json = {"title": "", "datasets": []}

    # 3. SECURE MERGE & ALIAS RESOLUTION
    title = llm_json.get("title", "")
    datasets = llm_json.get("datasets", [])
    
    final_datasets = []
    if title: 
        final_datasets.append(title)
        
    for d in datasets:
        if isinstance(d, str) and d.strip() and not _PATH_RE.match(d) and d not in final_datasets:
            final_datasets.append(d.strip())

    # Safely merge Python's table data (grouping identical models)
    raw_names = [exp.get("model", "") for exp in python_extracted_experiments]
    alias_map = _build_logical_aliases(raw_names)
    seen: dict[str, dict] = {}

    for exp in python_extracted_experiments:
        raw_name = exp.get("model", "").strip()
        raw_name = re.sub(r'\s*\[\d+\]\s*', '', raw_name) # Clean citations
        if not raw_name: continue
        
        canonical = alias_map.get(raw_name.lower(), raw_name)
        results = exp.get("results", {})

        if canonical not in seen:
            seen[canonical] = {"model": canonical, "results": results}
        else:
            for k, v in results.items():
                seen[canonical]["results"].setdefault(k, v)

    final_experiments = [v for v in seen.values() if v["results"]]

    return {
        "paper_id": paper_id,
        "datasets": final_datasets,
        "experiments": final_experiments,
    }

def main():
    input_dir   = Path("output")
    output_file = Path("final_results.json")

    md_files = sorted(input_dir.glob("*.md"))
    if not md_files:
        print("❌ No .md files found in output/")
        return

    results = []
    print(f"🚀 {len(md_files)} file(s) found. Starting Air-Gapped Hybrid Pipeline...\n")

    for i, md_path in enumerate(md_files):
        print(f"📄 [{i+1}/{len(md_files)}] {md_path.stem}")
        
        result = process_markdown_file(md_path)
        
        if result:
            results.append(result)
            
        if i < len(md_files) - 1:
            print("  ⏳ Waiting 3s before moving to the next paper...")
            time.sleep(3)

    output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n🎉 Saved {len(results)} paper(s) to {output_file}")

if __name__ == "__main__":
    main()