import sys; sys.path.insert(0,'tools')
from emu import Emu
from PIL import Image
e=Emu(sys.argv[1],'work/emu'); e.run(960); e.tap(128,96,after=120)
for i in range(300): e.press('A',hold=4,after=50)
ims=[e.image()]
e.run(600); ims.append(e.image())
e.save('s2.st'); e.load('s2.st'); e.run(120); ims.append(e.image())
s=Image.new('RGB',(256*3,384))
for i,im in enumerate(ims): s.paste(im,(i*256,0))
s.save('work/emu/stall2.png')
