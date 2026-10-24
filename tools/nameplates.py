"""Speaker name plates: a 256x128 2bpp texture in ARM9 (0x20D3FE0, palette 0x20D3FD8) cut into
cells by a table at 0x2107CAC (106 entries: u16 first part, u16 part count) and parts at
0x2107E54 (s16 x, s16 y, u16 w, u16 h, u16 u, u16 v).  Entry 2n is the plate of speaker n drawn
right-aligned (x = -w), entry 2n+1 the left-aligned one.  We redraw every name as one cell."""
import struct
import numpy as np
import objedit

TEX, TEX_W, TEX_H = 0x20D3FE0, 256, 128
INDEX, PARTS, N_ENTRY, N_PART = 0x2107CAC, 0x2107E54, 106, 0x80
INK, EDGE = 3, 1                      # palette: 0 transparent, 1 dark outline, 3 white

Q = '？？？'
NAMES = ['瞬', '奈良崎', '桐神乐', '本尼菲特', '立花', '迪亚波拉克曜子', '蛭田', '山笛', '围后', '芦屋金之助',
         '哀川', '太一', '钦平', '阿千代', '罗密欧', '敬子', '面堂', '大象', '我执', '油目',
         '南滨', '剑持', '黑川', Q, '上班族真田', '上班族前川', '上班族小山', Q, '越前', '御神',
         '圣子', Q, '数子', 'OL真奈美', Q, 'OL实加', '利根', Q, '真由', Q,
         Q, Q, '薰子', Q, '柜台', '柜台', '雷藏', '三濑', '大屋', '克洛伊',
         '花子', '小判', Q]


def cell(text):
    m = objedit.text_mask(text, 12, 'song')
    h, w = m.shape
    img = np.zeros((16, w + 4), np.uint8)
    y0 = (16 - h) // 2
    g = np.zeros_like(img, bool); g[y0:y0 + h, 2:2 + w] = m
    edge = np.zeros_like(g)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            edge |= np.roll(np.roll(g, dy, 0), dx, 1)
    img[edge] = EDGE; img[g] = INK
    W = (img.shape[1] + 7) // 8 * 8
    out = np.zeros((16, W), np.uint8); out[:, :img.shape[1]] = img
    return out


def apply(arm9, report):
    B = 0x2000000
    o = lambda a: a - B
    old = [struct.unpack_from('<2H', arm9, o(INDEX) + 4 * i) for i in range(N_ENTRY)]
    oldp = [struct.unpack_from('<hhHHHH', arm9, o(PARTS) + 12 * i) for i in range(N_PART)]
    lefts = [min(oldp[f + k][0] for k in range(c)) for f, c in old]
    tex = np.zeros((TEX_H, TEX_W), np.uint8)
    place, x, y, cache = {}, 0, 0, {}
    for n, name in enumerate(NAMES):
        if name in cache: place[n] = cache[name]; continue
        c = cell(name)
        w = min(c.shape[1], TEX_W)
        if x + w > TEX_W: x, y = 0, y + 16
        assert y + 16 <= TEX_H, 'name plate atlas full'
        tex[y:y + 16, x:x + w] = c[:, :w]
        place[n] = cache[name] = (x, y, w); x += w
    for i in range(N_ENTRY):
        u, v, w = place[i // 2]
        xo = -w if i % 2 == 0 else lefts[i]
        struct.pack_into('<2H', arm9, o(INDEX) + 4 * i, i, 1)
        struct.pack_into('<hhHHHH', arm9, o(PARTS) + 12 * i, xo, 0, w, 16, u, v)
    p = tex.reshape(TEX_H, TEX_W // 4, 4).astype(np.uint8)
    b = p[..., 0] | (p[..., 1] << 2) | (p[..., 2] << 4) | (p[..., 3] << 6)
    arm9[o(TEX):o(TEX) + TEX_W * TEX_H // 4] = b.tobytes()
    report.append(f'name plates: {len(NAMES)} names, atlas rows used {y // 16 + 1}/8')
