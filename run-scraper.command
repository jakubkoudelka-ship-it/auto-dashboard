#!/bin/bash
cd "$(dirname "$0")"
echo "Instaluji závislosti..."
pip3 install --break-system-packages -q -r scripts/requirements.txt 2>&1 | tee scraper-log.txt
echo "Spouštím scraper (všech 53 modelů, cca 2-3 minuty)..." | tee -a scraper-log.txt
python3 scripts/scrape_bazos.py --delay 2.0 2>&1 | tee -a scraper-log.txt
echo "" | tee -a scraper-log.txt
echo "HOTOVO. Toto okno můžete zavřít." | tee -a scraper-log.txt
