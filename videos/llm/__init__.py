from config.logger import logger

USE_LLM_MOCK = True

logger.warning("LLM MODE: MOCK")
from .mock import call_llm
