"""Drive the story: A to advance, tap choice buttons round-robin (bottom option first).
usage: autoplay.py ROM name steps [load.st]   -> work/emu/<name>_NN.png sheets, <name>.st"""
import sys, time; sys.path.insert(0, 'tools')
from emu import Emu
from PIL import Image
import numpy as np
rom, name, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
e = Emu(rom, 'work/emu')
if len(sys.argv) > 4: e.load(sys.argv[4])
else:
    e.run(960); e.tap(128, 96, after=120)
    for _ in range(30): e.press('A', hold=4, after=46)   # title: 'new game' is the default

def buttons(im):
    """centres (x, y) in bottom-screen coords of bright blue button bars."""
    a = np.asarray(im)[192:].astype(int)
    m = (a[:, :, 2] > 100) & (a[:, :, 1] >= 30) & (a[:, :, 2] - a[:, :, 0] > 60)
    m[:40] = False; m[168:] = False
    rows = m.sum(1) > 60
    out, y = [], 0
    while y < 192:
        if rows[y]:
            y0 = y
            while y < 192 and rows[y]: y += 1
            if y - y0 >= 6:
                yc = (y0 + y) // 2; r = m[y0 + 2]; x = 0
                while x < 256:
                    if r[x]:
                        x0 = x
                        while x < 256 and r[x]: x += 1
                        if x - x0 >= 50: out.append(((x0 + x) // 2, yc))
                    x += 1
        y += 1
    return out

shots, k, visits, t = [], 0, {}, time.time()
def flush():
    global shots, k
    s = Image.new('RGB', (256 * 6, 384 * 2))
    for i, im in enumerate(shots): s.paste(im, (i % 6 * 256, i // 6 * 384))
    s.save(f'work/emu/{name}_{k:02d}.png'); k += 1; shots = []

last = None; still = 0; probe = 0
PROBES = [(90, 90), (128, 96), (200, 100), (60, 150), (128, 180), (30, 180), (220, 180), (128, 40)]
for i in range(n):
    im = e.image() if e.frame else None
    b = buttons(im) if im else []
    cur = np.asarray(im).astype(int) if im else None
    if last is not None and cur is not None and np.abs(cur - last).mean() < 1.0: still += 1
    else: still = 0
    last = cur
    if still >= 6 and not b:
        x, y = PROBES[probe % len(PROBES)]; probe += 1; still = 0
        e.tap(x, y, hold=6, after=40); e.run(30); shots.append(e.image())
    elif b:
        key = tuple(b); c = visits.get(key, 0); visits[key] = c + 1
        x, y = b[::-1][c % len(b)]
        e.tap(x, y, hold=6, after=40); e.run(30)
        shots.append(e.image())
    else:
        e.press('A', hold=4, after=46)
        if i % 6 == 0: shots.append(e.image())
    if len(shots) >= 12: flush()
    if i % 500 == 499: e.save(f'{name}_{i // 500}.st')
if shots: flush()
e.save(name + '.st')
print('done', round(time.time() - t), 's', 'sheets', k)
