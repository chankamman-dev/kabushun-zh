import sys, ctypes as C; sys.path.insert(0,'tools')
from emu import Emu
import numpy as np
st=sys.argv[1]; box=tuple(map(int,sys.argv[2].split(',')))
lo,hi,CH=int(sys.argv[3],16),int(sys.argv[4],16),int(sys.argv[5],16)
e=Emu('out/kabushun_zh.nds','work/emu')
ptr=e.core.retro_get_memory_data(2)
def shot(z=None):
    e.load(st)
    if z: C.memset(ptr+z[0],0,z[1])
    e.run(2)
    return np.asarray(e.image())[box[1]:box[3],box[0]:box[2]].astype(int)
base=shot()
mask=(base[...,1]>225)&(base[...,2]>225)&(base[...,0]<180)
print('px',mask.sum())
for c in range(lo,hi,CH):
    try: diff=np.abs(shot((c,CH))-base)[mask].sum()
    except Exception as ex: diff=-1
    if diff: print(hex(0x2000000+c),diff)
