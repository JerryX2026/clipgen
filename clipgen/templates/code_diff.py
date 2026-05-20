from PIL import ImageDraw
from ..utils import *


def render(draw: ImageDraw, scene: dict):
    """Before/After code diff template."""
    gradient_bg(draw)

    title = scene.get("title", "Code Diff")
    accent = hex_rgb(scene.get("accent", "#00d2ff"))

    draw.text((60, 100), title, fill=accent, font=F(36))
    draw.rectangle([60, 155, 300, 159], fill=hex_rgb("#003355"))

    diff_y = 220
    dh = 400

    # Before panel
    before = scene.get("before", {})
    bw = 460
    rrect(draw, [40, diff_y, 40+bw, diff_y+dh], 10, fill=hex_rgb("#1a0f0a"))
    draw.rectangle([40, diff_y, 40+bw, diff_y+dh], outline=hex_rgb("#ff1744"), width=2)
    draw.text((55, diff_y+8), before.get("label", "Before"), fill=hex_rgb("#ff1744"), font=F(20))

    lcy = diff_y + 45
    for line in before.get("lines", []):
        text = line.get("text", "")
        color = line.get("color", "#c9d1d9")
        draw.text((55, lcy), text, fill=hex_rgb(color), font=F_MONO_S)
        lcy += 30

    # Arrow
    draw.text((512, diff_y+160), "→", fill=hex_rgb("#4a5568"), font=F(48))

    # After panel
    after = scene.get("after", {})
    rrect(draw, [580, diff_y, 580+bw, diff_y+dh], 10, fill=hex_rgb("#0d2817"))
    draw.rectangle([580, diff_y, 580+bw, diff_y+dh], outline=hex_rgb("#00c853"), width=2)
    draw.text((595, diff_y+8), after.get("label", "After"), fill=hex_rgb("#00c853"), font=F(20))

    rcy = diff_y + 45
    for line in after.get("lines", []):
        text = line.get("text", "")
        color = line.get("color", "#c9d1d9")
        draw.text((595, rcy), text, fill=hex_rgb(color), font=F_MONO_S)
        rcy += 30

    # Bottom note
    note = scene.get("note", "")
    if note:
        note_y = 700
        rrect(draw, [100, note_y, W-100, note_y+44], 10, fill=hex_rgb("#0d1f2d"))
        draw.rectangle([100, note_y, W-100, note_y+44], outline=accent, width=1)
        tw = draw.textlength(note, font=F(22))
        draw.text(((W-tw)//2, note_y+11), note, fill=hex_rgb("#ffffff"), font=F(22))
