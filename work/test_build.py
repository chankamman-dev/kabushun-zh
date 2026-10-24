import sys,struct; sys.path.insert(0,'tools')
import ndspy.rom, ndspy.codeCompression as cc
import engine, cnfont
rom=ndspy.rom.NintendoDSRom.fromFile('../downloads/nds-20261019/roms/Kabu Trader Shun (Japan).nds')
arm9=bytearray(cc.decompress(rom.arm9))
struct.pack_into("<I",arm9,0xb68+0x14,0)   # module params: compressed_static_end=0
lines=[(0x2130a,[('<1>','奈良崎　透'),('','……'),('[4:3]',None)],0x000),
       (0x21330,[('','他是父亲唯一的炒股弟子。')],0x800),
       (0x21352,[('','虽然总给人一种难以接近的')],0),
       (0x21370,[('','感觉，'),('[4:3]',None)],0),
       (0x21386,[('','但和父亲在一起时表情很丰富。')],0x800)]
chars=[]
def gid(c):
  if c not in chars: chars.append(c)
  return chars.index(c)
k=bytearray(rom.getFileByName('KSSCV.bin'))
KB=0x22B4000; rs=0x2130a; re_=0x213ac
bits=bytearray((re_-rs)//8+1)
for off,segs,flag in lines:
  o=off; n=0
  for tag,txt in segs:
    if txt is None:
      struct.pack_into('<H',k,o,0x4000|int(tag[3:-1],16)); o+=2; continue
    col=1 if tag=='<1>' else 0
    for c in txt:
      g=gid(c); struct.pack_into('<H',k,o,(col<<10)|(g&0x3ff))
      ui=(o-rs)//2; page=(g>>10)+1; bits[ui//4]|=page<<((ui%4)*2)
      o+=2; n+=1
  struct.pack_into('<H',k,o,0x8000|flag|n)
rom.setFileByName('KSSCV.bin',bytes(k))
lay=engine.Layout(len(bits),len(chars),range(0x200,0x400))
regions=[(KB+rs,KB+re_,lay.arm9_bits,KB,0x022B4028)]
engine.apply(arm9,lay,regions,bytes(bits),cnfont.build(chars),hooks=tuple(sys.argv[1].split(',')) if len(sys.argv)>1 else ('get','r3','grid'))
rom.arm9=bytes(arm9)
rom.saveToFile(sys.argv[2] if len(sys.argv)>2 else 'work/test1.nds'); print('ok',len(chars))
