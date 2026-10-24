"""Compare CN translation structure with JP: missing ids, page counts, line counts."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_ksscv import parse
ROOT = Path(__file__).resolve().parent.parent
jp = parse(ROOT / 'text/jp/ksscv.txt')
cn = parse(ROOT / 'text/cn')
hi = max(cn) if cn else -1
missing = [i for i in range(hi + 1) if i not in cn and any(any(l.strip() for l in p) for p in jp.get(i, []))]
print('translated', len(cn), 'up to', hi, 'missing', missing[:50])
for i in sorted(cn):
    j, c = jp.get(i, []), cn[i]
    if len(c) != len(j):
        print(f'@{i}: pages {len(c)} vs jp {len(j)}')
