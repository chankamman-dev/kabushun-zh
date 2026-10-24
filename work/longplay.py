"""Boot, start new game, mash A; save a contact sheet every `per` shots and a savestate at the end.
usage: longplay.py ROM name presses [every] [load.st]"""
import sys, time; sys.path.insert(0, 'tools')
from emu import Emu
from PIL import Image
rom, name, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
every = int(sys.argv[4]) if len(sys.argv) > 4 else 10
e = Emu(rom, 'work/emu')
if len(sys.argv) > 5:
    e.load(sys.argv[5])
else:
    e.run(960); e.tap(128, 96, after=120)
shots = []; t = time.time()
def flush(k):
    s = Image.new('RGB', (256 * 6, 384 * 2))
    for i, im in enumerate(shots): s.paste(im, (i % 6 * 256, i // 6 * 384))
    s.save(f'work/emu/{name}_{k:02d}.png')
k = 0
for i in range(n):
    e.press('A', hold=4, after=50)
    if i % every == every - 1:
        shots.append(e.image())
        if len(shots) == 12: flush(k); k += 1; shots = []
if shots: flush(k)
e.save(name + '.st')
print('done', round(time.time() - t), 's')
