import sys; sys.path.insert(0,'tools')
import gfxpatch as g, bgedit, numpy as np
from PIL import Image
bf=bgedit.BgFile(open('work/fs/title2.bin','rb').read())
g.logo_patch(bf,0); print(bf.commit())
c=bf.canvas(0,0,(0,0,32,24)); Image.fromarray(bf.pal[0][np.clip(c,0,255)]).resize((768,576),0).save('work/emu/dbg.png')
