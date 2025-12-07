import os
import httpx
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def call_llm(transcription):
    prompt = (
        f"Проанализируй транскрипт и верни JSON с двумя полями: "
        f"'description' (коротко) и 'hook' (4 слова):\n\n{transcription}\n\n"
        f"Возвращай только JSON."
    )

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Ты помогаешь генерировать описание и 4-словный хук."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 300,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
        resp.raise_for_status()
        j = resp.json()
        text = j["choices"][0]["message"]["content"]

    try:
        data = json.loads(text)
    except Exception:
        import re
        m = re.search(r"{.*}", text, re.S)
        if m:
            data = json.loads(m.group(0))
        else:
            desc = text.split("Hook:")[0].replace("Description:", "").strip()
            hook = text.split("Hook:")[-1].strip()
            data = {"description": desc, "hook": hook}
    return data
