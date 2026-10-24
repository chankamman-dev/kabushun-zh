import struct, numpy as np, sys
from PIL import Image, ImageDraw
def load(path):
    d=open(path,'rb').read()
    n=struct.unpack_from('<I',d,0)[0]; offs=[o&0x7fffffff for o in struct.unpack_from(f'<{n+1}I',d,4)]
    pal=np.frombuffer(d[offs[0]:offs[0]+512],'<u2').astype(int)
    rgb=np.stack([(pal&31)*255//31,((pal>>5)&31)*255//31,((pal>>10)&31)*255//31],-1).astype(np.uint8)
    tiles=np.frombuffer(d[offs[1]:offs[2]],np.uint8).reshape(-1,8,8)
    img=np.zeros((256,256),np.uint8)
    for i in range(1024):
        y,x=divmod(i,32); img[y*8:y*8+8,x*8:x*8+8]=tiles[i]
    return img,rgb
if __name__=='__main__':
    f,x0,y0,x1,y1=sys.argv[1],*map(int,sys.argv[2:6])
    img,rgb=load(f'work/fs/{f}.bin'); s=6
    im=Image.fromarray(rgb[img[y0:y1,x0:x1]]).resize(((x1-x0)*s,(y1-y0)*s),0); d=ImageDraw.Draw(im)
    for x in range(x0,x1):
        if x%8==0: d.line([((x-x0)*s,0),((x-x0)*s,im.height)],fill=(255,255,0)); d.text(((x-x0)*s+1,0),str(x),fill=(255,0,0))
    for y in range(y0,y1):
        if y%8==0: d.line([(0,(y-y0)*s),(im.width,(y-y0)*s)],fill=(255,255,0)); d.text((0,(y-y0)*s+1),str(y),fill=(255,0,0))
    im.save('work/emu/wall.png')
