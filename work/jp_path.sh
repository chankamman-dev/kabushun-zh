set -e
P=.venv/Scripts/python.exe
$P work/autoplay.py work/orig.nds jsp 1500 >/dev/null 2>&1
$P work/autoplay.py work/orig.nds jsq 1500 jsp.st >/dev/null 2>&1
echo stage2
