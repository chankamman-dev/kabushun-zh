import sys,struct,ctypes as C;sys.path.insert(0,'tools')
from emu import Emu
import numpy as np
A=open('work/arm9_dec.bin','rb').read()
sites=[0x2006bba,0x20073dc,0x200741e,0x2007544,0x2007ca8,0x2007cf2,0x2008d74,0x2009cd8,0x200a38a,0x200aee6,0x200b0ae,0x200bb08,0x200be54,0x200c09e,0x200c244,0x200c4a4,0x200c65a,0x200c85a,0x200cb06,0x200cd52,0x200cf9e,0x200d1e2,0x200e230,0x200e550,0x200e962,0x203c73a,0x2048a28,0x20ee5d8]
e=Emu('../downloads/nds-20261019/roms/Kabu Trader Shun (Japan).nds','work/emu')
# need a top-box state on original rom: reuse orig_story2 then advance
e.load('orig_story2.st')
import numpy as np
for i in range(40):
  e.press('A',hold=4,after=50)
  top=np.array(e.image())[:192]
  box=top[130:185,10:240]
  if ((box>200).all(2)).sum()>200: break
e.press('A',hold=4,after=60)
e.save('orig_top.st'); e.shot('orig_top.png')
def run(poke=None):
  e.load('orig_top.st')
  p=e.core.retro_get_memory_data(2)
  if poke: C.memmove(p+poke-0x2000000, struct.pack('<I',1),4)
  e.press('A',hold=4,after=80)
  return np.array(e.image())[:192]
base=run()
print('base ok', (base!=0).any())
for s in sites:
  o=s-0x2000000; h=struct.unpack_from('<H',A,o)[0]; la=((s+4)&~3)+(h&0xff)*4
  try: img=run(la)
  except Exception as ex: print(hex(s),'ERR',ex); continue
  d=(img!=base).any(2).sum()
  print(hex(s),hex(la),d,flush=True)
