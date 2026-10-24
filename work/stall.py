import sys; sys.path.insert(0,'tools')
from emu import Emu
import numpy as np
rom=sys.argv[1]
e=Emu(rom,'work/emu'); e.run(960); e.tap(128,96,after=120)
same=0; prev=None
for i in range(400):
    if i%5==0: e.save(f'stall_{i//5%4}.st')
    e.press('A',hold=4,after=50)
    im=np.asarray(e.image()).astype(int)
    if prev is not None and np.abs(im-prev).sum()<1000: same+=1
    else: same=0
    prev=im
    if same>=8: print('stall at',i); break
e.image().save('work/emu/stall_now.png')
