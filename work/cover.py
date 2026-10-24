"""Bilibili cover 1920x1080: Shun art right, Chinese title logo + big caption left.  work/cover.py OUT.png"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, 'tools')
import objedit

W, H = 1920, 1080
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out/bilibili_cover.png'
shun = Image.open('work/promo/cg/ta_bg32_1.png').convert('RGB')
title = Image.open('work/promo/pair_title_cn.png').convert('RGB')

bg = shun.resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)
im = Image.blend(Image.new('RGB', (W, H), (4, 8, 24)), bg, 0.55)
art = shun.resize((256 * 6, 192 * 6), Image.NEAREST)                      # 1536x1152
mask = Image.new('L', art.size, 255)                                     # soft left edge into the backdrop
md = ImageDraw.Draw(mask)
for x in range(320):
    md.line([(x, 0), (x, art.height)], fill=int(255 * (x / 320) ** 1.4))
im.paste(art, (W - art.width + 260, -30), mask)

shade = Image.new('L', (W, H), 0); sd = ImageDraw.Draw(shade)          # darken the left for the text
for x in range(1150):
    sd.line([(x, 0), (x, H)], fill=int(200 * (1 - x / 1150) ** 1.1))
im = Image.composite(Image.new('RGB', (W, H), (2, 4, 14)), im, shade)

logo = Image.open('work/promo/logo_cut.png').convert('RGBA')
LS = min(1217 / logo.width, 438 / logo.height)                                     # fills the top-left box
logo = logo.resize((round(logo.width * LS), round(logo.height * LS)), Image.NEAREST)
glow = Image.new('RGBA', (logo.width + 80, logo.height + 80), (0, 0, 0, 0))
glow.paste((0, 0, 0, 255), (40, 52), logo.split()[3])
glow = glow.filter(ImageFilter.GaussianBlur(14))
im.paste(glow, (49 - 40, 93 - 40), glow); im.paste(logo, (49, 93), logo)


def big_text(text, size, fill, stroke, stroke_fill, font='noto_black', shadow=8):
    f = objedit.load_font(font, size)
    w = int(f.getlength(text)) + 4 * stroke + shadow + 10; h = int(size * 1.4) + 2 * stroke + shadow
    lay = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(lay)
    d.text((2 * stroke + shadow, 2 * stroke + shadow), text, font=f, fill=(0, 0, 0, 200), stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
    d.text((2 * stroke, 2 * stroke), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return lay


def pixel(text, scale, color, shadow=(0, 0, 0)):
    m = objedit.text_mask(text, 12, 'song'); h, w = m.shape
    a = np.zeros((h + 1, w + 1, 4), np.uint8); a[1:, 1:][m] = shadow + (255,); a[:h, :w][m] = color + (255,)
    t = Image.fromarray(a, 'RGBA'); return t.resize((t.width * scale, t.height * scale), Image.NEAREST)


t1 = big_text('简体中文完整汉化', 150, (255, 214, 64), 10, (40, 10, 0))
im.paste(t1, (40, 590), t1)
sub = pixel('剧情／界面／图片　全部汉化', 7, (215, 228, 255))
im.paste(sub, (60, 840), sub)
tag = pixel('NDS', 5, (255, 255, 255))
d = ImageDraw.Draw(im); d.rectangle((W - 230, 50, W - 60, 50 + tag.height + 30), fill=(220, 30, 40))
im.paste(tag, (W - 145 - tag.width // 2, 65), tag)
im.save(OUT)
im.resize((1146, 645), Image.LANCZOS).save(OUT.replace('.png', '_small.jpg'), quality=92)
print(OUT)
