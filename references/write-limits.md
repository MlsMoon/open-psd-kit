# 写回边界

`psd-tools` 可以 `save`，但不能完整复刻 Photoshop。按这个表选命令。

## 保证

- 读取文档头与图层树
- 像素层 `topil` / 文档 `composite` 导出 PNG
- 改 `visible`、`opacity`、`name`、`blend_mode` 后保存
- 用 Pillow 图替换或新增像素层后保存

默认写到 `--out`。只有用户明确要求覆盖原文件时才加 `--in-place`。

## 不保证

- 智能对象内部文档往返
- 实时文字（字体、段落、变形）
- 图层样式（投影、描边、渐变叠加）完整写回
- 矢量形状路径与效果
- 16/32 位深度与全部混合模式的视觉一致

这些层在 `layers` 输出里标 `writable=false`。
对它们执行 `replace-pixels` 必须失败并说明 kind。

## 操作建议

1. 先 `inspect` 和 `layers --tree`
2. 需要看画面时再 `export`，不要在 batch 里合成
3. 改属性用 `set`；改画面用 `replace-pixels`
4. 保存后再次 `inspect` 对照层名、可见性和尺寸
5. 替换像素层时保留原层的 Pascal 名和 Unicode 名，避免中文层名按 mac_roman 写回失败
