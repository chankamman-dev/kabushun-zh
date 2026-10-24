import sys,struct;sys.path.insert(0,'tools')
from emu import Emu
import engine
e=Emu('out/pilot.nds','work/emu'); e.load('pilot.st'); e.run(1)
r=e.ram(); o=lambda a:a-0x2000000
cave=engine.CAVE
code=r[o(cave):o(cave)+0x600]
# find literal pool by searching p_regions value pattern: regions addr = cave+0x600+16+64
L_regions=cave+0x600+16+64
print('regions',[hex(x) for x in struct.unpack_from('<20I',r,o(L_regions))])
rr=L_regions+(engine.MAX_REGIONS+1)*20
print('rr',struct.unpack_from('<I',r,o(rr)))
print('bits',r[o(0x22ea708):o(0x22ea708)+32].hex())
print('pool',r[o(0x22d5244):o(0x22d5244)+40].hex())
for w in range(4):
  base=0x21a0d68+w*0x304
  g=struct.unpack_from('<96H',r,o(base+0x28))
  print('win',w,' '.join(f'{x:04x}' for x in g[:40]))
