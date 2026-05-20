from PIL import ImageDraw
from ..utils import *


def render(draw: ImageDraw, scene: dict):
    """Title card template."""
    gradient_bg(draw)
    for x in range(0, W+1, 60):
        draw.line([(x, 0), (x, H)], fill=(15, 25, 40), width=1)
    for y in range(0, H+1, 60):
        draw.line([(0, y), (W, y)], fill=(15, 25, 40), width=1)

    title = scene.get("title", "Title")
    title_size = scene.get("title_size", 60)
    subtitle = scene.get("subtitle", "")
    tags = scene.get("tags", [])
    accent = hex_rgb(scene.get("accent", "#00d2ff"))

    tw = draw.textlength(title, font=F(title_size))
    draw.text(((W-tw)//2, 380), title, fill=accent, font=F(title_size))

    if subtitle:
        tw = draw.textlength(subtitle, font=F(28))
        draw.text(((W-tw)//2, 500), subtitle, fill=hex_rgb("#c9d1d9"), font=F(28))

    if tags:
        tag_y = 650
        n = len(tags)
        gap = (W - 220 * n) // (n + 1)
        for i, tag in enumerate(tags):
            tx = gap + i * (220 + gap)
            rrect(draw, [tx, tag_y, tx+220, tag_y+50], 20, fill=hex_rgb("#0d1f2d"))
            draw.rectangle([tx, tag_y, tx+220, tag_y+50], outline=accent, width=1)
            draw.text((tx+16, tag_y+12), tag, fill=accent, font=F(20))
