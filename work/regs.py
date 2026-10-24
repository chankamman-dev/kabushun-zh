import struct
def fields(d):
    p=32; out={}
    while p+8<=len(d):
        cid,size=struct.unpack_from('<II',d,p); p+=8
        q=p
        while q<p+size:
            name=d[q:q+4]; sz,cnt=struct.unpack_from('<II',d,q+4); q+=12
            out.setdefault(cid,{})[name.decode('latin1')]=d[q:q+sz*cnt]; q+=sz*cnt
        p+=size
    return out
def arm9(d):
    f=fields(d)[1]
    return f
if __name__=='__main__':
    import sys
    d=open(sys.argv[1],'rb').read(); f=arm9(d)
    for k,v in f.items():
        if len(v)<=128: print(k, v.hex())
