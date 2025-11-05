

import asyncio
import json
from typing import List, Callable
from ._utilities import remove_outer_markdown

async def translate_slide_async(slide_data: dict, slide_index: int, prompt_function_async: Callable, target_language: str):
    """Translate a single slide asynchronously.
    slide_data is a dict mapping shape_id to {text: [...], use_run_mode: bool}
    """
    # Extract only the text arrays for translation
    # Convert shape_id to string for JSON compatibility
    text_arrays = {str(shape_id): info['text'] for shape_id, info in slide_data.items()}
    slide_json = json.dumps(text_arrays, ensure_ascii=False, indent=2)
    
    print(f"\n[Slide {slide_index}] Starting translation...")
    print(f"[Slide {slide_index}] Data structure: {len(slide_data)} shapes")
#     prompt = f"""
#     翻译以下文字为英文：在标普，我们始终关注您与家人的健康与安心。
# 为更好地支持您生活中的每一份牵挂，我们正式推出 「员工自购保险计划」— 以专属团购价格与承保条件，助您轻松构筑个人与家庭的保障防线。
# 即日起，扫码登录平台，了解详情并完成投保，为关心的TA多添一份安心。
#     """
    prompt = f"""

## Role
You are a senior insurance and financial localization expert, specializing in Business-to-Business (B2B) communication and corporate presentation documents.

## Task
Accurately translate the provided JSON object into **{target_language}**.

## Technical Requirements

### 1. Terminology & Precision
- **Mandatory use of standard, industry-accepted insurance and financial terminology**
- Translation must reflect professional-to-professional communication within the insurance sector

### 2. Register & Tone
- **Formal, professional, and concise** tone suitable for corporate presentations
- Avoid colloquialisms and excessive marketing language
- Focus on clarity and factual accuracy

### 3. Target Audience
- Insurance partners, corporate clients, or reinsurers
- Peer-to-peer expert dialogue level

### 4. Quality Assurance
- Maintain absolute consistency in key terminology throughout
- Ensure technical accuracy in insurance context

     
### 5. CRITICAL RULES - FOLLOW EXACTLY:

Rule 1: PRESERVE JSON STRUCTURE EXACTLY
- Input is a JSON object with keys (shape IDs) mapping to arrays of strings
- Output MUST have EXACTLY the same keys
- Each array MUST have EXACTLY the same length as the input array
- DO NOT add, remove, or modify any keys

Rule 2: MECHANICAL ONE-TO-ONE ARRAY TRANSLATION
- For each key, translate its array element-by-element
- Array[0] → Translated[0], Array[1] → Translated[1], etc.
- DO NOT merge, split, reorder, add, or remove ANY array elements
- If input array has N elements, output array MUST have EXACTLY N elements
- DO NOT infer or add missing elements based on context

Rule 3: ISOLATED TRANSLATION
- Translate EACH string INDEPENDENTLY
- DO NOT infer meaning from other strings
- DO NOT reorganize content based on context
- DO NOT add translations for elements that don't exist in the input
- Treat each string as completely independent

Rule 4: FORMATTING
- Preserve line breaks (\\n), spaces, punctuation exactly
- Keep proper nouns unchanged (PingAn, MSH, Aon, etc.)

Rule 5: OUTPUT FORMAT
- Return ONLY the JSON object, no explanations, no markdown code blocks
- Use the EXACT same structure as the input

EXAMPLE:
Input: {{"1": ["Apple", "Banana"], "2": ["Cherry"]}}
Output: {{"1": ["苹果", "香蕉"], "2": ["樱桃"]}}

WRONG Examples (DO NOT DO THIS):
{{"1": ["香蕉", "苹果"], "2": ["樱桃"]}}  ← WRONG! Order changed
{{"1": ["苹果和香蕉"], "2": ["樱桃"]}}  ← WRONG! Merged elements
{{"1": ["苹果", "香蕉"]}}  ← WRONG! Missing key "2"
{{"1": ["苹果", "香蕉", "橙子"], "2": ["樱桃"]}}  ← WRONG! Added extra element

Translate the following JSON object to {target_language}.

Original JSON:
{slide_json}

Return only the translated JSON object:"""

    try:
        translated_text = await prompt_function_async(prompt)
        print(f"response {translated_text}")

        # Save full response to debug file
        debug_file = f"debug_slide_{slide_index}_response.json"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(translated_text)
        print(f"[Slide {slide_index}] Full response saved to {debug_file}")
        
        print(f"[Slide {slide_index}] Raw response preview (first 500 chars):")
        print(f"{translated_text[:500]}")
        print(f"[Slide {slide_index}] Raw response preview (last 500 chars):")
        print(f"{translated_text[-500:]}")
        
        translated_text = remove_outer_markdown(translated_text)
        translated_arrays = json.loads(translated_text)
        
        # Validate structure - translated_arrays should be a dict with same keys
        if not isinstance(translated_arrays, dict):
            print(f"[Slide {slide_index}] ERROR: Response is not a dict, type={type(translated_arrays)}, using original")
            print(f"[Slide {slide_index}] Response preview: {str(translated_arrays)[:200]}")
            return slide_data
        
        if set(translated_arrays.keys()) != set(text_arrays.keys()):
            print(f"[Slide {slide_index}] ERROR: Keys mismatch")
            print(f"[Slide {slide_index}]   Expected keys: {sorted(text_arrays.keys())}")
            print(f"[Slide {slide_index}]   Received keys: {sorted(translated_arrays.keys())}")
            print(f"[Slide {slide_index}] Using original data")
            return slide_data
        
        # Rebuild slide_data with translated text
        result = {}
        for shape_id, info in slide_data.items():
            original_text = info['text']
            translated_text_array = translated_arrays.get(str(shape_id), original_text)  # JSON keys are strings
            
            # Validate array length
            if isinstance(original_text, list) and isinstance(translated_text_array, list):
                if len(original_text) != len(translated_text_array):
                    print(f"[Slide {slide_index}] ⚠️  WARNING: Shape ID {shape_id} text count mismatch")
                    print(f"[Slide {slide_index}]   Expected: {len(original_text)} items")
                    print(f"[Slide {slide_index}]   Received: {len(translated_text_array)} items")
                    print(f"[Slide {slide_index}]   This shape will NOT be translated. Please re-run translation.")
                    print(f"[Slide {slide_index}]   Tip: The AI may have added/removed elements. Check the prompt.")
                    # Use original text to avoid misalignment
                    translated_text_array = original_text
            
            result[shape_id] = {
                'text': translated_text_array,
                'use_run_mode': info['use_run_mode']
            }
        
        print(f"[Slide {slide_index}] Translation completed successfully")
        return result
        
    except Exception as e:
        print(f"[Slide {slide_index}] ERROR: {e}")
        print(f"[Slide {slide_index}] Using original data")
        return slide_data


async def translate_slides_async(original_texts: List[List], prompt_function_async: Callable, target_language: str = "English"):
    """Translate all slides asynchronously, one request per slide."""
    print("\n" + "="*60)
    print("STARTING ASYNC TRANSLATION")
    print(f"Total slides: {len(original_texts)}")
    print("="*60)
    
    # Create async tasks for all slides
    tasks = [
        translate_slide_async(slide_data, i, prompt_function_async, target_language)
        for i, slide_data in enumerate(original_texts)
    ]
    
    # Wait for all tasks to complete
    print("\nWaiting for all translation requests to complete...")
    translated_slides = await asyncio.gather(*tasks)
    
    print("\n" + "="*60)
    print("ALL TRANSLATIONS COMPLETED")
    print(f"Successfully translated {len(translated_slides)} slides")
    print("="*60 + "\n")
    
    return translated_slides