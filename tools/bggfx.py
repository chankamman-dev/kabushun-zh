"""Background graphics: sec0 = tile images (8bpp; attr byte2 0x46 = LZ10 compressed),
sec1 = tilemaps (u32 table of rel offsets; each map: u32 ?, u16 w, u16 h, u16 entries),
sec2 = layer config with 512-byte palettes at the end."""
import struct
import numpy as np
import ndspy.lz10 as lz10
import objgfx


def tiledata(sec0, im):
    raw = sec0[im['data']: im['data'] + max(im['size'], 4)]
    if (im['b'] >> 16) & 0xFF == 0x46 or raw[:1] == b'\x10' and (im['b'] >> 16) & 2:
        raw = lz10.decompress(sec0[im['data']:])
    return raw


def maps(sec1):
    first = struct.unpack_from('<I', sec1, 0)[0]
    n = first // 4
    offs = [struct.unpack_from('<I', sec1, 4 * i)[0] for i in range(n)]
    out = []
    for o in offs:
        if o == 0 or o + 8 > len(sec1): continue
        _, w, h = struct.unpack_from('<IHH', sec1, o)
        if not (0 < w <= 128 and 0 < h <= 128): continue
        ent = np.frombuffer(sec1[o + 8: o + 8 + 2 * w * h], '<u2')
        if ent.size < w * h: continue
        out.append((o, w, h, ent.reshape(h, w)))
    return out


def palettes(sec2):
    k = len(sec2) // 512
    pals = []
    for i in range(k):
        raw = sec2[len(sec2) - 512 * (k - i): len(sec2) - 512 * (k - i - 1) or None]
        c = np.frombuffer(raw, '<u2').astype(int)
        pals.append(np.stack([(c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31,
                              ((c >> 10) & 31) * 255 // 31], -1).astype(np.uint8))
    return pals


def render(tiles8, m, pal):
    h, w = m.shape
    img = np.zeros((h * 8, w * 8, 3), np.uint8)
    nt = len(tiles8)
    for y in range(h):
        for x in range(w):
            e = int(m[y, x]); t = e & 0x3FF
            if t >= nt: continue
            tile = tiles8[t]
            if e & 0x400: tile = tile[:, ::-1]
            if e & 0x800: tile = tile[::-1]
            img[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = pal[tile]
    return img
