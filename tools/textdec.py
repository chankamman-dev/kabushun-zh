import json,struct
cm=json.load(open('work/charmap.json',encoding='utf8')); G=cm['glyph']
def d(u,T):
  if u&0x8000: return f'[8:{u&0x7fff:x}]'
  if u&0x4000: return f'[4:{u&0x3fff:x}]'
  hb=(u>>10)&15; ch=G[str(T[u&0x3ff])]
  return ch if hb==0 else f'<{hb:x}{ch}>'
def region(b,s,e,table='t0',base=0x2000000,every=0):
  T=cm[table]; out=[]; o=s
  while o<e:
    u=struct.unpack_from('<H',b,o)[0]; out.append(d(u,T))
    if u&0x8000: out.append(f'  @{base+o+2:x}\n')
    o+=2
  return ''.join(out)
