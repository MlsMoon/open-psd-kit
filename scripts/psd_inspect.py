#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inspect / layers / batch-inspect。批量默认不合成。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from psd_common import (
    PsdKitError,
    document_record,
    emit_inspect_text,
    emit_json,
    emit_layers_text,
    fail,
    open_psd,
    resolve_path,
)


def inspect_file(path: Path) -> dict[str, Any]:
    """打开一份 PSD 并返回文档摘要。"""
    psd = open_psd(path)
    return document_record(path, psd)


def run_inspect(path: str, as_json: bool) -> None:
    """inspect 子命令。"""
    record = inspect_file(resolve_path(path))
    if as_json:
        emit_json(record)
        return
    emit_inspect_text(record)


def run_layers(path: str, tree: bool, as_json: bool) -> None:
    """layers 子命令。"""
    record = inspect_file(resolve_path(path))
    if as_json:
        emit_json(record)
        return
    emit_layers_text(record, tree=tree)


def collect_files(root: Path, pattern: str) -> list[Path]:
    """按 glob 收集文件，跳过常见缓存目录。"""
    skip = {".git", "Library", "PackageCache", "__pycache__", "node_modules"}
    files: list[Path] = []
    for path in root.rglob(pattern):
        if not path.is_file():
            continue
        if any(part in skip for part in path.parts):
            continue
        files.append(path)
    files.sort()
    return files


def run_batch_inspect(root: str, pattern: str, as_json: bool) -> None:
    """只读巡检目录，不 composite。"""
    base = Path(root)
    if not base.is_dir():
        fail(f"目录不存在: {base}")
    results: list[dict[str, Any]] = []
    failures = 0
    for path in collect_files(base, pattern):
        try:
            record = inspect_file(path)
            record["ok"] = True
            results.append(record)
        except PsdKitError as exc:
            failures += 1
            results.append({"path": path.as_posix(), "ok": False, "error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            failures += 1
            results.append({"path": path.as_posix(), "ok": False, "error": str(exc)})
    payload = {
        "root": base.as_posix(),
        "glob": pattern,
        "count": len(results),
        "failed": failures,
        "files": results,
    }
    if as_json:
        emit_json(payload)
        return
    print(f"batch {payload['count']} files, failed={failures}, root={base}")
    for item in results:
        if item.get("ok"):
            print(
                f"OK {item['width']}x{item['height']} {item['mode']} "
                f"layers={item['layer_count']} {item['path']}"
            )
        else:
            print(f"FAIL {item['path']}: {item.get('error')}")
    if failures:
        raise SystemExit(1)
