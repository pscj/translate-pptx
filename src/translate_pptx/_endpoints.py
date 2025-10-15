from functools import lru_cache

# @lru_cache(maxsize=128)
def prompt_openai(message: str, model="gpt-4o-2024-11-20"):
    """A prompt helper function that sends a message to openAI
    and returns only the text response.
    Results are cached to optimize for repeated queries.
    """
    import openai

    message = [{"role": "user", "content": message}]

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=message
    )
    return response.choices[0].message.content

def prompt_deepseek(message: str, model="deepseek-ai/DeepSeek-V3.2-Exp"):
    """A prompt helper function that sends a message to openAI
    and returns only the text response.
    Results are cached to optimize for repeated queries.
    """
    import requests
    import os
    import time
    
    url = "https://api.siliconflow.cn/v1/chat/completions"
    api_key = os.getenv("SILICONFLOW_API_KEY")
    
    if not api_key:
        raise ValueError("SILICONFLOW_API_KEY environment variable is not set")

    print(f"\n{'='*60}")
    print(f"[DeepSeek API] Calling model: {model}")
    print(f"[DeepSeek API] Message length: {len(message)} characters")
    print(f"{'='*60}")
    
    payload = {
        "model": model,
        "enable_thinking": True,
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    start_time = time.time()
    print(f"[DeepSeek API] Sending request...")
    
    response = requests.post(url, json=payload, headers=headers)
    
    elapsed_time = time.time() - start_time
    print(f"[DeepSeek API] Response received in {elapsed_time:.2f} seconds")
    print(f"[DeepSeek API] Status code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"[DeepSeek API] Error response: {response.text}")
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")
    
    response_data = response.json()
    content = response_data["choices"][0]["message"]["content"]
    
    print(f"[DeepSeek API] Response length: {len(content)} characters")
    print(f"{'='*60}\n")
    
    return content

def prompt_nop(message:str):
    """A prompt helper function that does nothing but returns the contained json. This function is useful for testing."""
    return "```json" + message.split("```json")[1]
