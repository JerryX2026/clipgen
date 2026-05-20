from PIL import ImageDraw
from ..utils import *


def render(draw: ImageDraw, scene: dict):
    """Comparison split-screen template (Cursor vs Claude Code style)."""
    gradient_bg(draw)
    for x in range(0, W+1, 60):
        draw.line([(x, 0), (x, H)], fill=(15, 25, 40), width=1)
    for y in range(0, H+1, 60):
        draw.line([(0, y), (W, y)], fill=(15, 25, 40), width=1)

    left = scene.get("left", {})
    right = scene.get("right", {})
    left_color = hex_rgb(left.get("color", "#58a6ff"))
    right_color = hex_rgb(right.get("color", "#00d2ff"))
    caption = scene.get("caption", "")

    # Left side
    l_name = left.get("name", "Left")
    l_sub = left.get("subtitle", "")
    tw = draw.textlength(l_name, font=F(52))
    draw.text(((W//2-tw)//2, 250), l_name, fill=left_color, font=F(52))
    if l_sub:
        tw = draw.textlength(l_sub, font=F(24))
        draw.text(((W//2-tw)//2, 330), l_sub, fill=hex_rgb("#8b949e"), font=F(24))

    # Right side
    r_name = right.get("name", "Right")
    r_sub = right.get("subtitle", "")
    tw = draw.textlength(r_name, font=F(52))
    draw.text((W//2+(W//2-tw)//2, 250), r_name, fill=right_color, font=F(52))
    if r_sub:
        tw = draw.textlength(r_sub, font=F(24))
        draw.text((W//2+(W//2-tw)//2, 330), r_sub, fill=hex_rgb("#8b949e"), font=F(24))

    # Center VS badge
    vs_y = 270
    draw.ellipse([W//2-40, vs_y+10, W//2+40, vs_y+90], fill=hex_rgb("#1a2332"))
    draw.ellipse([W//2-38, vs_y+12, W//2+38, vs_y+88], fill=hex_rgb("#0a0e17"))
    tw = draw.textlength("VS", font=F(32))
    draw.text((W//2-tw//2, vs_y+28), "VS", fill=hex_rgb("#ff6d00"), font=F(32))

    # Caption
    if caption:
        tw = draw.textlength(caption, font=F(30))
        draw.text(((W-tw)//2, 520), caption, fill=hex_rgb("#c9d1d9"), font=F(30))
        draw.rectangle([W//2-80, 580, W//2+80, 584], fill=hex_rgb("#4a5568"))

    # Tags
    tags = scene.get("tags", [])
    if tags:
        tag_y = 680
        n = len(tags)
        gap = (W - 220 * n) // (n + 1)
        for i, tag in enumerate(tags):
            tx = gap + i * (220 + gap)
            rrect(draw, [tx, tag_y, tx+220, tag_y+50], 20, fill=hex_rgb("#0d1f2d"))
            draw.rectangle([tx, tag_y, tx+220, tag_y+50], outline=right_color, width=1)
            draw.text((tx+16, tag_y+12), tag, fill=right_color, font=F(20))
