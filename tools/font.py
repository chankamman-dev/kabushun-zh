"""ARM9 main font: 16x16 2bpp (LSB-first), 64 bytes/glyph, code = glyph index."""
from PIL import Image
FONT_OFF = 0xF3860  # offset in decompressed arm9
def glyph(a, i, off=FONT_OFF):
    b = a[off + i * 64: off + i * 64 + 64]
    return [[(b[(y * 16 + x) // 4] >> ((x % 4) * 2)) & 3 for x in range(16)] for y in range(16)]
def sheet(a, first, count, out, cols=32, scale=2, off=FONT_OFF):
    col = {0: 255, 1: 0, 2: 110, 3: 180}
    img = Image.new('L', (cols * 17, ((count + cols - 1) // cols) * 17), 255)
    for k in range(count):
        g = glyph(a, first + k, off)
        for y in range(16):
            for x in range(16):
                if g[y][x]: img.putpixel((k % cols * 17 + x, k // cols * 17 + y), col[g[y][x]])
    img.resize((img.width * scale, img.height * scale), Image.NEAREST).save(out)
