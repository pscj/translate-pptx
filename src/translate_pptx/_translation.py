

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
    
    prompt = f"""Act as a professional insurance and financial translator. Translate the following JSON array to {target_language}.

🚨 CRITICAL RULES - FOLLOW EXACTLY:

Rule 1: MECHANICAL ONE-TO-ONE MAPPING
- DO NOT understand context between strings
- DO NOT reorganize content based on meaning
- Translate EACH string INDEPENDENTLY as if it comes from a different document
- String at position [0] → Translation at position [0]
- String at position [1] → Translation at position [1]
- And so on...

Rule 2: ABSOLUTE STRUCTURE PRESERVATION
- Input has N strings → Output MUST have EXACTLY N strings
- Same array depth, same nesting, EXACT same order
- DO NOT merge, split, add, remove, or reorder ANY element

Rule 3: ISOLATED TRANSLATION
- Translate the LITERAL text of each string
- DO NOT infer meaning from other strings
- DO NOT adjust translation based on context
- Treat each string as completely independent

Rule 4: FORMATTING
- Preserve line breaks (\\n), spaces, punctuation exactly
- Keep proper nouns unchanged (PingAn, MSH, Aon)

Rule 5: OUTPUT
- Return ONLY the JSON array, no explanations

EXAMPLE OF CORRECT BEHAVIOR:
Input: [\"Apple\", \"Banana\", \"Cherry\"]
Output: [\"苹果\", \"香蕉\", \"樱桃\"]

EXAMPLE OF WRONG BEHAVIOR (DO NOT DO THIS):
Input: [\"Apple\", \"Banana\", \"Cherry\"]
Output: [\"香蕉\", \"苹果\", \"樱桃\"]  ← WRONG! Order changed
Output: [\"苹果和香蕉\", \"樱桃\"]  ← WRONG! Merged strings

Original JSON:
{slide_json}

Return only the translated JSON array:"""

    try:
        translated_text = await prompt_function_async(prompt)
        translated_text = remove_outer_markdown(translated_text)
        translated_arrays = json.loads(translated_text)
        
        # Validate structure - translated_arrays should be a dict with same keys
        if not isinstance(translated_arrays, dict) or set(translated_arrays.keys()) != set(text_arrays.keys()):
            print(f"[Slide {slide_index}] ERROR: Structure mismatch, using original")
            return slide_data
        
        # Rebuild slide_data with translated text
        result = {}
        for shape_id, info in slide_data.items():
            original_text = info['text']
            translated_text_array = translated_arrays.get(str(shape_id), original_text)  # JSON keys are strings
            
            # Validate array length
            if isinstance(original_text, list) and isinstance(translated_text_array, list):
                if len(original_text) != len(translated_text_array):
                    print(f"[Slide {slide_index}] Shape ID {shape_id}: text count mismatch, using original")
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