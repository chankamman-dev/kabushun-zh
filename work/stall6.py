import sys; sys.path.insert(0,'tools')
from emu import Emu
from PIL import Image
e=Emu(sys.argv[1],'work/emu'); e.run(960); e.tap(128,96,after=120)
for i in range(130): e.press('A',hold=4,after=50)
ims=[]
e.run(4,['A'])
for k in range(24):
    e.run(3); ims.append(e.image().crop((0,120,256,215)))
e.run(200)
for k in range(8):
    e.run(10); ims.append(e.image().crop((0,120,256,215)))
s=Image.new('RGB',(256*4,95*8))
for i,im in enumerate(ims): s.paste(im,(i%4*256,i//4*95))
s.save('work/emu/stall6.png')
