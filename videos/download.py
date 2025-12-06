import httpx
from pathlib import Path

async def download_video(video_url, save_dir = "downloads"):
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    filename = video_url.split("/")[-1].split("?")[0]
    if not filename.endswith(".mp4"):
        filename += ".mp4"
    file_path = Path(save_dir) / filename

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.get(video_url)
            response.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(response.content)
        return str(file_path)
    except Exception as e:
        print(f"Error downloading {video_url}: {e}")
        return None
