exec(open('work/drive.py').read())
k=open('extract/KSSCV.bin','rb').read()
def check(tag):
  r=e.ram(); o=0x2B4000
  print(tag,'ksscv match',r[o:o+len(k)]==k, end=' ')
  gap=r[0x331B6C:0x35B000]
  nz=[i for i in range(0,len(gap),256) if any(gap[i:i+256])]
  print('gap nonzero blocks',len(nz),'of',len(gap)//256, hex(0x2331B6C+nz[0]) if nz else '')
e.run(300); check('boot')
e.load('title_menu.st'); check('title')
e.press('A',after=90); e.press('A',after=90); check('opening')
for i in range(30): e.press('A',after=40)
check('later'); e.shot('later.png')
