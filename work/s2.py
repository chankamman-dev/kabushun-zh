exec(open('work/drive.py').read())
e.load('title_menu.st'); e.press('A',after=90); e.press('A',after=90)
ram=e.ram(); open('work/ram_dialog1.bin','wb').write(ram)
f=open('extract/font_jp.bin','rb').read()[32:]
for idx in (137,288,99,264):
  g=f[idx*32+4:idx*32+26]
  print(idx,[hex(0x2000000+i) for i in range(len(ram)) if ram.startswith(g,i)][:5])
k=open('extract/KSSCV.bin','rb').read()
import re
pat=bytes.fromhex('8900 0801 0801'.replace(' ',''))
print([hex(m.start()) for m in re.finditer(re.escape(pat),k)][:20])
print(hex(ram.find(k[0x21244:0x21264])))
