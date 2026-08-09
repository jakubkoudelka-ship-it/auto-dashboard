/* ===========================================================
   Výběr rodinného auta – dashboard
   Vanilla JS, no build step. Data: data/cars.json
   Fotky: natahují se živě z Wikipedia REST API (CORS povoleno),
   s fallbackem na ikonu podle karoserie, pokud se fotka nenajde.
   =========================================================== */

const CATEGORY_LABELS = {
  kombi: "Kombi",
  mpv: "MPV",
  suv: "SUV",
  uzitkove: "Užitkové",
};

const CATEGORY_ICONS = {
  kombi: "🚙",
  mpv: "🚐",
  suv: "🚜",
  uzitkove: "📦",
};

const TIER_LABELS = {
  "200k": "do 200 tis. Kč",
  "280k": "280–320 tis. Kč",
  vyrazeno: "nad rozpočtem",
  avoid: "nedoporučeno",
};

const state = {
  cars: [],
  category: "all",
  tier: "all",
  query: "",
  sort: "rank",
  topOnly: false,
  listingsByCarId: {}, // volitelně naplněno z data/listings.json (viz scripts/scrape_bazos.py)
};

/**
 * Zkusí načíst data/listings.json (generuje scripts/scrape_bazos.py přes
 * GitHub Actions, viz .github/workflows/update-listings.yml). Soubor je
 * čistě volitelný — dokud neexistuje, dashboard funguje normálně jen
 * s odkazy "aktuální nabídka" na Sauto.cz / Bazoš.cz.
 */
async function loadListings() {
  try {
    const res = await fetch("data/listings.json");
    if (!res.ok) return;
    const data = await res.json();
    const map = {};
    data.forEach((entry) => {
      map[entry.car_id] = entry;
    });
    state.listingsByCarId = map;
  } catch (e) {
    // soubor zatím neexistuje nebo se stránka otevírá přes file:// — v pořádku, tichý fallback
  }
}

const IMG_CACHE_KEY = "auto-dashboard-img-cache-v1";
function loadImgCache() {
  try {
    return JSON.parse(localStorage.getItem(IMG_CACHE_KEY) || "{}");
  } catch (e) {
    return {};
  }
}
function saveImgCache(cache) {
  try {
    localStorage.setItem(IMG_CACHE_KEY, JSON.stringify(cache));
  } catch (e) {
    /* ignore quota errors */
  }
}
const imgCache = loadImgCache();

async function fetchWikiThumb(title) {
  if (imgCache[title] !== undefined) return imgCache[title];
  try {
    const url =
      "https://en.wikipedia.org/api/rest_v1/page/summary/" +
      encodeURIComponent(title.replace(/ /g, "_"));
    const res = await fetch(url);
    if (!res.ok) throw new Error("not ok");
    const data = await res.json();
    const src = (data.thumbnail && data.thumbnail.source) || null;
    imgCache[title] = src;
    saveImgCache(imgCache);
    return src;
  } catch (e) {
    imgCache[title] = null;
    saveImgCache(imgCache);
    return null;
  }
}

function bazosUrl(car) {
  const cenado = car.tier === "280k" || car.tier === "avoid" ? 350000 : 200000;
  const q = encodeURIComponent(car.bazosQuery);
  return `https://auto.bazos.cz/?hledat=${q}&hlokalita=&humkreis=25&cenaod=&cenado=${cenado}&Submit=Hled%C3%A1n%C3%AD`;
}

function sautoUrl(car) {
  const cenado = car.tier === "280k" || car.tier === "avoid" ? 350000 : 200000;
  const modelPart = car.sautoModel ? `/${encodeURIComponent(car.sautoModel)}` : "";
  return `https://www.sauto.cz/inzerce/osobni/${car.brandSlug}${modelPart}?cena-do=${cenado}&palivo=benzin`;
}

function tierClass(tier) {
  return "t-" + tier;
}

function listingsBlock(car) {
  const entry = state.listingsByCarId[car.id];
  if (!entry) {
    return `<div class="listings-block listings-empty">Živé inzeráty zatím nejsou nastavené — spusťte <code>scripts/scrape_bazos.py</code> přes GitHub Actions (viz README) nebo použijte tlačítka níže.</div>`;
  }
  const n = (entry.listings || []).length;
  const date = new Date(entry.scraped_at);
  const dateStr = isNaN(date) ? "" : date.toLocaleDateString("cs-CZ");
  if (!n) {
    return `<div class="listings-block listings-empty">Poslední kontrola (${dateStr}) nenašla žádné inzeráty v limitu ceny.</div>`;
  }
  const rows = entry.listings
    .slice(0, 5)
    .map((l) => {
      const unverified = l.engine_match !== true;
      const note = unverified
        ? '<span class="listing-engine-note" title="Nadpis inzerátu neobsahuje objem motoru, který hledáme — ověřte motorizaci přímo v inzerátu.">⚠︎ ověřte motorizaci</span>'
        : "";
      return `
      <li>
        <a href="${l.url}" target="_blank" rel="noopener">${l.title}</a>
        <span>${l.price_text || "cena neuvedena"}${l.location ? " · " + l.location : ""} ${note}</span>
      </li>`;
    })
    .join("");
  return `
    <div class="listings-block">
      <div class="listings-head">🔎 ${n} nalezených inzerátů <span class="listings-date">(aktualizováno ${dateStr})</span></div>
      <div class="listings-subnote">Inzeráty s jasně jinou motorizací (nafta, jiný objem) jsou automaticky vyřazené. U ⚠︎ položek nadpis objem motoru neuvádí — ověřte v inzerátu.</div>
      <ul class="listings-list">${rows}</ul>
    </div>
  `;
}

function cardTemplate(car) {
  const catIcon = CATEGORY_ICONS[car.category] || "🚗";
  return `
    <article class="car-card" data-id="${car.id}">
      <div class="car-photo" data-photo="${car.id}">
        <span class="fallback-icon">${catIcon}</span>
        ${car.top ? '<span class="badge-top">★ TOP</span>' : ""}
        <span class="badge-tier ${tierClass(car.tier)}">${TIER_LABELS[car.tier]}</span>
      </div>
      <div class="car-body">
        <span class="car-cat-tag">${CATEGORY_LABELS[car.category]}</span>
        <h3 class="car-name">${car.name}</h3>
        <div class="car-meta">
          <span>🧳 <b>${car.trunk}</b></span>
          <span>💰 <b>${car.price}</b></span>
        </div>
        <p class="car-reliability">${car.reliability}</p>
        <p class="car-note">${car.note}</p>
      </div>
    </article>
  `;
}

function renderStats(filtered) {
  const total = state.cars.length;
  const topCount = state.cars.filter((c) => c.top).length;
  document.getElementById("stats").innerHTML = `
    <div><b>${filtered.length}</b>/${total} modelů</div>
    <div><b>${topCount}</b> ★ top tipy</div>
  `;
}

function applyFilters() {
  let list = state.cars.slice();

  if (state.category !== "all") {
    list = list.filter((c) => c.category === state.category);
  }
  if (state.tier !== "all") {
    list = list.filter((c) => c.tier === state.tier);
  }
  if (state.topOnly) {
    list = list.filter((c) => c.top);
  }
  if (state.query.trim()) {
    const q = state.query.trim().toLowerCase();
    list = list.filter(
      (c) =>
        c.name.toLowerCase().includes(q) || c.brand.toLowerCase().includes(q)
    );
  }

  const tierRank = { "200k": 0, "280k": 1, vyrazeno: 2, avoid: 3 };
  list.sort((a, b) => {
    if (state.sort === "name") return a.name.localeCompare(b.name, "cs");
    if (state.sort === "price") return tierRank[a.tier] - tierRank[b.tier];
    if (state.sort === "trunk") {
      const numA = parseInt((a.trunk.match(/\d+/) || [0])[0], 10);
      const numB = parseInt((b.trunk.match(/\d+/) || [0])[0], 10);
      return numB - numA;
    }
    // default: rank -> top first, then tier, then name
    if (a.top !== b.top) return a.top ? -1 : 1;
    if (tierRank[a.tier] !== tierRank[b.tier])
      return tierRank[a.tier] - tierRank[b.tier];
    return a.name.localeCompare(b.name, "cs");
  });

  return list;
}

function render() {
  const list = applyFilters();
  const grid = document.getElementById("cardGrid");
  const empty = document.getElementById("emptyState");

  renderStats(list);

  if (!list.length) {
    grid.innerHTML = "";
    empty.hidden = false;
    return;
  }
  empty.hidden = true;
  grid.innerHTML = list.map(cardTemplate).join("");

  // wire clicks
  grid.querySelectorAll(".car-card").forEach((el) => {
    el.addEventListener("click", () => openModal(el.dataset.id));
  });

  // lazy-load photos
  list.forEach((car) => {
    fetchWikiThumb(car.wikiTitle).then((src) => {
      if (!src) return;
      const holder = grid.querySelector(`[data-photo="${car.id}"]`);
      if (!holder) return;
      const img = new Image();
      img.src = src;
      img.alt = car.name;
      img.loading = "lazy";
      img.onload = () => {
        holder.querySelector(".fallback-icon")?.remove();
        holder.prepend(img);
      };
    });
  });
}

function openModal(id) {
  const car = state.cars.find((c) => c.id === id);
  if (!car) return;
  const backdrop = document.getElementById("modalBackdrop");
  const content = document.getElementById("modalContent");
  const catIcon = CATEGORY_ICONS[car.category] || "🚗";

  content.innerHTML = `
    <div class="modal-photo" data-photo="modal-${car.id}">
      <span class="fallback-icon">${catIcon}</span>
    </div>
    <div class="modal-body">
      <h2>${car.name}</h2>
      <div class="modal-tags">
        <span class="tag">${CATEGORY_LABELS[car.category]}</span>
        <span class="tag">${TIER_LABELS[car.tier]}</span>
        ${car.top ? '<span class="tag" style="background:#fbe9d9;color:#b5651d;">★ Top doporučení</span>' : ""}
      </div>
      <div class="modal-grid">
        <div class="modal-stat"><div class="label">Kufr</div><div class="value">${car.trunk}</div></div>
        <div class="modal-stat"><div class="label">Cena</div><div class="value">${car.price}</div></div>
        <div class="modal-stat"><div class="label">Spolehlivost</div><div class="value">${car.reliability}</div></div>
        <div class="modal-stat"><div class="label">Značka</div><div class="value">${car.brand}</div></div>
      </div>
      <div class="note-box">${car.note}</div>
      ${car.engineNote ? `<div class="engine-box"><h4>🔧 Motorizace – co vybrat a proč</h4><p>${car.engineNote}</p></div>` : ""}
      <div class="pros-cons">
        <div class="pros">
          <h4>+ Klady</h4>
          <ul>${car.pros.map((p) => `<li>${p}</li>`).join("")}</ul>
        </div>
        <div class="cons">
          <h4>− Zápory</h4>
          <ul>${car.cons.map((p) => `<li>${p}</li>`).join("")}</ul>
        </div>
      </div>
      ${listingsBlock(car)}
      <div class="cta-row">
        <a class="cta-btn primary" target="_blank" rel="noopener" href="${sautoUrl(car)}">Sauto.cz – aktuální nabídka</a>
        <a class="cta-btn" target="_blank" rel="noopener" href="${bazosUrl(car)}">Bazoš.cz – hledat inzeráty</a>
      </div>
    </div>
  `;

  backdrop.classList.add("open");

  fetchWikiThumb(car.wikiTitle).then((src) => {
    if (!src) return;
    const holder = content.querySelector(`[data-photo="modal-${car.id}"]`);
    if (!holder) return;
    const img = new Image();
    img.src = src;
    img.alt = car.name;
    img.onload = () => {
      holder.querySelector(".fallback-icon")?.remove();
      holder.prepend(img);
    };
  });
}

function closeModal() {
  document.getElementById("modalBackdrop").classList.remove("open");
}

function wireControls() {
  document.querySelectorAll("#categoryFilters .pill").forEach((btn) => {
    btn.addEventListener("click", () => {
      document
        .querySelectorAll("#categoryFilters .pill")
        .forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.category = btn.dataset.cat;
      render();
    });
  });

  document.querySelectorAll("#tierFilters .pill").forEach((btn) => {
    btn.addEventListener("click", () => {
      document
        .querySelectorAll("#tierFilters .pill")
        .forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.tier = btn.dataset.tier;
      render();
    });
  });

  document.getElementById("searchBox").addEventListener("input", (e) => {
    state.query = e.target.value;
    render();
  });

  document.getElementById("sortSelect").addEventListener("change", (e) => {
    state.sort = e.target.value;
    render();
  });

  document.getElementById("topOnly").addEventListener("change", (e) => {
    state.topOnly = e.target.checked;
    render();
  });

  document.getElementById("modalClose").addEventListener("click", closeModal);
  document.getElementById("modalBackdrop").addEventListener("click", (e) => {
    if (e.target.id === "modalBackdrop") closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
}

async function init() {
  try {
    const res = await fetch("data/cars.json");
    state.cars = await res.json();
  } catch (e) {
    document.getElementById("cardGrid").innerHTML =
      '<p style="color:#b3261e">Nepodařilo se načíst data/cars.json. Pokud otevíráte soubor přímo (file://), spusťte prosím lokální server, např. <code>python3 -m http.server</code>, kvůli omezením prohlížeče na načítání lokálních souborů.</p>';
    return;
  }
  wireControls();
  await loadListings();
  render();
}

init();
