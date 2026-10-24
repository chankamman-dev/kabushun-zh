import sys; sys.path.insert(0,'tools')
import objedit, numpy as np, gfxpatch as g
from collections import Counter
from PIL import Image
def foot(idx, pal, style, font='song', size=12):
    new=idx.copy(); y0,y1,x0,x1=110,131,66,140
    sub=idx[y0:y1,x0:x1]; c2=[v for v,_ in Counter(sub.ravel().tolist()).most_common(2)]
    bg,st=c2
    others=[v for v in set(sub.ravel().tolist()) if v not in c2 and v>0]
    P=pal.astype(int); L=P.sum(1)
    order=sorted(others,key=lambda v:L[v])         # lightning glow colours
    lite=order[-2] if len(order)>1 else order[-1]  # the letters' outline colour (not the brightest)
    # letter outline pixels: lite colour with no other glow colour around
    glow=set(others)-{lite}
    H,W=idx.shape
    let=np.zeros(idx.shape,bool)
    for y in range(113,130):
        for x in range(x0,x1):
            if idx[y,x]!=lite: continue
            nb=idx[max(0,y-1):y+2,max(0,x-1):x+2].ravel().tolist()
            if not any(v in glow for v in nb): let[y,x]=True
    src=idx.copy()
    for y,x in zip(*np.where(let)):
        for d in range(1,12):
            xs=[xx for xx in (x-d,x+d) if 0<=xx<W and not let[y,xx] and src[y,xx] in (bg,st)]
            if xs: new[y,x]=src[y,xs[0]]; break
    m=objedit.text_mask('交易员卡片',size,font)
    h,w=m.shape; ty=113+(16-h)//2; tx=x0+3+(x1-x0-3-w)//2
    if style=='solid':
        g.stamp(new,m,ty,tx,order[-1],None,bg)
    else:   # hollow: light ring, dark inside
        ring=np.zeros((h+2,w+2),bool)
        for dy in (0,1,2):
            for dx in (0,1,2): ring[dy:dy+h,dx:dx+w]|=m
        mm=np.zeros_like(ring); mm[1:1+h,1:1+w]=m
        for yy,xx in zip(*np.where(ring)):
            Y,X=ty-1+yy,tx-1+xx
            if 0<=Y<H and 0<=X<W and new[Y,X]>=0: new[Y,X]=bg if mm[yy,xx] else lite
    return new
of=objedit.ObjFile(open('work/fs/obj_fnt.bin','rb').read(),open('work/fs/obj_dat.bin','rb').read())
rows=[]
for si,fi in ((614,5),(543,0),(613,0)):
    idx,own,pal=of.canvas(si,fi)
    ims=[pal[np.maximum(idx,0)]]
    for st,fn,sz in (('solid','song',12),('hollow','song',12),('hollow','noto_medium',13)):
        ims.append(pal[np.maximum(foot(idx,pal,st,fn,sz),0)])
    rows.append(np.concatenate([i[100:140,50:144] for i in ims],1))
Image.fromarray(np.concatenate(rows,0).astype(np.uint8)).resize((94*4*4,120*4),0).save('work/emu/z.png')
