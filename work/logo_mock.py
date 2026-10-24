import sys; sys.path.insert(0,'tools')
import bgedit, numpy as np, gfxpatch as g
from PIL import Image
def base():
    bf=bgedit.BgFile(open('work/fs/title2.bin','rb').read())
    return bf, bf.canvas(0,0,(0,0,32,24)).copy(), bf.pal[0]
WHITE=((255,255,255),(235,245,255),(255,255,255),(10,30,70),0,1)
def ch(t,size=40): return g._rgba_text(t,size,'yahei_b',*WHITE)
def kata(c,P,x0=66,x1=145,w=None):
    src=c.copy()
    for y in range(64,110):
        for x in range(x0,x1): c[y,x]=src[y,8+((x-8)%8)]
    rgb,a=g._rgba_text('交易员',32,'yahei_b',(110,230,250),(20,120,170),(255,255,255),(10,30,70),2,1,italic=0.15)
    if w: g._blend_into(c,P,rgb,a,x0,70,w=w,h=36)
    else: g._blend_into(c,P,rgb,a,x0,70,h=36)
def fillbox(c,x0=20,x1=63):
    for y in range(65,106): c[y,x0:x1]=c[y,21]
def A():
    bf,c,P=base(); fillbox(c)
    r,a=ch('股'); g._blend_into(c,P,r,a,23,66,w=36,h=19)
    r,a=ch('票'); g._blend_into(c,P,r,a,23,86,w=36,h=19)
    kata(c,P); return P[c]
def B():
    bf,c,P=base(); fillbox(c)
    r,a=ch('股'); g._blend_into(c,P,r,a,22,66,w=19,h=38)
    r,a=ch('票'); g._blend_into(c,P,r,a,41,66,w=19,h=38)
    kata(c,P); return P[c]
def C():
    bf,c,P=base()
    src=c.copy(); dx=30
    # move the right border (x 59..66) right by dx, widen the box
    c[60:110,61+dx:67+dx]=src[60:110,61:67]
    for x in range(61,61+dx): c[60:110,x]=src[60:110,40]
    c[60:110,66+dx:72+dx]=src[60:110,66:72] if False else c[60:110,66+dx:72+dx]
    fillbox(c,20,61+dx)
    r,a=ch('股'); g._blend_into(c,P,r,a,23,67,w=34,h=36)
    r,a=ch('票'); g._blend_into(c,P,r,a,57,67,w=34,h=36)
    kata(c,P,97,146,w=48); return P[c]
ims=[base()[2][base()[1]]]
try: ims.append(np.asarray(Image.open('work/promo/pair_title_cn.png')))
except Exception: pass
for f in (A,B,C): ims.append(f())
a=np.concatenate([np.concatenate(ims[:3],1),np.concatenate(ims[3:]+[np.zeros_like(ims[0])]*(3-len(ims[3:])),1)],0)
Image.fromarray(a.astype(np.uint8)).resize((a.shape[1]*2,a.shape[0]*2),0).save('work/emu/z.png')
