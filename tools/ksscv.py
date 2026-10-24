"""KSSCV.bin script/text container.

Header: 10 absolute pointers (file loads at 0x22B4000). Section 7 is the text
pool, section 8 holds zero-terminated line-pointer lists, section 9 holds one
pointer per message into section 8.  A line is a run of 16-bit units ended by
0x8000|flags|count (count = displayed chars, 0x800 = page break).

Markup used in the text files:
  {n}   colour n (bits 10-11) from here on       <n>  effect n (bits 12-13)
  [n]   command 0x4000|n with n < 0x100 (waits)  [xHHHH] other command
  page = lines separated by '\n'; pages separated by a line '--'
"""
import json, re, struct
from pathlib import Path

LOAD = 0x22B4000
ROOT = Path(__file__).resolve().parent.parent

def charmap():
    cm = json.loads((ROOT / 'work/charmap.json').read_text(encoding='utf8'))
    return cm['glyph'], cm['t0'], cm['t1']

class Ksscv:
    def __init__(self, data):
        self.data = bytes(data)
        self.ptr = [p - LOAD for p in struct.unpack_from('<10I', data, 0)]
        self.pool, self.s8, self.s9 = self.ptr[7], self.ptr[8], self.ptr[9]
        n = (len(data) - self.s9) // 4
        self.messages = []
        for i in range(n):
            o = struct.unpack_from('<I', data, self.s9 + 4 * i)[0] - LOAD
            lines = []
            while True:
                p = struct.unpack_from('<I', data, o)[0]; o += 4
                if p == 0: break
                lines.append(self.read_line(p - LOAD))
            self.messages.append(lines)

    def read_line(self, o):
        units = []
        while True:
            u = struct.unpack_from('<H', self.data, o)[0]; o += 2
            if u & 0x8000: return units, u & 0x7800
            units.append(u)

def decode_units(units, G, T):
    out, col, eff = [], 0, 0
    for u in units:
        if u & 0x4000:
            v = u & 0x3FFF
            out.append(f'[{v}]' if v < 0x100 else f'[x{v:04x}]'); continue
        c, e = (u >> 10) & 3, (u >> 12) & 3
        if c != col: out.append(f'{{{c}}}'); col = c
        if e != eff: out.append(f'<{e}>'); eff = e
        out.append(G[str(T[u & 0x3FF])])
    if col: out.append('{0}')
    if eff: out.append('<0>')
    return ''.join(out)

def pages(lines):
    """[(units, flags)] -> list of pages, each a list of (units, flags)."""
    pg, cur = [], []
    for i, (u, f) in enumerate(lines):
        cur.append((u, f))
        if f & 0x800 or i == len(lines) - 1:
            pg.append(cur); cur = []
    return pg

def export(path_bin, out_path):
    G, t0, t1 = charmap()
    k = Ksscv(Path(path_bin).read_bytes())
    blocks = []
    for i, msg in enumerate(k.messages):
        body = []
        for pi, pg in enumerate(pages(msg)):
            if pi: body.append('--')
            for u, f in pg:
                body.append(('^' if f & 0x2000 else '') + decode_units(u, G, t1))
        blocks.append(f'@{i}\n' + '\n'.join(body))
    Path(out_path).write_text('\n'.join(blocks) + '\n', encoding='utf8')
    return k

if __name__ == '__main__':
    k = export(ROOT / 'extract/KSSCV.bin', ROOT / 'text/jp/ksscv.txt')
    print(len(k.messages), 'messages')
