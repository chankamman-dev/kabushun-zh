"""Load a state, run actions, save state + sheet of the frame after each action.
usage: act.py ROM in.st out actions...
  A/B/X/Y/L/R/START/SELECT/UP/DOWN/LEFT/RIGHT  press (optionally *n repeat, e.g. A*5)
  t:x,y   tap bottom screen     dt:x,y  double tap     w:n  wait n frames
Writes work/emu/<out>.png (one frame per action) and <out>.st."""
import sys; sys.path.insert(0, 'tools')
from emu import Emu
from PIL import Image
rom, src, out, acts = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
e = Emu(rom, 'work/emu')
if src == 'boot': e.run(960); e.tap(128, 96, after=120)
else: e.load(src)
ims = []
for a in acts:
    rep = 1
    if '*' in a: a, rep = a.split('*'); rep = int(rep)
    for _ in range(rep):
        if a.startswith('t:'):
            x, y = map(int, a[2:].split(',')); e.tap(x, y, hold=6, after=40)
        elif a.startswith('dt:'):
            x, y = map(int, a[3:].split(',')); e.tap(x, y, hold=4, after=6); e.tap(x, y, hold=4, after=40)
        elif a.startswith('w:'):
            e.run(int(a[2:]))
        else:
            e.press(a, hold=4, after=46)
    ims.append(e.image())
e.save(out + '.st')
cols = min(6, len(ims)); rows = (len(ims) + cols - 1) // cols
s = Image.new('RGB', (256 * cols, 384 * rows))
for i, im in enumerate(ims): s.paste(im, (i % cols * 256, i // cols * 384))
s.save(f'work/emu/{out}.png')
