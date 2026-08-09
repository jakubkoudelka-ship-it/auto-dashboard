#!/bin/bash
cd "$(dirname "$0")"
LOG=github-check-log2.txt
echo "=== login shell PATH ===" > "$LOG"
echo "$PATH" >> "$LOG"
echo "" >> "$LOG"

echo "=== looking for gh in common locations ===" >> "$LOG"
for p in /opt/homebrew/bin/gh /usr/local/bin/gh /usr/bin/gh "$HOME/.local/bin/gh" $(which gh 2>/dev/null); do
  if [ -x "$p" ]; then
    echo "FOUND: $p" >> "$LOG"
  fi
done
echo "" >> "$LOG"

echo "=== sourcing zprofile/zshrc then checking gh ===" >> "$LOG"
source ~/.zprofile 2>/dev/null
source ~/.zshrc 2>/dev/null
which gh >> "$LOG" 2>&1
gh --version >> "$LOG" 2>&1
echo "" >> "$LOG"

echo "=== gh auth status (with sourced profile) ===" >> "$LOG"
gh auth status >> "$LOG" 2>&1
echo "" >> "$LOG"

echo "=== existing puella repo remote (for reference) ===" >> "$LOG"
if [ -d "$HOME/repos/puella-creatives-report" ]; then
  cd "$HOME/repos/puella-creatives-report"
  git remote -v >> "$LOG" 2>&1
  cd - > /dev/null
else
  echo "folder ~/repos/puella-creatives-report not found" >> "$LOG"
fi

echo "" >> "$LOG"
echo "HOTOVO. Toto okno muzete zavrit." >> "$LOG"
cat "$LOG"
