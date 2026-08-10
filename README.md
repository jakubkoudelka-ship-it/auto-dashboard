# Vybíráme auto pro Koudelkovy – dashboard

Interaktivní dashboard nad tržním researchem ojetých aut (kombi/MPV/SUV, benzín, rozpočet do cca 320 tis. Kč). Vznikl jako nástavba nad textovým reportem — cílem je mít místo statického dokumentu živý přehled s fotkami, filtry a odkazy na aktuální inzeráty.

## Co to umí

- **66 modelů** rozdělených do kategorií (kombi / MPV / SUV / užitkové), s filtrováním podle karoserie, cenového pásma a fulltextovým hledáním.
- **Fotky aut se načítají živě** z [Wikipedia REST API](https://en.wikipedia.org/api/rest_v1/) přímo v prohlížeči (žádné stažené obrázky v repozitáři) — funguje to i po nasazení na GitHub Pages. Pokud se fotka nenajde, zobrazí se ikona podle typu karoserie.
- **Detail auta** (klik na kartu): klady/zápory, spolehlivost, kufr, cenové rozpětí, a tlačítka na **předfiltrované hledání** na Sauto.cz a Bazoš.cz.
- Připravená (volitelná) integrace se scraperem — jakmile jednou vygenerujete `data/listings.json`, dashboard v detailu auta automaticky zobrazí i konkrétní nalezené inzeráty.

## Jak to spustit

Nejjednodušší je otevřít `index.html` přímo v prohlížeči. Pokud váš prohlížeč blokuje `fetch()` na lokální soubory (typicky Chrome), spusťte místo toho jednoduchý lokální server:

```bash
cd auto-dashboard
python3 -m http.server 8000
# otevřete http://localhost:8000
```

## Nasazení na GitHub Pages

1. Nahrajte obsah této složky do repozitáře na GitHub.
2. V nastavení repozitáře: **Settings → Pages → Source: Deploy from branch**, větev `main`, složka `/root`.
3. Po chvíli poběží na `https://<vas-github-username>.github.io/<nazev-repo>/`.

Žádný build krok není potřeba — je to čistý HTML/CSS/JS.

## Živé inzeráty — realita a jak to rozjet doopravdy

Přímý scraping Sauto.cz/Bazoš.cz **z prohlížeče** nejde — weby to blokují přes CORS a robotickou ochranu. Dashboard proto řeší "živé nabídky" dvěma úrovněmi:

1. **Funguje hned:** tlačítka „aktuální nabídka" v detailu auta otevřou už předvyplněné hledání přímo na Sauto.cz / Bazoš.cz v nové záložce.
2. **Volitelné rozšíření:** `scripts/scrape_bazos.py` je prototyp scraperu pro Bazoš.cz + `.github/workflows/update-listings.yml` je scaffold pro pravidelné (denní) spouštění přes GitHub Actions, které by výsledky commitovalo do `data/listings.json`. Dashboard tento soubor automaticky vyzvedne, pokud existuje.

**Než workflow zapnete, prosím:**
- Spusťte scraper lokálně (`python scripts/scrape_bazos.py --limit 3`) a zkontrolujte, že CSS selektory v `scripts/scrape_bazos.py` odpovídají aktuální struktuře webu — vznikl v sandboxu bez přístupu k živému internetu, takže **nebyl testován proti reálné stránce**, jen proti fabrikovanému HTML se stejnou strukturou, jakou web tradičně používal.
- Zkontrolujte `robots.txt` a podmínky použití cílového webu, ať scraping nejede v rozporu s nimi.

## Struktura repozitáře

```
auto-dashboard/
├── index.html              # struktura stránky
├── styles.css               # vzhled
├── app.js                   # veškerá logika (filtry, modal, fetch fotek/inzerátů)
├── data/
│   ├── cars.json             # data o všech 66 modelech (zdroj pravdy pro dashboard)
│   └── listings.json         # generuje scraper, volitelné, zatím neexistuje
├── scripts/
│   ├── scrape_bazos.py       # prototyp scraperu pro Bazoš.cz
│   └── requirements.txt
└── .github/workflows/
    └── update-listings.yml   # scaffold pro denní automatickou aktualizaci
```

## Jak přidat/upravit model

Stačí upravit `data/cars.json` — žádný build krok, změna se projeví po refreshi stránky. Pole u každého modelu:

| Pole | Význam |
|---|---|
| `wikiTitle` | název článku na Wikipedii, podle kterého se hledá fotka |
| `category` | `kombi` / `mpv` / `suv` / `uzitkove` |
| `tier` | `200k` / `280k` / `vyrazeno` / `avoid` — cenové pásmo pro filtr a limit v odkazech na inzeráty |
| `top` | `true` u modelů s odznakem ★ top doporučení |
| `brandSlug` | slug značky pro odkaz na Sauto.cz (např. `skoda`, `toyota`) |
| `bazosQuery` | dotaz použitý pro vyhledávání na Bazoš.cz |

## Známá omezení

- Fotky z Wikipedie odpovídají obecnému článku o modelu, ne nutně přesné generaci/karoserii popsané v kartě.
- `brandSlug` u Sauto.cz odkazů je na úrovni značky (ne konkrétního modelu) — spolehlivější než hádání přesných URL slugů jednotlivých modelů, ale znamená to širší výsledky hledání.
- Scraper je needotestovaný prototyp (viz sekce výše).
