"""Big before/after library for the promo: work/promo/pp/<key>_jp.png / _cn.png (+ sheet work/emu/pp_sheet.png)."""
import sys, os; sys.path.insert(0, 'tools'); sys.path.insert(0, 'work')
import ndspy.rom, objedit, bgedit, numpy as np, wall
from PIL import Image, ImageDraw
R = {'jp': ndspy.rom.NintendoDSRom.fromFile('rom/Kabu Trader Shun (Japan).nds'),
     'cn': ndspy.rom.NintendoDSRom.fromFile('rom/kabushun_zh.nds')}
dat = R['jp'].getFileByName('obj_dat.bin')
OF = {v: objedit.ObjFile(R[v].getFileByName('obj_fnt.bin'), dat) for v in R}
BG = (18, 22, 38)
os.makedirs('work/promo/pp', exist_ok=True)


def spr(v, si, fi):
    idx, own, pal = OF[v].canvas(si, fi)
    rgb = np.zeros(idx.shape + (3,), np.uint8); rgb[:] = BG; m = idx > 0; rgb[m] = pal[idx[m]]
    return Image.fromarray(rgb)


def bg(v, name, mi, ts=None):
    bf = bgedit.BgFile(R[v].getFileByName(name)); m = bf.maps[mi]
    if ts is None:
        mx = int((m & 0x3FF).max()); ts = next(t for t in range(len(bf.tiles)) if len(bf.tiles[t]) // 64 > mx)
    c = bf.canvas(mi, ts, (0, 0, m.shape[1], m.shape[0]))
    return Image.fromarray(bf.pal[min(ts, len(bf.pal) - 1)][c].astype(np.uint8))


def bg4(v, name, mi):
    """4bpp map with palette banks (boot.bin)."""
    bf = bgedit.BgFile(R[v].getFileByName(name))
    pal = np.frombuffer(bf.pals_raw[0], '<u2').astype(int)
    pal = np.stack([(pal & 31) * 255 // 31, ((pal >> 5) & 31) * 255 // 31, ((pal >> 10) & 31) * 255 // 31], -1).astype(np.uint8)
    raw = bytes(bf.tiles[0]); m = bf.maps[mi]; img = np.zeros((192, 256), int)
    for cy in range(24):
        for cx in range(32):
            e = int(m[cy, cx]); t = e & 0x3FF; b = np.frombuffer(raw[t * 32:t * 32 + 32], np.uint8)
            img[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8] = np.stack([b & 15, b >> 4], 1).reshape(8, 8) + 16 * (e >> 12)
    return Image.fromarray(pal[img])


def wallimg(v, name, crop=None):
    open('work/emu/_w.bin', 'wb').write(R[v].getFileByName(name)); img, rgb = wall.load('work/emu/_w.bin')
    im = Image.fromarray(rgb[img]); return im.crop(crop) if crop else im.crop((0, 0, 256, 192))


def stack(ims, cols=1, gap=4):
    rows = [ims[i:i + cols] for i in range(0, len(ims), cols)]
    W = max(sum(i.width for i in r) + gap * (len(r) - 1) for r in rows); H = sum(max(i.height for i in r) for r in rows) + gap * (len(rows) - 1)
    S = Image.new('RGB', (W, H), BG); y = 0
    for r in rows:
        x = 0
        for i in r: S.paste(i, (x, y)); x += i.width + gap
        y += max(i.height for i in r) + gap
    return S


LIB = [
    ('boot', '开机注意事项', lambda v: bg4(v, 'boot.bin', 2)),
    ('title', '标题 Logo', lambda v: bg(v, 'title2.bin', 0)),
    ('card1', '交易员卡片', lambda v: spr(v, 614, 5)),
    ('card2', '交易员卡片', lambda v: spr(v, 543, 0)),
    ('card3', '交易员卡片', lambda v: spr(v, 615, 1)),
    ('cardlogo', '卡片收集画面', lambda v: bg(v, 'view_bg.bin', 1)),
    ('ranking', '交易记录', lambda v: bg(v, 'ranking.bin', 0)),
    ('result', '交易结果', lambda v: bg(v, 'result00.bin', 0, 1)),
    ('trdset', '交易准备', lambda v: bg(v, 'trdset00.bin', 2, 0)),
    ('subinfo', '状态画面', lambda v: bg(v, 'sub_info.bin', 0, 0)),
    ('trial', '试炼模式', lambda v: bg(v, 'trial_bg.bin', 2, 1)),
    ('news1', '新闻标题', lambda v: bg(v, 'mi00.bin', 0)),
    ('news2', '新闻标题', lambda v: bg(v, 'ma00.bin', 0)),
    ('wall', '交易画面底屏', lambda v: wallimg(v, 'bged00.bin')),
    ('trials', '试炼标题', lambda v: stack([spr(v, 538, f) for f in (3, 4, 5, 6)])),
    ('menus', '菜单按钮', lambda v: stack([spr(v, 512, f) for f in (3, 7, 8, 9)])),
    ('tabs', '标签页', lambda v: stack([spr(v, 602, f) for f in (0, 1, 7, 9)])),
    ('confirm', '确认条', lambda v: stack([spr(v, 232, f) for f in (3, 4, 5)])),
    ('shouts', '买卖喊话', lambda v: stack([spr(v, 407, 2), spr(v, 409, 4), spr(v, 407, 9)])),
    ('ta', '交易技特效字', lambda v: stack([spr(v, 411, 1), spr(v, 411, 3), spr(v, 413, 3), spr(v, 413, 4)])),
    ('banner', '横幅', lambda v: stack([spr(v, 503, 5), spr(v, 671, 0), spr(v, 505, 0)])),
    ('touch', '小游戏提示', lambda v: stack([spr(v, 181, 0), spr(v, 216, 0), spr(v, 216, 8), spr(v, 646, 0)], 2)),
    ('tut1', '教程图解', lambda v: spr(v, 607, 7)),
    ('tut2', '教程图解', lambda v: spr(v, 672, 1)),
    ('contract', '签约名单', lambda v: stack([spr(v, 186, f) for f in (2, 3, 4, 5, 6, 7)], 2)),
    ('bubbles', '对战气泡', lambda v: stack([spr(v, 548, 0), spr(v, 551, 2), spr(v, 566, 1)])),
    ('names', '人名与提示', lambda v: stack([spr(v, 643, 0), spr(v, 643, 2), spr(v, 437, 0), spr(v, 2, 13)])),
    ('stocks', '股票名', lambda v: stack([spr(v, 612, f) for f in range(2, 14)], 3)),
]
if __name__ == '__main__':
    tiles = []
    for k, label, fn in LIB:
        try:
            a, b = fn('jp'), fn('cn')
        except Exception as e:
            print('FAIL', k, e); continue
        a.save(f'work/promo/pp/{k}_jp.png'); b.save(f'work/promo/pp/{k}_cn.png')
        pair = stack([a, b], 2, 6); d = ImageDraw.Draw(pair); d.text((2, 2), k, fill=(255, 255, 0)); tiles.append(pair)
        print(k, a.size)
    th = []
    for t in tiles:
        t = t.copy(); t.thumbnail((470, 200)); th.append(t)
    S = Image.new('RGB', (960, 210 * ((len(th) + 1) // 2)), (0, 0, 0))
    for i, t in enumerate(th): S.paste(t, ((i % 2) * 480, (i // 2) * 210))
    S.save('work/emu/pp_sheet.png')
