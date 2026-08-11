"""
Jednorazovy skript: prida 4 bi-fuel CNG+benzin modely do data/cars.json
(Skoda Octavia G-TEC, Seat Leon ST TGI, Seat Arona TGI, Skoda Kamiq G-TEC).

Bezi na CNG, ale v nadrzi maji vzdy i benzin jako zalozni palivo, takze
nejde o vyjimku z benzinoveho zamereni dashboardu - jen o palivove levnejsi
varianty. "consumption" pole je pro tyto ctyri auta v kg CNG/100 km (ne
litry benzinu) - viz "consumptionUnit" pole a uprava v app.js.

Spustit jen jednou, pak uz "skoda-octavia-gtec" atd. v cars.json existuje
a skript nic nepridava (idempotentni podle id).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARS_JSON = ROOT / "data" / "cars.json"

NEW_CARS = [
    {
        "id": "skoda-octavia-gtec",
        "name": "Škoda Octavia III G-TEC 1.4 TGI (CNG+benzín)",
        "wikiTitle": "Škoda Octavia",
        "brand": "Škoda",
        "brandSlug": "skoda",
        "category": "kombi",
        "tier": "200k",
        "top": False,
        "trunk": "495 l",
        "price": "150–300 tis. Kč (dle roku, výbavy a nájezdu – starší kusy pod 200 tis.)",
        "reliability": "Velmi dobrá u druhé generace motoru (1.4 TGI 81 kW) – výrazně spolehlivější než starší EcoFuel",
        "note": "Bi-fuel CNG/benzín – v nádrži je vždy i benzín jako záloha, takže to není odklon od benzínového zaměření srovnání, jen levnější provoz. Kupujte generaci 1.4 TGI 81 kW (cca 2014+), ne starší 1.4 EcoFuel 110 kW.",
        "pros": [
            "Provoz na CNG cca o 30–35 % levnější než na benzín (cca 41 Kč/kg CNG vs. benzín)",
            "Motor 1.4 TGI 81 kW prokázal v reálném provozu spolehlivost i přes 400 000 km (zkušenosti taxislužeb)",
            "Široká servisní síť Škoda",
            "Dojezd na oba zdroje dohromady přes 1000 km",
        ],
        "cons": [
            "Kufr zmenšený na 495 l kvůli dvěma nádržím na CNG pod podlahou",
            "Vyšší hmotnost (+139 kg) více zatěžuje zadní nápravu a tlumiče",
            "Revize CNG zařízení a nádrže vyžaduje mechanika specializovaného na CNG (zhruba v rytmu STK, cca 550 Kč)",
            "Vyhněte se starší generaci 1.4 EcoFuel (110 kW, do cca 2013) – měla reálné problémy se vstřikovači, zaseknutím motoru při přepínání paliv a korozí nádrží (svolávací akce)",
        ],
        "bazosQuery": "škoda octavia combi g-tec cng",
        "sautoModel": "octavia",
        "engineNote": "1.4 TGI, 81 kW – druhá generace koncernového CNG motoru, záměrně zeslabená oproti výchozímu TSI kvůli spolehlivosti. Odlišujte od starší, problematičtější generace 1.4 EcoFuel (110 kW, do cca 2013), která trápily zapékající se benzínové vstřikovače a koroze tlakových nádrží. Novější 1.5 TGI Evo (96 kW, od cca 2020) je zatím bez dostatku dlouhodobých dat. Nádrž (tlaková, výdrž 20 let) potřebuje pravidelnou revizi zhruba v rytmu STK.",
        "image": None,
        "consumptionUnit": "kg CNG/100 km",
    },
    {
        "id": "seat-leon-st-tgi",
        "name": "Seat Leon ST 1.4/1.5 TGI (CNG+benzín)",
        "wikiTitle": "SEAT Leon",
        "brand": "Seat",
        "brandSlug": "seat",
        "category": "kombi",
        "tier": "280k",
        "top": False,
        "trunk": "482 l",
        "price": "190–320 tis. Kč (dle nájezdu, i pod 200 tis. u vyššího nájezdu)",
        "reliability": "Velmi dobrá – stejná osvědčená motorová řada TGI jako Octavia G-TEC",
        "note": "Bi-fuel CNG/benzín na stejné platformě a se stejným motorem jako Octavia G-TEC, jen v Seat karoserii.",
        "pros": [
            "Stejný spolehlivý motor 1.4/1.5 TGI jako Octavia G-TEC",
            "Velký kufr na kombi (482 l i s nádržemi na CNG)",
            "Provoz na CNG výrazně levnější než benzín",
            "Technika sdílená s Octavií/Golfem",
        ],
        "cons": [
            "Méně servisů specializovaných na CNG než u Škody",
            "Vyšší zatížení zadní nápravy váhou nádrží",
            "Revize CNG nádrže nutná pravidelně (zhruba v rytmu STK)",
        ],
        "bazosQuery": "seat leon st tgi cng",
        "sautoModel": "leon",
        "engineNote": "1.4 TGI (81 kW) nebo novější 1.5 TGI (96 kW) – stejná motorová rodina jako u Octavie G-TEC, sdílená platforma VAG. Nádrže (CNG i menší benzínová záložní) jsou pod podlahou kufru, který se tak zmenší na 482 l.",
        "image": None,
        "consumptionUnit": "kg CNG/100 km",
    },
    {
        "id": "seat-arona-tgi",
        "name": "Seat Arona 1.0 TGI (CNG+benzín)",
        "wikiTitle": "SEAT Arona",
        "brand": "Seat",
        "brandSlug": "seat",
        "category": "suv",
        "tier": "280k",
        "top": False,
        "trunk": "282 l",
        "price": "190–320 tis. Kč (i pod 200 tis. při vysokém nájezdu/dovozu)",
        "reliability": "Dobrá, ale zatím bez dlouhodobých zkušeností (mladší motor 1.0 TGI)",
        "note": "Bi-fuel CNG/benzín, malé městské SUV. Motor je novější a méně proježděný než u Octavie, takže dlouhodobá spolehlivost není tak ověřená.",
        "pros": [
            "Provoz na CNG levnější než na benzín i u menšího motoru",
            "Motor uzpůsobený přímo pro CNG (upravená hlava, vačky, odolnější ventily) – podobná filozofie jako u osvědčené Octavie G-TEC",
            "Kompaktní SUV, snazší parkování ve městě",
            "Servisní síť Seat/Škoda",
        ],
        "cons": [
            "Malý kufr (282 l) kvůli nádržím na CNG",
            "Reálná spotřeba CNG bývá vyšší než papírová hodnota – downsizing tříválce se s CNG úplně nepovedl",
            "Zatím málo najetých kilometrů v provozu, dlouhodobá spolehlivost neověřená jako u Octavie",
            "Servis vyžaduje specializovaného mechanika pro CNG",
        ],
        "bazosQuery": "seat arona tgi cng",
        "sautoModel": "arona",
        "engineNote": "1.0 TGI, 66–90 kW – tříválec upravený speciálně pro CNG (jiné vačky, hlava, vstřikovače, odolnější výfukové ventily), stejná technika jako u Kamiqu a Ibizy. Oficiální spotřeba cca 3,8–4,4 kg/100 km, reálně častěji hlášeno 5–6 kg/100 km.",
        "image": None,
        "consumptionUnit": "kg CNG/100 km",
    },
    {
        "id": "skoda-kamiq-gtec",
        "name": "Škoda Kamiq G-TEC 1.0 TGI (CNG+benzín)",
        "wikiTitle": "Škoda Kamiq",
        "brand": "Škoda",
        "brandSlug": "skoda",
        "category": "suv",
        "tier": "vyrazeno",
        "top": False,
        "trunk": "278 l",
        "price": "340–480 tis. Kč (nad rozpočtem)",
        "reliability": "Dobrá, ale zatím bez dlouhodobých zkušeností (stejný mladší motor 1.0 TGI jako Arona/Ibiza)",
        "note": "Bi-fuel CNG/benzín, malé SUV. V bazaru vychází nad váš rozpočet, ale pro srovnání se hodí.",
        "pros": [
            "Stejný CNG motor jako u Arony/Ibizy, uzpůsobený přímo pro plyn",
            "Škoda servisní síť dostupná všude",
            "Provoz na CNG levnější než na benzín",
            "Modernější výbava a bezpečnostní asistenty než starší modely",
        ],
        "cons": [
            "Malý kufr (278 l) kvůli nádržím na CNG",
            "V bazaru spíš nad rozpočtem (~340 tis. Kč a víc)",
            "Zatím málo najetých kilometrů, dlouhodobá spolehlivost neověřená jako u Octavie",
            "Servis vyžaduje specializovaného mechanika pro CNG",
        ],
        "bazosQuery": "škoda kamiq g-tec cng",
        "sautoModel": "kamiq",
        "engineNote": "1.0 TGI, 66 kW – stejný tříválec jako Seat Arona/Ibiza, upravený přímo pro CNG. Oficiální spotřeba cca 3,8–4,4 kg/100 km, reálně častěji 5–6 kg/100 km.",
        "image": None,
        "consumptionUnit": "kg CNG/100 km",
    },
]


def main():
    cars = json.loads(CARS_JSON.read_text(encoding="utf-8"))
    existing_ids = {c["id"] for c in cars}
    added = 0
    for car in NEW_CARS:
        if car["id"] in existing_ids:
            continue
        cars.append(car)
        added += 1
    CARS_JSON.write_text(
        json.dumps(cars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Pridano {added} novych CNG modelu, celkem aut: {len(cars)}")


if __name__ == "__main__":
    main()
