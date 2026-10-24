# 株トレーダー瞬 简体中文汉化

Nintendo DS《株トレーダー瞬》（Capcom，2007，AK4J）的非官方简体中文汉化。

- 剧情：4704 条台词全部翻译并逐句校对
- 界面：ARM9 内 2000 余条 UI 字串、对战气泡、人名牌
- 图片：标题 Logo、开机画面、按钮、横幅、交易员卡片（36 张）、教程图解、新闻标题、喊话特效字等全部重绘

## 打补丁

补丁：[`patch/kabushun_zh.bps`](patch/kabushun_zh.bps)（BPS 格式）

原版 ROM 必须是：

| 项目 | 值 |
|---|---|
| 文件 | Kabu Trader Shun (Japan).nds |
| CRC32 | `D5CCB0EE` |
| SHA-1 | `960511cfe060f9ffb899921f7088398c533fb2c4` |

用 [Floating IPS](https://www.romhacking.net/utilities/1040/)、[Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) 等任意支持 BPS 的工具打补丁即可。打好后的 ROM：CRC32 `B2D9EE7D`，SHA-1 `1a434289f20c142a497ce61bf8e945b0455c5595`。

也可以用本仓库的脚本（Python 3）：

```
python tools/mkbps.py   # 生成补丁
```

## 目录

| 路径 | 内容 |
|---|---|
| `text/cn/` | 译文：`ksscv_*.txt` 剧情、`arm9.txt` 界面字串、`bubbles.txt` 对战气泡、`cards.txt` 交易员卡片、`segments.txt` / `sprites_plain.txt` 图片文字 |
| `text/glossary.txt` | 术语与人名对照 |
| `tools/` | 构建工具：`build.py` 总构建，`gfxpatch.py` 全部图片补丁，`engine.py` 字库/文字引擎补丁，`objedit.py` / `bgedit.py` 精灵与背景编辑，`mkbps.py` 补丁生成 |
| `work/` | 校对、测试、宣传片等辅助脚本；`work/fs/` 为解包出的游戏文件 |
| `rom/` | `Kabu Trader Shun (Japan).nds` 原版 ROM、`kabushun_zh.nds` 汉化 ROM |
| `extract/` | 解包数据（ARM9、KSSCV 剧本、图像等） |
| `text/jp/` | 日文原文（剧情与 ARM9 字串） |

构建：`python tools/build.py out/kabushun_zh.nds`（`tools/build.py` 读取 `../downloads/nds-20261019/roms/` 下的原版 ROM，可改 `SRC` 指向 `rom/`）。依赖 Python 3、ndspy、Pillow、numpy。

## 声明

本汉化为爱好者非官方作品，仅供学习交流，与 Capcom、Inti Creates、Nintendo 无关。请支持正版。
