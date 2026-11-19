# -*- coding: utf-8 -*-
"""从 large-files/ 分片重组大文件，逐片与整文件 sha256 校验。

克隆仓库后在仓库根运行（python 不在 PATH，用绝对路径）：
  D:\\software\\python31210\\install\\python.exe scripts\\restore_large_files.py

已存在且校验通过的文件跳过；缺片/校验失败立即报错退出（非 0），不静默。
路径锚到脚本自身位置而非 cwd，从任何目录运行都正确。
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "large-files" / "manifest.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if not MANIFEST.exists():
        print(f"分片清单缺失: {MANIFEST}", file=sys.stderr)
        print("仓库不完整。超过 1 MB 的文件不入库，只能由 large-files/ 分片还原。", file=sys.stderr)
        raise SystemExit(1)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    for file in manifest["files"]:
        target = ROOT / file["target"]
        if target.exists():
            existing = target.read_bytes()
            if len(existing) == file["size"] and sha256(existing) == file["sha256"]:
                print(f"已存在且校验通过: {file['target']}")
                continue

        chunks = []
        for part in file["parts"]:
            part_path = ROOT / part["path"]
            if not part_path.exists():
                raise SystemExit(f"缺少分片: {part['path']}")
            chunk = part_path.read_bytes()
            if len(chunk) != part["size"] or sha256(chunk) != part["sha256"]:
                raise SystemExit(f"分片校验失败: {part['path']}")
            chunks.append(chunk)

        restored = b"".join(chunks)
        if len(restored) != file["size"] or sha256(restored) != file["sha256"]:
            raise SystemExit(f"重组文件校验失败: {file['target']}")

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(restored)
        print(f"已重组: {file['target']} ({len(restored)} 字节)")


if __name__ == "__main__":
    main()