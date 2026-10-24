import sys; sys.path.insert(0,'tools')
from emu import Emu
import numpy as np
e=Emu(sys.argv[1],'work/emu'); e.run(960); e.tap(128,96,after=120)
hist=[]; prev=None; same=0
for i in range(130):
    e.save(f'r{i%12}.st')
    e.press('A',hold=4,after=50)
    im=np.asarray(e.image())[150:170,130:250].astype(int)   # marquee strip
    if prev is not None and np.abs(im-prev).sum()==0: same+=1
    else: same=0
    prev=im
    if same>=6 and i>95: print('stall at',i,'state r%d'%((i-8)%12)); break
e.image().save('work/emu/stall3_end.png')
