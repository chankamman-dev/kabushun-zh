"""Promo v3 (game-styled, cut to the music): work/promo_make3.py OUT.mp4
Music = the story BGM recorded from the game (cn_story.wav) from MUSIC0 s; the climax montage is cut on its beats."""
import sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, 'tools')
import objedit

FF = r'G:\ai liabary\thor-capture-pkg6-release\evidence\ci-dependencies\extracted\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe'
W, H, FPS = 1920, 1080, 30
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out/kabushun_zh_promo.mp4'
MUSIC0 = 17.0
BEAT, PHASE = 0.408, 60.295                              # measured from the track (146 bpm section)
beat_at = lambda t: PHASE - MUSIC0 + math.ceil((t - (PHASE - MUSIC0)) / BEAT) * BEAT   # next beat >= t
CG = 'work/promo/cg/'


def clip(path, ss, dur):
    p = subprocess.run([FF, '-loglevel', 'error', '-ss', str(ss), '-t', str(dur), '-i', path, '-f', 'rawvideo',
                        '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    return [Image.fromarray(f) for f in np.frombuffer(p, np.uint8).reshape(-1, 384, 256, 3)]


def pixel_text(text, scale=3, color=(255, 255, 255), shadow=(10, 10, 30)):
    m = objedit.text_mask(text, 12, 'song')
    h, w = m.shape
    a = np.zeros((h + 1, w + 1, 4), np.uint8)
    a[1:, 1:][m] = shadow + (255,); a[:h, :w][m] = color + (255,)
    im = Image.fromarray(a, 'RGBA')
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


def caption(im, text, y, scale=3, color=(255, 255, 255), chars=None):
    if chars is not None: text = text[:max(0, chars)]
    if not text: return
    t = pixel_text(text, scale, color)
    im.paste(t, ((W - t.width) // 2, y), t)


def side_by_side(frame):
    out = Image.new('RGB', (516, 192))
    out.paste(frame.crop((0, 0, 256, 192)), (0, 0)); out.paste(frame.crop((0, 192, 256, 384)), (260, 0))
    return out


def backdrop(src, dim=0.35):
    small = src.resize((max(1, src.width // 8), max(1, src.height // 8)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
    return Image.blend(Image.new('RGB', (W, H)), small.resize((W, H), Image.BILINEAR), dim)


def stage(img, scale=3, y=None):
    big = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    im = backdrop(img)
    x0 = (W - big.width) // 2; y0 = (H - big.height) // 2 if y is None else y
    im.paste(big, (x0, y0))
    return im, (x0, y0, big.width, big.height)


def kenburns(img, f, z0=1.0, z1=1.12, dx=0.0, dy=0.0):
    """full-frame pixel art (256x192), zoom z0->z1 over f in 0..1, drift dx/dy (fraction of width)."""
    z = z0 + (z1 - z0) * f
    base = W / img.width * z                             # cover the 16:9 frame
    big = img.resize((int(img.width * base), int(img.height * base)), Image.NEAREST)
    cx = big.width / 2 + dx * W * f; cy = big.height / 2 + dy * H * f
    return big.crop((int(cx - W / 2), int(cy - H / 2), int(cx - W / 2) + W, int(cy - H / 2) + H))


def flash(im, a, color=(255, 255, 255)):
    return Image.blend(im, Image.new('RGB', (W, H), color), max(0.0, min(1.0, a))) if a > 0 else im


def shake(im, amp):
    if amp < 1: return im
    out = Image.new('RGB', (W, H)); out.paste(im, (int(np.random.uniform(-amp, amp)), int(np.random.uniform(-amp, amp))))
    return out


def letterbox(im, frac):
    d = ImageDraw.Draw(im); b = int(H * frac)
    d.rectangle((0, 0, W, b), fill=(0, 0, 0)); d.rectangle((0, H - b, W, H), fill=(0, 0, 0))
    return im


def wipe(a, b, f):
    out = a.copy(); x = int(a.width * f)
    if x > 0: out.paste(b.crop((0, 0, x, b.height)), (0, 0))
    if 0 < x < a.width: ImageDraw.Draw(out).line([(x, 0), (x, a.height)], fill=(255, 220, 90), width=1)
    return out


ease = lambda f: 0 if f <= 0 else 1 if f >= 1 else f * f * (3 - 2 * f)
cg = lambda n: Image.open(CG + n + '.png').convert('RGB')
scenes = []

# A. teaser: three real lines from the game over its art, typed like the dialogue box
TEASE = [('dm16_bg01_0', '世界本身就是波。', 0.0, -0.03), ('ta_bg22_1', '你可是赢过本尼菲特的男人吧？', 0.03, 0.0),
         ('ta_bg32_1', '今后我要在股票上赌上一切。', 0.0, 0.02)]
TD = 2.4
timgs = [cg(n) for n, *_ in TEASE]
def s_tease(t):
    i = min(2, int(t / TD)); lt = t - i * TD
    n, line, dx, dy = TEASE[i]
    im = kenburns(timgs[i], lt / TD, 1.0, 1.1, dx, dy)
    im = Image.blend(Image.new('RGB', (W, H)), im, min(1, lt / 0.35) * 0.85)
    im = letterbox(im, 0.11)
    caption(im, line, H - 170, 4, chars=int((lt - 0.3) * 14))
    return im
scenes.append((TD * 3, s_tease))

# B. the real boot: CAPCOM, Chinese notice, logo animation, title
intro = clip('work/promo/cn_intro.mp4', 3.0, 13.0)
def s_boot(t):
    im, _ = stage(side_by_side(intro[min(len(intro) - 1, int(t * FPS))]))
    return im
scenes.append((13.0, s_boot))

# C. story: JP page, then the Chinese wipes over it
PAGES = [2, 3, 4, 7, 8, 9]
jp = [side_by_side(Image.open(f'work/promo/jp_pages/page_{k:02d}.png').convert('RGB')) for k in PAGES]
cn = [side_by_side(Image.open(f'work/promo/cn_pages/page_{k:02d}.png').convert('RGB')) for k in PAGES]
PG = 2.6
def s_story(t):
    i = min(len(PAGES) - 1, int(t / PG)); lt = t - i * PG
    im, (x0, y0, bw, bh) = stage(wipe(jp[i], cn[i], ease((lt - 0.6) / 0.8)), 3, 300)
    caption(im, '原版　→　中文版', y0 + bh + 44, 3, (190, 200, 225))
    return im
scenes.append((PG * len(PAGES), s_story))

# D. playing: tutorial trade at 1.5x
t0 = sum(d for d, _ in scenes)
GP = 51.0 - t0                                           # the climax must start at video 51 s (music 68 s)
tut = clip('work/promo/cn_tut.mp4', 16.0, GP * 1.5 + 0.5)
def s_play(t):
    im, (x0, y0, bw, bh) = stage(side_by_side(tut[min(len(tut) - 1, int(t * FPS * 1.5))]), 3, 300)
    caption(im, '交易　·　教程　·　新闻', y0 + bh + 44, 3, (190, 200, 225))
    return im
scenes.append((GP, s_play))

# E. climax montage on the beat: art shots and JP->CN picture wipes
MONT = ['ta_bg32_1', 'dm08_bg03_0', 'P:shouts', 'ta_bg18_0', 'dm10_bg00_0', 'P:title', 'ta_bg21_0', 'dm13_bg02_0',
        'P:card', 'dm08_bg05_0', 'ta_bg22_0', 'P:cardlogo', 'dm06_bg00_0', 'dm02_bg00_1', 'P:menus', 'dm04_bg00_0',
        'dm01_bg00_0', 'P:ranking', 'dm08_bg06_0', 'dm11_bg00_2', 'P:names', 'dm15_bg00_0', 'dm16_bg01_0']
LEN = {False: 2, True: 4}                                 # beats per art shot / per picture wipe
pairs = {}
for m in MONT:
    if m.startswith('P:'):
        k = m[2:]; pairs[k] = (Image.open(f'work/promo/pair_{k}_jp.png').convert('RGB'),
                               Image.open(f'work/promo/pair_{k}_cn.png').convert('RGB'))
arts = {m: cg(m) for m in MONT if not m.startswith('P:')}
start0 = beat_at(51.0) - 51.0                            # first cut lands on a beat
cuts = []; tt = start0
for m in MONT:
    d = LEN[m.startswith('P:')] * BEAT; cuts.append((tt, d, m)); tt += d
MD = tt
def s_mont(t):
    seg = next((c for c in cuts if c[0] <= t < c[0] + c[1]), cuts[-1] if t >= start0 else None)
    if seg is None: return flash(kenburns(arts['ta_bg32_1'], 0), 0.6)
    s0, d, m = seg; f = (t - s0) / d
    if m.startswith('P:'):
        a, b = pairs[m[2:]]
        fr = wipe(a, b, ease((f - 0.25) / 0.45))
        sc = max(2, min(5, int(min(1600 / fr.width, 900 / fr.height))))
        big = fr.resize((fr.width * sc, fr.height * sc), Image.NEAREST)
        im = backdrop(b, 0.5); im.paste(big, ((W - big.width) // 2, (H - big.height) // 2))
    else:
        k = MONT.index(m)
        im = kenburns(arts[m], f, 1.04, 1.16, (-1) ** k * 0.03, 0.0)
    return flash(im, 0.55 * (1 - (t - s0) / 0.14))
scenes.append((MD, s_mont))

# F. end: Shun, then the title slams in on the big hit (music 99.97 s)
t0 = sum(d for d, _ in scenes)
SLAM = 99.97 - MUSIC0 - t0
END = SLAM + 7.5
shun = cg('ta_bg32_1'); title = Image.open('work/promo/pair_title_cn.png').convert('RGB')
def s_end(t):
    if t < SLAM:
        im = kenburns(shun, t / SLAM, 1.0, 1.25, 0.0, -0.02)
        im = Image.blend(Image.new('RGB', (W, H)), im, 0.75)
        im = letterbox(im, 0.11)
        caption(im, '株トレーダー瞬', H - 175, 4, chars=int((t - 1.0) * 6))
        return im
    lt = t - SLAM
    sc = 4 if lt > 0.12 else 5
    im, (x0, y0, bw, bh) = stage(title, sc, 70 if sc == 4 else 0)
    if lt > 0.6: caption(im, '简体中文化', y0 + bh + 60, 6, (255, 220, 90), chars=int((lt - 0.6) * 10))
    if lt > 1.8: caption(im, '剧情　界面　图片', y0 + bh + 175, 3, (200, 210, 230))
    im = shake(flash(im, 1 - lt / 0.25), max(0, 18 * (1 - lt / 0.4)))
    return Image.blend(Image.new('RGB', (W, H)), im, max(0, min(1, (END - t) / 1.5)))
scenes.append((END, s_end))

total = sum(d for d, _ in scenes)
XF = 0.25
p = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                      '-i', '-', '-i', 'work/promo/cn_story.wav', '-i', 'work/promo/cn_intro.wav',
                      '-filter_complex',
                      f'[1:a]atrim={MUSIC0}:{MUSIC0 + total},asetpts=PTS-STARTPTS,afade=t=in:d=2,'
                      f'afade=t=out:st={total - 2}:d=2[m];'
                      f'[2:a]atrim=3:16,asetpts=PTS-STARTPTS,adelay={int(TD * 3 * 1000)}|{int(TD * 3 * 1000)},volume=0.9[s];'
                      f'[m][s]amix=inputs=2:duration=first:normalize=0[a]',
                      '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
                      '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
np.random.seed(1)
for si, (dur, fn) in enumerate(scenes):
    n = int(round(dur * FPS))
    for f in range(n):
        t = f / FPS
        frame = fn(t)
        if si + 1 < len(scenes) and t > dur - XF and scenes[si + 1][1] is not s_mont:
            frame = Image.blend(frame, scenes[si + 1][1](t - dur), (t - (dur - XF)) / XF)
        p.stdin.write(frame.tobytes())
    print('scene', si, round(dur, 2), flush=True)
p.stdin.close(); p.wait()
print('total', round(total, 1), 's ->', OUT)
