import sys;sys.path.insert(0,'tools')
from emu import Emu
from PIL import Image
rom,st,n,every=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
e=Emu(rom,'work/emu'); e.load(st)
names=[]
for i in range(n):
  e.press('A',hold=4,after=50)
  if i%every==every-1:
    nm=f'u{i:03d}.png'; e.shot(nm); names.append(nm)
e.save('u_end.st')
ims=[Image.open(e.dir/x) for x in names[-16:]]
s=Image.new('RGB',(256*4,384*4))
for i,im in enumerate(ims): s.paste(im,(i%4*256,i//4*384))
s.save(e.dir/'u_sheet.png')
