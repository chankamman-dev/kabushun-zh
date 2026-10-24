import sys; sys.path.insert(0,'tools')
import gfxpatch as g
class R:
    def __init__(s): s.f={}
    def getFileByName(s,n): return s.f.get(n) or open('work/fs/'+n,'rb').read()
    def setFileByName(s,n,d): s.f[n]=d
r=R(); rep=[]
getattr(g,sys.argv[1])(r,rep); print(rep)
for n,d in r.f.items(): open('work/fs/_t_'+n,'wb').write(d)
