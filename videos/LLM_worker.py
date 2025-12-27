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
    logger.info("call llm")
    prompt_desc = (
        "Проанализируй транскрипт и верни описание\n"
        f"Транскрипт:\n{transcription}"
    )

    prompt_hook = (
        "Проанализируй транскрипт и верни хук (4 слова)\n"
        f"Транскрипт:\n{transcription}"
    )

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    body_desc = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "user",
                "content": prompt_desc,
            }
        ],
        "temperature": 0.2,
        "max_output_tokens": 300,
    }

    body_hook = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "user",
                "content": prompt_hook,
            }
        ],
        "temperature": 0.2,
        "max_output_tokens": 300,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "LLM call fish2 attempt %d | transcription length=%d",
                attempt,
                len(transcription),
            )

            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp_desc = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers=headers,
                    json=body_desc,
                )

                resp_hook = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers=headers,
                    json=body_hook,
                )
                logger.info(resp_desc.json())
                resp_desc.raise_for_status()
                data_desc = resp_desc.json()

                logger.info(resp_hook.json())
                resp_hook.raise_for_status()
                data_hook = resp_hook.json()

            # Новый формат ответа
            text = data_desc["output"][0]["content"][0]["text"]
            desc = text

            text = data_hook["output"][0]["content"][0]["text"]
            hook = text

            return {"description": desc, "hook": hook}

            # if "description" not in result or "hook" not in result:
            #     raise ValueError(f"Invalid LLM response: {result}")
            #
            # # Гарантия 3 слов
            # hook_words = result["hook"].split()
            # if len(hook_words) != 3:
            #     logger.warning("Hook not 3 words, trimming: %s", result["hook"])
            #     result["hook"] = " ".join(hook_words[:4])
            #
            # logger.info("LLM call successful")
            # return result

        except httpx.HTTPStatusError as e:
            logger.error("OpenAI API error %s: %s", e.response.status_code, e.response.text)

        except Exception as e:
            logger.exception("LLM processing error (attempt %d): %s", attempt, e)

        if attempt < MAX_RETRIES:
            await asyncio.sleep(2 ** attempt)

    raise RuntimeError("Failed to get valid response from LLM after retries")
