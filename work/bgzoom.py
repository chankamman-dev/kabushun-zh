"""work/bgzoom.py OUT FILE MAP x0 y0 x1 y1 [scale] [--rom ROM]: zoom with 8px grid + coords"""
import sys; sys.path.insert(0,'tools')
import numpy as np, bgedit
from PIL import Image, ImageDraw
a=sys.argv[1:]; rom=None
if '--rom' in a: i=a.index('--rom'); rom=a[i+1]; del a[i:i+2]
out,name,mi=a[0],a[1],int(a[2]); x0,y0,x1,y1=map(int,a[3:7]); sc=int(a[7]) if len(a)>7 else 4
if rom:
    import ndspy.rom; data=ndspy.rom.NintendoDSRom.fromFile(rom).getFileByName(name)
else: data=open('work/fs/'+name,'rb').read()
bf=bgedit.BgFile(data); m=bf.maps[mi]; mx=int((m&0x3FF).max())
ts=next((t for t in range(len(bf.tiles)) if len(bf.tiles[t])//64>mx),0)
c=bf.canvas(mi,ts,(0,0,32,24)); rgb=bf.pal[min(ts,len(bf.pal)-1)][c].astype(np.uint8)[y0:y1,x0:x1]
im=Image.fromarray(rgb).resize(((x1-x0)*sc,(y1-y0)*sc),0); d=ImageDraw.Draw(im)
for x in range(x0,x1):
    if x%8==0: d.line([((x-x0)*sc,0),((x-x0)*sc,im.height)],fill=(255,0,0)); d.text(((x-x0)*sc+1,1),str(x),fill=(255,0,0))
for y in range(y0,y1):
    if y%8==0: d.line([(0,(y-y0)*sc),(im.width,(y-y0)*sc)],fill=(0,0,255)); d.text((1,(y-y0)*sc+1),str(y),fill=(0,0,255))
im.save(out)
