# Write limits

`psd-tools` can `save`, but it does not clone Photoshop. Pick commands from
this table.

## Guaranteed

- Read the document header and layer tree
- Export a pixel layer with `topil` or the document with `composite`
- Save after changing `visible`, `opacity`, `name`, or `blend_mode`
- Save after replacing or adding a pixel layer from a Pillow image

Write to `--out` by default. Add `--in-place` only when the user asks to
overwrite the source file.

## Not guaranteed

- Smart-object inner-document round-trip
- Live type (fonts, paragraphs, warps)
- Full layer-style writeback (shadow, stroke, gradient overlay)
- Vector shape paths and effects
- Visual match for 16/32-bit depth and every blend mode

Those layers are marked `writable=false` in `layers` output.
`replace-pixels` must fail on them and report the kind.

## Suggested order

1. Run `inspect` and `layers --tree` first
2. `export` only when a picture is needed; never composite in batch
3. Use `set` for properties and `replace-pixels` for pixels
4. `inspect` again after save and compare names, visibility, and size
5. When replacing pixels, keep the original Pascal name and Unicode name
   so non-ASCII layer names do not fail `mac_roman` encode on save
