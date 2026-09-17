#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PSD 打开、图层查找与 JSON 输出共用逻辑。"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

from psd_tools import PSDImage
from psd_tools.constants import BlendMode, ColorMode

PIXEL_KINDS = {"pixel"}
COLOR_MODE_NAMES = {item.value: item.name for item in ColorMode}


class PsdKitError(Exception):
    """可预期的打开或操作失败。"""


def fail(message: str, code: int = 2) -> None:
    """抛出可捕获的工具错误。code 留给 CLI 映射退出码。"""
    error = PsdKitError(message)
    error.exit_code = code
    raise error


def resolve_path(raw: str) -> Path:
    """解析用户路径；不存在则失败。"""
    path = Path(raw)
    if not path.is_file():
        fail(f"文件不存在: {path}")
    return path


def open_psd(path: Path) -> PSDImage:
    """打开 PSD/PSB，坏文件给出原因。"""
    try:
        return PSDImage.open(str(path))
    except Exception as exc:  # noqa: BLE001
        fail(f"无法打开 PSD: {path}: {exc}")
        raise


def color_mode_name(value: Any) -> str:
    """把 ColorMode 数值或枚举转成名称。"""
    if hasattr(value, "name"):
        return str(value.name)
    return COLOR_MODE_NAMES.get(int(value), str(value))


def blend_mode_name(value: Any) -> str:
    """混合模式转成可读名。"""
    if value is None:
        return ""
    if hasattr(value, "name"):
        return str(value.name)
    return str(value)


def parse_blend_mode(raw: str) -> BlendMode:
    """解析用户输入的混合模式名。"""
    key = raw.strip().upper().replace("-", "_").replace(" ", "_")
    try:
        return BlendMode[key]
    except KeyError:
        names = ", ".join(item.name for item in BlendMode)
        fail(f"未知混合模式: {raw}。可选: {names}")
        raise


def layer_kind(layer: Any) -> str:
    """图层 kind，缺省为 unknown。"""
    return str(getattr(layer, "kind", "unknown") or "unknown")


def is_pixel_writable(layer: Any) -> bool:
    """只有像素层允许 replace-pixels。"""
    return layer_kind(layer) in PIXEL_KINDS and not bool(layer.is_group())


def iter_layers(psd: PSDImage, include_groups: bool = True) -> Iterable[Any]:
    """按 descendants 顺序遍历图层。"""
    for layer in psd.descendants():
        if layer.is_group() and not include_groups:
            continue
        yield layer


def find_layer(psd: PSDImage, name: str) -> Any:
    """按精确名称找第一层；找不到就失败。"""
    layer = psd.find(name)
    if layer is None:
        fail(f"找不到图层: {name}")
    return layer


def layer_record(layer: Any) -> dict[str, Any]:
    """单层结构化摘要。"""
    bbox = [layer.left, layer.top, layer.right, layer.bottom]
    return {
        "name": layer.name,
        "kind": layer_kind(layer),
        "visible": bool(layer.visible),
        "opacity": int(layer.opacity),
        "blend_mode": blend_mode_name(layer.blend_mode),
        "bbox": bbox,
        "size": [int(layer.width), int(layer.height)],
        "group": bool(layer.is_group()),
        "writable": is_pixel_writable(layer),
    }


def document_record(path: Path, psd: PSDImage) -> dict[str, Any]:
    """文档级结构化摘要，不含像素。"""
    layers = [layer_record(layer) for layer in iter_layers(psd)]
    return {
        "path": path.as_posix(),
        "kind": "psb" if int(psd.version) == 2 else "psd",
        "version": int(psd.version),
        "width": int(psd.width),
        "height": int(psd.height),
        "mode": color_mode_name(psd.color_mode),
        "depth": int(psd.depth),
        "layer_count": len(layers),
        "layers": layers,
    }


def emit_json(payload: Any) -> None:
    """UTF-8 JSON 写到 stdout。"""
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def emit_inspect_text(record: dict[str, Any]) -> None:
    """人类可读 inspect。"""
    print(
        f"{record['kind']} v{record['version']} {record['width']}x{record['height']} "
        f"{record['mode']} {record['depth']}bit layers={record['layer_count']}"
    )
    print(f"path: {record['path']}")


def emit_layers_text(record: dict[str, Any], tree: bool) -> None:
    """人类可读图层列表。"""
    emit_inspect_text(record)
    if not tree:
        return
    for layer in record["layers"]:
        flag = "pixel" if layer["writable"] else layer["kind"]
        vis = "on" if layer["visible"] else "off"
        print(
            f"- {layer['name']} [{flag}] {vis} opacity={layer['opacity']} "
            f"blend={layer['blend_mode']} {layer['size'][0]}x{layer['size'][1]}"
        )


def parse_size(raw: str) -> tuple[int, int]:
    """解析 64x64 尺寸。"""
    parts = raw.lower().replace("*", "x").split("x")
    if len(parts) != 2:
        fail(f"尺寸格式应为 WIDTHxHEIGHT: {raw}")
    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError:
        fail(f"尺寸不是整数: {raw}")
        raise
    if width <= 0 or height <= 0:
        fail(f"尺寸必须为正: {raw}")
    return width, height


def require_out(out: str | None, in_place: bool, source: Path | None) -> Path:
    """决定写回路径。"""
    if in_place:
        if source is None:
            fail("--in-place 需要输入文件")
        return source
    if not out:
        fail("写回必须提供 --out，或显式 --in-place")
    return Path(out)
