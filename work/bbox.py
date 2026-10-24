import sys; sys.path.insert(0,'tools')
import objedit, objgfx, numpy as np
from scipy import ndimage
of=objedit.ObjFile(open('work/fs/obj_fnt.bin','rb').read(),open('work/fs/obj_dat.bin','rb').read())
for arg in sys.argv[1:]:
    si,fi=map(int,arg.split(':'))
    idx,own,pal=of.canvas(si,fi)
    nfr=len(objgfx.frames(of.dat[si]))
    print(f'== {si}:{fi} canvas {idx.shape[1]}x{idx.shape[0]} frames {nfr}')
    lum=pal[np.clip(idx,0,None)].astype(int).sum(-1)
    for name,mask in (('bright',(lum>600)&(idx>0)),('dark',(lum<150)&(idx>0))):
        lab,n=ndimage.label(ndimage.binary_dilation(mask,iterations=2))
        boxes=ndimage.find_objects(lab)
        bb=[(b[1].start,b[0].start,b[1].stop,b[0].stop) for b in boxes if (b[1].stop-b[1].start)*(b[0].stop-b[0].start)>30]
        print('  ',name,bb[:12])
