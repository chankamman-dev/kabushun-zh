"""Record a clip: rec.py ROM out.mp4 (boot|state.st) actions...  (same action syntax as act.py, plus
'pa:N' = press A then wait N frames).  Writes lossless 30 fps video (256x384) + .wav, and out.st."""
import sys, subprocess, wave; sys.path.insert(0, 'tools')
from emu import Emu
import numpy as np
FF = r'G:\ai liabary\thor-capture-pkg6-release\evidence\ci-dependencies\extracted\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe'
rom, out, src, acts = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
e = Emu(rom, 'work/emu')
if src == 'boot': pass
else: e.load(src)
e.audio = bytearray()
p = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '256x384', '-r', '30',
                      '-i', '-', '-c:v', 'libx264rgb', '-crf', '0', '-preset', 'ultrafast', out], stdin=subprocess.PIPE)
n = [0]
orig_run = e.run
def run(frames=1, buttons=(), touch=None):
    for _ in range(frames):
        orig_run(1, buttons, touch)
        n[0] += 1
        if n[0] % 2 == 0 and e.frame: p.stdin.write(np.asarray(e.image()).tobytes())
e.run = run
for a in acts:
    rep = 1
    if '*' in a: a, rep = a.split('*'); rep = int(rep)
    for _ in range(rep):
        if a.startswith('t:'):
            x, y = map(int, a[2:].split(',')); e.tap(x, y, hold=6, after=40)
        elif a.startswith('w:'): e.run(int(a[2:]))
        elif a.startswith('pa:'): e.press('A', hold=4, after=int(a[3:]))
        else: e.press(a, hold=4, after=46)
p.stdin.close(); p.wait()
a = np.frombuffer(bytes(e.audio), np.int16)
w = wave.open(out[:-4] + '.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(44228)
w.writeframes(a.tobytes()); w.close()
e.save(out[:-4].split('/')[-1] + '.st')
print('frames', n[0], 'audio s', len(a) / 2 / 44228)
