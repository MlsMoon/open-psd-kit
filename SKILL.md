---
name: open-psd-kit
description: >
  读取并修改 PSD/PSB 图层与像素。涵盖图层树、合成导出、可见性/不透明度/
  混合模式、像素层替换与安全写回。适用于检查 Photoshop 文件、导出单层、
  改贴图图层，或用户说“读一下这个 psd”、“把这层关掉再存”。
  禁止把宿主工程路径写进本 skill。
license: MIT
metadata:
  author: MlsMoon
  version: "1.0"
  compatibility: Requires Python 3.9+, psd-tools and Pillow.
---

# PSD：读取与修改

> 通用 Agent Skill：用开源 `psd-tools` 读/改 PSD 与 PSB。不绑定任何游戏项目。

## 1. 何时使用

- 用户提到 `.psd` / `.psb`、图层、合成导出、Emissive 贴图源文件
- 需要改可见性、不透明度、混合模式或替换像素层
- 禁止手改二进制 PSD，禁止调用本机 Photoshop 或商业 Aspose

先读 [写回边界](references/write-limits.md)。格式见 [PSD 速查](references/psd-format.md)。

## 2. 使用流程

| 需求 | 命令 | 输出 |
|---|---|---|
| 看尺寸/模式/层数 | `scripts/psd_kit.py inspect FILE` | 摘要或 `--json` |
| 看图层树 | `scripts/psd_kit.py layers FILE --tree` | 名称/类型/可写 |
| 导出合成或单层 | `scripts/psd_kit.py export FILE --out out.png` | PNG |
| 改图层属性 | `scripts/psd_kit.py set FILE --layer NAME --out out.psd` | 新 PSD |
| 替换像素层 | `scripts/psd_kit.py replace-pixels FILE --layer NAME --image in.png --out out.psd` | 新 PSD |
| 新建空白文档 | `scripts/psd_kit.py new --size 64x64 --mode RGBA --out out.psd` | 新 PSD |
| 批量只读巡检 | `scripts/psd_kit.py batch-inspect --root DIR --glob "*.psd"` | 摘要或 `--json` |

**约定**：默认摘要；`--json` 走 stdout（UTF-8）；失败退出码非 0 且 stderr 给原因。
批量默认不合成。写回默认到新文件；`--in-place` 必须显式。
单个 `.py` 约 250 行；入口是 `psd_kit.py`。

试错不能只留在对话里。门禁见 [references/self-iteration.md](references/self-iteration.md)。

本轮出现以下任一情况，收尾前必须跑升格门禁：

- 执行了 >=3 次 `psd_kit.py`
- 同一旗标族失败或改参后重试 >=2 次
- 用临时 Python 完成了本可变成一等旗标的能力

同一旗标族连续失败 2 次后，第三次之前必须重读本 skill 或 `--help`。
过门禁后选唯一落点：正式 CLI 旗标、`references/` 口径、或本 `SKILL.md` 用法。
授权：门禁通过后可直接回写本 skill。禁止写入宿主工程路径或业务资产名。
收尾必须输出「PSD 读写自我迭代」四行报告；未触发则写「本轮未触发 PSD 读写升格」。

## 3. 保证范围

| 能做 | 不能保证 |
|---|---|
| 读文档头、图层树、像素层像素 | 智能对象内容完整往返 |
| 改可见性 / 不透明度 / 名称 / 混合 | 实时文字引擎 |
| 替换或新增像素层后 `save` | 复杂图层样式、矢量形状 |

`writable=false` 的层只允许改属性，不能 `replace-pixels`。

## 4. 依赖

```bash
pip install -r requirements.txt
```

需要 Python 3.9+、`psd-tools`（含 composite 额外依赖）和 Pillow。

## 5. 示例

```bash
python scripts/psd_kit.py inspect assets/sample.psd
python scripts/psd_kit.py inspect assets/sample.psd --json
python scripts/psd_kit.py layers assets/sample.psd --tree
python scripts/psd_kit.py export assets/sample.psd --out out.png
python scripts/psd_kit.py export assets/sample.psd --layer Fill --out fill.png
python scripts/psd_kit.py set assets/sample.psd --layer Fill --visible 0 --out hidden.psd
python scripts/psd_kit.py replace-pixels assets/sample.psd --layer Fill --image patch.png --out patched.psd
python scripts/psd_kit.py new --size 64x64 --mode RGBA --out blank.psd
python scripts/psd_kit.py batch-inspect --root ./assets --glob "*.psd" --json
```

## 6. 检查清单

- [ ] 已 `pip install -r requirements.txt`
- [ ] 先 `inspect` / `layers`，再决定 export 还是写回
- [ ] 写回默认 `--out`，未获准不使用 `--in-place`
- [ ] 像素替换只打在 `kind=pixel` 且 `writable=true` 的层
- [ ] 批量巡检未对超大文件做 composite
- [ ] 公开仓文本没有宿主工程绝对路径或业务资产名
