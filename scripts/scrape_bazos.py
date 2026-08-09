#!/usr/bin/env python3
"""
scrape_bazos.py — best-effort scraper prototype pro auto.bazos.cz

DULEZITE UPOZORNENI (precti pred pouzitim):
- Tento skript NEBYL otestovan proti zivemu webu z vyvojoveho sandboxu
  (prostredi, ve kterem vznikl, nema pristup k vnejsi siti mimo npm registry).
  Je sestaven podle znameho / typickeho HTML schematu klasifikacnich webu
  rodiny Bazos.cz, ale struktura stranky se muze v case zmenit -> pred
  ostrym nasazenim (napr. v GitHub Actions) si over, ze selektory sedi,
  a pripadne uprav CSS selektory v sekci "SELEKTORY" nize.
- Over si aktualni robots.txt (https://auto.bazos.cz/robots.txt) a
  podminky pouziti webu. Skript defaultne stahuje pomalu (delay mezi
  requesty) a posila slusne User-Agent hlavicky, ale je na tobe, abys
  provoz drzel v mezich toho, co web dovoluje.
- Skript slouzi jako VYCHOZI BOD pro GitHub Actions workflow
  (.github/workflows/update-listings.yml), ne jako hotove produkcni reseni.

Pouziti:
    pip install -r requirements.txt
    python scripts/scrape_bazos.py                # projede vsechny modely v data/cars.json
    python scripts/scrape_bazos.py --limit 3       # jen prvnich N modelu (test)
    python scripts/scrape_bazos.py --delay 2.0     # pauza mezi requesty (sekundy)

Vystup:
    data/listings.json — pole objektu {car_id, query, url, scraped_at, listings: [...]}
"""

import argparse
import json
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CARS_JSON = ROOT / "data" / "cars.json"
OUT_JSON = ROOT / "data" / "listings.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; auto-dashboard-scraper/0.1; "
        "personal-use-research-bot)"
    ),
    "Accept-Language": "cs-CZ,cs;q=0.9",
}

MAX_LISTINGS_PER_CAR = 8
MAX_RAW_ITEMS_TO_SCAN = 40  # kolik prvnich vysledku z vypisu vubec projit pred filtrovanim

# Slova, ktera jasne znaci naftovy motor -> vyradit, protoze cely dashboard je jen pro benzin
DIESEL_KEYWORDS = [
    "tdi", "dci", "cdti", "hdi", "crdi", "jtd", "multijet", "d4d",
    "dtec", "cdi ", " cdi", "bluehdi", "nafta", "diesel", "tdci",
]

_DISPLACEMENT_RE = re.compile(r"(?<!\d)([12])[.,](\d)(?!\d)")


def normalize(text: str) -> str:
    """Lowercase a odstrani diakritiku, aby 'Škoda' == 'skoda' apod."""
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def required_keywords(car: dict):
    """
    Znacka + model, ktere by mel nadpis inzeratu obsahovat, aby slo o
    relevantni auto (Bazos casto do vysledku primichava placene 'TOP'
    inzeraty naprosto jineho auta, ktere s hledanym vyrazem nesouvisi).
    Vraci (brand_kw, model_kw) normalizovane bez diakritiky.
    """
    brand_raw = car.get("brand", "").split("/")[0].strip()
    brand_kw = normalize(brand_raw)
    model_kw = normalize(car.get("sautoModel") or "")
    return brand_kw, model_kw


def keyword_match(title: str, car: dict) -> bool:
    """True pokud nadpis obsahuje znacku a model hledaneho auta (nebo aspon jedno z nich,
    pokud druhe chybi ve vstupnich datech)."""
    norm_title = normalize(title)
    brand_kw, model_kw = required_keywords(car)
    brand_ok = (not brand_kw) or (brand_kw in norm_title)
    model_ok = (not model_kw) or (model_kw in norm_title)
    return brand_ok and model_ok


def extract_displacements(text: str):
    """Najde vsechny zminky objemu motoru typu '1.6' / '1,6' / '2.0' v textu."""
    return {f"{m.group(1)}.{m.group(2)}" for m in _DISPLACEMENT_RE.finditer(text)}


def target_displacement(car_name: str):
    """Odvodi cilovy objem motoru z nazvu modelu, napr. '1.6' z 'Octavia Combi 1.6 MPI/TSI'."""
    found = extract_displacements(car_name)
    return sorted(found)[0] if found else None


def classify_listing(title: str, target: str):
    """
    Vrati True/False/None podle toho, jestli inzerat odpovida ocekavane motorizaci:
    - False = jasny nesoulad (naftovy motor, nebo jiny objem nez cilovy) -> vyradit
    - True  = objem v nadpisu odpovida cilovemu
    - None  = nadpis neobsahuje info o motoru -> nejde overit, necháme (s poznamkou v UI)
    """
    lower = title.lower()
    if any(kw in lower for kw in DIESEL_KEYWORDS):
        return False
    if not target:
        return None
    found = extract_displacements(lower)
    if not found:
        return None
    return target in found


def bazos_search_url(query: str, cena_do: int) -> str:
    """Sestavi URL pro standardni vyhledavaci formular na *.bazos.cz."""
    q = quote(query)
    return (
        f"https://auto.bazos.cz/?hledat={q}&hlokalita=&humkreis=25"
        f"&cenaod=&cenado={cena_do}&Submit=Hled%C3%A1n%C3%AD"
    )


def price_cap_for_tier(tier: str) -> int:
    if tier in ("280k", "avoid"):
        return 350000
    return 200000


def parse_price(text: str):
    """'149 900 Kč' -> 149900 (int) nebo None pokud se neda parsovat."""
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


def fetch(url: str):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text


def parse_listings(html: str, base_url: str = "https://auto.bazos.cz"):
    """
    SELEKTORY — over/uprav podle aktualni struktury auto.bazos.cz.
    Bazos rodina webu tradicne pouziva blok `div.inzeraty` na jeden
    inzerat, s nadpisem v `h2.nadpis > a`, cenou v `div.inzeratycena`
    a fotkou v `div.inzeratyfotka img`. Pokud se struktura zmenila,
    uprav selektory tady na jednom miste.
    """
    soup = BeautifulSoup(html, "lxml")
    results = []

    items = soup.select("div.inzeraty")
    for item in items:
        title_el = item.select_one("h2.nadpis a") or item.select_one(".nadpis a")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        if href and not href.startswith("http"):
            href = base_url + href

        price_el = item.select_one(".inzeratycena")
        price_text = price_el.get_text(strip=True) if price_el else None

        loc_el = item.select_one(".inzeratylok")
        location = loc_el.get_text(strip=True) if loc_el else None

        img_el = item.select_one(".inzeratyfotka img")
        thumb = img_el.get("src") if img_el else None

        results.append(
            {
                "title": title,
                "url": href,
                "price_text": price_text,
                "price": parse_price(price_text),
                "location": location,
                "thumbnail": thumb,
            }
        )
        if len(results) >= MAX_RAW_ITEMS_TO_SCAN:
            break

    return results


def filter_and_cap_listings(listings, car: dict):
    """
    Odfiltruje inzeraty, ktere:
    - vubec nezminuji znacku/model hledaneho auta (Bazos casto do vysledku
      primichava placene 'TOP' inzeraty uplne jineho auta bez ohledu na dotaz),
    - maji jasne jinou motorizaci (nafta, jiny objem nez cilovy).
    Nejiste motorizace (objem v nadpisu neuveden) necha a oznaci v datech,
    aby to dashboard mohl zobrazit s poznamkou. Na konci orizne na MAX_LISTINGS_PER_CAR.
    """
    target = target_displacement(car["name"])
    kept = []
    for item in listings:
        if not keyword_match(item["title"], car):
            continue  # nadpis vubec nezminuje znacku/model -> nejspis promo inzerat jineho auta
        match = classify_listing(item["title"], target)
        if match is False:
            continue  # jasny nesoulad motorizace -> vyradit z vypisu
        item["engine_match"] = match  # True nebo None
        kept.append(item)
        if len(kept) >= MAX_LISTINGS_PER_CAR:
            break
    return kept


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="omezit na prvnich N modelu (test)")
    parser.add_argument("--delay", type=float, default=1.5, help="pauza mezi requesty v sekundach")
    args = parser.parse_args()

    cars = json.loads(CARS_JSON.read_text(encoding="utf-8"))
    if args.limit:
        cars = cars[: args.limit]

    out = []
    for i, car in enumerate(cars, 1):
        query = car.get("bazosQuery") or car["name"]
        cena_do = price_cap_for_tier(car.get("tier", "200k"))
        url = bazos_search_url(query, cena_do)

        print(f"[{i}/{len(cars)}] {car['id']} -> {url}", file=sys.stderr)

        try:
            html = fetch(url)
            raw_listings = parse_listings(html)
            listings = filter_and_cap_listings(raw_listings, car)
            status = "ok"
        except Exception as exc:  # noqa: BLE001 — chceme pokracovat i pri chybe jednoho requestu
            print(f"  chyba: {exc}", file=sys.stderr)
            listings = []
            status = f"error: {exc}"

        out.append(
            {
                "car_id": car["id"],
                "query": query,
                "search_url": url,
                "status": status,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "listings": listings,
            }
        )

        time.sleep(args.delay)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nHotovo, zapsano {len(out)} zaznamu do {OUT_JSON}", file=sys.stderr)


if __name__ == "__main__":
    main()
