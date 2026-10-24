"""Build the Chinese ROM: python tools/build.py [out.nds]

Inputs: original ROM, text/cn/arm9.txt (UI strings, in place) and
text/cn/ksscv.txt (story).  Missing translations keep the Japanese units.
"""
import hashlib, struct, sys
from pathlib import Path
import ndspy.rom, ndspy.codeCompression as cc

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine, cnfont, gfxpatch, nameplates
from textenc import Charset, Encoder
from build_ksscv import build as build_ksscv, parse
from arm9text import BLOCKS, lines as arm9_lines

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT.parent / 'downloads/nds-20261019/roms/Kabu Trader Shun (Japan).nds'
SHA = '115b58a5f2b2f8a61c4d541c1abccfbe06b3a681188f3cf1caafe6d3b6353e56'
KS_GUARD = (0x22B4000, 0x022B4028)

def parse_arm9(path):
    out, cur = {}, None
    if not Path(path).exists(): return out
    for raw in Path(path).read_text(encoding='utf8').split('\n'):
        if raw.startswith('@'):
            cur = int(raw[1:].split()[0], 16)
        elif cur is not None and raw.strip():
            out[cur] = raw; cur = None
    return out

def keep_glyphs(arm9, orig9, slots, cn9, L, report):
    """Kanji glyphs still used by untranslated ARM9 strings (e.g. the number-format charset
    '月倍日') sit in the cave; copy their original bitmaps to free slots at the top of the old
    kanji area and repoint both code->glyph tables."""
    o = lambda a: a - engine.BASE
    tabs = [struct.unpack_from('<I', orig9, o(engine.TABLES) + 4 * i)[0] for i in range(2)]
    T = [list(struct.unpack_from('<1024H', orig9, o(t))) for t in tabs]
    need = set()
    for addr, (units, term) in slots.items():
        if addr in cn9: continue
        for u in units:
            if u & 0x4000: continue
            for t in T:
                g = t[u & 0x3FF]
                if engine.KEEP_GLYPHS <= g < 1213: need.add(g)
    slot = 1212
    moved = {}
    for g in sorted(need):
        while engine.FONT0 + slot * 64 < L.end: raise AssertionError('no free glyph slot')
        arm9[o(engine.FONT0 + slot * 64):o(engine.FONT0 + slot * 64) + 64] = orig9[o(engine.FONT0 + g * 64):o(engine.FONT0 + g * 64) + 64]
        moved[g] = slot; slot -= 1
    for ti, t in enumerate(tabs):
        for c in range(1024):
            if T[ti][c] in moved: struct.pack_into('<H', arm9, o(t) + 2 * c, moved[T[ti][c]])
    report.append(f'kept {len(moved)} original kanji glyphs for untranslated strings')


def main(out_path):
    data = SRC.read_bytes()
    assert hashlib.sha256(data).hexdigest() == SHA
    rom = ndspy.rom.NintendoDSRom(data)
    arm9 = bytearray(cc.decompress(rom.arm9))
    orig9 = bytes(arm9)
    struct.pack_into('<I', arm9, 0xB68 + 0x14, 0)          # module params: compressed_static_end = 0
    problems = []
    report_extra = []
    cs = Charset()

    # --- ARM9 UI strings, in place (allocated first -> resident glyphs) ---
    enc0 = Encoder('both', cs)
    cn9 = parse_arm9(ROOT / 'text/cn/arm9.txt')
    # identical to the Japanese (either reading): keep the original units, so strings the game
    # copies into work buffers (losing our page bits) still resolve to the right glyph
    jp9 = {}
    cur = None
    for line in (ROOT / 'text/jp/arm9.txt').read_text(encoding='utf8').splitlines():
        if line.startswith('@'): cur = int(line.split()[0][1:], 16); jp9[cur] = set(); continue
        if cur is not None: jp9[cur].add(line[1:] if line.startswith('#') else line)
    same = [a for a, t in cn9.items() if t in jp9.get(a, ())]
    for a in same: del cn9[a]
    report_extra.append(f'arm9: {len(same)} strings identical to Japanese left as is')
    slots = {addr: (units, term) for addr, units, term in arm9_lines(arm9)}
    block_pages = {b: [0] * ((b[1] - b[0]) // 2) for b in BLOCKS}
    for addr, text in cn9.items():
        if addr not in slots: problems.append(f'arm9 {addr:x}: no such line'); continue
        units, term = slots[addr]
        if len(units) == 1 and addr % 4 == 2 and units[0] >> 8 in (1, 2, 3):
            problems.append(f'arm9 {addr:x}: looks like the high half of a pointer, skipped'); continue
        center = text.startswith('=')              # '=' prefix: centre within the original width
        u, p, n = enc0.encode(text[1:] if center else text)
        room = len(units)
        if len(u) > room: problems.append(f'arm9 {addr:x}: {len(u)} > {room}: {text}'); continue
        pad = room - len(u)
        left = pad // 2 if center else 0
        sp = enc0.page0['　']
        u = [sp] * left + u + [sp] * (pad - left); p = [0] * left + p + [0] * (pad - left); n += pad
        o = addr - engine.BASE
        struct.pack_into(f'<{room + 1}H', arm9, o, *u, 0x8000 | (term & 0x7800) | n)
        blk = next(b for b in BLOCKS if b[0] <= addr < b[1])
        for i, pg in enumerate(p):
            block_pages[blk][(addr - blk[0]) // 2 + i] = pg
    n_res = len(cs.chars)

    # --- KSSCV story text ---
    ks_orig = rom.getFileByName('KSSCV.bin')
    ks = build_ksscv(ks_orig, ROOT / 'text/cn', cs, problems, stub_untranslated='--stub' in sys.argv)
    story_font = cnfont.build(cs.chars[n_res:])
    ks_data = ks['data'] + bytes(-len(ks['data']) % 4)
    font2 = 0x22B4000 + len(ks_data)
    ks_data += story_font
    if len(ks_data) > len(ks_orig):
        problems.append(f'KSSCV grew: {len(ks_data)} > {len(ks_orig)} (+{len(ks_data) - len(ks_orig)})')
    rom.setFileByName('KSSCV.bin', ks_data)

    # --- graphic text ---
    gfx_report = []
    gfxpatch.apply(rom, gfx_report)

    # --- engine ---
    bits = bytearray()
    regions = []
    blk_bits = []
    for b in BLOCKS:
        pg = block_pages[b]
        bb = bytearray((len(pg) + 3) // 4)
        for i, x in enumerate(pg): bb[i // 4] |= x << ((i % 4) * 2)
        blk_bits.append(bytes(bb))
    # never recycle: page-0 codes the text uses, the special-glyph/icon row (incl. the page arrow
    # frames at 316-319) and every built-in kana/punctuation cell
    reserved = set(ks['page0_codes']) | {0} | set(range(256, 320)) | set(enc0.page0.values())
    pool = [c for c in range(1024) if c not in reserved]
    L = engine.Layout(sum(engine.align4(len(x)) for x in blk_bits), n_res, pool,
                      n_total=len(cs.chars), font2=font2)
    a = L.arm9_bits
    for b, bb in zip(BLOCKS, blk_bits):
        regions.append((b[0], b[1], a, 0, 0)); bits += bb + bytes(-len(bb) % 4); a += engine.align4(len(bb))
    if ks['any_cn']:
        regions.append((ks['pool_start'], ks['pool_end'], ks['bits_addr'], *KS_GUARD))
    engine.apply(arm9, L, regions, bytes(bits), cnfont.build(cs.chars[:n_res]))
    keep_glyphs(arm9, orig9, slots, cn9, L, report_extra)
    nameplates.apply(arm9, report_extra)
    # recompress (BLZ): uncompressed ARM9 pushes the ROM past its 32 MB capacity and the tail files wrap
    comp = bytearray(cc.compress(bytes(arm9), isArm9=True))
    struct.pack_into('<I', comp, 0xB68 + 0x14, engine.BASE + len(comp))
    assert cc.decompress(bytes(comp)) [0x4000:] == bytes(arm9)[0x4000:]
    # pad to a fixed size so the ROM layout (and savestates) survive ARM9 tweaks;
    # the padding lies inside the decompressed area and is overwritten at boot
    ARM9_FIXED = 0xB8000
    assert len(comp) <= ARM9_FIXED, f'arm9 {len(comp):#x} > {ARM9_FIXED:#x}'
    rom.arm9 = bytes(comp) + bytes(ARM9_FIXED - len(comp))
    rom.saveToFile(out_path)
    size = Path(out_path).stat().st_size
    if size > 128 * 1024 << rom.deviceCapacity:
        problems.append(f'ROM {size:#x} exceeds device capacity {128 * 1024 << rom.deviceCapacity:#x}')

    report = [f'glyphs: resident {n_res}, story {len(cs.chars) - n_res}, total {len(cs.chars)}',
              f'cave used {L.end - engine.CAVE} / {engine.CAVE_END - engine.CAVE}',
              f'KSSCV {len(ks_data)} / {len(ks_orig)}', f'3D pool cells {len(pool)}'] + report_extra + gfx_report
    print('\n'.join(report))
    if problems:
        print(f'{len(problems)} problems:'); print('\n'.join(problems[:80]))
    (ROOT / 'work/build_report.txt').write_text('\n'.join(report + problems), encoding='utf8')

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    main(args[0] if args else str(ROOT / 'out/kabushun_zh.nds'))
