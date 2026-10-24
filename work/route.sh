# usage: route.sh ROM prefix   -> work/emu/<prefix>_trade.st at the tutorial trade start
R=$1; P=$2; PY=.venv/Scripts/python.exe
$PY work/autoplay.py $R ${P}1 1000 >/dev/null 2>&1
$PY work/nav.py $R ${P}1.st ${P}2 195,50 40 >/dev/null 2>&1
$PY work/autoplay.py $R ${P}4 150 ${P}2.st >/dev/null 2>&1
$PY work/nav.py $R ${P}4.st ${P}5 60,50 80 >/dev/null 2>&1
$PY work/act.py $R ${P}5.st ${P}6 t:232,12 w:120 t:128,48 w:120 t:35,80 w:60 t:150,146 w:20 dt:150,146 w:120 A*3 w:60 >/dev/null 2>&1
$PY work/act.py $R ${P}6.st ${P}7 A*3 w:60 t:16,182 w:120 >/dev/null 2>&1
$PY work/act.py $R ${P}7.st ${P}8 t:128,112 w:120 A*3 w:60 A*3 w:60 >/dev/null 2>&1
echo route-done
rm -f work/emu/${P}t_*.png
$PY work/autoplay.py $R ${P}t 400 ${P}8.st >/dev/null 2>&1
echo trade-done
