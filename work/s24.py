import sys,struct;sys.path.insert(0,'tools')
from emu import Emu
import engine, ndspy.rom
rom=ndspy.rom.NintendoDSRom.fromFile('out/pilot.nds'); a=rom.arm9
e=Emu('out/pilot.nds','work/emu')
e.run(960)
r=e.ram()
c0=engine.CAVE-0x2000000; c1=engine.CAVE_END-0x2000000
diff=[i for i in range(c0,c1,16) if r[i:i+16]!=a[i:i+16]]
print('cave diffs at boot',len(diff), [hex(0x2000000+x) for x in diff[:10]])
