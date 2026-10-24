"""Sprite graphics: obj_fnt.bin (tiles + palettes) and obj_dat.bin (frames of OAM parts).

obj_fnt section: entries of 20 bytes after the first word (whose own value is the offset of the
first image data, relative to offset 0):
  +0 rel data offset (relative to this field)   +4 a: low16 = data size, bits16-23 = format
  +8 b: low16 = size/4, flags                    +12 rel palette offset   +16 palette info (low16 = size)
obj_dat section: u32 rel(frames)=8, u32 rel(anim); frames: u32 n?; (u16 off, u16 count) table,
offsets relative to the table start; parts are 4 bytes: tile/4, shape<<6|size<<4|x, x, y.
"""
import struct
import numpy as np

SIZES = {  # (shape, size) -> (w, h) in pixels
    (0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64),
    (1, 0): (16, 8), (1, 1): (32, 8), (1, 2): (32, 16), (1, 3): (64, 32),
    (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}


def images(sec):
    """-> list of dict(data_off, size, fmt, pal_off, pal_size, field offsets)"""
    first = struct.unpack_from('<I', sec, 0)[0]
    out = []
    p = 0
    while True:
        if p == 0:
            doff = first
        else:
            doff = p + struct.unpack_from('<I', sec, p)[0]
        a, b, pr, pi = struct.unpack_from('<IIII', sec, p + 4)
        out.append(dict(data=doff, size=a & 0x3FFFF, fmt=(a >> 16) & 0xFF, a=a, b=b,
                        pal=p + 12 + pr, pal_size=pi & 0xFFFF, field=p))
        p += 20
        if p + 20 > first: break
    return out


def frames(sec, t=None):
    """-> list of (image index, parts); parts are (tile4, attr, x, y).
    obj_dat: u32 header offsets, the first points at the frame block (u32 4 + table)."""
    if t is None: t = struct.unpack_from('<I', sec, 0)[0] + 4
    n_first = struct.unpack_from('<H', sec, t)[0]
    nfr = n_first // 4
    out = []
    for i in range(nfr):
        off, cnt, img = struct.unpack_from('<HBB', sec, t + 4 * i)
        parts = []
        for k in range(cnt):
            q = t + off + 4 * k
            tile, attr, x, y = struct.unpack_from('<BBbb', sec, q)
            parts.append((tile, attr, x, y))
        out.append((img, parts))
    return out


def palette(sec, im):
    raw = sec[im['pal']: im['pal'] + im['pal_size']]
    c = np.frombuffer(raw, '<u2').astype(int)
    rgb = np.stack([(c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31], -1)
    return rgb.astype(np.uint8)


def tiles8(raw):
    return np.frombuffer(raw, np.uint8)[: len(raw) // 64 * 64].reshape(-1, 8, 8)


def tiles4(raw):
    a = np.frombuffer(raw, np.uint8)
    px = np.empty(a.size * 2, np.uint8)
    px[0::2] = a & 15; px[1::2] = a >> 4
    return px.reshape(-1, 8, 8)


def render(fsec, dsec, fi, tiles=None, pal=None, t=None):
    """render frame fi -> (RGBA array, origin)"""
    ims = images(fsec)
    img_i, parts = frames(dsec, t)[fi]
    im = ims[min(img_i, len(ims) - 1)]
    if tiles is None:
        raw = fsec[im['data']: im['data'] + im['size']]
        tiles = tiles8(raw) if im['pal_size'] > 32 else tiles4(raw)
    if pal is None:
        pal = palette(fsec, im)
    boxes = []
    for tile, attr, x, y in parts:
        w, h = SIZES[(attr >> 6, (attr >> 4) & 3)]
        boxes.append((x, y, w, h))
    if not boxes: return None, (0, 0)
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes); y1 = max(b[1] + b[3] for b in boxes)
    img = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    for (tile, attr, x, y), (_, _, w, h) in reversed(list(zip(parts, boxes))):
        base = tile * 4 if im['pal_size'] <= 32 else tile * 2
        for ty in range(h // 8):
            for tx in range(w // 8):
                ti = base + ty * (w // 8) + tx
                if ti >= len(tiles): continue
                t = tiles[ti]
                rgba = np.zeros((8, 8, 4), np.uint8)
                rgba[..., :3] = pal[t.astype(int) % len(pal)]
                rgba[..., 3] = np.where(t > 0, 255, 0)
                yy, xx = y - y0 + ty * 8, x - x0 + tx * 8
                m = rgba[..., 3] > 0
                img[yy:yy + 8, xx:xx + 8][m] = rgba[m]
    return img, (x0, y0)
