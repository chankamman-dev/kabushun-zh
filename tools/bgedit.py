"""Edit 8bpp background screens (sec0 tile images, sec1 32x24 maps) and rebuild the container."""
import struct
from collections import Counter
import numpy as np
import ndspy.lz10 as lz10
import pack, objgfx, bggfx


class BgFile:
    def __init__(self, data):
        self.orig = bytes(data)
        n = struct.unpack_from('<I', data, 0)[0]
        offs = struct.unpack_from(f'<{n + 1}I', data, 4)
        self.flags = [o & 0x80000000 for o in offs]
        raw = [bytes(data[offs[i] & 0x7FFFFFFF: offs[i + 1] & 0x7FFFFFFF]) for i in range(n)]
        self.seclz = [bool(f) and r[:1] == b'' for f, r in zip(self.flags, raw)]
        self.secs = [bytearray(lz10.decompress(r) if z else r) for r, z in zip(raw, self.seclz)]
        s0 = bytes(self.secs[0])
        self.ims = objgfx.images(s0)
        self.tiles, self.comp, self.pals_raw = [], [], []
        for im in self.ims:
            comp = (im['b'] >> 16) & 0xFF == 0x46
            raw = bggfx.tiledata(s0, im)
            self.comp.append(comp)
            self.tiles.append(bytearray(raw))
            self.pals_raw.append(s0[im['pal']: im['pal'] + im['pal_size']])
        self.dirty = False
        s1 = bytes(self.secs[1])
        first = struct.unpack_from('<I', s1, 0)[0]
        self.map_offs = [struct.unpack_from('<I', s1, 4 * i)[0] for i in range(first // 4)]
        self.maps = []
        for o in self.map_offs:
            _, w, h = struct.unpack_from('<IHH', s1, o)
            self.maps.append(np.frombuffer(s1[o + 8: o + 8 + 2 * w * h], '<u2').reshape(h, w).copy())
        self.pal = bggfx.palettes(bytes(self.secs[2]))

    def tile(self, ts, t):
        return np.frombuffer(bytes(self.tiles[ts][t * 64:(t + 1) * 64]), np.uint8).reshape(8, 8)

    def canvas(self, mi, ts, rect):
        cx0, cy0, cx1, cy1 = rect
        m = self.maps[mi]
        out = np.zeros(((cy1 - cy0) * 8, (cx1 - cx0) * 8), int)
        for cy in range(cy0, cy1):
            for cx in range(cx0, cx1):
                e = int(m[cy, cx]); t = self.tile(ts, e & 0x3FF)
                if e & 0x400: t = t[:, ::-1]
                if e & 0x800: t = t[::-1]
                out[(cy - cy0) * 8:(cy - cy0) * 8 + 8, (cx - cx0) * 8:(cx - cx0) * 8 + 8] = t
        return out

    def edit(self, mi, ts, rect, img):
        """queue new pixels for the cells of rect (cell coords); commit() applies them."""
        if not hasattr(self, 'pending'): self.pending = {}
        cx0, cy0, cx1, cy1 = rect
        old = self.canvas(mi, ts, rect)
        for cy in range(cy0, cy1):
            for cx in range(cx0, cx1):
                sl = (slice((cy - cy0) * 8, (cy - cy0) * 8 + 8), slice((cx - cx0) * 8, (cx - cx0) * 8 + 8))
                blk = img[sl].astype(np.uint8)
                if (blk == old[sl]).all(): continue
                self.pending[(ts, mi, cy, cx)] = blk.tobytes()

    def commit(self, ts_maps=None):
        """ts_maps: {tileset: [map indices drawn with it]} for counting tile uses."""
        added = 0
        pend = getattr(self, 'pending', {})
        by_ts = {}
        for (ts, mi, cy, cx), data in pend.items(): by_ts.setdefault(ts, {})[(mi, cy, cx)] = data
        for ts, edits in by_ts.items():
            maps = (ts_maps or {}).get(ts, range(len(self.maps)))
            uses = {}
            for mi in maps:
                m = self.maps[mi]
                for cy in range(m.shape[0]):
                    for cx in range(m.shape[1]):
                        uses.setdefault(int(m[cy, cx]) & 0x3FF, []).append((mi, cy, cx))
            existing = {}
            n = len(self.tiles[ts]) // 64
            for t in range(n): existing.setdefault(bytes(self.tiles[ts][t * 64:(t + 1) * 64]), t)
            done = set()
            for (mi, cy, cx), data in edits.items():
                if (mi, cy, cx) in done: continue
                e = int(self.maps[mi][cy, cx]); t = e & 0x3FF
                us = uses.get(t, [])
                same = all(u in edits and edits[u] == data and
                           (int(self.maps[u[0]][u[1], u[2]]) & 0xC00) == (e & 0xC00) for u in us)
                if same and not (e & 0xC00):
                    self.tiles[ts][t * 64:(t + 1) * 64] = data
                    done.update(us); continue
                if data in existing:
                    nt = existing[data]
                else:
                    nt = len(self.tiles[ts]) // 64
                    self.tiles[ts] += data; existing[data] = nt; added += 1
                self.maps[mi][cy, cx] = (e & 0xF000) | nt
                done.add((mi, cy, cx))
        self.pending = {}
        self.dirty = True
        return added

    def build(self):
        if not self.dirty: return self.orig
        # sec0: entries + (data, palette) pairs
        n = len(self.ims)
        hdr = 20 * n
        body = bytearray(); fields = []
        for i, im in enumerate(self.ims):
            data = bytes(self.tiles[i])
            if self.comp[i]: data = lz10.compress(data)
            while len(data) % 4: data += b'\0'
            doff = hdr + len(body); body += data
            poff = hdr + len(body); body += self.pals_raw[i]
            fields.append((doff, len(data), poff))
        s0 = bytearray(hdr)
        for i, (im, (doff, size, poff)) in enumerate(zip(self.ims, fields)):
            p = 20 * i
            a = (im['a'] & ~0x3FFFF & 0xFFFFFFFF) | size
            if i == 0: struct.pack_into('<I', s0, 0, doff)
            else: struct.pack_into('<I', s0, p, doff - p)
            struct.pack_into('<III', s0, p + 4, a, im['b'], poff - (p + 12))
            orig_s0 = bytes(self.secs[0])
            struct.pack_into('<I', s0, p + 16, struct.unpack_from('<I', orig_s0, im['field'] + 16)[0])
        s0 += body
        # sec1: maps in place
        s1 = bytearray(self.secs[1])
        for o, m in zip(self.map_offs, self.maps):
            s1[o + 8: o + 8 + m.size * 2] = m.astype('<u2').tobytes()
        secs = [bytes(s0), bytes(s1)] + [bytes(s) for s in self.secs[2:]]
        secs = [lz10.compress(x) if z else x for x, z in zip(secs, self.seclz)]
        n = len(secs)
        out = bytearray(struct.pack('<I', n))
        pos = 4 + 4 * (n + 1)
        offs = []
        for f, s in zip(self.flags, secs):
            offs.append(pos | f); pos += len(s)
            while pos % 4: pos += 1
        offs.append(pos)
        out += struct.pack(f'<{n + 1}I', *offs)
        for s in secs:
            out += s
            while len(out) % 4: out += b'\0'
        return bytes(out)
