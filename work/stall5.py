import sys; sys.path.insert(0,'tools')
from emu import Emu
from PIL import Image
e=Emu(sys.argv[1],'work/emu'); e.run(960); e.tap(128,96,after=120)
ims=[]
for i in range(118):
    if i>=96: e.save(f'p{i}.st')
    e.press('A',hold=4,after=50)
    if i>=96: ims.append(e.image().crop((0,120,256,215)))
s=Image.new('RGB',(256*4,95*6))
for i,im in enumerate(ims): s.paste(im,(i%4*256,i//4*95))
s.save('work/emu/stall5.png')
