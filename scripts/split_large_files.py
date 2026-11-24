# -*- coding: utf-8 -*-
"""把超过 1 MB 的大文件拆成 900,000 字节的分片并生成 sha256 校验清单。

公司代理限制单次上传 ~1MB，所以原文件不入库（.gitignore 排除），
Git 仓库保存 large-files/ 下的分片，逐片 commit + push。
克隆后由 scripts/restore_large_files.py 重组并校验。

分片必须被 .gitattributes 的 `large-files/**/*.bin binary` 覆盖，
否则 core.autocrlf=true 会把无 NUL 的分片当文本做行尾转换、静默改坏。

去重复用：目标文件若与清单中已有文件 sha256 相同（典型场景是按集数
改名后的副本），只追加一条指向原分片的别名条目，不再重复切割上传。
restore 脚本对别名条目无感知——它只按 parts 列表还原。

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
MANIFEST_PATH = CHUNK_ROOT / "manifest.json"
CHUNK_SIZE = 900_000  # 小于 1,000,000 字节，给传输留余量

TARGETS = [
    Path("01眉山：一个母亲和两个儿子-程夫人的育儿秘籍.mp4"),
    Path("02一举成名：欧阳修的那场误会.mp4"),
    Path("03苏轼的跌宕人生：从天才到流放.mp4"),
    Path("04苏轼的转折点：党争、悲痛与退让.mp4"),
    Path("05明月几时有-苏轼和王弗.m4a"),
    Path("06苏轼：风雨中的政治与人生.mp4"),
    Path("07乌台诗案造就苏东坡.m4a"),
    Path("07乌台诗案：一份权威的历史报告.mp4"),
    Path("08黄州：苏轼死了，苏东坡活了.mp4"),
    Path("09苏轼：为何两党都不讨好？.mp4"),
    Path("10苏轼在杭州：贬谪官员的城市守护传奇.mp4"),
    Path("11苏轼在惠州：半生漂泊与旷达.mp4"),
    Path("12苏轼最后的岁月：流放与北归.mp4"),
    Path("20大宋情景喜剧：苏轼与文坛神话-苏小妹佛印.mp4"),
    Path("41苏轼与永恒的西湖：一场诗意之旅.mp4"),
    Path("42苏轼：苦难铸就的伟大.mp4"),
    Path("43“芳草”的真正含义：苏轼历史纪录片.mp4"),
    Path("44苏轼：密州出猎，千古江城子.mp4"),
    Path("45苏轼的千古绝唱：明月背后的动人故事.mp4"),
    Path("46苏轼的风暴：《定风波》背后的故事.mp4"),
    Path("48苏轼的浴火重生.mp4"),
    Path("49观察者效应：苏轼与庐山.mp4"),
    Path("50苏轼与春江晚景.mp4"),
    Path("51解码苏轼《赠刘景文》.mp4"),
    Path("21苏东坡与东坡肉：一块猪肉的千年传奇.mp4"),
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    CHUNK_ROOT.mkdir(parents=True, exist_ok=True)
    existing: dict[str, dict] = {}
    if MANIFEST_PATH.exists():
        old = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        existing = {f["target"]: f for f in old.get("files", [])}

    entries: list[dict] = []
    seen_sha: dict[str, dict] = {}
    # 尚未被任何 TARGETS 认领的旧条目（按 sha 索引），用于识别"改名"：
    # 本地文件改了名但字节没变时，沿用旧分片、把清单条目的 target 改成新名字，
    # 而不是把同样的内容再切一遍、再上传几百个分片。
    unclaimed = {f["sha256"]: dict(f) for f in existing.values()}

    for relative in TARGETS:
        source = ROOT / relative
        target = relative.as_posix()
        if not source.exists():
            print(f"警告: 跳过不存在的目标 {target}")
            continue
        data = source.read_bytes()
        digest = sha256(data)

        if digest in seen_sha:
            original = seen_sha[digest]
            entries.append(
                {
                    "target": target,
                    "size": len(data),
                    "sha256": digest,
                    "duplicateOf": original["target"],
                    "parts": original["parts"],  # 指向同一组分片，不重复入库
                }
            )
            print(f"{target}: 与 {original['target']} 字节相同，复用分片")
            continue

        reused = existing.get(target)
        if reused and reused["sha256"] == digest:
            entries.append(reused)
            seen_sha[digest] = reused
            unclaimed.pop(digest, None)
            print(f"{target}: 内容未变，沿用已有 {len(reused['parts'])} 个分片")
            continue

        renamed = unclaimed.pop(digest, None)
        if renamed:
            old_target = renamed["target"]
            renamed["target"] = target
            entries.append(renamed)
            seen_sha[digest] = renamed
            print(f"{target}: 由 {old_target} 改名而来，沿用已有 {len(renamed['parts'])} 个分片")
            continue

        file_dir = CHUNK_ROOT / relative.parent / f"{relative.name}.parts"
        file_dir.mkdir(parents=True, exist_ok=True)
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

        entry = {"target": target, "size": len(data), "sha256": digest, "parts": parts}
        entries.append(entry)
        seen_sha[digest] = entry
        print(f"{target}: {len(data)} 字节 -> {len(parts)} 个分片")

    # 本地已删除、也没有改名目标接管的旧条目：清单里去掉，分片目录一并清理，
    # 否则仓库会永久保留一批谁也还原不了的分片。
    for leftover in unclaimed.values():
        for part in leftover.get("parts", []):
            part_dir = (ROOT / part["path"]).parent
            if part_dir.exists():
                for stale in part_dir.glob("part-*.bin"):
                    stale.unlink()
                part_dir.rmdir()
        print(f"清理: {leftover['target']} 已不存在，移除清单条目与分片")

    manifest = {"version": 1, "chunkSize": CHUNK_SIZE, "files": entries}
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"清单: {MANIFEST_PATH.relative_to(ROOT).as_posix()}（{len(entries)} 个目标）")


if __name__ == "__main__":
    main()