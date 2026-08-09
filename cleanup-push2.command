#!/bin/bash
cd "$(dirname "$0")"
LOG=cleanup-log2.txt
echo "=== cleanup take 2 ===" > "$LOG"

for f in github-check-log.txt github-check-log2.txt \
  push-log.txt push-diag-log.txt push-ssh-log.txt cleanup-log.txt \
  check-github-setup.command check-github-setup2.command \
  push-to-github.command push-diag.command push-ssh.command \
  cleanup-push.command cleanup-push2.command; do
  git rm --cached --ignore-unmatch -q "$f" >> "$LOG" 2>&1
done

git add -A >> "$LOG" 2>&1
git status >> "$LOG" 2>&1
git commit -m "Cleanup: remove remaining debug/setup scripts and logs" >> "$LOG" 2>&1
export GIT_SSH_COMMAND="ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new"
( git push >> "$LOG" 2>&1 ; echo "push exit code: $?" >> "$LOG" ) &
PUSH_PID=$!
( sleep 20 && kill -9 $PUSH_PID 2>/dev/null ) &
KILLER_PID=$!
wait $PUSH_PID 2>/dev/null
kill $KILLER_PID 2>/dev/null

echo "" >> "$LOG"
echo "HOTOVO. Toto okno muzete zavrit." >> "$LOG"
cat "$LOG"
