# llama_client.py (HOSTED - OpenRouter)

import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()  # load .env file

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# For standard text queries
TEXT_MODEL = "meta-llama/llama-3-8b-instruct"
# For image/table scanning
VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct" 

if not API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY not found in .env")

def call_llama(prompt: str) -> str:
    """Standard text-only completion."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",   
        "X-Title": "final-project"             
    }

    payload = {
        "model": TEXT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You extract structured scientific facts from research papers. "
                    "Return ONLY valid JSON."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0
    }

    # Added timeout=60 to prevent the script from freezing!
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def image_to_markdown(image_bytes: bytes) -> str:
    """
    Takes raw image bytes (screenshot of a table), sends it to LLaMA Vision, 
    and asks it to return a perfectly formatted Markdown table.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",   
        "X-Title": "pdf-table-extractor"             
    }

    # Encode the image bytes to base64 so the API can read it
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    image_data_url = f"data:image/png;base64,{base64_image}"

    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "Convert this image of a table into a perfectly formatted Markdown table. Do not include any conversational text before or after the table. Return ONLY the markdown table."
                    },
                    {
                        "type": "image_url", 
                        "image_url": {
                            "url": image_data_url
                        }
                    }
                ]
            }
        ],
        "temperature": 0
    }

    # Added timeout=60 to prevent the script from freezing!
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    
    if response.status_code == 401:
        error_msg = response.json().get("error", {}).get("message", "Unauthorized")
        raise ConnectionRefusedError(f"❌ OPENROUTER 401: {error_msg}. Check your API key in .env.")
        
    if response.status_code != 200:
        print("❌ VISION API STATUS:", response.status_code)
        print("❌ RESPONSE:", response.text)
        response.raise_for_status()
    
    # Extract the markdown string returned by the AI
    data = response.json()
    if "choices" not in data or not data["choices"]:
        raise ValueError(f"❌ Unexpected OpenRouter response: {data}")
        
    # FIXED: Store it in a variable first, THEN clean it, THEN return it.
    ai_markdown = data["choices"][0]["message"]["content"]
    ai_markdown = ai_markdown.replace("```markdown", "").replace("```", "").strip()
    
    return ai_markdown