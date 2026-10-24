import sys; sys.path.insert(0,'tools')
import bgedit, numpy as np
from PIL import Image
bf=bgedit.BgFile(open('work/fs/boot.bin','rb').read())
pal4=np.frombuffer(bf.pals_raw[0],'<u2').astype(int)
pal4=np.stack([(pal4&31)*255//31,((pal4>>5)&31)*255//31,((pal4>>10)&31)*255//31],-1).astype(np.uint8)[16:32]
raw=bytes(bf.tiles[0]); outs=[]
def decode(mi):
    m=bf.maps[mi]; img=np.zeros((192,256),int)
    for cy in range(24):
        for cx in range(32):
            e=int(m[cy,cx]); t=e&0x3FF; b=np.frombuffer(raw[t*32:t*32+32],np.uint8)
            img[cy*8:cy*8+8,cx*8:cx*8+8]=np.stack([b&15,b>>4],1).reshape(8,8)
    return img
def erase(img, y0=24, y1=145):
    H,W=img.shape
    def at(y,x): return img[y, x] if 0<=y<H and 0<=x<W else -1
    mask=np.zeros_like(img,bool)
    for y in range(y0,y1):
        for x in range(W):
            v=img[y,x]
            ok=sum(v==at(y+s*2*k, x-s*2*k) for k in (1,2) for s in (1,-1))
            mask[y,x]= ok<2
    g=mask.copy()
    for _ in range(2): g[1:]|=g[:-1].copy(); g[:-1]|=g[1:].copy(); g[:,1:]|=g[:,:-1].copy(); g[:,:-1]|=g[:,1:].copy()
    g[:y0]=False; g[y1:]=False
    new=img.copy()
    for y,x in zip(*np.where(g)):
        for k in range(1,60):
            for s in (1,-1):
                yy,xx=y+s*2*k,x-s*2*k
                if 0<=yy<H and 0<=xx<W and not g[yy,xx]: new[y,x]=img[yy,xx]; break
            else: continue
            break
    return new
if __name__=='__main__':
    for mi in (2,3,4):
        img=decode(mi); new=erase(img)
        outs.append(np.concatenate([pal4[img],pal4[new]],0))
    Image.fromarray(np.concatenate(outs,1)).save('work/emu/z.png')
