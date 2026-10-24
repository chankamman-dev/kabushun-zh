"""Game container: u32 n, n+1 offsets (bit31 = section is LZ10/LZ11-compressed)."""
import struct
import ndspy.lz10 as lz10
try:
    import ndspy.lz11 as lz11
except Exception:
    lz11 = None

def sections(d):
    n = struct.unpack_from('<I', d, 0)[0]
    offs = struct.unpack_from(f'<{n + 1}I', d, 4)
    out = []
    for i in range(n):
        a, b = offs[i] & 0x7FFFFFFF, offs[i + 1] & 0x7FFFFFFF
        out.append((bool(offs[i] >> 31), d[a:b]))
    return out

def unpack(d):
    res = []
    for comp, s in sections(d):
        if comp:
            if s[0] == 0x10: s = lz10.decompress(s)
            elif s[0] == 0x11 and lz11: s = lz11.decompress(s)
        res.append((comp, s))
    return res
