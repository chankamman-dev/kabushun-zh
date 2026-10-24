import sys,struct;sys.path.insert(0,'tools'); sys.path.insert(0,'work')
from emu import Emu
import engine
e=Emu('work/test1.nds','work/emu'); e.load('u_end.st'); e.run(1)
r=e.ram()
import ndspy.rom
L=engine.Layout(40,41,range(0x200,0x400))
o=lambda a:a-0x2000000
print('rr',struct.unpack_from('<I',r,o(L.rr)))
print('owner',r[o(L.owner):o(L.owner)+16].hex())
print('cmap',r[o(L.cmap):o(L.cmap)+20].hex())
print('regions',[hex(x) for x in struct.unpack_from('<10I',r,o(L.regions))])
print('code ok', r[o(L.code):o(L.code)+16].hex())
