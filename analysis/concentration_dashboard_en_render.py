"""English, guided version of the West Java SPKLU concentration dashboard — everything is recomputed in the browser.

    python3 analysis/concentration_dashboard_en_render.py   -> analysis/concentration_dashboard_en.html

Same data and estimators as concentration_dashboard.html (Indonesian), with: a plain-language verdict that updates
with every control, a population-quintile chart, a side-by-side comparison of the three placement rules, help
text on every measure, a searchable sub-district table with CSV export, and a shareable URL that stores the state.
Data per sub-district (kecamatan) from data/jabar_kecamatan_spklu.geojson (built by scripts/concentration_kecamatan_jabar.py).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(HERE))
G = json.load(open("data/jabar_kecamatan_spklu.geojson", encoding="utf-8"))

TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>West Java Charging Equity Explorer</title>
<meta name="description" content="Who gets West Java's public EV chargers? Explore how charging supply is distributed across 629 sub-districts by income, development, density and EV ownership, and test where new chargers would help most.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700&family=Source+Sans+3:wght@400;600&display=swap">
<style>
:root{
  --bg:#fcfcfb; --fg:#0b0b0b; --fg2:#52514e; --fg3:#7d7b75; --line:#e4e2dc; --panel:#f4f3ef; --grid:#ebe9e3; --chip:#e9e7e1;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --zero:#d9d7d0; --hatch:#bdbab2;
  --q1:#cde2fb; --q2:#9ec5f4; --q3:#5598e7; --q4:#256abf; --q5:#104281;
  --good:#0ca30c; --warn:#fab219; --crit:#d03b3b; --mid:#f0efec;
  --display:"Archivo",system-ui,sans-serif; --body:"Source Sans 3",system-ui,sans-serif;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#1a1a19; --fg:#ffffff; --fg2:#c3c2b7; --fg3:#8f8d85; --line:#34332f; --panel:#232321; --grid:#2c2b28; --chip:#2e2d2a;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --zero:#3a3936; --hatch:#5a5853; --mid:#383835;
  --q1:#184f95; --q2:#256abf; --q3:#3987e5; --q4:#6da7ec; --q5:#b7d3f6; color-scheme:dark } }
:root[data-theme="dark"]{
  --bg:#1a1a19; --fg:#ffffff; --fg2:#c3c2b7; --fg3:#8f8d85; --line:#34332f; --panel:#232321; --grid:#2c2b28; --chip:#2e2d2a;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --zero:#3a3936; --hatch:#5a5853; --mid:#383835;
  --q1:#184f95; --q2:#256abf; --q3:#3987e5; --q4:#6da7ec; --q5:#b7d3f6; color-scheme:dark }
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.45;margin:0;padding-block:18px 56px;padding-inline:clamp(16px,3vw,32px)}
h1,h2,h3{font-family:var(--display);text-wrap:balance;margin:0}
h1{font-size:clamp(22px,3vw,30px);line-height:1.1}
h2{font-size:17px;margin:0 0 6px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
h3{font-size:12.5px;color:var(--fg2);font-weight:600;letter-spacing:.05em;text-transform:uppercase;margin:0 0 6px}
a{color:var(--s1)}
.top{display:flex;flex-wrap:wrap;gap:6px 18px;align-items:baseline;justify-content:space-between;margin-bottom:10px}
.top .sub{color:var(--fg2);font-size:14px}
.top .lang{font-size:13px;color:var(--fg2)}
.howto{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:10px 0 16px}
.howto .st{background:var(--panel);border-radius:6px;padding:10px 12px;font-size:13.5px;color:var(--fg2);display:flex;gap:10px;align-items:flex-start}
.howto .st b{display:block;color:var(--fg)}
.howto .n{flex:none;width:24px;height:24px;border-radius:50%;background:var(--fg);color:var(--bg);font-weight:700;font-size:13px;display:grid;place-items:center;font-family:var(--display)}
.grid{display:grid;grid-template-columns:290px minmax(0,1fr);gap:18px;align-items:start}
@media (max-width:900px){.grid{grid-template-columns:1fr}.side{position:static;max-height:none}}
.side{position:sticky;top:0;display:flex;flex-direction:column;gap:12px;max-height:100vh;overflow:auto;padding:2px 2px 8px 0}
.card{background:var(--panel);border-radius:6px;padding:12px 14px;min-width:0}
.chips{display:flex;flex-wrap:wrap;gap:5px}
.chip{font:inherit;font-size:13px;padding:3px 9px;border-radius:999px;border:1px solid transparent;background:var(--chip);color:var(--fg);cursor:pointer}
.chip[aria-pressed="true"]{background:var(--s1);color:#fff;border-color:var(--s1)}
.chip.preset{background:transparent;border-color:var(--line)}
.chip.preset[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
button:focus-visible,select:focus-visible,input:focus-visible,summary:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
label.row{display:flex;flex-direction:column;gap:3px;font-size:13px;color:var(--fg2);margin-top:8px}
label.row span b{color:var(--fg);font-variant-numeric:tabular-nums}
input[type=range]{width:100%;accent-color:var(--s1)}
select,input[type=search]{font:inherit;font-size:14px;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:4px 8px;width:100%}
.btn{font:inherit;font-size:13px;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:5px 10px;cursor:pointer}
.btn.primary{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.btnrow{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.help{display:inline-grid;place-items:center;width:16px;height:16px;border-radius:50%;border:1px solid var(--fg3);color:var(--fg3);font-size:11px;font-weight:600;cursor:help;vertical-align:middle;margin-left:4px;font-family:var(--body)}
.verdict{border-left:4px solid var(--s1);padding:14px 16px}
.verdict .badge{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:600;padding:3px 10px;border-radius:999px;background:var(--mid);color:var(--fg)}
.verdict .badge i{width:10px;height:10px;border-radius:50%;display:inline-block}
.verdict p{margin:8px 0 0;font-size:16px;line-height:1.5}
.verdict p b{font-variant-numeric:tabular-nums}
.verdict .after{margin-top:8px;padding-top:8px;border-top:1px dashed var(--line);font-size:14.5px;color:var(--fg2)}
.verdict .after b{color:var(--s2)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:10px}
.kpi{background:var(--panel);border-radius:6px;padding:12px 14px;min-width:0}
.kpi .v{font-family:var(--display);font-size:26px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.1;display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
.kpi .v .after{color:var(--s2);font-size:20px}
.kpi .l{color:var(--fg2);font-size:13px;margin-top:3px}
.kpi .s{color:var(--fg3);font-size:12px;font-variant-numeric:tabular-nums}
.main{display:flex;flex-direction:column;gap:14px;min-width:0}
.two{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media (max-width:1100px){.two{grid-template-columns:1fr}}
svg{display:block;width:100%;height:auto;max-width:100%}
svg text{font-family:var(--body);fill:var(--fg2);font-size:12px}
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px;color:var(--fg2);margin-top:6px}
.legend i{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:5px;border-radius:2px}
.legend i.box{height:11px}
.mapleg{display:flex;gap:2px;align-items:flex-end;margin-top:6px;font-size:11px;color:var(--fg2);flex-wrap:wrap}
.mapleg .sw{display:flex;flex-direction:column;gap:2px}
.mapleg .sw i{display:block;width:52px;height:9px}
.tip{position:fixed;pointer-events:none;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:4px;padding:6px 9px;font-size:13px;line-height:1.35;box-shadow:0 2px 10px rgba(0,0,0,.12);max-width:280px;z-index:9;font-variant-numeric:tabular-nums}
table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
th,td{padding:5px 7px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){text-align:left}
th{font-weight:600;color:var(--fg2);font-size:12px;cursor:pointer;user-select:none;position:sticky;top:0;background:var(--panel)}
th[aria-sort]{color:var(--fg)}
.scroll{overflow:auto;max-height:520px}
.note{font-size:13px;color:var(--fg2);margin:6px 0 0}
.plus{color:var(--s2);font-weight:600}
.ctrls{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;font-size:13px;color:var(--fg2);margin-bottom:6px}
.ctrls select,.ctrls input{width:auto}
details.method{font-size:13.5px;color:var(--fg2)}
details.method summary{cursor:pointer;color:var(--fg);font-weight:600}
details.method p{margin:8px 0}
dl.gloss{display:grid;grid-template-columns:max-content 1fr;gap:4px 14px;font-size:13.5px;margin:8px 0 0}
dl.gloss dt{font-weight:600;color:var(--fg)}dl.gloss dd{margin:0;color:var(--fg2)}
.rules td.best{color:var(--s3);font-weight:600}
.toast{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);background:var(--fg);color:var(--bg);padding:7px 14px;border-radius:999px;font-size:13px;opacity:0;transition:opacity .2s;pointer-events:none}
.toast.on{opacity:1}
@media (prefers-reduced-motion:no-preference){path.kec{transition:fill .15s}}
</style></head><body>

<div class="top">
  <div><h1>West Java Charging Equity Explorer</h1><div class="sub">Who gets the public EV chargers? March 2026 · 629 sub-districts · 636 chargers · 50.4 million residents · every number is recomputed in your browser as you move a control</div></div>
  <div class="lang"><a href="concentration_dashboard.html">Bahasa Indonesia</a> · <a href="../index.html#tab=keadilan">main dashboard</a></div>
</div>
<div class="howto">
  <div class="st"><span class="n">1</span><span><b>Pick a region</b>All of West Java, a preset metropolitan area, or any mix of districts (kabupaten/kota).</span></div>
  <div class="st"><span class="n">2</span><span><b>Choose what to measure</b>Rank residents by income, development, poverty, density or EV ownership; measure chargers, capacity, energy or sessions.</span></div>
  <div class="st"><span class="n">3</span><span><b>Read the verdict</b>A concentration index (CI) above zero means supply tilts toward the top of the ranking; below zero toward the bottom. The 95 % band says whether that tilt is real.</span></div>
  <div class="st"><span class="n">4</span><span><b>Test a scenario</b>Add new chargers with one of three placement rules and watch the index, coverage and map respond.</span></div>
</div>

<div class="grid">
<aside class="side">
  <div class="card">
    <h3>Region</h3>
    <div class="chips" id="presets"></div>
    <div class="chips" id="kabs" style="margin-top:8px"></div>
    <div class="note" id="region-sum"></div>
  </div>
  <div class="card">
    <h3>What to measure</h3>
    <label class="row"><span>Rank residents from low to high by <span class="help" title="The ranking variable. Income-type variables come from BPS 2024 at district (kabupaten/kota) level and are inherited by each sub-district; density and EV ownership are measured per sub-district.">?</span></span><select id="rank">
      <option value="exp">Spending per person, district (BPS 2024)</option><option value="ipm">Human Development Index, district (BPS 2024)</option>
      <option value="npov">Poverty rate, district (poorest → richest)</option><option value="dens">Population density, sub-district</option><option value="ev100k">EV owners per 100,000, sub-district</option></select></label>
    <label class="row"><span>Supply to measure <span class="help" title="What is being shared out. Chargers and kW come from the March 2026 master list; kWh and sessions are March 2026 transactions.">?</span></span><select id="outcome">
      <option value="ch">Number of chargers</option><option value="kw">Charging capacity (kW)</option><option value="kwh">Energy sold, Mar 2026 (kWh)</option><option value="trx">Charging sessions, Mar 2026</option></select></label>
    <label class="row"><span>Include sub-districts with at least <b id="minpop-v">500</b> residents <span class="help" title="Drops tiny or uninhabited polygons (reservoirs, forest) that would otherwise distort per-capita figures.">?</span></span><input type="range" id="minpop" min="0" max="50000" step="500" value="500"></label>
  </div>
  <div class="card">
    <h3>Scenario: add chargers</h3>
    <label class="row"><span>Add <b id="n-v">0</b> new chargers in the selected region</span><input type="range" id="nnew" min="0" max="500" step="5" value="0"></label>
    <label class="row"><span>Placement rule</span><select id="rule">
      <option value="equal">Equalise: lowest chargers per person first</option><option value="demand">Follow demand: most EV owners per charger first</option><option value="poor">Pro-poor: lowest-spending district first</option></select></label>
    <p class="note">Each new charger counts as 50 kW. Scenarios change chargers and kW only; energy and sessions stay at March 2026 values.</p>
    <div class="btnrow"><button class="btn primary" id="share" type="button">Copy share link</button><button class="btn" id="csv" type="button">Download table (CSV)</button><button class="btn" id="reset" type="button">Reset</button></div>
  </div>
</aside>

<div class="main">
  <div class="card verdict" id="verdict"></div>
  <div class="kpis" id="kpis"></div>
  <div class="two">
    <div class="card">
      <h2>Who gets the supply? <span class="help" title="Residents are split into five equal groups by the ranking variable. Each bar is that group's share of the supply; if supply were spread evenly, every bar would be 20 %.">?</span></h2>
      <div id="quint"></div>
      <div class="legend"><span><i class="box" style="background:var(--s1)"></i>March 2026</span><span id="qleg2" hidden><i class="box" style="background:var(--s2)"></i>With scenario</span><span><i style="background:var(--fg3);height:1px"></i>Even share (20 %)</span></div>
    </div>
    <div class="card">
      <h2>Concentration curve <span class="help" title="Residents are lined up from the lowest to the highest value of the ranking variable (x-axis). The curve shows how much of the supply the bottom x % of residents receive. Below the diagonal = supply tilts to the top of the ranking.">?</span></h2>
      <div id="curve"></div>
      <div class="legend"><span><i style="background:var(--s1)"></i>March 2026</span><span id="cleg2" hidden><i style="background:var(--s2)"></i>With scenario</span><span><i style="background:var(--fg3);height:1px"></i>Line of equality</span></div>
    </div>
  </div>
  <div class="card">
    <h2>Map of sub-districts</h2>
    <div class="ctrls"><span>Colour by</span><select id="layer"><option value="ch100k">Chargers per 100,000 residents (with scenario)</option><option value="kwhpc">kWh sold per resident</option><option value="ev100k">EV owners per 100,000</option><option value="dens">Population density</option><option value="exp">District spending per person</option></select><span class="note" style="margin:0">Hover for details · outlined in orange = receives a new charger in the scenario</span></div>
    <div id="map"></div><div class="mapleg" id="mapleg"></div>
  </div>
  <div class="card" id="rules-card">
    <h2>Which placement rule helps most? <span class="help" title="The same number of new chargers placed under each rule, so the rules can be compared on identical terms.">?</span></h2>
    <div id="rules"></div>
  </div>
  <div class="card">
    <h2>District by district</h2>
    <p class="note" id="bars-note">Each district's index is computed inside that district (its sub-districts ranked by the chosen variable). Only districts with at least 6 sub-districts and 3 chargers are shown. Click a bar to focus on that district.</p>
    <div id="bars"></div>
  </div>
  <div class="card">
    <h2>Sub-district table</h2>
    <div class="ctrls"><input type="search" id="q" placeholder="Search sub-district or district…" aria-label="Search"><span id="tbl-note"></span></div>
    <div class="scroll" id="table"></div>
  </div>
  <details class="method"><summary>Glossary</summary>
    <dl class="gloss">
      <dt>Concentration index (CI)</dt><dd>Twice the area between the concentration curve and the line of equality, from −1 to +1. Positive: supply is concentrated among residents high on the ranking (e.g. richer districts). Negative: among those low on it. Zero: proportional to population. Think of it as a Gini coefficient that knows who is rich and who is poor.</dd>
      <dt>95 % band</dt><dd>Bootstrap interval from 300 resamples of sub-districts. If the band does not cross zero, the tilt is unlikely to be an accident of which sub-districts happen to have chargers.</dd>
      <dt>Coverage</dt><dd>Share of residents living in a sub-district that contains at least one charger. Says nothing about distance or capacity — only whether there is something nearby at all.</dd>
      <dt>Gini (chargers per person)</dt><dd>Inequality of chargers per resident across sub-districts, 0 (identical everywhere) to 1 (all in one place). Unlike the CI it ignores who is rich or poor.</dd>
      <dt>HHI</dt><dd>Herfindahl–Hirschman index of charger shares across sub-districts (0–10,000). Higher = supply bunched in fewer places.</dd>
      <dt>Quintile</dt><dd>One fifth of residents, grouped by the ranking variable: Q1 is the lowest fifth (e.g. poorest), Q5 the highest.</dd>
    </dl>
  </details>
  <details class="method"><summary>Method and data sources</summary>
    <p>CI = 2·cov<sub>w</sub>(supply per resident, population-weighted fractional rank) / weighted mean, identical to 1 − 2∫L(p)dp on the curve. Bands: 300 bootstrap resamples of sub-districts, recomputed once a control stops moving. HHI on charger shares across sub-districts. Population: Kontur 2023 (H3 resolution 8); sub-district boundaries dissolved from HDX–BPS 2020 village polygons. HDI, adjusted spending per person and poverty rate P0: BPS 2024 by district, inherited by sub-districts because no official sub-district figures exist. Chargers and kW: PLN master list March 2026; kWh and sessions: March 2026 transaction recap; EV owner locations: completed PLN home-charger applications.</p>
    <p>Limits to keep in mind: sub-district containment is not reachability (a charger just across a boundary serves neighbours too); income is district-level, so within-district gradients use density instead; one month of transactions. The companion travel-time analysis on the main dashboard addresses the first point.</p>
  </details>
</div>
</div>
<div class="tip" id="tip" hidden></div>
<div class="toast" id="toast">Link copied</div>

<script>
const GEO = __GEO__;
const NS = "http://www.w3.org/2000/svg";
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const fmt = (x, d=0) => (x ?? 0).toLocaleString("en-US", {minimumFractionDigits:d, maximumFractionDigits:d});
const sgn = x => isNaN(x) ? "–" : (x>0?"+":"") + x.toFixed(3);
const el = (t, a={}, parent) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (parent) parent.appendChild(e); return e; };
const tip = document.getElementById("tip");
function showTip(ev, html){ tip.innerHTML = html; tip.hidden = false; const w = tip.offsetWidth, h = tip.offsetHeight; tip.style.left = Math.min(ev.clientX + 14, innerWidth - w - 8) + "px"; tip.style.top = (ev.clientY + 16 + h > innerHeight ? ev.clientY - h - 10 : ev.clientY + 16) + "px"; }
const hideTip = () => tip.hidden = true;
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

// ---------- data
const F = GEO.features.map((f, i) => ({ i, g: f.geometry, ...f.properties, npov: -f.properties.pov, ev100k: f.properties.pop ? 1e5*f.properties.ev/f.properties.pop : 0 }));
const KABS = [...new Set(F.map(f => f.kab))].sort((a,b) => a.localeCompare(b));
const PRESETS = { "All West Java": [], "Jabodetabek (West Java part)": ["Bogor","Kota Bogor","Kota Depok","Bekasi","Kota Bekasi"], "Greater Bandung": ["Kota Bandung","Kota Cimahi","Bandung","Bandung Barat","Sumedang"],
  "Purwasuka corridor": ["Purwakarta","Subang","Karawang"], "Greater Cirebon": ["Kota Cirebon","Cirebon","Indramayu","Majalengka","Kuningan"], "Eastern Priangan": ["Garut","Tasikmalaya","Kota Tasikmalaya","Ciamis","Kota Banjar","Pangandaran"], "Sukabumi–Cianjur": ["Sukabumi","Kota Sukabumi","Cianjur"] };
const RANKLAB = {exp:"spending per person", ipm:"HDI", npov:"poverty (poorest → richest)", dens:"population density", ev100k:"EV owners per 100,000"};
const RANKHI = {exp:"richer districts", ipm:"more developed districts", npov:"less poor districts", dens:"denser sub-districts", ev100k:"sub-districts with more EV owners"};
const RANKLO = {exp:"poorer districts", ipm:"less developed districts", npov:"poorer districts", dens:"sparser sub-districts", ev100k:"sub-districts with fewer EV owners"};
const QLO = {exp:"poorest fifth", ipm:"least developed fifth", npov:"poorest fifth", dens:"sparsest fifth", ev100k:"fifth with fewest EV owners"};
const QHI = {exp:"richest fifth", ipm:"most developed fifth", npov:"least poor fifth", dens:"densest fifth", ev100k:"fifth with most EV owners"};
const OUTLAB = {ch:"chargers", kw:"charging capacity", kwh:"energy sold", trx:"charging sessions"};
const OUTVERB = {ch:"are", kw:"is", kwh:"is", trx:"are"};
const RULELAB = {equal:"equalise", demand:"follow demand", poor:"pro-poor"};

// ---------- state (URL hash first, then localStorage, then defaults)
const S = { regions: new Set(), rank: "exp", outcome: "ch", minpop: 500, n: 0, rule: "equal", layer: "ch100k", sortKey: "pop", sortDir: -1, q: "" };
function readState(){
  try { Object.assign(S, JSON.parse(localStorage.getItem("spklu-dash-en") || "{}"), { regions: new Set(JSON.parse(localStorage.getItem("spklu-dash-en-regions") || "[]")) }); } catch (e) {}
  const h = new URLSearchParams(location.hash.slice(1)); if (![...h.keys()].length) return;
  if (h.has("r")) S.regions = new Set(h.get("r") ? h.get("r").split("|").filter(k => KABS.includes(k)) : []);
  for (const k of ["rank","outcome","rule","layer"]) if (h.has(k)) S[k] = h.get(k);
  for (const k of ["minpop","n"]) if (h.has(k)) S[k] = +h.get(k) || 0;
}
function save(){ try { localStorage.setItem("spklu-dash-en", JSON.stringify({rank:S.rank, outcome:S.outcome, minpop:S.minpop, n:S.n, rule:S.rule, layer:S.layer})); localStorage.setItem("spklu-dash-en-regions", JSON.stringify([...S.regions])); } catch (e) {}
  const h = new URLSearchParams({r:[...S.regions].join("|"), rank:S.rank, outcome:S.outcome, minpop:S.minpop, n:S.n, rule:S.rule, layer:S.layer}); history.replaceState(null, "", "#" + h.toString()); }
readState();

// ---------- estimators
function wranks(r, w){ const n = r.length, o = [...Array(n).keys()].sort((a,b) => r[a]-r[b]); const W = w.reduce((s,x) => s+x, 0); const out = new Array(n); let cum = 0, i = 0;
  while (i < n){ let j = i, sw = 0; while (j+1 < n && r[o[j+1]] === r[o[i]]) j++; for (let k = i; k <= j; k++) sw += w[o[k]]; const mid = (cum + sw/2) / W; for (let k = i; k <= j; k++) out[o[k]] = mid; cum += sw; i = j+1; } return out; }
function ci(h, r, w){ const W = w.reduce((s,x) => s+x, 0), H = h.reduce((s,x) => s+x, 0); if (H <= 0 || W <= 0) return NaN; const R = wranks(r, w); const mu = H / W; let mR = 0; for (let i = 0; i < w.length; i++) mR += w[i]*R[i]; mR /= W; let cov = 0; for (let i = 0; i < w.length; i++) cov += w[i] * (h[i]/w[i] - mu) * (R[i] - mR); return 2 * (cov / W) / mu; }
function boot(h, r, w, reps=300){ const n = h.length, out = []; let seed = 2026; const rnd = () => (seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296;
  for (let b = 0; b < reps; b++){ const hh = [], rr = [], ww = []; for (let i = 0; i < n; i++){ const j = Math.floor(rnd()*n); hh.push(h[j]); rr.push(r[j]); ww.push(w[j]); } const c = ci(hh, rr, ww); if (!isNaN(c)) out.push(c); }
  out.sort((a,b) => a-b); return out.length ? [out[Math.floor(out.length*0.025)], out[Math.floor(out.length*0.975)]] : [NaN, NaN]; }
function curve(h, r, w){ const o = [...Array(h.length).keys()].sort((a,b) => r[a]-r[b]); const W = w.reduce((s,x) => s+x, 0), H = h.reduce((s,x) => s+x, 0) || 1; const pts = [[0,0]]; let cw = 0, ch = 0; for (const i of o){ cw += w[i]; ch += h[i]; pts.push([cw/W, ch/H]); } return pts; }
function quintiles(h, r, w){ const o = [...Array(h.length).keys()].sort((a,b) => r[a]-r[b]); const W = w.reduce((s,x) => s+x, 0), H = h.reduce((s,x) => s+x, 0) || 1; const q = [0,0,0,0,0], qp = [0,0,0,0,0]; let cw = 0;
  for (const i of o){ const lo = cw/W, hi = (cw+w[i])/W; for (let k = 0; k < 5; k++){ const a = Math.max(lo, k/5), b = Math.min(hi, (k+1)/5); if (b > a){ const share = (b-a)/(hi-lo); q[k] += h[i]*share; qp[k] += w[i]*share; } } cw += w[i]; }
  return q.map((x,k) => ({share: x/H, pop: qp[k], per100k: qp[k] ? 1e5*x/qp[k] : 0})); }
function gini(v){ const s = [...v].sort((a,b) => a-b), n = s.length, T = s.reduce((a,b) => a+b, 0); if (!n || !T) return NaN; let acc = 0; for (let i = 0; i < n; i++) acc += (i+1)*s[i]; return 2*acc/(n*T) - (n+1)/n; }
function hhi(v){ const T = v.reduce((a,b) => a+b, 0); if (!T) return NaN; return v.reduce((s,x) => s + (x/T)**2, 0) * 10000; }

// ---------- scenario
function scenario(sub, rule, n){ const add = new Array(sub.length).fill(0); if (!n) return add;
  const key = rule === "equal" ? i => (sub[i].ch + add[i]) / sub[i].pop : rule === "demand" ? i => -(sub[i].ev) / (sub[i].ch + add[i] + 1) : i => sub[i].exp * 1e3 + (sub[i].ch + add[i]) / sub[i].pop * 1e6;
  while (n-- > 0){ let best = -1, bv = Infinity; for (let i = 0; i < sub.length; i++){ const v = key(i); if (v < bv){ bv = v; best = i; } } if (best < 0) break; add[best]++; } return add; }
const supplyWith = (f, a) => S.outcome === "ch" ? f.ch + a : S.outcome === "kw" ? f.kw + 50*a : f[S.outcome];

// ---------- compute
let CUR = null, bootTimer = null;
function compute(){
  const inR = f => !S.regions.size || S.regions.has(f.kab);
  const sub = F.filter(f => inR(f) && f.pop >= S.minpop);
  const add = scenario(sub, S.rule, S.n);
  const w = sub.map(f => f.pop), r = sub.map(f => f[S.rank]);
  const h0 = sub.map(f => f[S.outcome]), h1 = sub.map((f, i) => supplyWith(f, add[i]));
  const ch0 = sub.map(f => f.ch), ch1 = sub.map((f, i) => f.ch + add[i]);
  const P = w.reduce((s,x) => s+x, 0);
  const cov = c => w.reduce((s, x, i) => s + (c[i] > 0 ? x : 0), 0) / P * 100;
  CUR = { sub, add, w, r, h0, h1, ci0: ci(h0, r, w), ci1: ci(h1, r, w), cov0: cov(ch0), cov1: cov(ch1), per0: 1e5*ch0.reduce((a,b) => a+b, 0)/P, per1: 1e5*ch1.reduce((a,b) => a+b, 0)/P,
          gini0: gini(ch0.map((c,i) => c/w[i])), gini1: gini(ch1.map((c,i) => c/w[i])), hhi0: hhi(ch0), hhi1: hhi(ch1), P, lo0: NaN, hi0: NaN, lo1: NaN, hi1: NaN,
          nkec0: ch0.filter(c => c > 0).length, nkec1: ch1.filter(c => c > 0).length, q0: quintiles(h0, r, w), q1: quintiles(h1, r, w), chTot: ch0.reduce((a,b) => a+b, 0) };
  render();
  clearTimeout(bootTimer); bootTimer = setTimeout(() => { [CUR.lo0, CUR.hi0] = boot(h0, r, w); if (S.n) [CUR.lo1, CUR.hi1] = boot(h1, r, w); renderVerdict(); renderKPI(); }, 350);
}
function render(){ renderVerdict(); renderKPI(); renderQuint(); renderCurve(); renderMap(); renderRules(); renderBars(); renderTable(); renderRegionSum(); save(); }

// ---------- verdict
function verdictOf(c, lo, hi){
  const sig = !isNaN(lo) && (lo > 0 || hi < 0);
  if (isNaN(c)) return {cls:"--fg3", txt:"No supply in this selection", word:"no supply"};
  if (Math.abs(c) < 0.05 || (!isNaN(lo) && !sig)) return {cls:"--good", txt: isNaN(lo) ? "Close to proportional" : "Not distinguishable from proportional", word:"roughly in proportion to population"};
  return c > 0 ? {cls:"--crit", txt:"Tilted toward " + RANKHI[S.rank] + (sig ? " · significant" : ""), word:"concentrated among " + RANKHI[S.rank]}
               : {cls:"--s3", txt:"Tilted toward " + RANKLO[S.rank] + (sig ? " · significant" : ""), word:"concentrated among " + RANKLO[S.rank]};
}
function renderVerdict(){
  const c = CUR, v = verdictOf(c.ci0, c.lo0, c.hi0), reg = S.regions.size ? [...S.regions].join(", ") : "West Java as a whole";
  const q = c.q0, band = isNaN(c.lo0) ? "band being computed…" : `95 % band ${sgn(c.lo0)} to ${sgn(c.hi0)}`;
  let html = `<span class="badge"><i style="background:var(${v.cls})"></i>${v.txt}</span>
    <p>In <b>${esc(reg)}</b>, ${OUTLAB[S.outcome]} ${isNaN(c.ci0) ? "cannot be assessed — there is none in the selected sub-districts." : `${OUTVERB[S.outcome]} <b>${v.word}</b>: concentration index <b>${sgn(c.ci0)}</b> (${band}) across ${fmt(c.sub.length)} sub-districts ranked by ${RANKLAB[S.rank]}.
    The ${QLO[S.rank]} of residents receives <b>${fmt(q[0].share*100,1)} %</b> of the ${OUTLAB[S.outcome]}; the ${QHI[S.rank]} receives <b>${fmt(q[4].share*100,1)} %</b> — a ${q[0].share > 0 ? fmt(q[4].share/q[0].share,1)+"×" : "∞"} ratio where 1× would be even.`}</p>`;
  if (S.n > 0 && !isNaN(c.ci1)){ const v1 = verdictOf(c.ci1, c.lo1, c.hi1), d = c.ci1 - c.ci0;
    html += `<div class="after">Adding <b>${fmt(S.n)}</b> chargers with the <b>${RULELAB[S.rule]}</b> rule moves the index to <b>${sgn(c.ci1)}</b> (${d < 0 ? "more equitable" : d > 0 ? "less equitable" : "unchanged"} by ${Math.abs(d).toFixed(3)}), lifts coverage from ${fmt(c.cov0,1)} % to <b>${fmt(c.cov1,1)} %</b> of residents, and gives the ${QLO[S.rank]} <b>${fmt(c.q1[0].share*100,1)} %</b> of the supply. Verdict after: ${v1.txt.toLowerCase()}.</div>`; }
  document.getElementById("verdict").innerHTML = html;
  document.getElementById("verdict").style.borderLeftColor = `var(${v.cls})`;
}

// ---------- KPIs
function renderKPI(){
  const c = CUR, sc = S.n > 0; const band = (lo, hi) => isNaN(lo) ? "computing 95 % band…" : `95 % band ${sgn(lo)} to ${sgn(hi)}`;
  const tile = (v0, v1, l, s, h) => `<div class="kpi"><div class="v"><span>${v0}</span>${sc ? `<span class="after">→ ${v1}</span>` : ""}</div><div class="l">${l}<span class="help" title="${esc(h)}">?</span></div><div class="s">${s}</div></div>`;
  document.getElementById("kpis").innerHTML =
    tile(sgn(c.ci0), sgn(c.ci1), `Concentration index`, sc ? band(c.lo1, c.hi1) + " (scenario)" : band(c.lo0, c.hi0), `${OUTLAB[S.outcome]} ranked by ${RANKLAB[S.rank]}. +1 = all supply at the top of the ranking, −1 = all at the bottom, 0 = proportional to population.`) +
    tile(fmt(c.cov0,1)+" %", fmt(c.cov1,1)+" %", "Residents with a charger in their sub-district", `${c.nkec0}${sc ? " → "+c.nkec1 : ""} of ${c.sub.length} sub-districts have one`, "Coverage by containment only — a charger across the boundary does not count, and distance is ignored.") +
    tile(fmt(c.per0,2), fmt(c.per1,2), "Chargers per 100,000 residents", `${fmt(c.P)} residents · ${fmt(c.chTot)} chargers${sc ? " + "+S.n : ""}`, "Overall supply level of the selection, before asking who gets it.") +
    tile(isNaN(c.gini0)?"–":c.gini0.toFixed(2), isNaN(c.gini1)?"–":c.gini1.toFixed(2), "Gini of chargers per person", `HHI ${fmt(c.hhi0)}${sc ? " → "+fmt(c.hhi1) : ""}`, "Plain inequality between sub-districts, blind to who is rich or poor. Compare with the concentration index to separate 'unequal' from 'inequitable'.");
}

function renderRegionSum(){ const n = S.regions.size; document.getElementById("region-sum").textContent = n ? `${n} district${n>1?"s":""}: ` + [...S.regions].join(", ") : "All of West Java (27 districts)";
  document.querySelectorAll("#kabs .chip").forEach(b => b.setAttribute("aria-pressed", S.regions.has(b.dataset.k)));
  document.querySelectorAll("#presets .chip").forEach(b => { const set = PRESETS[b.dataset.p]; b.setAttribute("aria-pressed", set.length ? set.length === S.regions.size && set.every(k => S.regions.has(k)) : !S.regions.size); }); }

// ---------- quintile bars
function renderQuint(){
  const W = 520, H = 300, m = {l:44, r:14, t:18, b:54}, pw = W-m.l-m.r, ph = H-m.t-m.b, sc = S.n > 0;
  const q0 = CUR.q0, q1 = CUR.q1, top = Math.max(0.3, ...q0.map(x => x.share), ...(sc ? q1.map(x => x.share) : [])) * 1.08;
  const Y = v => m.t + (1 - v/top)*ph, bw = pw/5, gap = 2;
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":"Share of supply by population quintile"});
  [0, .1, .2, .3, .4, .5, .6].filter(v => v < top).forEach(v => { el("line", {x1:m.l, x2:W-m.r, y1:Y(v), y2:Y(v), stroke:css("--grid")}, svg); el("text", {x:m.l-6, y:Y(v)+4, "text-anchor":"end"}, svg).textContent = Math.round(v*100)+" %"; });
  el("line", {x1:m.l, x2:W-m.r, y1:Y(.2), y2:Y(.2), stroke:css("--fg3"), "stroke-dasharray":"3 3"}, svg);
  const labs = ["Q1 " + QLO[S.rank].replace(" fifth",""), "Q2", "Q3", "Q4", "Q5 " + QHI[S.rank].replace(" fifth","")];
  q0.forEach((x, k) => { const x0 = m.l + k*bw + 6, wdt = bw - 12, inner = sc ? (wdt-gap)/2 : wdt;
    const bar = (v, xx, col, lab) => { const y = Y(v), hh = Math.max(0, m.t+ph-y); const p = el("path", {d:`M${xx} ${m.t+ph}V${y+4}a4 4 0 0 1 4 -4h${inner-8}a4 4 0 0 1 4 4V${m.t+ph}Z`, fill:css(col)}, svg);
      el("text", {x:xx+inner/2, y:y-5, "text-anchor":"middle", "font-size":11, fill:css("--fg")}, svg).textContent = fmt(v*100,1)+" %";
      p.addEventListener("pointermove", ev => showTip(ev, `<b>${labs[k]}</b> (${lab})<br>${fmt(v*100,1)} % of ${OUTLAB[S.outcome]}<br>${fmt(x.pop)} residents · ${fmt(x.per100k,2)} per 100,000`)); p.addEventListener("pointerleave", hideTip); };
    bar(x.share, x0, "--s1", "March 2026"); if (sc) bar(q1[k].share, x0+inner+gap, "--s2", "with scenario");
    el("text", {x:m.l + k*bw + bw/2, y:H-m.b+16, "text-anchor":"middle", "font-size":11.5}, svg).textContent = labs[k].length > 16 ? labs[k].slice(0,15)+"…" : labs[k]; });
  el("text", {x:m.l + pw/2, y:H-10, "text-anchor":"middle"}, svg).textContent = `Residents in fifths, ranked by ${RANKLAB[S.rank]} · bars = share of ${OUTLAB[S.outcome]}`;
  const box = document.getElementById("quint"); box.innerHTML = ""; box.appendChild(svg); document.getElementById("qleg2").hidden = !sc; document.getElementById("cleg2").hidden = !sc;
}

// ---------- map
const MW = 1000, hatchId = "hatch";
function geomPath(g, PX, PY){ const ring = r => r.map((c,i) => (i?"L":"M") + PX(c[0]).toFixed(1) + " " + PY(c[1]).toFixed(1)).join("") + "Z"; return g.type === "Polygon" ? g.coordinates.map(ring).join("") : g.coordinates.map(p => p.map(ring).join("")).join(""); }
function renderMap(){
  const inR = f => !S.regions.size || S.regions.has(f.kab); const sel = F.filter(inR);
  let minx=1e9, miny=1e9, maxx=-1e9, maxy=-1e9; const walk = (c, fn) => typeof c[0] === "number" ? fn(c) : c.forEach(x => walk(x, fn));
  sel.forEach(f => walk(f.g.coordinates, c => { if (c[0]<minx) minx=c[0]; if (c[0]>maxx) maxx=c[0]; if (c[1]<miny) miny=c[1]; if (c[1]>maxy) maxy=c[1]; }));
  const pad = (maxx-minx)*0.02; minx-=pad; maxx+=pad; miny-=pad; maxy+=pad;
  const k = Math.cos((miny+maxy)/2*Math.PI/180), MH = Math.max(260, Math.min(620, Math.round(MW*(maxy-miny)/((maxx-minx)*k))));
  const PX = x => (x-minx)/(maxx-minx)*MW, PY = y => (maxy-y)/(maxy-miny)*MH;
  const box = document.getElementById("map"); box.innerHTML = "";
  const svg = el("svg", {viewBox:`0 0 ${MW} ${MH}`, role:"img", "aria-label":"Map of sub-districts"}); box.appendChild(svg);
  const defs = el("defs", {}, svg); const pat = el("pattern", {id:hatchId, width:6, height:6, patternUnits:"userSpaceOnUse", patternTransform:"rotate(45)"}, defs); el("rect", {width:6, height:6, fill:css("--zero")}, pat); el("line", {x1:0, y1:0, x2:0, y2:6, stroke:css("--hatch"), "stroke-width":1.5}, pat);
  const addMap = new Map(CUR.sub.map((f, i) => [f.i, CUR.add[i]]));
  const L = { ch100k: [f => f.pop ? 1e5*(f.ch + (addMap.get(f.i)||0))/f.pop : 0, v => fmt(v,2), "chargers per 100,000"], kwhpc: [f => f.pop ? f.kwh/f.pop : 0, v => fmt(v,3), "kWh per resident"], ev100k: [f => f.ev100k, v => fmt(v,2), "EV owners per 100,000"], dens: [f => f.dens, v => fmt(v), "residents per km²"], exp: [f => f.exp, v => fmt(v), "thousand Rp per person per month"] }[S.layer];
  const vals = sel.map(L[0]); const idx = vals.map((v,i) => i).filter(i => vals[i] > 0).sort((a,b) => vals[a]-vals[b]); const tot = idx.reduce((s,i) => s + sel[i].pop, 0);
  const cuts = []; let acc = 0, qn = 1; for (const i of idx){ acc += sel[i].pop; if (acc >= tot*qn/5 && cuts.length < 4){ cuts.push(vals[i]); qn++; } }
  const cls = v => v <= 0 ? -1 : (cuts.findIndex(c => v <= c) + 5) % 5; const cols = ["--q1","--q2","--q3","--q4","--q5"];
  if (S.regions.size) F.filter(f => !inR(f)).forEach(f => { const inside = f.g.coordinates.flat(f.g.type === "Polygon" ? 1 : 2).some(c => c[0] > minx && c[0] < maxx && c[1] > miny && c[1] < maxy); if (inside) el("path", {d:geomPath(f.g, PX, PY), fill:css("--grid"), stroke:css("--bg"), "stroke-width":0.5}, svg); });
  sel.forEach((f, i) => { const a = addMap.get(f.i) || 0; const p = el("path", {d:geomPath(f.g, PX, PY), class:"kec", fill: cls(vals[i]) < 0 ? `url(#${hatchId})` : css(cols[cls(vals[i])]), stroke: a ? css("--s2") : css("--bg"), "stroke-width": a ? 2 : 0.6}, svg);
    if (a) p.parentNode.appendChild(p);
    p.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(f.kec)}</b> · ${esc(f.kab)}<br>${fmt(f.pop)} residents · ${fmt(f.dens)} per km²<br>${f.ch} chargers${a ? ` <span class="plus">+${a}</span>` : ""} · ${fmt(f.kw)} kW · ${fmt(f.kwh)} kWh · ${fmt(f.trx)} sessions<br>${f.ev} EV owners · district spending ${fmt(f.exp)}k Rp · HDI ${f.ipm}<br><i>${L[2]}: ${L[1](vals[i])}</i>`)); p.addEventListener("pointerleave", hideTip);
    p.addEventListener("click", () => { S.regions = new Set([f.kab]); compute(); }); });
  const edges = idx.length ? [vals[idx[0]], ...cuts, vals[idx[idx.length-1]]] : [];
  document.getElementById("mapleg").innerHTML = `<div class="sw"><i style="background:repeating-linear-gradient(45deg,var(--zero) 0 3px,var(--hatch) 3px 4px)"></i>zero</div>` + (edges.length ? cols.map((c,j) => `<div class="sw"><i style="background:var(${c})"></i>${L[1](edges[j])}–${L[1](edges[j+1])}</div>`).join("") : "") + `<div style="margin-left:10px">${L[2]} · population quintiles of the selection · click a sub-district to focus its district</div>`;
}

// ---------- curve
function renderCurve(){
  const W = 520, H = 300, m = {l:50, r:14, t:14, b:42}, pw = W-m.l-m.r, ph = H-m.t-m.b, X = p => m.l + p*pw, Y = p => m.t + (1-p)*ph;
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":"Concentration curve"});
  for (let i = 0; i <= 4; i++){ const p = i/4; el("line", {x1:X(0), x2:X(1), y1:Y(p), y2:Y(p), stroke:css("--grid")}, svg); el("line", {y1:Y(0), y2:Y(1), x1:X(p), x2:X(p), stroke:css("--grid")}, svg); el("text", {x:X(p), y:H-m.b+16, "text-anchor":"middle"}, svg).textContent = p*100+" %"; el("text", {x:m.l-6, y:Y(p)+4, "text-anchor":"end"}, svg).textContent = p*100+" %"; }
  el("text", {x:X(.5), y:H-6, "text-anchor":"middle"}, svg).textContent = `Cumulative share of residents, lowest → highest ${RANKLAB[S.rank]}`;
  el("text", {x:12, y:Y(.5), "text-anchor":"middle", transform:`rotate(-90 12 ${Y(.5)})`}, svg).textContent = `Cumulative share of ${OUTLAB[S.outcome]}`;
  el("line", {x1:X(0), y1:Y(0), x2:X(1), y2:Y(1), stroke:css("--fg3"), "stroke-dasharray":"3 3"}, svg);
  const c0 = curve(CUR.h0, CUR.r, CUR.w), c1 = S.n ? curve(CUR.h1, CUR.r, CUR.w) : null;
  const d = pts => pts.map((p,i) => (i?"L":"M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1)).join("");
  if (c1) el("path", {d:d(c1), fill:"none", stroke:css("--s2"), "stroke-width":2}, svg);
  el("path", {d:d(c0), fill:"none", stroke:css("--s1"), "stroke-width":2}, svg);
  el("text", {x:X(.05), y:Y(.93), fill:css("--s1"), "font-weight":600}, svg).textContent = `CI ${sgn(CUR.ci0)}`;
  if (c1) el("text", {x:X(.05), y:Y(.86), fill:css("--s2"), "font-weight":600}, svg).textContent = `Scenario CI ${sgn(CUR.ci1)}`;
  const cross = el("line", {y1:Y(0), y2:Y(1), stroke:css("--fg3"), visibility:"hidden"}, svg);
  const interp = (pts, x) => { for (let i = 1; i < pts.length; i++) if (pts[i][0] >= x){ const [x0,y0] = pts[i-1], [x1,y1] = pts[i]; return x1 === x0 ? y1 : y0 + (y1-y0)*(x-x0)/(x1-x0); } return 1; };
  const hit = el("rect", {x:m.l, y:m.t, width:pw, height:ph, fill:"transparent"}, svg);
  hit.addEventListener("pointermove", ev => { const rc = svg.getBoundingClientRect(); const p = Math.max(0, Math.min(1, ((ev.clientX-rc.left)*W/rc.width - m.l)/pw)); cross.setAttribute("x1", X(p)); cross.setAttribute("x2", X(p)); cross.setAttribute("visibility", "visible");
    showTip(ev, `<b>Bottom ${fmt(p*100)} % of residents</b> by ${RANKLAB[S.rank]}<br>receive ${fmt(interp(c0,p)*100,1)} % of ${OUTLAB[S.outcome]}${c1 ? `<br>with scenario: ${fmt(interp(c1,p)*100,1)} %` : ""}`); });
  hit.addEventListener("pointerleave", () => { cross.setAttribute("visibility", "hidden"); hideTip(); });
  const box = document.getElementById("curve"); box.innerHTML = ""; box.appendChild(svg);
}

// ---------- rule comparison
function renderRules(){
  const box = document.getElementById("rules"); const n = S.n || 100;
  const rows = ["equal","demand","poor"].map(rule => { const add = scenario(CUR.sub, rule, n); const h = CUR.sub.map((f,i) => supplyWith(f, add[i])); const chn = CUR.sub.map((f,i) => f.ch + add[i]);
    const P = CUR.P, cov = CUR.w.reduce((s,x,i) => s + (chn[i] > 0 ? x : 0), 0)/P*100, q = quintiles(h, CUR.r, CUR.w);
    return {rule, ci: ci(h, CUR.r, CUR.w), cov, q1: q[0].share, nk: add.filter(a => a > 0).length}; });
  const best = k => { const v = rows.map(r => r[k]); return k === "ci" ? Math.min(...v.map(Math.abs)) : Math.max(...v); };
  const bci = best("ci"), bcov = best("cov"), bq = best("q1");
  box.innerHTML = `<p class="note" style="margin:0 0 6px">${S.n ? `${fmt(n)} new chargers (the scenario slider)` : `Illustrative: 100 new chargers (move the scenario slider to change)`} placed under each rule. Baseline: CI ${sgn(CUR.ci0)}, coverage ${fmt(CUR.cov0,1)} %, ${QLO[S.rank]} gets ${fmt(CUR.q0[0].share*100,1)} %.</p>
   <div class="scroll" style="max-height:none"><table class="rules"><thead><tr><th>Rule</th><th>How it places chargers</th><th>Index after</th><th>Coverage after</th><th>${QLO[S.rank]} gets</th><th>Sub-districts receiving</th></tr></thead><tbody>` +
   rows.map(r => `<tr${r.rule === S.rule ? ' style="font-weight:600"' : ""}><td>${RULELAB[r.rule][0].toUpperCase()+RULELAB[r.rule].slice(1)}${r.rule === S.rule ? " ◀" : ""}</td><td style="text-align:left;white-space:normal;max-width:320px">${{equal:"Always the sub-district with the fewest chargers per resident", demand:"Always the sub-district with the most EV owners per existing charger", poor:"The lowest-spending district first, then its sub-districts with the fewest chargers per resident"}[r.rule]}</td>
     <td class="${Math.abs(r.ci) === bci ? "best" : ""}">${sgn(r.ci)}</td><td class="${r.cov === bcov ? "best" : ""}">${fmt(r.cov,1)} %</td><td class="${r.q1 === bq ? "best" : ""}">${fmt(r.q1*100,1)} %</td><td>${fmt(r.nk)}</td></tr>`).join("") + `</tbody></table></div>
   <p class="note">Green = best on that column (index closest to zero, highest coverage, largest share to the bottom fifth). The rules trade off: equalising maximises coverage, pro-poor maximises the bottom fifth's share, following demand tracks where EVs already are.</p>`;
}

// ---------- district bars
function renderBars(){
  const rows = []; const kabLevel = ["exp","ipm","npov"].includes(S.rank); const rk = kabLevel ? "dens" : S.rank;
  for (const kab of KABS){ if (S.regions.size && !S.regions.has(kab)) continue; const sub = CUR.sub.map((f,i) => [f, CUR.add[i]]).filter(([f]) => f.kab === kab); if (sub.length < 6) continue;
    const chs = sub.reduce((s,[f]) => s + f.ch, 0); if (chs < 3) continue; const w = sub.map(([f]) => f.pop), r = sub.map(([f]) => f[rk]);
    if (new Set(r).size < 2) continue;
    const h0 = sub.map(([f]) => f[S.outcome]), h1 = sub.map(([f,a]) => supplyWith(f, a));
    rows.push({kab, n: sub.length, ch: chs, c0: ci(h0, r, w), c1: ci(h1, r, w)}); }
  rows.sort((a,b) => b.c0 - a.c0);
  const box = document.getElementById("bars"); box.innerHTML = "";
  document.getElementById("bars-note").textContent = (kabLevel ? `${RANKLAB[S.rank][0].toUpperCase()+RANKLAB[S.rank].slice(1)} is the same for every sub-district within a district, so inside each district the sub-districts are ranked by population density instead. ` : "") + "Bars to the right of zero: supply tilts toward the " + (kabLevel ? "denser" : RANKHI[S.rank].replace("sub-districts","").replace("districts","").trim()) + " sub-districts of that district. Only districts with at least 6 sub-districts and 3 chargers are shown. Click a bar to focus on that district.";
  if (!rows.length){ box.insertAdjacentHTML("beforeend", `<p class="note">No district in the selection meets the threshold (≥ 6 sub-districts, ≥ 3 chargers).</p>`); return; }
  const rowH = 24, W = 760, lab = 150, H = rows.length*rowH + 30, lo = Math.min(-0.2, ...rows.map(x => Math.min(x.c0, x.c1))) - 0.05, hi = Math.max(0.2, ...rows.map(x => Math.max(x.c0, x.c1))) + 0.05;
  const X = v => lab + (v-lo)/(hi-lo)*(W-lab-110);
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":"Concentration index by district"});
  [-0.5,-0.25,0,0.25,0.5,0.75].filter(v => v > lo && v < hi).forEach(v => { el("line", {x1:X(v), x2:X(v), y1:0, y2:H-24, stroke: v ? css("--grid") : css("--fg3")}, svg); el("text", {x:X(v), y:H-8, "text-anchor":"middle"}, svg).textContent = (v>0?"+":"") + v; });
  rows.forEach((x, i) => { const y = i*rowH + 4; const g = el("g", {style:"cursor:pointer"}, svg);
    el("text", {x:lab-8, y:y+13, "text-anchor":"end", fill:css("--fg")}, g).textContent = x.kab;
    const bar = (v, col, yy, hh) => el("path", {d: v >= 0 ? `M${X(0)} ${yy}H${X(v)-3}a3 3 0 0 1 3 3v${hh-6}a3 3 0 0 1 -3 3H${X(0)}Z` : `M${X(0)} ${yy}H${X(v)+3}a3 3 0 0 0 -3 3v${hh-6}a3 3 0 0 0 3 3H${X(0)}Z`, fill:css(col)}, g);
    if (S.n && Math.abs(x.c1 - x.c0) > 1e-9){ bar(x.c0, "--s1", y, 7); bar(x.c1, "--s2", y+9, 7); } else bar(x.c0, "--s1", y, 16);
    el("text", {x: X(Math.max(x.c0, S.n ? x.c1 : x.c0, 0)) + 6, y:y+13, "font-size":11}, g).textContent = sgn(x.c0) + (S.n && Math.abs(x.c1-x.c0) > 1e-9 ? ` → ${sgn(x.c1)}` : "");
    g.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(x.kab)}</b><br>${x.n} sub-districts · ${x.ch} chargers<br>CI of ${OUTLAB[S.outcome]} by ${RANKLAB[rk]}: ${sgn(x.c0)}${S.n ? `<br>with scenario: ${sgn(x.c1)}` : ""}<br><i>click to focus</i>`)); g.addEventListener("pointerleave", hideTip);
    g.addEventListener("click", () => { S.regions = new Set([x.kab]); compute(); }); });
  box.appendChild(svg);
}

// ---------- table
const COLS = [["kecamatan","Sub-district"],["kab","District"],["pop","Residents"],["dens","per km²"],["ch","Chargers"],["add","New"],["kw","kW"],["kwh","kWh"],["trx","Sessions"],["ev","EV owners"],["ch100k","Chargers/100k"],["exp","Spending (k Rp)"],["ipm","HDI"]];
function tableRows(){ const q = S.q.trim().toLowerCase(); const rows = CUR.sub.map((f, i) => ({...f, kecamatan: f.kec, add: CUR.add[i], ch100k: 1e5*(f.ch + CUR.add[i])/f.pop})).filter(r => !q || r.kecamatan.toLowerCase().includes(q) || r.kab.toLowerCase().includes(q));
  rows.sort((a,b) => { const va = a[S.sortKey], vb = b[S.sortKey]; return (typeof va === "string" ? va.localeCompare(vb) : va - vb) * S.sortDir; }); return rows; }
function renderTable(){
  const rows = tableRows();
  document.getElementById("tbl-note").textContent = `${fmt(rows.length)} sub-districts${S.q ? " match" : " in the selection"} · click a column header to sort`;
  document.getElementById("table").innerHTML = `<table><thead><tr>${COLS.map(([k,l]) => `<th data-k="${k}"${S.sortKey===k ? ` aria-sort="${S.sortDir<0?"descending":"ascending"}"` : ""}>${l}${S.sortKey===k ? (S.sortDir<0?" ▾":" ▴") : ""}</th>`).join("")}</tr></thead><tbody>` +
    rows.map(r => `<tr><td>${esc(r.kecamatan)}</td><td>${esc(r.kab)}</td><td>${fmt(r.pop)}</td><td>${fmt(r.dens)}</td><td>${r.ch}</td><td>${r.add ? `<span class="plus">+${r.add}</span>` : ""}</td><td>${fmt(r.kw)}</td><td>${fmt(r.kwh)}</td><td>${fmt(r.trx)}</td><td>${r.ev}</td><td>${fmt(r.ch100k,2)}</td><td>${fmt(r.exp)}</td><td>${r.ipm}</td></tr>`).join("") + "</tbody></table>";
  document.querySelectorAll("#table th").forEach(th => th.addEventListener("click", () => { const k = th.dataset.k; if (S.sortKey === k) S.sortDir *= -1; else { S.sortKey = k; S.sortDir = (k === "kecamatan" || k === "kab") ? 1 : -1; } renderTable(); }));
}
function downloadCSV(){ const rows = tableRows(); const head = COLS.map(c => c[1]).join(","); const body = rows.map(r => [r.kecamatan, r.kab, r.pop, r.dens, r.ch, r.add, r.kw, r.kwh, r.trx, r.ev, r.ch100k.toFixed(2), r.exp, r.ipm].map(v => typeof v === "string" ? `"${v.replace(/"/g,'""')}"` : v).join(",")).join("\n");
  const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([head + "\n" + body], {type:"text/csv"})); a.download = "west_java_subdistricts_" + (S.n ? `scenario_${S.n}_${S.rule}` : "march2026") + ".csv"; a.click(); }

// ---------- controls
const presetsBox = document.getElementById("presets"), kabsBox = document.getElementById("kabs");
presetsBox.innerHTML = Object.keys(PRESETS).map(p => `<button type="button" class="chip preset" data-p="${p}">${p}</button>`).join("");
kabsBox.innerHTML = KABS.map(k => `<button type="button" class="chip" data-k="${k}">${k}</button>`).join("");
presetsBox.addEventListener("click", e => { const b = e.target.closest(".chip"); if (!b) return; S.regions = new Set(PRESETS[b.dataset.p]); compute(); });
kabsBox.addEventListener("click", e => { const b = e.target.closest(".chip"); if (!b) return; const k = b.dataset.k; if (S.regions.has(k)) S.regions.delete(k); else S.regions.add(k); compute(); });
const bind = (id, key, parse=v => v, label) => { const i = document.getElementById(id); i.value = S[key]; if (label) document.getElementById(label).textContent = fmt(+S[key]); i.addEventListener("input", () => { S[key] = parse(i.value); if (label) document.getElementById(label).textContent = fmt(+S[key]); compute(); }); };
bind("rank", "rank"); bind("outcome", "outcome"); bind("rule", "rule"); bind("layer", "layer"); bind("minpop", "minpop", Number, "minpop-v"); bind("nnew", "n", Number, "n-v");
document.getElementById("q").addEventListener("input", e => { S.q = e.target.value; renderTable(); });
document.getElementById("csv").addEventListener("click", downloadCSV);
document.getElementById("share").addEventListener("click", async () => { save(); try { await navigator.clipboard.writeText(location.href); } catch (e) { prompt("Copy this link:", location.href); } const t = document.getElementById("toast"); t.classList.add("on"); setTimeout(() => t.classList.remove("on"), 1600); });
document.getElementById("reset").addEventListener("click", () => { Object.assign(S, {regions:new Set(), rank:"exp", outcome:"ch", minpop:500, n:0, rule:"equal", layer:"ch100k", q:""}); for (const [id, key] of [["rank","rank"],["outcome","outcome"],["rule","rule"],["layer","layer"],["minpop","minpop"],["nnew","n"]]) document.getElementById(id).value = S[key]; document.getElementById("minpop-v").textContent = "500"; document.getElementById("n-v").textContent = "0"; document.getElementById("q").value = ""; compute(); });
compute();
</script></body></html>
"""

html = TEMPLATE.replace("__GEO__", json.dumps(G, ensure_ascii=False, separators=(",", ":")))
open("analysis/concentration_dashboard_en.html", "w", encoding="utf-8").write(html)
print("ok", len(html) // 1024, "KB")
