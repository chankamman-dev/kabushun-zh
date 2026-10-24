import sys; sys.path.insert(0,'tools')
import objedit, numpy as np
of=objedit.ObjFile(open('work/fs/obj_fnt.bin','rb').read(),open('work/fs/obj_dat.bin','rb').read())
for a in sys.argv[1:]:
    si,fi=map(int,a.split(':'))
    idx,own,pal=of.canvas(si,fi)
    print(a,idx.shape)
    for v in sorted(set(idx.ravel().tolist())):
        if v>=0: print('  ',format(v,'x'),tuple(int(c) for c in pal[v]),int((idx==v).sum()))
    for y,r in enumerate(idx): print(f'{y:3d} '+''.join(' ' if v<0 else ('.' if v==0 else format(v,'x')) for v in r))
