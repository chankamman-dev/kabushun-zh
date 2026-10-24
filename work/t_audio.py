import sys; sys.path.insert(0,'tools')
from emu import Emu
import numpy as np, wave
e=Emu('out/kabushun_zh.nds','work/emu'); print(e.sample_rate())
e.audio=bytearray()
for k in range(90):
    e.run(60)
a=np.frombuffer(bytes(e.audio),np.int16).reshape(-1,2)
print(len(a), len(a)/90)
sec=len(a)//90
print([int(np.abs(a[i*sec:(i+1)*sec]).mean()) for i in range(90)])
w=wave.open('work/emu/boot.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(round(len(a)/90/ (60/59.8261))); w.writeframes(a.tobytes()); w.close()
e.shot('boot_end.png')
