#!/usr/bin/env python3
"""Jednorazovy skript: rozdeli spojenou polozku 'VW Sharan / Ford Galaxy /
Seat Alhambra' na dve samostatne polozky (Sharan/Galaxy a Alhambra
zvlast), s opravenou cenou dle aktualniho pruzkumu bazaru (puvodni text
"prakticky mimo rozpocet" byl prilis pesimisticky - realne benzinove TSI
kusy se prodavaji v pasmu 170-220 tis. Kc)."""
import json

CARS_PATH = "data/cars.json"

with open(CARS_PATH, encoding="utf-8") as f:
    cars = json.load(f)

old = next(c for c in cars if c["id"] == "vw-sharan-galaxy-alhambra")
idx = cars.index(old)

sharan_galaxy = {
    "id": "vw-sharan-galaxy",
    "name": "VW Sharan / Ford Galaxy 1.4 TSI/2.0 TSI",
    "wikiTitle": "Volkswagen Sharan",
    "brand": "VW / Ford",
    "brandSlug": "volkswagen",
    "category": "mpv",
    "tier": "200k",
    "top": False,
    "trunk": "300–850 l",
    "price": "170–220 tis. Kč (roč. 2011–2013, vyšší nájezd)",
    "reliability": "Velmi dobrá",
    "note": "Nejprostornější 7místné MPV v přehledu, benzín se dá sehnat i v rozpočtu.",
    "pros": [
        "Nejprostornější 7místé MPV v přehledu",
        "Velmi odolná mechanika, sdílená s Passat/Goll platformou",
        "Motor 1.4 TSI/2.0 TSI je při dobré péči odolný",
    ],
    "cons": [
        "Benzín na trhu vzácnější než diesel, hlídat historii servisu",
        "1.4 TSI (twincharger u starších verzí) mechanicky složitější",
        "Vyšší spotřeba u těžšího 7místého karoserie",
    ],
    "bazosQuery": "vw sharan benzín",
    "sautoModel": "sharan",
    "engineNote": "Benzínové verze bývají 1.4 TSI nebo 2.0 TSI (obě přeplňované, přímé vstřikování). 1.4 TSI u starších ročníků (do cca 2012) může být provedení s dvojím přeplňováním (turbo+kompresor), mechanicky složitější. 2.0 TSI je jednodušší (jen turbo) a obvykle spolehlivější volba. Benzínové kusy jsou na trhu vzácnější než dieselové, ale reálně sehnatelné v rozpočtu kolem 170-220 tis. Kč, obvykle s vyšším nájezdem.",
    "image": old.get("image"),
}

alhambra = {
    "id": "seat-alhambra",
    "name": "Seat Alhambra 1.4 TSI/2.0 TSI",
    "wikiTitle": "Seat Alhambra",
    "brand": "Seat",
    "brandSlug": "seat",
    "category": "mpv",
    "tier": "200k",
    "top": False,
    "trunk": "300–850 l",
    "price": "170–220 tis. Kč (roč. 2011–2013, vyšší nájezd)",
    "reliability": "Velmi dobrá",
    "note": "Mechanicky identická s VW Sharan (sdílená platforma) – nejprostornější 7místné MPV v přehledu.",
    "pros": [
        "Nejprostornější 7místé MPV v přehledu",
        "Mechanicky identická se Sharan – stejná spolehlivost",
        "Motor 1.4 TSI/2.0 TSI je při dobré péči odolný",
    ],
    "cons": [
        "Benzín na trhu vzácnější než diesel, hlídat historii servisu",
        "1.4 TSI (twincharger u starších verzí) mechanicky složitější",
        "Vyšší spotřeba u těžšího 7místého karoserie",
    ],
    "bazosQuery": "seat alhambra benzín",
    "sautoModel": "alhambra",
    "engineNote": "Motorová nabídka a rizika jsou stejná jako u sesterského VW Sharan (sdílená platforma PQ35/PQ46) – doporučujeme 2.0 TSI před starším 1.4 TSI (twincharger). Benzínové kusy Alhambry se na bazaru objevují o něco častěji za mírně nižší cenu než u VW verze, i když jde mechanicky o identické auto.",
    "image": old.get("image"),
}

cars[idx:idx + 1] = [sharan_galaxy, alhambra]

with open(CARS_PATH, "w", encoding="utf-8") as f:
    json.dump(cars, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"Hotovo. Celkem v cars.json: {len(cars)}")
