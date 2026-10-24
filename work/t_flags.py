import sys; sys.path.insert(0,'tools')
import objedit,objgfx, ndspy.rom
from collections import Counter
o=open('work/fs/obj_fnt.bin','rb').read()
n=ndspy.rom.NintendoDSRom.fromFile('out/kabushun_zh.nds').getFileByName('obj_fnt.bin')
of=objedit.ObjFile(o,open('work/fs/obj_dat.bin','rb').read())
for si in range(len(of.dat)):
    a,b=of.secs[si][0],of.secs[si][1] if len(of.secs[si])>1 else None
    s,e=of.secs[si][0], of.secs[si][0]+len(of.sec(si))
    if o[s:e]==n[s:e]: continue
    try: fr=objgfx.frames(of.dat[si])
    except Exception: print(si,'?'); continue
    c=Counter(p[1]&15 for img,ps in fr for p in ps)
    print(si, dict(c))
