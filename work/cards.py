import sys; sys.path.insert(0,'tools')
import objedit, numpy as np
from PIL import Image
of=objedit.ObjFile(open('work/fs/obj_fnt.bin','rb').read(),open('work/fs/obj_dat.bin','rb').read())
items=[(int(a.split(':')[0]),int(a.split(':')[1])) for a in sys.argv[2].split(',')]; out=sys.argv[1]; sc=int(sys.argv[3]) if len(sys.argv)>3 else 2
ims=[]
for si,fi in items:
    idx,own,pal=of.canvas(si,fi); rgb=np.zeros(idx.shape+(3,),np.uint8); m=idx>0; rgb[m]=pal[idx[m]]
    ims.append(Image.fromarray(rgb[0:104]).resize((idx.shape[1]*sc,104*sc),0))
w,h=ims[0].size; S=Image.new('RGB',(w*2+6,(h+6)*((len(ims)+1)//2)))
for k,i in enumerate(ims): S.paste(i,((k%2)*(w+6),(k//2)*(h+6)))
S.save(out)
