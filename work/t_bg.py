import sys; sys.path.insert(0,'tools')
import ndspy.rom, bgedit, gfxpatch as g, numpy as np
from PIL import Image
name=sys.argv[1]
bf=bgedit.BgFile(open('work/fs/'+name,'rb').read())
for mi,rect,t,kw in g.TRDSET[name]: g.bg_label(bf,mi,rect,t,**kw)
print('new tiles',bf.commit(g.TS_MAPS.get(name)), [len(t)//64 for t in bf.tiles])
open('work/emu/_t.bin','wb').write(bf.build())
