"""SRT subtitle generation"""

import re
import os


def split_subtitles(script: str, total_duration: float) -> list:
    """Split script into timed subtitle chunks."""
    parts = re.split(r'(?<=[。？！\?])', script)
    parts = [p.strip() for p in parts if p.strip()]
    chunks = []
    for part in parts:
        if len(part) > 20:
            sub = re.split(r'(?<=[，、；：])', part)
            chunks.extend([s.strip() for s in sub if s.strip()])
        else:
            chunks.append(part)
    merged = []
    for chunk in chunks:
        if merged and len(merged[-1]) + len(chunk) < 16:
            merged[-1] += chunk
        else:
            merged.append(chunk)
    total_chars = sum(len(c) for c in merged)
    if total_chars == 0:
        return [(0.0, total_duration, script)]
    current = 0.0
    result = []
    for i, chunk in enumerate(merged):
        dur = len(chunk) / total_chars * total_duration
        end = total_duration if i == len(merged) - 1 else min(current + max(dur, 0.8), total_duration)
        result.append((round(current, 3), round(end, 3), chunk))
        current = end
    return result


def srt_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec % 1) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def gen_srt(subs: list) -> str:
    lines = []
    for i, (st, et, txt) in enumerate(subs, 1):
        lines.extend([str(i), f"{srt_time(st)} --> {srt_time(et)}", txt, ""])
    return "\n".join(lines)


def write_srt(script: str, total_duration: float, output_path: str):
    """Generate and write SRT file."""
    subs = split_subtitles(script, total_duration)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(gen_srt(subs))
    return subs
