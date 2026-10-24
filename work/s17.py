import sys,ctypes as C;sys.path.insert(0,'tools')
from emu import Emu
import numpy as np
from PIL import Image
e=Emu('../downloads/nds-20261019/roms/Kabu Trader Shun (Japan).nds','work/emu')
e.load('title_menu.st'); e.run(1)
p=e.core.retro_get_memory_data(2)
C.memset(p+0xF3868+285*64,0,(1213-285)*64)
names=[]
for i in range(260):
  e.press('A',hold=4,after=50)
  top=np.array(e.image())[:192]
  box=top[130:185,10:240]; shadow=((box[:,:,0]<90)&(box[:,:,2]>120)&(box[:,:,1]<40)).sum()
  if shadow>150:
    e.run(60); e.shot(f'y{len(names)}.png'); names.append(f'y{len(names)}.png')
    if len(names)>=4: break
s=Image.new('RGB',(256*4,384))
for i,n in enumerate(names): s.paste(Image.open(e.dir/n),(i*256,0))
s.save(e.dir/'y_sheet.png')
