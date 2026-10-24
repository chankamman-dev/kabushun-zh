"""work/bgr.py OUT FILE [--rom ROM] [--patch fn]: render every map of a BG file (tileset by max tile index)"""
import sys; sys.path.insert(0,'tools')
import numpy as np, bgedit
from PIL import Image, ImageDraw
args=sys.argv[1:]; out=args.pop(0); name=args.pop(0); rom=None
if '--rom' in args: i=args.index('--rom'); rom=args[i+1]; del args[i:i+2]
if rom:
    import ndspy.rom; data=ndspy.rom.NintendoDSRom.fromFile(rom).getFileByName(name)
else: data=open('work/fs/'+name,'rb').read()
bf=bgedit.BgFile(data)
print('tilesets',[len(t)//64 for t in bf.tiles],'pals',len(bf.pal),'maps',len(bf.maps),[m.shape for m in bf.maps])
ims=[]
for mi,m in enumerate(bf.maps):
    mx=int((m&0x3FF).max())
    ts=next((t for t in range(len(bf.tiles)) if len(bf.tiles[t])//64>mx), 0)
    c=bf.canvas(mi,ts,(0,0,m.shape[1],m.shape[0]))
    rgb=bf.pal[min(ts,len(bf.pal)-1)][c].astype(np.uint8)
    im=Image.fromarray(rgb); ImageDraw.Draw(im).text((2,2),f'{mi}/ts{ts}',fill=(255,255,0)); ims.append(im)
W=4; w,h=ims[0].size
S=Image.new('RGB',(w*min(W,len(ims)),h*((len(ims)+W-1)//W)))
for i,im in enumerate(ims): S.paste(im,((i%W)*w,(i//W)*h))
S.save(out)
