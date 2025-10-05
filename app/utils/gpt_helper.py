import os
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def ask_gpt(prompt: str) -> str:
    """
    Fallback GPT-5 answer generator.
    """
    if not OPENAI_API_KEY:
        return "AI service not configured yet. Please check server settings."

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            json={
                "model": "gpt-5",
                "messages": [
                    {"role": "system", "content": "You are an expert auto mechanic assistant named Morshed."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300
            },
            timeout=20
        )

        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip() or "No response from AI."
    except Exception as e:
        return f"Error contacting GPT-5: {e}"

