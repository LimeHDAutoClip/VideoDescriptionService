import ffmpeg
from pathlib import Path


def insert_hook_top(input_path: str, output_path: str, hook_text: str):

    hook_text = hook_text.replace("'", "\\'")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    (
        ffmpeg
        .input(input_path)
        .filter(
            "drawtext",
            text=hook_text,
            fontcolor="white",
            fontsize="h*0.06",
            borderw=3,
            bordercolor="black",
            x="(w-text_w)/2",
            y="h*0.03",
        )
        .output(
            output_path,
            vcodec="libx264",
            acodec="copy"
        )
        .overwrite_output()
        .run(quiet=True)
    )
