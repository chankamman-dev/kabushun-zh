import sys; sys.path.insert(0,'tools')
import objedit, numpy as np
from PIL import Image, ImageDraw
fnt=open(sys.argv[1] if sys.argv[1].endswith('.bin') else 'work/fs/obj_fnt.bin','rb').read(); sys.argv=sys.argv[1:] if sys.argv[1].endswith('.bin') else sys.argv; dat=open('work/fs/obj_dat.bin','rb').read()
of=objedit.ObjFile(fnt,dat)
out=[]
for arg in sys.argv[1:]:
    si,fi=(arg.split(':')+['0'])[:2]; si=int(si); fi=int(fi)
    idx,own,pal=of.canvas(si,fi)
    rgb=np.zeros(idx.shape+(3,),np.uint8); rgb[:]=(40,40,40)
    m=idx>0; rgb[m]=pal[idx[m]%len(pal)]
    im=Image.fromarray(rgb).resize((idx.shape[1]*3,idx.shape[0]*3),0)
    im=im.convert('RGB')
    d=ImageDraw.Draw(im)
    for x in range(0,im.width,24):
        d.line([(x,0),(x,im.height)],fill=(90,90,0)); d.text((x+1,0),str(x//3),fill=(255,255,0))
    for y in range(0,im.height,24):
        d.line([(0,y),(im.width,y)],fill=(90,90,0)); d.text((0,y+1),str(y//3),fill=(0,255,255))
    out.append((arg,im,pal))
W=max(i.width for _,i,_ in out); H=sum(i.height+14 for _,i,_ in out)
S=Image.new('RGB',(max(W,300),H),(0,0,0)); y=0; d=ImageDraw.Draw(S)
for a,i,p in out:
    d.text((0,y),a,fill=(255,255,0)); S.paste(i,(0,y+12)); y+=i.height+14
S.save('work/emu/showsec.png')
