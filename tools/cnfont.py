"""Chinese 12x12 1bpp glyphs rendered from SimSun's embedded 12px bitmaps."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np

_font = None
def _f():
    global _font
    if _font is None:
        _font = ImageFont.truetype('C:/Windows/Fonts/simsun.ttc', 12, index=0)
    return _font

def bitmap(ch):
    im = Image.new('1', (16, 16), 0)
    d = ImageDraw.Draw(im); d.fontmode = '1'
    d.text((0, 0), ch, font=_f(), fill=1)
    a = np.array(im, dtype=bool)[1:13, :12]      # SimSun 12px draws ink in rows 1..12
    return a

def pack(a):
    """12x12 bool -> 18 bytes, bit (12*y + x) LSB-first."""
    v = 0
    for y in range(12):
        for x in range(12):
            if a[y, x]: v |= 1 << (12 * y + x)
    return v.to_bytes(18, 'little')

def build(chars):
    return b''.join(pack(bitmap(c)) for c in chars)
