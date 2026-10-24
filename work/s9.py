import sys,json;sys.path.insert(0,'tools')
from emu import Emu
e=Emu('work/test1.nds','work/emu')
e.load('u_end.st')
r=e.ram(); open('work/ram_test1.bin','wb').write(r)
a=open('work/arm9_dec.bin','rb').read()
o=json.load(open('work/ocr.json',encoding='utf8'))
for ch in '覚経僕崎':
  idx=[int(i) for i,v in o.items() if v[0][1]==ch][0]
  g=a[0xF3868+idx*64+8:0xF3868+idx*64+56]
  print(ch,idx,[hex(0x2000000+i) for i in range(len(r)) if r.startswith(g,i)][:4])
