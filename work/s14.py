import sys,ctypes as C;sys.path.insert(0,'tools')
from emu import Emu
e=Emu('../downloads/nds-20261019/roms/Kabu Trader Shun (Japan).nds','work/emu')
e.load('orig_top.st'); e.run(2); e.shot('w0.png')
p=e.core.retro_get_memory_data(2)
C.memset(p+0xF3868+285*64,0,(1213-285)*64)
for i in range(3): e.press('A',hold=4,after=80); e.shot(f'w{i+1}.png')
from PIL import Image
s=Image.new('RGB',(256*4,192))
for i in range(4): s.paste(Image.open(e.dir/f'w{i}.png').crop((0,0,256,192)),(i*256,0))
s.save(e.dir/'w_sheet.png')
