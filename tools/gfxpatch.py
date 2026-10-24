"""Graphic text replacements, applied to the ROM's files at build time."""
import numpy as np
from collections import Counter
import objedit, bgedit
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

# trading-art names, in obj_fnt section order (14..53, repeated 54..93)
TA_BUTTON = ['气势', '转换心情', '动摇', '双刃动摇', '预料之中', '买入煽动', '卖出煽动', '狂欢', '冷却',
             '下单失误', '全力买入', '全力卖出', '千元极致', '渔翁之利', '同生共死', '胆量对决', '强制平仓',
             '花吹雪', '一击', '拍落', '洗牌', '安魂曲', '确信', '冰之吐息', '庄家团', '大佬风范', '新星风范',
             '无声', '抵消', '万元恶戏', '神之手', '恶魔之手', '开眼', '分红', '背水一战', '气场', '泄露',
             '再次泄露', '头版刊登', '万元恶戏']


def place(text, width, size=12, font='song'):
    gap = {1: 0, 2: 12, 3: 4}.get(len(text), 0)
    m = objedit.text_mask(text, size, font, spacing=gap)
    return objedit.squeeze(m, width)


def ta_buttons(of, report):
    for k, name in enumerate(TA_BUTTON):
        for si in (14 + k, 54 + k):
            idx, own, pal = of.canvas(si, 0)
            # button body: the 64-wide part; text area = columns between the end caps
            ink = (idx == 1) | (idx == 3)
            body = idx[:, :64] if si < 54 else idx[:, -64:]
            off = 0 if si < 54 else idx.shape[1] - 64
            x_lo, x_hi = (off + 12, off + 64) if si < 54 else (off + 0, off + 52)
            y_lo, y_hi = 3, 17
            new = idx.copy()
            for y in range(y_lo, y_hi):
                row = idx[y, x_lo:x_hi]
                vals = [v for v in row if v not in (1, 3)]
                bg = Counter(vals).most_common(1)[0][0] if vals else 6
                for x in range(x_lo, x_hi):
                    new[y, x] = bg
            m = place(name, 50)
            h, w = m.shape
            y0 = 4 + max(0, (12 - h) // 2)
            x0 = x_lo + (x_hi - x_lo - w) // 2
            for yy in range(h):
                for xx in range(w):
                    if m[yy, xx]:
                        new[y0 + yy, x0 + xx] = 1
                        if yy + 1 >= h or not m[yy + 1, xx]:
                            if y0 + yy + 1 < y_hi and new[y0 + yy + 1, x0 + xx] != 1:
                                new[y0 + yy + 1, x0 + xx] = 7
            of.write(own, new)
    report.append(f'TA buttons: {2 * len(TA_BUTTON)} sprites')


def apply(rom, report):
    fnt = rom.getFileByName('obj_fnt.bin'); dat = rom.getFileByName('obj_dat.bin')
    of = objedit.ObjFile(fnt, dat)
    ta_buttons(of, report)
    ta_titles(of, report)
    stock_names(of, report)
    buttons_misc(of, report)
    trade_labels(of, report)
    bubbles(of, report)
    notices(of, report)
    plain_sprites(of, report)
    banners(of, report)
    small_glyphs(of, report)
    small_lists(of, report)
    contract_list(of, report)
    segment_sprites(of, report)
    trial_titles(of, report)
    misc_sprites(of, report)
    more_sprites(of, report)
    shouts(of, report)
    ta_effects(of, report)
    trader_cards(of, report)
    tutorial_pics(of, report)
    intro_logo(of, report)
    chapter_titles(of, report)
    assert len(of.data) == len(fnt)
    rom.setFileByName('obj_fnt.bin', bytes(of.data))
    bg_files(rom, report)
    wallpapers(rom, report)
    news(rom, report)
    logos(rom, report)
    ranking(rom, report)
    card_logo(rom, report)
    watermarks(rom, report)
    wall_logos(rom, report)
    boot_screens(rom, report)
    news_tickers(rom, report)
    status_card(rom, report)


TA_TITLE = ['气势', '转换心情', '动摇', '双刃动摇', '预料之中', '买入煽动', '卖出煽动', '狂欢', '冷却',
            '下单失误！', '全力买入煽动', '全力卖出煽动', '千元极致', '渔翁之利', '同生共死', '胆量对决！',
            '强制平仓！', '花吹雪', '一击', '拍落', '洗牌', '安魂曲', '确信', '冰之吐息', '庄家团', '大佬风范',
            '新星风范', '无声交易', '抵消', '一万元恶作剧', '看不见的神之手', '看不见的恶魔之手', '开眼！', '分红',
            '背水一战', '气场', '泄露', '再次泄露', '头版刊登', '气场']


def gray_text(text, height, max_w, font='yahei_b', stroke=2):
    """white text with black outline -> (alpha, luminance) arrays sized to height."""
    from PIL import Image, ImageDraw, ImageFont
    size = height
    f = objedit.load_font(font, size)
    w = int(f.getlength(text)) + 2 * stroke + 4
    im = Image.new('LA', (w, size * 2), (0, 0))
    d = ImageDraw.Draw(im)
    d.text((stroke + 1, 2), text, font=f, fill=(255, 255), stroke_width=stroke, stroke_fill=(0, 255))
    a = np.asarray(im)
    ys = np.where(a[..., 1].any(1))[0]; xs = np.where(a[..., 1].any(0))[0]
    a = a[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]
    img = Image.fromarray(a, 'LA')
    h = a.shape[0]
    if h != height or a.shape[1] > max_w:
        nw = min(max_w, round(a.shape[1] * height / h))
        img = img.resize((nw, height), Image.LANCZOS)
    a = np.asarray(img)
    return a[..., 1], a[..., 0]


def gray_index(alpha, lum, pal):
    """map to grayscale palette indices 1..15 (0 = transparent)."""
    grays = pal[1:, 0].astype(int)
    idx = 1 + np.abs(lum[..., None].astype(int) - grays[None, None, :]).argmin(-1)
    return np.where(alpha > 100, idx, 0)


def ta_titles(of, report):
    n = 0
    for k, name in enumerate(TA_TITLE):
        for si in [278 + k] + ([183, 187] if name == '同生共死' else []):
            f = of.sec(si); fr = objedit.objgfx.frames(of.dat[si])
            idx, own, pal = of.canvas(si, 0)
            img_i, parts = fr[0]
            x0 = min(p[2] for p in parts); y0 = min(p[3] for p in parts)
            big = [p for p in parts if objedit.objgfx.SIZES[(p[1] >> 6, (p[1] >> 4) & 3)][1] >= 32]
            if not big: continue
            bx0 = min(p[2] for p in big) - x0; by0 = min(p[3] for p in big) - y0
            bx1 = max(p[2] + 64 for p in big) - x0; by1 = by0 + 32
            region = idx[by0:by1, bx0:bx1]
            ys, xs = np.where(region > 0)
            if not len(ys): continue
            th = ys.max() - ys.min() + 1                       # original text height
            new = idx.copy(); new[by0:by1, bx0:bx1] = np.where(region >= 0, 0, region)
            al, lum = gray_text(name, th, bx1 - bx0 - 4)
            gi = gray_index(al, lum, pal)
            ty = by0 + ys.min(); tx = bx0 + xs.min()
            h = min(gi.shape[0], new.shape[0] - ty)
            w = min(gi.shape[1], bx1 - tx, new.shape[1] - tx)
            sub = new[ty:ty + h, tx:tx + w]
            sub[:] = np.where(gi[:h, :w] > 0, gi[:h, :w], sub)
            of.write(own, new); n += 1
    report.append(f'TA titles: {n} sprites')


STOCKS = ['竹柴电器', '索尼克', '半导泰克斯', 'V等离子', '阿达寇达', '天王堂', '刚线上', '半田汽车', '丸菱汽车',
          '严岛建设', '下町建设', '丸菱重工业', '丸菱不动产', '小小家居', '大卫管理', '全日铁', '帝国矿业',
          '飞龙啤酒', '综合食品', '天海制果', '丸菱银行', '帝国银行', '帝国损保', '桐神乐证券', '爱证券',
          '利斯库鲁', '大日石油', '软科技', '天堂之门', 'MMA创投', '意象点', '盖亚制药', '高天原制药',
          '德川电力', '太阁燃气', '三岛屋', '大余', '九十九', '阿迪诺', '日轮航空', 'NR铁道', '湾岸汽船',
          '白犬快递', '四国制纸', '极东化学', '支仓橡胶', '维纳斯研究所', '丸菱商事', '帝国商事', '山冈兴业',
          '东京纺织', '生物疗法', '烤肉杉太', '满福寿司', '胜屋', '新欧米伽', '东都度假村', '京阪球团',
          '每朝放送', '王牌广报堂', 'DDT', 'AMIVA', '风力发电社', '娱乐节拍', '哈莫尼克斯',
          '天王堂', '刚线上', '半田汽车', '丸菱汽车']           # obj_fnt 96..164


def draw_shadowed(canvas, mask, y0, x0, ink, shadow):
    h, w = mask.shape
    H, W = canvas.shape
    for yy in range(h):
        for xx in range(w):
            if not mask[yy, xx]: continue
            for dy, dx in ((1, 0), (0, 1), (1, 1)):
                Y, X = y0 + yy + dy, x0 + xx + dx
                if 0 <= Y < H and 0 <= X < W and canvas[Y, X] != ink: canvas[Y, X] = shadow
    for yy in range(h):
        for xx in range(w):
            if mask[yy, xx] and 0 <= y0 + yy < H and 0 <= x0 + xx < W: canvas[y0 + yy, x0 + xx] = ink


def stock_names(of, report):
    for k, name in enumerate(STOCKS):
        si = 96 + k
        idx, own, pal = of.canvas(si, 0)
        new = np.where(idx >= 0, 0, idx)
        m = objedit.text_mask(name, 12, 'song', spacing=1 if len(name) <= 3 else 0)
        if len(name) <= 2: m = objedit.text_mask(name, 12, 'song', spacing=8)
        m = objedit.squeeze(m, idx.shape[1] - 3)
        h, w = m.shape
        draw_shadowed(new, m, 1 + max(0, (12 - h) // 2), (idx.shape[1] - 1 - w) // 2, 5, 1)
        of.write(own, new)
    report.append(f'stock names: {len(STOCKS)} sprites')


def erase_rows(new, rect):
    """fill rect with each row's most common index (gradient backgrounds)."""
    x0, y0, x1, y1 = rect
    for y in range(y0, y1):
        row = [v for v in new[y, x0:x1] if v >= 0]
        if row: new[y, x0:x1] = np.where(new[y, x0:x1] >= 0, Counter(row).most_common(1)[0][0], new[y, x0:x1])


def erase_inpaint(new, rect, text_idx):
    """replace text-coloured pixels by the nearest non-text pixel in the same row."""
    x0, y0, x1, y1 = rect
    src = new.copy()
    for y in range(y0, y1):
        for x in range(x0, x1):
            if src[y, x] in text_idx:
                for d in range(1, 64):
                    for xx in (x - d, x + d):
                        if x0 <= xx < x1 and src[y, xx] >= 0 and src[y, xx] not in text_idx:
                            new[y, x] = src[y, xx]; break
                    else: continue
                    break


def stamp(new, m, y0, x0, ink, shadow=None, outline=None):
    H, W = new.shape; h, w = m.shape
    def put(Y, X, v):
        if 0 <= Y < H and 0 <= X < W and new[Y, X] >= 0: new[Y, X] = v
    if outline is not None:
        for yy in range(h):
            for xx in range(w):
                if m[yy, xx]:
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1): put(y0 + yy + dy, x0 + xx + dx, outline)
    if shadow is not None:
        for yy in range(h):
            for xx in range(w):
                if m[yy, xx]:
                    for dy, dx in ((1, 0), (0, 1), (1, 1)): put(y0 + yy + dy, x0 + xx + dx, shadow)
    for yy in range(h):
        for xx in range(w):
            if m[yy, xx]: put(y0 + yy, x0 + xx, ink)


def bold(m):
    b = m.copy(); b[:, 1:] |= m[:, :-1]
    return b


def label(of, si, frames, rect, text, ink, size=12, font='song', shadow=None, outline=None, thick=False,
          erase='rows', text_idx=(), align='center', spacing=0, valign='center'):
    for fi in frames:
        idx, own, pal = of.canvas(si, fi)
        new = idx.copy()
        if erase == 'rows': erase_rows(new, rect)
        elif erase == 'inpaint': erase_inpaint(new, rect, set(text_idx))
        elif erase.startswith('const:'):
            v = int(erase[6:]); x0, y0, x1, y1 = rect
            new[y0:y1, x0:x1] = np.where(new[y0:y1, x0:x1] >= 0, v, new[y0:y1, x0:x1])
        m = objedit.text_mask(text, size, font, spacing=spacing)
        if thick: m = bold(m)
        x0, y0, x1, y1 = rect
        m = objedit.squeeze(m, x1 - x0)
        h, w = m.shape
        tx = x0 + (x1 - x0 - w) // 2 if align == 'center' else x0 if align == 'left' else x1 - w
        ty = y0 + (y1 - y0 - h) // 2 if valign == 'center' else y0
        stamp(new, m, ty, tx, ink if not isinstance(ink, dict) else ink[fi],
              shadow if not isinstance(shadow, dict) else shadow[fi], outline)
        of.write(own, new)


def buttons_misc(of, report):
    label2(of, 13, [0, 1, 2], (5, 8, 44, 25), '返回', size=14, spacing=2)
    label2(of, 13, [3, 4, 5], (4, 7, 42, 25), '交易所', size=13)
    label2(of, 13, [6, 7, 8], (3, 8, 42, 25), '北滨市', size=13)
    report.append('misc buttons')


def text_rgba(text, size, font, ink, outline=None, stroke=1, shadow=None, spacing=0):
    from PIL import Image, ImageDraw, ImageFont
    f = objedit.load_font(font, size)
    w = sum(int(f.getlength(c)) + spacing for c in text) + 8
    im = Image.new('RGBA', (w, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if font == 'song' and size <= 12: d.fontmode = '1'
    if shadow is not None:
        x = 4
        for c in text:
            d.text((x + 1, 5), c, font=f, fill=tuple(shadow) + (255,)); x += int(f.getlength(c)) + spacing
    x = 4
    for c in text:
        kw = dict(stroke_width=stroke, stroke_fill=tuple(outline) + (255,)) if outline is not None else {}
        d.text((x, 4), c, font=f, fill=tuple(ink) + (255,), **kw); x += int(f.getlength(c)) + spacing
    a = np.asarray(im)
    ys = np.where(a[..., 3].any(1))[0]; xs = np.where(a[..., 3].any(0))[0]
    return a[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]


def fit(rgba, max_w, max_h):
    from PIL import Image
    h, w = rgba.shape[:2]
    s = min(1.0, max_w / w, max_h / h)
    if s < 1.0:
        img = Image.fromarray(rgba, 'RGBA').resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
        rgba = np.asarray(img)
    return rgba


def nearest(pal, rgb, allowed):
    p = pal[allowed].astype(int)
    return allowed[int(((p - np.asarray(rgb, int)) ** 2).sum(1).argmin())]


def label2(of, si, frames, rect, text, ink=(255, 255, 255), size=13, font='yahei_b', outline=None, stroke=1,
           shadow=None, align='center', spacing=0, erase=True, far=120, keep0=True, dy=0):
    """AA text blended over the (erased) background and snapped to the sprite palette."""
    for fi in frames:
        idx, own, pal = of.canvas(si, fi)
        new = idx.copy()
        x0, y0, x1, y1 = rect
        if isinstance(ink, str):            # 'auto': the text colour = commonest non-background colour
            cnt = Counter()
            for y in range(y0, y1):
                row = [v for v in idx[y, x0:x1] if v > 0]
                if not row: continue
                bg = Counter(row).most_common(1)[0][0]
                for v in row:
                    if v != bg and ((pal[v].astype(int) - pal[bg].astype(int)) ** 2).sum() > 60 * 60: cnt[v] += 1
            light = [k for k, _ in cnt.most_common() if pal[k].astype(int).sum() > 200]
            v = light[0] if light else (cnt.most_common(1)[0][0] if cnt else 15)
            inkv = tuple(int(c) for c in pal[v])
        else:
            inkv = ink
        inkc = np.asarray(inkv, int)
        allowed = np.arange(1 if keep0 else 0, len(pal))
        if erase:
            for y in range(y0, y1):
                allrow = [v for v in idx[y, x0:x1] if v >= 0]
                if allrow and allrow.count(0) * 2 >= len(allrow):
                    seg = new[y, x0:x1]; new[y, x0:x1] = np.where(seg >= 0, 0, seg); continue
                row = [v for v in idx[y, x0:x1] if v > 0 and ((pal[v].astype(int) - inkc) ** 2).sum() > far * far]
                if row:
                    bg = Counter(row).most_common(1)[0][0]
                    seg = new[y, x0:x1]; new[y, x0:x1] = np.where(seg > 0, bg, seg)
        t = fit(text_rgba(text, size, font, inkv, outline, stroke, shadow, spacing), x1 - x0, y1 - y0)
        h, w = t.shape[:2]
        tx = x0 + (x1 - x0 - w) // 2 if align == 'center' else x0 if align == 'left' else x1 - w
        ty = y0 + (y1 - y0 - h) // 2 + dy
        for yy in range(h):
            for xx in range(w):
                a = t[yy, xx, 3] / 255.0
                Y, X = ty + yy, tx + xx
                if a <= 0.05 or not (0 <= Y < new.shape[0] and 0 <= X < new.shape[1]) or new[Y, X] < 0: continue
                base = pal[new[Y, X]].astype(float) if new[Y, X] > 0 else t[yy, xx, :3].astype(float)
                rgb = base * (1 - a) + t[yy, xx, :3] * a
                new[Y, X] = nearest(pal, rgb, allowed)
        of.write(own, new)


def label_core(idx, rect, text, ink=None, shadow=None, size=12, font='song', thick=False,
               align='center', spacing=0, valign='center', dy=0, bg=None, outline=None, dx=0, text_idx=None,
               erase_from=None):
    """pixel-art label on an index canvas: erase rect with each row's background (edge columns),
    draw a 1-bit glyph mask in the ink index (auto = commonest non-background index), optional
    shadow ('auto' = second commonest) / outline index."""
    x0, y0, x1, y1 = rect
    rowbg = []; cnt = Counter()
    for y in range(y0, y1):
        row = [v for v in idx[y, x0:x1] if v >= 0]
        edge = [v for v in list(idx[y, x0:x0 + 2]) + list(idx[y, x1 - 2:x1]) if v >= 0]
        if bg == 'right': edge = [v for v in idx[y, x1:x1 + 4] if v >= 0]
        b = Counter(edge or row).most_common(1)[0][0] if (edge or row) else 0
        if bg is not None and bg != 'right': b = bg
        rowbg.append(b)
        for v in row:
            if v != b: cnt[v] += 1
    order = [k for k, _ in cnt.most_common()]
    inkv = ink if ink is not None else (order[0] if order else 15)
    shv = shadow
    if shadow == 'auto': shv = next((k for k in order if k != inkv), None)
    new = idx.copy()
    if erase_from == 'above':         # copy the two rows above the rect (keeps 2-row dither phases)
        for y in range(y0, y1):
            src = y0 - 2 + ((y - y0) % 2)
            new[y, x0:x1] = idx[src, x0:x1]
    elif text_idx is not None:          # in-paint: text pixels <- nearest same-parity background pixel
        ti = set(text_idx); src = idx.copy()
        for y in range(y0, y1):
            for x in range(x0, x1):
                if src[y, x] not in ti: continue
                for d in (2, -2, 4, -4, 6, -6, 8, -8, 1, -1, 3, -3, 10, -10, 12, -12, 16, -16, 20, -20):
                    xx = x + d
                    if 0 <= xx < src.shape[1] and src[y, xx] >= 0 and src[y, xx] not in ti:
                        new[y, x] = src[y, xx]; break
    else:
        for k, y in enumerate(range(y0, y1)):
            seg = new[y, x0:x1]; new[y, x0:x1] = np.where(seg >= 0, rowbg[k], seg)
    m = objedit.text_mask(text, size, font, spacing=spacing)
    if thick: m = bold(m)
    m = objedit.squeeze(m, x1 - x0)
    h, w = m.shape
    tx = (x0 + (x1 - x0 - w) // 2 if align == 'center' else x0 if align == 'left' else x1 - w) + dx
    ty = (y0 + (y1 - y0 - h) // 2 if valign == 'center' else y0) + dy
    stamp(new, m, ty, tx, inkv, shv, outline)
    return new


def label_px(of, si, frames, rect, text, **kw):
    for fi in frames:
        idx, own, pal = of.canvas(si, fi)
        of.write(own, label_core(idx, rect, text, **kw))


def trade_labels(of, report):
    for fi in range(len(objedit.objgfx.frames(of.dat[624]))):
        label_px(of, 624, [fi], (9, 2, 68, 14), '东证1部', thick=True)
        label_px(of, 624, [fi], (9, 26, 68, 38), '东证2部', thick=True)
    for fi in range(len(objedit.objgfx.frames(of.dat[703]))):
        for y in (0, 40, 80):
            if y < 80: label_px(of, 703, [fi], (9, y + 2, 68, y + 14), '东证1部' if y == 0 else '东证2部', thick=True)
            label_px(of, 703, [fi], (34, y + 17, 68, y + 31), '股票', shadow='auto')
    for fi, (a, c) in enumerate([('还有', '股票可选'), ('还有', '股票要选')]):
        label_px(of, 625, [fi], (0, 0, 64, 12), a, ink=15, outline=2, bg=0, align='left', dy=0)
        label_px(of, 625, [fi], (30, 15, 58, 27), '支', ink=2, shadow=1, bg=15, align='right')
        label_px(of, 625, [fi], (0, 31, 64, 43), c, ink=15, outline=2, bg=0, align='left')
    report.append('trade labels')


def detect_text(canvas, pal, rect, ink_bright=True):
    """ink = brightest (or darkest) index in rect; shadow = index found mostly right/below ink."""
    x0, y0, x1, y1 = rect
    sub = canvas[y0:y1, x0:x1]
    vals = [v for v in set(sub.ravel().tolist()) if v >= 0]
    lum = {v: int(pal[v].astype(int).sum()) for v in vals}
    ink = max(vals, key=lum.get) if ink_bright else min(vals, key=lum.get)
    tot = Counter(sub.ravel().tolist()); adj = Counter()
    ys, xs = np.where(sub == ink)
    for y, x in zip(ys, xs):
        for dy, dx in ((0, 1), (1, 0), (1, 1)):
            if y + dy < sub.shape[0] and x + dx < sub.shape[1]:
                v = int(sub[y + dy, x + dx])
                if v != ink: adj[v] += 1
    shadow = None
    for v, c in adj.most_common():
        if c / tot[v] > 0.5 and tot[v] > 4: shadow = v; break
    return ink, shadow


def bg_label(bf, mi, rect, text, ts=0, ink_bright=None, bg_idx=None, **kw):
    """label on background map mi (pixel rect in screen coords)."""
    canvas = bf.canvas(mi, ts, (0, 0, 32, 24))
    if bg_idx == 'auto':
        x0, y0, x1, y1 = rect
        edge = list(canvas[y0, x0:x1]) + list(canvas[y1 - 1, x0:x1]) + list(canvas[y0 + 1, x0:x1])
        bg_idx = tuple(v for v, c in Counter(int(v) for v in edge).items() if c > 3)
    if bg_idx is not None:
        x0, y0, x1, y1 = rect
        tidx = tuple(v for v in set(canvas[y0:y1, x0:x1].ravel().tolist()) if v not in bg_idx)
        kw = dict(kw, text_idx=tidx)
        if kw.pop('ink_dark', False):
            p = bf.pal[min(ts, len(bf.pal) - 1)]
            allv = set(canvas[y0:y1, x0:x1].ravel().tolist())
            kw['ink'] = min(allv, key=lambda v: int(p[v].astype(int).sum()))
    if ink_bright is not None:
        ink, sh = detect_text(canvas, bf.pal[min(ts, len(bf.pal) - 1)], rect, ink_bright)
        kw = dict(kw, ink=ink, shadow=sh, text_idx=tuple(v for v in (ink, sh) if v is not None))
    new = label_core(canvas, rect, text, **kw)
    x0, y0, x1, y1 = rect
    cr = (x0 // 8, y0 // 8, (x1 + 7) // 8, (y1 + 7) // 8)
    sub = new[cr[1] * 8:cr[3] * 8, cr[0] * 8:cr[2] * 8]
    bf.edit(mi, ts, cr, sub)


HDR = dict(ink_bright=True, thick=True, align='left', dy=1)
LBL = dict(ink_bright=False, align='left')
RANK = dict(bg_idx='auto', ink_dark=True, thick=True, align='left')
TS0_MAPS = {'trd_info.bin': [0, 1, 2], 'sub_info.bin': [0, 2, 3, 4, 8, 9], 'trdset00.bin': [1, 2, 3, 4, 6], 'trdset01.bin': [1, 2, 3, 4, 5, 6]}
BLUE = dict(erase_from='above', ink_dark=True, bg_idx='auto', thick=True, align='left')
HDRD = dict(ink_bright=False, thick=True, align='left', dy=1)
TRDSET = {
    'sub_info.bin': [(0, (58, 31, 146, 45), '交易员等级', BLUE),
                     (0, (72, 113, 142, 127), '持有股票数', BLUE),
                     (0, (58, 149, 154, 163), '交易员点数', BLUE),
                     (0, (56, 169, 82, 183), '资产', BLUE),
                     (2, (16, 9, 200, 26), '股票确认', HDRD),
                     (3, (22, 9, 220, 26), '交易追加功能确认', HDRD), (8, (22, 9, 220, 26), '交易追加功能确认', HDRD),
                     (4, (22, 9, 220, 26), '交易技确认', HDRD), (9, (22, 9, 220, 26), '交易技确认', HDRD),
                     (2, (12, 89, 72, 103), '每股收益', LBL), (2, (12, 105, 72, 119), '每股资产', LBL),
                     (2, (12, 121, 72, 135), '成长性', LBL)],
    'trd_info.bin': [(0, (58, 63, 143, 78), '交易员等级', dict(erase_from='above', ink_dark=True, bg_idx='auto',
                                                               thick=True, align='left'))],
    'trdset00.bin': [(1, (16, 9, 200, 26), '单人交易准备', HDR), (6, (16, 9, 200, 26), '单人交易准备', HDR),
                     (2, (16, 9, 200, 26), '选择使用股票', HDR), (3, (16, 9, 200, 26), '装备交易技', HDR),
                     (4, (23, 9, 200, 26), '图表设置', HDR),
                     (2, (13, 89, 72, 103), '每股收益', LBL),
                     (2, (13, 105, 72, 119), '每股资产', LBL),
                     (2, (13, 121, 72, 135), '成长性', LBL)],
    'trdset01.bin': [(1, (16, 9, 200, 26), '对战交易准备', HDR), (2, (16, 9, 200, 26), '选择使用股票', HDR),
                     (3, (16, 9, 200, 26), '装备交易技', HDR), (4, (16, 9, 200, 26), '对手的情报', HDR),
                     (5, (16, 9, 200, 26), '对手的情报', HDR), (6, (23, 9, 200, 26), '图表设置', HDR),
                     (4, (58, 62, 143, 78), '交易员等级', RANK),
                     (2, (11, 89, 64, 103), '每股收益', LBL),
                     (2, (11, 105, 64, 119), '每股资产', LBL),
                     (2, (11, 121, 64, 135), '成长性', LBL)],
}


R1 = dict(LBL, ts=1)
RH = dict(ink=194, shadow=223, bg_idx=(235, 229), thick=True, align='left', ts=1)
TRDSET['result00.bin'] = (
    [(m, (55, 40, 126, 55), '交易结果', RH) for m in (0, 1, 2, 5, 6)] +
    [(m, (12, 58, 96, 72), t, R1) for m, t in ((0, '使用金额'), (6, '使用金额'), (1, '利润'), (2, '经过天数'), (5, '获得TP'))] +
    [(m, (12, 74, 96, 88), t, R1) for m, t in ((0, '利润'), (6, '利润'), (5, '胜利金额'))] +
    [(m, (12, 90, 96, 104), t, R1) for m, t in ((0, '利润率'), (6, '利润率'), (5, '获得股票'))] +
    [(m, (12, 122, 96, 136), '大获利', R1) for m in (0, 6)] +
    [(m, (12, 144, 110, 158), '合计获得TP', R1) for m in (0, 6)] +
    [(3, r, t, kw) for _, r, t, kw in TRDSET['sub_info.bin'][:4]])
TS_MAPS = {'result00.bin': {0: [3, 4], 1: [0, 1, 2, 5, 6]}, 'trial_bg.bin': {0: [0], 1: [1, 2, 3]}}
T1 = dict(HDR, ts=1); TL = dict(LBL, ts=1)
TRDSET['trial_bg.bin'] = (
    [(1, (18, 11, 120, 27), '条件选择', T1), (1, (40, 39, 216, 55), '关于试炼模式', dict(TL, align='center'))] +
    [(m, (15, 11, 160, 27), '试炼模式的记录', T1) for m in (2, 3)] +
    [(m, (68, y, 124, y + 14), t, TL) for m, t in ((2, '经过天数'), (3, '利润')) for y in (84, 124, 164)])
def bg_note(bf, mi, rect, text, erase, ts=0, ink=None, size=12, font='song', thick=False, dy=0):
    """label on ruled-notebook backgrounds.  erase: ('mode',) row mode of the whole line;
    ('win', sx0, sx1) tile the same rows from a clean window; ('dark', L) in-paint pixels darker than L
    from their row neighbours.  ink = darkest colour of the old text unless given."""
    work = bf.__dict__.setdefault('_work', {})
    if (mi, ts) not in work: work[(mi, ts)] = bf.canvas(mi, ts, (0, 0, 32, 24))
    c = work[(mi, ts)].copy(); P = bf.pal[min(ts, len(bf.pal) - 1)].astype(int); L = P.sum(1)
    x0, y0, x1, y1 = rect
    sub = c[y0:y1, x0:x1]
    if ink is None: ink = int(min(set(sub.ravel().tolist()), key=lambda v: L[v]))
    new = c.copy()
    if erase[0] == 'mode':
        for y in range(y0, y1): new[y, x0:x1] = Counter(c[y].tolist()).most_common(1)[0][0]
    elif erase[0] == 'win':
        sx0, sx1 = erase[1], erase[2]
        for x in range(x0, x1): new[y0:y1, x] = c[y0:y1, sx0 + (x - x0) % (sx1 - sx0)]
    elif erase[0] == 'dark':                  # grey/black text pixels (low saturation, darker than L)
        S = P.max(1) - P.min(1)
        txt = lambda v: L[v] < erase[1] and S[v] < 48
        for y in range(y0, y1):
            for x in range(x0, x1):
                if not txt(c[y, x]): continue
                for d in (1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 8, -8, 10, -10, 12, -12, 16, -16):
                    if x0 <= x + d < x1 and not txt(c[y, x + d]): new[y, x] = c[y, x + d]; break
    m = objedit.text_mask(text, size, font)
    if thick: m = bold(m)
    m = objedit.squeeze(m, x1 - x0 - 1)
    h, w = m.shape
    stamp(new, m, y0 + (y1 - y0 - h) // 2 + dy, x0 + 1, ink)
    work[(mi, ts)] = new
    cr = (x0 // 8, y0 // 8, (x1 + 7) // 8, (y1 + 7) // 8)
    bf.edit(mi, ts, cr, new[cr[1] * 8:cr[3] * 8, cr[0] * 8:cr[2] * 8])


NOTE = ([(m, (20, 8, 126, 23), '单人交易记录', ('mode',)) for m in range(4)] +
        [(m, (172, 8, 226, 23), t, ('dark', 640)) for m, t in ((0, '利润'), (2, '利润率'), (3, '获得TP'))] +
        [(m, (56, y, 112, y + 14), t, ('win', 120, 176)) for m, t in ((0, '利润'), (2, '利润率'), (3, '获得TP'))
         for y in (32, 84, 136)] +
        [(m, (56, y, 112, y + h), t, ('win', 120, 176)) for m in range(4) for y0 in (32, 84, 136)
         for y, h, t in ((y0 + 16, 13, '使用金额'), (y0 + 29, 14, '投资期间'))] +
        [(4, (16, 8, 172, 23), '自由对战交易记录', ('mode',)), (4, (172, 8, 226, 23), '综合战绩', ('dark', 640)),
         (4, (86, 82, 102, 96), '战', ('win', 56, 80)), (4, (144, 82, 160, 96), '胜', ('win', 110, 140)),
         (4, (201, 82, 217, 96), '败', ('win', 162, 190)), (4, (88, 112, 118, 126), '胜率', ('win', 120, 148))])


def ranking(rom, report):
    bf = bgedit.BgFile(rom.getFileByName('ranking.bin'))
    for mi, rect, text, er in NOTE: bg_note(bf, mi, rect, text, er)
    added = bf.commit()
    assert len(bf.tiles[0]) // 64 <= 1024, 'ranking: too many tiles'
    rom.setFileByName('ranking.bin', bf.build())
    report.append(f'ranking.bin: {len(NOTE)} labels, {added} new tiles')


def bg_files(rom, report):
    for name, specs in TRDSET.items():
        bf = bgedit.BgFile(rom.getFileByName(name))
        for mi, rect, text, kw in specs:
            bg_label(bf, mi, rect, text, **kw)
        added = bf.commit(TS_MAPS[name] if name in TS_MAPS else ({0: TS0_MAPS.get(name)} if name in TS0_MAPS else None))
        assert len(bf.tiles[0]) // 64 <= 1024, f'{name}: too many tiles'
        rom.setFileByName(name, bf.build())
        report.append(f'{name}: {len(specs)} labels, {added} new tiles')


def _clusters(rows, gap=2):
    out = []
    for y in rows:
        if out and y - out[-1][-1] <= gap: out[-1].append(y)
        else: out.append([y])
    return out


def _inpaint(new, rect, ti, skip_bg=True):
    """text pixels <- nearest non-text pixel in the row; pixels equal to the row's background
    (e.g. a shadow colour that is also a band colour) are left alone."""
    x0, y0, x1, y1 = rect
    src = new.copy()
    for y in range(max(0, y0), min(new.shape[0], y1)):
        row = [int(v) for v in list(src[y, :max(0, x0)]) + list(src[y, x1:]) if v > 0]
        if not row: row = [int(v) for v in src[y] if v > 0 and v not in ti]
        rbg = Counter(row).most_common(1)[0][0] if row else 0
        for x in range(max(0, x0), min(new.shape[1], x1)):
            v = src[y, x]
            if v not in ti or (skip_bg and v == rbg): continue
            for d in (1, -1, 2, -2, 3, -3, 4, -4, 6, -6, 8, -8, 12, -12):
                xx = x + d
                if x0 <= xx < x1 and src[y, xx] >= 0 and src[y, xx] not in ti:
                    new[y, x] = src[y, xx]; break
            else:
                new[y, x] = rbg


def bubble(of, si, fi, name, lines, INK=14, SH=7, TAG=13, TAGO=1):
    idx, own, pal = of.canvas(si, fi)
    new = idx.copy()
    H, W = idx.shape
    # name tag: tag ink pixels in the top rows
    ys, xs = np.where(idx[:16] == TAG)
    if len(ys) and name:
        r = (xs.min() - 3, ys.min() - 2, xs.max() + 3, ys.max() + 3)
        _inpaint(new, r, {TAG, TAGO, 15}, skip_bg=False)
        m = objedit.text_mask(name, 12, 'song')
        m = objedit.squeeze(m, r[2] - r[0] - 2)
        h, w = m.shape
        stamp(new, m, ys.min(), xs.max() + 1 - w, TAG, None, TAGO)
    # text lines
    rows = [y for y in range(16, H) if (idx[y] == INK).any()]
    cl = _clusters(rows)
    for k, c in enumerate(cl):
        cxs = np.where((idx[c[0]:c[-1] + 1] == INK).any(0))[0]
        x0, x1 = int(cxs.min()), int(cxs.max()) + 1
        _inpaint(new, (x0 - 1, c[0] - 1, x1 + 3, c[-1] + 3), {INK, SH})
        if k < len(lines) and lines[k]:
            m = objedit.text_mask(lines[k], 12, 'song')
            m = objedit.squeeze(m, x1 - x0 + 1)
            stamp(new, m, c[0], x0, INK, SH)
    of.write(own, new)


def bubbles(of, report):
    n = 0
    for line in (ROOT / 'text/cn/bubbles.txt').read_text(encoding='utf8').splitlines():
        if not line.strip() or line.startswith('#'): continue
        key, name, *ls = line.split('|')
        si, fi = map(int, key.split(':'))
        bubble(of, si, fi, name, ls); n += 1
    report.append(f'versus bubbles: {n}')


NOTICES = [
    # (section, [frames], rect, text, kw)
    (610, [3], (4, 14, 172, 29), '决定买方还是卖方。', {}),
    (610, [3], (4, 31, 172, 46), '请从中选择一张卡片。', {}),
    (611, [4], (4, 15, 172, 29), '牛市标准·试炼', {}),
    (611, [4], (4, 31, 172, 45), '只能买入的基本规则。', {}),
    (611, [4], (4, 46, 172, 60), '先赚到一定金额者获胜。', {}),
    (611, [5], (4, 15, 172, 29), '熊市标准·试炼', {}),
    (611, [5], (4, 31, 172, 45), '只能做空的基本规则。', {}),
    (611, [5], (4, 46, 172, 60), '先赚到一定金额者获胜。', {}),
    (611, [6], (4, 15, 172, 29), '８射８杀', {}),
    (611, [6], (4, 31, 172, 45), '先连续８次获利了结者胜。', {}),
    (611, [6], (4, 46, 172, 60), '失败就从第１次重来。', {}),
    (535, [0, 1, 2], (4, 15, 172, 29), '要结束交易吗？', {}),
    (667, [4], (4, 15, 172, 29), '交易技的应对方法', {}),
    (667, [4], (4, 31, 172, 45), '用触控笔把下屏的花瓣', {}),
    (667, [4], (4, 46, 172, 60), '弹到画面外。', {}),
    (668, [4], (4, 15, 172, 29), '交易技的应对方法', {}),
    (668, [4], (4, 31, 172, 45), '用触控笔连续点下屏', {}),
    (668, [4], (4, 46, 172, 60), '敲碎冰块。', {}),
    (513, [1], (6, 14, 170, 30), '未选择使用的股票！', {}),
    (540, [2], (6, 14, 170, 30), '未选择使用的股票！', {}),
    (673, [0, 1, 2, 3], (6, 4, 80, 16), '签约所需条件', dict(align='left', ink=5, outline=1, sh=None, bg='right')),
    (673, [0, 1, 2, 3], (8, 16, 110, 28), '交易员等级', dict(align='left', ink=1, sh=3, bg='right')),
    (673, [0, 1, 2, 3], (8, 32, 53, 44), '赌注金额', dict(align='left', ink=1, sh=3, bg=4)),
]


def notices(of, report):
    for si, frames, rect, text, kw in NOTICES:
        kw = dict(kw); sh = kw.pop('sh', 'auto')
        label_px(of, si, frames, rect, text, shadow=sh, **kw)
    report.append(f'notices: {len(NOTICES)} labels')


def label_dark(of, si, frames, rect, text, lum_max=330, thick=False, size=12, align='left', dx=0):
    """dark text on a varying background: in-paint every dark pixel in rect, redraw in the
    commonest dark colour."""
    for fi in frames:
        idx, own, pal = of.canvas(si, fi)
        x0, y0, x1, y1 = rect
        sub = idx[y0:y1, x0:x1]
        dark = {int(v) for v in set(sub.ravel().tolist()) if v >= 0 and int(pal[v].astype(int).sum()) < lum_max}
        cnt = Counter(int(v) for v in sub.ravel() if v in dark)
        if not cnt: continue
        ink = cnt.most_common(1)[0][0]
        new = idx.copy()
        _inpaint(new, rect, dark, skip_bg=False)
        m = objedit.text_mask(text, size, 'song')
        if thick: m = bold(m)
        m = objedit.squeeze(m, x1 - x0)
        h, w = m.shape
        tx = (x0 if align == 'left' else x0 + (x1 - x0 - w) // 2) + dx
        stamp(new, m, y0 + (y1 - y0 - h) // 2, tx, ink)
        of.write(own, new)


MENU = [(512, [3], '选择使用股票'), (512, [7, 10], '图表设置'), (512, [8], '装备交易技'),
        (512, [9], '对手的情报'), (541, [2], '选择使用股票'), (541, [10, 1], '装备交易技'),
        (541, [12, 13], '单人交易记录')]


def menu_buttons(of, report):
    for si, frames, text in MENU:
        label_dark(of, si, frames, (18, 5, 150, 18), text)
    report.append('menu buttons')


def read_sprite_list(path):
    """'@a,b' sets the sections; 'frame|text' lines -> {section: {frame: text}}."""
    out, secs = {}, []
    for line in (ROOT / path).read_text(encoding='utf8').splitlines():
        if not line.strip() or line.startswith('#'): continue
        if line.startswith('@'): secs = [int(s) for s in line[1:].split(',')]; continue
        f, text = line.split('|', 1)
        for s in secs: out.setdefault(s, {})[int(f)] = text
    return out


def frame_keys(of, si):
    keys = []
    for fi in range(len(objedit.objgfx.frames(of.dat[si]))):
        try: idx, own, pal = of.canvas(si, fi)
        except ValueError: keys.append(None); continue
        keys.append(idx.tobytes())
    return keys


def plain_sprites(of, report, path='text/cn/sprites_plain.txt'):
    """one-colour text sprites (no outline): clear and redraw with 12px SimSun."""
    n = 0
    for si, texts in read_sprite_list(path).items():
        keys = frame_keys(of, si)
        bykey = {keys[f]: t for f, t in texts.items() if f < len(keys) and keys[f]}
        for fi, k in enumerate(keys):
            if k not in bykey: continue
            idx, own, pal = of.canvas(si, fi)
            vals = [v for v in idx.ravel().tolist() if v > 0]
            if not vals: continue
            ink = Counter(vals).most_common(1)[0][0]
            new = np.where(idx >= 0, 0, idx)
            m = objedit.text_mask(bykey[k], 12, 'song')
            m = objedit.squeeze(m, idx.shape[1] - 2)
            stamp(new, m, max(0, (min(idx.shape[0], 13) - m.shape[0]) // 2), 1, ink)
            of.write(own, new, clear_hidden=True); n += 1
    report.append(f'plain text sprites: {n} frames')


def chain_parts(of, si, chain):
    """parts of a segment chain with x offsets and front-first order, from their first use."""
    import segments
    for img, ps in objedit.objgfx.frames(of.dat[si]):
        keys = [(p[0], p[1]) for p in ps]
        if all(k in keys for k in chain):
            sel = [p for p in ps if (p[0], p[1]) in chain]          # frame order = front first
            x0 = min(p[2] for p in sel)
            return [(p[0], p[1], p[2] - x0, p[3]) for p in sel]
    raise KeyError(chain)


def part_canvas(of, si, key):
    """(idx, own, pal) of one OAM part (tile, attr) or of a chain of parts as laid out in a frame.
    Pixels hidden behind a front part are recorded in of._pairs to be kept equal on write."""
    import segments
    parts = [(key[0], key[1], 0, 0)] if isinstance(key[0], int) else chain_parts(of, si, list(key))
    b8 = segments.is8(of, si)
    y0 = min(p[3] for p in parts)
    pieces = [(p, segments.part_pixels(of, si, (p[0], p[1], 0, 0))) for p in parts]
    W = max(p[2] + w for p, (_, w, _) in pieces); H = max(p[3] - y0 + h for p, (_, _, h) in pieces)
    idx = np.full((H, W), -1, int); own = np.full((H, W), -1, np.int64); pairs = []
    for p, (pix, w, h) in pieces:                       # front first: later parts only fill holes
        for (x, y), k in pix.items():
            X, Y = p[2] + x, p[3] - y0 + y
            if own[Y, X] >= 0: pairs.append((int(own[Y, X]), k)); continue
            idx[Y, X] = segments.get_px(of, k, b8); own[Y, X] = k
    of._bpp8 = b8; of._pairs = pairs
    im = objedit.objgfx.images(of.sec(si))[0]
    return idx, own, objedit.objgfx.palette(of.sec(si), im)


def restyle(of, si, frames, text, rect=None, font='yahei_b', size=None, stroke=1, spacing=0,
            thr=90, fill=None, outline=None, clear_hidden=False, align='center', dy=0, pad=1, box=None,
            text_idx=None, text_lum=None, erase=None, auto_top=False, near=0, inpaint_dir=0, clear=False, fill_all=False, pixel=None):
    """replace the text of a frame keeping its look: per-row background, per-row fill colour
    (gradients) and outline colour are measured from the original pixels in rect; the new text
    is drawn anti-aliased in those colours and snapped to the sprite palette."""
    from PIL import Image, ImageDraw, ImageFont
    frames = list(frames)
    orig = {fi: (part_canvas(of, si, fi) if isinstance(fi, tuple) else of.canvas(si, fi)) for fi in frames}
    for fi in frames:
        bx = box
        idx, own, pal = orig[fi]
        if not isinstance(fi, tuple): of.canvas(si, fi)     # refresh the hidden-pixel list
        H, W = idx.shape
        x0, y0, x1, y1 = rect or (0, 0, W, H)
        if auto_top:                          # rect/box are relative to the first mostly-opaque row
            top = next((y for y in range(H) if (idx[y] > 0).sum() * 2 > W), 0)
            y0, y1 = y0 + top, y1 + top
            if bx is not None: bx = (bx[0], bx[1] + top, bx[2], bx[3] + top)
        x1, y1 = min(x1, W), min(y1, H)
        P = pal.astype(int)
        rowbg, diff = {}, np.zeros(idx.shape, bool)
        for y in range(y0, y1):
            row = [v for v in idx[y, x0:x1] if v >= 0]
            if not row: continue
            b = Counter(row).most_common(1)[0][0]; rowbg[y] = b
            for x in range(x0, x1):
                v = idx[y, x]
                if v >= 0 and v != b and (b == 0 or v == 0 or ((P[v] - P[b]) ** 2).sum() > thr * thr):
                    diff[y, x] = v != 0 or b != 0
        if clear:                             # transparent sprite: the whole old text goes
            rowbg = {y: 0 for y in range(y0, y1)}; diff[:] = False; diff[y0:y1, x0:x1] = idx[y0:y1, x0:x1] > 0
        if text_lum is not None:
            lo, hi = text_lum; L = P.sum(1)
            text_idx = {int(v) for v in set(idx[y0:y1, x0:x1].ravel().tolist()) if v > 0 and (L[v] < lo or L[v] > hi)}
        if text_idx is not None:
            sel = np.zeros_like(diff); sel[y0:y1, x0:x1] = np.isin(idx[y0:y1, x0:x1], list(text_idx))
            diff = sel
            yy_, xx_ = np.where(diff)
            if len(yy_) and bx is None:
                bx = (max(0, xx_.min() - 1), yy_.min(), min(W, xx_.max() + 2), yy_.max() + 1)
        ys, xs = np.where(diff)
        if bx is not None: ty0, ty1 = bx[1], bx[3]
        elif not len(ys): continue
        else: ty0, ty1 = ys.min(), ys.max() + 1
        vals = [int(idx[y, x]) for y, x in zip(ys, xs) if idx[y, x] > 0]
        lum = lambda v: int(P[v].sum())
        oc = Counter(v for v in vals if lum(v) < 250)
        out_rgb = np.asarray(outline if outline is not None else (P[oc.most_common(1)[0][0]] if oc else (0, 0, 0)))
        fills = {}
        for y in range(ty0, ty1):
            r = [P[int(v)] for v in idx[y, x0:x1][diff[y, x0:x1]]
                 if v > 0 and (lum(int(v)) >= 250 if not fill_all else (P[int(v)] != out_rgb).any())]
            if r: fills[y] = np.mean(r, 0)
        if fill is not None: fills = {y: np.asarray(fill) for y in range(ty0, ty1)}
        if not fills: fills = {ty0: np.array([255, 255, 255])}
        fy = sorted(fills)
        new = idx.copy()
        if erase == 'inpaint':                  # dithered gradients: mask far-from-row-colour pixels
            m = np.zeros(idx.shape, bool)
            if text_idx is not None:
                m = diff.copy()
                if near:                          # plus far-from-row-colour pixels next to the text
                    dm = np.zeros(idx.shape, bool)
                    for y in range(y0, y1):
                        if y not in rowbg: continue
                        b = P[rowbg[y]]
                        for x in range(x0, x1):
                            v = idx[y, x]
                            if v > 0 and ((P[v] - b) ** 2).sum() > thr * thr: dm[y, x] = True
                    g = m.copy()
                    for _ in range(near): g[1:] |= g[:-1].copy(); g[:-1] |= g[1:].copy(); g[:, 1:] |= g[:, :-1].copy(); g[:, :-1] |= g[:, 1:].copy()
                    m |= dm & g
            else:
                for y in range(y0, y1):
                    if y not in rowbg: continue
                    b = P[rowbg[y]]
                    for x in range(x0, x1):
                        v = idx[y, x]
                        if v > 0 and ((P[v] - b) ** 2).sum() > thr * thr: m[y, x] = True
            m2 = m.copy(); m2[1:] |= m[:-1]; m2[:-1] |= m[1:]; m2[:, 1:] |= m[:, :-1]; m2[:, :-1] |= m[:, 1:]
            m2[:y0] = False; m2[y1:] = False; m2[:, :x0] = False; m2[:, x1:] = False
            src = idx.copy()
            dirs = [inpaint_dir * k for k in range(2, 200, 2)] + [-inpaint_dir * k for k in range(2, 96, 2)] if inpaint_dir else None
            for y, x in zip(*np.where(m2)):
                for d in (dirs if dirs else [s * k for k in range(2, 96, 2) for s in (1, -1)]):
                    xx = x + d
                    if 0 <= xx < W and not m2[y, xx] and src[y, xx] > 0:
                        new[y, x] = src[y, xx]; break
                else:
                    if y in rowbg: new[y, x] = rowbg[y]
            rowbg = {}
        for y in range(y0, y1):
            if y in rowbg:
                if text_idx is not None:
                    new[y, x0:x1] = np.where(diff[y, x0:x1], rowbg[y], new[y, x0:x1]); continue
                seg = new[y, x0:x1]; new[y, x0:x1] = np.where(seg >= 0, rowbg[y], seg)
        if pixel:                                          # crisp bitmap text (SimSun 12) with a drop shadow
            m = objedit.squeeze(objedit.text_mask(text, 12, pixel), (bx[2] - bx[0] if bx else x1 - x0) - 2)
            mh, mw = m.shape
            px0 = (bx[0] if bx else x0) + (pad if align != 'center' else ((bx[2] - bx[0] if bx else x1 - x0) - mw) // 2)
            py0 = ty0 + (ty1 - ty0 - mh) // 2 + dy
            allowed_ = np.arange(1, len(pal))
            stamp(new, m, py0, px0, int(nearest(pal, fill if fill is not None else (255, 255, 255), allowed_)),
                  int(nearest(pal, outline if outline is not None else (24, 32, 48), allowed_)))
            of.write(np.where(new != idx, own, -1), new, clear_hidden=clear_hidden)
            continue
        th = ty1 - ty0
        sz = size or th
        if size is None:                                  # scale so the inked height matches th
            f = objedit.load_font(font, sz)
            bb = [f.getbbox(c) for c in text if c.strip()]
            gh = max(b[3] for b in bb) - min(b[1] for b in bb) + 2 * stroke if bb else th
            sz = max(6, round(sz * th / max(1, gh)))
        f = objedit.load_font(font, sz)
        tw = sum(int(f.getlength(c)) + spacing for c in text) + 2 * stroke + 4
        im_f = Image.new('L', (tw, sz * 2), 0); im_o = Image.new('L', (tw, sz * 2), 0)
        df, do = ImageDraw.Draw(im_f), ImageDraw.Draw(im_o)
        x = stroke + 1
        for c in text:
            if c.strip():
                do.text((x, 2), c, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
                df.text((x, 2), c, font=f, fill=255)
            x += (int(f.getlength(c)) if c != ' ' else sz // 3) + spacing
        a_o = np.asarray(im_o).astype(float) / 255; a_f = np.asarray(im_f).astype(float) / 255
        yy, xx = np.where(a_o > 0.05)
        a_o = a_o[yy.min():yy.max() + 1, xx.min():xx.max() + 1]; a_f = a_f[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
        if bx is not None: x0, x1 = bx[0], bx[2]
        mw = (x1 - x0) - 2 * pad; mh = th + 2
        h, w = a_o.shape
        nw, nh = min(w, mw), min(h, mh)
        if (nw, nh) != (w, h):
            a_o = np.asarray(Image.fromarray((a_o * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS)) / 255
            a_f = np.asarray(Image.fromarray((a_f * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS)) / 255
        h, w = a_o.shape
        tx = x0 + (x1 - x0 - w) // 2 if align == 'center' else x0 + pad
        tyy = ty0 + (th - h) // 2 + dy
        allowed = np.arange(1, len(pal))
        for j in range(h):
            Y = tyy + j
            if not 0 <= Y < H: continue
            fr = fills[min(fy, key=lambda q: abs(q - Y))]
            for i in range(w):
                X = tx + i
                if not 0 <= X < W or new[Y, X] < 0: continue
                ao, af = a_o[j, i], a_f[j, i]
                if ao < 0.05: continue
                base = P[new[Y, X]].astype(float) if new[Y, X] > 0 else None
                col = out_rgb * (1 - af) + fr * af
                if base is None:
                    if ao < 0.5: continue
                    rgb = col
                else:
                    rgb = base * (1 - ao) + col * ao
                new[Y, X] = nearest(pal, rgb, allowed)
        of.write(np.where(new != idx, own, -1), new, clear_hidden=clear_hidden)   # only what changed
        if isinstance(fi, tuple):
            import segments
            for fk, hk in getattr(of, '_pairs', []):
                segments.set_px(of, hk, segments.get_px(of, fk, of._bpp8), of._bpp8)


def banners(of, report):
    restyle(of, 503, range(3, 11), '平仓', rect=(16, 10, 112, 30), box=(30, 11, 98, 29),
            fill=(255, 255, 255), outline=(0, 16, 120))
    restyle(of, 704, [6], '破产宣告')
    restyle(of, 704, range(7, 12), '破产宣告', box=(4, 3, 124, 29), fill=(255, 235, 235), outline=(150, 0, 0))
    restyle(of, 544, range(3, 9), '服务器故障', rect=(0, 4, 400, 20), text_idx={5, 7, 8},
            fill=(255, 90, 40), outline=(90, 0, 0))
    restyle(of, 509, [5, 6], '倒下', rect=(16, 4, 112, 28), box=(30, 4, 98, 28), fill=(255, 230, 230), outline=(200, 0, 0))
    restyle(of, 505, [0, 1], '达成条件', rect=(6, 3, 92, 24), box=(8, 3, 90, 23))
    restyle(of, 671, [0], '大获利!!')
    restyle(of, 8, [16], '平仓')
    B = dict(erase='inpaint', text_lum=(465, 620), auto_top=True, fill=(255, 255, 255), outline=(24, 32, 48), font='yahei_b', align='left',
             box=(20, 5, 156, 19))
    D = dict(B, text_lum=(0, 420))                     # highlighted (dark) buttons: only the light text
    for si, frames, text, kw in [(512, [3], '选择使用股票', B), (512, [10], '图表设置', B), (512, [7], '图表设置', D),
                                 (512, [8], '装备交易技', B), (512, [9], '对手的情报', B), (541, [2], '选择使用股票', B),
                                 (541, [10], '装备交易技', B), (541, [1], '装备交易技', D),
                                 (541, [13], '试炼模式的记录', B), (541, [12], '试炼模式的记录', D),
                                 (512, [0], '选择使用股票', D), (512, [1], '装备交易技', D), (512, [2], '对手的情报', D),
                                 (541, [0], '选择使用股票', D)]:
        restyle(of, si, frames, text, rect=(20, 3, 156, 21), pixel='song', **kw)
    report.append('banners')


def small_glyphs(of, report):
    """trade top bar: 'あと' -> '剩' (frames 19 white, 129 red; shadow index 1)."""
    for fi in (19, 129):
        idx, own, pal = of.canvas(8, fi)
        ink = Counter(v for v in idx.ravel().tolist() if v > 1).most_common(1)[0][0]
        new = np.where(idx >= 0, 0, idx)
        m = objedit.text_mask('剩', 12, 'song')
        stamp(new, m, 14 - m.shape[0], 1, ink, 1)
        of.write(own, new)
    report.append('small glyphs')


def small_lists(of, report):
    # 612: stock names, white with shadow on transparent (frame k+2 = STOCKS[k])
    n = 0
    names612 = {0: '天王堂', 64: '天王堂', 65: '哈莫尼克斯'}
    names612.update({k + 2: s for k, s in enumerate(STOCKS[0:5] + STOCKS[6:63])})
    for fi, name in sorted(names612.items()):
        idx, own, pal = of.canvas(612, fi)
        new = np.where(idx >= 0, 0, idx)
        m = objedit.squeeze(objedit.text_mask(name, 12, 'song', spacing=1 if len(name) <= 3 else 0), idx.shape[1] - 2)
        stamp(new, m, 1, 1 + max(0, (idx.shape[1] - 2 - m.shape[1]) // 2), 5, 1)
        of.write(own, new); n += 1
    # 618-620: small trading-art buttons (frame k = TA_BUTTON[k])
    for si in (618, 619, 620):
        for k, name in enumerate(TA_BUTTON[:len(objedit.objgfx.frames(of.dat[si]))]):
            idx, own, pal = of.canvas(si, k)
            new = idx.copy()
            for y in range(3, 17):
                row = [v for v in idx[y, 0:52] if v not in (1, 3) and v > 0]
                if row: new[y, 0:52] = np.where(idx[y, 0:52] > 0, Counter(row).most_common(1)[0][0], idx[y, 0:52])
            m = place(name, 50)
            h, w = m.shape
            stamp(new, m, 4 + max(0, (12 - h) // 2), (52 - w) // 2, 1)
            of.write(own, new); n += 1
    report.append(f'small lists: {n} frames')


CONTRACT = ['奈良崎', '桐神乐', '本尼菲特', '立花', '迪亚波拉克曜子', '蛭田', '山笛', '围后', '芦屋金之助', '哀川',
            '太一', '钦平', '阿千代', '罗密欧', '敬子', '面堂', '大象', '我执', '油目', '南滨', '剑持', '黑川', '大屋',
            '上班族真田', '上班族前川', '上班族小山', '越前', '御神', '圣子', '数子', 'OL真奈美', 'OL实加', '利根',
            '真由', '花子']                                              # obj 186 frames 2..36


def part_pixels(of, si, part):
    """{(x, y): byte-key} of one OAM part (4bpp), in part-local coordinates."""
    import segments
    return segments.part_pixels(of, si, part)


def set_px(of, key, v):
    o, hi = divmod(key, 2)
    b = of.data[o]
    of.data[o] = (b & 0x0F) | (v << 4) if hi else (b & 0xF0) | v


def strip_text(of, si, fi, text, skip, ink, shade, size=12, dy=2, font='song', blank=(), clear=(), bg=0,
               erase_rows=(0, 99)):
    """redraw a name made of text strip parts (all parts except those in skip) of one frame;
    parts in blank are cleared and not drawn into (e.g. a part used twice in the frame)."""
    parts = [p for p in objedit.objgfx.frames(of.dat[si])[fi][1] if (p[0], p[1]) not in skip]
    for p in parts:
        if (p[0], p[1]) in blank:
            for k in part_pixels(of, si, p)[0].values(): set_px(of, k, 0)
    parts = [p for p in parts if (p[0], p[1]) not in blank]
    cov = {}
    for p in parts:
        pix, w, h = part_pixels(of, si, p)
        for (x, y), k in pix.items(): cov.setdefault((p[2] + x, p[3] + y), k)
    xs = [x for x, _ in cov]; ys = [y for _, y in cov]
    X0, X1, Y0 = min(xs), max(xs) + 1, min(ys)
    m = objedit.squeeze(objedit.text_mask(text, size, font), X1 - X0 - 1)
    h, w = m.shape
    tx = X0 + (X1 - X0 - w) // 2
    for (x, y), k in cov.items():                 # erase old text only, keep box pieces/borders
        o, hi = divmod(k, 2); v = (of.data[o] >> (4 * hi)) & 15
        if v in clear and erase_rows[0] <= y - Y0 < erase_rows[1] and (x > X0 or v == ink): set_px(of, k, bg)
    for yy in range(h):
        for xx in range(w):
            if m[yy, xx]:
                for (ddx, ddy) in ((1, 0), (0, 1), (1, 1)):
                    k = cov.get((tx + xx + ddx, Y0 + dy + yy + ddy))
                    if k is not None and not (yy + ddy < h and xx + ddx < w and m[yy + ddy, xx + ddx]): set_px(of, k, shade)
    for yy in range(h):
        for xx in range(w):
            if m[yy, xx]:
                k = cov.get((tx + xx, Y0 + dy + yy))
                if k is not None: set_px(of, k, ink)


def contract_list(of, report):
    restyle(of, 186, [2], '签约中', rect=(0, 0, 80, 12), text_idx={1, 10}, font='hei',
            fill=(255, 255, 255), outline=(16, 16, 16))
    for k, name in enumerate(CONTRACT):
        strip_text(of, 186, k + 2, name, {(16, 160), (0, 112), (24, 160)}, 1, 12, dy=4,
                   clear=(1, 12), bg=13, erase_rows=(3, 16))
    report.append(f'contract list: {len(CONTRACT)}')


def _info_texts():
    t = ['获得10万日元以上的利润', '2只股票各获得5万日元以上的利润', '获得30万日元以上的利润', '让资产增加200万日元']
    t += [f'战胜2名交易员|（已战胜{i}人）' for i in range(2)] + ['战胜2名交易员|（达成条件）']
    t += ['只靠做空获得50万日元以上的利润']
    t += [f'让持有股票数达到15只以上|（目前{i}只）' for i in range(15)] + ['让持有股票数达到15只以上|（达成条件）']
    t += [f'战胜4名交易员|（已战胜{i}人）' for i in range(4)] + ['战胜4名交易员|（达成条件）']
    t += [f'10只股票各获得100万日元以上的利润|（已完成{i}只）' for i in range(10)]
    t += ['10只股票各获得100万日元以上的利润|（达成条件）', '让交易员等级达到8以上', '让交易员等级达到8以上|（达成条件）']
    return t                                                     # obj 690 frames 0..41; 693 = 3..41


def info_boxes(of, report):
    texts = _info_texts(); n = 0
    for si, off in ((690, 0), (693, 3)):
        for fi in range(len(objedit.objgfx.frames(of.dat[si]))):
            if fi + off >= len(texts): break
            idx, own, pal = of.canvas(si, fi)
            H, W = idx.shape; P = pal.astype(int)
            new = idx.copy(); rows = []; cnt = Counter()
            for y in range(13, H):
                row = [v for v in idx[y, 6:W] if v > 0]
                if not row: continue
                b = Counter(row).most_common(1)[0][0]
                tx = [x for x in range(6, W) if idx[y, x] > 0 and idx[y, x] != b and ((P[idx[y, x]] - P[b]) ** 2).sum() > 60 * 60]
                if tx and len(tx) < W * 0.8:
                    rows.append(y)
                    for x in tx: cnt[int(idx[y, x])] += 1; new[y, x] = b
            if not rows: continue
            cl = _clusters(rows, 1)
            ink = max(cnt, key=lambda v: cnt[v]) if cnt else 15
            others = [v for v, _ in cnt.most_common() if v != ink]
            sh = others[0] if others else None
            for k, line in enumerate(texts[fi + off].split('|')):
                if k >= len(cl): break
                m = objedit.squeeze(objedit.text_mask(line, 12, 'song'), W - 12)
                stamp(new, m, cl[k][0] - 1, 8, ink, sh)
            of.write(np.where(new != idx, own, -1), new); n += 1
    report.append(f'info boxes: {n}')


def segment_sprites(of, report):
    import segments
    cn = segments.load_cn(ROOT / 'text/cn/segments.txt')
    for si, m in cn.items(): segments.redraw(of, si, m)
    report.append(f'segment sprites: {sum(len(v) for v in cn.values())} fragments')


GU8 = ['XXX.XXX.', 'X.X.X.X.', 'XXX.X.XX', 'X.X.....', 'XXX.XXXX', 'X.X..XX.', 'X.X..XX.', 'X.XXX..X']   # 股 (8px)


def _wall_templates():
    import struct as _s
    d = (ROOT / 'work/fs/bgau02.bin').read_bytes() if (ROOT / 'work/fs/bgau02.bin').exists() else None
    return d


def wallpapers(rom, report):
    """trade-screen sheets bg[a-e][ud]0n: '株' -> '股' (8px), '銘柄' -> '股票'."""
    import struct as _s
    files = [f'bg{c}{s}{n:02d}.bin' for c in 'abcde' for s in 'ud' for n in range(4)]
    ref = None; n_rep = 0
    def parse(d):
        n = _s.unpack_from('<I', d, 0)[0]; offs = [o & 0x7FFFFFFF for o in _s.unpack_from(f'<{n + 1}I', d, 4)]
        tiles = np.frombuffer(d[offs[1]:offs[2]], np.uint8).reshape(-1, 8, 8)
        img = np.zeros((256, 256), np.uint8)
        for i in range(min(1024, len(tiles))):
            y, x = divmod(i, 32); img[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = tiles[i]
        return offs, img
    try: base = rom.getFileByName('bgau02.bin')
    except Exception: return
    _, img = parse(base)
    t_kabu = img[9:19, 197:207] != 1
    t_mei = img[7:18, 224:250] != 1
    t_son = parse(rom.getFileByName('bgau03.bin'))[1][193:203, 208:218] != 1
    t_son = t_son[1:9, 1:9]
    gu = np.array([[c == 'X' for c in r] for r in GU8])
    gp = objedit.text_mask('股票', 12, 'song'); gp = bold(gp)
    for f in files:
        try: d = bytearray(rom.getFileByName(f))
        except Exception: continue
        offs, img = parse(d)
        new = img.copy()
        for tmpl, glyph in ((t_kabu, gu), (t_mei, gp)):
            th, tw = tmpl.shape
            win = np.lib.stride_tricks.sliding_window_view(img, (th, tw))
            hit = ((win != win[..., :1, :1]) == tmpl).all(axis=(2, 3))
            for y, x in zip(*np.where(hit)):
                    reg = img[y:y + th, x:x + tw]
                    bgv = reg[0, 0]; inkv = reg[tmpl][0]
                    if not (reg[tmpl] == inkv).all(): continue
                    gh, gw = glyph.shape
                    new[y:y + th, x:x + tw] = bgv
                    oy = y + (th - gh) // 2 if gh <= th else y - (gh - th)
                    ox = x + (tw - gw) // 2
                    for yy in range(gh):
                        for xx in range(gw):
                            if glyph[yy, xx] and 0 <= oy + yy < 256: new[oy + yy, ox + xx] = inkv
                    n_rep += 1
        th, tw = t_son.shape                          # 損 -> 损 (8px): drop the inner bar of 貝
        win = np.lib.stride_tricks.sliding_window_view(img, (th, tw))
        for y, x in zip(*np.where(((win != win[..., :1, :1]) == t_son).all(axis=(2, 3)))):
            new[y + 4, x + 5:x + 7] = img[y, x]; n_rep += 1
        if not np.array_equal(new, img):
            raw = bytearray()
            for i in range(1024):
                yy, xx = divmod(i, 32); raw += new[yy * 8:yy * 8 + 8, xx * 8:xx * 8 + 8].tobytes()
            d[offs[1]:offs[1] + len(raw)] = raw
            rom.setFileByName(f, bytes(d))
    report.append(f'wallpapers: {n_rep} glyphs')


TRIAL = [(((32, 112), (16, 112)), '天海制果再现'), (((64, 112), (48, 112)), '短跑选手'),
         (((96, 112), (80, 112)), '双倍奉还！'), (((128, 112), (112, 112)), '牛市交易'),
         (((160, 112), (144, 112)), '垃圾股狂欢'), (((192, 112), (176, 112)), '坚持一年'),
         (((224, 112), (208, 112)), '疯狂交易'), (((0, 113), (240, 112)), '亿之路')]


def trial_titles(of, report):
    for k, (_, text) in enumerate(TRIAL):
        for fi in (3 + k, 11 + k):                    # normal / highlighted
            idx, own, pal = of.canvas(538, fi)
            restyle(of, 538, [fi], text, rect=(2, 2, idx.shape[1] - 2, 24), erase='inpaint', thr=40,
                    text_lum=(0, 585), near=2, fill=(255, 255, 255), outline=(40, 40, 110), font='yahei_b',
                    box=(6, 5, idx.shape[1] - 6, 21))
    report.append(f'trial titles: {len(TRIAL)}')


def ranking_tabs(of, report):
    K = dict(erase='inpaint', thr=40, text_lum=(0, 300), near=2, fill=(40, 24, 120), outline=(235, 235, 245),
             font='yahei_b', rect=(4, 3, 156, 22), box=(8, 5, 152, 20))
    for frames, text in (([0, 1], '利润排行榜'), ([2, 3], '利润率排行榜'), ([4, 5], '获得TP排行榜')):
        restyle(of, 418, frames, text, **K)
    report.append('ranking tabs')


class _BgOf:
    """adapter so restyle() can edit a background map canvas (si = map index, fi ignored)."""
    def __init__(self, bf, ts=0):
        self.bf, self.ts, self.cur = bf, ts, {}
    def canvas(self, si, fi):
        if si not in self.cur: self.cur[si] = self.bf.canvas(si, self.ts, (0, 0, 32, 24)).copy()
        c = self.cur[si]
        own = np.arange(c.size).reshape(c.shape)
        return c.copy(), own, self.bf.pal[min(self.ts, len(self.bf.pal) - 1)]
    def write(self, own, new, clear_hidden=False):
        si = self._si
        c = self.cur[si]
        m = own >= 0
        c.ravel()[own[m].ravel()] = new[m].ravel()
    def flush(self):
        for si, c in self.cur.items(): self.bf.edit(si, self.ts, (0, 0, 32, 24), c)


def bg_restyle(bf, mi, text, **kw):
    o = _BgOf(bf); o._si = mi
    restyle(o, mi, [0], text, **kw)
    o.flush()


NEWS = {   # file: [(map, rect, text, kw)]
}
_NA = dict(font='yahei_b', erase='inpaint', thr=50, text_lum=(0, 450), near=4, inpaint_dir=1)
_NB = dict(font='yahei_b', erase='inpaint', thr=50, text_lum=(0, 600), near=4)


def _news_list():
    head = lambda t: (t, )
    m = {'ma00': ['旅行热潮！', '公示地价上涨！'], 'ma01': ['丸菱关联股热潮！', '帝国关联股热潮！'],
         'ma02': ['金融股热潮！', '低PBR股热潮！'], 'ma03': ['低价股热潮！', '商社股热潮！'],
         'ma04': ['高科技股热潮！', '资源股热潮！'], 'ma05': ['IT股热潮！', '一部市场股热潮！'],
         'ma06': ['二部市场股热潮！', '新兴股热潮！'], 'ma07': ['棒球热潮！', '游戏热潮！'],
         'mi01': ['狂欢化！', '热门商品诞生！'], 'mi02': ['取得专利！', 'TOB！'], 'mi03': ['业务合作！', '股报刊登！'],
         'mi04': ['上调预期', '券商上调评级'], 'news_mi00': ['一部市场股热潮！', '上调预期']}
    g = {'ma08': ['发生大地震！'], 'mi00': ['追加保证金！', '南滨氏推荐！'], 'mi05': ['下调预期', '券商下调评级'],
         'mi06': ['丑闻曝光！', '发生事故！'], 'mi07': ['发行MSCB！'], 'news_ma00': ['下调预期', '券商下调评级']}
    return m, g


def news(rom, report):
    m, g = _news_list(); n = 0
    for files, rect, box, kw in ((m, (42, 144, 256, 184), (50, 148, 252, 180), _NA),
                                 (g, (24, 138, 240, 186), (40, 156, 228, 180), _NB)):
        for f, texts in files.items():
            bf = bgedit.BgFile(rom.getFileByName(f + '.bin'))
            for mi, t in enumerate(texts):
                bg_restyle(bf, mi, t, rect=rect, box=box, **kw)
                n += 1
            bf.commit()
            rom.setFileByName(f + '.bin', bf.build())
    W = dict(font='yahei_b', erase='inpaint', thr=50, text_lum=(0, 600), near=2)
    L = dict(W, fill=(40, 70, 150), outline=(255, 255, 255))
    SPECIAL = {'mi08': [(0, (48, 128, 176, 150), '桐神乐证券股', dict(L, box=(52, 131, 172, 147))),
                        (1, (48, 128, 176, 150), '桐神乐证券股', dict(L, box=(52, 131, 172, 147))),
                        (0, (24, 150, 240, 188), '有人在收购！？', dict(_NA, box=(28, 153, 236, 184))),
                        (1, (24, 150, 250, 188), '收购集团是LTA！？', dict(_NA, box=(28, 153, 248, 184))),
                        (0, (64, 12, 124, 32), '桐神乐', W), (1, (64, 12, 124, 32), '桐神乐', W)],
               'mi09': [(0, (28, 124, 142, 149), '收购已成定局！', dict(_NA, box=(30, 128, 140, 147))),
                        (0, (18, 149, 240, 188), '要以TOB对抗吗！？', dict(_NA, box=(22, 153, 236, 184))),
                        (0, (64, 12, 124, 32), '桐神乐', W), (0, (14, 78, 122, 98), '公开收购股份', W)],
               'mi02': [(0, (16, 74, 124, 96), '新技术开发', W), (1, (14, 78, 122, 98), '公开收购股份', W)]}
    for f, specs in SPECIAL.items():
        bf = bgedit.BgFile(rom.getFileByName(f + '.bin'))
        for mi, rect, text, kw in specs:
            bg_restyle(bf, mi, text, rect=rect, **kw); n += 1
        bf.commit()
        rom.setFileByName(f + '.bin', bf.build())
    report.append(f'news headlines: {n}')


def news_preview(out='work/emu/news_cn.png'):
    """debug: render every patched headline from work/fs."""
    from PIL import Image
    class R:
        def __init__(s): s.f = {}
        def getFileByName(s, n): return s.f.get(n) or (ROOT / 'work/fs' / n).read_bytes()
        def setFileByName(s, n, d): s.f[n] = d
    r = R(); news(r, [])
    files = ['mi08', 'mi09', 'mi02']
    S = Image.new('RGB', (512, 192 * len(files)))
    for k, f in enumerate(files):
        bf = bgedit.BgFile(r.getFileByName(f + '.bin'))
        for mi in range(min(2, len(bf.maps))):
            c = bf.canvas(mi, 0, (0, 0, 32, 24))
            S.paste(Image.fromarray(bf.pal[0][np.clip(c, 0, 255)]), (mi * 256, k * 192))
    S.save(out)


def _rgba_text(text, size, font, fill_top, fill_bot, inner, outer, s_in=2, s_out=1, italic=0.0, spacing=0):
    """RGBA text: gradient fill, inner (white) stroke, outer (dark) stroke, optional shear."""
    from PIL import Image, ImageDraw, ImageFont
    f = objedit.load_font(font, size)
    pad = s_in + s_out + 4
    w = sum(int(f.getlength(c)) + spacing for c in text) + 2 * pad + int(size * italic) + 4
    h = size + 2 * pad + 8
    def layer(stroke):
        im = Image.new('L', (w, h), 0); d = ImageDraw.Draw(im); x = pad
        for c in text:
            d.text((x, pad), c, font=f, fill=255, stroke_width=stroke, stroke_fill=255); x += int(f.getlength(c)) + spacing
        if italic: im = im.transform(im.size, Image.AFFINE, (1, italic, -italic * h * 0.5, 0, 1, 0), Image.BICUBIC)
        return np.asarray(im).astype(float) / 255
    a_out, a_in, a_f = layer(s_in + s_out), layer(s_in), layer(0)
    ys = np.arange(h)[:, None] / max(1, h - 1)
    grad = np.asarray(fill_top)[None, None, :] * (1 - ys[..., None]) + np.asarray(fill_bot)[None, None, :] * ys[..., None]
    rgb = np.asarray(outer, float) * np.ones((h, w, 3))
    rgb = rgb * (1 - a_in[..., None]) + np.asarray(inner, float) * a_in[..., None]
    rgb = rgb * (1 - a_f[..., None]) + grad * a_f[..., None]
    yy, xx = np.where(a_out > 0.05)
    sl = (slice(yy.min(), yy.max() + 1), slice(xx.min(), xx.max() + 1))
    return rgb[sl], a_out[sl]


def _blend_into(c, P, rgb, alpha, x0, y0, w=None, h=None):
    from PIL import Image
    if w or h:
        H0, W0 = alpha.shape
        w = w or round(W0 * h / H0); h = h or round(H0 * w / W0)
        rgb = np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize((w, h), Image.LANCZOS)).astype(float)
        alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)) / 255
    allowed = np.arange(1, len(P))
    for j in range(alpha.shape[0]):
        for i in range(alpha.shape[1]):
            a = alpha[j, i]
            Y, X = y0 + j, x0 + i
            if a < 0.08 or not (0 <= Y < c.shape[0] and 0 <= X < c.shape[1]): continue
            base = P[c[Y, X]].astype(float)
            c[Y, X] = nearest(P, base * (1 - a) + rgb[j, i] * a, allowed)


LOGO_OF = None                                            # obj file used for the logo's lightning line


def _lightning():
    """the logo's lightning chart line, complete (obj 633 frame 7, the intro layer), as RGB + mask;
    it sits at (16, 36) in title2.bin's logo coordinates."""
    of = LOGO_OF or objedit.ObjFile((ROOT / 'work/fs/obj_fnt.bin').read_bytes(), (ROOT / 'work/fs/obj_dat.bin').read_bytes())
    idx, own, pal = of.canvas(633, 7)
    return pal[np.maximum(idx, 0)].astype(int), idx > 0


def _box_text(c, P, x0, y0, w, h):
    """'股票' side by side (condensed) inside the logo's square box."""
    for k, t in enumerate('股票'):
        rgb, a = _rgba_text(t, 40, 'yahei_b', (255, 255, 255), (235, 245, 255), (255, 255, 255), (10, 30, 70), 0, 1)
        _blend_into(c, P, rgb, a, x0 + k * w, y0, w=w, h=h)


def logo_patch(bf, mi, dx=0, dy=0, ts=0):
    """'株トレーダー瞬' -> '股票交易员瞬' (coordinates relative to title2.bin's logo)."""
    c = bf.canvas(mi, ts, (0, 0, 32, 24)).copy(); P = bf.pal[min(ts, len(bf.pal) - 1)]
    X = lambda x: x + dx; Y = lambda y: y + dy
    for y in range(Y(65), Y(106)):                      # box interior: per-row teal from its left edge
        v = c[y, X(21)]
        c[y, X(20):X(63)] = v
    _box_text(c, P, X(22), Y(66), 19, 38)
    src = c.copy()                                       # background dots under the katakana
    for y in range(Y(60), Y(112)):
        for x in range(X(66), X(145)):
            c[y, x] = src[y, X(8) + ((x - X(8)) % 8)]
    Pi = P.astype(int)
    for y in range(Y(75), Y(88)):                         # tail of the old 'ー' running up to 瞬's outline
        xr = next((x for x in range(X(145), X(170)) if Pi[c[y, x]][0] > Pi[c[y, x]][2] + 60), X(159))
        for x in range(X(145), min(xr - 3, X(156))):
            c[y, x] = src[y, X(8) + ((x - X(8)) % 8)]
    lrgb, lm = _lightning()                              # put the lightning line back where it was erased
    allowed = np.arange(1, len(P))
    for j, i in zip(*np.where(lm)):
        x, y = X(16) + i, Y(36) + j
        if X(66) <= x < X(156) and Y(60) <= y < Y(112) and (x < X(145) or c[y, x] == src[y, X(8) + ((x - X(8)) % 8)]):
            c[y, x] = nearest(P, lrgb[j, i], allowed)
    rgb, a = _rgba_text('交易员', 32, 'yahei_b', (130, 235, 255), (0, 80, 140), (255, 255, 255), (8, 20, 50),
                        2, 1, italic=0.18)
    _blend_into(c, P, rgb, a, X(65), Y(71), w=82, h=33)
    bf.edit(mi, ts, (0, 0, 32, 24), c)


def logos(rom, report):
    for f in ('title2.bin', 'title.bin'):
        bf = bgedit.BgFile(rom.getFileByName(f))
        logo_patch(bf, 0)
        bf.commit()
        rom.setFileByName(f, bf.build())
    report.append('title logo')


def misc_sprites(of, report):
    """result labels, dividend plate, map titles, big character names."""
    restyle(of, 542, [1], '利润', font='yahei_b', clear=True)
    restyle(of, 542, [2], '经过天数', font='yahei_b', clear=True)
    restyle(of, 691, [0], '北滨市', font='yahei_b', clear=True)
    pixel_restyle(of, 691, [1], '交易中心', outline=2, spacing=3, font='hei', thick=False, size=13)
    for fi, t in enumerate(['相场瞬', '桐神乐 花子', '奈良崎透']):
        restyle(of, 643, [fi], t, font='serif_h', clear=True)
    plate_text(of, 437, [0, 8, 9, 10, 11, 12, 13, 14, 15], '分红', font='noto_bold', thick=False, spacing=6)
    for si in (511, 684): part_label(of, si, SUM_LABELS)
    for si in (685, 532): part_label(of, si, {26: '使用金额', 27: '投资期间', 28: '使用股票数'})
    report.append('misc sprites')


def pixel_restyle(of, si, frames, text, size=12, font='song', thick=True, outline=None, spacing=0, dy=0):
    """small transparent text sprite: clear it and draw a 1-bit glyph mask, each row filled with the
    colour the original text had on that row (gradients), with a 1px outline index."""
    for fi in frames:
        idx, own, pal = of.canvas(si, fi)
        ys, xs = np.where(idx > 0)
        if not len(ys): continue
        oc = outline if outline is not None else Counter(idx[idx > 0].tolist()).most_common(1)[0][0]
        rowc = {}
        for y in range(ys.min(), ys.max() + 1):
            c = Counter(int(v) for v in idx[y] if v > 0 and v != oc)
            if c: rowc[y] = c.most_common(1)[0][0]
        new = np.where(idx > 0, 0, idx)
        m = objedit.text_mask(text, size, font, spacing=spacing)
        if thick: m = bold(m)
        m = objedit.squeeze(m, xs.max() - xs.min() - 1)
        h, w = m.shape
        bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        tx = bx0 + (bx1 - bx0 - w) // 2; ty = by0 + (by1 - by0 - h) // 2 + dy
        stamp(new, m, ty, tx, 1, None, oc)
        ry = sorted(rowc)
        for yy in range(h):
            Y = ty + yy
            if not 0 <= Y < new.shape[0]: continue
            col = rowc[min(ry, key=lambda q: abs(q - Y))]
            for xx in range(w):
                X = tx + xx
                if m[yy, xx] and 0 <= X < new.shape[1] and new[Y, X] >= 0: new[Y, X] = col
        of.write(own, new, clear_hidden=True)


def plate_text(of, si, frames, text, font='hei', thick=True, size=None, spacing=1, rect=None, bright=False, align='center'):
    """text on a flat plate: text pixels (non-fill pixels inside the fill-coloured rows) become the
    fill colour, the new text is drawn 1-bit in the darkest text colour with a 1px drop shadow in the
    commonest other text colour."""
    for fi in frames:
        idx, own, pal = of.canvas(si, fi)
        P = pal.astype(int)
        main = Counter(int(v) for v in idx.ravel() if v > 0).most_common(1)[0][0]
        txt = np.zeros(idx.shape, bool); cols = []
        prow = [y for y in range(idx.shape[0]) if (idx[y] == main).sum() >= 4]
        mode = [y for y in prow if Counter(int(v) for v in idx[y] if v > 0).most_common(1)[0][0] == main]
        for y in prow:
            if not mode[0] <= y <= mode[-1]: continue
            row = idx[y]
            xm = np.where(row == main)[0]; cols += [xm.min(), xm.max()]
            for x in range(xm.min(), xm.max() + 1):
                if rect and not (rect[0] <= x < rect[2] and rect[1] <= y < rect[3]): continue
                if row[x] > 0 and row[x] != main: txt[y, x] = True
        ys, xs = np.where(txt)
        if not len(ys): continue
        vals = Counter(int(idx[y, x]) for y, x in zip(ys, xs))
        ink = (max if bright else min)(vals, key=lambda v: P[v].sum())
        sh = next((v for v, _ in vals.most_common() if v != ink), None)
        new = idx.copy(); new[txt] = main
        h0 = ys.max() - ys.min() + 1
        m = objedit.text_mask(text, size or h0 - 1, font, spacing=spacing)
        if thick: m = bold(m)
        ix0, ix1 = min(cols) + 2, max(cols) - 1
        if rect: ix0, ix1 = max(ix0, rect[0]), min(ix1, rect[2])
        m = objedit.squeeze(m, ix1 - ix0)
        h, w = m.shape
        tx = ix0 + (ix1 - ix0 - w) // 2 if align == 'center' else xs.min()
        ty = ys.min() + (h0 - 1 - h) // 2
        stamp(new, m, ty, tx, ink, sh)
        of.write(np.where(new != idx, own, -1), new)


def part_label(of, si, frame_texts, size=12, font='song'):
    """labels made of shared OAM parts: each column belongs to the covering part that starts last
    (the other parts are blanked there), so every shared part gets the same pixels in all frames."""
    import segments
    b8 = segments.is8(of, si)
    for fi, text in frame_texts.items():
        idx, own, pal = of.canvas(si, fi)
        vals = Counter(int(v) for v in idx.ravel() if v > 0)
        P = pal.astype(int)
        ink = max(vals, key=lambda v: P[v].sum()); sh = min(vals, key=lambda v: P[v].sum())
        img, parts = objedit.objgfx.frames(of.dat[si])[fi]
        X0 = min(p[2] for p in parts); Y0 = min(p[3] for p in parts)
        W = max(p[2] - X0 + objedit.objgfx.SIZES[(p[1] >> 6, (p[1] >> 4) & 3)][0] for p in parts)
        H = idx.shape[0]
        m = objedit.squeeze(objedit.text_mask(text, size, font), W - 1)
        new = np.zeros((H, W), int)
        stamp(new, m, max(0, (H - m.shape[0]) // 2 - 1), 0, ink, sh)
        for p in parts:
            pw, ph = objedit.objgfx.SIZES[(p[1] >> 6, (p[1] >> 4) & 3)]
            px0 = p[2] - X0
            later = [q[2] - X0 for q in parts if q is not p and q[2] > p[2] and q[2] - X0 < px0 + pw]
            cut = min(later) if later else px0 + pw
            pix, _, _ = segments.part_pixels(of, si, (p[0], p[1], 0, 0), img)
            for (x, y), key in pix.items():
                X, Y = px0 + x, p[3] - Y0 + y
                v = int(new[Y, X]) if X < cut and Y < H and X < W else 0
                segments.set_px(of, key, v, b8)


SUM_LABELS = {30: '使用股票数', 31: '投资期间', 32: '胜利金额', 33: '目标金额', 34: '对决金额', 35: '使用金额'}


def more_sprites(of, report):
    ranking_tabs(of, report)
    plate_text(of, 200, [12, 13, 14], '返回', rect=(3, 0, 40, 32), bright=True, align='left')
    for chain, text in CONFIRM232: overlay_label(of, 232, chain, text, dark=True)
    for frames, text, sh in (([0], '状态', 11), ([1], '交易技', 11), ([2], '状态', 8), ([3], '交易技', 8),
                             ([7, 8], '移动平均线', 32), ([9, 10], '阻力线', 32), ([11, 12], '布林带', 32)):
        restyle(of, 602, frames, text, rect=(24, 5, 156, 27), text_idx={253, sh}, erase='inpaint', font='yahei_b', size=14,
                fill=(255, 255, 255), outline=tuple(int(c) for c in of.canvas(602, frames[0])[2][sh]))
    for si, chain, text in TOUCH: chain_text(of, si, chain, text, thick=False, spacing=1)
    wipe_text(of, 2, range(2, 14), 13, '未完待续', font='noto_medium', stroke=1, spacing=1,
              fill=(170, 228, 255), outline=(16, 40, 150))
    for si in (663, 664):
        idx, own, pal = of.canvas(si, 0)                  # above the bar: only the old text
        top = next(y for y in range(idx.shape[0]) if (idx[y, :4] > 0).any())
        new = idx.copy(); new[:top, :44] = np.where(idx[:top, :44] >= 0, 0, idx[:top, :44])
        of.write(own, new)
        restyle(of, si, [0], '松', rect=(6, 2, 40, 18), text_lum=(150, 600), font='yahei_b', size=14,
                align='left', pad=3)
    report.append('more sprites')


def overlay_label(of, si, chain, text, size=12, font='song', gap=2, dark=False):
    """transparent icon+text overlay made of a chain of parts: keep the icon (first opaque column
    run), clear the rest and draw the text with the original fill / outline colours."""
    import segments
    idx, own, pal = part_canvas(of, si, chain)
    H, W = idx.shape
    col = (idx > 0).any(0)
    x = int(np.argmax(col))
    while x < W and col[x]: x += 1
    ie = x
    P = pal.astype(int)
    vals = Counter(int(v) for v in idx[:, ie:].ravel() if v > 0)
    top = [v for v, _ in vals.most_common(4)]
    ink = max(top, key=lambda v: P[v].sum()); edge = min(top, key=lambda v: P[v].sum())
    if dark: ink, edge = edge, ink
    new = idx.copy(); new[:, ie:] = np.where(idx[:, ie:] >= 0, 0, idx[:, ie:])
    m = objedit.squeeze(objedit.text_mask(text, size, font), W - ie - gap - 2)
    h, w = m.shape
    stamp(new, m, (H - h) // 2, ie + gap, ink, None, edge)
    of.write(np.where(new != idx, own, -1), new)
    for fk, hk in getattr(of, '_pairs', []):
        segments.set_px(of, hk, segments.get_px(of, fk, of._bpp8), of._bpp8)


CONFIRM232 = [(((48, 97), (44, 97), (148, 17)), '股票确认'),
              (((100, 97), (96, 97), (92, 97), (88, 97), (84, 97)), '交易技确认'),
              (((104, 97), (116, 97), (112, 97), (108, 97), (170, 17)), '交易追加功能确认'),
              (((12, 97), (8, 97)), '保存')]


def chain_text(of, si, chain, text, size=13, font='hei', thick=True, spacing=0):
    """one-colour text overlay (chain of parts on a transparent background): clear and redraw."""
    import segments
    idx, own, pal = part_canvas(of, si, chain)
    ink = Counter(int(v) for v in idx.ravel() if v > 0).most_common(1)[0][0]
    H, W = idx.shape
    new = np.where(idx >= 0, 0, idx)
    m = objedit.text_mask(text, size, font, spacing=spacing)
    if thick: m = bold(m)
    m = objedit.squeeze(m, W - 1)
    h, w = m.shape
    stamp(new, m, (H - h) // 2, (W - w) // 2, ink)
    of.write(np.where(new != idx, own, -1), new)
    for fk, hk in getattr(of, '_pairs', []):
        segments.set_px(of, hk, segments.get_px(of, fk, of._bpp8), of._bpp8)


TOUCH = [(181, ((12, 96), (24, 16)), '快擦！'), (181, ((16, 96), (20, 16)), '快弹！'),
         (216, ((12, 96), (64, 16)), '快转！'), (216, ((32, 96), (72, 16)), '快戳！'),
         (216, ((16, 96), (81, 128)), '快拉！'), (646, ((12, 96), (20, 16)), '快戳！')]


def wipe_text(of, si, frames, full, text, **kw):
    """text revealed by a streak wipe: draw the new text on the full frame, then rebuild every
    other frame row by row from it (same horizontal shift and coverage as the original row)."""
    orig = {fi: of.canvas(si, fi) for fi in frames}
    F = orig[full][0]
    restyle(of, si, [full], text, clear=True, **kw)
    N = of.canvas(si, full)[0]
    for fi in frames:
        if fi == full: continue
        idx, own, pal = orig[fi]
        if idx.shape != F.shape: continue
        if (idx == F).all():
            of.write(np.where(N != idx, own, -1), N); continue
        new = np.where(idx >= 0, 0, idx)
        for y in range(idx.shape[0]):
            row = idx[y] > 0
            if not row.any(): continue
            best, bd = 0, None
            for d in range(-12, 13):
                sh = np.roll(F[y] > 0, d)
                err = (sh != row).sum()
                if bd is None or err < bd: best, bd = d, err
            cov = row.copy()                          # coverage: runs of the row, gaps < 8 closed
            xs_ = np.where(row)[0]
            for a_, b_ in zip(xs_[:-1], xs_[1:]):
                if b_ - a_ < 8: cov[a_:b_] = True
            for k in (1, 2): cov |= np.roll(cov, 1) | np.roll(cov, -1)
            if bd <= max(2, row.sum() // 10): cov[:] = True        # whole row shown (just shifted)
            src = np.roll(N[y], best)
            new[y] = np.where((idx[y] >= 0) & cov & (src > 0), src, new[y])
        of.write(np.where(new != idx, own, -1), new)


def typed_shout(of, si, final, frames, cn, cursors, size=24, stroke=2, font='yahei_b'):
    """typewriter shout (obj 407/409).  Typed char tiles (parts not in the final frame) take CN
    char k in order of appearance; a final-frame part takes the chars whose typed tiles it replaced
    when it first appeared (left-over chars go to the remaining final parts by x).  Every part sits
    at one fixed position, so each is redrawn on its own and all frames stay consistent."""
    from PIL import Image, ImageDraw, ImageFont
    import segments
    fr = objedit.objgfx.frames(of.dat[si])
    key = lambda p: (p[0], p[1])
    fin = sorted([p for p in fr[final][1] if key(p) not in cursors], key=lambda p: p[2])
    finkeys = {key(p) for p in fin}
    size_of = lambda p: objedit.objgfx.SIZES[(p[1] >> 6, (p[1] >> 4) & 3)]
    idx, own, pal = of.canvas(si, final)
    Y0 = min(p[3] for p in fr[final][1])
    P = pal.astype(int); L = P.sum(1)
    vals = Counter(int(v) for v in idx.ravel() if v > 0)
    edge = min(vals, key=lambda v: L[v])
    rowfill = {}                                          # fill colour per row: bright colours only
    Lmax = max(L[v] for v in vals)
    for y in range(idx.shape[0]):
        c = Counter(int(v) for v in idx[y] if v > 0 and v != edge and L[v] >= 0.6 * Lmax)
        if c: rowfill[Y0 + y] = P[c.most_common(1)[0][0]]
    allowed = np.array(sorted(vals))
    typed, order = {}, []
    for fi in frames:
        for p in fr[fi][1]:
            k = key(p)
            if k in cursors or k in finkeys or k in typed: continue
            typed[k] = len(order); order.append(p)
    resp = {key(c): [typed[key(p)] for p in order if c[2] <= p[2] + 20 < c[2] + size_of(c)[0]] for c in fin}
    used = {i for v in resp.values() for i in v}
    left = [i for i in range(len(cn)) if i not in used]
    free = [p for p in fin if not resp.get(key(p))]
    for n, p in enumerate(free):
        resp[key(p)] = left[n:n + 1] if n < len(free) - 1 else left[n:]
    if not free and left and fin: resp[key(fin[-1])] = resp.get(key(fin[-1]), []) + left
    def strip(text):                                     # text -> (outline+shadow mask, fill alpha), tight
        f = objedit.load_font(font, size)
        W = int(sum(f.getlength(ch) for ch in text)) + 4 * stroke + 12; H = size * 2
        im_o = Image.new('L', (W, H)); im_f = Image.new('L', (W, H))
        x = 2 * stroke + 2
        for ch in text:
            ImageDraw.Draw(im_o).text((x, 2 * stroke), ch, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
            ImageDraw.Draw(im_f).text((x, 2 * stroke), ch, font=f, fill=255)
            x += f.getlength(ch) - 1
        o = np.asarray(im_o) / 255; fl = np.asarray(im_f) / 255
        o = np.maximum(o, np.roll(np.roll(o, 1, 0), 1, 1))           # drop shadow
        ys, xs = np.where(o > 0.5)
        return o[ys.min():ys.max() + 1, xs.min():xs.max() + 1], fl[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    def fit(o, fl, w, h):
        if o.shape[1] > w or o.shape[0] > h:
            s_ = min(w / o.shape[1], h / o.shape[0])
            nw, nh = max(1, int(o.shape[1] * s_)), max(1, int(o.shape[0] * s_))
            o = np.asarray(Image.fromarray((o * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS)) / 255
            fl = np.asarray(Image.fromarray((fl * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS)) / 255
        return o, fl
    def put(part, o, fl, ox, oy):                         # (ox, oy): layout origin in OAM coordinates
        w, h = size_of(part)
        pix, _, _ = segments.part_pixels(of, si, part)
        img = np.zeros((h, w), int)
        for (x, y), k in pix.items():
            j, i = part[3] + y - oy, part[2] + x - ox
            if 0 <= j < o.shape[0] and 0 <= i < o.shape[1] and o[j, i] >= 0.5:
                fc = rowfill[min(rowfill, key=lambda q: abs(q - part[3] - y))]
                img[y, x] = nearest(pal, P[edge] * (1 - fl[j, i]) + fc * fl[j, i], allowed)
        for (x, y), k in pix.items(): segments.set_px(of, k, int(img[y, x]))
    xa = min(p[2] for p in fin); xb = max(p[2] + size_of(p)[0] for p in fin)
    chars = [ch for ch in cn if ch]
    if order:                                            # char k centred on its typing slot
        cen = [p[2] + 16 for p in order][:len(chars)]
        pitch = (cen[-1] - cen[0]) / max(1, len(cen) - 1) if len(cen) > 1 else 28
        while len(cen) < len(chars): cen.append(cen[-1] + pitch)
    else:
        cen = [xa + (xb - xa) * (k + 0.5) / len(chars) for k in range(len(chars))]
    X0 = -160; lay_o = np.zeros((32, 320)); lay_f = np.zeros((32, 320))
    gl = [fit(*strip(ch), 34, 31) for ch in chars]
    tot = sum(g_[0].shape[1] for g_ in gl) + len(gl) - 1
    if tot > xb - xa - 2:                                  # too wide for the frame: shrink every glyph
        f_ = (xb - xa - 2 - (len(gl) - 1)) / (tot - (len(gl) - 1))
        gl = [fit(go, gf, max(1, int(go.shape[1] * f_)), max(1, int(go.shape[0] * f_))) for go, gf in gl]
    for k, ch in enumerate(chars):                         # even spacing: 1 px between glyph boxes
        if k: cen[k] = cen[k - 1] + gl[k - 1][0].shape[1] / 2 + 1 + gl[k][0].shape[1] / 2
    left = cen[0] - gl[0][0].shape[1] / 2; right = cen[-1] + gl[-1][0].shape[1] / 2
    shift = (xa + xb) / 2 - (left + right) / 2               # centre the line in the frame
    if left + shift < xa: shift = xa - left
    for k, ch in enumerate(chars):
        go, gf = gl[k]
        x = int(round(cen[k] + shift - go.shape[1] / 2)) - X0; y = (32 - go.shape[0]) // 2
        sl = (slice(y, y + go.shape[0]), slice(x, x + go.shape[1]))
        m_ = go >= 0.5
        lay_o[sl] = np.where(m_, go, lay_o[sl]); lay_f[sl] = np.where(m_, gf, lay_f[sl])
    for p in fin + order: put(p, lay_o, lay_f, X0, -16)


def shout_groups(of, si, cursors, n_final=10):
    fr = objedit.objgfx.frames(of.dat[si])
    starts = [i for i in range(n_final, len(fr)) if all((p[0], p[1]) in cursors for p in fr[i][1])
              and (i == n_final or not all((p[0], p[1]) in cursors for p in fr[i - 1][1]))]
    out = []
    for s, e in zip(starts, starts[1:] + [len(fr)]):
        keys = {(p[0], p[1]) for i in range(s, e) for p in fr[i][1]} - set(cursors)
        best = max(range(n_final), key=lambda f: len(keys & {(p[0], p[1]) for p in fr[f][1]}))
        out.append((best, list(range(s, e))))
    return out


def _shout_texts(v):                          # final frame -> CN char per JP char (None = blank)
    t = {2: f'这只股票该{v}！', 4: f'果断{v}进！' if v == '买' else f'果断{v}出！', 6: f'{v}入吧！' if v == '买' else f'{v}出吧！',
         8: f'就{v}它！'}
    return {f: list(t[f - (f % 2 == 1)]) for f in range(2, 10)}


SHOUTS = {407: ({(50, 81), (136, 32)}, _shout_texts('买')), 409: ({(60, 81), (136, 32)}, _shout_texts('卖'))}


_BOLD = dict(font='noto_black', size=28, stroke=2); _THIN = dict(font='noto_medium', size=28, stroke=1)
SHOUT_STYLE = {2: _BOLD, 3: _THIN, 4: _THIN, 5: _BOLD, 6: _THIN, 7: _BOLD, 8: _THIN, 9: _BOLD}   # as the JP frames


def shouts(of, report):
    for si, (cur, texts) in SHOUTS.items():
        groups = shout_groups(of, si, cur)
        done = set()
        for final, frames in groups:
            if final not in texts: continue
            typed_shout(of, si, final, frames, texts[final], cur, **SHOUT_STYLE[final]); done.add(final)
        for final in set(texts) - done:
            typed_shout(of, si, final, [], texts[final], cur, **SHOUT_STYLE[final])
    report.append('shouts')


TA_FX = {411: [(0, '排行榜第一！', 'yahei'), (1, '排行榜第一！', 'yahei_b'), (2, '排行榜第一！', 'yahei_b'),
               (3, '狂欢会场', 'yahei_b'), (4, '狂欢会场', 'yahei'), (5, '狂欢会场', 'yahei_b'),
               (6, '庄家!?', 'yahei'), (7, '庄家!?', 'yahei'), (8, '庄家!?', 'yahei_b'),
               (9, '狂欢!?', 'yahei'), (10, '狂欢!?', 'yahei_b'), (11, '狂欢!?', 'yahei')],
         413: [(0, '删除', 'yahei'), (1, '删除', 'yahei_b'), (2, '删除帖子', 'yahei'), (3, '删除帖子', 'yahei_b'),
               (4, '论坛关闭', 'yahei'), (5, '论坛关闭', 'yahei'), (6, '帖子沉底', 'yahei'), (7, '帖子沉底', 'yahei_b')]}


def ta_effects(of, report):
    for si, lst in TA_FX.items():
        for fi, text, font in lst:
            bold_ = font == 'yahei_b'
            restyle(of, si, [fi], text, font='noto_black' if bold_ else 'noto_regular', clear=True, fill=(255, 255, 255),
                    outline=(0, 0, 0), stroke=2 if bold_ else 1)
    report.append('TA effect captions')


def card_logo(rom, report):
    """view_bg 'トレーダーカード' -> '交易员卡片': rebuild the striped banner row by row, redraw the title."""
    bf = bgedit.BgFile(rom.getFileByName('view_bg.bin'))
    P = bf.pal[0].astype(int)
    red = lambda v: P[v][0] > P[v][1] + 40 and P[v][0] > P[v][2] + 40
    x0, y0, x1, y1 = 20, 66, 236, 120                   # banner rows; letter feet below it are erased apart
    rgb, a = _rgba_text('交易员卡片', 48, 'yahei_b', (150, 235, 255), (10, 70, 170), (255, 255, 255), (10, 20, 60),
                        4, 2, italic=0.2, spacing=2)
    def sh(m, dy, dx): return np.roll(np.roll(m, dy, 0), dx, 1)
    for mi in range(len(bf.maps)):
        c = bf.canvas(mi, 0, (0, 0, 32, 24)).copy()
        rgbc = P[c]
        cool = ~(rgbc[..., 0] > rgbc[..., 2] + 60)
        reg = np.zeros_like(cool); reg[y0:y1, 14:232] = True
        core = cool & reg                                 # thick cool strokes = letters (lightning is thin)
        core = np.logical_and.reduce([sh(core, dy, dx) for dy in range(-3, 4) for dx in range(-3, 4)])
        core[60:90, 180:240] = False                      # keep the starburst
        let = np.logical_or.reduce([sh(core, dy, dx) for dy in range(-4, 5) for dx in range(-4, 5)]) & reg
        body = let.copy()
        ring = np.logical_or.reduce([sh(let, dy, dx) for dy in range(-3, 4) for dx in range(-3, 4)]) & cool & reg
        ring[:80, 190:] = False
        let |= ring
        let[80:87, 208:231] |= cool[80:87, 208:231]       # the dakuten of 'ド'
        orig = c.copy()                                   # the lightning: bright pixels along its path
        bright = (rgbc[..., 2] >= 200) | (rgbc.sum(-1) > 600)
        path = np.zeros_like(bright)
        for xa, xb, ya, yb in ((8, 82, 116, 134), (58, 108, 96, 126), (126, 232, 50, 92)):
            path[ya:yb, xa:xb] = True
        path[50:55] = False                                # the silhouettes' outline above the banner
        bolt = bright & path & ~body
        bolt = np.logical_or.reduce([sh(bolt, dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]) & path & ~body & cool
        cyan = (rgbc[..., 1] > 170) & (rgbc[..., 2] > 230) & (rgbc[..., 0] < 200)
        low = np.zeros_like(cyan); low[112:132, 8:106] = True       # lower zigzag: cyan edges + the white core
        coreonly = np.logical_or.reduce([sh(core, dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)])
        bolt |= np.logical_or.reduce([sh(cyan & low, dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]) & low & cool & ~coreonly
        bolt[78:88, 196:232] = False; bolt[114:127, 20:50] = False    # dakuten of 'ド', foot of 'ト'
        for y in range(y0, y1):                           # banner rows: the row's warm colour
            row = [int(v) for v in c[y, 0:256] if red(int(v))]
            if not row: continue
            fillv = Counter(row).most_common(1)[0][0]
            c[y, let[y]] = fillv
        src = c.copy()
        feet = let[112:120].any(0)
        feet = np.logical_or.reduce([np.roll(feet, d) for d in range(-2, 3)])
        for y in range(120, 125):                         # letter feet below the banner: row in-paint
            bad = feet & ~((rgbc[y, :, 0] > rgbc[y, :, 2] + 60))
            for x in np.where(bad)[0]:
                for d in range(1, 40):
                    xs = [xx for xx in (x - d, x + d) if 0 <= xx < 256 and not bad[xx]]
                    if xs: c[y, x] = src[y, xs[0]]; break
        c[bolt] = orig[bolt]                              # lightning back, behind the new title
        _blend_into(c, P, rgb, a, 26, 72, w=204, h=47)
        bf.edit(mi, 0, (0, 0, 32, 24), c)
    added = bf.commit()
    assert len(bf.tiles[0]) // 64 <= 1024
    rom.setFileByName('view_bg.bin', bf.build())
    report.append(f'trader card logo: {added} new tiles')


def watermark_logo(bf, mi, ts=0, alpha=0.85):
    """faded title watermark (subtit/subend): '株' -> '股' in its box, 'トレーダー' -> '交易员'."""
    c = bf.canvas(mi, ts, (0, 0, 32, 24)).copy(); P = bf.pal[min(ts, len(bf.pal) - 1)]
    Pf = P.astype(float); allowed = np.arange(1, len(P))
    src = c.copy()
    for y in range(24, 53):                              # box interior: its left-edge colour per row
        c[y, 11:44] = src[y, 11]
    for y in range(18, 60):                              # katakana: row gradient between clean ends
        a, b = Pf[src[y, 47]], Pf[src[y, 99]]
        for x in range(48, 99):
            t = (x - 47) / 52
            c[y, x] = nearest(P, a * (1 - t) + b * t, allowed)
    for k, t in enumerate('股票'):
        rgb, al = _rgba_text(t, 40, 'yahei_b', (255, 255, 255), (235, 245, 255), (255, 255, 255), (10, 30, 70), 0, 0)
        _blend_into(c, P, rgb, al * 0.9, 13 + 15 * k, 24, w=15, h=28)
    rgb, al = _rgba_text('交易员', 32, 'yahei_b', (190, 220, 255), (120, 170, 240), (220, 235, 255), (40, 70, 160),
                         1, 1, italic=0.15)
    _blend_into(c, P, rgb, al * alpha, 47, 24, w=54, h=30)
    bf.edit(mi, ts, (0, 0, 32, 24), c)


def watermarks(rom, report):
    for f in ('subtit.bin', 'subend.bin'):
        bf = bgedit.BgFile(rom.getFileByName(f))
        watermark_logo(bf, 0)
        bf.commit({0: [0]})
        rom.setFileByName(f, bf.build())
    report.append('watermark logos')


class _WallBf:
    """adapter: a wallpaper sheet (palette + 1024 tiles in identity order) seen as a 32x24 BgFile map."""
    def __init__(self, d):
        import struct as _s
        self.d = bytearray(d)
        n = _s.unpack_from('<I', d, 0)[0]; self.offs = [o & 0x7FFFFFFF for o in _s.unpack_from(f'<{n + 1}I', d, 4)]
        pal = np.frombuffer(bytes(d[self.offs[0]:self.offs[0] + 512]), '<u2').astype(int)
        self.pal = [np.stack([(pal & 31) * 255 // 31, ((pal >> 5) & 31) * 255 // 31, ((pal >> 10) & 31) * 255 // 31], -1).astype(np.uint8)]
        tiles = np.frombuffer(bytes(d[self.offs[1]:self.offs[1] + 65536]), np.uint8).reshape(-1, 8, 8)
        self.img = np.zeros((256, 256), int)
        for i in range(1024):
            y, x = divmod(i, 32); self.img[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = tiles[i]
    def canvas(self, mi, ts, rect):
        return self.img[:192].copy()
    def edit(self, mi, ts, rect, c):
        self.img[:c.shape[0], :c.shape[1]] = c
    def build(self):
        raw = bytearray()
        for i in range(1024):
            y, x = divmod(i, 32); raw += self.img[y * 8:y * 8 + 8, x * 8:x * 8 + 8].astype(np.uint8).tobytes()
        self.d[self.offs[1]:self.offs[1] + len(raw)] = raw
        return bytes(self.d)


def wall_logos(rom, report):
    for f in ('bged00.bin', 'bged01.bin'):
        w = _WallBf(rom.getFileByName(f))
        logo_patch(w, 0)
        rom.setFileByName(f, w.build())
    report.append('wallpaper logos')


def _wrap(text, font, size, width):
    from PIL import ImageFont
    f = objedit.load_font(font, size)
    lines, cur, w = [], '', 0
    for c in text:
        cw = int(f.getlength(c))
        if w + cw > width:
            if c in '，。、；：！？）”」' and cur:          # no punctuation at a line start
                lines.append(cur[:-1]); cur = cur[-1]; w = int(f.getlength(cur))
            else:
                lines.append(cur); cur, w = '', 0
        cur += c; w += cw
    if cur: lines.append(cur)
    return lines


def card_footer(new, idx, pal):
    """trader card footer 'トレーダーカード' -> '交易员卡片' in the same look: the speed-line stripes,
    lightning and spark stay; only the katakana's outlines (outline colour with no glow colour next to
    them) are removed, and the new title is drawn hollow (light ring, dark inside) like the original."""
    y0, y1, x0, x1 = 110, 131, 66, 140
    sub = idx[y0:y1, x0:x1]
    bg, st = [v for v, _ in Counter(sub.ravel().tolist()).most_common(2)]
    others = [v for v in set(sub.ravel().tolist()) if v not in (bg, st) and v > 0]
    L = pal.astype(int).sum(1)
    order = sorted(others, key=lambda v: L[v])
    lite = order[-2] if len(order) > 1 else order[-1]
    glow = set(others) - {lite}
    H, W = idx.shape
    let = np.zeros(idx.shape, bool)
    for y in range(113, 130):
        for x in range(x0, x1):
            if idx[y, x] == lite and not any(v in glow for v in idx[max(0, y - 1):y + 2, max(0, x - 1):x + 2].ravel()):
                let[y, x] = True
    src = new.copy()
    for y, x in zip(*np.where(let)):
        for d in range(1, 12):
            xs = [xx for xx in (x - d, x + d) if 0 <= xx < W and not let[y, xx] and src[y, xx] in (bg, st)]
            if xs: new[y, x] = src[y, xs[0]]; break
    m = objedit.text_mask('交易员卡片', 13, 'noto_medium')
    h, w = m.shape; ty = 113 + (16 - h) // 2; tx = x0 + 3 + (x1 - x0 - 3 - w) // 2
    ring = np.zeros((h + 2, w + 2), bool)
    for dy in (0, 1, 2):
        for dx in (0, 1, 2): ring[dy:dy + h, dx:dx + w] |= m
    inner = np.zeros_like(ring); inner[1:1 + h, 1:1 + w] = m
    for yy, xx in zip(*np.where(ring)):
        Y, X = ty - 1 + yy, tx - 1 + xx
        if 0 <= Y < H and 0 <= X < W and new[Y, X] >= 0: new[Y, X] = bg if inner[yy, xx] else lite
    return new


def trader_cards(of, report, path='text/cn/cards.txt'):
    """trader cards (obj 543/613/614/615): name in the header, the profile wrapped below."""
    n = 0
    for line in open(ROOT / path, encoding='utf-8'):
        if line.startswith('#') or not line.strip(): continue
        key, name, desc = line.rstrip('\n').split('|')
        si, fi = map(int, key.split(':'))
        idx, own, pal = of.canvas(si, fi)
        cnt = Counter(idx[26:100, 7:136].ravel().tolist()).most_common(2)
        bgv, ink = cnt[0][0], cnt[1][0]
        new = idx.copy()
        new[8:23, 7:117] = bgv                       # name (the number box at x>=117 stays)
        new[23:104, 7:137] = bgv
        m = objedit.text_mask(name, 16, 'serif_h')
        m = objedit.squeeze(m, 104)
        stamp(new, m, 7 + max(0, (16 - m.shape[0]) // 2), 9, ink)
        lines = _wrap(desc, 'song', 12, 126)
        assert len(lines) <= 6, (key, lines)
        for k, ln in enumerate(lines):
            m = objedit.text_mask(ln, 12, 'song')
            m = objedit.squeeze(m, 128)
            stamp(new, m, 26 + 12 * k, 8, ink)
        new = card_footer(new, idx, pal)
        of.write(np.where(new != idx, own, -1), new); n += 1
    report.append(f'trader cards: {n}')


def chain_notes(of, si, chain, items, size=12, font='song'):
    """flat-background labels on a chain of parts: each item (rect, text, ink, align, squeeze_to);
    the rect is filled with each row's commonest colour, then the text drawn 1-bit (SimSun 12)."""
    import segments
    idx, own, pal = part_canvas(of, si, chain)
    new = idx.copy()
    for rect, text, ink, align in items:
        x0, y0, x1, y1 = rect
        rowbg = {y: Counter(int(v) for v in idx[y, x0:x1] if v > 0).most_common(1)[0][0] for y in range(y0, y1)}
        if ink is None:                          # commonest colour that is not a row background
            bgs = set(rowbg.values())
            cnt = Counter(int(v) for v in idx[y0:y1, x0:x1].ravel() if v > 0 and v not in bgs)
            top = cnt.most_common(1)[0][1]
            P = pal.astype(int)
            ink = min((v for v, n in cnt.items() if n * 5 >= top), key=lambda v: P[v].sum())
        for y in range(y0, y1): new[y, x0:x1] = rowbg[y]
        m = objedit.squeeze(objedit.text_mask(text, size, font), x1 - x0 - 1)
        h, w = m.shape
        tx = x0 + 1 if align == 'left' else x0 + (x1 - x0 - w) // 2
        stamp(new, m, y0 + (y1 - y0 - h) // 2, tx, ink)
    of.write(np.where(new != idx, own, -1), new)
    for fk, hk in getattr(of, '_pairs', []):
        segments.set_px(of, hk, segments.get_px(of, fk, of._bpp8), of._bpp8)


def tutorial_pics(of, report):
    pop = ((128, 48), (160, 48), (192, 48))
    restyle(of, 607, [pop], '标准规则', rect=(40, 7, 150, 22), text_idx=None, text_lum=(150, 700), erase='inpaint',
            fill=(255, 255, 255), outline=(40, 30, 110), font='yahei_b', size=13, near=1, thr=40)
    chain_notes(of, 607, pop, [((2, 25, 170, 37), '基本规则。', None, 'left'),
                               ((2, 37, 170, 50), '一定期间内赚得多的一方获胜。', None, 'left')])
    card = ((32, 49), (0, 49), (224, 48))
    chain_notes(of, 607, card, [((8, 7, 64, 18), '对决金额', None, 'left'), ((8, 18, 64, 29), '投资期间', None, 'left'),
                                ((8, 29, 64, 40), '使用股票数', None, 'left'), ((8, 40, 64, 51), '胜利金额', None, 'left'),
                                ((80, 29, 174, 40), '（需要选择）', None, 'left')], size=11, font='hei')
    NW = dict(erase='inpaint', text_lum=(200, 640), near=2, thr=50, fill=(255, 255, 255), outline=(60, 20, 20),
              font='yahei_b', align='left')
    restyle(of, 672, [1], 'IT相关股热潮！', rect=(14, 82, 148, 105), **NW)
    restyle(of, 672, [3], '上调预期', rect=(14, 82, 148, 105), **NW)
    frame_text(of, 672, 1, (12, 7, 150, 20), '软科技 半导泰克斯 MMA')
    frame_text(of, 672, 3, (100, 7, 145, 20), '天海制果', align='right')
    TAB = dict(lum_lo=200, font='song', size=12)
    for fi in (30, 31, 32): frame_text(of, 672, fi, (1, 44, 58, 56), '天海制果', **TAB)
    for fi in range(12, 18): frame_text(of, 608, fi, (66, 48, 116, 61), '竹柴电器', **TAB)
    for fi, y, t in ((2, 44, '软科技'), (2, 65, '半导泰克斯'), (2, 87, 'MMA')):
        frame_text(of, 672, fi, (0, y, 40, y + 10), t, lum_hi=520, lum_lo=150, font='hei', size=10, fill=True)
    report.append('tutorial pictures')


def frame_text(of, si, fi, rect, text, lum_hi=560, ink=(255, 255, 255), font='hei', size=12, align='left', lum_lo=-1,
               fill=False):
    """bright 1-bit text on a busy background: in-paint the old bright text from its row
    neighbours, draw the new one in the palette colour nearest to ink."""
    idx, own, pal = of.canvas(si, fi)
    P = pal.astype(int); L = P.sum(1)
    x0, y0, x1, y1 = rect
    new = idx.copy()
    txt = lambda v: v > 0 and (L[v] > lum_hi or L[v] < lum_lo)
    for y in range(y0, y1):
        if fill:                                  # flat tab: the row's commonest non-text colour
            c = Counter(int(v) for v in idx[y, x0:x1] if v > 0 and not txt(v))
            if c: new[y, x0:x1] = np.where(idx[y, x0:x1] > 0, c.most_common(1)[0][0], idx[y, x0:x1])
            continue
        for x in range(x0, x1):
            if not txt(idx[y, x]): continue
            for d in (1, -1, 2, -2, 3, -3, 4, -4, 6, -6, 8, -8, 12, -12):
                if 0 <= x + d < idx.shape[1] and idx[y, x + d] >= 0 and not txt(idx[y, x + d]):
                    new[y, x] = idx[y, x + d]; break
    m = objedit.squeeze(objedit.text_mask(text, size, font), x1 - x0)
    h, w = m.shape
    tx = x0 if align == 'left' else x1 - w if align == 'right' else x0 + (x1 - x0 - w) // 2
    stamp(new, m, y0 + (y1 - y0 - h) // 2, tx, int(nearest(pal, ink, np.arange(1, len(pal)))))
    of.write(np.where(new != idx, own, -1), new)


BOOT = {2: [(37, '本游戏纯属虚构，'), (55, '与真实存在的人物、团体、'), (73, '事件等均无任何关系。'),
            (109, '此外，本游戏无意推荐'), (127, '任何证券买卖或特定股票。')],
        3: [(62, '无法读取数据。'), (98, '请关闭电源，'), (116, '重新插入游戏卡。')],
        4: [(62, '无法写入数据。'), (98, '请关闭电源，'), (116, '重新插入游戏卡。')]}


def boot_screens(rom, report):
    """boot.bin 4bpp screens (disclaimer, read/write error): rebuild the diagonal-striped background
    under the text from clean pixels along the stripe direction, draw the CN lines, append new tiles."""
    bf = bgedit.BgFile(rom.getFileByName('boot.bin'))
    tiles = bytearray(bf.tiles[0]); n0 = len(tiles) // 32
    have = {bytes(tiles[t * 32:t * 32 + 32]): t for t in range(n0)}
    idxs = {mi: (bf.maps[mi].astype(int) & 0x3FF) for mi in BOOT}     # may exceed 1023 until repacked
    for mi, lines in BOOT.items():
        m = bf.maps[mi]; img = np.zeros((192, 256), int)
        for cy in range(24):
            for cx in range(32):
                b = np.frombuffer(bytes(tiles[(int(m[cy, cx]) & 0x3FF) * 32:][:32]), np.uint8)
                img[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8] = np.stack([b & 15, b >> 4], 1).reshape(8, 8)
        H, W = img.shape
        at = lambda y, x: img[y, x] if 0 <= y < H and 0 <= x < W else -1
        mask = np.zeros_like(img, bool)
        for y in range(24, 145):
            for x in range(W):
                mask[y, x] = sum(img[y, x] == at(y + s * 2 * k, x - s * 2 * k) for k in (1, 2) for s in (1, -1)) < 2
        for _ in range(2):
            mask[1:] |= mask[:-1].copy(); mask[:-1] |= mask[1:].copy(); mask[:, 1:] |= mask[:, :-1].copy(); mask[:, :-1] |= mask[:, 1:].copy()
        mask[:24] = False; mask[145:] = False
        new = img.copy()
        for y, x in zip(*np.where(mask)):
            for k in range(1, 60):
                hit = next(((y + s * 2 * k, x - s * 2 * k) for s in (1, -1) if 0 <= y + s * 2 * k < H and
                            0 <= x - s * 2 * k < W and not mask[y + s * 2 * k, x - s * 2 * k]), None)
                if hit: new[y, x] = img[hit]; break
        for y0, text in lines:
            t = objedit.text_mask(text, 12, 'song')
            stamp(new, t, y0, (256 - t.shape[1]) // 2, 15, 1)
        for cy in range(24):
            for cx in range(32):
                blk = new[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8]
                if (blk == img[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8]).all(): continue
                data = bytes((blk[:, 0::2] | (blk[:, 1::2] << 4)).astype(np.uint8).ravel())
                if data not in have: have[data] = len(tiles) // 32; tiles += data
                idxs[mi][cy, cx] = have[data]
    packed, remap = bytearray(), {}                      # drop tiles no map uses any more
    for mi in BOOT:
        m = bf.maps[mi]
        for cy in range(24):
            for cx in range(32):
                t = int(idxs[mi][cy, cx])
                if t not in remap: remap[t] = len(packed) // 32; packed += tiles[t * 32:t * 32 + 32]
                m[cy, cx] = (int(m[cy, cx]) & 0xFC00) | remap[t]
    tiles = packed
    assert len(tiles) // 32 <= 1024, len(tiles) // 32
    bf.tiles[0] = tiles; bf.dirty = True
    rom.setFileByName('boot.bin', bf.build())
    report.append(f'boot screens: {len(tiles) // 32 - n0} new tiles')


def intro_logo(of, report):
    """obj 633: the opening animation's logo pieces ('株' box, 'トレーダー') -> '股', '交易员'."""
    from PIL import Image
    idx, own, pal = of.canvas(633, 0)
    P = pal.astype(int); new = idx.copy()
    for y in range(12, 54): new[y, 11:53] = idx[y, 11]           # box interior: its left-edge colour
    _box_text(new, P, 13, 14, 19, 38)
    of.write(np.where(new != idx, own, -1), new)
    idx, own, pal = of.canvas(633, 2)
    P = pal.astype(int); H, W = idx.shape
    new = np.where(idx >= 0, 0, idx)
    rgb, a = _rgba_text('交易员', 32, 'yahei_b', (110, 230, 250), (20, 120, 170), (255, 255, 255), (10, 30, 70),
                        2, 1, italic=0.15)
    h = 30; w = min(W - 2, round(a.shape[1] * h / a.shape[0]))
    rgb = np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize((w, h), Image.LANCZOS)).astype(float)
    a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)) / 255
    y0, x0 = 6, (W - w) // 2                    # inside the area the parts cover
    allowed = np.arange(1, len(P))
    for j in range(h):
        for i in range(w):
            if a[j, i] >= 0.5 and new[y0 + j, x0 + i] >= 0: new[y0 + j, x0 + i] = nearest(P, rgb[j, i], allowed)
    of.write(own, new, clear_hidden=True)
    report.append('intro logo')


CHAPTERS = [('奈良崎的工作', '工'), ('股票的世界', '世'), ('对战交易！', '交'), ('股市高手们', '手'), ('股票交易员瞬', '交'),
            ('本尼菲特的阴影', '的'), ('第一次败北', '败'), ('女操盘手们', '手'), ('再战！', '战'), ('真相大白', '真'),
            ('股票的极致', '极')]                                     # obj 1, image k = chapter k (Ex, Chart.01..10)


def _title_parts(of, si, fi, ymin=60):
    import segments
    out = []
    for p in objedit.objgfx.frames(of.dat[si])[fi][1]:
        if p[3] < ymin: continue
        pix, w, h = segments.part_pixels(of, si, (p[0], p[1], 0, 0), objedit.objgfx.frames(of.dat[si])[fi][0])
        out.append((p, pix, w, h))
    return out


def chapter_titles(of, report):
    """chapter title cards (obj 1): redraw the crisp final title in CN, then re-create every
    animation frame by giving the CN title the same horizontal shift + motion blur that the JP
    frame shows relative to the JP final title."""
    from PIL import Image, ImageDraw
    import segments
    si = 1
    fr = objedit.objgfx.frames(of.dat[si])
    ims = objedit.objgfx.images(of.sec(si))
    X0, Y0, WW, HH = -72, 56, 330, 56                     # common canvas in OAM coordinates
    def compose(fi):
        img = fr[fi][0]; pal = objedit.objgfx.palette(of.sec(si), ims[img])
        a = np.zeros((HH, WW), int); keys = {}
        for p, pix, w, h in reversed(_title_parts(of, si, fi)):          # front part = first in list
            for (x, y), k in pix.items():
                X, Y = p[2] + x - X0, p[3] + y - Y0
                if 0 <= X < WW and 0 <= Y < HH:
                    v = segments.get_px(of, k, False)
                    if v or (Y, X) not in keys: a[Y, X] = v
                    keys.setdefault((Y, X), []).append(k)
        return a, keys, pal
    def rgba(a, pal):
        P = pal.astype(float); out = np.zeros(a.shape + (4,)); m = a > 0
        out[m, :3] = P[a[m]]; out[m, 3] = 1; return out
    def blur(r, s, k):
        r = np.roll(r, s, 1)
        if s > 0: r[:, :s] = 0
        elif s < 0: r[:, s:] = 0
        if k <= 1: return r
        pm = r.copy(); pm[..., :3] *= pm[..., 3:4]
        ker = np.ones(k) / k
        out = np.stack([np.apply_along_axis(lambda v: np.convolve(v, ker, 'same'), 1, pm[..., c]) for c in range(4)], -1)
        al = out[..., 3:4]; out[..., :3] = np.where(al > 1e-6, out[..., :3] / np.maximum(al, 1e-6), 0)
        return out
    n = 0
    for img_i, (text, red) in enumerate(CHAPTERS):
        frames = [fi for fi in range(len(fr)) if fr[fi][0] == img_i and _title_parts(of, si, fi)]
        if not frames: continue
        final = frames[-1]
        A, keys_f, pal = compose(final)
        P = pal.astype(int); L = P.sum(1)
        ys, xs = np.where(A > 0)
        bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        vals = [int(v) for v in A[A > 0]]
        reds = {v for v in set(vals) if P[v][0] > 150 and P[v][1] < 110}
        dark = min(set(vals), key=lambda v: L[v])
        rowf, rowr = {}, {}
        for y in range(by0, by1):
            c = [int(v) for v in A[y] if v > 0 and v != dark and v not in reds and L[v] > 300]
            if c: rowf[y] = np.mean([P[v] for v in c], 0)
            c = [int(v) for v in A[y] if v in reds]
            if c: rowr[y] = np.mean([P[v] for v in c], 0)
        # crisp CN final as RGBA
        cov = np.zeros((HH, WW), bool)
        for (Y, X) in keys_f: cov[Y, X] = True
        rows_ = [y for y in range(by0, by1) if cov[y].any()]
        bx0 = max(int(np.where(cov[y])[0].min()) for y in rows_); bx1 = min(int(np.where(cov[y])[0].max()) + 1 for y in rows_)
        H = by1 - by0; W = bx1 - bx0
        f = objedit.load_font('noto_black', 64)
        tw = int(sum(f.getlength(ch) for ch in text)) + 24
        mo = Image.new('L', (tw, 96)); mf = Image.new('L', (tw, 96)); mr = Image.new('L', (tw, 96))
        x = 8
        for ch in text:
            ImageDraw.Draw(mo).text((x, 8), ch, font=f, fill=255, stroke_width=6, stroke_fill=255)
            ImageDraw.Draw(mr if ch == red else mf).text((x, 8), ch, font=f, fill=255)
            x += f.getlength(ch) - 2
        bb = mo.getbbox()
        sw = min(W, round((bb[2] - bb[0]) * (H / (bb[3] - bb[1]))))
        mo, mf, mr = [m.crop(bb).resize((sw, H), Image.LANCZOS) for m in (mo, mf, mr)]
        o = np.asarray(mo) / 255; fl = np.asarray(mf) / 255; rd = np.asarray(mr) / 255
        top_f = rowf.get(min(rowf), np.array([255, 255, 255])) if rowf else np.array([255, 255, 255])
        cn = np.zeros((HH, WW, 4))
        ox = bx0 + (W - sw) // 2
        for j in range(H):
            Y = by0 + j
            fc = rowf[min(rowf, key=lambda q: abs(q - Y))] if rowf else top_f
            rc = rowr[min(rowr, key=lambda q: abs(q - Y))] if rowr else np.array([255, 40, 40])
            for i in range(sw):
                if o[j, i] < 0.45: continue
                col = P[dark] * (1 - fl[j, i] - rd[j, i]) + fc * fl[j, i] + rc * rd[j, i]
                cn[Y, ox + i, :3] = col; cn[Y, ox + i, 3] = 1
        JPF = rgba(A, pal)
        allowed = np.array(sorted(set(vals) | {dark}))
        for fi in frames:
            B, keys, _ = compose(fi)
            JB = rgba(B, pal)
            best = None
            for k in (1, 3, 5, 7, 9, 13, 17, 23, 31, 41):
                for s in range(-48, 49, 2):
                    T = blur(JPF, s, k)
                    e = np.abs((T[..., 3] > 0.35).astype(float) - JB[..., 3]).sum()
                    if best is None or e < best[0]: best = (e, s, k)
            _, s, k = best
            for s2 in range(s - 2, s + 3):
                T = blur(JPF, s2, k); e = np.abs((T[..., 3] > 0.35).astype(float) - JB[..., 3]).sum()
                if e < best[0]: best = (e, s2, k)
            _, s, k = best
            C = blur(cn, s, k)
            out = np.zeros((HH, WW), int)
            m = C[..., 3] > 0.35
            for Y, X in zip(*np.where(m)):
                out[Y, X] = int(nearest(pal, C[Y, X, :3], allowed))
            for (Y, X), ks in keys.items():
                for kk in ks: segments.set_px(of, kk, int(out[Y, X]), False)
            n += 1
    report.append(f'chapter titles: {n} frames')


NEWS_ROWS = [['TOB！', '追加保证金！', '低PBR股热潮！'], ['发生大地震！', '旅行热潮！', '发行MSCB！'],
             ['登上股票报纸！', '棒球热潮！', '南滨一郎推荐！'], ['丑闻曝光！', '券商上调评级', '发生事故！'],
             ['游戏热潮！', '公示地价上涨！', '下调预期'], ['低价股热潮！', '商社股热潮！', '上调预期'],
             ['资源股热潮！', '金融股热潮！', '狂欢化！'], ['新兴股热潮！', '券商下调评级', '取得专利！'],
             ['IT股热潮！', '一部市场股热潮！'], ['丸菱关联股热潮！', '二部市场股热潮！'],
             ['帝国关联股热潮！', '高科技股热潮！'], ['热门商品诞生！', '业务合作！']]
NEWS_SPANS = [[(1, 45), (48, 106), (112, 222)], [(0, 71), (80, 151), (160, 244)], [(0, 71), (80, 151), (160, 244)],
              [(0, 71), (80, 169), (176, 234)], [(0, 83), (96, 180), (192, 242)], [(0, 83), (96, 180), (192, 242)],
              [(0, 83), (96, 180), (192, 250)], [(0, 83), (96, 185), (192, 250)], [(4, 110), (112, 222)],
              [(0, 110), (112, 222)], [(0, 110), (112, 222)], [(1, 97), (112, 171)]]
RULE_SPANS = {'news_00.bin': [[(0, 118), (128, 250)], [(0, 131), (132, 250)], [(0, 131), (132, 224)], [(0, 111), (112, 255)]],
              'news_01.bin': [[(0, 101), (102, 256)], [(0, 176)], [(0, 195)], [(0, 218)]],
              'news_02.bin': [[(0, 218)], [(0, 180)], [(0, 235)], []]}
NEWS_RULES = {'news_00.bin': [['规则：标准规则', '规则：试炼领域'], ['规则：牛市标准规则', '规则：无尽'],
                              ['规则：熊市标准规则', '规则：精神战'], ['规则：一边倒', '规则：八击八杀']],
              'news_01.bin': [['规则：三支箭', '规则：疯狂马卡洛夫'], ['规则：西部德州扑克'],
                              ['规则：标准规则试炼'], ['规则：牛市标准规则试炼']],
              'news_02.bin': [['规则：熊市标准规则试炼'], ['规则：一边倒试炼'], ['规则：疯狂马卡洛夫试炼'], []]}


def _news_spans(band, rule):
    """phrase spans (x0, x1) of one 16-px text row: split after '！' glyphs and at wide gaps."""
    col = band.any(0); runs = []; x = 0
    while x < 256:
        if col[x]:
            s = x
            while x < 256 and col[x]: x += 1
            runs.append([s, x])
        x += 1
    def bang(r):
        s, e = r
        if e - s > 3: return False
        rows = band[:, s:e].any(1); ys = np.where(rows)[0]
        return ys.max() - ys.min() >= 8 and any(not rows[y] for y in range(ys.min(), ys.max()))
    spans = []
    for i, r in enumerate(runs):
        if spans and not rule and bang(runs[i]) is False and spans[-1][2]:
            spans.append([r[0], r[1], False]); continue
        if not spans or (r[0] - spans[-1][1] >= (8 if rule else 6) and not (not rule and bang(r))):
            spans.append([r[0], r[1], False])
        else:
            spans[-1][1] = r[1]
        if not rule and bang(r): spans[-1][2] = True
    return [(s, e) for s, e, _ in spans]


def news_tickers(rom, report):
    """news_00..02: 256x256 1-colour sheets of news / rule phrases used by the trade screen ticker."""
    import struct as _s
    n = 0
    for f, rules in NEWS_RULES.items():
        d = bytearray(rom.getFileByName(f)); k = _s.unpack_from('<I', d, 0)[0]
        o = [x & 0x7FFFFFFF for x in _s.unpack_from(f'<{k + 1}I', d, 4)]
        tiles = np.frombuffer(bytes(d[o[1]:o[2]]), np.uint8).reshape(-1, 8, 8)
        img = np.zeros((256, 256), np.uint8)
        for i in range(1024): y, x = divmod(i, 32); img[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = tiles[i]
        ink = int(np.bincount(img[img > 0]).argmax())
        new = img.copy()
        for r, texts in enumerate(NEWS_ROWS + rules):
            spans = NEWS_SPANS[r] if r < 12 else RULE_SPANS[f][r - 12]
            if len(spans) != len(texts):
                report.append(f'{f} row {r}: {len(spans)} spans vs {len(texts)} texts'); continue
            for (x0, x1), t in zip(spans, texts):
                new[r * 16:r * 16 + 16, x0:min(256, x1 + 1)] = 0
                m = objedit.text_mask(t, 12, 'song')
                m = objedit.squeeze(m, x1 - x0)
                h, w = m.shape
                yy = r * 16 + (16 - h) // 2; xx = x0
                new[yy:yy + h, xx:xx + w][m] = ink
                n += 1
        raw = bytearray()
        for i in range(1024): y, x = divmod(i, 32); raw += new[y * 8:y * 8 + 8, x * 8:x * 8 + 8].tobytes()
        d[o[1]:o[1] + len(raw)] = raw
        rom.setFileByName(f, bytes(d))
    report.append(f'news tickers: {n} phrases')


class _BmpOf:
    """adapter so restyle() can edit a raw 256xN 8bpp bitmap (scr*.bin: pixels + palette)."""
    def __init__(self, pix, pal):
        self.c, self.pal = pix, pal
    def canvas(self, si, fi):
        return self.c.copy(), np.arange(self.c.size).reshape(self.c.shape), self.pal
    def write(self, own, new, clear_hidden=False):
        m = own >= 0
        self.c.ravel()[own[m].ravel()] = new[m].ravel()


SCR9900 = [((6, 7, 36, 24), '相场', 'dark'), ((58, 30, 143, 46), '交易员等级', 'blue'),
           ((12, 48, 112, 64), '见习交易员', 'dark'), ((72, 112, 138, 128), '持有股票数', 'blue'),
           ((58, 147, 151, 163), '交易员点数', 'blue'), ((58, 167, 98, 183), '总资产', 'blue')]


def status_card(rom, report):
    import struct as _s
    d = bytearray(rom.getFileByName('scr9900.bin')); k = _s.unpack_from('<I', d, 0)[0]
    o = [x & 0x7FFFFFFF for x in _s.unpack_from(f'<{k + 1}I', d, 4)]
    pix = np.frombuffer(bytes(d[o[0]:o[1]]), np.uint8).reshape(-1, 256).astype(int)
    pal = np.frombuffer(bytes(d[o[1]:o[1] + 512]), '<u2').astype(int)
    pal = np.stack([(pal & 31) * 255 // 31, ((pal >> 5) & 31) * 255 // 31, ((pal >> 10) & 31) * 255 // 31], -1).astype(np.uint8)
    L = pal.astype(int).sum(1); Pi = pal.astype(int)
    isbg = lambda v: L[v] >= 520 and Pi[v][1] >= Pi[v][2] and Pi[v][1] >= Pi[v][0]
    for (x0, y0, x1, y1), text, kind in SCR9900:
        sub = pix[y0:y1, x0:x1]
        txt = [int(v) for v in sub.ravel() if L[v] < 450]
        ink = int(np.bincount(txt).argmax()) if kind == 'blue' else int(min(set(txt), key=lambda v: L[v]))
        src = pix.copy()
        for y in range(y0, y1):                              # background: same row, 8-px grid period
            for x in range(x0, x1):
                for dd in sorted(range(-160, 161, 8), key=abs):
                    if dd == 0: continue
                    xx = x + dd
                    if 0 <= xx < 256 and not (x0 <= xx < x1) and isbg(src[y, xx]):
                        pix[y, x] = src[y, xx]; break
        sp = 0
        while kind == 'blue' and objedit.text_mask(text, 12, 'song', spacing=sp + 1).shape[1] + 1 <= x1 - x0 - 1: sp += 1
        m = bold(objedit.text_mask(text, 12, 'song', spacing=sp)) if kind == 'blue' else objedit.text_mask(text, 12, 'song')
        m = objedit.squeeze(m, x1 - x0)
        stamp(pix, m, y0 + (y1 - y0 - m.shape[0]) // 2, x0, ink)
    of = _BmpOf(pix, pal)
    d[o[0]:o[1]] = of.c.astype(np.uint8).tobytes()
    rom.setFileByName('scr9900.bin', bytes(d))
    report.append('status card scr9900')
