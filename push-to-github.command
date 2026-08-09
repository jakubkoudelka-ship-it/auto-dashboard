#!/bin/bash
cd "$(dirname "$0")"
LOG=push-log.txt
echo "=== push to github ===" > "$LOG"

if [ ! -d .git ]; then
  git init >> "$LOG" 2>&1
  git branch -M main >> "$LOG" 2>&1
fi

git remote remove origin >> "$LOG" 2>&1
git remote add origin https://github.com/jakubkoudelka-ship-it/auto-dashboard.git >> "$LOG" 2>&1

cat > .gitignore <<'EOF'
__pycache__/
*.pyc
.DS_Store
.vscode/
node_modules/
*.log
.~lock*
EOF

git add -A >> "$LOG" 2>&1
git commit -m "Initial commit: auto-dashboard – výběr rodinného auta" >> "$LOG" 2>&1
echo "" >> "$LOG"
echo "=== pushing ===" >> "$LOG"
git push -u origin main >> "$LOG" 2>&1

echo "" >> "$LOG"
echo "HOTOVO. Toto okno muzete zavrit." >> "$LOG"
cat "$LOG"
