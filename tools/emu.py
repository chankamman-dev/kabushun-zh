"""In-process headless DeSmuME libretro wrapper (no window, no focus stealing)."""
import ctypes as C, os
from pathlib import Path
import numpy as np
from PIL import Image

TOOLS = Path(__file__).resolve().parent
B = dict(B=0, Y=1, SELECT=2, START=3, UP=4, DOWN=5, LEFT=6, RIGHT=7, A=8, X=9, L=10, R=11)

class Var(C.Structure): _fields_ = [('key', C.c_char_p), ('value', C.c_char_p)]
class Game(C.Structure): _fields_ = [('path', C.c_char_p), ('data', C.c_void_p), ('size', C.c_size_t), ('meta', C.c_char_p)]
ENV = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
VIDEO = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
AUDIO = C.CFUNCTYPE(None, C.c_int16, C.c_int16)
BATCH = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
POLL = C.CFUNCTYPE(None)
INPUT = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)
LOG = C.CFUNCTYPE(None, C.c_int, C.c_char_p)

class Emu:
    def __init__(self, rom_path, workdir):
        self.dir = Path(workdir); self.dir.mkdir(parents=True, exist_ok=True)
        self.core = C.CDLL(str(TOOLS / 'desmume_libretro.dll'))
        self.frame = None; self.pixel = 2; self.buttons = set(); self.touch = None
        self.audio = None                 # set to bytearray() to capture int16 stereo samples
        self.options = {b'desmume_cpu_mode': b'interpreter', b'desmume_opengl_mode': b'disabled',
                        b'desmume_pointer_type': b'touch', b'desmume_pointer_mouse': b'enabled',
                        b'desmume_screens_layout': b'top/bottom', b'desmume_internal_resolution': b'256x192',
                        b'desmume_num_cores': b'1'}
        self._dirb = str(self.dir).encode()
        self._cbs = [LOG(lambda l, f: None)]
        self._cbs += [ENV(self._env), VIDEO(self._video), AUDIO(lambda l, r: None), BATCH(self._batch),
                      POLL(lambda: None), INPUT(self._input)]
        c = self.core
        for name, cb in zip(['environment', 'video_refresh', 'audio_sample', 'audio_sample_batch', 'input_poll', 'input_state'], self._cbs[1:]):
            fn = getattr(c, 'retro_set_' + name); fn.argtypes = [type(cb)]; fn(cb)
        c.retro_init()
        rom = Path(rom_path).resolve(); data = rom.read_bytes()
        self._rombuf = C.create_string_buffer(data)
        c.retro_load_game.argtypes = [C.POINTER(Game)]; c.retro_load_game.restype = C.c_bool
        g = Game(str(rom).encode(), C.cast(self._rombuf, C.c_void_p), len(data), None)
        assert c.retro_load_game(C.byref(g)), 'load failed'
        c.retro_serialize_size.restype = C.c_size_t
        c.retro_serialize.argtypes = [C.c_void_p, C.c_size_t]; c.retro_serialize.restype = C.c_bool
        c.retro_unserialize.argtypes = [C.c_void_p, C.c_size_t]; c.retro_unserialize.restype = C.c_bool
        c.retro_get_memory_data.argtypes = [C.c_uint]; c.retro_get_memory_data.restype = C.c_void_p
        c.retro_get_memory_size.argtypes = [C.c_uint]; c.retro_get_memory_size.restype = C.c_size_t

    def _env(self, cmd, data):
        if cmd == 27: C.cast(data, C.POINTER(C.c_void_p))[0] = C.cast(self._cbs[0], C.c_void_p); return True
        if cmd in (9, 31, 30): C.cast(data, C.POINTER(C.c_char_p))[0] = self._dirb; return True
        if cmd == 10: self.pixel = C.cast(data, C.POINTER(C.c_int))[0]; return self.pixel in (0, 1, 2)
        if cmd == 15:
            v = C.cast(data, C.POINTER(Var)).contents; v.value = self.options.get(v.key); return v.value is not None
        if cmd == 17: C.cast(data, C.POINTER(C.c_bool))[0] = False; return True
        if cmd == 3: C.cast(data, C.POINTER(C.c_bool))[0] = True; return True
        if cmd in (39, 52): C.cast(data, C.POINTER(C.c_uint))[0] = 0; return True
        if cmd in (16, 11, 18, 35, 37): return True
        return False

    def _video(self, data, w, h, pitch):
        if not data or data == C.c_void_p(-1).value: return
        self.frame = (C.string_at(data, h * pitch), w, h, pitch, self.pixel)

    def _batch(self, data, n):
        if self.audio is not None and data: self.audio += C.string_at(data, n * 4)
        return n

    def sample_rate(self):
        buf = (C.c_double * 8)()                   # geometry: 4 uint + float, then timing: fps, rate
        self.core.retro_get_system_av_info(C.byref(buf))
        raw = bytes(buf); import struct
        return struct.unpack_from('<dd', raw, 24)

    def _input(self, port, device, index, id):
        if device == 1: return int(id in self.buttons)
        if device == 6 and self.touch:
            x, y = self.touch
            if id == 0: return int((x + .5) / 256 * 65536 - 32768)
            if id == 1: return int((y + 192 + .5) / 384 * 65536 - 32768)
            if id == 2: return 1
        return 0

    def run(self, frames=1, buttons=(), touch=None):
        self.buttons = {B[b] for b in buttons}; self.touch = touch
        for _ in range(frames): self.core.retro_run()
        self.buttons = set(); self.touch = None

    def press(self, button, hold=6, after=20):
        self.run(hold, [button]); self.run(after)

    def tap(self, x, y, hold=6, after=20):
        self.run(hold, touch=(x, y)); self.run(after)

    def image(self):
        raw, w, h, pitch, fmt = self.frame
        if fmt == 1:
            a = np.frombuffer(raw, np.uint8).reshape(h, pitch)[:, :w * 4].reshape(h, w, 4); rgb = a[:, :, [2, 1, 0]]
        else:
            a = np.frombuffer(raw, np.uint16).reshape(h, pitch // 2)[:, :w]
            if fmt == 2: rgb = np.stack([((a >> 11) & 31) * 255 // 31, ((a >> 5) & 63) * 255 // 63, (a & 31) * 255 // 31], -1)
            else: rgb = np.stack([((a >> 10) & 31) * 255 // 31, ((a >> 5) & 31) * 255 // 31, (a & 31) * 255 // 31], -1)
        return Image.fromarray(rgb.astype('uint8'))

    def shot(self, name):
        p = self.dir / name; self.image().save(p); return p

    def ram(self):
        n = self.core.retro_get_memory_size(2); p = self.core.retro_get_memory_data(2)
        return C.string_at(p, n)

    def save(self, name):
        n = self.core.retro_serialize_size(); b = C.create_string_buffer(n)
        assert self.core.retro_serialize(b, n); (self.dir / name).write_bytes(b.raw)

    def load(self, name):
        d = (self.dir / name).read_bytes(); b = C.create_string_buffer(d)
        assert self.core.retro_unserialize(b, len(d))
