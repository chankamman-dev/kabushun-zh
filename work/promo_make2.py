"""Promo, game-styled: blurred game frame as backdrop, DS screens side by side, JP->CN wipes, pixel text.
work/promo_make2.py OUT.mp4"""
import sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, 'tools')
import objedit

FF = r'G:\ai liabary\thor-capture-pkg6-release\evidence\ci-dependencies\extracted\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe'
W, H, FPS = 1920, 1080, 30
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out/kabushun_zh_promo.mp4'
S = 3                                                    # pixel scale of the DS screens


def clip(path, ss, dur):
    p = subprocess.run([FF, '-loglevel', 'error', '-ss', str(ss), '-t', str(dur), '-i', path, '-f', 'rawvideo',
                        '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    return [Image.fromarray(f) for f in np.frombuffer(p, np.uint8).reshape(-1, 384, 256, 3)]


def pixel_text(text, scale=3, color=(255, 255, 255), shadow=(16, 16, 40)):
    """game-like bitmap text: SimSun 12 1-bit, scaled up hard-edged, 1-px drop shadow."""
    m = objedit.text_mask(text, 12, 'song')
    h, w = m.shape
    a = np.zeros((h + 1, w + 1, 4), np.uint8)
    a[1:, 1:][m] = shadow + (255,)
    a[:h, :w][m] = color + (255,)
    im = Image.fromarray(a, 'RGBA')
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


def side_by_side(frame):
    """256x384 (top over bottom) -> 512x192 (top | bottom)."""
    out = Image.new('RGB', (512 + 4, 192), (0, 0, 0))
    out.paste(frame.crop((0, 0, 256, 192)), (0, 0)); out.paste(frame.crop((0, 192, 256, 384)), (260, 0))
    return out


def backdrop(src):
    small = src.resize((src.width // 8 or 1, src.height // 8 or 1), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
    bg = small.resize((W, H), Image.BILINEAR)
    return Image.blend(Image.new('RGB', (W, H)), bg, 0.35)


def stage(img, y=None):
    """backdrop from img + img itself scaled S x, centred (y = top edge, default centred)."""
    big = img.resize((img.width * S, img.height * S), Image.NEAREST)
    im = backdrop(img)
    x0 = (W - big.width) // 2; y0 = (H - big.height) // 2 if y is None else y
    im.paste(big, (x0, y0))
    return im, (x0, y0, big.width, big.height)


def caption(im, text, y, scale=3, color=(255, 255, 255)):
    t = pixel_text(text, scale, color)
    im.paste(t, ((W - t.width) // 2, y), t)


def wipe(a, b, f):
    """JP image a, CN image b (same size); the CN side grows from the left, f in 0..1; divider line."""
    out = a.copy(); x = int(a.width * f)
    if x > 0: out.paste(b.crop((0, 0, x, b.height)), (0, 0))
    if 0 < x < a.width:
        d = ImageDraw.Draw(out); d.line([(x, 0), (x, a.height)], fill=(255, 220, 90), width=1)
    return out


ease = lambda f: 0 if f <= 0 else 1 if f >= 1 else f * f * (3 - 2 * f)
scenes = []

# 1. cold open: the real boot (CAPCOM, Chinese notice, logo animation, title)
intro = clip('work/promo/cn_intro.mp4', 0.0, 16.6)
def s_intro(t):
    fr = side_by_side(intro[min(len(intro) - 1, int(t * FPS))])
    im, _ = stage(fr)
    return im
scenes.append((16.6, s_intro))

# 2. story: each page shows the Japanese original, then the Chinese wipes over it
PAGES = [2, 3, 4, 7, 8, 9]
jp = [side_by_side(Image.open(f'work/promo/jp_pages/page_{k:02d}.png').convert('RGB')) for k in PAGES]
cn = [side_by_side(Image.open(f'work/promo/cn_pages/page_{k:02d}.png').convert('RGB')) for k in PAGES]
PG = 2.8
def s_story(t):
    i = min(len(PAGES) - 1, int(t / PG)); lt = t - i * PG
    fr = wipe(jp[i], cn[i], ease((lt - 0.7) / 0.9))
    im, (x0, y0, bw, bh) = stage(fr, 330)
    caption(im, '日文原版 → 中文版', y0 + bh + 40, 3, (200, 210, 230))
    return im
scenes.append((PG * len(PAGES), s_story))

# 3. play: tutorial trade, as it is
tut = clip('work/promo/cn_tut.mp4', 18.0, 13.0)
def s_tut(t):
    im, _ = stage(side_by_side(tut[min(len(tut) - 1, int(t * FPS))]))
    return im
scenes.append((13.0, s_tut))

# 4. redrawn graphics: wipe from JP to CN on each picture
PAIRS = ['title', 'card', 'ranking', 'cardlogo', 'shouts', 'menus', 'names']
pims = [(Image.open(f'work/promo/pair_{k}_jp.png').convert('RGB'), Image.open(f'work/promo/pair_{k}_cn.png').convert('RGB'))
        for k in PAIRS]
PD = 2.6
def s_pairs(t):
    i = min(len(pims) - 1, int(t / PD)); lt = t - i * PD
    a, b = pims[i]
    fr = wipe(a, b, ease((lt - 0.5) / 0.9))
    sc = max(2, min(4, int(min(1500 / fr.width, 760 / fr.height))))
    big = fr.resize((fr.width * sc, fr.height * sc), Image.NEAREST)
    im = backdrop(b)
    im.paste(big, ((W - big.width) // 2, (H - big.height) // 2 - 40))
    caption(im, '图片文字全部重绘', (H + big.height) // 2 + 10, 3, (200, 210, 230))
    return im
scenes.append((PD * len(PAIRS), s_pairs))

# 5. end: the Chinese title screen, one quiet line
title = Image.open('work/promo/pair_title_cn.png').convert('RGB')
def s_end(t):
    im, (x0, y0, bw, bh) = stage(title, 150)
    caption(im, '株トレーダー瞬　中文化', y0 + bh + 50, 4)
    caption(im, '非官方汉化　请支持正版', y0 + bh + 140, 2, (150, 160, 185))
    a = min(1, (7.0 - t) / 1.5)
    return Image.blend(Image.new('RGB', (W, H)), im, max(0, a))
scenes.append((7.0, s_end))

total = sum(d for d, _ in scenes)
XF = 0.4
p = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                      '-i', '-', '-i', 'work/promo/cn_intro.wav', '-ss', '16.6', '-t', str(total), '-i', 'work/promo/cn_story.wav',
                      '-filter_complex', f'[1:a]atrim=0:16.6[a1];[2:a]afade=t=in:d=1.0,afade=t=out:st={total - 16.6 - 2.5}:d=2.5[a2];'
                                         f'[a1][a2]concat=n=2:v=0:a=1[a]',
                      '-map', '0:v', '-map', '[a]',
                      '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                      '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for si, (dur, fn) in enumerate(scenes):
    n = int(round(dur * FPS))
    for f in range(n):
        t = f / FPS
        frame = fn(t)
        if si + 1 < len(scenes) and t > dur - XF:
            frame = Image.blend(frame, scenes[si + 1][1](t - dur), (t - (dur - XF)) / XF)
        p.stdin.write(frame.tobytes())
    print('scene', si, flush=True)
p.stdin.close(); p.wait()
print('total', round(total, 1), 's ->', OUT)
