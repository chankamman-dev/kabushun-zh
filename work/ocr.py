import sys,json
sys.path.insert(0,'tools')
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from font import glyph
a=open('work/arm9_dec.bin','rb').read()
OFF=0xF3868
N=1213
def fg(i):
  g=np.array(glyph(a,i,OFF)); return (g==1)
cands=[]
for b1 in list(range(0x81,0xa0))+list(range(0xe0,0xf0)):
  for b2 in range(0x40,0xfd):
    try: c=bytes([b1,b2]).decode('cp932')
    except: continue
    if len(c)==1: cands.append(c)
cands=sorted(set(cands))
fonts={'msg':ImageFont.truetype('C:/Windows/Fonts/msgothic.ttc',12)}
def render(c,f):
  im=Image.new('1',(16,16),0); d=ImageDraw.Draw(im); d.text((0,0),c,font=f,fill=1)
  return np.array(im,dtype=bool)
R={c:render(c,fonts['msg']) for c in cands}

C=list(R.keys()); RA=np.stack([R[c] for c in C]).reshape(len(C),-1).astype(np.float32)
shifted=[]
for dy in range(-2,3):
  for dx in range(-2,3):
    shifted.append(np.stack([np.roll(np.roll(R[c],dy,0),dx,1) for c in C]).reshape(len(C),-1).astype(np.float32))
cnt=[s.sum(1) for s in shifted]
def best(m):
  mv=m.reshape(-1).astype(np.float32); ms=mv.sum(); sc=np.zeros(len(C),np.float32)
  for s,cn in zip(shifted,cnt):
    inter=s@mv; v=inter/(cn+ms-inter+1e-6); sc=np.maximum(sc,v)
  idx=np.argsort(-sc)[:3]; return [(float(sc[i]),C[i]) for i in idx]
out={}
for i in range(N):
  m=fg(i)
  if not m.any(): out[i]=[[1.0,' ']]; continue
  out[i]=[[round(s,3),c] for s,c in best(m)]
json.dump(out,open('work/ocr.json','w',encoding='utf8'),ensure_ascii=False)
