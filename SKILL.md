---
name: open-psd-kit
description: >
  Read and modify PSD/PSB layers and pixels. Covers layer trees, composite
  export, visibility/opacity/blend, pixel-layer replace, and safe writes.
  Use when inspecting Photoshop files, exporting a layer, editing a texture
  layer, or the user says "read this psd" / "hide this layer and save".
  After repeated psd_kit trials, self-iterate official CLI flags instead
  of leaving ad-hoc Python in chat. Never write host-project paths into
  this skill.
license: MIT
metadata:
  author: MlsMoon
  version: "1.1"
  compatibility: Requires Python 3.9+, psd-tools and Pillow.
---

# PSD: Read and Modify

> Generic agent skill: read and write PSD/PSB with open-source `psd-tools`.
> Not tied to any game project.

## 1. When to use

- The user mentions `.psd` / `.psb`, layers, composite export, or emissive sources
- Visibility, opacity, blend mode, or pixel-layer replacement is required
- Do not hand-edit binary PSD. Do not call local Photoshop or commercial Aspose

Read [write limits](references/write-limits.md) first. Format notes:
[PSD cheat sheet](references/psd-format.md).

## 2. Workflow

| Need | Command | Output |
|---|---|---|
| Size / mode / layer count | `scripts/psd_kit.py inspect FILE` | Summary or `--json` |
| Layer tree | `scripts/psd_kit.py layers FILE --tree` | Name / kind / writable |
| Composite or single layer | `scripts/psd_kit.py export FILE --out out.png` | PNG |
| Edit layer properties | `scripts/psd_kit.py set FILE --layer NAME --out out.psd` | New PSD |
| Replace a pixel layer | `scripts/psd_kit.py replace-pixels FILE --layer NAME --image in.png --out out.psd` | New PSD |
| Create a blank document | `scripts/psd_kit.py new --size 64x64 --mode RGBA --out out.psd` | New PSD |
| Stack images as layers | `scripts/psd_kit.py stack --layer BC=bc.png --layer Mask=mask.png --out out.psd` | New PSD |
| Read-only batch scan | `scripts/psd_kit.py batch-inspect --root DIR --glob "*.psd"` | Summary or `--json` |

**Contract**: human summary by default; `--json` on UTF-8 stdout; non-zero
exit on failure with the reason on stderr. Batch inspect never composites.
Writes go to a new file; `--in-place` must be explicit. Keep each `.py` near
250 lines. Entry point is `psd_kit.py`.

Do not leave retries only in chat. Protocol, gate, skip rules, landing,
and authorization: [references/self-iteration.md](references/self-iteration.md).

Run the gate before wrap-up if any of these happened this turn:

- `psd_kit.py` ran 3 or more times
- The same flag family failed or was retried 2 or more times
- Ad-hoc Python did work that should become a first-class flag
- This skill or `--help` disagrees with the actual CLI result

After 2 failures in the same flag family, reread this skill or `--help`
before a third try. A passed gate may update this skill's `SKILL.md`,
`references/`, and `scripts/` directly. Never write host-project paths
or asset names.

Wrap-up must print the four-line "PSD read/write self-iteration" report.
If the gate did not fire, write "No PSD read/write promotion this turn."

## 3. Guaranteed scope

| Supported | Not guaranteed |
|---|---|
| Document header, layer tree, pixel-layer pixels | Smart-object payload round-trip |
| Visibility / opacity / name / blend | Live type engine |
| Replace or add a pixel layer, then `save` | Complex layer styles, vector shapes |

`writable=false` layers may get property edits only. Do not `replace-pixels`.

## 4. Dependencies

```bash
pip install -r requirements.txt
```

Requires Python 3.9+, `psd-tools` (with composite extras), and Pillow.

## 5. Examples

```bash
python scripts/psd_kit.py inspect assets/sample.psd
python scripts/psd_kit.py inspect assets/sample.psd --json
python scripts/psd_kit.py layers assets/sample.psd --tree
python scripts/psd_kit.py export assets/sample.psd --out out.png
python scripts/psd_kit.py export assets/sample.psd --layer Fill --out fill.png
python scripts/psd_kit.py set assets/sample.psd --layer Fill --visible 0 --out hidden.psd
python scripts/psd_kit.py replace-pixels assets/sample.psd --layer Fill --image patch.png --out patched.psd
python scripts/psd_kit.py new --size 64x64 --mode RGBA --out blank.psd
python scripts/psd_kit.py stack --layer BC=bc.png --layer Mask=mask.png --out stacked.psd
python scripts/psd_kit.py batch-inspect --root ./assets --glob "*.psd" --json
```

## 6. Checklist

- [ ] `pip install -r requirements.txt` is done
- [ ] `inspect` / `layers` first, then export or write
- [ ] Writes use `--out`; `--in-place` only when approved
- [ ] Pixel replace targets `kind=pixel` and `writable=true`
- [ ] Batch inspect did not composite huge files
- [ ] Public-repo text has no host-project paths or asset names
- [ ] Self-iteration gate was judged; a passed attempt used one landing
