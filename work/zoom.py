import sys
from PIL import Image
im=Image.open(sys.argv[1]); x0,y0,x1,y1=map(int,sys.argv[2:6]); s=int(sys.argv[7]) if len(sys.argv)>7 else 4
c=im.crop((x0,y0,x1,y1)); c.resize((c.width*s,c.height*s),Image.NEAREST).save(sys.argv[6])
