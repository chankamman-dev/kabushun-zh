"""Edit sprite frames in obj_fnt.bin in place (tile pixels only; sizes never change).

canvas(si, fi) -> (idx, own): idx = palette-index image of the frame (-1 = no tile),
own = per-pixel (byte offset in the section, nibble/byte flag) so edits can be written back.
Tiles shared between frames change everywhere they are used."""
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pack, objgfx

FONTS = {'hei': 'C:/Windows/Fonts/simhei.ttf', 'yahei_b': 'C:/Windows/Fonts/msyhbd.ttc',
         'yahei': 'C:/Windows/Fonts/msyh.ttc', 'song': 'C:/Windows/Fonts/simsun.ttc',
         'serif_h': 'C:/Windows/Fonts/Source Han Serif SC Heavy (TrueType).ttf',
         'noto_black': 'C:/Windows/Fonts/NotoSansSC-VF.ttf:Black', 'noto_bold': 'C:/Windows/Fonts/NotoSansSC-VF.ttf:Bold',
         'noto_regular': 'C:/Windows/Fonts/NotoSansSC-VF.ttf:Regular', 'noto_medium': 'C:/Windows/Fonts/NotoSansSC-VF.ttf:Medium'}


def load_font(name, size):
    """ImageFont for FONTS[name]; 'path:Variation' picks a variable font's named instance."""
    from PIL import ImageFont
    path, _, var = FONTS[name].partition('.ttf:')
    if var:
        f = ImageFont.truetype(path + '.ttf', size); f.set_variation_by_name(var); return f
    return ImageFont.truetype(FONTS[name], size)

FLAGS = True                     # honour attr tile-high / flip bits in canvas()


class ObjFile:
    def __init__(self, fnt_bytes, dat_bytes):
        self.data = bytearray(fnt_bytes)
        n = struct.unpack_from('<I', self.data, 0)[0]
        offs = struct.unpack_from(f'<{n + 1}I', self.data, 4)
        self.secs = [(offs[i] & 0x7FFFFFFF, offs[i + 1] & 0x7FFFFFFF) for i in range(n)]
        self.dat = [s for _, s in pack.sections(dat_bytes)]

    def sec(self, si):
        a, b = self.secs[si]
        return bytes(self.data[a:b])

    def canvas(self, si, fi, t=None):
        f = self.sec(si); d = self.dat[si]
        ims = objgfx.images(f)
        img_i, parts = objgfx.frames(d, t)[fi]
        im = ims[min(img_i, len(ims) - 1)]
        bpp8 = im['pal_size'] > 32
        tsz = 64 if bpp8 else 32
        boxes = [objgfx.SIZES[(attr >> 6, (attr >> 4) & 3)] for _, attr, _, _ in parts]
        x0 = min(p[2] for p in parts); y0 = min(p[3] for p in parts)
        x1 = max(p[2] + b[0] for p, b in zip(parts, boxes)); y1 = max(p[3] + b[1] for p, b in zip(parts, boxes))
        idx = np.full((y1 - y0, x1 - x0), -1, int)
        own = np.full((y1 - y0, x1 - x0), -1, np.int64)
        base_off = self.secs[si][0] + im['data']
        ntiles = im['size'] // tsz
        hidden = []
        for (tile, attr, x, y), (w, h) in reversed(list(zip(parts, boxes))):
            hf = vf = False
            if FLAGS:                    # attr low bits: tile bits 8-9, h-flip, v-flip
                tile += 256 * (attr & 3); hf, vf = bool(attr & 4), bool(attr & 8)
            tb = tile * (2 if bpp8 else 4)
            for ty in range(h // 8):
                for tx in range(w // 8):
                    ti = tb + ty * (w // 8) + tx
                    if ti >= ntiles: continue
                    for py in range(8):
                        for px in range(8):
                            if bpp8:
                                o = base_off + ti * 64 + py * 8 + px; v = self.data[o]; key = o * 2
                            else:
                                o = base_off + ti * 32 + py * 4 + px // 2
                                v = (self.data[o] >> (4 * (px & 1))) & 15; key = o * 2 + (px & 1)
                            Y, X = y - y0 + ty * 8 + py, x - x0 + tx * 8 + px
                            if hf: X = x - x0 + w - 1 - (tx * 8 + px)
                            if vf: Y = y - y0 + h - 1 - (ty * 8 + py)
                            if v == 0 and idx[Y, X] > 0: continue      # transparent: keep the part behind
                            if own[Y, X] >= 0: hidden.append(int(own[Y, X]))
                            idx[Y, X] = v; own[Y, X] = key
        self._bpp8 = bpp8
        vis = set(own[own >= 0].tolist())
        self._hidden = [k for k in hidden if k not in vis]
        pal = objgfx.palette(f, im)
        return idx, own, pal

    def write(self, own, idx, clear_hidden=False):
        """write the canvas back; pixels of parts covered by a front part are cleared so that
        edited transparent pixels do not reveal the old content behind."""
        pairs = list(zip(own.ravel(), idx.ravel()))
        if clear_hidden: pairs += [(k, 0) for k in getattr(self, '_hidden', [])]
        for k, v in pairs:
            if k < 0 or v < 0: continue
            o, hi = divmod(int(k), 2)
            if self._bpp8: self.data[o] = int(v)
            else:
                b = self.data[o]
                self.data[o] = (b & 0x0F) | (int(v) << 4) if hi else (b & 0xF0) | int(v)


def text_mask(text, size, font='hei', spacing=0, threshold=110, bold=False, aa=None):
    """Render text as a bool mask (tight height = size)."""
    f = load_font(font, size)
    w = sum(int(f.getlength(c)) + spacing for c in text) + 4
    im = Image.new('L', (max(w, 1), size + 8), 0)
    d = ImageDraw.Draw(im)
    if aa is False or (aa is None and size <= 16): d.fontmode = '1'
    x = 1
    for c in text:
        d.text((x, 2), c, font=f, fill=255)
        if bold: d.text((x + 1, 2), c, font=f, fill=255)
        x += int(f.getlength(c)) + spacing
    a = np.asarray(im) > threshold
    ys = np.where(a.any(1))[0]; xs = np.where(a.any(0))[0]
    if not len(ys): return np.zeros((size, 1), bool)
    return a[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]


def squeeze(mask, max_w):
    """Horizontally scale a mask down (nearest) to fit max_w."""
    h, w = mask.shape
    if w <= max_w: return mask
    xs = (np.arange(max_w) * w / max_w).astype(int)
    return mask[:, xs]
