#!/usr/bin/env python3
"""
Spocita transparentni skore 0-100 pro kazde auto v data/cars.json a ulozi
ho do pole "score". Skore je vazeny soucet ctyr slozek:

  35 % spolehlivost   - odvozeno z textoveho pole "reliability" (klicova
                         slova) + bonus/malus podle rizikovych/pozitivnich
                         frazi v "pros"/"cons" (napinak retezu, koroze,
                         elektronika, bezudrzbovy rozvod, bez turba...)
  30 % rozpocet        - podle pole "tier": do 200 tis. = 100 b.,
                         280-320 tis. = 78 b., nad rozpoctem = 30 b.,
                         nedoporuceno (avoid) = 8 b.
  15 % prostor          - kufr (litry, "na sedadla", ne sklopeno) normalizovany
                         v ramci kategorie (kombi/mpv/suv/uzitkove), aby se
                         SUV neporovnavalo s velkym MPV
  20 % znackova preference - vychozi 100 b. pro vsechny znacky; Skoda ma
                         (na zaklade explicitniho pozadavku uzivatele, ze je
                         pro nej az posledni volba) malus na 55 b. Zmente
                         BRAND_PREFERENCE nize, pokud se preference zmeni.

Auta s tier == "avoid" nikdy nedostanou znacku TOP bez ohledu na skore.
Top 3 auta s nejvyssim skore (a tier != avoid) dostanou "top": true,
zbytek "top": false - nahrazuje drivejsi rucni vyber.

Spustit:
    python3 scripts/score_cars.py
"""
import json
import re
import unicodedata

CARS_PATH = "data/cars.json"

WEIGHTS = {
    "reliability": 0.35,
    "budget": 0.30,
    "space": 0.15,
    "brand": 0.20,
}

TIER_SCORE = {
    "200k": 100,
    "280k": 78,
    "vyrazeno": 30,
    "avoid": 8,
}

# Znackova preference uzivatele. 100 = neutralni. Upravte podle libosti.
BRAND_PREFERENCE = {
    "skoda": 55,
}

STRONG_POS = [
    "vynikaj", "nejvyss ze vsech", "japonsk", "typick", "elita",
    "nadprumern", "velmi dobr", "velmi spolehliv", "extremn jednoduch",
]
POS = [
    "dobr", "spolehliv", "solidn", "slusn", "odoln", "robustn",
    "jednoduch", "atmosferick", "uspor",
]
NEG = [
    "prumern", "nachylnejs", "elektronik", "hydropneumatik", "sporn",
    "slab", "rizikov", "nedoporuc", "hors", "korozn",
]

CONS_RISK_STEMS = [
    "napinak", "retez", "koroz", "elektronik", "karbon",
    "hydropneumatik", "olej", "turbo",
]
PROS_BONUS_STEMS = [
    "spolehliv", "bezudrzbov", "jednoduch", "bez turba", "bez gpf",
    "bez dpf", "nejlevnejsi servis", "levny servis", "dostupne dily",
]


def normalize(text):
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def reliability_score(car):
    text = normalize(car.get("reliability", ""))
    if any(k in text for k in STRONG_POS):
        base = 93
    elif any(k in text for k in POS):
        base = 78
    elif any(k in text for k in NEG):
        base = 48
    else:
        base = 65  # neutralni popisny text bez jasneho hodnoticiho slova

    cons_text = normalize(" ".join(car.get("cons", [])))
    penalty = sum(2 for k in CONS_RISK_STEMS if k in cons_text)
    base -= min(penalty, 15)

    pros_text = normalize(" ".join(car.get("pros", [])))
    bonus = sum(2 for k in PROS_BONUS_STEMS if k in pros_text)
    base += min(bonus, 12)

    return max(5, min(100, base))


def parse_trunk(trunk_str):
    nums = [int(n) for n in re.findall(r"\d+", trunk_str or "")]
    return nums[0] if nums else None


def brand_score(brand):
    b = normalize(brand)
    for key, val in BRAND_PREFERENCE.items():
        if key in b:
            return val
    return 100


def main():
    with open(CARS_PATH, encoding="utf-8") as f:
        cars = json.load(f)

    # prostor: normalizace v ramci kategorie
    trunk_by_cat = {}
    for car in cars:
        t = parse_trunk(car.get("trunk", ""))
        car["_trunk_l"] = t
        if t is not None:
            trunk_by_cat.setdefault(car["category"], []).append(t)

    cat_minmax = {
        cat: (min(vals), max(vals)) for cat, vals in trunk_by_cat.items()
    }

    for car in cars:
        rel = reliability_score(car)
        budget = TIER_SCORE.get(car["tier"], 50)

        t = car.pop("_trunk_l")
        if t is None:
            space = 50
        else:
            lo, hi = cat_minmax[car["category"]]
            space = 100 if hi == lo else round((t - lo) / (hi - lo) * 100)

        brand = brand_score(car["brand"])

        total = (
            WEIGHTS["reliability"] * rel
            + WEIGHTS["budget"] * budget
            + WEIGHTS["space"] * space
            + WEIGHTS["brand"] * brand
        )
        total = max(0, min(100, round(total)))

        car["score"] = total
        car["scoreBreakdown"] = {
            "reliability": rel,
            "budget": budget,
            "space": space,
            "brand": brand,
        }

    # TOP 3 podle skore, tier != avoid
    eligible = [c for c in cars if c["tier"] != "avoid"]
    eligible.sort(key=lambda c: c["score"], reverse=True)
    top_ids = {c["id"] for c in eligible[:3]}
    for car in cars:
        car["top"] = car["id"] in top_ids

    with open(CARS_PATH, "w", encoding="utf-8") as f:
        json.dump(cars, f, ensure_ascii=False, indent=2)
        f.write("\n")

    ranked = sorted(cars, key=lambda c: c["score"], reverse=True)
    print(f"{'skore':>5}  {'top':^3}  {'tier':^9}  {'znacka':<14}  nazev")
    for c in ranked:
        print(
            f"{c['score']:>5}  {'★' if c['top'] else ' ':^3}  {c['tier']:^9}  {c['brand']:<14}  {c['name']}"
        )


if __name__ == "__main__":
    main()
