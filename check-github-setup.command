#!/bin/bash
cd "$(dirname "$0")"
echo "=== git ===" > github-check-log.txt
git --version >> github-check-log.txt 2>&1
echo "" >> github-check-log.txt
echo "=== gh (GitHub CLI) ===" >> github-check-log.txt
gh --version >> github-check-log.txt 2>&1
echo "" >> github-check-log.txt
echo "=== gh auth status ===" >> github-check-log.txt
gh auth status >> github-check-log.txt 2>&1
echo "" >> github-check-log.txt
echo "HOTOVO. Toto okno muzete zavrit." >> github-check-log.txt
cat github-check-log.txt
