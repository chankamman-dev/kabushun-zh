import sys; sys.path.insert(0,'tools')
import numpy as np, ndspy.rom, bgedit, gfxpatch as g
from PIL import Image
rom=ndspy.rom.NintendoDSRom.fromFile(r'G:\ai liabary\downloads\nds-20261019\roms\Kabu Trader Shun (Japan).nds')
bf=bgedit.BgFile(rom.getFileByName('result00.bin'))
o=bf.canvas(5,1,(0,0,32,24))
for mi,rect,t,kw in g.TRDSET['result00.bin']: g.bg_label(bf,mi,rect,t,**kw)
bf.commit(g.TS_MAPS['result00.bin'])
c=bf.canvas(5,1,(0,0,32,24))
for y in range(38,56): print(''.join('%4d'%v for v in c[y,96:128]))
print()
for y in range(38,56): print(''.join('%4d'%v for v in o[y,96:128]))
