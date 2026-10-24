import sys,ctypes as C,struct;sys.path.insert(0,'tools')
from emu import Emu
e=Emu('../downloads/nds-20261019/roms/Kabu Trader Shun (Japan).nds','work/emu')
e.load('orig_top.st'); e.run(1)
p=e.core.retro_get_memory_data(2)
A=open('work/arm9_dec.bin','rb').read()
lit=((0x2009c6a+4)&~3)+0x214
print(hex(lit), hex(struct.unpack_from('<I',A,lit-0x2000000)[0]))
C.memmove(p+lit-0x2000000, struct.pack('<I',0x20F3868+300*64),4)
for i in range(3): e.press('A',hold=4,after=80); e.shot(f'x{i}.png')
from PIL import Image
s=Image.new('RGB',(256*3,384))
for i in range(3): s.paste(Image.open(e.dir/f'x{i}.png'),(i*256,0))
s.save(e.dir/'x_sheet.png')
