import httpx
import aiofiles
import asyncio
from pathlib import Path
from config.logger import logger

MAX_RETRIES = 3
SAVE_DIR = ".../videos/processed/"

async def download_video(video_url, save_dir=SAVE_DIR):
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    filename = video_url.split("/")[-1].split("?")[0]
    if not filename.endswith(".mp4"):
        filename += ".mp4"
    file_path = Path(save_dir) / filename

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("Downloading video '%s', attempt %d", video_url, attempt)
            async with httpx.AsyncClient(timeout=None) as client:
                resp = await client.get(video_url)
                resp.raise_for_status()
                content = resp.content

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)

            logger.info("Video downloaded successfully: %s", file_path)
            return str(file_path)

        except Exception as e:
            logger.warning("Attempt %d failed for video '%s': %s", attempt, video_url, e)
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 ** attempt)
            else:
                logger.error("Failed to download video after %d attempts: %s", MAX_RETRIES, video_url)
                raise
