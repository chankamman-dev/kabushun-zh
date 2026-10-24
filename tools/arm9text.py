"""ARM9 UI strings: fixed-position line slots inside two text blocks (table t0)."""
import json, re, struct
from pathlib import Path
from ksscv import charmap, decode_units

BASE = 0x2000000
BLOCKS = [(0x210BA80, 0x210D860), (0x216F000, 0x2185000)]
JPCHAR = re.compile(r'[぀-ヿ一-鿿０-ｚ]')

def lines(arm9):
    """All validated lines: (addr, units, terminator)."""
    out = []
    for s, e in BLOCKS:
        o = s - BASE
        while o < e - BASE:
            units, p, ok = [], o, False
            for _ in range(60):
                u = struct.unpack_from('<H', arm9, p)[0]; p += 2
                if u & 0x8000:
                    ok = (u & 0x7FF) == sum(1 for x in units if not x & 0x4000)
                    break
                units.append(u)
            if ok:
                out.append((BASE + o, units, u)); o = p
            else:
                o += 2
    return out

def freq():
    """Plausibility of a decoded line: known bigrams first, unigram log-frequency second."""
    import collections, math
    root = Path(__file__).resolve().parent.parent
    corpus = (root / 'text/jp/ksscv.txt').read_text(encoding='utf8')
    uni = collections.Counter(corpus)
    bi = set(corpus[i:i + 2] for i in range(len(corpus) - 1))
    tot = sum(uni.values())
    def score(txt):
        s = re.sub(r'\{\d\}|<\d>|\[x?[0-9a-f]+\]', '', txt)
        b = sum(1 for i in range(len(s) - 1) if s[i:i + 2] in bi)
        u = sum(max(math.log((uni.get(ch, 0) + 0.1) / tot), -11) for ch in s if JPCHAR.match(ch))
        return (b, u)
    return score

def export(arm9, path):
    """Each line is decoded with both tables; the more plausible reading comes
    first, the other (if different) follows on a '#' line for the translator."""
    G, t0, t1 = charmap()
    f = freq()
    rows = []
    for addr, units, term in lines(arm9):
        cand = sorted(((f(decode_units(units, G, T)), -tn, decode_units(units, G, T))
                       for tn, T in ((0, t0), (1, t1))), reverse=True)
        txt = cand[0][2]
        if not JPCHAR.search(txt): continue
        alt = f'\n#{cand[1][2]}' if cand[1][2] != txt else ''
        rows.append(f'@{addr:x} {len(units)}\n{txt}{alt}')
    Path(path).write_text('\n'.join(rows) + '\n', encoding='utf8')
    return len(rows)

if __name__ == '__main__':
    root = Path(__file__).resolve().parent.parent
    print(export((root / 'work/arm9_dec.bin').read_bytes(), root / 'text/jp/arm9.txt'))
