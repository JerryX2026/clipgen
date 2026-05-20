"""FFmpeg video rendering"""

import os
import shutil
import subprocess

import imageio_ffmpeg


def render_segment(ffmpeg: str, image_path: str, audio_path: str, srt_path: str,
                   output_path: str, subtitle_style: str = None) -> bool:
    """Render a single video segment from image + audio + subtitles."""
    srt_local = os.path.basename(srt_path)
    shutil.copy2(srt_path, srt_local)

    if subtitle_style is None:
        subtitle_style = (
            "FontName=Microsoft+YaHei,FontSize=16,"
            "PrimaryColour=&H00FFFFFF,BackColour=&H80000000,"
            "BorderStyle=3,Outline=0,Shadow=0,Alignment=2,MarginV=10"
        )

    vf = f"subtitles={srt_local}:force_style='{subtitle_style}'"

    cmd = [ffmpeg, "-y", "-loop", "1", "-i", image_path, "-i", audio_path,
           "-c:v", "libx264", "-tune", "stillimage",
           "-vf", vf,
           "-c:a", "aac", "-b:a", "192k",
           "-pix_fmt", "yuv420p",
           "-f", "mpegts", "-shortest", output_path]

    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        os.remove(srt_local)
    except Exception:
        pass
    return r.returncode == 0


def concat_segments(ffmpeg: str, segments: list, output_path: str) -> bool:
    """Concatenate TS segments into final MP4."""
    concat_file = os.path.join(os.path.dirname(output_path) or ".", "_segments.txt")
    with open(concat_file, "w") as f:
        for seg in segments:
            f.write(f"file '{os.path.abspath(seg)}'\n")

    cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0",
           "-i", concat_file, "-c", "copy", "-movflags", "+faststart", output_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        os.remove(concat_file)
    except Exception:
        pass
    return r.returncode == 0


def get_ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()
