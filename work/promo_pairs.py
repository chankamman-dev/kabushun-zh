"""before/after stills for the promo: work/promo/pair_*.png (JP left image, CN right image as separate files)"""
import sys; sys.path.insert(0,'tools'); sys.path.insert(0,'work')
import ndspy.rom, objedit, bgedit, numpy as np, wall
from PIL import Image
jp=ndspy.rom.NintendoDSRom.fromFile('work/orig.nds'); cn=ndspy.rom.NintendoDSRom.fromFile('out/kabushun_zh.nds')
dat=jp.getFileByName('obj_dat.bin')
OF={'jp':objedit.ObjFile(jp.getFileByName('obj_fnt.bin'),dat),'cn':objedit.ObjFile(cn.getFileByName('obj_fnt.bin'),dat)}
R={'jp':jp,'cn':cn}
def spr(v,si,fi,bg=(18,22,38)):
    idx,own,pal=OF[v].canvas(si,fi); rgb=np.zeros(idx.shape+(3,),np.uint8); rgb[:]=bg; m=idx>0; rgb[m]=pal[idx[m]]; return Image.fromarray(rgb)
def bgimg(v,name,mi,ts=0):
    bf=bgedit.BgFile(R[v].getFileByName(name)); c=bf.canvas(mi,ts,(0,0,32,24)); return Image.fromarray(bf.pal[min(ts,len(bf.pal)-1)][c].astype(np.uint8))
def wallimg(v,name):
    open('work/emu/_w.bin','wb').write(R[v].getFileByName(name)); img,rgb=wall.load('work/emu/_w.bin'); return Image.fromarray(rgb[img][:192])
def stack(ims,gap=6,bg=(18,22,38)):
    w=max(i.width for i in ims); h=sum(i.height for i in ims)+gap*(len(ims)-1)
    S=Image.new('RGB',(w,h),bg); y=0
    for i in ims: S.paste(i,((w-i.width)//2,y)); y+=i.height+gap
    return S
pairs={
 'title': lambda v: bgimg(v,'title2.bin',0),
 'card': lambda v: stack([spr(v,614,5),]) ,
 'card2': lambda v: spr(v,615,1),
 'ranking': lambda v: bgimg(v,'ranking.bin',0),
 'cardlogo': lambda v: bgimg(v,'view_bg.bin',1),
 'menus': lambda v: stack([spr(v,538,3),spr(v,512,3),spr(v,602,7),spr(v,232,3)]),
 'shouts': lambda v: stack([spr(v,407,2),spr(v,409,4),spr(v,411,1),spr(v,413,3)]),
 'names': lambda v: stack([spr(v,643,0),spr(v,643,2),spr(v,437,0),spr(v,2,13)]),
 'wall': lambda v: wallimg(v,'bged00.bin'),
 'boot': lambda v: None,
}
for k,f in pairs.items():
    for v in ('jp','cn'):
        im=f(v)
        if im is not None: im.save(f'work/promo/pair_{k}_{v}.png')
print('ok')
