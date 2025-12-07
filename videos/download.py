import httpx
from pathlib import Path

async def download_video(video_url, save_dir = "media/videos"):
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    filename = video_url.split("/")[-1].split("?")[0]
    if not filename.endswith(".mp4"):
        filename += ".mp4"
    file_path = Path(save_dir) / filename

    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.get(video_url)
        resp.raise_for_status()
        content = resp.content
        with open(file_path, "wb") as f:
            f.write(content)

    return str(file_path)
