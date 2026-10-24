exec(open('work/drive.py').read())
import ctypes as C, json, struct
cm=json.load(open('work/charmap.json',encoding='utf8')); G=cm['glyph']; T=cm['t0']
inv={}
for c in range(1024): inv.setdefault(G[str(T[c])],c)
a=open('work/arm9_dec.bin','rb').read()
target='そう悲観'
units=[inv[ch] for ch in target]
pat=struct.pack('<%dH'%len(units),*units)
off=a.find(pat); print('arm9 off',hex(off))
e.load('title_menu.st'); e.press('A',after=90); e.press('A',after=90)
p=e.core.retro_get_memory_data(2)
ram=C.string_at(p,4*1024*1024)
print('in ram at', [hex(0x2000000+i) for i in range(len(ram)) if ram.startswith(pat,i)][:5])
addr=off
# poke: replace そう with ＡＢ
for i,ch in enumerate('ＡＢ'):
  C.memmove(p+addr+2*i, struct.pack('<H',inv[ch]),2)
for i in range(4):
  e.press('A',after=120); e.shot(f'poke{i}.png')
sheet([f'poke{i}.png' for i in range(4)],'poke_sheet.png')
