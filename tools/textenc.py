"""Markup text -> 16-bit units + page numbers, shared glyph allocation."""
import re
from ksscv import charmap

# chars that keep the original (page 0) glyph when the table can reach it
PAGE0_OK = set('０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
               'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
               '！？＃＄％＆（）＊＋－／＜＝＞＠［］＾＿｛｝｜～　…・ー「」×▼△■￥')
TOKEN = re.compile(r'\{(\d)\}|<(\d)>|\[x([0-9a-fA-F]{4})\]|\[(\d+)\]|\{(tb|orz|\+|A|B|X|Y|L|R|>|>b|>c)\}|(.)', re.S)
SPECIAL = {'tb': '{tb}', 'orz': '{orz}', '+': '{+}', 'A': '{A}', 'B': '{B}', 'X': '{X}', 'Y': '{Y}',
           'L': '{L}', 'R': '{R}', '>': '{>}', '>b': '{>b}', '>c': '{>c}'}

class Charset:
    """Global allocation of new glyphs (gid -> char)."""
    def __init__(self):
        self.chars = []
        self.index = {}
    def gid(self, ch):
        g = self.index.get(ch)
        if g is None:
            g = self.index[ch] = len(self.chars)
            self.chars.append(ch)
            assert g < 3 * 1024, 'too many glyphs'
        return g

class Encoder:
    def __init__(self, table, charset):
        G, t0, t1 = charmap()
        G = dict(G)
        G['12'] = '、'; G['14'] = '。'          # ASCII ',' '.' slots actually draw 、。
        self.page0 = {}
        for code in range(1024):
            if table == 'both':                 # ARM9 strings: table unknown, use codes equal in both
                if t0[code] != t1[code]: continue
                g = t0[code]
            else:
                g = (t0 if table == 't0' else t1)[code]
            ch = G[str(g)]
            if g < 285 and ch not in self.page0:
                self.page0[ch] = code
        self.cs = charset

    def encode(self, text):
        """-> (units, pages, count) for one line."""
        units, pages, col, eff, n = [], [], 0, 0, 0
        for m in TOKEN.finditer(text):
            c, e, xcmd, wcmd, sp, ch = m.groups()
            if c is not None: col = int(c); continue
            if e is not None: eff = int(e); continue
            if xcmd is not None: units.append(0x4000 | int(xcmd, 16)); pages.append(0); continue
            if wcmd is not None: units.append(0x4000 | int(wcmd)); pages.append(0); continue
            if sp is not None: ch = SPECIAL[sp]
            hb = (eff << 12) | (col << 10)
            if ch in self.page0 and (ch in PAGE0_OK or ch.startswith('{') or '぀' <= ch <= 'ヿ'):
                units.append(hb | self.page0[ch]); pages.append(0)
            else:
                g = self.cs.gid(ch)
                units.append(hb | (g & 0x3FF)); pages.append((g >> 10) + 1)
            n += 1
        return units, pages, n
