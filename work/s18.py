import sys,ctypes as C;sys.path.insert(0,'tools')
from emu import Emu
import numpy as np
from PIL import Image
e=Emu('../downloads/nds-20261019/roms/Kabu Trader Shun (Japan).nds','work/emu')
e.load('orig_story2.st'); e.run(1)
p=e.core.retro_get_memory_data(2)
C.memset(p+0xF3868+285*64,0,(1213-285)*64)
for i in range(40):
  e.press('A',hold=4,after=50)
  top=np.array(e.image())[:192]
  box=top[130:185,10:240]
  if ((box>200).all(2)).sum()>200: break
names=[]
for k in range(4):
  e.press('A',hold=4,after=80); n=f'z{k}.png'; e.shot(n); names.append(n)
s=Image.new('RGB',(256*4,384))
for i,n in enumerate(names): s.paste(Image.open(e.dir/n),(i*256,0))
s.save(e.dir/'z_sheet.png')
