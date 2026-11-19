#!/bin/bash
# 逐分片 commit + push（绕过代理单次上传~1MB限制），每片双重校验防假绿：
# ① 本地 HEAD 相对 push 前前进 ② ls-remote 的 main == 新 HEAD。
# 任一失败立即退出非 0，绝不把失败刷成 "Everything up-to-date" 的假成功。
set -u
R=/d/CJDUBS/1014sushi
PARTS_DIR="large-files/乌台诗案造就苏东坡.m4a.parts"
ok=0
for p in "$R/$PARTS_DIR"/part-*.bin; do
  name=$(basename "$p")
  rel="$PARTS_DIR/$name"
  before=$(git -C "$R" rev-parse HEAD)
  git -C "$R" add "$rel" || { echo "FAIL add $rel"; exit 1; }
  # add 静默失败会让 commit 无事可做，这里显式确认暂存区真有这个文件
  git -C "$R" diff --cached --name-only | grep -qF "$rel" || { echo "FAIL stage-empty $rel"; exit 1; }
  git -C "$R" commit -q -m "音频分片 $name（乌台诗案造就苏东坡.m4a，900KB/片绕代理1MB上传限制）" || { echo "FAIL commit $rel"; exit 1; }
  after=$(git -C "$R" rev-parse HEAD)
  [ "$before" != "$after" ] || { echo "FAIL head-not-advanced $rel"; exit 1; }
  if ! git -C "$R" push origin main > /tmp/push_$name.log 2>&1; then
    echo "FAIL push $rel"; cat /tmp/push_$name.log; exit 1
  fi
  remote=$(git -C "$R" ls-remote origin main | cut -f1)
  [ "$remote" = "$after" ] || { echo "FAIL remote-mismatch $rel local=$after remote=$remote"; exit 1; }
  ok=$((ok+1))
  echo "OK $ok $name -> $after"
done
echo "DONE $ok/16 parts pushed and verified"