#!/usr/bin/env python3
"""
Predstahne fotky aut z Wikipedie a ulozi jejich URL primo do data/cars.json
(pole "image"). Dashboard pak fotky nenacita zive pri kazdem otevreni stranky
(coz bylo pomale/nespolehlive - az 53 soubeznych dotazu na en.wikipedia.org
pri kazdem nacteni), ale pouzije uz hotovou URL primo v <img src="...">.

Spustit lokalne (potrebuje realny pristup k internetu):
    python3 scripts/fetch_car_images.py

Bezpecne spustit opakovane - prepise vsechny fotky. Pro dofetchnuti jen
chybejicich pouzijte --missing-only.
"""
import json
import subprocess
import sys
import time
import urllib.parse

CARS_PATH = "data/cars.json"
UA = "auto-dashboard/1.0 (osobni projekt; kontakt: jakub.koudelka@puellavone.sk)"


def fetch_thumb(title, size=640):
    url = (
        "https://en.wikipedia.org/w/api.php?action=query&prop=pageimages"
        f"&piprop=thumbnail%7Coriginalimage&pithumbsize={size}&format=json&titles="
        + urllib.parse.quote(title)
    )
    # Pouziva se system curl (macOS Keychain trust store) misto Python
    # urllib/ssl - vyhne se casti castemu problemu s chybejicimi CA
    # certifikaty u python.org/Homebrew instalaci Pythonu na macOS
    # (CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate).
    result = subprocess.run(
        ["curl", "-s", "--max-time", "15", "-A", UA, url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout:
        raise RuntimeError(
            f"curl selhal (kod {result.returncode}): {result.stderr.strip()}"
        )
    data = json.loads(result.stdout)
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        thumb = page.get("thumbnail")
        if thumb and thumb.get("source"):
            return thumb["source"]
    return None


def main():
    missing_only = "--missing-only" in sys.argv

    with open(CARS_PATH, encoding="utf-8") as f:
        cars = json.load(f)

    cache = {}
    updated = 0
    failed = []
    for car in cars:
        if missing_only and car.get("image"):
            continue
        title = car["wikiTitle"]
        if title in cache:
            src = cache[title]
        else:
            try:
                src = fetch_thumb(title)
            except Exception as e:
                print(f"  chyba u '{title}': {e}")
                src = None
            cache[title] = src
            time.sleep(0.25)
        if src:
            car["image"] = src
            updated += 1
            print(f"OK   {car['id']}: {src}")
        else:
            car["image"] = None
            failed.append(car["id"])
            print(f"MISS {car['id']} ({title}) -> pouzije se ikona")

    with open(CARS_PATH, "w", encoding="utf-8") as f:
        json.dump(cars, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"\nHotovo: {updated} fotek ulozeno primo do cars.json, {len(failed)} bez fotky (fallback ikona).")
    if failed:
        print("Bez fotky:", ", ".join(failed))


if __name__ == "__main__":
    main()
