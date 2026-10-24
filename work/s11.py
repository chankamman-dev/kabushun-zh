import sys,json;sys.path.insert(0,'tools')
from emu import Emu
from font import glyph
import numpy as np
e=Emu('work/test1.nds','work/emu'); e.load('u_end.st')
r=e.ram(); open('work/ram_test1.bin','wb').write(r)
a=open('work/arm9_dec.bin','rb').read()
o=json.load(open('work/ocr.json',encoding='utf8'))
def idx(ch): return [int(i) for i,v in o.items() if v[0][1]==ch][0]
for ch in ['覚','経','僕']:
  g=np.array(glyph(a,idx(ch),0xF3868)); f=(g==1)
  pats={}
  for y0 in (3,4,5):
    rows=[sum(1<<x for x in range(16) if f[y,x]) for y in range(y0,y0+4)]
    pats[f'lsb16_y{y0}']=b''.join(v.to_bytes(2,'little') for v in rows)
    rowsm=[sum(1<<(15-x) for x in range(16) if f[y,x]) for y in range(y0,y0+4)]
    pats[f'msb16_y{y0}']=b''.join(v.to_bytes(2,'big') for v in rowsm)
    # 4bpp linear with value 1 or f, shadows ignored -> use full g mapping
    for vmap in ({1:1,3:3},{1:15,3:1},{1:1,3:2},{1:2,3:1},{1:15,3:14},{1:1,3:0xf}):
      bb=bytearray()
      for y in range(y0,y0+2):
        for x in range(0,16,2):
          lo=vmap.get(int(g[y,x]),0); hi=vmap.get(int(g[y,x+1]),0); bb.append(lo|hi<<4)
      pats[f'4bpp{vmap}_y{y0}']=bytes(bb)
  for k,p in pats.items():
    i=r.find(p)
    if i>=0: print(ch,k,hex(0x2000000+i))
print('done')
