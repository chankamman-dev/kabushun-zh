import sys; sys.path.insert(0,'tools')
import numpy as np, ndspy.rom, bgedit, gfxpatch as g
from PIL import Image
rom=ndspy.rom.NintendoDSRom.fromFile(r'G:\ai liabary\downloads\nds-20261019\roms\Kabu Trader Shun (Japan).nds')
bf=bgedit.BgFile(rom.getFileByName('result00.bin'))
for mi,rect,t,kw in g.TRDSET['result00.bin']: g.bg_label(bf,mi,rect,t,**kw)
bf.commit(g.TS_MAPS['result00.bin'])
ims=[]
for mi in (0,5,3):
    ts={3:0}.get(mi,1)
    for p in (0,1):
        ims.append(bf.pal[p][bf.canvas(mi,ts,(0,0,32,24))].astype('uint8'))
a=np.concatenate([np.concatenate(ims[i:i+2],1) for i in (0,2,4)],0)
Image.fromarray(a).save('work/emu/z.png')
