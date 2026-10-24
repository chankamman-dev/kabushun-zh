import sys;sys.path.insert(0,'tools')
from emu import Emu
from PIL import Image
e=Emu('../downloads/nds-20261019/roms/Kabu Trader Shun (Japan).nds','work/emu')
def sheet(names,out):
  ims=[Image.open(e.dir/n) for n in names]
  s=Image.new('RGB',(256*min(4,len(ims)),384*((len(ims)+3)//4)))
  for i,im in enumerate(ims): s.paste(im,(i%4*256,i//4*384))
  s.save(e.dir/out)
