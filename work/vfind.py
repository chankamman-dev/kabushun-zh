import sys, os; sys.path.insert(0,'tools'); sys.path.insert(0,'work')
import regs, pack
d=open(sys.argv[1],'rb').read()
v=regs.fields(d)[4]['LCDM']
W=32
idx={}
for o in range(0,len(v)-W,4):
    ch=v[o:o+W]
    if len(set(ch))<4: continue
    idx.setdefault(ch,o)
hits={}
for n in sorted(os.listdir('work/fs')):
    if not n.endswith('.bin'): continue
    dd=open('work/fs/'+n,'rb').read()
    try: secs=pack.unpack(dd)
    except Exception: secs=[(False,dd)]
    for si,(c,s) in enumerate(secs):
        cnt=0; first=None
        for o in range(0,len(s)-W,W):
            vo=idx.get(s[o:o+W])
            if vo is not None:
                cnt+=1
                if first is None: first=(o,vo)
        if cnt>=4: hits[(n,si)]=(cnt,first)
for k,v2 in sorted(hits.items(),key=lambda x:-x[1][0])[:30]: print(k,v2[0],hex(v2[1][0]),hex(v2[1][1]))
