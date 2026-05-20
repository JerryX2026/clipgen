"""TTS audio generation via edge-tts"""

import asyncio
import os
import subprocess
from edge_tts import Communicate

from .utils import F_MONO_S


async def generate_audio(script: str, output_path: str, voice: str = "zh-CN-XiaoxiaoNeural",
                         rate: str = "+30%") -> float:
    """Generate TTS audio and return duration in seconds."""
    comm = Communicate(script, voice, rate=rate, pitch="+0Hz")
    await comm.save(output_path)

    # Get duration via ffmpeg
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    r = subprocess.run([ffmpeg, '-i', output_path, '-f', 'null', '-'],
                       capture_output=True, text=True)
    for line in r.stderr.split('\n'):
        if 'Duration' in line:
            parts = line.strip().split(',')[0].split('Duration: ')[1]
            h, m, s = parts.split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 1.0


def generate_audio_sync(script: str, output_path: str, voice: str = "zh-CN-XiaoxiaoNeural",
                        rate: str = "+30%") -> float:
    """Synchronous wrapper for generate_audio."""
    return asyncio.run(generate_audio(script, output_path, voice, rate))
