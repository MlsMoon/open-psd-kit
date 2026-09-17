#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""set / replace-pixels / new. Writes go to a new file by default."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer
from psd_tools.constants import Tag

from psd_common import (
    fail,
    find_layer,
    is_pixel_writable,
    open_psd,
    parse_blend_mode,
    parse_size,
    require_out,
    resolve_path,
)


def save_psd(psd: PSDImage, dest: Path) -> None:
    """Save a PSD, creating parent directories as needed."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    psd.save(str(dest))
    print(f"wrote {dest.as_posix()}")


def run_set(
    path: str,
    layer_name: str,
    visible: int | None,
    opacity: int | None,
    new_name: str | None,
    blend: str | None,
    out: str | None,
    in_place: bool,
) -> None:
    """Change one layer's visibility, opacity, name, or blend."""
    source = resolve_path(path)
    dest = require_out(out, in_place, source)
    if visible is None and opacity is None and new_name is None and blend is None:
        fail("set requires --visible / --opacity / --name / --blend")
    psd = open_psd(source)
    layer = find_layer(psd, layer_name)
    if visible is not None:
        layer.visible = bool(visible)
    if opacity is not None:
        if opacity < 0 or opacity > 255:
            fail("--opacity must be 0..255")
        layer.opacity = opacity
    if new_name:
        layer.name = new_name
    if blend:
        layer.blend_mode = parse_blend_mode(blend)
    save_psd(psd, dest)


def run_replace_pixels(
    path: str,
    layer_name: str,
    image_path: str,
    out: str | None,
    in_place: bool,
) -> None:
    """Replace an existing pixel layer with an image."""
    source = resolve_path(path)
    dest = require_out(out, in_place, source)
    image_file = resolve_path(image_path)
    try:
        image = Image.open(image_file)
    except Exception as exc:  # noqa: BLE001
        fail(f"cannot open image: {image_file}: {exc}")
        return
    psd = open_psd(source)
    layer = find_layer(psd, layer_name)
    if not is_pixel_writable(layer):
        fail(f"layer is not pixel-writable: {layer_name} kind={layer.kind}")
    parent = layer.parent if layer.parent is not None else psd
    index = parent.index(layer)
    legacy_name = getattr(getattr(layer, "_record", None), "name", None) or "Layer"
    try:
        legacy_name.encode("mac_roman")
    except UnicodeEncodeError:
        legacy_name = "Layer"
    replacement = PixelLayer.frompil(
        image,
        parent,
        name=legacy_name,
        top=layer.top,
        left=layer.left,
    )
    replacement.visible = layer.visible
    replacement.opacity = layer.opacity
    replacement.blend_mode = layer.blend_mode
    _copy_unicode_layer_name(layer, replacement)
    parent.remove(layer)
    parent.insert(index, replacement)
    save_psd(psd, dest)


def _copy_unicode_layer_name(source: object, dest: object) -> None:
    """Copy the Unicode layer name so save does not encode via mac_roman."""
    source_record = getattr(source, "_record", None)
    dest_record = getattr(dest, "_record", None)
    if source_record is None or dest_record is None:
        return
    blocks = getattr(source_record, "tagged_blocks", None)
    dest_blocks = getattr(dest_record, "tagged_blocks", None)
    if not blocks or dest_blocks is None:
        return
    if Tag.UNICODE_LAYER_NAME in blocks:
        dest_blocks[Tag.UNICODE_LAYER_NAME] = blocks[Tag.UNICODE_LAYER_NAME]


def run_new(size: str, mode: str, out: str | None, fill_name: str) -> None:
    """Create a blank document with one solid pixel layer for self-checks."""
    if not out:
        fail("new requires --out")
    dest = Path(out)
    width, height = parse_size(size)
    color_mode = mode.upper()
    if color_mode not in {"RGB", "RGBA", "L"}:
        fail("new --mode supports RGB / RGBA / L only")
    try:
        psd = PSDImage.new(color_mode, (width, height))
    except Exception as exc:  # noqa: BLE001
        fail(f"cannot create PSD: {exc}")
        return
    fill = (255, 80, 40, 255) if "A" in color_mode else (255, 80, 40)
    if color_mode == "L":
        fill = 200
    image = Image.new(color_mode, (width, height), fill)
    psd.create_pixel_layer(image, name=fill_name)
    save_psd(psd, dest)
