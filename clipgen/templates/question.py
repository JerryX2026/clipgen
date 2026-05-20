from PIL import ImageDraw
from ..utils import *


def render(draw: ImageDraw, scene: dict):
    """Question/vote template (A/B choice)."""
    gradient_bg(draw)

    question = scene.get("question", "你选哪个？")
    option_a = scene.get("option_a", "A")
    option_b = scene.get("option_b", "B")
    a_color = hex_rgb(scene.get("a_color", "#58a6ff"))
    b_color = hex_rgb(scene.get("b_color", "#00d2ff"))
    comment_prompt = scene.get("comment_prompt", "评论区告诉我")

    # Question
    draw.text((W//2-100, 280), "?", fill=b_color, font=F(92))
    tw = draw.textlength(question, font=F(40))
    draw.text(((W-tw)//2, 440), question, fill=hex_rgb("#ffffff"), font=F(40))

    # Option A
    opt_y = 560
    opt_h = 120
    rrect(draw, [120, opt_y, W-120, opt_y+opt_h], 18, fill=hex_rgb("#0d1117"))
    draw.rectangle([120, opt_y, W-120, opt_y+opt_h], outline=a_color, width=2)
    draw.text((280, opt_y+38), f"A. {option_a}", fill=a_color, font=F(28))

    # Option B
    opt_y2 = opt_y + opt_h + 40
    rrect(draw, [120, opt_y2, W-120, opt_y2+opt_h], 18, fill=hex_rgb("#0a1628"))
    draw.rectangle([120, opt_y2, W-120, opt_y2+opt_h], outline=b_color, width=2)
    draw.text((280, opt_y2+38), f"B. {option_b}", fill=b_color, font=F(28))

    # Comment CTA
    cmt_y = 840
    rrect(draw, [120, cmt_y, W-120, cmt_y+48], 12, fill=hex_rgb("#0d1f2d"))
    draw.rectangle([120, cmt_y, W-120, cmt_y+48], outline=hex_rgb("#ffd600"), width=1)
    tw = draw.textlength(comment_prompt, font=F(22))
    draw.text(((W-tw)//2, cmt_y+13), comment_prompt, fill=hex_rgb("#ffd600"), font=F(22))
