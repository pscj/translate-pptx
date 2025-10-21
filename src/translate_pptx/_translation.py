

import asyncio
import json
from typing import List, Callable
from ._utilities import remove_outer_markdown


async def translate_slide_async(slide_data: List, slide_index: int, prompt_function_async: Callable, target_language: str):
    """Translate a single slide asynchronously."""
    slide_json = json.dumps(slide_data, ensure_ascii=False, indent=2)
    
    print(f"\n[Slide {slide_index}] Starting translation...")
    print(f"[Slide {slide_index}] Data structure: {len(slide_data)} shapes")
    
    prompt = f"""Translate the following JSON array to {target_language}.

CRITICAL REQUIREMENTS:
1. Comprehensive Understanding Before Translation:
FIRST, read and comprehend the ENTIRE JSON array's context and meaning. Understand the relationships between strings, especially within nested structures, to ensure accurate and contextually appropriate translations.
THEN, perform a precise, sentence-by-sentence translation, ensuring the original intent, nuance, and technical terms are correctly rendered.
2. Absolute Structural Integrity:
You MUST preserve the EXACT JSON structure. This includes:
The same number of arrays and objects.
The same nesting levels.
The EXACT SEQUENCE and ORDER of all elements. The first string in the original MUST remain the first in the translation, and the last MUST remain the last.
DO NOT add, remove, reorder, sort, or rearrange any elements.
3. Content Translation Policy:
Translate ALL human-readable text content.
Keep English proper nouns, abbreviations, and codes unchanged (e.g., "PingAn", "MSH", "UHC", "Aon", "GDPR").
Establish terminology consistency across the entire document for repeated terms.
4. Exact Formatting Preservation:
PRESERVE ALL non-content characters EXACTLY as they appear. This includes:
Line breaks (\n). If a string contains \n, the translation MUST contain \n in the identical position.
Spaces, punctuation, and indentation.
Empty strings ("").
5. Output Instructions:
Return ONLY the final, translated JSON array.
Do not include any explanations, notes, or introductory text.

Original JSON:
{slide_json}

Return only the translated JSON array:"""

    try:
        translated_text = await prompt_function_async(prompt)
        translated_text = remove_outer_markdown(translated_text)
        translated_data = json.loads(translated_text)
        
        # Validate structure
        if len(slide_data) != len(translated_data):
            print(f"[Slide {slide_index}] ERROR: Structure mismatch, using original")
            return slide_data
        
        # Validate each shape's structure
        for j in range(len(slide_data)):
            if isinstance(slide_data[j], list) and isinstance(translated_data[j], list):
                if len(slide_data[j]) != len(translated_data[j]):
                    print(f"[Slide {slide_index}] Shape {j}: run count mismatch, using original")
                    translated_data[j] = slide_data[j]
        
        print(f"[Slide {slide_index}] Translation completed successfully")
        return translated_data
        
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


def translate_data_structure_of_texts_recursive(original_texts, prompt_function, target_language: str = "English"):
    """Translate the data structure of a list of texts recursively and return the texts, ideally in the same format but in a different language.
    It case it cannot conserve the data structure, it will return the original texts.
    """
    import json
    from ._utilities import remove_outer_markdown

    # Convert all texts to JSON in one go
    original_texts_json = json.dumps(original_texts, ensure_ascii=False, indent=2)
    print("\n" + "="*60)
    print("ORIGINAL JSON INPUT:")
    print(original_texts_json)
    print("="*60)
    print("\nORIGINAL STRUCTURE:")
    print(f"Total slides: {len(original_texts)}")
    for i, slide in enumerate(original_texts):
        print(f"  Slide {i}: {len(slide)} shapes")
        for j, shape in enumerate(slide):
            if isinstance(shape, list):
                print(f"    Shape {j}: {len(shape)} runs")
            else:
                print(f"    Shape {j}: string ('{shape[:30]}...' if len(shape) > 30 else '{shape}')")
    print("="*60 + "\n")
    
    # Single prompt for all slides
    prompt = f"""Translate the following JSON array to {target_language}.

CRITICAL REQUIREMENTS:
1. You MUST preserve the EXACT JSON structure - same number of arrays, same nesting levels, SAME ORDER
2. Translate ONLY the text content, NOT the structure
3. DO NOT reorder, sort, or rearrange any elements - keep the EXACT same sequence
4. The first string in the original MUST be the first string in the translation
5. The last string in the original MUST be the last string in the translation
6. Translate ALL text including company names, but keep English names/abbreviations unchanged (e.g., "PingAn", "MSH", "UHC", "Aon")
7. PRESERVE ALL line breaks (\\n), spaces, and empty strings EXACTLY as they appear in the original
8. If a string contains \\n (newline), the translated string MUST also contain \\n at the same positions
9. Return ONLY the translated JSON array, no explanations

Original JSON:
{original_texts_json}

Return only the translated JSON array:"""

    # Single API call
    translated_texts = remove_outer_markdown(prompt_function(prompt))
    print("\n" + "="*60)
    print("TRANSLATED RAW RESPONSE (first 2000 chars):")
    print(translated_texts[:2000] if len(translated_texts) > 2000 else translated_texts)
    print("="*60 + "\n")

    # Parse the result
    try:
        translated_texts_json = json.loads(translated_texts)
        print("\n" + "="*60)
        print("TRANSLATED STRUCTURE:")
        print(f"Total slides: {len(translated_texts_json)}")
        for i, slide in enumerate(translated_texts_json):
            print(f"  Slide {i}: {len(slide)} shapes")
            for j, shape in enumerate(slide):
                if isinstance(shape, list):
                    print(f"    Shape {j}: {len(shape)} runs")
                    # Show details for problematic shapes
                    if i == 1 and j in [3, 7]:  # Slide 1 (index 1), Shape 3 and 7
                        for k, run in enumerate(shape):
                            print(f"      Run {k}: '{run}'")
                else:
                    print(f"    Shape {j}: string ('{shape[:30]}...' if len(shape) > 30 else '{shape}')")
        print("="*60 + "\n")
    except Exception as e:
        print(f"Failed to parse translated JSON: {e}")
        print(f"Raw response: {translated_texts[:1000]}")
        return original_texts

    # Validate structure matches
    if len(original_texts) != len(translated_texts_json):
        print(f"Lengths do not match: original={len(original_texts)}, translated={len(translated_texts_json)}")
        return original_texts

    # Validate each slide's structure
    for i in range(len(original_texts)):
        if len(original_texts[i]) != len(translated_texts_json[i]):
            print(f"Slide {i}: shape count mismatch, using original")
            translated_texts_json[i] = original_texts[i]
        else:
            # Validate each shape's structure
            for j in range(len(original_texts[i])):
                if isinstance(original_texts[i][j], list) and isinstance(translated_texts_json[i][j], list):
                    if len(original_texts[i][j]) != len(translated_texts_json[i][j]):
                        print(f"Slide {i}, Shape {j}: run count mismatch, using original")
                        translated_texts_json[i][j] = original_texts[i][j]

    return translated_texts_json