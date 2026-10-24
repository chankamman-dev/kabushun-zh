import sys,struct;sys.path.insert(0,'tools')
from emu import Emu
import engine
sys.argv=['x']
exec(open('tools/build.py',encoding='utf8').read().split("def main")[0])
# recompute layout like build
e=Emu('out/pilot.nds','work/emu')
e.run(960); e.tap(128,96,after=120)
for i in range(101): e.press('A',hold=4,after=50)
r=e.ram(); o=lambda a:a-0x2000000
import re
code=r[o(engine.CAVE):o(engine.CAVE)+0x600]
open('work/cave_code.bin','wb').write(code)
reg=engine.CAVE+0x600+16+64; rr=reg+(engine.MAX_REGIONS+1)*20; pool=rr+4
print('rr',struct.unpack_from('<I',r,o(rr))[0])
print('pool',struct.unpack_from('<8H',r,o(pool)))
