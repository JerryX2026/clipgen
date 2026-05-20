from PIL import ImageDraw
from ..utils import *


def render(draw: ImageDraw, scene: dict):
    """Terminal window template showing command output."""
    gradient_bg(draw)

    title = scene.get("title", "Terminal")
    accent = hex_rgb(scene.get("accent", "#00d2ff"))

    # Section title
    draw.text((60, 100), title, fill=accent, font=F(36))
    draw.rectangle([60, 155, 60+len(title)*20, 159], fill=hex_rgb("#003355"))

    # Terminal window
    tx, ty = 60, 200
    tw_, th_ = 960, 520
    rrect(draw, [tx, ty, tx+tw_, ty+th_], 12, fill=hex_rgb("#0a0a0a"))
    draw.rectangle([tx, ty, tx+tw_, ty+th_], outline=hex_rgb("#333"), width=2)
    draw.rectangle([tx, ty, tx+tw_, ty+30], fill=hex_rgb("#1a1a1a"))
    for cx in [tx+14, tx+32, tx+50]:
        draw.ellipse([cx, ty+10, cx+8, ty+18], fill=hex_rgb("#555"))

    # Lines
    lines = scene.get("lines", [])
    tty = ty + 55
    for line in lines:
        text = line.get("text", "")
        color = line.get("color", "white")
        color_map = {
            "white": hex_rgb("#ffffff"),
            "dim": hex_rgb("#8b949e"),
            "green": hex_rgb("#00e676"),
            "cyan": hex_rgb("#00d2ff"),
            "red": hex_rgb("#ff1744"),
            "orange": hex_rgb("#ff6d00"),
        }
        c = color_map.get(color, hex_rgb("#ffffff"))
        draw.text((tx+20, tty), text, fill=c, font=F_MONO_S)
        tty += 32

    # Bottom note
    note = scene.get("note", "")
    if note:
        note_y = 780
        rrect(draw, [180, note_y, W-180, note_y+48], 10, fill=hex_rgb("#0d1f2d"))
        draw.rectangle([180, note_y, W-180, note_y+48], outline=accent, width=1)
        tw = draw.textlength(note, font=F(22))
        draw.text(((W-tw)//2, note_y+12), note, fill=hex_rgb("#c9d1d9"), font=F(22))
