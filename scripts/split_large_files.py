# -*- coding: utf-8 -*-
"""把超过 1 MB 的大文件拆成 900,000 字节的分片并生成 sha256 校验清单。

公司代理限制单次上传 ~1MB，所以原文件不入库（.gitignore 排除），
Git 仓库保存 large-files/ 下的分片，逐片 commit + push。
克隆后由 scripts/restore_large_files.py 重组并校验。

分片必须被 .gitattributes 的 `large-files/**/*.bin binary` 覆盖，
否则 core.autocrlf=true 会把无 NUL 的分片当文本做行尾转换、静默改坏。

用法（python 不在 PATH，用绝对路径）：
  D:\\software\\python31210\\install\\python.exe scripts\\split_large_files.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CHUNK_ROOT = ROOT / "large-files"
CHUNK_SIZE = 900_000  # 小于 1,000,000 字节，给传输留余量

TARGETS = [
    Path("乌台诗案造就苏东坡.m4a"),
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    CHUNK_ROOT.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {
        "version": 1,
        "chunkSize": CHUNK_SIZE,
        "files": [],
    }

    for relative in TARGETS:
        source = ROOT / relative
        if not source.exists():
            raise FileNotFoundError(f"缺少待拆分文件: {relative.as_posix()}")
        data = source.read_bytes()
        file_dir = CHUNK_ROOT / relative.parent / f"{relative.name}.parts"
        file_dir.mkdir(parents=True, exist_ok=True)

        # 只清理当前目标自己的旧分片
        for old_part in file_dir.glob("part-*.bin"):
            old_part.unlink()

        parts = []
        for index, offset in enumerate(range(0, len(data), CHUNK_SIZE)):
            chunk = data[offset : offset + CHUNK_SIZE]
            part_path = file_dir / f"part-{index:03d}.bin"
            part_path.write_bytes(chunk)
            parts.append(
                {
                    "path": part_path.relative_to(ROOT).as_posix(),
                    "size": len(chunk),
                    "sha256": sha256(chunk),
                }
            )

        manifest["files"].append(
            {
                "target": relative.as_posix(),
                "size": len(data),
                "sha256": sha256(data),
                "parts": parts,
            }
        )
        print(f"{relative.as_posix()}: {len(data)} 字节 -> {len(parts)} 个分片")

    manifest_path = CHUNK_ROOT / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"清单: {manifest_path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()