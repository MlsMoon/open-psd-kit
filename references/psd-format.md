# PSD / PSB 格式速查

只写打开文件时要用的判别规则，不展开完整 Photoshop 规范。

## 文件头

- 签名 4 字节：`8BPS`
- 版本 `uint16` 大端：`1` = PSD，`2` = PSB（大文档）
- 随后保留 6 字节零，再是通道数、高度、宽度、位深、颜色模式

本工具用 `psd-tools` 解析，不要手拆后续块。

## 颜色模式

`psd-tools` 的 `ColorMode`：`BITMAP=0`、`GRAYSCALE=1`、`INDEXED=2`、
`RGB=3`、`CMYK=4`、`MULTICHANNEL=7`、`DUOTONE=8`、`LAB=9`。

`inspect` 输出名称而不是数字。导出 PNG 时按文档 `pil_mode` 转换。

## 图层 kind

`psd-tools` 常见 `layer.kind`：

| kind | 含义 | 像素替换 |
|---|---|---|
| `pixel` | 栅格层 | 可以 |
| `group` | 组 | 否 |
| `smartobject` | 智能对象 | 否 |
| `type` | 文字 | 否 |
| `adjustment` | 调整层 | 否 |
| `shape` | 矢量形状 | 否 |
| `fill` | 填充层 | 否 |

属性修改（可见性/不透明度/名称/混合）对大多数层可用。
`replace-pixels` 只接受 `pixel`。

## 不透明度

图层 `opacity` 是 `0..255`，不是百分比。CLI `--opacity` 也用 `0..255`。
