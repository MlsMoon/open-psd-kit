#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared PSD open, layer lookup, and JSON output helpers."""

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
    """Expected open or mutate failure."""


def fail(message: str, code: int = 2) -> None:
    """Raise a catchable tool error. `code` maps to the CLI exit code."""
    error = PsdKitError(message)
    error.exit_code = code
    raise error


def resolve_path(raw: str) -> Path:
    """Resolve a user path. Fail if the file is missing."""
    path = Path(raw)
    if not path.is_file():
        fail(f"file not found: {path}")
    return path


def open_psd(path: Path) -> PSDImage:
    """Open a PSD/PSB and report a useful reason on bad files."""
    try:
        return PSDImage.open(str(path))
    except Exception as exc:  # noqa: BLE001
        fail(f"cannot open PSD: {path}: {exc}")
        raise


def color_mode_name(value: Any) -> str:
    """Convert a ColorMode value or enum to a name."""
    if hasattr(value, "name"):
        return str(value.name)
    return COLOR_MODE_NAMES.get(int(value), str(value))


def blend_mode_name(value: Any) -> str:
    """Convert a blend mode to a readable name."""
    if value is None:
        return ""
    if hasattr(value, "name"):
        return str(value.name)
    return str(value)


def parse_blend_mode(raw: str) -> BlendMode:
    """Parse a user blend-mode name."""
    key = raw.strip().upper().replace("-", "_").replace(" ", "_")
    try:
        return BlendMode[key]
    except KeyError:
        names = ", ".join(item.name for item in BlendMode)
        fail(f"unknown blend mode: {raw}. choices: {names}")
        raise


def layer_kind(layer: Any) -> str:
    """Layer kind, defaulting to unknown."""
    return str(getattr(layer, "kind", "unknown") or "unknown")


def is_pixel_writable(layer: Any) -> bool:
    """Only pixel layers may be used with replace-pixels."""
    return layer_kind(layer) in PIXEL_KINDS and not bool(layer.is_group())


def iter_layers(psd: PSDImage, include_groups: bool = True) -> Iterable[Any]:
    """Walk layers in descendant order."""
    for layer in psd.descendants():
        if layer.is_group() and not include_groups:
            continue
        yield layer


def find_layer(psd: PSDImage, name: str) -> Any:
    """Find the first layer by exact name. Fail if missing."""
    layer = psd.find(name)
    if layer is None:
        fail(f"layer not found: {name}")
    return layer


def layer_record(layer: Any) -> dict[str, Any]:
    """Structured summary for one layer."""
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
    """Document-level summary without pixels."""
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
    """Write UTF-8 JSON to stdout."""
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def emit_inspect_text(record: dict[str, Any]) -> None:
    """Human-readable inspect."""
    print(
        f"{record['kind']} v{record['version']} {record['width']}x{record['height']} "
        f"{record['mode']} {record['depth']}bit layers={record['layer_count']}"
    )
    print(f"path: {record['path']}")


def emit_layers_text(record: dict[str, Any], tree: bool) -> None:
    """Human-readable layer list."""
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
    """Parse a WIDTHxHEIGHT size."""
    parts = raw.lower().replace("*", "x").split("x")
    if len(parts) != 2:
        fail(f"size must be WIDTHxHEIGHT: {raw}")
    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError:
        fail(f"size is not an integer pair: {raw}")
        raise
    if width <= 0 or height <= 0:
        fail(f"size must be positive: {raw}")
    return width, height


def require_out(out: str | None, in_place: bool, source: Path | None) -> Path:
    """Resolve the write path."""
    if in_place:
        if source is None:
            fail("--in-place requires an input file")
        return source
    if not out:
        fail("write requires --out, or an explicit --in-place")
    return Path(out)
