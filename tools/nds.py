"""Minimal NDS ROM reader: header, ARM9/overlays, NitroFS FNT/FAT."""
import struct
from pathlib import Path

class Rom:
    def __init__(self, data):
        self.data = bytearray(data)
        d = self.data
        h = lambda o: struct.unpack_from('<I', d, o)[0]
        self.arm9_off, self.arm9_entry, self.arm9_ram, self.arm9_size = h(0x20), h(0x24), h(0x28), h(0x2C)
        self.arm7_off, self.arm7_size = h(0x30), h(0x3C)
        self.fnt_off, self.fnt_size = h(0x40), h(0x44)
        self.fat_off, self.fat_size = h(0x48), h(0x4C)
        self.ovt9_off, self.ovt9_size = h(0x50), h(0x54)
        self.fat = [struct.unpack_from('<II', d, self.fat_off + i * 8) for i in range(self.fat_size // 8)]
        self.names = {}
        self._walk(0xF000, '')
        self.overlays = []
        for i in range(self.ovt9_size // 32):
            e = struct.unpack_from('<8I', d, self.ovt9_off + i * 32)
            self.overlays.append(dict(id=e[0], ram=e[1], size=e[2], bss=e[3], sinit=e[4], sinit_end=e[5], file=e[6], flags=e[7]))

    def _walk(self, dir_id, prefix):
        d = self.data
        base = self.fnt_off + (dir_id & 0xFFF) * 8
        sub_off, first, _ = struct.unpack_from('<IHH', d, base)
        p = self.fnt_off + sub_off
        fid = first
        while True:
            t = d[p]; p += 1
            if t == 0: break
            n = t & 0x7F
            name = bytes(d[p:p + n]).decode('ascii'); p += n
            if t & 0x80:
                sub = struct.unpack_from('<H', d, p)[0]; p += 2
                self._walk(sub, prefix + name + '/')
            else:
                self.names[prefix + name] = fid; fid += 1

    def file(self, key):
        fid = self.names[key] if isinstance(key, str) else key
        s, e = self.fat[fid]
        return bytes(self.data[s:e])

    def arm9(self):
        return bytes(self.data[self.arm9_off:self.arm9_off + self.arm9_size])
