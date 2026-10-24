"""Text built from shared strip parts: find segments (chains of parts that always appear
together in the same order on a line), render them, and redraw each with a CN fragment."""
from collections import defaultdict
import numpy as np
import objedit, objgfx


def lines_of(of, si, skip):
    """per frame: list of lines; a line = list of parts (tile, attr, x, y) sorted by x."""
    out = []
    for img, ps in objgfx.frames(of.dat[si]):
        ps = [p for p in ps if (p[0], p[1]) not in skip]
        byy = defaultdict(list)
        for p in ps: byy[p[3]].append(p)
        out.append([sorted(v, key=lambda p: p[2]) for _, v in sorted(byy.items())])
    return out


def segments(of, si, skip):
    L = lines_of(of, si, skip)
    succ, pred = defaultdict(set), defaultdict(set)
    for fr in L:
        for line in fr:
            keys = [(p[0], p[1]) for p in line]
            for i, k in enumerate(keys):
                succ[k].add(keys[i + 1] if i + 1 < len(keys) else None)
                pred[k].add(keys[i - 1] if i > 0 else None)
                # gap between parts breaks a chain
            for i in range(len(line) - 1):
                w = objgfx.SIZES[(line[i][1] >> 6, (line[i][1] >> 4) & 3)][0]
                if line[i][2] + w + 2 < line[i + 1][2]: succ[keys[i]].add('gap')
    keys = set(succ)
    head = lambda k: not (len(pred[k]) == 1 and None not in pred[k] and len(succ[next(iter(pred[k]))]) == 1)
    segs = []
    for k in sorted(keys):
        if not head(k): continue
        chain = [k]
        while len(succ[chain[-1]]) == 1:
            n = next(iter(succ[chain[-1]]))
            if n in (None, 'gap') or len(pred[n]) != 1: break
            chain.append(n)
        segs.append(chain)
    return segs, L


def render_segments(of, si, skip, out):
    from PIL import Image, ImageDraw
    segs, L = segments(of, si, skip)
    pos = {}
    for fr in L:                     # relative x offsets of parts inside a segment (first occurrence)
        for line in fr:
            for p in line: pos.setdefault((p[0], p[1]), p)
    f = of.sec(si); im = objgfx.images(f)[0]; pal = objgfx.palette(f, im)
    rows = []
    for n, chain in enumerate(segs):
        x0 = pos[chain[0]][2]
        pixs = []
        X1 = 0
        for k in chain:
            pix, w, h = part_pixels(of, si, (k[0], k[1], pos[k][2], pos[k][3]))
            pixs.append((pos[k][2] - x0, pix)); X1 = max(X1, pos[k][2] - x0 + w)
        H = max(y for _, pix in pixs for (_, y) in pix) + 1
        a = np.zeros((H, X1), int); b8 = is8(of, si)
        for dx, pix in pixs:
            for (x, y), key in pix.items(): a[y, dx + x] = get_px(of, key, b8)
        rgb = pal[a]; rgb[a == 0] = (40, 40, 40)
        rows.append((n, Image.fromarray(rgb.astype(np.uint8)).resize((X1 * 2, H * 2), 0)))
    W = 1100; x = y = rh = 0; S = Image.new('RGB', (W, 6000)); d = ImageDraw.Draw(S)
    for n, img in rows:
        if x + img.width + 40 > W: x = 0; y += rh + 4; rh = 0
        rh = max(rh, img.height)
        d.text((x, y + 10), str(n), fill=(255, 255, 0)); S.paste(img, (x + 28, y)); x += img.width + 40
    S.crop((0, 0, W, y + rh + 4)).save(out)
    return segs


def part_pixels(of, si, part, img=0):
    """{(x, y): key} of one OAM part; key = byte*2 + nibble (4bpp) or byte*2 (8bpp)."""
    tile, attr, px, py = part
    ims = objgfx.images(of.sec(si)); im = ims[min(img, len(ims) - 1)]
    bpp8 = im['pal_size'] > 32
    w, h = objgfx.SIZES[(attr >> 6, (attr >> 4) & 3)]
    base = of.secs[si][0] + im['data']
    tile += 256 * (attr & 3)
    fx = (lambda X: w - 1 - X) if attr & 4 else (lambda X: X)
    fy = (lambda Y: h - 1 - Y) if attr & 8 else (lambda Y: Y)
    out = {}
    for ty in range(h // 8):
        for tx in range(w // 8):
            ti = tile * (2 if bpp8 else 4) + ty * (w // 8) + tx
            for y in range(8):
                for x in range(8):
                    pos = (fx(tx * 8 + x), fy(ty * 8 + y))
                    if bpp8: out[pos] = (base + ti * 64 + y * 8 + x) * 2
                    else:
                        o = base + ti * 32 + y * 4 + x // 2
                        out[pos] = o * 2 + (x & 1)
    return out, w, h


def is8(of, si):
    return objgfx.images(of.sec(si))[0]['pal_size'] > 32


def common_parts(of, si):
    fr = objgfx.frames(of.dat[si])
    cnt = defaultdict(int)
    for img, ps in fr:
        for k in {(p[0], p[1]) for p in ps}: cnt[k] += 1
    return {k for k, v in cnt.items() if v == len(fr)}


def redraw(of, si, cn, skip=None, size=12, font='song', dy=None):
    """cn: {segment index: text}; other segments are left alone."""
    from collections import Counter
    skip = common_parts(of, si) if skip is None else skip
    segs, L = segments(of, si, skip)
    pos = {}
    for fr in L:
        for line in fr:
            for p in line: pos.setdefault((p[0], p[1]), p)
    b8 = is8(of, si)
    val = lambda key: get_px(of, key, b8)
    gbg = {}                                  # background per (line y, row): mode over all strips
    for chain in segs:
        ly = pos[chain[0]][3]
        for k in chain:
            for (x, y), key in part_pixels(of, si, (k[0], k[1], 0, 0))[0].items():
                gbg.setdefault((ly, y), Counter())[val(key)] += 1
    gbg = {k: c.most_common(1)[0][0] for k, c in gbg.items()}
    limit = {}                                # visible width: up to the next part of the line
    first = {c[0]: n for n, c in enumerate(segs)}
    for fr in L:
        for line in fr:
            keys = [(p[0], p[1]) for p in line]
            for i, k in enumerate(keys):
                if k not in first: continue
                n = first[k]; j = i + len(segs[n])
                if j < len(line): limit[n] = min(limit.get(n, 999), line[j][2] - line[i][2])
    for n, text in cn.items():
        chain = segs[n]; x0 = pos[chain[0]][2]; ly = pos[chain[0]][3]
        cov = {}
        for k in chain:
            pix, w, h = part_pixels(of, si, (k[0], k[1], 0, 0))
            for (x, y), key in pix.items(): cov.setdefault((pos[k][2] - x0 + x, y), key)
        W = min(max(x for x, _ in cov) + 1, limit.get(n, 999))
        rowbg, txt = {}, Counter()
        for y in range(16):
            row = [val(cov[(x, y)]) for x in range(W) if (x, y) in cov]
            if row:
                rowbg[y] = gbg.get((ly, y), Counter(row).most_common(1)[0][0])
                for v in row:
                    if v != rowbg[y]: txt[v] += 1
        tc = [v for v, _ in txt.most_common()]
        ink = tc[0] if tc else 15; sh = tc[1] if len(tc) > 1 else None
        rows_with = [y for y in range(16) if any((x, y) in cov and val(cov[(x, y)]) in tc[:2] for x in range(W))]
        top = min(rows_with) if rows_with else 2
        for (x, y), key in cov.items():
            if y in rowbg and val(key) != rowbg[y]:
                set_px(of, key, rowbg[y], b8)
        right = text.startswith('>')
        if right: text = text[1:]
        m = objedit.squeeze(objedit.text_mask(text, size, font), W - 2)
        h, w = m.shape
        ty = (top - 1) if dy is None else dy
        ox = (W - 1 - w) if right else 2
        def put(x, y, v):
            k = cov.get((x, y))
            if k is not None: set_px(of, k, v, b8)
        if sh is not None:
            for yy in range(h):
                for xx in range(w):
                    if m[yy, xx]:
                        for ddx, ddy in ((1, 0), (0, 1), (1, 1)):
                            if not (yy + ddy < h and xx + ddx < w and m[yy + ddy, xx + ddx]): put(ox + xx + ddx, ty + yy + ddy, sh)
        for yy in range(h):
            for xx in range(w):
                if m[yy, xx]: put(ox + xx, ty + yy, ink)


def set_px(of, key, v, bpp8=False):
    o, hi = divmod(key, 2)
    if bpp8: of.data[o] = v; return
    b = of.data[o]
    of.data[o] = (b & 0x0F) | (v << 4) if hi else (b & 0xF0) | v


def get_px(of, key, bpp8=False):
    o, hi = divmod(key, 2)
    return of.data[o] if bpp8 else (of.data[o] >> (4 * hi)) & 15


def load_cn(path):
    from pathlib import Path
    out = {}
    for line in Path(path).read_text(encoding='utf8').splitlines():
        if not line.strip() or line.startswith('#'): continue
        k, t = line.split('|', 1); si, n = map(int, k.split(':'))
        out.setdefault(si, {})[n] = t
    return out
