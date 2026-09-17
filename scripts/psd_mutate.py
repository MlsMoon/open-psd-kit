#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""set / replace-pixels / new。默认写到新文件。"""

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
    """保存 PSD，缺目录时创建。"""
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
    """改一层的可见性、不透明度、名称或混合。"""
    source = resolve_path(path)
    dest = require_out(out, in_place, source)
    if visible is None and opacity is None and new_name is None and blend is None:
        fail("set 至少提供 --visible / --opacity / --name / --blend")
    psd = open_psd(source)
    layer = find_layer(psd, layer_name)
    if visible is not None:
        layer.visible = bool(visible)
    if opacity is not None:
        if opacity < 0 or opacity > 255:
            fail("--opacity 必须是 0..255")
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
    """用一张图替换已有像素层。"""
    source = resolve_path(path)
    dest = require_out(out, in_place, source)
    image_file = resolve_path(image_path)
    try:
        image = Image.open(image_file)
    except Exception as exc:  # noqa: BLE001
        fail(f"无法打开图片: {image_file}: {exc}")
        return
    psd = open_psd(source)
    layer = find_layer(psd, layer_name)
    if not is_pixel_writable(layer):
        fail(f"图层不可替换像素: {layer_name} kind={layer.kind}")
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
    """把 Unicode 图层名从原层拷到新像素层，避免 save 走 mac_roman 失败。"""
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
    """新建空白文档并放一层实色像素，便于自检。"""
    if not out:
        fail("new 必须提供 --out")
    dest = Path(out)
    width, height = parse_size(size)
    color_mode = mode.upper()
    if color_mode not in {"RGB", "RGBA", "L"}:
        fail("new --mode 仅支持 RGB / RGBA / L")
    try:
        psd = PSDImage.new(color_mode, (width, height))
    except Exception as exc:  # noqa: BLE001
        fail(f"无法新建 PSD: {exc}")
        return
    fill = (255, 80, 40, 255) if "A" in color_mode else (255, 80, 40)
    if color_mode == "L":
        fill = 200
    image = Image.new(color_mode, (width, height), fill)
    psd.create_pixel_layer(image, name=fill_name)
    save_psd(psd, dest)
