import sys; sys.path.insert(0,'tools')
from collections import Counter
import numpy as np, ndspy.rom, bgedit, gfxpatch as g
rom=ndspy.rom.NintendoDSRom.fromFile(r'G:\ai liabary\downloads\nds-20261019\roms\Kabu Trader Shun (Japan).nds')
bf=bgedit.BgFile(rom.getFileByName('result00.bin'))
for mi,rect,t,kw in g.TRDSET['result00.bin']:
    ts=kw.get('ts',0)
    c=bf.canvas(mi,ts,(0,0,32,24)); x0,y0,x1,y1=rect
    sub=c[y0:y1,x0:x1]; cnt=Counter(sub.ravel().tolist())
    ink,sh=g.detect_text(c,bf.pal[ts],rect,kw.get('ink_bright'))
    print(mi,t,ink,sh,cnt.most_common(6), [tuple(bf.pal[p][v]) for p in (0,1) for v in (ink,)])
from PIL import Image
c=bf.canvas(5,1,(0,0,32,24))
im=Image.fromarray(bf.pal[1][c].astype('uint8')).crop((0,30,140,110)).resize((560,320),0); im.save('work/emu/z.png')
