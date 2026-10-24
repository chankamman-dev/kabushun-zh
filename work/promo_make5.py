"""Promo v4: DS bezel at 2x, longer real play, synthesized SFX (typing / whoosh / hit), music cut to the beat.
work/promo_make4.py OUT.mp4"""
import sys, subprocess, math, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, 'tools')
import objedit

FF = r'G:\ai liabary\thor-capture-pkg6-release\evidence\ci-dependencies\extracted\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe'
W, H, FPS, SR = 1920, 1080, 30, 44228
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out/kabushun_zh_promo.mp4'
BEAT, PHASE = 0.408, 60.295
CG = 'work/promo/cg/'
SFX = []                                                   # (time, kind, gain)


def sfx(t, kind, gain=1.0): SFX.append((t, kind, gain))


def clip(path, ss, dur):
    p = subprocess.run([FF, '-loglevel', 'error', '-ss', str(ss), '-t', str(dur), '-i', path, '-f', 'rawvideo',
                        '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    return [Image.fromarray(f) for f in np.frombuffer(p, np.uint8).reshape(-1, 384, 256, 3)]


def pixel_text(text, scale=3, color=(255, 255, 255), shadow=(10, 10, 30)):
    m = objedit.text_mask(text, 12, 'song'); h, w = m.shape
    a = np.zeros((h + 1, w + 1, 4), np.uint8); a[1:, 1:][m] = shadow + (255,); a[:h, :w][m] = color + (255,)
    im = Image.fromarray(a, 'RGBA'); return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


def caption(im, text, xy, scale=3, color=(255, 255, 255), chars=None, anchor='c'):
    if chars is not None: text = text[:max(0, chars)]
    if not text: return
    t = pixel_text(text, scale, color)
    x, y = xy
    if anchor == 'c': x -= t.width // 2
    im.paste(t, (x, y), t)


typed = {}
def typer(key, text, t0, t, rate=14):
    """number of chars shown at time t; emits a blip per new char (once per key/char)."""
    n = max(0, min(len(text), int((t - t0) * rate)))
    done = typed.get(key, 0)
    if n > done:
        for k in range(done, n):
            if text[k].strip(): sfx(CUR[0] + t0 + (k + 1) / rate, 'blip', 0.5)
        typed[key] = n
    return n


def backdrop(src, dim=0.32):
    small = src.resize((max(1, src.width // 8), max(1, src.height // 8)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
    return Image.blend(Image.new('RGB', (W, H)), small.resize((W, H), Image.BILINEAR), dim)


S2 = 2
BZ = Image.new('RGBA', (512 + 56, 768 + 92), (0, 0, 0, 0))                # DS bezel, drawn once
_d = ImageDraw.Draw(BZ)
_d.rounded_rectangle((0, 0, BZ.width - 1, BZ.height - 1), 26, fill=(28, 30, 38, 255), outline=(70, 74, 88, 255), width=3)
_d.rounded_rectangle((18, 18, BZ.width - 19, 18 + 384 + 10), 6, fill=(8, 8, 10, 255))
_d.rounded_rectangle((18, 18 + 384 + 10 + 34, BZ.width - 19, BZ.height - 19), 6, fill=(8, 8, 10, 255))
_d.line([(30, 18 + 384 + 10 + 17), (BZ.width - 31, 18 + 384 + 10 + 17)], fill=(48, 50, 60, 255), width=2)


def ds(frame, im=None, cx=W // 2, cy=H // 2):
    """256x384 (top over bottom) in a DS bezel at 2x, on a blurred backdrop of itself."""
    if im is None: im = backdrop(frame)
    x0 = cx - BZ.width // 2; y0 = cy - BZ.height // 2
    sh = Image.new('RGBA', (BZ.width + 60, BZ.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 40, BZ.width + 30, BZ.height + 40), 30, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(18)); im.paste(sh, (x0 - 30, y0 - 30), sh)
    im.paste(BZ, (x0, y0), BZ)
    top = frame.crop((0, 0, 256, 192)).resize((512, 384), Image.NEAREST)
    bot = frame.crop((0, 192, 256, 384)).resize((512, 384), Image.NEAREST)
    im.paste(top, (x0 + 28, y0 + 23)); im.paste(bot, (x0 + 28, y0 + 23 + 384 + 44))
    return im, (x0, y0, BZ.width, BZ.height)


def framed(img, scale, f_zoom=0.0, cx=W // 2, cy=H // 2, glow=True):
    """pixel image at an integer-ish scale (small zoom on top), soft shadow, on its blurred backdrop."""
    s = scale * (1 + f_zoom)
    big = img.resize((int(img.width * s), int(img.height * s)), Image.NEAREST)
    im = backdrop(img, 0.4)
    x0 = cx - big.width // 2; y0 = cy - big.height // 2
    if glow:
        sh = Image.new('RGBA', (big.width + 80, big.height + 80), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle((40, 50, big.width + 40, big.height + 50), fill=(0, 0, 0, 170))
        sh = sh.filter(ImageFilter.GaussianBlur(20)); im.paste(sh, (x0 - 40, y0 - 40), sh)
    im.paste(big, (x0, y0))
    return im, (x0, y0, big.width, big.height)


def flash(im, a):
    return Image.blend(im, Image.new('RGB', (W, H), (255, 255, 255)), max(0.0, min(1.0, a))) if a > 0 else im


def shake(im, amp):
    if amp < 1: return im
    out = Image.new('RGB', (W, H)); out.paste(im, (int(np.random.uniform(-amp, amp)), int(np.random.uniform(-amp, amp))))
    return out


def letterbox(im, frac):
    d = ImageDraw.Draw(im); b = int(H * frac)
    d.rectangle((0, 0, W, b), fill=(0, 0, 0)); d.rectangle((0, H - b, W, H), fill=(0, 0, 0)); return im


def wipe(a, b, f):
    out = a.copy(); x = int(a.width * f)
    if x > 0: out.paste(b.crop((0, 0, x, b.height)), (0, 0))
    if 0 < x < a.width: ImageDraw.Draw(out).line([(x, 0), (x, a.height)], fill=(255, 220, 90), width=1)
    return out


ease = lambda f: 0 if f <= 0 else 1 if f >= 1 else f * f * (3 - 2 * f)
cg = lambda n: Image.open(CG + n + '.png').convert('RGB')
scenes = []                                                  # (dur, fn, events(t0) -> None)
CUR = [0.0]

# A. teaser
TEASE = [('dm16_bg01_0', '世界本身就是波。'), ('ta_bg22_1', '你可是赢过本尼菲特的男人吧？'), ('ta_bg32_1', '今后我要在股票上赌上一切。')]
TD = 2.6
timgs = [cg(n) for n, _ in TEASE]
def s_tease(t):
    i = min(2, int(t / TD)); lt = t - i * TD
    im, (x0, y0, bw, bh) = framed(timgs[i], 3, 0.06 * lt / TD)
    im = Image.blend(Image.new('RGB', (W, H)), im, min(1, lt / 0.35))
    n = typer(('tease', i), TEASE[i][1], i * TD + 0.3, t)
    caption(im, TEASE[i][1], (W // 2, y0 + bh + 40), 3, chars=n)
    return im
scenes.append((TD * 3, s_tease, lambda t0: [sfx(t0 + i * TD, 'whoosh', 0.35) for i in range(3)]))

# B. boot
intro = clip('work/promo/cn_intro.mp4', 3.0, 13.0)
scenes.append((13.0, lambda t: ds(intro[min(len(intro) - 1, int(t * FPS))])[0], lambda t0: sfx(t0, 'whoosh', 0.5)))

# C. story pages: JP, then the Chinese wipes over it
PAGES = [2, 3, 4, 7, 8, 9]
jp = [Image.open(f'work/promo/jp_pages/page_{k:02d}.png').convert('RGB') for k in PAGES]
cn = [Image.open(f'work/promo/cn_pages/page_{k:02d}.png').convert('RGB') for k in PAGES]
PG = 2.6
def s_story(t):
    i = min(len(PAGES) - 1, int(t / PG)); lt = t - i * PG
    f = ease((lt - 0.6) / 0.8)
    fr = wipe(jp[i], cn[i], f)
    im, (x0, y0, bw, bh) = ds(fr, backdrop(cn[i]), W // 2 + 180)
    caption(im, '原版', (x0 - 210, y0 + 330), 4, (170, 180, 200) if f < 0.5 else (90, 96, 110))
    caption(im, '中文版', (x0 - 210, y0 + 420), 4, (255, 220, 90) if f >= 0.5 else (90, 96, 110))
    return im
scenes.append((PG * len(PAGES), s_story,
               lambda t0: [sfx(t0 + i * PG + 0.6, 'swipe', 0.45) for i in range(len(PAGES))] + [sfx(t0, 'whoosh', 0.4)]))

PP = lambda k: (Image.open(f'work/promo/pp/{k}_jp.png').convert('RGB'), Image.open(f'work/promo/pp/{k}_cn.png').convert('RGB'))

# C2. picture wall: 4 JP->CN wipes per screen
GRID = [('card2', '交易员卡片'), ('result', '交易结果'), ('trdset', '交易准备'), ('subinfo', '状态画面'),
        ('trials', '试炼标题'), ('menus', '菜单按钮'), ('tabs', '标签页'), ('confirm', '确认条'),
        ('news2', '新闻标题'), ('wall', '交易画面'), ('trial', '试炼模式'), ('card3', '交易员卡片'),
        ('banner', '横幅'), ('touch', '小游戏提示'), ('tut1', '教程图解'), ('tut2', '教程图解'),
        ('contract', '签约名单'), ('bubbles', '对战气泡'), ('stocks', '股票名'), ('ranking', '交易记录'),
        ('shouts', '买卖喊话'), ('ta', '交易技特效字'), ('names', '人名与提示'), ('cardlogo', '卡片收集画面')]
gims = [(PP(k), lab) for k, lab in GRID]
GS = 2.9
def s_grid(t):
    i = min(len(gims) // 4 - 1, int(t / GS)); lt = t - i * GS
    im = backdrop(gims[i * 4][0][1], 0.28)
    caption(im, '图片文字　全部重绘', (W // 2, 34), 4, (255, 220, 90))
    for c in range(4):
        (a, b), lab = gims[i * 4 + c]
        cx = W // 4 * (1 + 2 * (c % 2)); cy = 160 + 450 * (c // 2) + 200
        sc = max(1, min(3, int(min(820 / a.width, 380 / a.height))))
        f = ease((lt - 0.35 - 0.22 * c) / 0.7)
        fr = wipe(a, b, f).resize((a.width * sc, a.height * sc), Image.NEAREST)
        x0, y0 = cx - fr.width // 2, cy - fr.height // 2
        sh = Image.new('RGBA', (fr.width + 60, fr.height + 60), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle((30, 38, fr.width + 30, fr.height + 38), fill=(0, 0, 0, 160))
        sh = sh.filter(ImageFilter.GaussianBlur(14)); im.paste(sh, (x0 - 30, y0 - 30), sh)
        im.paste(fr, (x0, y0))
        caption(im, lab, (cx, cy + 205), 2, (200, 210, 230))
    return Image.blend(Image.new('RGB', (W, H)), im, min(1, lt / 0.15))
scenes.append((GS * (len(gims) // 4), s_grid,
               lambda t0: [sfx(t0 + i * GS + 0.35 + 0.22 * c, 'swipe', 0.3) for i in range(len(gims) // 4) for c in range(4)]))

# D. real play: tutorial buy, trade setup, TRADE START, a full trade at 4x
p3a = clip('work/promo/play3.mp4', 0.0, 7.0); p3b = clip('work/promo/play3.mp4', 33.0, 4.0)
p4a = clip('work/promo/play4.mp4', 0.0, 6.0); p4b = clip('work/promo/play4.mp4', 6.0, 64.0)
PLAY = [(p3a, 1, 7.0, '教程'), (p3b, 1, 4.0, '交易准备'), (p4a, 1, 6.0, '实战'), (p4b, 4, 16.0, '实战　×4')]
PD = sum(d for *_, d, _ in PLAY)
def s_play(t):
    acc = 0
    for frames, sp, d, label in PLAY:
        if t < acc + d or (frames is p4b):
            lt = t - acc
            fr = frames[min(len(frames) - 1, int(lt * FPS * sp))]
            im, (x0, y0, bw, bh) = ds(fr, None, W // 2 + 180)
            caption(im, label, (x0 - 210, y0 + 380), 4, (230, 235, 245))
            return im
        acc += d
scenes.append((PD, s_play, lambda t0: [sfx(t0 + a, 'whoosh', 0.3) for a in np.cumsum([0] + [d for *_, d, _ in PLAY[:-1]])]))

# E. climax montage on the beat (music offset set below so its start sits on a beat)
MONT = ['ta_bg32_1', 'dm08_bg03_0', 'P:shouts', 'ta_bg18_0', 'P:title', 'ta_bg21_0', 'dm13_bg02_0',
        'P:card1', 'dm08_bg05_0', 'P:cardlogo', 'ta_bg22_0', 'P:news1', 'dm06_bg00_0', 'P:boot', 'dm04_bg00_0',
        'P:ta', 'dm01_bg00_0', 'P:ranking', 'dm08_bg06_0', 'P:names', 'dm15_bg00_0', 'dm16_bg01_0']
pairs = {m[2:]: PP(m[2:]) for m in MONT if m.startswith('P:')}
arts = {m: cg(m) for m in MONT if not m.startswith('P:')}
cuts = []; tt = 0.0
for m in MONT:
    d = (4 if m.startswith('P:') else 2) * BEAT; cuts.append((tt, d, m)); tt += d
MD = tt
def s_mont(t):
    s0, d, m = next((c for c in cuts if c[0] <= t < c[0] + c[1]), cuts[-1]); f = (t - s0) / d
    if m.startswith('P:'):
        a, b = pairs[m[2:]]
        fr = wipe(a, b, ease((f - 0.25) / 0.45))
        sc = max(2, min(3, int(min(1300 / fr.width, 760 / fr.height))))
        im, _ = framed(fr, sc, 0.0)
    else:
        im, _ = framed(arts[m], 3.4, 0.08 * f, W // 2 + int((-1) ** MONT.index(m) * 30 * f))
    return flash(im, 0.6 * (1 - (t - s0) / 0.14))
def mont_events(t0):
    for s0, d, m in cuts:
        sfx(t0 + s0, 'kick', 0.55)
        if m.startswith('P:'): sfx(t0 + s0 + 0.25 * d, 'swipe', 0.5)
scenes.append((MD, s_mont, mont_events))

# F. end: Shun, then the title slams in on the big hit
SLAM_M = 99.97
shun = cg('ta_bg32_1'); title = Image.open('work/promo/pair_title_cn.png').convert('RGB')
F = {}
def s_end(t):
    slam, end = F['slam'], F['end']
    if t < slam:
        im, (x0, y0, bw, bh) = framed(shun, 3.4, 0.12 * t / slam)
        im = Image.blend(Image.new('RGB', (W, H)), im, 0.85)
        n = typer('end', '株トレーダー瞬', 1.0, t, 6)
        caption(im, '株トレーダー瞬', (W // 2, y0 + bh + 30), 4, chars=n)
        return im
    lt = t - slam
    im, (x0, y0, bw, bh) = framed(title, 3 if lt > 0.12 else 3.4, 0, W // 2, 430)
    if lt > 0.6:
        n = typer('end2', '简体中文化', slam + 0.6, t, 10)
        caption(im, '简体中文化', (W // 2, y0 + bh + 50), 6, (255, 220, 90), chars=n)
    if lt > 1.8: caption(im, '剧情　界面　图片', (W // 2, y0 + bh + 160), 3, (200, 210, 230))
    im = shake(flash(im, 1 - lt / 0.25), max(0, 18 * (1 - lt / 0.4)))
    return Image.blend(Image.new('RGB', (W, H)), im, max(0, min(1, (end - t) / 1.5)))
scenes.append((None, s_end, lambda t0: (sfx(t0 + F['slam'], 'hit', 1.0), sfx(t0 + F['slam'] - 0.6, 'riser', 0.6))))

# ---- timeline and music map ----
starts = []; acc = 0.0
for d, fn, ev in scenes[:-2]: starts.append(acc); acc += d
E0 = acc                                                     # montage start (video)
M_E0 = PHASE + math.ceil((68.0 - PHASE) / BEAT) * BEAT        # a beat at/after music 68 s
F0 = E0 + MD
F['slam'] = SLAM_M - (M_E0 + MD)
F['end'] = F['slam'] + 7.5
scenes[-1] = (F['end'], s_end, scenes[-1][2])
starts += [E0, F0]
total = F0 + F['end']


def load(path):
    w = wave.open(path); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    return a


story = load('work/promo/cn_story.wav'); intro_a = load('work/promo/cn_intro.wav')
p3 = load('work/promo/play3.wav'); p4 = load('work/promo/play4.wav')
N = int(total * SR) + SR
mix = np.zeros((N, 2), np.float32)
def put(src, s_src, t_dst, dur, gain=1.0, fin=0.3, fout=0.3):
    a = src[int(s_src * SR):int((s_src + dur) * SR)].copy()
    n = len(a); env = np.ones(n, np.float32)
    k = int(fin * SR); env[:k] *= np.linspace(0, 1, k) if k else 1
    k = int(fout * SR); env[n - k:] *= np.linspace(1, 0, k) if k else 1
    i = int(t_dst * SR); mix[i:i + n] += a * env[:, None] * gain
D0 = starts[4]                                               # play section start
put(story, 17.0, 0.0, D0 + 0.4, 0.9, 1.5, 0.6)                # A-C: story BGM
put(intro_a, 3.0, starts[1], 13.0, 0.8, 0.05, 0.3)            # boot jingles
put(p3, 0.0, D0, 7.0, 1.0, 0.4, 0.15); put(p3, 33.0, D0 + 7.0, 4.0, 1.0, 0.15, 0.15)
put(p4, 0.0, D0 + 11.0, PD - 11.0 + 0.3, 1.0, 0.15, 0.5)      # game audio during play
put(story, M_E0 - 0.6, E0 - 0.6, total - E0 + 0.6, 0.95, 0.3, 2.5)


def synth(kind):
    if kind == 'blip':
        t = np.arange(int(0.03 * SR)) / SR; return (np.sign(np.sin(2 * np.pi * 1320 * t)) * np.exp(-t * 90) * 0.12)
    if kind == 'whoosh':
        n = int(0.45 * SR); x = np.random.randn(n); env = np.sin(np.linspace(0, np.pi, n)) ** 2
        k = np.ones(40) / 40; x = np.convolve(x, k, 'same'); return x * env * 0.25
    if kind == 'swipe':
        n = int(0.22 * SR); x = np.random.randn(n); x = np.convolve(x, np.ones(12) / 12, 'same')
        return x * np.linspace(1, 0, n) ** 2 * 0.22
    if kind == 'kick':
        t = np.arange(int(0.18 * SR)) / SR; f = 120 * np.exp(-t * 25) + 45
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * 0.35
    if kind == 'hit':
        t = np.arange(int(1.2 * SR)) / SR; f = 90 * np.exp(-t * 6) + 38
        boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5) * 0.7
        crash = np.convolve(np.random.randn(len(t)), np.ones(3) / 3, 'same') * np.exp(-t * 5) * 0.25
        return boom + crash
    if kind == 'riser':
        n = int(0.6 * SR); x = np.convolve(np.random.randn(n), np.ones(6) / 6, 'same'); return x * np.linspace(0, 1, n) ** 3 * 0.25


np.random.seed(2)
# ---- render video ----
p = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                      '-i', '-', '-i', 'work/promo/_mix.wav', '-map', '0:v', '-map', '1:a',
                      '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                      '-shortest', '-movflags', '+faststart', OUT + '.tmp.mp4'], stdin=subprocess.PIPE) if False else None
frames_out = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                               '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
                               '-pix_fmt', 'yuv420p', 'work/promo/_v.mp4'], stdin=subprocess.PIPE)
XF = 0.25
for si, (dur, fn, ev) in enumerate(scenes):
    CUR[0] = starts[si]; ev(starts[si])
    n = int(round(dur * FPS))
    for f in range(n):
        t = f / FPS
        frame = fn(t)
        if si + 1 < len(scenes) and t > dur - XF and scenes[si + 1][1] is not s_mont:
            CUR[0] = starts[si + 1]; nxt = scenes[si + 1][1](t - dur); CUR[0] = starts[si]
            frame = Image.blend(frame, nxt, (t - (dur - XF)) / XF)
        frames_out.stdin.write(frame.tobytes())
    print('scene', si, round(dur, 2), flush=True)
frames_out.stdin.close(); frames_out.wait()

for t, kind, g in SFX:
    s = synth(kind); i = int(t * SR)
    if 0 <= i < N: seg = s[:N - i]; mix[i:i + len(seg)] += (seg * g)[:, None]
peak = np.abs(mix).max(); mix = mix / max(1.0, peak / 0.95)
w = wave.open('work/promo/_mix.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix[:int(total * SR)] * 32767).astype(np.int16).tobytes()); w.close()
subprocess.run([FF, '-y', '-loglevel', 'error', '-i', 'work/promo/_v.mp4', '-i', 'work/promo/_mix.wav', '-map', '0:v', '-map', '1:a',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT], check=True)
print('total', round(total, 1), 's, sfx', len(SFX), '->', OUT)
