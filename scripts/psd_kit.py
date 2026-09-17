#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""open-psd-kit CLI 入口。实现见 psd_inspect / psd_export / psd_mutate。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from psd_common import PsdKitError  # noqa: E402
from psd_export import run_export  # noqa: E402
from psd_inspect import run_batch_inspect, run_inspect, run_layers  # noqa: E402
from psd_mutate import run_new, run_replace_pixels, run_set  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    """组装子命令。"""
    parser = argparse.ArgumentParser(
        prog="psd_kit.py",
        description="读取并修改 PSD/PSB。默认摘要；--json 输出结构化结果。",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="文档尺寸、模式、层数")
    inspect.add_argument("file")
    inspect.add_argument("--json", action="store_true")

    layers = sub.add_parser("layers", help="图层树")
    layers.add_argument("file")
    layers.add_argument("--tree", action="store_true")
    layers.add_argument("--json", action="store_true")

    export = sub.add_parser("export", help="导出合成或单层 PNG")
    export.add_argument("file")
    export.add_argument("--layer")
    export.add_argument("--out")

    setter = sub.add_parser("set", help="改图层属性并保存")
    setter.add_argument("file")
    setter.add_argument("--layer", required=True)
    setter.add_argument("--visible", type=int, choices=(0, 1))
    setter.add_argument("--opacity", type=int)
    setter.add_argument("--name")
    setter.add_argument("--blend")
    setter.add_argument("--out")
    setter.add_argument("--in-place", action="store_true")

    replace = sub.add_parser("replace-pixels", help="用图片替换像素层")
    replace.add_argument("file")
    replace.add_argument("--layer", required=True)
    replace.add_argument("--image", required=True)
    replace.add_argument("--out")
    replace.add_argument("--in-place", action="store_true")

    new = sub.add_parser("new", help="新建空白 PSD")
    new.add_argument("--size", default="64x64")
    new.add_argument("--mode", default="RGBA")
    new.add_argument("--out", required=True)
    new.add_argument("--layer-name", default="Fill")

    batch = sub.add_parser("batch-inspect", help="目录只读巡检，不合成")
    batch.add_argument("--root", required=True)
    batch.add_argument("--glob", default="*.psd")
    batch.add_argument("--json", action="store_true")
    return parser


def dispatch(args: argparse.Namespace) -> None:
    """按子命令分发。"""
    if args.command == "inspect":
        run_inspect(args.file, args.json)
        return
    if args.command == "layers":
        run_layers(args.file, args.tree, args.json)
        return
    if args.command == "export":
        run_export(args.file, args.layer, args.out)
        return
    if args.command == "set":
        run_set(
            args.file,
            args.layer,
            args.visible,
            args.opacity,
            args.name,
            args.blend,
            args.out,
            args.in_place,
        )
        return
    if args.command == "replace-pixels":
        run_replace_pixels(args.file, args.layer, args.image, args.out, args.in_place)
        return
    if args.command == "new":
        run_new(args.size, args.mode, args.out, args.layer_name)
        return
    if args.command == "batch-inspect":
        run_batch_inspect(args.root, args.glob, args.json)


def main() -> None:
    """CLI 入口。"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args()
    try:
        dispatch(args)
    except PsdKitError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(getattr(exc, "exit_code", 2)) from exc


if __name__ == "__main__":
    main()
