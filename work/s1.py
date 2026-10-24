exec(open('work/drive.py').read())
e.run(960); e.tap(128,96,after=120); e.shot('m0.png'); e.save('title_menu.st')
names=['m0.png']
for i in range(7):
  e.press('A',after=90); n=f'm{i+1}.png'; e.shot(n); names.append(n)
sheet(names,'menu_sheet.png')
