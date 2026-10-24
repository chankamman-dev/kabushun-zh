"""load state, overwrite RAM ranges with the freshly built ARM9 image, save as new state"""
import sys, struct, ctypes as C; sys.path.insert(0,'tools')
from emu import Emu
import ndspy.rom, ndspy.codeCompression as cc
rom, src, dst = sys.argv[1:4]; ranges=[tuple(int(x,16) for x in r.split('-')) for r in sys.argv[4:]]
r=ndspy.rom.NintendoDSRom.fromFile(rom); raw=r.arm9
end=struct.unpack_from('<I',raw,0xB68+0x14)[0]-0x2000000
a=bytes(cc.decompress(raw[:end]))
e=Emu(rom,'work/emu'); e.load(src)
ptr=e.core.retro_get_memory_data(2)
for lo,hi in ranges:
    d=a[lo-0x2000000:hi-0x2000000]; C.memmove(ptr+lo-0x2000000, C.c_char_p(d), len(d))
e.save(dst); print('ok')
