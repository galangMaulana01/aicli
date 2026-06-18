import time
from openai import OpenAI
from config import NVIDIA_API_KEY, MODEL_NAME

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

def chat(messages: list[dict]) -> str:
    if len(messages) > 12:
        system = [m for m in messages if m["role"] == "system"]
        recent = [m for m in messages if m["role"] != "system"][-10:]
        messages = system + recent

    for attempt in range(4):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.1,
                max_tokens=2048,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            wait = 5 * (attempt + 1)
            print(f"[LLM] Error: {e} | retry {attempt+1}/4 wait {wait}s")
            time.sleep(wait)

    raise RuntimeError("LLM failed after retries")
