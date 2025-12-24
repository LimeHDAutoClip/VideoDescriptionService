import os
import json
import asyncio
import httpx
from dotenv import load_dotenv
from config.logger import logger

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

MAX_RETRIES = 3
TIMEOUT = 60


async def call_llm(transcription: str) -> dict:
    prompt = (
        "Проанализируй транскрипт и верни СТРОГО JSON:\n"
        "{\n"
        '  "description": "короткое описание",\n'
        '  "hook": "четыре слова"\n'
        "}\n\n"
        f"Транскрипт:\n{transcription}"
    )

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.2,
        "max_output_tokens": 300,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "LLM call attempt %d | transcription length=%d",
                attempt,
                len(transcription),
            )

            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers=headers,
                    json=body,
                )
                resp.raise_for_status()
                data = resp.json()

            # Новый формат ответа
            text = data["output"][0]["content"][0]["text"]
            result = json.loads(text)

            if "description" not in result or "hook" not in result:
                raise ValueError(f"Invalid LLM response: {result}")

            # Гарантия 4 слов
            hook_words = result["hook"].split()
            if len(hook_words) != 4:
                logger.warning("Hook not 4 words, trimming: %s", result["hook"])
                result["hook"] = " ".join(hook_words[:4])

            logger.info("LLM call successful")
            return result

        except httpx.HTTPStatusError as e:
            logger.error("OpenAI API error %s: %s", e.response.status_code, e.response.text)

        except Exception as e:
            logger.exception("LLM processing error (attempt %d): %s", attempt, e)

        if attempt < MAX_RETRIES:
            await asyncio.sleep(2 ** attempt)

    raise RuntimeError("Failed to get valid response from LLM after retries")
