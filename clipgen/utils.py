"""Shared utilities: colors, fonts, drawing helpers"""

import os
from PIL import Image, ImageDraw, ImageFont

FONT_CACHE = {}
FONT_PATHS = [
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]

try:
    F_MONO = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 28)
    F_MONO_S = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 22)
except Exception:
    fm = ImageFont.load_default()
    F_MONO = fm
    F_MONO_S = fm

W = 1080
H = 1920


def hex_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def get_font(size: int):
    if size not in FONT_CACHE:
        for path in FONT_PATHS:
            try:
                FONT_CACHE[size] = ImageFont.truetype(path, size, encoding="unic")
                break
            except Exception:
                continue
        else:
            FONT_CACHE[size] = ImageFont.load_default()
    return FONT_CACHE[size]


# Preload common sizes
FS = {18:24,20:26,22:28,24:30,26:34,28:36,30:38,32:40,34:42,36:44,
      38:46,40:48,42:50,44:52,48:56,50:60,52:64,56:68,60:72,64:76,
      72:86,80:96,92:104}
for s in list(range(14, 106, 2)):
    get_font(s)


def F(size: int):
    return get_font(FS.get(size, size))


def rrect(draw, xy, r, **kw):
    x1, y1, x2, y2 = xy
    draw.pieslice([x1, y1, x1+r*2, y1+r*2], 180, 270, **kw)
    draw.pieslice([x2-r*2, y1, x2, y1+r*2], 270, 360, **kw)
    draw.pieslice([x1, y2-r*2, x1+r*2, y2], 90, 180, **kw)
    draw.pieslice([x2-r*2, y2-r*2, x2, y2], 0, 90, **kw)
    draw.rectangle([x1+r, y1, x2-r, y2], **kw)
    draw.rectangle([x1, y1+r, x2, y2-r], **kw)


def gradient_bg(draw, top="#0a0e17", bottom="#0d1b2a"):
    tc = hex_rgb(top)
    bc = hex_rgb(bottom)
    for y in range(H):
        t = y / H
        draw.line([(0, y), (W, y)], fill=(
            int(tc[0] + (bc[0]-tc[0])*t),
            int(tc[1] + (bc[1]-tc[1])*t),
            int(tc[2] + (bc[2]-tc[2])*t),
        ))


def glow_text(draw, xy, text, color, font, glow="#003366", r=2):
    x, y = xy
    c = hex_rgb(color) if isinstance(color, str) else color
    g = hex_rgb(glow) if isinstance(glow, str) else glow
    for dx, dy in [(r,0),(-r,0),(0,r),(0,-r),(r,r),(-r,r),(r,-r),(-r,-r)]:
        draw.text((x+dx, y+dy), text, fill=g, font=font)
    draw.text((x, y), text, fill=c, font=font)


def new_image():
    return Image.new("RGB", (W, H))


def save_slide(img, path: str):
    img.save(path)
    return path
