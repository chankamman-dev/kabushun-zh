"""Apply 'addr|old|new' substring fixes inside @addr blocks of text/cn/arm9.txt (or a given file)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = sys.argv[2] if len(sys.argv) > 2 else 'text/cn/arm9.txt'
t = open(path, encoding='utf-8').read()
bad = 0
for line in open(sys.argv[1], encoding='utf-8').read().split('\n'):
    if not line.strip() or line.startswith('#'): continue
    a, old, new = line.split('|', 2)
    tag = f'@{a}\n'
    i = t.find(tag)
    if i < 0: print('no block', a); bad += 1; continue
    j = t.find('\n@', i + len(tag)); j = len(t) if j < 0 else j
    seg = t[i:j]
    if old not in seg: print('miss', a, old); bad += 1; continue
    t = t[:i] + seg.replace(old, new, 1) + t[j:]
open(path, 'w', encoding='utf-8', newline='\n').write(t)
print('done, failed', bad)
