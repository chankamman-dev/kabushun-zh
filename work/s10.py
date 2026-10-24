import sys;sys.path.insert(0,'tools')
from emu import Emu
import ndspy.rom
e=Emu('work/test1.nds','work/emu'); e.load('u_end.st')
r=e.ram()
rom=ndspy.rom.NintendoDSRom.fromFile('work/test1.nds')
a=rom.arm9
print('rom arm9 len',len(a), 'site',a[0x9d1e:0x9d24].hex(), 'ram site', r[0x9d1e:0x9d24].hex())
print('cave rom',a[0xf7aa8:0xf7ab8].hex(),'ram',r[0xf7aa8:0xf7ab8].hex())
diff=sum(1 for i in range(0,len(a),4) if a[i:i+4]!=r[i:i+4]); print('diff words',diff)
o=0xF3868+396*64
print('ram glyph396', r[o:o+16].hex(), 'rom', a[o:o+16].hex())
cave=0xF7FA8
print('ram cave', r[cave:cave+16].hex(), 'rom', a[cave:cave+16].hex())
import struct
print('regions in ram'); 
