"""work/parts.py OUT SEC: distinct parts (tile,size) of a single-image section, 3x."""
import sys; sys.path.insert(0,'tools')
import objedit, objgfx, numpy as np
from PIL import Image, ImageDraw
out,si=sys.argv[1],int(sys.argv[2])
of=objedit.ObjFile(open('work/fs/obj_fnt.bin','rb').read(),open('work/fs/obj_dat.bin','rb').read())
f=of.sec(si); ims=objgfx.images(f); fr=objgfx.frames(of.dat[si])
parts=sorted({(p[0],p[1]) for _,ps in fr for p in ps})
im=ims[0]; bpp8=im['pal_size']>32; tsz=64 if bpp8 else 32
pal=objgfx.palette(f,im); raw=f[im['data']:im['data']+im['size']]
rows=[]
for tile,attr in parts:
    w,h=objgfx.SIZES[(attr>>6,(attr>>4)&3)]
    tb=tile*(2 if bpp8 else 4); a=np.zeros((h,w),int)
    for ty in range(h//8):
        for tx in range(w//8):
            ti=tb+ty*(w//8)+tx; t=raw[ti*tsz:(ti+1)*tsz]
            if len(t)<tsz: continue
            px=np.frombuffer(t,np.uint8) if bpp8 else np.stack([np.frombuffer(t,np.uint8)&15,np.frombuffer(t,np.uint8)>>4],-1).ravel()
            a[ty*8:ty*8+8,tx*8:tx*8+8]=px.reshape(8,8)
    rgb=pal[a%len(pal)]; rgb[a==0]=(60,0,60)
    rows.append((f'{tile}:{w}x{h}',Image.fromarray(rgb.astype(np.uint8)).resize((w*3,h*3),0)))
W=1200; x=y=rh=0; S=Image.new('RGB',(W,20000)); d=ImageDraw.Draw(S)
for t,img in rows:
    if x+img.width>W: x=0; y+=rh+12; rh=0
    d.text((x,y),t,fill=(255,255,0)); S.paste(img,(x,y+10)); x+=img.width+6; rh=max(rh,img.height)
S.crop((0,0,W,y+rh+12)).save(out); print(len(parts))
