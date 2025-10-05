import os, json
from openai import OpenAI

def ask_gpt(prompt: str):
    """Fallback call to GPT-5 to generate structured JSON response"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY not set", "causes": ["Unknown"], "advice": "Setup key in Render"}

    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are an automotive assistant for car diagnostics."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    try:
        return json.loads(completion.choices[0].message.content)
    except Exception:
        return {"causes": ["Unknown"], "advice": "Consult a professional mechanic."}


