import sys
from PIL import Image
def view(buf,off,count,out,cols=32,bpg=32,w=16,h=16,lsb=True):
  img=Image.new('L',(cols*(w+2),((count+cols-1)//cols)*(h+2)),255)
  rb=bpg//h
  for g in range(count):
    b=buf[off+g*bpg:off+g*bpg+bpg]
    if len(b)<bpg: break
    for y in range(h):
      for x in range(w):
        byte=b[y*rb+x//8]; bit=(byte>>(x%8))&1 if lsb else (byte>>(7-x%8))&1
        if bit: img.putpixel((g%cols*(w+2)+x,g//cols*(h+2)+y),0)
  img.resize((img.width*2,img.height*2),Image.NEAREST).save(out)
if __name__=='__main__':
  f,off,n,out=sys.argv[1],int(sys.argv[2],0),int(sys.argv[3]),sys.argv[4]
  view(open(f,'rb').read(),off,n,out)
