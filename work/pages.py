"""work/pages.py ROM OUTDIR N: boot, start a new game, capture each dialogue page once fully shown
(yellow continue arrow on the bottom screen), then advance.  -> OUTDIR/page_NN.png"""
import sys, os; sys.path.insert(0, 'tools')
from emu import Emu
import numpy as np
rom, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
os.makedirs(out, exist_ok=True)
e = Emu(rom, 'work/emu')
e.run(960); e.tap(128, 96, after=60)
def arrow():
    a = np.asarray(e.image()).astype(int)[192:]
    return ((a[..., 0] > 200) & (a[..., 1] > 140) & (a[..., 2] < 90)).sum() >= 4
k = 0; idle = 0
while k < n:
    for f in range(900):
        e.run(1)
        if arrow(): break
    else:
        e.press('A', hold=4, after=30); continue
    e.run(8)                                   # let the arrow settle
    e.image().save(f'{out}/page_{k:02d}.png'); k += 1
    e.press('A', hold=4, after=6)
print('pages', k)
