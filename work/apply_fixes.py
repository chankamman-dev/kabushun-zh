"""Replace whole message blocks in text/cn/ksscv*.txt with blocks from a fixes file (@id ... )."""
import sys, glob, re
fix = {}
cur = None
for line in open(sys.argv[1], encoding='utf-8').read().split('\n'):
    if line.startswith('@'):
        cur = int(line[1:].split()[0]); fix[cur] = []
    elif cur is not None:
        fix[cur].append(line)
for k in fix:
    while fix[k] and not fix[k][-1].strip(): fix[k].pop()
done = set()
for f in sorted(glob.glob('text/cn/ksscv*.txt')):
    lines = open(f, encoding='utf-8').read().split('\n')
    out = []; skip = False
    for line in lines:
        if line.startswith('@'):
            mid = int(line[1:].split()[0])
            if mid in fix:
                out.append(line); out += fix[mid]; skip = True; done.add(mid); continue
            skip = False
        if not skip: out.append(line)
    open(f, 'w', encoding='utf-8').write('\n'.join(out))
miss = sorted(set(fix) - done)
print('applied', len(done), 'missing', miss)
