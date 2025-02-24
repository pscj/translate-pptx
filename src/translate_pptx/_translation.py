



def translate_data_structure_of_texts_recursive(original_texts, prompt_function, target_language: str = "German"):
    """Translate the data structure of a list of texts recursively and return the texts, ideally in the same format but in a different language.
    It case it cannot conserve the data structure, it will return the original texts.
    """
    import json
    from ._utilities import remove_outer_markdown

    new_texts = []
    for s, original_text in enumerate(original_texts):
        original_text_json = json.dumps(original_text)
        print("ORIGINAL:\n", original_text_json)
        prompt = f"Translate the following text elements to {target_language}. Keep all institute names, project names, library names, and technical terms unchanged. Preserve all line breaks and empty lines exactly as they appear. Preserve the JSON array structure exactly. Return only the translated JSON: {original_text_json}"

        translated_texts = remove_outer_markdown(prompt_function(prompt))
        print("TRANSLATED:\n", translated_texts)

        try:
            translated_texts_json = json.loads(translated_texts)
        except:
            new_texts.append(original_text)
            continue

        if len(original_text) != len(translated_texts_json):
            print("Lengths do not match")
            translated_texts_json = original_text

        elif any(len(orig) != len(trans) for orig, trans in zip(original_text, translated_texts_json)):
            print("Lengths of inner lists do not match")
            for i in range(len(original_text)):
                if len(original_text[i]) != len(translated_texts_json[i]):
                    translated_texts_json[i] = original_text[i]

        new_texts.append(translated_texts_json)

    return new_texts