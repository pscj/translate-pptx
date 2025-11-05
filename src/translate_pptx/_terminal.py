def command_line_interface(argv=None):
    """Command-line interface for the translate_pptx package."""
    import sys
    import os
    import asyncio
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()

    from ._pptx import extract_text_from_slides, replace_text_in_slides
    from ._translation import translate_slides_async
    from ._endpoints import prompt_deepseek_official_async as prompt_deepseek_async
    # from ._endpoints import prompt_deepseek_async

    # Read config from terminal arguments
    if argv is None:
        argv = sys.argv

    input_pptx = argv[1]
    target_language = argv[2]
    
    # Auto-generate output filename: original_name_target_language.pptx
    counter = 0
    suffix = ""
    while True:
        output_pptx = input_pptx.replace(".pptx", f"_{target_language}{suffix}.pptx")
        if os.path.exists(output_pptx):
            counter += 1
            suffix = f"_{counter}"
        else:
            break
    
    if len(argv) > 3:
        llm_name = argv[3]
    else:
        llm_name = "deepseek"

    # Currently only support async deepseek
    if "deepseek" not in llm_name.lower():
        raise ValueError(f"Currently only 'deepseek' model is supported for async translation")

    # Extract text
    texts = extract_text_from_slides(input_pptx)
    
    print(f"\n{'='*60}")
    print(f"Extracted {len(texts)} slides from {input_pptx}")
    print(f"{'='*60}\n")

    # Translate text asynchronously (one request per slide)
    translated_texts = asyncio.run(translate_slides_async(texts, prompt_deepseek_async, target_language))
    
    print("\n" + "="*60)
    print("Writing translated content to output file...")
    print("="*60 + "\n")
    
    # Replace text
    replace_text_in_slides(input_pptx, translated_texts, output_pptx, target_language)

    print(f"\n{'='*60}")
    print(f"SUCCESS: Translated presentation saved to {output_pptx}")
    print(f"{'='*60}\n")
