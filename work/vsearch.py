import sys;sys.path.insert(0,'tools')
from font import glyph
import numpy as np, json
a=open('work/arm9_dec.bin','rb').read()
o=json.load(open('work/ocr.json',encoding='utf8'))
idx={v[0][1]:int(i) for i,v in o.items() if int(i)>=285}
def search(st,chars,maps=((1,3),),bpp=4):
  res=[]
  for ch in chars:
    g=np.array(glyph(a,idx[ch],0xF3868))
    for va,vb in maps:
      m=np.zeros_like(g); m[g==1]=va; m[g==3]=vb
      for dy in range(8):
        for dx in range(8):
          c=np.zeros((32,32),int); c[dy:dy+16,dx:dx+16]=m
          for ty in range(4):
            for tx in range(4):
              x0,y0=tx*8,ty*8
              if not (x0>=dx and x0+8<=dx+12): continue
              t=c[y0:y0+8,x0:x0+8]
              rows=[r for r in range(8) if t[r].any()]
              if len(rows)<6: continue
              if bpp==4: bb=bytes(int(t[y,x])|int(t[y,x+1])<<4 for y in range(8) for x in range(0,8,2))
              else: bb=bytes(int(t[y,x]) for y in range(8) for x in range(8))
              p=st.find(bb)
              if p>=0: res.append((ch,va,vb,dx,dy,hex(p)))
  return res
