import sys;sys.path.insert(0,'tools')
from emu import Emu
from PIL import Image
rom=sys.argv[1]; n=int(sys.argv[2])
e=Emu(rom,'work/emu')
e.run(960); e.tap(128,96,after=120); e.shot('t_title.png')
names=[]
for i in range(n):
  e.press('A',hold=4,after=50)
  if i%2==1:
    nm=f't{i:03d}.png'; e.shot(nm); names.append(nm)
e.save('t_end.st')
ims=[Image.open(e.dir/x) for x in names[-16:]]
s=Image.new('RGB',(256*4,384*4))
for i,im in enumerate(ims): s.paste(im,(i%4*256,i//4*384))
s.save(e.dir/'t_sheet.png')
