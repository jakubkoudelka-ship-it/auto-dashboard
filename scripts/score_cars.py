#!/usr/bin/env python3
"""
Spocita transparentni skore 0-100 pro kazde auto v data/cars.json a ulozi
ho do pole "score". Skore je vazeny soucet SEDMI slozek popisujicich
VLASTNOSTI auta - pořizovaci cena zaměrně NENI soucasti skore, protoze
neni vlastnosti auta jako takoveho (jde o promenlivy udaj konkretniho
inzeratu/trhu, ne o parametr modelu). Rozpocet zustava zobrazeny zvlast -
jako tier badge na karte ("do 200 tis. Kc" / "280-320 tis. Kc" / ...) a
jako filtrovaci pilulky nahore, takze si ho muzete kdykoli sami omezit.

  25 % spolehlivost       - odvozeno z textoveho pole "reliability" (klicova
                            slova) + bonus/malus podle rizikovych/pozitivnich
                            frazi v "pros"/"cons" (napinak retezu, koroze,
                            elektronika, bezudrzbovy rozvod, bez turba...)
  15 % bezpecnost (NCAP)  - hvezdicky Euro NCAP (viz NCAP_DATA); ruzne
                            generace testovaciho protokolu nejsou 1:1
                            srovnatelne (test se v case zpřísňoval), proto
                            se u kazdeho auta zobrazuje i rok testu.
                            Netestovana auta dostavaji neutralni 50 b.
  10 % spotreba paliva    - odhad realne kombinovane spotreby (l/100 km),
                            normalizovano napric celym seznamem (mensi
                            spotreba = vyssi skore) - viz CONSUMPTION_DATA
  10 % servis a dily      - kombinace obecne znamky dostupnosti/ceny
                            servisu a dilu pro danou znacku v CR
                            (BRAND_SERVICE_BASE) + klicova slova v pros/cons
  15 % prostor            - kufr (litry, "na sedadla", ne sklopeno)
                            normalizovany v ramci kategorie (kombi/mpv/suv/
                            uzitkove), aby se SUV neporovnavalo s velkym MPV
   5 % dostupnost na trhu - kolik relevantnich inzeratu se aktualne najde
                            (data/listings.json ze scripts/scrape_bazos.py) -
                            malo inzeratu = hur se to realne shani
  20 % znackova preference - vychozi 100 b. pro vsechny znacky; Skoda ma
                            (na zaklade explicitniho pozadavku uzivatele, ze
                            je pro nej az posledni volba) malus na 55 b.
                            Vaha 20 % je zamerne vyssi nez u ostatnich slozek,
                            protoze s pribyvajicimi vlastnostmi (bezpecnost,
                            servis, dostupnost) by Skoda diky sirokemu
                            zastoupeni na CZ trhu jinak preference prebila -
                            tato vaha to spolehlive vyvazuje.
                            Zmente BRAND_PREFERENCE nize, pokud se preference
                            zmeni.

Znacku TOP (top 3 podle skore) mohou dostat jen auta v realnem rozpoctu
(tier "200k" nebo "280k") - auto nad rozpoctem nebo s tier "avoid" se
nikdy neoznaci jako TOP doporuceni, bez ohledu na to, jak dobre skoruje
na vlastnostech, protoze si ho reálně nekoupite.

Spustit:
    python3 scripts/score_cars.py

Zdroje pro spotrebu a NCAP: typicke udavane kombinovane spotreby pro danou
motorizaci a oficialni vysledky euroncap.com (rok testu uveden u kazdeho
auta v poli "ncap"). U par vzacnych/domacich modelu (Lada Niva) Euro NCAP
test neexistuje - "ncap": null.
"""
import json
import re
import unicodedata

CARS_PATH = "data/cars.json"
LISTINGS_PATH = "data/listings.json"

WEIGHTS = {
    "reliability": 0.25,
    "safety": 0.15,
    "consumption": 0.10,
    "service": 0.10,
    "space": 0.15,
    "availability": 0.05,
    "brand": 0.20,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

# Tier, ktery je eligible pro znacku TOP (realny rozpocet). "vyrazeno" a
# "avoid" jsou z TOP vyrazeny vzdy, i kdyby mely nejvyssi skore vlastnosti.
TOP_ELIGIBLE_TIERS = {"200k", "280k"}

# Znackova preference uzivatele. 100 = neutralni. Upravte podle libosti.
BRAND_PREFERENCE = {
    "skoda": 55,
}

# Obecna dostupnost/cena servisu a dilu pro danou znacku v CR (100 =
# nejlevnejsi a nejdostupnejsi, mensi cislo = drazsi dily / rezasi sit
# mechaniku). Hruby odhad podle beznych zkusenosti na ceskem trhu, ne
# oficialni statistika - lze kdykoli upravit.
BRAND_SERVICE_BASE = {
    "skoda": 100,
    "volkswagen": 90, "vw": 90, "seat": 90, "audi": 90,
    "ford": 88, "opel": 86, "renault": 85, "dacia": 88,
    "hyundai": 84, "kia": 84,
    "toyota": 78, "honda": 76, "nissan": 76, "mazda": 74,
    "mitsubishi": 74, "suzuki": 76,
    "peugeot": 70, "citroen": 70, "citroën": 70, "fiat": 68,
    "chevrolet": 66, "daewoo": 66,
    "volvo": 60, "subaru": 60,
    "lada": 55,
}

# Odhad realne kombinovane spotreby (l/100 km) pro danou motorizaci.
CONSUMPTION_DATA = {
    "skoda-octavia2-combi": 7.0,
    "fiat-tipo-kombi": 6.2,
    "toyota-avensis-corolla-verso": 7.3,
    "ford-mondeo-combi": 8.2,
    "ford-focus-combi": 6.4,
    "kia-ceed-hyundai-i30-combi": 6.7,
    "mazda6-kombi": 7.8,
    "peugeot-308-sw": 6.7,
    "seat-leon-st": 7.0,
    "volvo-v70-v50": 9.2,
    "skoda-roomster-rapid": 6.0,
    "dacia-logan-mcv": 7.0,
    "renault-megane-grandtour": 7.1,
    "vw-golf-passat-variant": 7.0,
    "citroen-c4-c5-tourer": 7.0,
    "mazda-premacy-5": 7.8,
    "seat-altea-xl": 7.0,
    "fiat-500l": 6.2,
    "opel-zafira": 7.8,
    "renault-grand-scenic": 7.2,
    "vw-sharan-galaxy-alhambra": 8.7,
    "dacia-duster1": 7.5,
    "nissan-qashqai1": 7.2,
    "hyundai-ix35": 8.0,
    "mitsubishi-asx": 7.0,
    "suzuki-sx4": 7.2,
    "suzuki-vitara-new": 6.0,
    "skoda-yeti": 6.5,
    "subaru-forester": 8.7,
    "honda-crv-civic-tourer": 8.0,
    "tucson-sportage-moderni": 7.0,
    "dacia-dokker": 7.2,
    "renault-kangoo": 7.7,
    "partner-tepee-berlingo": 7.2,
    "fiat-doblo": 7.2,
    "citroen-c4-picasso": 7.0,
    "ford-cmax": 7.7,
    "ford-smax": 8.7,
    "kia-carens": 7.7,
    "toyota-verso": 7.2,
    "mitsubishi-outlander": 9.2,
    "suzuki-grand-vitara": 10.0,
    "lada-niva": 10.5,
    "toyota-auris-touring": 6.7,
    "opel-astra-combi": 6.5,
    "opel-insignia-combi": 7.8,
    "skoda-superb-combi": 7.2,
    "hyundai-i40-combi": 7.0,
    "chevrolet-daewoo-lacetti": 7.7,
    "octavia3-14tsi-ea211": 5.7,
    "octavia3-16mpi": 6.5,
    "duster2-sce": 7.2,
    "octavia3-duster2-evo-avoid": 5.7,
}

# Euro NCAP hvezdicky (0-5, None = netestovano) + rok testu (informacni,
# ukazuje generaci testovaciho protokolu - viz euroncap.com).
NCAP_DATA = {
    "skoda-octavia2-combi": (5, 2004),
    "fiat-tipo-kombi": (3, 2016),
    "toyota-avensis-corolla-verso": (5, 2003),
    "ford-mondeo-combi": (5, 2003),
    "ford-focus-combi": (5, 2011),
    "kia-ceed-hyundai-i30-combi": (5, 2007),
    "mazda6-kombi": (5, 2008),
    "peugeot-308-sw": (5, 2007),
    "seat-leon-st": (5, 2012),
    "volvo-v70-v50": (5, 2007),
    "skoda-roomster-rapid": (5, 2006),
    "dacia-logan-mcv": (3, 2007),
    "renault-megane-grandtour": (5, 2008),
    "vw-golf-passat-variant": (5, 2009),
    "citroen-c4-c5-tourer": (5, 2010),
    "mazda-premacy-5": (5, 2010),
    "seat-altea-xl": (5, 2004),
    "fiat-500l": (5, 2013),
    "opel-zafira": (5, 2011),
    "renault-grand-scenic": (5, 2009),
    "vw-sharan-galaxy-alhambra": (5, 2011),
    "dacia-duster1": (3, 2011),
    "nissan-qashqai1": (5, 2007),
    "hyundai-ix35": (5, 2010),
    "mitsubishi-asx": (5, 2010),
    "suzuki-sx4": (4, 2006),
    "suzuki-vitara-new": (5, 2015),
    "skoda-yeti": (5, 2009),
    "subaru-forester": (5, 2013),
    "honda-crv-civic-tourer": (5, 2012),
    "tucson-sportage-moderni": (5, 2015),
    "dacia-dokker": (3, 2013),
    "renault-kangoo": (4, 2008),
    "partner-tepee-berlingo": (3, 2008),
    "fiat-doblo": (3, 2010),
    "citroen-c4-picasso": (5, 2013),
    "ford-cmax": (5, 2010),
    "ford-smax": (5, 2006),
    "kia-carens": (5, 2013),
    "toyota-verso": (5, 2009),
    "mitsubishi-outlander": (5, 2012),
    "suzuki-grand-vitara": (4, 2007),
    "lada-niva": (None, None),
    "toyota-auris-touring": (5, 2013),
    "opel-astra-combi": (5, 2009),
    "opel-insignia-combi": (5, 2008),
    "skoda-superb-combi": (5, 2015),
    "hyundai-i40-combi": (5, 2011),
    "chevrolet-daewoo-lacetti": (3, 2005),
    "octavia3-14tsi-ea211": (5, 2013),
    "octavia3-16mpi": (5, 2013),
    "duster2-sce": (3, 2018),
    "octavia3-duster2-evo-avoid": (5, 2013),
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

SERVICE_POS_STEMS = [
    "nejlevnejsi servis", "levny servis", "dostupne dily", "mechanik",
    "nahradni dily kdekoli", "dostupnost dilu", "siroka sit", "levne dily",
]
SERVICE_NEG_STEMS = [
    "drahe dily", "spatna dostupnost", "malo mechaniku", "vzacne dily",
    "special", "draha udrzba", "drahy servis",
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


def service_score(car):
    b = normalize(car.get("brand", ""))
    base = 65
    for key, val in BRAND_SERVICE_BASE.items():
        if key in b:
            base = val
            break

    text = normalize(" ".join(car.get("pros", []) + car.get("cons", [])))
    base += min(sum(4 for k in SERVICE_POS_STEMS if k in text), 12)
    base -= min(sum(4 for k in SERVICE_NEG_STEMS if k in text), 12)
    return max(5, min(100, round(base)))


def safety_score(car_id):
    stars, _year = NCAP_DATA.get(car_id, (None, None))
    if stars is None:
        return 50  # netestovano - neutralni, nepenalizujeme za chybejici data
    return stars * 20


def parse_trunk(trunk_str):
    nums = [int(n) for n in re.findall(r"\d+", trunk_str or "")]
    return nums[0] if nums else None


def brand_score(brand):
    b = normalize(brand)
    for key, val in BRAND_PREFERENCE.items():
        if key in b:
            return val
    return 100


def load_listing_counts():
    try:
        with open(LISTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    return {entry["car_id"]: len(entry.get("listings", [])) for entry in data}


def availability_score(count):
    if count is None:
        return 50  # zadna data o inzeratech - neutralni
    return round(min(100, count / 6 * 100))


def main():
    with open(CARS_PATH, encoding="utf-8") as f:
        cars = json.load(f)

    listing_counts = load_listing_counts()

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

    # spotreba: normalizace napric celym seznamem (mensi = lepsi)
    consumptions = [v for v in CONSUMPTION_DATA.values() if v is not None]
    cons_lo, cons_hi = min(consumptions), max(consumptions)

    for car in cars:
        rel = reliability_score(car)

        t = car.pop("_trunk_l")
        if t is None:
            space = 50
        else:
            lo, hi = cat_minmax[car["category"]]
            space = 100 if hi == lo else round((t - lo) / (hi - lo) * 100)

        brand = brand_score(car["brand"])
        service = service_score(car)
        safety = safety_score(car["id"])

        cons_l100 = CONSUMPTION_DATA.get(car["id"])
        car["consumption"] = cons_l100
        if cons_l100 is None:
            consumption = 50
        else:
            consumption = round(
                100 - (cons_l100 - cons_lo) / (cons_hi - cons_lo) * 100
            )

        ncap_stars, ncap_year = NCAP_DATA.get(car["id"], (None, None))
        car["ncap"] = (
            {"stars": ncap_stars, "year": ncap_year}
            if ncap_stars is not None
            else None
        )

        count = listing_counts.get(car["id"])
        availability = availability_score(count)

        total = (
            WEIGHTS["reliability"] * rel
            + WEIGHTS["safety"] * safety
            + WEIGHTS["consumption"] * consumption
            + WEIGHTS["service"] * service
            + WEIGHTS["space"] * space
            + WEIGHTS["availability"] * availability
            + WEIGHTS["brand"] * brand
        )
        total = max(0, min(100, round(total)))

        car["score"] = total
        car["scoreBreakdown"] = {
            "reliability": rel,
            "safety": safety,
            "consumption": consumption,
            "service": service,
            "space": space,
            "availability": availability,
            "brand": brand,
        }

    # TOP 3 podle skore, jen mezi auty v realnem rozpoctu
    eligible = [c for c in cars if c["tier"] in TOP_ELIGIBLE_TIERS]
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
