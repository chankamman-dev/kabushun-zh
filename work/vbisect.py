import sys, struct; sys.path.insert(0,'tools')
from emu import Emu
import numpy as np
st=sys.argv[1]; box=tuple(map(int,sys.argv[2].split(',')))  # x0,y0,x1,y1 in 256x384 image
d=bytearray(open('work/emu/'+st,'rb').read())
# locate LCDM field data offset
p=32; loc=None
while p+8<=len(d):
    cid,size=struct.unpack_from('<II',d,p); p+=8; q=p
    while q<p+size:
        name=bytes(d[q:q+4]); sz,cnt=struct.unpack_from('<II',d,q+4); q+=12
        if name==b'LCDM': loc=(q,sz*cnt)
        q+=sz*cnt
    p+=size
off,n=loc; print('LCDM',hex(off),hex(n))
e=Emu('out/kabushun_zh.nds','work/emu')
def shot(buf):
    open('work/emu/_vb.st','wb').write(buf); e.load('_vb.st'); e.run(1)
    return np.asarray(e.image())[box[1]:box[3],box[0]:box[2]].astype(int)
base=shot(d)
mask=(base[...,1]>225)&(base[...,2]>225)&(base[...,0]<180)
print('white px',mask.sum())
CH=int(sys.argv[5],16) if len(sys.argv)>5 else 0x4000
rng=range(int(sys.argv[3],16),int(sys.argv[4],16),CH) if len(sys.argv)>4 else range(0,n,CH)
for c in rng:
    b=bytearray(d); b[off+c:off+c+CH]=bytes(CH)
    diff=np.abs(shot(b)-base)[mask].sum()
    if diff: print(hex(c),diff)
