"""work/overview.py OUT SEC... : unique frames, scale 1, labeled, max N per section"""
import sys; sys.path.insert(0,'tools')
import objedit, objgfx, numpy as np
from PIL import Image, ImageDraw
args=sys.argv[1:]; out=args.pop(0); N=40
if args and args[0].startswith("N="): N=int(args.pop(0)[2:])
of=objedit.ObjFile(open('work/fs/obj_fnt.bin','rb').read(),open('work/fs/obj_dat.bin','rb').read())
W=1200; S=Image.new('RGB',(W,8000)); d=ImageDraw.Draw(S); x=y=rh=0
for s in args:
    si=int(s); seen=set(); k=0
    try: fr=objgfx.frames(of.dat[si])
    except Exception: continue
    for fi in range(len(fr)):
        try: idx,own,pal=of.canvas(si,fi)
        except Exception: continue
        key=idx.tobytes()
        if key in seen or idx.size>256*192: continue
        seen.add(key); k+=1
        if k>N: break
        rgb=np.zeros(idx.shape+(3,),np.uint8); rgb[:]=(60,0,60); m=idx>0; rgb[m]=pal[idx[m]%len(pal)]
        im=Image.fromarray(rgb)
        if x+im.width>W: x=0; y+=rh+12; rh=0
        d.text((x,y),f'{si}:{fi}',fill=(255,255,0)); S.paste(im,(x,y+10)); x+=im.width+4; rh=max(rh,im.height)
S.crop((0,0,W,y+rh+14)).save(out)
