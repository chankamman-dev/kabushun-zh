"""Compose the promo video: work/promo_make.py OUT.mp4
Scenes are built from recorded clips (work/promo/*.mp4, 256x384 @30fps) and before/after stills."""
import sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FF = r'G:\ai liabary\thor-capture-pkg6-release\evidence\ci-dependencies\extracted\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe'
W, H, FPS = 1920, 1080, 30
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out/kabushun_zh_promo.mp4'
FB = 'C:/Windows/Fonts/msyhbd.ttc'; FR = 'C:/Windows/Fonts/msyh.ttc'
font = lambda s, b=True: ImageFont.truetype(FB if b else FR, s)
ACC = (255, 196, 64); TXT = (240, 244, 255); SUB = (160, 180, 220)


def clip(path, ss, dur):
    p = subprocess.run([FF, '-loglevel', 'error', '-ss', str(ss), '-t', str(dur), '-i', path, '-f', 'rawvideo',
                        '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    a = np.frombuffer(p, np.uint8).reshape(-1, 384, 256, 3)
    return [Image.fromarray(f) for f in a]


# ---------- background: navy gradient, faint grid, slowly scrolling price line ----------
yy = np.linspace(0, 1, H)[:, None]
base = (np.array([10, 16, 34]) * (1 - yy[..., None]) + np.array([4, 6, 14]) * yy[..., None]) * np.ones((H, W, 1))
BASE = Image.fromarray(base.astype(np.uint8))
d = ImageDraw.Draw(BASE)
for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(20, 30, 58))
for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(20, 30, 58))
rng = np.random.default_rng(7)
walk = np.cumsum(rng.normal(0, 9, 4000)); walk = (walk - walk.min()) / (walk.max() - walk.min())


def background(t):
    im = BASE.copy(); d = ImageDraw.Draw(im)
    off = int(t * 40)
    pts = [(x, 700 - 380 * walk[(x // 6 + off) % 4000]) for x in range(0, W + 6, 6)]
    d.line(pts, fill=(30, 60, 110), width=3)
    return im


def ds(frame, scale=2.5):
    w, h = int(256 * scale), int(384 * scale)
    im = frame.resize((w, h), Image.NEAREST)
    fr = Image.new('RGB', (w + 12, h + 12), (60, 80, 120)); fr.paste(im, (6, 6))
    return fr


def shadow_text(img, xy, text, f, fill, anchor='la', sh=3):
    d = ImageDraw.Draw(img)
    d.text((xy[0] + sh, xy[1] + sh), text, font=f, fill=(0, 0, 0), anchor=anchor)
    d.text(xy, text, font=f, fill=fill, anchor=anchor)


def tag(img, xy, text, color):
    d = ImageDraw.Draw(img); f = font(34)
    b = d.textbbox(xy, text, font=f, anchor='mm')
    d.rounded_rectangle((b[0] - 22, b[1] - 10, b[2] + 22, b[3] + 10), 12, fill=color)
    d.text(xy, text, font=f, fill=(10, 14, 28), anchor='mm')


def side_caption(img, x, y, title, lines):
    shadow_text(img, (x, y), title, font(64), ACC)
    for i, l in enumerate(lines): shadow_text(img, (x, y + 110 + i * 66), l, font(40, False), TXT, sh=2)


# ---------- scenes: each is (duration_s, render(t_local) -> Image) ----------
scenes = []

def s_title(t):
    im = background(t)
    a = min(1, t / 0.8)
    logo = Image.open('work/promo/pair_title_cn.png').resize((768, 576), Image.NEAREST)
    im.paste(logo, ((W - 768) // 2, 70))
    shadow_text(im, (W // 2, 720), '株トレーダー瞬', font(96), TXT, 'mm')
    shadow_text(im, (W // 2, 840), '简体中文汉化版', font(80), ACC, 'mm')
    shadow_text(im, (W // 2, 950), 'Nintendo DS  ·  剧情 / 界面 / 图片  完整汉化', font(40, False), SUB, 'mm', 2)
    return Image.blend(Image.new('RGB', (W, H)), im, a)
scenes.append((5.0, s_title))

intro = clip('work/promo/cn_intro.mp4', 4.2, 11.0)
def s_intro(t):
    im = background(t + 5)
    im.paste(ds(intro[min(len(intro) - 1, int(t * FPS))]), (180, 54))
    side_caption(im, 980, 300, '开场全中文', ['注意事项画面重绘', '标题动画 Logo「股票交易员瞬」', '标题画面 Logo 重绘'])
    return im
scenes.append((11.0, s_intro))

PAGES = [2, 3, 4, 7, 8, 9]                         # matching dialogue pages (work/pages.py), fully shown
jpp = [ds(Image.open(f'work/promo/jp_pages/page_{k:02d}.png').convert('RGB'), 2.2) for k in PAGES]
cnp = [ds(Image.open(f'work/promo/cn_pages/page_{k:02d}.png').convert('RGB'), 2.2) for k in PAGES]
PG = 16.0 / len(PAGES)
def s_story(t):
    im = background(t + 16)
    i = min(len(PAGES) - 1, int(t / PG)); lt = t - i * PG
    a, b = jpp[i], cnp[i]
    if lt < 0.3 and i > 0:                               # short cross-fade between pages
        f = lt / 0.3; a = Image.blend(jpp[i - 1], a, f); b = Image.blend(cnp[i - 1], b, f)
    im.paste(a, (300, 150)); im.paste(b, (1040, 150))
    tag(im, (300 + 287, 118), '原版', (170, 180, 200)); tag(im, (1040 + 287, 118), '汉化版', ACC)
    shadow_text(im, (W // 2, 48), '剧情全文翻译 · 4704 条台词逐句校对', font(50), TXT, 'mm', 2)
    return im
scenes.append((16.0, s_story))

tut = clip('work/promo/cn_tut.mp4', 18.0, 14.0)
def s_tut(t):
    im = background(t + 32)
    im.paste(ds(tut[min(len(tut) - 1, int(t * FPS))]), (180, 54))
    side_caption(im, 980, 300, '交易与教程', ['交易界面、股票名称', '教程图解逐张重绘', '交易技按钮与说明'])
    return im
scenes.append((14.0, s_tut))

PAIRS = [('title', '标题 Logo'), ('card', '交易员卡片（36 张）'), ('ranking', '交易记录'),
         ('cardlogo', '卡片收集画面'), ('shouts', '买卖喊话与特效字'), ('menus', '菜单与按钮'),
         ('names', '人名、横幅与提示')]
pims = {k: (Image.open(f'work/promo/pair_{k}_jp.png'), Image.open(f'work/promo/pair_{k}_cn.png')) for k, _ in PAIRS}
PD = 3.2
def s_pairs(t):
    im = background(t + 46)
    i = min(len(PAIRS) - 1, int(t / PD)); k, label = PAIRS[i]
    a, b = pims[k]
    s = min(820 / a.width, 760 / a.height); s = max(1, math.floor(s * 2) / 2)
    A = a.resize((int(a.width * s), int(a.height * s)), Image.NEAREST); B = b.resize(A.size, Image.NEAREST)
    lt = t - i * PD; fade = min(1, lt / 0.35)
    y = 200 + (760 - A.height) // 2
    im.paste(A, (500 - A.width // 2, y)); im.paste(B, (1420 - B.width // 2, y))
    d = ImageDraw.Draw(im); d.polygon([(925, 560), (995, 600), (925, 640)], fill=ACC)
    tag(im, (500, 160), '原版', (170, 180, 200)); tag(im, (1420, 160), '汉化版', ACC)
    shadow_text(im, (W // 2, 60), '图片文字全部重绘 · ' + label, font(50), TXT, 'mm', 2)
    return Image.blend(background(t + 46), im, fade) if fade < 1 else im
scenes.append((PD * len(PAIRS), s_pairs))

def s_outro(t):
    im = background(t + 70)
    logo = Image.open('work/promo/pair_title_cn.png').resize((640, 480), Image.NEAREST)
    im.paste(logo, ((W - 640) // 2, 90))
    shadow_text(im, (W // 2, 660), '株トレーダー瞬  简体中文汉化版', font(72), TXT, 'mm')
    shadow_text(im, (W // 2, 770), '剧情 · 界面 · 图片  完整汉化', font(48), ACC, 'mm', 2)
    shadow_text(im, (W // 2, 900), '非官方粉丝汉化，仅供学习交流，请支持正版', font(36, False), SUB, 'mm', 2)
    a = min(1, (6.5 - t) / 1.2)
    return Image.blend(Image.new('RGB', (W, H)), im, max(0, a))
scenes.append((6.5, s_outro))

total = sum(d for d, _ in scenes)
XF = 0.5
music_ss = 16.6
p = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                      '-i', '-', '-ss', str(music_ss), '-t', str(total), '-i', 'work/promo/cn_story.wav',
                      '-af', f'afade=t=in:d=1.5,afade=t=out:st={total - 2.5}:d=2.5',
                      '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                      '-shortest', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
t0 = 0.0
for si, (dur, fn) in enumerate(scenes):
    n = int(round(dur * FPS))
    for f in range(n):
        t = f / FPS
        frame = fn(t)
        if si + 1 < len(scenes) and t > dur - XF:                 # crossfade into the next scene
            nxt = scenes[si + 1][1](t - dur)
            frame = Image.blend(frame, nxt, (t - (dur - XF)) / XF)
        p.stdin.write(frame.tobytes())
    t0 += dur
    print('scene', si, 'done', flush=True)
p.stdin.close(); p.wait()
print('total', total, 's ->', OUT)
