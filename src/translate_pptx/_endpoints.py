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

async def prompt_siliconflow_async(message: str, model="Pro/deepseek-ai/DeepSeek-V3.1"):
    """Async version of prompt_deepseek for concurrent API calls using SiliconFlow."""
    import aiohttp
    import os
    import time
    
    url = "https://api.siliconflow.cn/v1/chat/completions"
    api_key = os.getenv("SILICONFLOW_API_KEY")
    
    if not api_key:
        raise ValueError("SILICONFLOW_API_KEY environment variable is not set")

    print(f"\n{'='*60}")
    print(f"[DeepSeek API Async] Calling model: {model}")
    print(f"[DeepSeek API Async] Message length: {len(message)} characters")
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
    print(f"[DeepSeek API Async] Sending request...")
    print(f"[DeepSeek API Async] message: {payload}")
    
    timeout = aiohttp.ClientTimeout(total=600)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload, headers=headers) as response:
            elapsed_time = time.time() - start_time
            print(f"[DeepSeek API Async] Response received in {elapsed_time:.2f} seconds")
            print(f"[DeepSeek API Async] Status code: {response.status}")
            
            if response.status != 200:
                error_text = await response.text()
                print(f"[DeepSeek API Async] Error response: {error_text}")
                raise Exception(f"API request failed with status {response.status}: {error_text}")
            
            response_data = await response.json()
            content = response_data["choices"][0]["message"]["content"]
            
            print(f"[DeepSeek API Async] Response length: {len(content)} characters")
            print(f"{'='*60}\n")
            
            return content

async def prompt_deepseek_official_async(message: str, model="deepseek-reasoner"):
    """Async version using DeepSeek official API for concurrent API calls.
    
    Args:
        message: The prompt message to send
        model: DeepSeek model name (default: "deepseek-reasoner" - thinking mode)
               Available models: 
               - "deepseek-reasoner": Advanced reasoning model with thinking process
               - "deepseek-chat": Fast chat model
    
    Environment Variables:
        DEEPSEEK_API_KEY: Your DeepSeek API key from https://platform.deepseek.com/
    """
    import aiohttp
    import os
    import time
    
    # DeepSeek official API endpoint
    url = "https://api.deepseek.com/chat/completions"
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable is not set. Get your API key from https://platform.deepseek.com/")

    print(f"\n{'='*60}")
    print(f"[DeepSeek Official API] Calling model: {model}")
    if model == "deepseek-reasoner":
        print(f"[DeepSeek Official API]  Thinking Mode ENABLED - Advanced reasoning")
    print(f"[DeepSeek Official API] Message length: {len(message)} characters")
    print(f"{'='*60}")
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 0.7,
        "max_tokens": 8000
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    start_time = time.time()
    print(f"[DeepSeek Official API] Sending request...")
    # print(f"[DeepSeek API Async] message: {payload}")
    
    timeout = aiohttp.ClientTimeout(total=600)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload, headers=headers) as response:
            elapsed_time = time.time() - start_time
            print(f"[DeepSeek Official API] Response received in {elapsed_time:.2f} seconds")
            print(f"[DeepSeek Official API] Status code: {response.status}")
            
            if response.status != 200:
                error_text = await response.text()
                print(f"[DeepSeek Official API] Error response: {error_text}")
                raise Exception(f"API request failed with status {response.status}: {error_text}")
            
            response_data = await response.json()
            message_obj = response_data["choices"][0]["message"]
            content = message_obj["content"]
            
            # Check for reasoning content (thinking process)
            reasoning_content = message_obj.get("reasoning_content", "")
            
            print(f"[DeepSeek Official API] Response length: {len(content)} characters")
            if reasoning_content:
                print(f"[DeepSeek Official API]  Reasoning length: {len(reasoning_content)} characters")
                
                # Display full reasoning content in console
                print(f"\n{'='*80}")
                print(f"THINKING PROCESS (FULL):")
                print(f"{'='*80}")
                print(reasoning_content)
                print(f"{'='*80}\n")
                
                # Save full reasoning content to file for inspection
                import json
                reasoning_file = "debug_reasoning_process.txt"
                try:
                    with open(reasoning_file, "w", encoding="utf-8") as f:
                        f.write("="*80 + "\n")
                        f.write("DEEPSEEK REASONER - THINKING PROCESS\n")
                        f.write("="*80 + "\n\n")
                        f.write(reasoning_content)
                        f.write("\n\n" + "="*80 + "\n")
                        f.write("FINAL TRANSLATION RESULT\n")
                        f.write("="*80 + "\n\n")
                        f.write(content)
                    print(f"[DeepSeek Official API]  Full reasoning also saved to: {reasoning_file}")
                except Exception as e:
                    print(f"[DeepSeek Official API] Warning: Could not save reasoning: {e}")
            
            usage = response_data.get('usage', {})
            print(f"[DeepSeek Official API] Token usage: {usage}")
            if 'reasoning_tokens' in usage:
                print(f"[DeepSeek Official API]  Reasoning tokens: {usage['reasoning_tokens']}")
            print(f"{'='*60}\n")
            
            return content

def prompt_nop(message:str):
    """A prompt helper function that does nothing but returns the contained json. This function is useful for testing."""
    return "```json" + message.split("```json")[1]
