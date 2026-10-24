"""Engine patch: page-extended glyphs for every text renderer.

Text units keep their original 16-bit layout (bit15 line end, bit14 command,
bits12-13 effect, bits10-11 colour, bits0-9 code).  A side bitmap (2 bits per
text unit, looked up by the unit's address) gives a page 0-3:
  page 0  -> original behaviour (code -> table -> original glyph)
  page n  -> new glyph id (n-1)*1024 + code, stored as 12x12 1bpp and expanded
             at runtime to the game's 16x16 2bpp format (shadow generated).

Renderers patched:
  * getGlyph callers (0x200E244, 0x200E96E)       2D text (bottom screen, menus)
  * renderer3 inline lookup (0x2009D1E)            typewriter 2D window
  * 3D dialogue grid copy (0x2008734, replaced)     top-screen box: the unit's code
    is replaced by a dynamic cell of the 512x512 2bpp atlas texture; new glyphs
    are drawn into the RAM atlas and the changed 2KB bands re-uploaded.
The original kanji area of font 1 (glyphs 285..1212) is reused as the cave.
"""
import struct
import keystone

BASE = 0x2000000
FONT0 = 0x20F3868            # original 2bpp font, 64 bytes/glyph
KEEP_GLYPHS = 285            # ASCII, kana, symbols stay
CAVE = FONT0 + KEEP_GLYPHS * 64
CAVE_END = FONT0 + 1213 * 64
TABLES = 0x20F27C4           # pointer array to code->glyph tables
ATLAS = 0x20E27C4            # 3D text atlas, code c at +(c//32)*0x800+(c%32)*4, stride 128
GX_BEGIN, GX_LOAD, GX_END = 0x20BEC50, 0x20BEAEC, 0x20BEA7C
CALLERS = {0x200E244: 0x24, 0x200E96E: 0x04}   # bl getGlyph site -> caller stack slot of unit pointer
R3_SITE = 0x2009D1E          # renderer3: lsls r2,r1,#6; ldr r1,=FONT0; adds r2,r1,r2
R3_PTR_SLOT, R3_CODE_SLOT = 0x08, 0x44
GRID_FUNC = 0x2008734        # 3D grid copy function (leaf, thumb), replaced wholesale
GLYPH_BYTES = 18             # 12 rows x 12 bits, LSB-first bitstream
MAX_REGIONS = 4

def asm(src, addr):
    ks = keystone.Ks(keystone.KS_ARCH_ARM, keystone.KS_MODE_ARM)
    enc, _ = ks.asm(src, addr)
    return bytes(enc)

def thumb_blx(src, dst):
    """Thumb BLX (to ARM) from src to 4-aligned dst."""
    off = dst - ((src + 4) & ~3)
    assert -0x400000 <= off < 0x400000 and off % 4 == 0
    return struct.pack('<HH', 0xF000 | ((off >> 12) & 0x7FF), 0xE800 | ((off >> 1) & 0x7FF))

def code_src(L):
    s0, s1 = CALLERS.values()
    return f'''
  b stub_get0
  b stub_get1
  b stub_r3
  b grid_copy

@ --- 2D: replacements for `bl getGlyph` (r0=code, r1=table) ---
stub_get0:
  push {{r0, r1, lr}}
  ldr r2, [sp, #{s0} + 12]
  b get_common
stub_get1:
  push {{r0, r1, lr}}
  ldr r2, [sp, #{s1} + 12]
get_common:
  bl resolve
  movs r2, r0
  pop {{r0, r1, lr}}
  movne r0, r2
  bxne lr
  ldr r2, p_tables
  ldr r3, [r2, r1, lsl #2]
  mov r0, r0, lsl #1
  ldrh r0, [r3, r0]
  ldr r2, p_font0
  add r0, r2, r0, lsl #6
  bx lr

@ --- renderer3: r1 = original glyph index; return r2 = glyph pointer ---
stub_r3:
  push {{r0, r1, r3, lr}}
  ldr r2, [sp, #{R3_PTR_SLOT} + 16]
  ldr r0, [sp, #{R3_CODE_SLOT} + 16]
  mov r0, r0, lsr #1
  bl resolve
  movs r2, r0
  pop {{r0, r1, r3, lr}}
  ldreq r2, p_font0
  addeq r2, r2, r1, lsl #6
  bx lr

@ --- 3D grid copy: ARM rewrite of 0x2008734(win, col, line, src, count, arg5) ---
@ copies `count` text units into window `win`'s 32x10 grid; Chinese units get
@ their code replaced by a dynamic atlas cell.
grid_copy:
  push {{r4-r11, lr}}
  ldr r12, p_win_mask
  ldrb r12, [r12, #0x15]
  mov r4, #1
  tst r12, r4, lsl r0
  beq gc_ret
  cmp r1, #0x20
  bge gc_ret
  cmp r2, #0xa
  bge gc_ret
  ldr r12, p_windows
  mov r4, #0x304
  mla r8, r0, r4, r12
  ldr r4, [sp, #40]
  strb r4, [r8, #0x1c]
  ldr r9, [sp, #36]
  mov r6, r3
  mov r5, r1
  mov r11, r2
  add r7, r8, r2, lsl #6
  add r7, r7, r1, lsl #1
  mov r10, #0
gc_loop:
  cmp r10, r9
  bge gc_done
  ldrh r4, [r6]
  bl xform
  add r6, r6, #2
  strh r4, [r7, #0x28]
  add r7, r7, #2
  add r5, r5, #1
  cmp r5, #0x20
  bge gc_done
  add r10, r10, #1
  b gc_loop
gc_done:
  ldrb r2, [r8, #7]
  cmp r5, r2
  movgt r2, r5
  strb r2, [r8, #7]
  ldrb r2, [r8, #6]
  add r4, r11, #1
  cmp r4, r2
  movle r4, r2
  strb r4, [r8, #6]
  add r2, r8, r11, lsl #2
  sub r4, r5, #1
  mov r4, r4, lsl #4
  ldr r12, p_off2a8
  str r4, [r2, r12]
  mov r4, r5, lsl #4
  ldr r12, p_off2d0
  str r4, [r2, r12]
  mov r4, #0x10
  strb r4, [r8, #0x1d]
gc_ret:
  pop {{r4-r11, lr}}
  bx lr

@ xform(r4 = unit, r6 = unit address) -> r4 (Chinese code replaced by atlas cell)
xform:
  push {{r0-r3, r5, r7-r12, lr}}
  tst r4, #0xC000
  bne xf_out
  mov r2, r6
  bl page_of
  cmp r0, #0
  beq xf_out
  bl gid_of
  mov r10, r0
  bl cache_get
  cmp r0, #0x10000
  blo xf_have
  bl alloc_line
  mov r0, r10
  bl cache_get
  cmp r0, #0x10000
  bhs xf_out
xf_have:
  mov r4, r4, lsr #10
  orr r4, r0, r4, lsl #10
xf_out:
  pop {{r0-r3, r5, r7-r12, lr}}
  bx lr

@ gid_of(r0=page>0, r4=unit) -> r0 = gid (clobbers r1)
gid_of:
  sub r0, r0, #1
  mov r1, r4, lsl #22
  mov r1, r1, lsr #22
  add r0, r1, r0, lsl #10
  bx lr

@ cache_get(r0=gid) -> r0 = cell, or 0x10000 if absent (clobbers r1)
cache_get:
  ldr r1, p_cmap
  mov r0, r0, lsl #1
  ldrh r0, [r1, r0]
  ldr r1, p_ffff
  cmp r0, r1
  moveq r0, #0x10000
  bx lr

@ alloc_line(r6 = first unit): give every uncached char up to the line end an
@ atlas cell, draw it into the RAM atlas and upload the touched 2KB bands.
alloc_line:
  push {{r4-r11, lr}}
  mov r7, r6
  mov r11, #0
al_scan:
  ldrh r4, [r7]
  tst r4, #0x8000
  bne al_upload
  tst r4, #0x4000
  bne al_next
  mov r2, r7
  bl page_of
  cmp r0, #0
  beq al_next
  bl gid_of
  mov r10, r0
  bl cache_get
  cmp r0, #0x10000
  blo al_next
  ldr r3, p_rr
  ldr r5, [r3]
  add r9, r5, #1
  ldr r8, p_npool
  cmp r9, r8
  movhs r9, #0
  str r9, [r3]
  mov r8, r5, lsl #1
  ldr r3, p_owner
  ldrh r9, [r3, r8]
  strh r10, [r3, r8]
  ldr r1, p_ffff
  cmp r9, r1
  ldrne r3, p_cmap
  movne r9, r9, lsl #1
  strhne r1, [r3, r9]
  ldr r3, p_pool
  ldrh r9, [r3, r8]
  ldr r3, p_cmap
  mov r8, r10, lsl #1
  strh r9, [r3, r8]
  mov r0, r10
  bl decode
  ldr r3, p_atlas
  mov r8, r9, lsr #5
  mov r1, #1
  orr r11, r11, r1, lsl r8
  add r3, r3, r8, lsl #11
  and r8, r9, #31
  add r3, r3, r8, lsl #2
  mov r8, #0
al_copy:
  ldr r1, [r0, r8, lsl #2]
  str r1, [r3]
  add r3, r3, #128
  add r8, r8, #1
  cmp r8, #16
  blt al_copy
al_next:
  add r7, r7, #2
  b al_scan
al_upload:
  cmp r11, #0
  beq al_out
  ldr r12, p_gx_begin
  blx r12
  mov r5, #0
al_band:
  mov r1, #1
  tst r11, r1, lsl r5
  beq al_band_next
  ldr r0, p_atlas
  add r0, r0, r5, lsl #11
  mov r1, r5, lsl #11
  mov r2, #0x800
  ldr r12, p_gx_load
  blx r12
al_band_next:
  add r5, r5, #1
  cmp r5, #32
  blt al_band
  ldr r12, p_gx_end
  blx r12
al_out:
  pop {{r4-r11, pc}}

@ resolve(r0=code10, r2=unit ptr) -> r0 = decoded glyph ptr, or 0 for page 0
resolve:
  push {{r4, lr}}
  mov r4, r0
  bl page_of
  cmp r0, #0
  popeq {{r4, pc}}
  sub r0, r0, #1
  add r0, r4, r0, lsl #10
  bl decode
  pop {{r4, pc}}

@ page_of(r2=unit ptr) -> r0 = page 0..3 (clobbers r1, r3, r12)
page_of:
  push {{r4-r6, lr}}
  ldr r3, p_regions
pg_loop:
  ldr r4, [r3], #4
  cmp r4, #0
  beq pg_zero
  ldr r5, [r3], #4
  ldr r6, [r3], #4
  ldr r12, [r3], #4
  ldr r1, [r3], #4
  cmp r2, r4
  blo pg_loop
  cmp r2, r5
  bhs pg_loop
  cmp r12, #0
  beq pg_ok
  ldr r12, [r12]
  cmp r12, r1
  bne pg_loop
pg_ok:
  sub r4, r2, r4
  mov r4, r4, lsr #1
  ldrb r0, [r6, r4, lsr #2]
  and r4, r4, #3
  mov r4, r4, lsl #1
  mov r0, r0, lsr r4
  and r0, r0, #3
  pop {{r4-r6, pc}}
pg_zero:
  mov r0, #0
  pop {{r4-r6, pc}}

@ decode(r0=gid) -> r0 = scratch: 16 rows x u32 of 2bpp (1=ink, 3=shadow)
decode:
  push {{r4-r10, lr}}
  ldr r4, p_font
  ldr r1, p_nres
  cmp r0, r1
  subhs r0, r0, r1
  ldrhs r4, p_font2
  add r0, r0, r0, lsl #3
  add r4, r4, r0, lsl #1
  ldr r5, p_scratch
  ldr r3, p_lut
  ldr r10, p_mask
  mov r6, #0
  mov r7, #0
dc_row:
  sub r1, r6, #2
  cmp r1, #12
  movhs r2, #0
  bhs dc_got
  add r1, r1, r1, lsl #1
  mov r1, r1, lsl #2
  add r12, r4, r1, lsr #3
  ldrb r2, [r12]
  ldrb lr, [r12, #1]
  orr r2, r2, lr, lsl #8
  ldrb lr, [r12, #2]
  orr r2, r2, lr, lsl #16
  and r1, r1, #7
  mov r2, r2, lsr r1
  and r2, r2, r10
dc_got:
  orr r1, r7, r2, lsl #1
  orr r1, r1, r7, lsl #1
  bic r1, r1, r2
  mov r7, r2
  and r12, r2, #15
  ldrb r0, [r3, r12]
  mov r12, r2, lsr #4
  and r12, r12, #15
  ldrb r12, [r3, r12]
  orr r0, r0, r12, lsl #8
  mov r12, r2, lsr #8
  and r12, r12, #15
  ldrb r12, [r3, r12]
  orr r0, r0, r12, lsl #16
  and r12, r1, #15
  ldrb r8, [r3, r12]
  mov r12, r1, lsr #4
  and r12, r12, #15
  ldrb r12, [r3, r12]
  orr r8, r8, r12, lsl #8
  mov r12, r1, lsr #8
  and r12, r12, #15
  ldrb r12, [r3, r12]
  orr r8, r8, r12, lsl #16
  mov r12, r1, lsr #12
  and r12, r12, #15
  ldrb r12, [r3, r12]
  orr r8, r8, r12, lsl #24
  orr r0, r0, r8
  orr r0, r0, r8, lsl #1
  str r0, [r5, r6, lsl #2]
  add r6, r6, #1
  cmp r6, #16
  blt dc_row
  mov r0, r5
  pop {{r4-r10, pc}}

p_regions: .word {L.regions:#x}
p_font: .word {L.font:#x}
p_font2: .word {L.font2:#x}
p_nres: .word {L.n_glyphs}
p_scratch: .word {L.scratch:#x}
p_lut: .word {L.lut:#x}
p_mask: .word 0xfff
p_ffff: .word 0xffff
p_tables: .word {TABLES:#x}
p_font0: .word {FONT0:#x}
p_cmap: .word {L.cmap:#x}
p_pool: .word {L.pool:#x}
p_owner: .word {L.owner:#x}
p_rr: .word {L.rr:#x}
p_npool: .word {L.npool}
p_atlas: .word {ATLAS:#x}
p_gx_begin: .word {GX_BEGIN:#x}
p_gx_load: .word {GX_LOAD:#x}
p_gx_end: .word {GX_END:#x}
p_windows: .word 0x21a0d68
p_win_mask: .word 0x21a1968
p_off2a8: .word 0x2a8
p_off2d0: .word 0x2d0
'''

def spread_lut():
    out = bytearray()
    for n in range(16):
        v = 0
        for b in range(4):
            if n >> b & 1: v |= 1 << (2 * b)
        out.append(v)
    return bytes(out)

def align4(n): return (n + 3) & ~3

class Layout:
    """Places code, tables, ARM9 bitmap and font in the cave."""
    def __init__(self, arm9_bits_len, n_glyphs, pool, n_total=None, font2=0):
        a = CAVE
        self.code = a; self.code_size = 0x600; a += self.code_size
        self.lut = a; a += 16
        self.scratch = a; a += 64
        self.regions = a; a += (MAX_REGIONS + 1) * 20
        self.rr = a; a += 4
        self.pool_cells = list(pool)
        self.npool = len(self.pool_cells)
        self.pool = a; a += align4(2 * self.npool)
        self.owner = a; a += align4(2 * self.npool)
        self.n_glyphs = n_glyphs                 # resident glyphs (gid < n_glyphs)
        self.n_total = n_total or n_glyphs       # all gids (story glyphs live at font2)
        self.font2 = font2
        self.cmap = a; a += align4(2 * max(self.n_total, 1))
        self.arm9_bits = a; a += align4(arm9_bits_len)
        self.font = a; a += n_glyphs * GLYPH_BYTES
        self.end = a
        assert self.end <= CAVE_END, f'cave overflow by {self.end - CAVE_END} bytes'

def apply(arm9, L, regions, arm9_bits, font_bytes, hooks=('get', 'r3', 'grid')):
    """arm9: bytearray (decompressed). regions: list of (start, end, bits_addr, guard_addr, guard_val)."""
    o = lambda addr: addr - BASE
    def put(addr, data): arm9[o(addr):o(addr) + len(data)] = data
    code = asm(code_src(L), L.code)
    assert len(code) <= L.code_size, hex(len(code))
    arm9[o(CAVE):o(CAVE_END)] = bytes(CAVE_END - CAVE)
    put(L.code, code)
    put(L.lut, spread_lut())
    assert len(regions) <= MAX_REGIONS
    put(L.regions, b''.join(struct.pack('<5I', *r) for r in regions) + bytes(20))
    put(L.pool, struct.pack(f'<{L.npool}H', *L.pool_cells))
    put(L.owner, b'\xff\xff' * L.npool)
    put(L.cmap, b'\xff\xff' * L.n_total)
    put(L.arm9_bits, arm9_bits)
    put(L.font, font_bytes)
    entries = [L.code + 4 * i for i in range(4)]
    for site, stub in zip(CALLERS, entries[:2] if 'get' in hooks else []):
        h1, h2 = struct.unpack_from('<HH', arm9, o(site))
        assert (h1 & 0xF800) == 0xF000 and (h2 & 0xF800) == 0xF800, hex(site)
        put(site, thumb_blx(site, stub))
    assert bytes(arm9[o(R3_SITE):o(R3_SITE) + 6]) == bytes.fromhex('8a015e498a18')
    if 'r3' in hooks: put(R3_SITE, thumb_blx(R3_SITE, entries[2]) + bytes.fromhex('c046'))
    assert bytes(arm9[o(GRID_FUNC):o(GRID_FUNC) + 4]) == bytes.fromhex('f0b4041c')
    if 'grid' in hooks:   # thumb `bx pc; nop` then ARM `ldr pc, [pc, #-4]; .word target`
        put(GRID_FUNC, bytes.fromhex('7847c046') + struct.pack('<II', 0xE51FF004, entries[3]))
    return code
