# -*- coding: utf-8 -*-
"""绕过"超大响应收尾被代理掐断"的远端完整性验证。

背景：本机代理对 ~480MB 的克隆响应会在收尾时重置连接（curl 56，
残余仅几 KB），HTTP/1.1 与 postBuffer 均无效。改用：
  1. --filter=blob:none 部分克隆 —— 只拉提交/树对象（几 MB，单响应小）；
  2. 按清单逐个 git cat-file blob —— 每个分片触发一次 ~900KB 的按需
     fetch，天然低于代理的响应体积限制；
  3. 逐片校验 size+sha256，拼装后整文件 sha256 与本地原件比对。

用法：
  git clone --depth=1 --filter=blob:none --no-checkout <url> <dir>
  D:\\software\\python31210\\install\\python.exe scripts\\verify_remote.py <clone-dir> <original-dir>
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cat_blob(clone: Path, rel: str, expected_size: int, expected_sha: str) -> bytes:
    for attempt in range(1, 4):
        proc = subprocess.run(
            ["git", "-C", str(clone), "cat-file", "blob", f"HEAD:{rel}"],
            capture_output=True,
        )
        if proc.returncode == 0:
            data = proc.stdout
            if len(data) == expected_size and sha(data) == expected_sha:
                return data
            raise SystemExit(f"分片内容不符: {rel}")
        print(f"  重试 {rel} (attempt {attempt}): {proc.stderr.decode('utf-8', 'replace').strip()[:200]}", flush=True)
        time.sleep(10)
    raise SystemExit(f"分片取回失败: {rel}")


def main() -> None:
    clone = Path(sys.argv[1]).resolve()
    orig = Path(sys.argv[2]).resolve()
    # --no-checkout 克隆的工作区是空的，清单本身也从远端 blob 读，顺带验证它没坏
    remote_manifest = subprocess.run(
        ["git", "-C", str(clone), "cat-file", "blob", "HEAD:large-files/manifest.json"],
        capture_output=True, check=True,
    ).stdout
    man = json.loads(remote_manifest.decode("utf-8"))
    local_manifest = (orig / "large-files" / "manifest.json").read_bytes()
    # 本地文件是 Windows CRLF（write_text 默认换行转换），入库 blob 是 LF——
    # 归一换行后比字节，同时比 JSON 语义
    same = remote_manifest.replace(b"\r\n", b"\n") == local_manifest.replace(b"\r\n", b"\n")
    same = same and json.loads(remote_manifest) == json.loads(local_manifest)
    print(f"清单一致性: 远端 {len(remote_manifest)} 字节 / 本地 {len(local_manifest)} 字节 → "
          f"{'一致' if same else '不一致!'}")
    if not same:
        raise SystemExit("远端清单与本地不一致")

    bad = 0
    for f in man["files"]:
        chunks = [
            cat_blob(clone, p["path"], p["size"], p["sha256"]) for p in f["parts"]
        ]
        restored = b"".join(chunks)
        ok_remote = len(restored) == f["size"] and sha(restored) == f["sha256"]
        local = orig / f["target"]
        ok_local = local.exists() and sha(local.read_bytes()) == f["sha256"]
        ok = ok_remote and ok_local
        bad += 0 if ok else 1
        tag = " (改名别名)" if f.get("duplicateOf") else ""
        print(
            f"{'OK ' if ok else 'BAD'}  {f['size']:>10}  {len(f['parts']):>3}片  "
            f"{f['target']}{tag}  remote={'√' if ok_remote else '×'} local={'√' if ok_local else '×'}",
            flush=True,
        )
    print(f"RESULT: {len(man['files'])-bad}/{len(man['files'])} 一致" + (" — 全部通过" if bad == 0 else f"，{bad} 个失败"))
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()