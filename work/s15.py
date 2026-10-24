import sys,ctypes as C;sys.path.insert(0,'tools')
from emu import Emu
import numpy as np
e=Emu('../downloads/nds-20261019/roms/Kabu Trader Shun (Japan).nds','work/emu')
def run(lo,hi):
  e.load('orig_top.st'); e.run(1)
  p=e.core.retro_get_memory_data(2)
  if hi>lo: C.memset(p+lo,0,hi-lo)
  for i in range(3): e.press('A',hold=4,after=80)
  return np.array(e.image())[130:185]
base=run(0,0)
lo,hi=0x1C0A00,0x3E0000
ranges=[(0x1C0A00,0x22B4000-0x2000000),(0x2B4000,0x331B6C),(0x331B6C,0x35B000),(0x35B000,0x3E0000),(0x100000,0x1C0A00),(0x0F3868,0x100000)]
for a,b in ranges:
  try:
    img=run(a,b); d=(img!=base).any(2).sum()
  except Exception as ex: d='ERR'
  print(hex(a+0x2000000),hex(b+0x2000000),d,flush=True)
  e.shot(f'bs_{a:x}.png')
