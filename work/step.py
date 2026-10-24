"""step.py in.st out.st action...  -> work/emu/z.png strip (frame after each action)"""
import sys; sys.path.insert(0,'tools')
from emu import Emu
from PIL import Image
e=Emu('out/kabushun_zh.nds','work/emu'); e.load(sys.argv[1]); e.run(2); ims=[e.image()]
for a in sys.argv[3:]:
    rep=1
    if '*' in a: a,rep=a.split('*'); rep=int(rep)
    for _ in range(rep):
        if a.startswith('t:'): x,y=map(int,a[2:].split(',')); e.tap(x,y,hold=6,after=40)
        elif a.startswith('dt:'): x,y=map(int,a[3:].split(',')); e.tap(x,y,hold=4,after=6); e.tap(x,y,hold=4,after=40)
        elif a.startswith('w:'): e.run(int(a[2:]))
        else: e.press(a,hold=4,after=46)
    ims.append(e.image())
e.save(sys.argv[2])
S=Image.new('RGB',(256*len(ims),384))
for i,im in enumerate(ims): S.paste(im,(i*256,0))
S.save('work/emu/z.png')
