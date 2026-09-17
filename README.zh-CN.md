# open-psd-kit

[English](README.md) · [简体中文](README.zh-CN.md)

教 AI 读取和修改 Photoshop PSD / PSB 的 [Agent Skill](https://agentskills.io/specification)。

本仓库**就是** skill 目录。目录名、GitHub 仓名和 `SKILL.md` 的 `name` 必须保持 `open-psd-kit`。

## 做什么

不要手改 PSD 二进制，也不要依赖本机 Photoshop。本 skill 用开源 [psd-tools](https://github.com/psd-tools/psd-tools) 提供稳定 CLI：inspect、图层树、导出、改属性、替换像素层。

不绑定任何游戏项目。

## 命令

见英文 README 表格，或 `python scripts/psd_kit.py -h`。

默认人类可读摘要，`--json` 输出 UTF-8 结构化结果。失败非 0，原因在 stderr。
写回默认到新文件；`--in-place` 必须显式。批量巡检不合成。

样例：`assets/sample.psd`（由本工具生成）。

```bash
pip install -r requirements.txt
python scripts/psd_kit.py inspect assets/sample.psd
```

保证范围：像素层属性 + 像素替换。智能对象、实时文字、复杂样式不保证往返。

## 许可

MIT。见 `LICENSE` 与 `NOTICE`。
