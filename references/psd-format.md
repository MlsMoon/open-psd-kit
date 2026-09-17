# PSD / PSB cheat sheet

Only the rules needed to open a file. This is not a full Photoshop spec.

## File header

- Signature: 4 bytes `8BPS`
- Version: big-endian `uint16`; `1` = PSD, `2` = PSB (large document)
- Then 6 reserved zero bytes, channel count, height, width, depth, color mode

This tool parses with `psd-tools`. Do not hand-split later blocks.

## Color mode

`psd-tools` `ColorMode`: `BITMAP=0`, `GRAYSCALE=1`, `INDEXED=2`,
`RGB=3`, `CMYK=4`, `MULTICHANNEL=7`, `DUOTONE=8`, `LAB=9`.

`inspect` prints the name, not the number. PNG export follows document
`pil_mode`.

## Layer kind

Common `layer.kind` values from `psd-tools`:

| kind | Meaning | Pixel replace |
|---|---|---|
| `pixel` | Raster layer | Yes |
| `group` | Group | No |
| `smartobject` | Smart object | No |
| `type` | Type / text | No |
| `adjustment` | Adjustment | No |
| `shape` | Vector shape | No |
| `fill` | Fill | No |

Property edits (visibility / opacity / name / blend) work on most layers.
`replace-pixels` accepts `pixel` only.

## Opacity

Layer `opacity` is `0..255`, not a percent. CLI `--opacity` uses `0..255`.
