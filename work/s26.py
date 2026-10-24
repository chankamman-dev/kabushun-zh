import sys,struct;sys.path.insert(0,'tools')
from emu import Emu
import engine
L=engine.Layout(12000,12,list(range(1018)),n_total=284,font2=0)
print('cmap',hex(L.cmap),'owner',hex(L.owner),'pool',hex(L.pool))
e=Emu('out/pilot.nds','work/emu')
e.run(960); e.tap(128,96,after=120)
for i in range(101): e.press('A',hold=4,after=50)
r=e.ram(); o=lambda a:a-0x2000000
cm=struct.unpack_from('<284H',r,o(L.cmap))
print('cmap nonffff',[(g,c) for g,c in enumerate(cm) if c!=0xffff][:40])
code=r[o(engine.CAVE):o(engine.CAVE)+0x600]
import capstone
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
lits=[struct.unpack_from('<I',code,i)[0] for i in range(0,0x600,4)]
print('lits',[hex(x) for x in lits if 0x20f0000<x<0x2110000][:30])
