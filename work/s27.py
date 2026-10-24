import sys,struct;sys.path.insert(0,'tools')
from emu import Emu
import engine
L=engine.Layout(12000,12,list(range(1018)),n_total=284,font2=0)
e=Emu('out/pilot.nds','work/emu')
o=lambda a:a-0x2000000
def chk(tag):
  r=e.ram(); cm=struct.unpack_from('<284H',r,o(L.cmap))
  z=[g for g,c in enumerate(cm) if c!=0xffff]
  print(tag,len(z),z[:5],flush=True)
e.run(960); chk('boot'); e.tap(128,96,after=120); chk('title')
for i in range(101):
  e.press('A',hold=4,after=50)
  if i%5==0: chk(f'p{i}')
