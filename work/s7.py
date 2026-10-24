import sys;sys.path.insert(0,'tools')
from emu import Emu
e=Emu('../downloads/nds-20261019/roms/Kabu Trader Shun (Japan).nds','work/emu')
e.load('title_menu.st')
for i in range(70): e.press('A',hold=4,after=50)
e.shot('orig_story.png'); e.save('orig_story.st')
r=e.ram(); open('work/ram_story.bin','wb').write(r)
f=open('extract/font_jp.bin','rb').read()[32:]
for idx in (97,99,137,288):
  g=f[idx*32+4:idx*32+28]
  print(idx,[hex(0x2000000+i) for i in range(len(r)) if r.startswith(g,i)][:4])
