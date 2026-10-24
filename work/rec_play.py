"""Record real play: rec_play.py ROM state.st out.mp4 frames
Trade screen: buy on the bright BUY button, sell some time later; menus/dialogue: autoplay-like."""
import sys, subprocess, wave; sys.path.insert(0, 'tools'); sys.path.insert(0, 'work')
from emu import Emu
import numpy as np
FF = r'G:\ai liabary\thor-capture-pkg6-release\evidence\ci-dependencies\extracted\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe'
rom, st, out, N = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
e = Emu(rom, 'work/emu'); e.load(st); e.run(2); e.audio = bytearray()
p = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '256x384', '-r', '30',
                      '-i', '-', '-c:v', 'libx264rgb', '-crf', '0', '-preset', 'ultrafast', out], stdin=subprocess.PIPE)
n = [0]; orig = e.run
def run(frames=1, buttons=(), touch=None):
    for _ in range(frames):
        orig(1, buttons, touch); n[0] += 1
        if n[0] % 2 == 0 and e.frame: p.stdin.write(np.asarray(e.image()).tobytes())
e.run = run
def bottom(): return np.asarray(e.image()).astype(int)[192:]
def btn(a, x0, x1):                                          # mean colour of the BUY/SELL button area
    return a[166:186, x0:x1].reshape(-1, 3).mean(0)
def buttons(a):
    m = (a[:, :, 2] > 100) & (a[:, :, 1] >= 30) & (a[:, :, 2] - a[:, :, 0] > 60)
    m[:40] = False; m[168:] = False
    rows = m.sum(1) > 60
    out, y = [], 0
    while y < 192:
        if rows[y]:
            y0 = y
            while y < 192 and rows[y]: y += 1
            if y - y0 >= 6:
                yc = (y0 + y) // 2; r = m[y0 + 2]; x = 0
                while x < 256:
                    if r[x]:
                        x0 = x
                        while x < 256 and r[x]: x += 1
                        if x - x0 >= 50: out.append(((x0 + x) // 2, yc))
                    x += 1
        y += 1
    return out
visits = {}
for a_ in sys.argv[5:]:
    x_, y_ = map(int, a_[2:].split(',')); e.tap(x_, y_, hold=6, after=30)
holding = False; last = 0; k = 0
while n[0] < N:
    a = bottom()
    buy, sell = btn(a, 95, 140), btn(a, 170, 215)
    g = a[180:188, 8:56].reshape(-1, 3).mean(0)                # the green gauge under Shun = trade screen
    if g[1] > 140 and g[0] < 140 and g[2] < 120:
        if not holding and buy[0] > 150 and buy[1] < 90 and n[0] - last > 90:
            e.tap(118, 176, hold=6, after=20); holding = True; last = n[0]
        elif holding and sell[2] > 150 and n[0] - last > 240:
            e.tap(192, 176, hold=6, after=20); holding = False; last = n[0]
        else:
            e.run(10)
    else:
        b = buttons(a)
        if b:
            key = tuple(b); c = visits.get(key, 0); visits[key] = c + 1
            e.tap(*b[::-1][c % len(b)], hold=6, after=40); e.run(20)
        else: e.press('A', hold=4, after=36)
        k += 1
p.stdin.close(); p.wait()
au = np.frombuffer(bytes(e.audio), np.int16)
w = wave.open(out[:-4] + '.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(44228); w.writeframes(au.tobytes()); w.close()
e.save(out.split('/')[-1][:-4] + '.st')
print('frames', n[0])
