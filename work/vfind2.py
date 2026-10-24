import sys, os; sys.path.insert(0,'tools'); sys.path.insert(0,'work')
import regs, pack, ndspy.lz10 as lz10
d=open(sys.argv[1],'rb').read()
v=regs.fields(d)[4]['LCDM']
lo,hi=int(sys.argv[2],16),int(sys.argv[3],16)
W=16
idx={}
for o in range(lo,hi-W,2):
    ch=v[o:o+W]
    if len(set(ch))<3: continue
    idx.setdefault(ch,o)
def blobs(n,dd):
    try: secs=pack.unpack(dd)
    except Exception: secs=[(False,dd)]
    for si,(c,s) in enumerate(secs):
        yield si,s
        # nested LZ in image entries
        for o in range(0,min(len(s),64),4):
            pass
hits=[]
for n in sorted(os.listdir('work/fs')):
    dd=open('work/fs/'+n,'rb').read()
    for si,s in blobs(n,dd):
        cnt=0; first=None
        for o in range(0,len(s)-W,W):
            vo=idx.get(s[o:o+W])
            if vo is not None:
                cnt+=1
                if first is None: first=(o,vo)
        if cnt>=3: hits.append((cnt,n,si,first))
for h in sorted(hits,reverse=True)[:15]: print(h[0],h[1],h[2],hex(h[3][0]),hex(h[3][1]))
