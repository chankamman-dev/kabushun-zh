"""Apply substring fixes inside message blocks: lines 'id|old|new' (old must occur in that block).
old may ignore markup ([n], [xHHHH], <n>, {n}); markup inside the matched span is re-inserted
after the same character occurrence in new (or kept at the edges)."""
import sys, glob, re
sys.stdout.reconfigure(encoding='utf-8')
MK = r'(?:\[x?[0-9a-f]+\]|<\d>|\{\d\})'
subs = []
for line in open(sys.argv[1], encoding='utf-8').read().split('\n'):
    if not line.strip() or line.startswith('#'): continue
    i, old, new = line.split('|', 2)
    subs.append((int(i), old, new))
files = {f: open(f, encoding='utf-8').read() for f in sorted(glob.glob('text/cn/ksscv*.txt'))}
def block(text, mid):
    tag = f'@{mid}\n'
    if text.startswith(tag): a = 0
    else:
        a = text.find('\n' + tag)
        if a < 0: return None
        a += 1
    b = text.find('\n@', a + len(tag))
    return a, (b if b >= 0 else len(text))
def fuzzy(seg, old, new):
    pat = (MK + '*').join(re.escape(c) for c in old)
    m = re.search(pat, seg)
    if not m: return None
    span = m.group(0)
    toks, plain = [], ''
    for t in re.finditer(MK + '|.', span, re.S):
        s = t.group(0)
        if len(s) > 1 or re.fullmatch(MK, s): toks.append((plain, s))
        else: plain += s
    out = new
    ins = []
    for pre, tok in toks:
        if not pre: ins.append((0, tok)); continue
        c, k = pre[-1], pre.count(pre[-1])
        pos = [j + 1 for j, ch in enumerate(new) if ch == c]
        ins.append((pos[min(k, len(pos)) - 1] if pos else len(new), tok))
    for p, tok in sorted(ins, key=lambda x: -x[0]): out = out[:p] + tok + out[p:]
    return seg[:m.start()] + out + seg[m.end():]
bad = []
for mid, old, new in subs:
    for f, t in files.items():
        r = block(t, mid)
        if r is None: continue
        a, b = r
        seg = t[a:b]
        if old in seg: seg = seg.replace(old, new, 1)
        else:
            s2 = fuzzy(seg, old, new)
            if s2 is None: bad.append((mid, old)); break
            seg = s2
        files[f] = t[:a] + seg + t[b:]
        break
    else:
        bad.append((mid, 'NO BLOCK'))
for f, t in files.items(): open(f, 'w', encoding='utf-8', newline='\n').write(t)
print('applied', len(subs) - len(bad), 'failed', bad)
