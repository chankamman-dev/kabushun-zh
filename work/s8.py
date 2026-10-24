import sys;sys.path.insert(0,'tools')
from emu import Emu
e=Emu('../downloads/nds-20261019/roms/Kabu Trader Shun (Japan).nds','work/emu')
e.load('orig_story.st')
for i in range(60):
  e.press('A',hold=4,after=50)
  im=e.image().crop((0,140,256,190))
  import numpy as np
  a=np.array(im); 
  if (a.sum(2)>600).sum()>150 and i>2: break
e.shot('orig_story2.png'); e.save('orig_story2.st'); print('i',i)
r=e.ram(); open('work/ram_story.bin','wb').write(r)
