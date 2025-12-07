import os
import json
import httpx
import asyncio
from config.logger import logger

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_RETRIES = 3
TIMEOUT = 60

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

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("LLM call attempt %d for transcription length %d", attempt, len(transcription))
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=body
                )
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

            if "description" not in data or "hook" not in data:
                raise ValueError(f"Invalid LLM response, missing fields: {data}")
            if len(data["hook"].split()) != 4:
                logger.warning("Hook does not contain 4 words, adjusting: %s", data["hook"])
                data["hook"] = " ".join(data["hook"].split()[:4])

            logger.info("LLM call successful")
            return data

        except httpx.RequestError as e:
            logger.warning("Network error during LLM call attempt %d: %s", attempt, e)
        except Exception as e:
            logger.exception("Error processing LLM response attempt %d: %s", attempt, e)

        if attempt < MAX_RETRIES:
            await asyncio.sleep(2 ** attempt)

    logger.error("LLM call failed after %d attempts", MAX_RETRIES)
    raise RuntimeError("Failed to get valid response from LLM")
