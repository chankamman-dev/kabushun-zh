"""Side-by-side JP/CN review chunks: work/review/kNNNN.txt (per message: JP lines then CN lines)."""
import sys, re, glob
sys.path.insert(0, 'tools')
from build_ksscv import parse
jp = {}
cur = None
for line in open('text/jp/ksscv.txt', encoding='utf-8').read().split('\n'):
    if line.startswith('@'):
        cur = int(line[1:].split()[0]); jp[cur] = [[]]
    elif cur is not None:
        if line == '--': jp[cur].append([])
        else: jp[cur][-1].append(line)
cn = parse('text/cn')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
ids = sorted(jp)
strip = lambda s: re.sub(r'\[x?[0-9a-f]+\]|<\d>|\{\d\}', '', s)
for k in range(0, len(ids), N):
    out = []
    for i in ids[k:k + N]:
        j = ' / '.join(' | '.join(strip(l) for l in pg if l.strip()) for pg in jp[i])
        c = ' / '.join(' | '.join(strip(l) for l in pg if l.strip()) for pg in cn.get(i, [[]]))
        if not j.strip() and not c.strip(): continue
        out.append(f'@{i}\nJ {j}\nC {c}')
    open(f'work/review/k{ids[k]:04d}.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(len(ids))
