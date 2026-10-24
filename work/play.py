import sys;sys.path.insert(0,'tools')
from emu import Emu
from PIL import Image
rom,out=sys.argv[1],sys.argv[2]; n=int(sys.argv[3]) if len(sys.argv)>3 else 100
e=Emu(rom,'work/emu')
e.run(960); e.tap(128,96,after=120)
shots=[]
for i in range(n):
  e.press('A',hold=4,after=50)
  if i>=n-24 and i%3==2: shots.append(e.image())
e.save(out+'.st')
s=Image.new('RGB',(256*4,384*2))
for i,im in enumerate(shots[-8:]): s.paste(im,(i%4*256,i//4*384))
s.save(f'work/emu/{out}.png')
