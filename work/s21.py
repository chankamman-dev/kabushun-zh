import sys,struct;sys.path.insert(0,'tools')
from emu import Emu
import ndspy.rom
rom=ndspy.rom.NintendoDSRom.fromFile('out/pilot.nds')
k=rom.getFileByName('KSSCV.bin')
e=Emu('out/pilot.nds','work/emu'); e.load('pilot.st'); e.run(1)
r=e.ram()
o=0x2B4000
print('len',len(k))
same=[i for i in range(0,len(k),0x1000) if r[o+i:o+i+0x1000]!=k[i:i+0x1000]]
print('diff blocks',[hex(x) for x in same[:20]], len(same))
print('hdr', [hex(x) for x in struct.unpack_from('<10I',r,o)])
d=[i for i in range(len(k)) if r[o+i]!=k[i]]
print('first diff',hex(d[0]),'last',hex(d[-1]),'count',len(d))
print('ram',r[o+d[0]-16:o+d[0]+32].hex())
print('file',k[d[0]-16:d[0]+32].hex())
