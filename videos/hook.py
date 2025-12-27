from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import textwrap
import tempfile
from pathlib import Path


def make_text_image(
    text: str,
    font_path: str,
    video_width: int,
    font_size_ratio: float = 0.02,
    max_chars_per_line: int = 18,
    padding: int = 14,
    line_spacing: int = 12,
    radius: int = 30,
):
    lines = textwrap.wrap(text, width=max_chars_per_line)

    font_size = int(video_width * font_size_ratio)
    font = ImageFont.truetype(font_path, font_size)

    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)

    text_width = max(draw.textlength(line, font=font) for line in lines)
    text_height = sum(
        font.getbbox(line)[3] for line in lines
    ) + line_spacing * (len(lines) - 1)

    img_width = int(text_width + padding * 2)
    img_height = int(text_height + padding * 2)

    img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        (0, 0, img_width, img_height),
        radius=radius,
        fill="white"
    )

    y = padding
    for line in lines:
        line_width = draw.textlength(line, font=font)
        x = (img_width - line_width) // 2
        draw.text((x, y), line, fill="black", font=font)
        y += font.getbbox(line)[3] + line_spacing

    return img


def insert_hook(input_path: str, output_path: str, hook_text: str):
    video = VideoFileClip(input_path)

    img = make_text_image(
        text=hook_text,
        font_path="videos/fonts/Inter-Bold.ttf",
        video_width=video.w,
        font_size_ratio=0.02,
        max_chars_per_line=18,
        padding=14,
        line_spacing=12,
        radius=30,
    )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name, format="PNG")

    text_clip = (
        ImageClip(tmp.name)
        .set_duration(video.duration)
        .set_position("center")
    )

    final = CompositeVideoClip([video, text_clip])

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=video.fps,
        threads=4,
        logger=None
    )
