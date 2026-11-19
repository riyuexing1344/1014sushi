#!/bin/bash
# 逐分片 commit + push（绕过代理单次上传~1MB限制），每片双重校验防假绿：
# ① 本地 HEAD 相对 push 前前进 ② ls-remote 的 main == 新 HEAD。
# 任一失败立即退出非 0，绝不把失败刷成 "Everything up-to-date" 的假成功。
#
# 用法：
#   bash scripts/push_parts.sh                # 推 large-files/ 下全部未提交分片
#   bash scripts/push_parts.sh "某个目录名"    # 只推该 .parts 目录
set -u
R=/d/CJDUBS/1014sushi
filter="${1:-}"
ok=0
fail=0
# 只处理尚未入库的分片（git ls-files 里没有的），已推过的自动跳过
while IFS= read -r rel; do
  case "$rel" in large-files/*.bin) ;; *) continue ;; esac
  if [ -n "$filter" ] && [[ "$rel" != *"$filter"* ]]; then continue; fi
  name=$(basename "$rel")
  before=$(git -C "$R" rev-parse HEAD)
  git -C "$R" add "$rel" || { echo "FAIL add $rel"; fail=1; break; }
  # add 静默失败会让 commit 无事可做，这里显式确认暂存区真有这个文件
  git -C "$R" diff --cached --name-only | grep -qF "$rel" || { echo "FAIL stage-empty $rel"; fail=1; break; }
  git -C "$R" commit -q -m "音频分片 $rel（900KB/片绕代理1MB上传限制）" || { echo "FAIL commit $rel"; fail=1; break; }
  after=$(git -C "$R" rev-parse HEAD)
  [ "$before" != "$after" ] || { echo "FAIL head-not-advanced $rel"; fail=1; break; }
  if ! git -C "$R" push origin main > /tmp/push_$name.log 2>&1; then
    echo "FAIL push $rel"; cat /tmp/push_$name.log; fail=1; break
  fi
  remote=$(git -C "$R" ls-remote origin main | cut -f1)
  [ "$remote" = "$after" ] || { echo "FAIL remote-mismatch $rel local=$after remote=$remote"; fail=1; break; }
  ok=$((ok+1))
  echo "OK $ok $rel -> $after"
done < <(git -C "$R" ls-files --others --exclude-standard -- large-files/)
[ "$fail" -eq 0 ] || exit 1
echo "DONE $ok parts pushed and verified"