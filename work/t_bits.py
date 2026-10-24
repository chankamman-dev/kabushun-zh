import sys; sys.path.insert(0,'tools')
import objedit,objgfx
of=objedit.ObjFile(open('work/fs/obj_fnt.bin','rb').read(),open('work/fs/obj_dat.bin','rb').read())
big=[];hi=[]
for si in range(len(of.dat)):
    try: ims=objgfx.images(of.sec(si)); fr=objgfx.frames(of.dat[si])
    except Exception: continue
    if any(i['a']&0x30000 for i in ims): big.append(si)
    if any(p[1]&3 for _,ps in fr for p in ps): hi.append(si)
print('big',big); print('hi',hi)
