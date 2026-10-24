"""work/sheet.py OUT.png SEC [SEC...] [--orig|--cn ROM]: all frames of sections, unique only, 3x."""
import sys; sys.path.insert(0,'tools')
import objedit, objgfx, numpy as np
from PIL import Image, ImageDraw
args=sys.argv[1:]; out=args.pop(0)
fnt=open('work/fs/obj_fnt.bin','rb').read()
if '--cn' in args:
    i=args.index('--cn'); rom=args[i+1]; del args[i:i+2]
    import ndspy.rom; fnt=ndspy.rom.NintendoDSRom.fromFile(rom).getFileByName('obj_fnt.bin')
of=objedit.ObjFile(fnt,open('work/fs/obj_dat.bin','rb').read())
if '--flags' in args: args.remove('--flags'); objedit.FLAGS=True
if '--patch' in args:
    i=args.index('--patch'); fns=args[i+1].split(','); del args[i:i+2]
    import gfxpatch
    rep=[]
    for fn in fns: getattr(gfxpatch,fn)(of,rep)
    print(rep)
scale=3; W=1200; rows=[]
for s in args:
    si=int(s); seen=set()
    for fi in range(len(objgfx.frames(of.dat[si]))):
        try: idx,own,pal=of.canvas(si,fi)
        except ValueError: continue
        k=idx.tobytes()
        if k in seen: continue
        seen.add(k)
        rgb=np.zeros(idx.shape+(3,),np.uint8); rgb[:]=(60,0,60)
        m=idx>0; rgb[m]=pal[idx[m]%len(pal)]
        rows.append((f'{si}:{fi}',Image.fromarray(rgb).resize((idx.shape[1]*scale,idx.shape[0]*scale),0)))
x=y=rh=0; S=Image.new('RGB',(W,20000)); d=ImageDraw.Draw(S)
for t,im in rows:
    if x+im.width>W: x=0; y+=rh+12; rh=0
    d.text((x,y),t,fill=(255,255,0)); S.paste(im,(x,y+10)); x+=im.width+6; rh=max(rh,im.height)
S.crop((0,0,W,y+rh+12)).save(out)
