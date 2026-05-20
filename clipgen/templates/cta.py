from PIL import ImageDraw
from ..utils import *


def render(draw: ImageDraw, scene: dict):
    """Call-to-action / follow prompt template."""
    gradient_bg(draw, bottom="#070a12")
    for x in range(0, W+1, 50):
        draw.line([(x, 0), (x, H)], fill=(12, 20, 35), width=1)
    for y in range(0, H+1, 50):
        draw.line([(0, y), (W, y)], fill=(12, 20, 35), width=1)

    main_text = scene.get("text", "关注我")
    subtitle = scene.get("subtitle", "每天一个 AI 编程效率技巧")
    show_button = scene.get("show_button", True)
    button_text = scene.get("button_text", "下期更精彩 →")

    glow_text(draw, ((W-180)//2, 420), main_text, hex_rgb("#00d2ff"), F(60), glow="#003366", r=4)

    tw = draw.textlength(subtitle, font=F(28))
    draw.text(((W-tw)//2, 560), subtitle, fill=hex_rgb("#c9d1d9"), font=F(28))

    draw.ellipse([100, 200, 180, 280], outline=hex_rgb("#003355"), width=2)
    draw.ellipse([W-180, 740, W-100, 820], outline=hex_rgb("#003355"), width=2)

    if show_button:
        btn_y = 740
        rrect(draw, [340, btn_y, 410, btn_y+70], 35, fill=hex_rgb("#00d2ff"))
        draw.text((358, btn_y+18), "▶", fill=(0, 0, 0), font=F(32))
        tw = draw.textlength(button_text, font=F(26))
        draw.text(((W-tw)//2, btn_y+20), button_text, fill=hex_rgb("#c9d1d9"), font=F(26))
