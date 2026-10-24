"""Make (and verify) a BPS patch from the original ROM to the translated ROM.
usage: mkbps.py original.nds translated.nds out.bps
Files that only moved inside the ROM are encoded as SourceCopy, unchanged bytes at the same
offset as SourceRead, everything else as TargetRead."""
import sys, struct, zlib


def varint(n):
    out = bytearray()
    while True:
        x = n & 0x7F; n >>= 7
        if n == 0: out.append(0x80 | x); return bytes(out)
        out.append(x); n -= 1


def fat(rom):
    off, size = struct.unpack_from('<II', rom, 0x48)
    return [struct.unpack_from('<II', rom, off + 8 * i) for i in range(size // 8)]


def regions(rom):
    """(start, end) of every file plus ARM9/ARM7/banner, keyed for matching between ROMs."""
    r = {('file', i): (a, b) for i, (a, b) in enumerate(fat(rom)) if b > a}
    a9, _, _, s9 = struct.unpack_from('<IIII', rom, 0x20)
    a7, _, _, s7 = struct.unpack_from('<IIII', rom, 0x30)
    r[('arm9',)] = (a9, a9 + s9); r[('arm7',)] = (a7, a7 + s7)
    bn = struct.unpack_from('<I', rom, 0x68)[0]
    if bn: r[('banner',)] = (bn, bn + 0x840)
    return r


def make(src, tgt):
    rs, rt = regions(src), regions(tgt)
    copies = {}; edits = {}                              # target start -> (length, source start)
    for k, (a, b) in rt.items():
        if k in rs:
            sa, sb = rs[k]
            if sb - sa == b - a and src[sa:sb] == tgt[a:b]: copies[a] = (b - a, sa)
            else: edits[a] = (b - a, sa, sb - sa)              # changed file: diff against its old copy
    out = bytearray(b'BPS1') + varint(len(src)) + varint(len(tgt)) + varint(0)
    import numpy as np
    n = len(tgt); m = min(n, len(src))
    eq = np.zeros(n, bool); eq[:m] = np.frombuffer(src[:m], np.uint8) == np.frombuffer(tgt[:m], np.uint8)
    srel = 0
    def gap(i, j):                                       # bytes i..j outside the moved files
        k = i
        while k < j:
            # next run of >= 16 equal bytes
            seg = eq[k:j]
            if seg.all() and j - k >= 16:
                out.extend(varint(((j - k - 1) << 2) | 0)); return
            idx = np.flatnonzero(np.diff(np.concatenate(([0], seg.view(np.int8), [0]))))
            runs = [(k + s_, k + e_) for s_, e_ in zip(idx[0::2], idx[1::2]) if e_ - s_ >= 16]
            pos = k
            for s_, e_ in runs:
                if s_ > pos: out.extend(varint(((s_ - pos - 1) << 2) | 1)); out.extend(tgt[pos:s_])
                out.extend(varint(((e_ - s_ - 1) << 2) | 0)); pos = e_
            if pos < j: out.extend(varint(((j - pos - 1) << 2) | 1)); out.extend(tgt[pos:j])
            return
    def scopy(ln, sa, ta):
        nonlocal srel
        if sa == ta: out.extend(varint(((ln - 1) << 2) | 0)); return
        d = sa - srel
        out.extend(varint(((ln - 1) << 2) | 2)); out.extend(varint((abs(d) << 1) | (d < 0)))
        srel = sa + ln
    def edit(a_, ln, sa, sl):
        m_ = min(ln, sl)
        e = np.frombuffer(src[sa:sa + m_], np.uint8) == np.frombuffer(tgt[a_:a_ + m_], np.uint8)
        idx = np.flatnonzero(np.diff(np.concatenate(([0], e.view(np.int8), [0]))))
        pos = 0
        for s_, e_ in zip(idx[0::2], idx[1::2]):
            if e_ - s_ < 16: continue
            if s_ > pos: out.extend(varint(((s_ - pos - 1) << 2) | 1)); out.extend(tgt[a_ + pos:a_ + s_])
            scopy(e_ - s_, sa + s_, a_ + s_); pos = e_
        if pos < ln: out.extend(varint(((ln - pos - 1) << 2) | 1)); out.extend(tgt[a_ + pos:a_ + ln])
    i = 0
    allr = {**{a_: ('c',) + v for a_, v in copies.items()}, **{a_: ('e',) + v for a_, v in edits.items()}}
    for a_ in sorted(allr):
        if a_ < i: continue
        if a_ > i: gap(i, a_)
        r_ = allr[a_]
        if r_[0] == 'c': scopy(r_[1], r_[2], a_)
        else: edit(a_, r_[1], r_[2], r_[3])
        i = a_ + r_[1]
    if i < n: gap(i, n)
    out += struct.pack('<II', zlib.crc32(src), zlib.crc32(tgt))
    out += struct.pack('<I', zlib.crc32(out))
    return bytes(out)


def apply(src, patch):
    p = 4
    def rd():
        nonlocal p
        data, shift = 0, 1
        while True:
            x = patch[p]; p += 1
            data += (x & 0x7F) * shift
            if x & 0x80: return data
            shift <<= 7; data += shift
    ss, ts, ms = rd(), rd(), rd(); p += ms
    tgt = bytearray(ts); o = 0; srel = trel = 0
    while p < len(patch) - 12:
        d = rd(); cmd, ln = d & 3, (d >> 2) + 1
        if cmd == 0: tgt[o:o + ln] = src[o:o + ln]
        elif cmd == 1: tgt[o:o + ln] = patch[p:p + ln]; p += ln
        elif cmd == 2:
            v = rd(); srel += -(v >> 1) if v & 1 else (v >> 1)
            tgt[o:o + ln] = src[srel:srel + ln]; srel += ln
        else:
            v = rd(); trel += -(v >> 1) if v & 1 else (v >> 1)
            for k in range(ln): tgt[o + k] = tgt[trel]; trel += 1
        o += ln
    return bytes(tgt)


if __name__ == '__main__':
    src = open(sys.argv[1], 'rb').read(); tgt = open(sys.argv[2], 'rb').read()
    bps = make(src, tgt)
    assert apply(src, bps) == tgt, 'patch does not reproduce the target'
    open(sys.argv[3], 'wb').write(bps)
    print(f'{sys.argv[3]}: {len(bps):,} bytes, verified (source crc32 {zlib.crc32(src):08X}, target {zlib.crc32(tgt):08X})')
