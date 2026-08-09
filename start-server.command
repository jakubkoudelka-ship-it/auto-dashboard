#!/bin/bash
cd "$(dirname "$0")"
echo "Spouštím lokální server pro Výběr rodinného auta..."
echo "Otevírám http://localhost:8000 v prohlížeči..."
( sleep 1 && open "http://localhost:8000" ) &
python3 -m http.server 8000
