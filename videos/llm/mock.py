import asyncio
from config.logger import logger


async def call_llm(transcription: str) -> dict:
    logger.warning("⚠️ USING MOCK LLM (OpenAI disabled)")

    # имитация задержки сети
    await asyncio.sleep(0.3)

    words = transcription.split()

    return {
        "description": "Мок описание видео",
        "hook": " ".join(words[:4]) if len(words) >= 4 else "Пример мок хука",
    }
