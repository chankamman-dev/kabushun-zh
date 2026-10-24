import sys,struct;sys.path.insert(0,'tools')
from emu import Emu
import engine
e=Emu(sys.argv[1],'work/emu')
e.run(960); e.tap(128,96,after=120)
o=lambda a:a-0x2000000
L_regions=engine.CAVE+0x600+16+64; rr=L_regions+(engine.MAX_REGIONS+1)*20
for i in range(120):
  e.press('A',hold=4,after=50)
  r=e.ram()
  for w in range(4):
    base=0x21a0d68+w*0x304
    g=struct.unpack_from('<64H',r,o(base+0x28))
    if any(g):
      print(i,'win',w,' '.join(f'{x:04x}' for x in g[:24]),'rr',struct.unpack_from('<I',r,o(rr))[0])
  if i>75: 
    e.shot(f'dbg{i}.png')
