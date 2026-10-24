"""Rebuild KSSCV.bin text sections (7 pool, 8 line lists, 9 message index)
from the markup text, plus the 2-bit page map for the pool."""
import re, struct
from pathlib import Path
from ksscv import Ksscv, LOAD, charmap, decode_units, pages
from textenc import Encoder

MAX_W = 20

def parse(path):
    """text file(s) -> {id: [[line, ...] per page]}; a directory means every ksscv*.txt in it"""
    p = Path(path)
    files = sorted(p.glob('ksscv*.txt')) if p.is_dir() else [p]
    text = '\n'.join(f.read_text(encoding='utf8') for f in files)
    msgs, cur = {}, None
    for raw in text.split('\n'):
        if raw.startswith('@'):
            cur = msgs.setdefault(int(raw[1:].split()[0]), [[]])
        elif cur is not None:
            if raw == '--': cur.append([])
            else: cur[-1].append(raw)
    for k, v in msgs.items():
        for pg in v:                      # trailing blank lines are file formatting, leading ones are layout
            while len(pg) > 1 and not pg[-1].strip(): pg.pop()
        msgs[k] = v
    return msgs

def build(orig_bytes, cn_path, charset, problems, stub_untranslated=False):
    k = Ksscv(orig_bytes)
    G, t0, t1 = charmap()
    enc = Encoder('t1', charset)
    cn = parse(cn_path) if cn_path and Path(cn_path).exists() else {}
    if '﻿' in str(cn.keys()): pass
    pool, pool_pages, lists = bytearray(), [], []
    page0_codes = set()
    for mi, msg in enumerate(k.messages):
        jp_pages = pages(msg)
        line_units = []          # [(units, pages, terminator)]
        if mi in cn:
            cpages = cn[mi]
            for pi, pg in enumerate(cpages):
                jp_n = len(jp_pages[pi]) if pi < len(jp_pages) else 3
                limit = max(jp_n, 3) if len(jp_pages) and max(len(p) for p in jp_pages) <= 3 else jp_n
                if len(pg) > limit: problems.append(f'@{mi} page {pi}: {len(pg)} lines > {limit}')
                for li, line in enumerate(pg):
                    flag = 0
                    if line.startswith('^'): flag |= 0x2000; line = line[1:]
                    u, p, n = enc.encode(line)
                    if n > MAX_W: problems.append(f'@{mi} line too long ({n}): {line}')
                    last = li == len(pg) - 1
                    if last and pi < len(cpages) - 1: flag |= 0x800
                    line_units.append((u, p, 0x8000 | flag | n))
        elif stub_untranslated:
            line_units.append(([0x108, 0x108], [0, 0], 0x8002))   # '……'
        else:
            for u, f in msg:
                n = sum(1 for x in u if not x & 0x4000)
                line_units.append((list(u), [0] * len(u), 0x8000 | f | n))
        ptrs = []
        for u, p, term in line_units:
            ptrs.append(LOAD + k.pool + len(pool))
            for x, pg in zip(u, p):
                if not x & 0x4000 and pg == 0: page0_codes.add(x & 0x3FF)
            pool += struct.pack(f'<{len(u) + 1}H', *u, term)
            pool_pages += p + [0]
        lists.append(ptrs)
    # layout: header..section6 unchanged | pool | s8 | s9 | page bits
    out = bytearray(orig_bytes[:k.pool])
    out += pool
    while len(out) % 4: out += b'\0'; pool_pages.append(0)
    s8 = len(out)
    list_addr = []
    for ptrs in lists:
        list_addr.append(LOAD + len(out))
        out += struct.pack(f'<{len(ptrs) + 1}I', *ptrs, 0)
    s9 = len(out)
    out += struct.pack(f'<{len(list_addr)}I', *list_addr)
    struct.pack_into('<I', out, 0x20, LOAD + s8)
    struct.pack_into('<I', out, 0x24, LOAD + s9)
    bits = bytearray((len(pool_pages) + 3) // 4)
    for i, p in enumerate(pool_pages):
        bits[i // 4] |= p << ((i % 4) * 2)
    bits_off = len(out)
    out += bits
    return dict(data=bytes(out), pool_start=LOAD + k.pool, pool_end=LOAD + k.pool + len(pool),
                bits_addr=LOAD + bits_off, page0_codes=page0_codes, any_cn=bool(cn))
