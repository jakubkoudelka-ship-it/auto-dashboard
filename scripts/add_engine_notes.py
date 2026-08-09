# -*- coding: utf-8 -*-
"""Jednorázový skript: doplní pole engineNote (a volitelně extraPro/extraCon)
do data/cars.json. Spustit z /auto-dashboard: python3 scripts/add_engine_notes.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARS_JSON = ROOT / "data" / "cars.json"

DATA = {
    "skoda-octavia2-combi": {
        "engineNote": "V nabídce byly tři motorizace: 1.6 MPI (75 kW, nepřímé vstřikování, rozvodový řemen) je nejjednodušší a nejprověřenější volba – desítky let ověřená technika bez rizika karbonizace z přímého vstřiku. 1.6 FSI (přímé vstřikování) se nedoporučuje, trpí zanášením sacích ventilů karbonem. 1.6/2.0 TSI (od cca 2010) je výkonnější, ale u ročníků před 2012 má často problém s poddimenzovaným napínákem rozvodového řetězu – řetěz se natahuje a v horším případě přeskočí o zub. Pro váš profil (krátké městské trasy) jednoznačně doporučujeme 1.6 MPI: nejnižší riziko poruchy a nejlevnější servis.",
        "extraPro": "1.6 MPI je nejbezpečnější motor z nabídky – bez turba, bez přímého vstřiku",
        "extraCon": "1.6 FSI a rané TSI (do 2012) raději vynechte",
    },
    "fiat-tipo-kombi": {
        "engineNote": "Motor 1.4 16V (rodina FIRE/E.torQ) je atmosférický, s nepřímým vstřikováním a rozvodovým řemenem (výměna cca každých 120 000 km / 5 let). Nemá turbo ani přímé vstřikování, takže odpadá riziko karbonizace sacích ventilů i zanášení GPF. Slabším bodem bývá jen hlučnější chod a nižší výkon, mechanicky je ale nenáročný a levný na opravy. Turbo verzi 1.4 T-Jet bychom pro váš profil krátkých městských tras nedoporučovali – přímé vstřikování a turbo znamenají vyšší riziko karbonizace.",
        "extraPro": "Bez turba a bez GPF – ideální pro krátké městské trasy",
        "extraCon": "Verzi 1.4 T-Jet pro váš profil nedoporučujeme",
    },
    "toyota-avensis-corolla-verso": {
        "engineNote": "Motor 1.8 VVT-i (1ZZ-FE) má rozvodový řetěz, ale ročníky vyrobené před rokem 2005 trpí zvýšenou spotřebou oleje kvůli poddimenzovaným olejovým kanálkům v pístech – vada byla opravena až v roce 2005. Před koupí bezpodmínečně zkontrolujte spotřebu oleje na delší zkušební jízdě, případně hledejte novější kus (po 2005) nebo pozdější motor 1ZR-FE/2ZR-FE, který touto vadou netrpí. Jinak jde o typicky toyotí nenáročný a odolný motor bez turba a bez GPF.",
        "extraPro": "Motory po roce 2005 už nemají vadu s olejem",
        "extraCon": "U starších kusů (před 2005) hlídejte spotřebu oleje",
    },
    "ford-mondeo-combi": {
        "engineNote": "Motor 2.0 Duratec pochází z dílny Mazdy a na rozdíl od menších fordích jednotek 1.6/1.8 má rozvodový řetěz místo řemenu – odpadá tak riziko spojené s opomenutou výměnou řemenu. Je atmosférický, s nepřímým vstřikováním, takže bez rizik spojených s karbonizací od přímého vstřiku. Patří mezi nejspolehlivější fordí benzínové motory té doby.",
        "extraPro": "Rozvodový řetěz místo řemenu (motor vyvinutý s Mazdou)",
        "extraCon": "I přesto sledujte pravidelnou výměnu oleje",
    },
    "ford-focus-combi": {
        "engineNote": "Motor 1.6 (rodina Sigma/Duratec Ti-VCT) má rozvodový řemen s intervalem cca 160 000 km – klíčové je mít doloženou výměnu, protože jde o kolizní motor (při přetržení řemenu se ohnou ventily). Nemá hydraulické zdvihátka, takže je potřeba jednou za 150–160 tis. km nechat seřídit ventilové vůle, což majitelé často zanedbávají. Jinak je to jednoduchý atmosférický motor bez turba a bez přímého vstřikování.",
        "extraPro": "Bez turba, bez přímého vstřikování",
        "extraCon": "Nutné pravidelné seřizování ventilových vůlí (chybí hydrokompenzátory)",
    },
    "kia-ceed-hyundai-i30-combi": {
        "engineNote": "V tomto ročníku (2007–2012) šlo většinou ještě o starší motor Beta 1.6 16V s rozvodovým řemenem (interval cca 90–100 tis. km, kolizní motor). Novější přímovstřikovaný Gamma 1.6 GDI dorazil až později (cca od 2011) a v tomto rozpočtu se téměř nevyskytuje. Motor je nenáročný, hlavní riziko je jen zanedbaná výměna řemenu – vyžádejte si doklad o servisu.",
        "extraPro": "Jednoduchý atmosférický motor bez turba",
        "extraCon": "Kolizní rozvodový řemen – vyžádejte si doklad o výměně",
    },
    "mazda6-kombi": {
        "engineNote": "Atmosférický motor 2.0 z rodiny MZR (vyvinutý společně s Fordem, sourozenec Duratecu) má rozvodový řetěz a je bez turba i přímého vstřikování. Patří mezi nejodolnější motory své doby a zvládá vysoké nájezdy bez zásahu do rozvodu – hlavní podmínkou je jen pravidelná výměna oleje.",
        "extraPro": "Rozvodový řetěz, bez turba, bez přímého vstřiku",
        "extraCon": "Hlučnější chod ve vyšších otáčkách",
    },
    "peugeot-308-sw": {
        "engineNote": "Starší atmosférický motor 1.6 16V VTi (bez turba, nepřímé vstřikování) je oproti novější přeplňované verzi 1.6 THP jednoznačně bezpečnější volbou. THP totiž trpí karbonizací sacích ventilů a natahováním rozvodového řetězu (v extrémních případech i po 40–50 tis. km), oprava vyjde na 15–50 tis. Kč. U atmosférické 1.6 16V VTi tato rizika odpadají – zaplatíte za to nižším výkonem.",
        "extraPro": "Atmosférická 1.6 16V bez rizik karbonizace",
        "extraCon": "Přeplňované verzi THP (pokud na ni narazíte) se vyhněte",
    },
    "seat-leon-st": {
        "engineNote": "Stejný motor 1.6 MPI jako u Octavie (koncernový EA111, nepřímé vstřikování, rozvodový řemen) – jde o nejjednodušší a nejprověřenější motorizaci VAG koncernu z té doby, bez rizik spojených s přímým vstřikováním nebo turbem.",
        "extraPro": "Stejně bezpečný motor jako Octavia/Golf (1.6 MPI)",
        "extraCon": "U vyšších nájezdů zkontrolujte historii výměny rozvodového řemene",
    },
    "volvo-v70-v50": {
        "engineNote": "Pětiválec 2.4i (B5244) má rozvodový řemen s intervalem 120 000 km – jde o kolizní motor, takže bez doloženého servisu rozvodu byste ho neměli kupovat. Motor je jinak mechanicky odolný, sledovanou slabinou je vyšší spotřeba oleje u starších kusů. Menší 1.8 (u V50) je technicky jednodušší, ale méně výkonný a stále vyžaduje hlídání rozvodového řemene.",
        "extraPro": "Mechanicky odolný pětiválec",
        "extraCon": "Kolizní rozvodový řemen (120 tis. km) – bez dokladu o výměně nekupovat",
    },
    "skoda-roomster-rapid": {
        "engineNote": "Motor 1.2 TSI (EA111, tříválec s turbem a přímým vstřikováním) má rozvodový řetěz, jehož napínač byl u kusů vyrobených před polovinou roku 2011 poddimenzovaný – řetěz se natahoval už mezi 30 000 a 100 000 km, v krajním případě přeskočil o zub a poškodil ventily. Od listopadu 2011 je díl posílený (širší řetěz, nová vodítka, lepší napínák). Před koupí bezpodmínečně ověřte, zda byl napínák vyměněn za posílenou verzi, nebo zvolte pozdější ročník.",
        "extraPro": "Od listopadu 2011 vylepšený, posílený napínák řetězu",
        "extraCon": "U starších kusů hrozí natažení řetězu už od 30 tis. km",
    },
    "dacia-logan-mcv": {
        "engineNote": "Motor 1.6 16V (rodina Renault K4M) je stejný jako u Duster/Dokker – jednoduchý atmosférický motor s rozvodovým řetězem. Napínač řetězu je dobré nechat zkontrolovat kolem 80–100 tis. km, jinak jde o nenáročnou a levnou techniku bez turba a bez GPF.",
        "extraPro": "Stejný osvědčený motor jako Duster/Dokker",
        "extraCon": "Kontrola napínače rozvodového řetězu kolem 80–100 tis. km",
    },
    "renault-megane-grandtour": {
        "engineNote": "Stejná motorizace 1.6 16V K4M jako u Duster/Loganu – rozvodový řetěz, kontrola napínače doporučená kolem 80–100 tis. km. Bez turba a přímého vstřikování, takže nehrozí karbonizace ani zanášení GPF.",
        "extraPro": "Bez turba a bez GPF",
        "extraCon": "Kontrola napínače rozvodového řetězu doporučená",
    },
    "vw-golf-passat-variant": {
        "engineNote": "V tomto rozpočtu byste narazili na starší motory 1.4/1.6 (EA111) nebo 2.0 (EA113/EA888) – zásadně upřednostněte atmosférické MPI verze před FSI/TSI kvůli riziku karbonizace a (u 1.2/1.4 TSI) natahování rozvodového řetězu. Realisticky je ale celý tento pár mimo rozpočet ve slušném stavu.",
        "extraPro": "MPI verze jsou bezpečnější než FSI/TSI",
        "extraCon": "1.2/1.4 TSI trpí stejným problémem s řetězem jako u menších modelů (Yeti/Roomster)",
    },
    "citroen-c4-c5-tourer": {
        "engineNote": "Atmosférickým motorům 1.6/2.0 16V (rodina EW) se nevyhýbejte – jsou bez turba, s nepřímým vstřikováním, a i přes vyšší spotřebu oleje u starších kusů patří mezi nejspolehlivější motory PSA koncernu. Přeplňovanému 1,6 THP se ale vyhněte úplně – trpí karbonizací sacích ventilů a natahováním rozvodového řetězu (oprava 15–50 tis. Kč).",
        "extraPro": "Atmosférická 1.6/2.0 EW je bezpečnější než THP",
        "extraCon": "Přeplňovanému 1.6 THP se vyhněte úplně",
    },
    "mazda-premacy-5": {
        "engineNote": "Starší atmosférické benzínové motory 1.6/1.8/2.0 (bez turba, nepřímé vstřikování) mají rozvodový řemen – ověřte si servisní historii výměny. Jinak jde o jednoduchou a odolnou techniku bez GPF a bez rizik spojených s přímým vstřikováním.",
        "extraPro": "Jednoduchá atmosférická technika bez GPF",
        "extraCon": "Ověřte historii výměny rozvodového řemene",
    },
    "seat-altea-xl": {
        "engineNote": "Stejný motor 1.6 MPI jako Octavia/Leon (EA111, nepřímé vstřikování, rozvodový řemen) – jde o nejjednodušší a nejbezpečnější volbu z celé nabídky motorů VAG té doby.",
        "extraPro": "Stejný bezpečný motor jako Octavia/Golf/Leon",
        "extraCon": "Sledujte historii výměny rozvodového řemene",
    },
    "fiat-500l": {
        "engineNote": "Preferujte atmosférický 1.4 16V (FIRE, nepřímé vstřikování, rozvodový řemen) před přeplňovaným 1.4 T-Jet (turbo, přímé vstřikování, vyšší riziko karbonizace při krátkých městských trasách). Motoru 0.9 TwinAir se vyhněte úplně – má nejvíc stížností na spolehlivost turba a rozvodového řetězu.",
        "extraPro": "Preferujte atmosférickou 1.4 16V před T-Jet",
        "extraCon": "Motoru 0.9 TwinAir se vyhněte úplně",
    },
    "opel-zafira": {
        "engineNote": "U starších motorů řady Z16XE/X16XEL (do cca 2005) je rozvodový řemen nutné měnit už po 60 000 km – jde o kolizní motor. Novější Z16XER má interval až 150 000 km. Před koupí bezpodmínečně zjistěte přesný kód motoru a ověřte servisní historii rozvodu, protože rozdíl v intervalu je zásadní.",
        "extraPro": "Novější Z16XER má bezpečnější interval řemene (150 tis. km)",
        "extraCon": "Starší kódy (do cca 2005) mají jen 60 tis. km interval – ověřte kód motoru",
    },
    "renault-grand-scenic": {
        "engineNote": "Stejná motorizace 1.6 16V K4M jako u Duster/Megane – rozvodový řetěz, doporučená kontrola napínače kolem 80–100 tis. km.",
        "extraPro": "Stejný osvědčený motor K4M jako Duster",
        "extraCon": "Kontrola napínače rozvodového řetězu doporučená",
    },
    "vw-sharan-galaxy-alhambra": {
        "engineNote": "Benzínové verze bývají obvykle 1.8T/2.0 (přeplňované, u starších generací i s rozvodovým řemenem) – v tomto rozpočtu ale narazíte téměř výhradně na dieselové kusy, benzín je vzácný a najít dobře udržovaný exemplář je náročné.",
        "extraPro": "Motor 1.8T/2.0 je při dobré péči odolný",
        "extraCon": "Benzínové kusy jsou vzácné, hůř se ověřuje historie",
    },
    "dacia-duster1": {
        "engineNote": "Motor 1.6 16V (Renault K4M) je jednoduchý atmosférický motor s rozvodovým řetězem bez turba a bez GPF – ideální pro krátké městské trasy. Jediné riziko je napínač řetězu, který doporučujeme nechat zkontrolovat kolem 80–100 tis. km, pak už motor obvykle bez problémů zvládá 250 000+ km.",
        "extraPro": "Bez turba a bez GPF – ideální pro krátké trasy",
        "extraCon": None,
    },
    "nissan-qashqai1": {
        "engineNote": "Motor 1.6 16V má bezúdržbový rozvodový řetěz, který je obecně velmi spolehlivý – jen napínače je dobré nechat zkontrolovat kolem 100–150 tis. km. Bez turba a bez přímého vstřikování, takže bez rizika karbonizace.",
        "extraPro": "Bez turba, bez přímého vstřikování",
        "extraCon": "Napínače řetězu zkontrolovat kolem 100–150 tis. km",
    },
    "hyundai-ix35": {
        "engineNote": "Motory 1.6/2.0 (rodina Gamma/Nu) mají rozvodový řetěz s variabilním časováním (CVVT) – patří mezi spolehlivější korejské motory té doby, hlavní podmínkou je pravidelná výměna oleje a kontrola hydraulických napínačů. Atmosférické verze bez turba jsou bezpečnější volba než pozdější přeplňované GDI/T-GDI jednotky.",
        "extraPro": "Rozvodový řetěz s CVVT, atmosférické verze bez turba",
        "extraCon": "Preferujte atmosférickou verzi před pozdějšími GDI/T-GDI",
    },
    "mitsubishi-asx": {
        "engineNote": "Motor 1.6 MIVEC (4A92) má rozvodový řetěz a je považován za velmi spolehlivý, atmosférický, bez přímého vstřikování. Patří mezi hlavní důvody, proč se ASX v tomto rozpočtu tak dobře hodnotí – nemá typické neduhy přeplňovaných downsizovaných motorů.",
        "extraPro": "Rozvodový řetěz, bez přímého vstřikování",
        "extraCon": "Menší nabídka na trhu",
    },
    "suzuki-sx4": {
        "engineNote": "Motor 1.6 VVT (M16A) má rozvodový řetěz s unikátním napínačem podobným motocyklovým motorům, který udrží řetěz napnutý i po vypnutí motoru – proto je extrémně tichý a spolehlivý i při vysokých nájezdech, poruchy rozvodu jsou prakticky neznámé. Jedna z nejspolehlivějších motorizací v celém přehledu.",
        "extraPro": "Unikátní napínač řetězu – extrémně tichý a spolehlivý i při vysokých nájezdech",
        "extraCon": "Nižší výkon, menší prostornost",
    },
    "suzuki-vitara-new": {
        "engineNote": "Aktuální generace už často nabízí přeplňovaný 1.4 Boosterjet s přímým vstřikováním – modernější, ale komplexnější technika. V tomto rozpočtu se k němu ale prakticky nedostanete, cena je zcela mimo dosah.",
        "extraPro": None,
        "extraCon": "Modernější Boosterjet je komplexnější technika",
    },
    "skoda-yeti": {
        "engineNote": "Motory 1.2 TSI a 1.4 TSI (EA111) mají rozvodový řetěz se stejnou slabinou jako Roomster/Octavia – u kusů vyrobených před polovinou 2011 hrozí natahování řetězu kvůli poddimenzovanému napínači. Vyžádejte si doklad o kontrole/výměně napínače nebo zvolte pozdější ročník s vylepšeným dílem.",
        "extraPro": "Od poloviny 2011 vylepšený napínák řetězu",
        "extraCon": "U starších kusů ověřte výměnu napínače",
    },
    "subaru-forester": {
        "engineNote": "Atmosférický motor 2.0 (FB20) má výrobcem deklarovaný bezúdržbový rozvodový řetěz, hlavní slabinou je ale zvýšená spotřeba oleje – při zanedbaných intervalech výměny (doporučeno měnit i častěji než udává výrobce, cca každých 7 500 km) hrozí zadření pístních kroužků. Sledujte hladinu oleje mezi výměnami.",
        "extraPro": "Bezúdržbový rozvodový řetěz",
        "extraCon": "Sledujte hladinu oleje mezi výměnami (vyšší spotřeba)",
    },
    "honda-crv-civic-tourer": {
        "engineNote": "Motor 1.8 i-VTEC (R18A) má úzký a tichý rozvodový řetěz bez zaznamenaných hromadných poruch, nespotřebovává nadměrně olej ani chladicí kapalinu a při pravidelných výměnách oleje (5–10 tis. km) zvládá 250 000–300 000 km bez zásahu. Patří mezi nejspolehlivější benzínové motory v celém přehledu.",
        "extraPro": "Jeden z nejspolehlivějších benzínových motorů v celém přehledu",
        "extraCon": None,
    },
    "tucson-sportage-moderni": {
        "engineNote": "Moderní generace nabízí přímovstřikované motory Gamma/Smartstream (často i s turbem), technicky vyspělejší, ale komplexnější a citlivější na krátké městské trasy (riziko karbonizace a zanášení GPF). V tomto rozpočtu je ale celý model mimo dosah.",
        "extraPro": None,
        "extraCon": "Modernější GDI/T-GDI motory jsou citlivější na krátké trasy",
    },
    "dacia-dokker": {
        "engineNote": "Stejný motor K4M 1.6 16V jako Duster – rozvodový řetěz, doporučená kontrola napínače kolem 80–100 tis. km, jinak nenáročná a levná technika.",
        "extraPro": "Stejný osvědčený motor jako Duster",
        "extraCon": "Kontrola napínače rozvodového řetězu doporučená",
    },
    "renault-kangoo": {
        "engineNote": "Motor 1.6 16V K4M je stejná osvědčená technika jako u Duster/Loganu – rozvodový řetěz, atmosférický, bez GPF. Starší generace mohou mít i jednodušší 1.4/1.6 8V s rozvodovým řemenem – ověřte si konkrétní motorizaci a servisní historii.",
        "extraPro": "Bez GPF, atmosférický motor",
        "extraCon": "U starších generací ověřte, zda má řemen, nebo řetěz",
    },
    "partner-tepee-berlingo": {
        "engineNote": "Atmosférické motory 1.4/1.6 16V (bez turba, nepřímé vstřikování) jsou bezpečnější volbou než přeplňovaný VTi Turbo/THP. Rozvodový řemen bývá potřeba měnit v intervalu výrobce – vyžádejte si doklad o poslední výměně.",
        "extraPro": "Atmosférické verze bez rizik turba/GDI",
        "extraCon": "Ověřte historii výměny rozvodového řemene",
    },
    "fiat-doblo": {
        "engineNote": "Motor 1.4 16V (FIRE) je atmosférický s nepřímým vstřikováním a rozvodovým řemenem (interval cca 120 tis. km / 5 let) – jednoduchá a odolná technika bez rizik spojených s turbem nebo přímým vstřikováním.",
        "extraPro": "Bez turba, bez přímého vstřikování",
        "extraCon": "Ověřte historii výměny rozvodového řemene (120 tis. km)",
    },
    "citroen-c4-picasso": {
        "engineNote": "Atmosférický 1.6 VTi (bez turba, nepřímé vstřikování) je bezpečnější volba než přeplňovaný 1.6 THP, který trpí karbonizací a natahováním rozvodového řetězu. Staré robotizované převodovky (pokud na ně narazíte) se také raději vyhněte – manuál nebo klasický automat je jistější.",
        "extraPro": "Atmosférická 1.6 VTi je bezpečnější než THP",
        "extraCon": "Přeplňovanému THP se vyhněte úplně",
    },
    "ford-cmax": {
        "engineNote": "Pro těžší karoserii C-Maxu doporučujeme raději 1.8 nebo 2.0 Duratec před slabším 1.6 – u větších motorů (1.8/2.0) je typicky rozvodový řetěz (odvozeno od Mazdy), zatímco menší 1.6 Sigma/Ti-VCT má rozvodový řemen s intervalem 160 tis. km a navíc vyžaduje pravidelné seřizování ventilových vůlí.",
        "extraPro": "1.8/2.0 mají rozvodový řetěz (na rozdíl od 1.6)",
        "extraCon": "1.6 navíc vyžaduje pravidelné seřizování ventilových vůlí",
    },
    "ford-smax": {
        "engineNote": "Benzínové verze bývají 1.8/2.0 Duratec s rozvodovým řetězem, ale na trhu v tomto rozpočtu naprosto převažují diesely – najít dobře udržovaný benzín je náročné.",
        "extraPro": "Benzínové 1.8/2.0 mají rozvodový řetěz",
        "extraCon": "Na trhu silně převažují diesely",
    },
    "kia-carens": {
        "engineNote": "V tomto ročníku šlo většinou o starší motor Beta 1.6/2.0 16V s rozvodovým řemenem (kolizní motor, interval cca 90–100 tis. km) – před koupí ověřte doklad o výměně.",
        "extraPro": "Jednoduchý atmosférický motor",
        "extraCon": "Kolizní rozvodový řemen – ověřte servisní historii",
    },
    "toyota-verso": {
        "engineNote": "Sdílí základ i motorizaci s Corolla Verso/Avensis (1.8 VVT-i, 1ZZ-FE) – stejně jako u Avensis platí, že starší kusy (před 2005) mohou mít zvýšenou spotřebu oleje kvůli konstrukční vadě pístních kroužků. Preferujte novější ročník nebo si při zkušební jízdě ověřte spotřebu oleje.",
        "extraPro": "Sdílí spolehlivou toyotí techniku s Avensis",
        "extraCon": "Starší kusy (před 2005) hlídejte na spotřebu oleje",
    },
    "mitsubishi-outlander": {
        "engineNote": "Starší benzínový motor 2.4 (4B12) má rozvodový řetěz a je typicky japonsky odolný, hlavní nevýhodou je vyšší spotřeba paliva u těžšího SUV. Bez turba a bez přímého vstřikování, takže bez rizik karbonizace.",
        "extraPro": "Rozvodový řetěz, bez turba",
        "extraCon": "Menší nabídka benzínových kusů na trhu",
    },
    "suzuki-grand-vitara": {
        "engineNote": "Atmosférický motor 2.0 (J20A) má rozvodový řemen s intervalem cca 100 tis. km – jednoduchá technika bez turba, o něco hlučnější a náročnější na spotřebu při vyšších otáčkách, ale mechanicky nenáročná.",
        "extraPro": "Jednoduchá atmosférická technika",
        "extraCon": "Ověřte historii výměny rozvodového řemene (100 tis. km)",
    },
    "lada-niva": {
        "engineNote": "Motor 1.7i (odvozený z Fiatu, injekční verze) má rozvodový řetěz, který podle zkušeností majitelů vydrží statisíce kilometrů i při zanedbané údržbě. Jde o extrémně jednoduchou a odolnou techniku – starší karburátorové verze jsou ještě jednodušší (bez elektroniky), ale hůř se u nich shání náhradní díly a splňují nižší emisní normy.",
        "extraPro": "Řetěz vydrží statisíce km i při zanedbané údržbě",
        "extraCon": "Karburátorové verze mají horší dostupnost dílů",
    },
    "toyota-auris-touring": {
        "engineNote": "Novější motory 1.6/1.8 Valvematic (typicky 1ZR-FAE/2ZR-FAE) už nemají problém se spotřebou oleje jako starší 1ZZ-FE – jde o moderní, ale stále atmosférické (bez turba) a spolehlivé motory s rozvodovým řetězem.",
        "extraPro": "Novější motory bez vady s olejem jako u staršího 1ZZ-FE",
        "extraCon": "Ověřte přesný kód motoru (Valvematic vs starší 1ZZ)",
    },
    "opel-astra-combi": {
        "engineNote": "Stejná rodina motorů jako u Zafiry – u starších kódů (X16XEL, Z16XE, do cca 2005) je rozvodový řemen nutné měnit už po 60 000 km, u novějších (Z16XER/A16XER) až po 150 000 km. Bezpodmínečně ověřte konkrétní kód motoru a servisní historii rozvodu.",
        "extraPro": "Novější kódy mají bezpečnější interval řemene",
        "extraCon": "Starší kódy (do 2005) mají jen 60 tis. km interval – ověřte kód motoru",
    },
    "opel-insignia-combi": {
        "engineNote": "Novější motory řady Family1/Ecotec (1.6/1.8) mají prodloužený interval rozvodového řemene až 150 000 km – bezpečnější volba než starší generace. Auto je ale ve slušném stavu spíš nad rozpočtem.",
        "extraPro": "Prodloužený interval rozvodového řemene (150 tis. km)",
        "extraCon": None,
    },
    "skoda-superb-combi": {
        "engineNote": "U první generace (2001–2008) byste narazili hlavně na motory 1.8T/2.0 FSI (EA113) – přímé vstřikování s rizikem karbonizace sacích ventilů. Bezpečnější volbou by byl atmosférický 2.0 MPI, pokud se najde, ale celé auto je v tomto rozpočtu prakticky nedostupné.",
        "extraPro": None,
        "extraCon": "1.8T/2.0 FSI má riziko karbonizace sacích ventilů",
    },
    "hyundai-i40-combi": {
        "engineNote": "Benzínový motor 1.6/2.0 GDI (přímé vstřikování) je modernější, ale citlivější na krátké městské trasy kvůli riziku karbonizace sacích ventilů. Na trhu navíc benzín silně ustupuje naftě – většina nabídky jsou diesely.",
        "extraPro": None,
        "extraCon": "GDI motory jsou citlivější na krátké městské trasy",
    },
    "chevrolet-daewoo-lacetti": {
        "engineNote": "Motor 1.4/1.6 (F14D3/F16D3) má rozvodový řemen s poměrně krátkým intervalem výměny (cca 60 000 km) – jde o kolizní motor, takže bez dokladu o pravidelné výměně hrozí ohnuté ventily. Motor má i další slabiny (netěsnící víko hlavy, citlivé vstřikovače), proto je to spíš nouzová/přechodná volba.",
        "extraPro": None,
        "extraCon": "Kolizní rozvodový řemen s krátkým intervalem (60 tis. km)",
    },
    "octavia3-14tsi-ea211": {
        "engineNote": "Motor 1.4 TSI EA211 (na rozdíl od staršího EA111) má vyřešený problém s natahováním rozvodového řetězu – nová generace přinesla robustnější napínač i vedení řetězu. Má přímé vstřikování a u ročníků po cca 2017/2018 i GPF, takže se hodí spíš pro časté delší/dálniční jízdy, které filtr pravidelně vypálí. Pro čistě krátké městské trasy zvažte raději 1.6 MPI z předchozí generace nebo přímo 1.6 MPI Octavii III (viz níže).",
        "extraPro": "EA211 má vyřešený problém s řetězem oproti staršímu EA111",
        "extraCon": "Pro čistě městské trasy zvažte raději 1.6 MPI",
    },
    "octavia3-16mpi": {
        "engineNote": "Motor 1.6 MPI je v rámci třetí generace Octavie nejjednodušší volba – nepřímé vstřikování, atmosférický, bez GPF (nepotřebuje ho, protože bez přímého vstřiku nevzniká tolik pevných částic). Ideální právě pro váš profil krátkých městských tras, kde by se GPF u přeplňovaných TSI motorů nestíhal pravidelně vypalovat.",
        "extraPro": "Bez GPF – nejbezpečnější volba pro krátké městské trasy",
        "extraCon": None,
    },
    "duster2-sce": {
        "engineNote": "Motor 1.6 SCe je atmosférický s nepřímým vstřikováním (na rozdíl od přeplňovaného TCe) – nemá GPF a je tak bezpečnější volbou pro krátké městské trasy. Výkonem je slabší než přeplňované verze, ale mechanicky nejjednodušší a nejméně náchylný na karbonizaci.",
        "extraPro": "Bez GPF, nepřímé vstřikování",
        "extraCon": None,
    },
    "octavia3-duster2-evo-avoid": {
        "engineNote": "Nejnovější motory 1.0–1.5 TSI/TCe EVO mají přímé vstřikování a povinný GPF (filtr pevných částic) – ten potřebuje pravidelně dosáhnout vyšších otáček/teplot na delší jízdě, aby se sám vypálil. Při výhradně krátkých městských trasách (váš hlavní profil) hrozí zanášení GPF i karbonizace/ředění oleje palivem u downsizovaných přeplňovaných motorů. Pro váš profil proto tuto motorizaci nedoporučujeme.",
        "extraPro": None,
        "extraCon": None,
    },
}


def main():
    cars = json.loads(CARS_JSON.read_text(encoding="utf-8"))
    missing = [c["id"] for c in cars if c["id"] not in DATA]
    if missing:
        print("CHYBI DATA PRO:", missing)

    updated = 0
    for car in cars:
        info = DATA.get(car["id"])
        if not info:
            continue
        car["engineNote"] = info["engineNote"]
        if info.get("extraPro"):
            car.setdefault("pros", [])
            if info["extraPro"] not in car["pros"]:
                car["pros"].append(info["extraPro"])
        if info.get("extraCon"):
            car.setdefault("cons", [])
            if info["extraCon"] not in car["cons"]:
                car["cons"].append(info["extraCon"])
        updated += 1

    CARS_JSON.write_text(json.dumps(cars, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Hotovo, aktualizovano {updated} z {len(cars)} aut.")


if __name__ == "__main__":
    main()
