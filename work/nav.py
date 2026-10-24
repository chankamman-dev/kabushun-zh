"""Navigate the trade center: nav.py ROM in.st out place_x,place_y [steps]
Dialogue -> A; talk list (yellow back button) -> back; room menu (cyan Map button) -> Map;
map (purple top screen) -> tap destination, then stop after the scene starts."""
import sys; sys.path.insert(0, 'tools')
from emu import Emu
from PIL import Image
import numpy as np
rom, src, out, dest = sys.argv[1], sys.argv[2], sys.argv[3], tuple(map(int, sys.argv[4].split(',')))
steps = int(sys.argv[5]) if len(sys.argv) > 5 else 60
e = Emu(rom, 'work/emu'); e.load(src); e.run(10)
ims = []
def state(im):
    a = np.asarray(im).astype(int)
    bl = a[192 + 176:192 + 188, 4:30].reshape(-1, 3).mean(0)     # bottom-left button
    top = a[20:100, :].reshape(-1, 3).mean(0)
    if bl[0] > 150 and bl[1] > 110 and bl[2] < 90: return 'list'
    if bl[2] > 150 and bl[1] > 120 and bl[0] < 120: return 'menu'
    if top[2] > 150 and top[0] < 140 and top[1] < 140: return 'map'
    return 'other'
went = False
for i in range(steps):
    im = e.image(); s = state(im)
    if s == 'map' and not went:
        e.tap(*dest, hold=6, after=120); went = True
    elif s in ('list', 'menu') and not went:
        e.tap(16, 182, hold=6, after=90)
    else:
        e.press('A', hold=4, after=46)
    ims.append(e.image())
    if went and i > 0 and s == 'other' and len(ims) > 3: pass
e.save(out + '.st')
sel = ims[::max(1, len(ims) // 12)][:12]
S = Image.new('RGB', (256 * 6, 384 * 2))
for k, im in enumerate(sel): S.paste(im, (k % 6 * 256, k // 6 * 384))
S.save(f'work/emu/{out}.png')
print('went', went)
