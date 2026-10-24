import capstone,struct
A=open('work/arm9_dec.bin','rb').read(); BASE=0x2000000
T=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB); R=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
def dis(addr,n=200,thumb=True,data=A,base=BASE):
  md=T if thumb else R; o=addr-base
  for i in md.disasm(data[o:o+n],addr):
    extra=''
    if i.mnemonic=='ldr' and 'pc' in i.op_str and '#' in i.op_str:
      imm=int(i.op_str.split('#')[-1].rstrip(']'),0); la=((i.address+4)&~3)+imm
      if 0<=la-base<len(data)-4: extra=f'  ; ={struct.unpack_from("<I",data,la-base)[0]:#x}'
    print(f'{i.address:#x}: {i.mnemonic} {i.op_str}{extra}')
def bl_callers(target,data=A,base=BASE):
  out=[]
  for o in range(0,len(data)-4,2):
    h1,h2=struct.unpack_from('<HH',data,o)
    if (h1&0xF800)==0xF000 and (h2&0xE800)==0xE800:
      off=((h1&0x7FF)<<12)|((h2&0x7FF)<<1)
      if off&0x400000: off-=0x800000
      t=base+o+4+off
      if (h2&0xF800)==0xE800: t&=~3
      if t==target: out.append(base+o)
  return out
