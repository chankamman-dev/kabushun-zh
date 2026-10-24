"""Print Japanese messages a..b-1: python tools/chunk.py a b"""
import sys, re
from pathlib import Path
a, b = int(sys.argv[1]), int(sys.argv[2])
txt = (Path(__file__).resolve().parent.parent / 'text/jp/ksscv.txt').read_text(encoding='utf8')
blocks = re.split(r'\n(?=@\d+\n)', txt)
out = [blk for blk in blocks if a <= int(blk[1:blk.index('\n')] if '\n' in blk else blk[1:]) < b]
sys.stdout.buffer.write(('\n'.join(out) + '\n').encode('utf8'))
