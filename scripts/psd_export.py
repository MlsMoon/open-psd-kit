#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export a flattened composite or a single-layer PNG."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from psd_common import fail, find_layer, is_pixel_writable, open_psd, resolve_path


def save_image(image: Image.Image, dest: Path) -> None:
    """Save a PNG, creating parent directories as needed."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest)


def run_export(path: str, layer_name: str | None, out: str | None) -> None:
    """export subcommand."""
    if not out:
        fail("export requires --out")
    dest = Path(out)
    psd = open_psd(resolve_path(path))
    try:
        if layer_name:
            layer = find_layer(psd, layer_name)
            image = layer.topil() if is_pixel_writable(layer) else layer.composite()
        else:
            image = psd.composite()
    except Exception as exc:  # noqa: BLE001
        fail(f"export failed: {exc}")
        return
    if image is None:
        fail("export produced an empty image")
    save_image(image, dest)
    print(f"wrote {dest.as_posix()} {image.size[0]}x{image.size[1]}")
