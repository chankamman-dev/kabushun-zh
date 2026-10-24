import sys,struct,ctypes as C;sys.path.insert(0,'tools')
from emu import Emu
e=Emu('work/test1.nds','work/emu'); e.load('u_end.st')
p=e.core.retro_get_memory_data(2)
# set t1 table (0x20F2868) all entries -> 99 ('い')
C.memmove(p+0xF2868, struct.pack('<1024H',*([99]*1024)),2048)
for i in range(6):
  e.press('A',hold=4,after=60); e.shot(f'pk{i}.png')
from PIL import Image
s=Image.new('RGB',(256*3,384*2))
for i in range(6): s.paste(Image.open(e.dir/f'pk{i}.png'),(i%3*256,i//3*384))
s.save(e.dir/'pk_sheet.png')
