import sys; sys.path.insert(0,'tools')
from emu import Emu
from PIL import Image
e=Emu(sys.argv[1],'work/emu'); e.load(sys.argv[2])
ims=[]
for k in range(10):
    e.press('A',hold=4,after=50); ims.append(e.image())
s=Image.new('RGB',(256*5,384*2))
for i,im in enumerate(ims): s.paste(im,(i%5*256,i//5*384))
s.save('work/emu/stall4.png')
