from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)

def generate_response(messages):
    """Menghubungkan ke Groq API dengan parameter yang kompatibel."""
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
        )
        return completion
    except Exception as e:
        return str(e)
