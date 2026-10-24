"""work/fr.py OUT SI:FI[,FI..] ... [--patch fn,fn] [--scale N]: orig (top) vs patched (bottom) of chosen frames"""
import sys; sys.path.insert(0,'tools')
import objedit, numpy as np
from PIL import Image, ImageDraw
args=sys.argv[1:]; out=args.pop(0); fns=[]; sc=4
if '--patch' in args: i=args.index('--patch'); fns=args[i+1].split(','); del args[i:i+2]
if '--scale' in args: i=args.index('--scale'); sc=int(args[i+1]); del args[i:i+2]
ld=lambda: objedit.ObjFile(open('work/fs/obj_fnt.bin','rb').read(),open('work/fs/obj_dat.bin','rb').read())
a=ld(); b=ld()
import gfxpatch
for fn in fns: getattr(gfxpatch,fn)(b,[])
sel=[]
for s in args:
    si,fs=s.split(':'); sel+=[(int(si),int(f)) for f in fs.split(',')]
def img(of,si,fi):
    idx,own,pal=of.canvas(si,fi); rgb=np.zeros(idx.shape+(3,),np.uint8); rgb[:]=(60,0,60); m=idx>0; rgb[m]=pal[idx[m]%len(pal)]
    return Image.fromarray(rgb).resize((idx.shape[1]*sc,idx.shape[0]*sc),0)
cols=[(img(a,si,fi),img(b,si,fi),f'{si}:{fi}') for si,fi in sel]
W=1200; x=y=rh=0; S=Image.new('RGB',(W,6000)); d=ImageDraw.Draw(S)
for p,q,t in cols:
    if x+p.width>W: x=0; y+=rh+14; rh=0
    d.text((x,y),t,fill=(255,255,0)); S.paste(p,(x,y+12)); S.paste(q,(x,y+14+p.height)); x+=p.width+6; rh=max(rh,2*p.height+4)
S.crop((0,0,W,y+rh+16)).save(out)
