"""Render the English evidence pages for charging concentration & equity (one template, two scopes).

    python3 analysis/concentration_explorer_render.py jabar      -> analysis/concentration_jabar_en.html
    python3 analysis/concentration_explorer_render.py national   -> analysis/concentration_national_en.html

Inputs: analysis/concentration_explorer_<scope>.json (scripts/concentration_explorer.py) and the unit polygons
(data/jabar_kecamatan_spklu.geojson or data/kabkota_bps.geojson). Everything is embedded; the page is standalone.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); os.chdir(ROOT)
scope = sys.argv[1] if len(sys.argv) > 1 else "jabar"
D = json.load(open(f"analysis/concentration_explorer_{scope}.json", encoding="utf-8"))
if scope == "jabar":
    G = json.load(open("data/jabar_kecamatan_spklu.geojson", encoding="utf-8"))
    geo = [[f["properties"]["code"], f["geometry"]] for f in G["features"]]
else:
    G = json.load(open("data/kabkota_bps.geojson", encoding="utf-8"))
    def rnd(o):
        if isinstance(o, list): return [rnd(x) for x in o]
        return round(o, 4) if isinstance(o, float) else o
    geo = [[f["properties"]["kode_wilayah"], dict(type=f["geometry"]["type"], coordinates=rnd(f["geometry"]["coordinates"]))] for f in G["features"]]

TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ Charging Equity Evidence</title>
<meta name="description" content="Who gets public EV chargers in __TITLE__? Supply concentration, concentration indices with bootstrap bands, quintiles, maps and decompositions — the evidence base for the 'Who is really served' thesis.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700&family=Source+Sans+3:wght@400;600&display=swap">
<style>
:root{--bg:#fcfcfb;--fg:#0b0b0b;--fg2:#52514e;--fg3:#7d7b75;--line:#e4e2dc;--panel:#f4f3ef;--grid:#ebe9e3;--chip:#e9e7e1;
 --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--zero:#d9d7d0;--hatch:#bdbab2;--good:#0ca30c;--crit:#d03b3b;--mid:#f0efec;
 --q1:#cde2fb;--q2:#9ec5f4;--q3:#5598e7;--q4:#256abf;--q5:#104281;--display:"Archivo",system-ui,sans-serif;--body:"Source Sans 3",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1a1a19;--fg:#fff;--fg2:#c3c2b7;--fg3:#8f8d85;--line:#34332f;--panel:#232321;--grid:#2c2b28;--chip:#2e2d2a;
 --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--zero:#3a3936;--hatch:#5a5853;--mid:#383835;--q1:#184f95;--q2:#256abf;--q3:#3987e5;--q4:#6da7ec;--q5:#b7d3f6;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#1a1a19;--fg:#fff;--fg2:#c3c2b7;--fg3:#8f8d85;--line:#34332f;--panel:#232321;--grid:#2c2b28;--chip:#2e2d2a;
 --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--zero:#3a3936;--hatch:#5a5853;--mid:#383835;--q1:#184f95;--q2:#256abf;--q3:#3987e5;--q4:#6da7ec;--q5:#b7d3f6;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16px;line-height:1.5;margin:0;padding-block:26px 64px;padding-inline:clamp(16px,4vw,40px)}
.wrap{max-width:1120px;margin:0 auto}
h1,h2,h3{font-family:var(--display);text-wrap:balance;margin:0}
h1{font-size:clamp(28px,4vw,40px);line-height:1.1;font-weight:700}
h2{font-size:22px;font-weight:700;margin-top:48px;display:flex;gap:10px;align-items:baseline}
h2 .n{font-size:13px;color:var(--fg3);font-weight:500;letter-spacing:.08em}
h3{font-size:15px;font-weight:600;color:var(--fg2)}
p{max-width:76ch;margin:8px 0}
.lede{color:var(--fg2);font-size:17px}
.eyebrow{font-family:var(--display);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--fg3);font-weight:500}
.nav{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0 0;font-size:13px}
.nav a{color:var(--fg2);text-decoration:none;background:var(--chip);padding:3px 10px;border-radius:999px}
.nav a:hover{color:var(--fg)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin-top:22px}
.kpi{background:var(--panel);padding:13px 15px;border-radius:6px;min-width:0}
.kpi .v{font-family:var(--display);font-size:28px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.1}
.kpi .l{color:var(--fg2);font-size:13.5px;margin-top:4px}
.kpi .s{color:var(--fg3);font-size:12.5px;font-variant-numeric:tabular-nums}
.ev{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin-top:16px}
.ev .card{background:var(--panel);border-radius:6px;padding:14px 16px;border-left:4px solid var(--s1);display:flex;flex-direction:column;gap:6px}
.ev .card .big{font-family:var(--display);font-size:24px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.1}
.ev .card .big small{font-size:13px;font-weight:500;color:var(--fg2)}
.ev .card .t{font-weight:600;font-size:15px}
.ev .card .d{font-size:13.5px;color:var(--fg2);line-height:1.45}
.ev .card .so{font-size:13px;color:var(--fg);background:var(--mid);border-radius:4px;padding:5px 8px;margin-top:auto}
.ev .card .so b{font-weight:600}
.ev .card.crit{border-left-color:var(--crit)}.ev .card.good{border-left-color:var(--good)}.ev .card.warn{border-left-color:var(--s4)}
.panel{background:var(--panel);border-radius:6px;padding:16px;margin-top:14px;min-width:0}
.controls{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin-bottom:10px;font-size:14px}
.controls label{display:flex;gap:6px;align-items:center;color:var(--fg2)}
select,button{font:inherit;font-size:14px;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:4px 8px}
button[aria-pressed="true"]{border-color:var(--fg);font-weight:600}
button:focus-visible,select:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px;color:var(--fg2);margin:6px 0 0}
.legend i{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:6px;border-radius:2px}
.legend i.dot{width:10px;height:10px;border-radius:50%}.legend i.box{width:14px;height:12px;border-radius:2px}
svg{display:block;width:100%;height:auto;max-width:100%}
#curve svg{max-width:680px}
svg text{font-family:var(--body);fill:var(--fg2);font-size:12px}
.tip{position:fixed;pointer-events:none;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:4px;padding:6px 9px;font-size:13px;line-height:1.35;box-shadow:0 2px 10px rgba(0,0,0,.12);max-width:280px;z-index:9;font-variant-numeric:tabular-nums}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}.three{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
@media (max-width:860px){.two,.three{grid-template-columns:1fr}}
table{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums}
th,td{padding:5px 8px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
th:first-child,td:first-child{text-align:left;white-space:normal}
th{font-weight:600;color:var(--fg2);font-size:12.5px;position:sticky;top:0;background:var(--panel);cursor:pointer}
th[aria-sort]{color:var(--fg)}
.scroll{overflow:auto;max-height:460px}
details{margin-top:10px;font-size:14px}summary{cursor:pointer;color:var(--fg2)}
.note{font-size:13.5px;color:var(--fg2);max-width:80ch}
.sig{color:var(--fg3);font-size:12px}
ul{max-width:80ch;padding-left:20px}li{margin:4px 0}
a{color:var(--s1)}
.mapleg{display:flex;gap:2px;align-items:flex-end;margin-top:8px;font-size:12px;color:var(--fg2);flex-wrap:wrap}
.mapleg .sw{display:flex;flex-direction:column;align-items:flex-start;gap:3px}.mapleg .sw i{display:block;width:56px;height:10px}
.lists{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-top:14px}
.lists ol{margin:4px 0 0;padding-left:20px;font-size:13.5px;font-variant-numeric:tabular-nums}.lists li{margin:2px 0}.lists li span{color:var(--fg3)}
.bar{display:inline-block;height:8px;border-radius:4px;background:var(--grid);width:80px;vertical-align:middle;margin-right:6px;overflow:hidden}.bar i{display:block;height:100%;background:var(--s1)}
.pos{color:var(--crit);font-weight:600}.neg{color:var(--s3);font-weight:600}
dl.gloss{display:grid;grid-template-columns:max-content 1fr;gap:4px 14px;font-size:14px;margin:8px 0 0;max-width:90ch}dl.gloss dt{font-weight:600}dl.gloss dd{margin:0;color:var(--fg2)}
.lang{font-size:13px;color:var(--fg2);margin-top:6px}
@media (prefers-reduced-motion:no-preference){path.u{transition:fill .15s}}
</style></head><body><div class="wrap">
<div class="eyebrow" id="eyebrow"></div>
<h1 id="h1"></h1>
<p class="lede" id="lede"></p>
<div class="lang" id="lang"></div>
<div class="nav"><a href="#s0">Key evidence</a><a href="#s1">Map</a><a href="#s2">How unequal</a><a href="#s3">Is it inequitable</a><a href="#s4">Quintiles</a><a href="#s5">Scatter</a><a href="#s6">Inside each __PARENT__</a><a href="#s7">Where inequality comes from</a><a href="#s8">Robustness</a><a href="#s9">What it would take</a><a href="#s10">Table</a><a href="#s11">Method</a></div>

<div class="kpis" id="kpis"></div>

<h2 id="s0"><span class="n">00</span>Key evidence</h2>
<p class="note">Each card is one finding computed from the data below, with what it implies for the thesis. Red = equity concern, amber = mixed, green = reassuring. Numbers are population-weighted unless stated.</p>
<div class="ev" id="evidence"></div>

<h2 id="s1"><span class="n">01</span>Where the supply is</h2>
<p class="note">Colour classes are population-weighted quintiles of the selected layer across all __UNITS__; hatched = zero. Hover or tap a __UNIT__ for its numbers.</p>
<div class="panel"><div class="controls"><label>Layer <select id="layer"></select></label><span class="note" id="map-note"></span></div><div id="map"></div><div class="mapleg" id="mapleg"></div></div>
<div class="lists" id="lists"></div>

<h2 id="s2"><span class="n">02</span>How unequal is the supply?</h2>
<p class="note">Equality asks whether supply is spread in proportion to people, without asking who the people are. Lorenz curves line __UNITS__ up from the lowest to the highest chargers per resident; the Gini is twice the area between the curve and the diagonal.</p>
<div class="two">
 <div class="panel"><h3>Lorenz curves — supply per resident vs population</h3><div id="lorenz"></div><div class="legend"><span><i style="background:var(--s1)"></i>Chargers</span><span><i style="background:var(--s2)"></i>Capacity (kW)</span><span><i style="background:var(--fg3);height:1px"></i>Perfect equality</span></div></div>
 <div class="panel"><h3>Concentration of supply across __UNITS__</h3><div class="scroll" style="max-height:none" id="market"></div><p class="note" id="market-note"></p></div>
</div>

<h2 id="s3"><span class="n">03</span>Is it inequitable — does supply follow advantage?</h2>
<p class="note">The concentration index (CI) ranks residents by a socio-economic variable (low → high) and reads how much of the supply the bottom x % receive. +1 = everything at the top of the ranking, 0 = proportional, −1 = everything at the bottom. Dots are estimates, bars are 95 % bootstrap bands (__BOOT__ resamples of __UNITS__); filled dots do not cross zero. For yes/no and share outcomes the Erreygers-corrected index is shown.</p>
<div class="panel"><div id="forest"></div><div class="legend" id="forest-leg"></div><details><summary>Table of values</summary><div class="scroll" id="forest-table"></div></details></div>
<div class="panel"><div class="controls"><label>Rank residents by <select id="cv-rank"></select></label><label>Supply <select id="cv-out"></select></label></div><div id="curve"></div><p class="note" id="curve-note"></p></div>

<h2 id="s4"><span class="n">04</span>Fifths of the population</h2>
<p class="note">Residents are split into five groups of equal population by the ranking variable (Q1 = lowest). If supply were proportional to people, every bar would be the same height.</p>
<div class="panel"><div class="controls"><label>Rank by <select id="q-rank"></select></label></div><div class="three" id="quint"></div><p class="note" id="q-note"></p></div>

<h2 id="s5"><span class="n">05</span>Every __UNIT__ at once</h2>
<p class="note">Each bubble is one __UNIT__ (size = residents). The horizontal axis is the ranking variable, the vertical axis chargers per 100,000 residents (square-root scale so that zero and the extremes both stay visible). Spearman's ρ measures the rank association.</p>
<div class="panel"><div class="controls"><label>Horizontal axis <select id="sc-rank"></select></label><span id="sc-note" class="note"></span></div><div id="scatter"></div><div class="legend"><span><i class="dot" style="background:var(--s1)"></i>Regency (kabupaten)</span><span><i class="dot" style="background:var(--s2)"></i>City (kota)</span><span><i class="dot" style="background:var(--hatch)"></i>No charger</span></div></div>

<h2 id="s6"><span class="n">06</span>Inside each __PARENT__</h2>
<p class="note">The same index recomputed within each __PARENT__ (its __UNITS__ ranked by population density, the one variable that varies inside a __PARENT__ everywhere). Large positive = that __PARENT__'s chargers sit in its densest __UNITS__. Only __PARENTS__ with ≥ 6 __UNITS__ and ≥ 5 chargers.</p>
<div class="panel"><div id="within"></div><details><summary>Table</summary><div class="scroll" id="within-table"></div></details></div>

<h2 id="s7"><span class="n">07</span>Where the inequality comes from</h2>
<p class="note">Theil's T of chargers per resident is additively split into inequality <i>between</i> groups and <i>within</i> them. A large between-share means the gap is mostly one group against another; a small one means the gap lives inside every group.</p>
<div class="panel"><div id="theil"></div></div>
<div id="groups"></div>

<h2 id="s8"><span class="n">08</span>Does the verdict survive subsetting?</h2>
<p class="note">The headline indices recomputed on subsets. If a sign flips, the finding depends on which __UNITS__ are in the frame.</p>
<div class="panel"><div class="scroll" style="max-height:none" id="robust"></div></div>

<h2 id="s9"><span class="n">09</span>What it would take to equalise</h2>
<p class="note">Chargers that would have to be added so that every __UNIT__ reaches today's average per 100,000 residents, holding existing chargers in place (water-filling). A planning yardstick, not a recommendation.</p>
<div class="panel"><div class="kpis" id="deficit-kpi" style="margin-top:0"></div><div class="lists" id="deficit-list"></div></div>

<h2 id="s10"><span class="n">10</span>__PARENTS_CAP__ side by side</h2>
<div class="panel"><div class="scroll" id="pt"></div><p class="note">Click a header to sort.</p></div>

<h2 id="s11"><span class="n">11</span>Method, sources and limits</h2>
<div class="panel" id="method"></div>
<details><summary>Glossary</summary><dl class="gloss">
<dt>Concentration index (CI)</dt><dd>C = 2·cov<sub>w</sub>(supply per resident, population-weighted fractional rank) / mean. Equivalent to 1 − 2∫L(p)dp on the concentration curve. Positive = supply concentrated among residents high on the ranking.</dd>
<dt>Erreygers CI</dt><dd>Correction for bounded outcomes (a yes/no flag or a 0–100 % share) so the index stays comparable across prevalence levels: 8·cov<sub>w</sub>(y, R)/(max−min).</dd>
<dt>95 % band</dt><dd>Percentile bootstrap over __UNITS__ (__BOOT__ resamples). "Significant" = band excludes zero.</dd>
<dt>Gini (per resident)</dt><dd>Inequality of chargers per resident across __UNITS__, weighted by residents; blind to who is rich or poor.</dd>
<dt>HHI / N<sub>eff</sub> / CR<sub>k</sub></dt><dd>Herfindahl index of supply shares (0–10,000), its inverse (how many equal-sized __UNITS__ would give the same concentration), and the share held by the top k __UNITS__.</dd>
<dt>Theil T</dt><dd>Entropy inequality measure that decomposes exactly into between- and within-group parts.</dd>
<dt>20:20, Palma</dt><dd>Share of chargers held by the top 20 % of residents (ranked by chargers per resident) over the bottom 20 %; Palma = top 10 % over bottom 40 %.</dd>
</dl></details>
</div>
<div class="tip" id="tip" hidden></div>
<script>
const D = __D__; const GEO = __GEO__; const M = D.meta;
const NS = "http://www.w3.org/2000/svg"; const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const fmt = (x, d=0) => (x==null||isNaN(x)) ? "–" : (+x).toLocaleString("en-US", {minimumFractionDigits:d, maximumFractionDigits:d});
const sgn = x => (x==null||isNaN(x)) ? "–" : (x>0?"+":"") + (+x).toFixed(3);
const pct = (x, d=1) => fmt(x, d) + " %";
const esc = s => String(s??"").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const el = (t, a={}, parent) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (parent) parent.appendChild(e); return e; };
const tip = document.getElementById("tip");
function showTip(ev, html){ tip.innerHTML = html; tip.hidden = false; const w = tip.offsetWidth, h = tip.offsetHeight; tip.style.left = Math.min(ev.clientX + 14, innerWidth - w - 8) + "px"; tip.style.top = (ev.clientY + 16 + h > innerHeight ? ev.clientY - h - 10 : ev.clientY + 16) + "px"; }
const hideTip = () => tip.hidden = true;
const NAT = M.scope === "national";
const U = D.units.map(a => { const o = {}; D.unit_cols.forEach((c, i) => o[c] = a[i]); o.per100k = 1e5*o.ch/o.pop; o.kw100k = 1e5*o.kw/o.pop; o.npov = -o.pov; if (!NAT){ o.ev100k = 1e5*o.ev/o.pop; o.kwhpc = o.kwh/o.pop; } return o; });
const RL = Object.fromEntries(M.ranks.map(r => [r.key, r])); const OL = Object.fromEntries(M.outcomes.map(o => [o.key, o.label]));
const B = (r, o) => D.B.find(b => b.rank === r && b.outcome === o);
const UNIT = M.unit, UNITS = M.unit_pl, PARENT = M.parent, PARENTS = M.parent_pl;

// ---------- header & KPIs
document.getElementById("eyebrow").textContent = `${M.title} · ${M.period} · ${fmt(M.chargers)} chargers · ${fmt(M.n_units)} ${UNITS} · ${fmt(M.pop/1e6,1)} million residents (Kontur 2023)`;
document.getElementById("h1").textContent = NAT ? "Who gets Indonesia's public EV chargers?" : "Who gets West Java's public EV chargers?";
document.getElementById("lede").innerHTML = `Two families of measures for one question. <b>Equality</b> (Lorenz, Gini, HHI) asks how evenly supply is spread across people. <b>Equity</b> (concentration indices) asks whether whatever unevenness exists follows <i>need</i> or follows <i>advantage</i> — residents are ranked from poorest to richest and the cumulative share of chargers is read against the cumulative share of people. ${NAT ? "This page covers all 508 districts; the companion page drills into West Java's 629 sub-districts with usage data." : "This page drills into 629 sub-districts with usage (kWh, sessions) and EV-owner data; the companion page covers all 508 districts of Indonesia."}`;
document.getElementById("lang").innerHTML = NAT ? `Companion: <a href="concentration_jabar_en.html">West Java sub-district evidence</a> · <a href="concentration_dashboard_en.html">interactive West Java explorer</a> · <a href="../index.html#tab=keadilan">main dashboard (Indonesian)</a>` : `Companion: <a href="concentration_national_en.html">national district evidence</a> · <a href="concentration_dashboard_en.html">interactive explorer (scenarios)</a> · <a href="concentration_jabar.html">Bahasa Indonesia</a>`;
const cov = D.A.coverage, exCh = B("exp","ch"), exKw = B("exp","kw"), exHas = B("exp","has"), qe = D.Q.exp;
const kp = [
  [sgn(exCh.ci), `CI chargers ~ spending per person`, `95 % ${sgn(exCh.lo)} … ${sgn(exCh.hi)} · ${exCh.signif ? "pro-rich, significant" : "not distinguishable from zero"}`],
  [sgn(exKw.ci), `CI capacity (kW) ~ spending`, `95 % ${sgn(exKw.lo)} … ${sgn(exKw.hi)} · ${exKw.signif ? "pro-rich, significant" : "n.s."}`],
  [pct(cov.pop_share), `residents whose ${UNIT} has a charger`, `${fmt(cov.units_with_charger)} of ${fmt(M.n_units)} ${UNITS} · ${fmt(cov.pop_without/1e6,1)} M people in ${UNITS} without one`],
  [`${fmt(qe[4].ch_per100k/Math.max(qe[0].ch_per100k,1e-6),1)}×`, `chargers per resident, richest vs poorest fifth`, `${fmt(qe[4].ch_per100k,2)} vs ${fmt(qe[0].ch_per100k,2)} per 100,000`],
  [D.A.gini_pc.ch.toFixed(2), `Gini of chargers per resident`, `across ${UNITS}, population-weighted`],
  [D.D.theil_parent.between_share == null ? "–" : pct(100*D.D.theil_parent.between_share,0), `of inequality is between ${PARENTS}`, `Theil decomposition; the rest is inside ${PARENTS}`]];
if (NAT) kp.push([pct(M.within10), "residents within 10 km of a charger", `${pct(M.beyond25)} live beyond 25 km`]);
else kp.push([`${fmt(qe[4].kwh_per100k/Math.max(qe[0].kwh_per100k,1e-6),1)}×`, "energy sold per resident, richest vs poorest fifth", `${fmt(qe[4].kwh_per100k/1e5,4)} vs ${fmt(qe[0].kwh_per100k/1e5,4)} kWh per resident`]);
document.getElementById("kpis").innerHTML = kp.map(([v,l,s]) => `<div class="kpi"><div class="v">${v}</div><div class="l">${l}</div><div class="s">${s}</div></div>`).join("");

// ---------- evidence cards (auto-generated from the data)
function evidence(){
  const cards = [];
  const Qd = D.Q.dens, Qi = D.Q.ipm, grp = n => D.D.groups.find(g => g.name === n);
  const cls = (b) => b.signif ? (b.ci > 0 ? "crit" : "good") : "warn";
  cards.push({c: cls(exCh), big: sgn(exCh.ci), small: "CI chargers ~ spending", t: exCh.signif ? `Chargers are ${exCh.ci>0?"concentrated in richer":"concentrated in poorer"} ${UNITS}` : "Charger placement is not measurably tilted by income", d: `${pct(100*qe[0].ch/(D.meta.chargers))} of chargers serve the poorest fifth of residents, ${pct(100*qe[4].ch/D.meta.chargers)} the richest fifth (band ${sgn(exCh.lo)} to ${sgn(exCh.hi)}).`, so: exCh.signif ? `<b>Vertical-equity pass rule fails</b> (proposal §5.8: CI ≤ 0 with band not crossing zero).` : `<b>Placement passes the equity test on counts</b> — but see capacity and use.`});
  cards.push({c: cls(exKw), big: sgn(exKw.ci), small: "CI capacity (kW) ~ spending", t: exKw.ci > exCh.ci + 0.05 ? "Capacity is more pro-rich than counts" : "Capacity tracks counts", d: `Counting kilowatts instead of units ${exKw.ci > exCh.ci + 0.05 ? "raises" : "leaves"} the index ${exKw.ci > exCh.ci + 0.05 ? "from "+sgn(exCh.ci)+" to "+sgn(exKw.ci) : "at "+sgn(exKw.ci)}: ${exKw.ci > exCh.ci + 0.05 ? "the bigger, faster chargers go where spending is higher." : "charger size does not add a further tilt."}`, so: `<b>A 7 kW and a 200 kW unit are not the same service</b> — the thesis measures capacity, not counts.`});
  if (!NAT){ const bk = B("exp","kwh"); cards.push({c: cls(bk), big: sgn(bk.ci), small: "CI energy sold ~ spending", t: "Use is far more pro-rich than placement", d: `Energy actually dispensed has an index of ${sgn(bk.ci)} against ${sgn(exCh.ci)} for charger counts; the richest fifth draws ${fmt(qe[4].kwh_per100k/Math.max(qe[0].kwh_per100k,1e-6),1)}× the energy per resident of the poorest fifth.`, so: `<b>Access does not convert into use</b> for poorer areas — the capability gap RQ3 is about.`}); }
  else { const bw = B("exp","within10"); cards.push({c: cls(bw), big: sgn(bw.ci), small: "Erreygers CI, residents ≤ 10 km", t: "Reach, not just counts, follows income", d: `${pct(qe[4].within10)} of the richest fifth live within 10 km of a charger against ${pct(qe[0].within10)} of the poorest fifth; ${pct(qe[0].beyond25)} of the poorest fifth live beyond 25 km.`, so: `<b>Step 1 of the service ladder (reachable) already fails</b> for a large poor minority.`}); }
  cards.push({c: "warn", big: `${pct(100*D.D.top20_share,0)}`, small: "of chargers go to the best-served 20 % of residents", t: `Unequal by any standard: ${D.D.ratio2020 == null ? "the bottom fifth has none" : "20:20 ratio "+fmt(D.D.ratio2020,1)+"×"}`, d: `Ranked by chargers per resident, the best-served fifth holds ${pct(100*D.D.top20_share,0)} of all chargers and the worst-served half holds ${pct(100*D.D.bottom50_share,0)}; Gini ${D.A.gini_pc.ch.toFixed(2)}, HHI ${fmt(D.A.supply.ch.hhi)} (≈ ${fmt(D.A.supply.ch.n_eff)} equal-sized ${UNITS}).`, so: `<b>Unequal and inequitable are different questions</b> — this card is the first, the CI cards are the second.`});
  cards.push({c: "crit", big: `${fmt(cov.pop_without/1e6,1)} M`, small: `people in ${UNITS} with no charger at all`, t: `${fmt(cov.units_without)} ${UNITS} have zero chargers`, d: `Largest: ${D.A.largest_without.slice(0,3).map(x => `${x.name} (${fmt(x.pop/1e3,0)}k)`).join(", ")}. ${NAT ? "" : "Several are dense, affluent commuter sub-districts — gaps are not only a poverty story."}`, so: `<b>Containment ≠ reach</b>: a charger across the boundary may serve them — the travel-time analysis tests this.`});
  const tp = D.D.theil_parent; cards.push({c: tp.between_share > 0.5 ? "crit" : "warn", big: pct(100*tp.between_share,0), small: `of inequality is between ${PARENTS}`, t: tp.between_share > 0.5 ? `The gap is mostly ${PARENT} vs ${PARENT}` : `The gap lives inside every ${PARENT}`, d: tp.between_share > 0.5 ? `Theil T ${tp.T}: ${pct(100*tp.between_share,0)} between ${PARENTS}, ${pct(100*(1-tp.between_share),0)} within. ${NAT ? "DKI Jakarta holds "+pct(100*tp.groups.find(g=>g.group==="DKI Jakarta").supply_share,0)+" of chargers for "+pct(100*tp.groups.find(g=>g.group==="DKI Jakarta").pop_share,1)+" of people." : ""}` : `Theil T ${tp.T}: only ${pct(100*tp.between_share,0)} is between ${PARENTS}; ${pct(100*(1-tp.between_share),0)} is between ${UNITS} of the same ${PARENT}.`, so: tp.between_share > 0.5 ? `<b>${PARENT.charAt(0).toUpperCase()+PARENT.slice(1)}-level allocation is the lever.</b>` : `<b>Allocation inside each ${PARENT} is the lever</b>, not transfers between them.`});
  const cr = grp("City vs regency").rows, city = cr.find(r => r.group.startsWith("City")), reg = cr.find(r => r.group.startsWith("Regency"));
  cards.push({c: "warn", big: `${fmt(city.per100k/Math.max(reg.per100k,1e-6),1)}×`, small: "city vs regency, chargers per resident", t: "Cities are served, regencies are not", d: `Cities: ${fmt(city.per100k,2)} per 100,000, ${pct(city.cov)} of residents covered${NAT ? ", "+pct(city.within10)+" within 10 km" : ""}. Regencies: ${fmt(reg.per100k,2)}, ${pct(reg.cov)}${NAT ? ", "+pct(reg.within10)+" within 10 km" : ""}; they hold ${pct(100*reg.pop/(city.pop+reg.pop),0)} of the population.`, so: `<b>Urban form explains part of the income gradient</b> — density and income are entangled; see the robustness table.`});
  const dch = B("dens","ch"); cards.push({c: cls(dch), big: sgn(dch.ci), small: "CI chargers ~ density", t: "Density gradient", d: `Ranked by density alone the index is ${sgn(dch.ci)}; ranked by spending ${sgn(exCh.ci)}; by HDI ${sgn(B("ipm","ch").ci)}; by poverty ${sgn(B("npov","ch").ci)}.`, so: `<b>${Math.abs(dch.ci) > Math.abs(exCh.ci) ? "Density explains more of the pattern than income" : "Income explains at least as much as density"}</b> — the proposal ranks by HDI, not income, for this reason.`});
  const rob = D.G.robust, flips = rob.filter(r => Math.sign(r.ci_ch) !== Math.sign(exCh.ci) && Math.abs(r.ci_ch) > 0.03);
  cards.push({c: flips.length ? "warn" : "good", big: `${rob.length - flips.length}/${rob.length}`, small: "subsets keep the sign of the headline index", t: flips.length ? "The verdict depends on the frame" : "The verdict is stable across subsets", d: flips.length ? `Sign flips in: ${flips.map(r => r.subset).join(", ")}.` : `Range of CI chargers ~ spending across subsets: ${sgn(Math.min(...rob.map(r=>r.ci_ch)))} to ${sgn(Math.max(...rob.map(r=>r.ci_ch)))}.`, so: `<b>Report the specification curve, not a single number</b> (proposal §5.8).`});
  cards.push({c: "warn", big: fmt(D.G.deficit), small: `chargers to lift every ${UNIT} to the average`, t: `+${pct(100*D.G.deficit/M.chargers,0)} of today's stock`, d: `${fmt(D.G.units_short)} ${UNITS} are below ${fmt(D.G.mean100k,2)} per 100,000. Largest single needs: ${D.G.top.slice(0,3).map(x => `${x.name} (+${x.need})`).join(", ")}.`, so: `<b>Equalising counts is cheap relative to the network's growth rate</b> — the harder question is whether counts are the right target.`});
  document.getElementById("evidence").innerHTML = cards.map(c => `<div class="card ${c.c}"><div class="big">${c.big} <small>${c.small}</small></div><div class="t">${c.t}</div><div class="d">${c.d}</div><div class="so">${c.so}</div></div>`).join("");
}
evidence();

// ---------- map
const GI = new Map(GEO); const UI = new Map(U.map(u => [u.id, u]));
const LAYERS = [["per100k","Chargers per 100,000 residents", v => fmt(v,2)], ["kw100k","Capacity kW per 100,000", v => fmt(v,0)], ["exp","Spending per person (k Rp/month, district)", v => fmt(v)], ["ipm","HDI (district)", v => fmt(v,1)], ["pov","Poverty rate % (district)", v => fmt(v,1)], ["dens","Residents per km²", v => fmt(v)]].concat(NAT ? [["within10","Residents within 10 km of a charger (%)", v => fmt(v,1)], ["beyond25","Residents beyond 25 km (%)", v => fmt(v,1)], ["dc","DC fast chargers", v => fmt(v)]] : [["kwhpc","kWh sold per resident", v => fmt(v,4)], ["ev100k","EV owners per 100,000", v => fmt(v,2)]]);
document.getElementById("layer").innerHTML = LAYERS.map(l => `<option value="${l[0]}">${l[1]}</option>`).join("");
function geomPath(g, PX, PY){ const ring = r => r.map((c,i) => (i?"L":"M") + PX(c[0]).toFixed(1) + " " + PY(c[1]).toFixed(1)).join("") + "Z"; return g.type === "Polygon" ? g.coordinates.map(ring).join("") : g.coordinates.map(p => p.map(ring).join("")).join(""); }
let bbox = null;
function renderMap(){
  const key = document.getElementById("layer").value, L = LAYERS.find(l => l[0] === key);
  if (!bbox){ let minx=1e9,miny=1e9,maxx=-1e9,maxy=-1e9; const walk = (c, fn) => typeof c[0] === "number" ? fn(c) : c.forEach(x => walk(x, fn)); GEO.forEach(([id,g]) => walk(g.coordinates, c => { if (c[0]<minx) minx=c[0]; if (c[0]>maxx) maxx=c[0]; if (c[1]<miny) miny=c[1]; if (c[1]>maxy) maxy=c[1]; })); bbox = [minx,miny,maxx,maxy]; }
  const [minx,miny,maxx,maxy] = bbox, MW = 1000, k = Math.cos((miny+maxy)/2*Math.PI/180), MH = Math.round(MW*(maxy-miny)/((maxx-minx)*k));
  const PX = x => (x-minx)/(maxx-minx)*MW, PY = y => (maxy-y)/(maxy-miny)*MH;
  const box = document.getElementById("map"); box.innerHTML = ""; const svg = el("svg", {viewBox:`0 0 ${MW} ${MH}`, role:"img", "aria-label":"Map"}); box.appendChild(svg);
  const defs = el("defs", {}, svg); const pat = el("pattern", {id:"hatch", width:6, height:6, patternUnits:"userSpaceOnUse", patternTransform:"rotate(45)"}, defs); el("rect", {width:6, height:6, fill:css("--zero")}, pat); el("line", {x1:0, y1:0, x2:0, y2:6, stroke:css("--hatch"), "stroke-width":1.5}, pat);
  const us = U.filter(u => GI.has(u.id)); const vals = us.map(u => u[key]); const idx = vals.map((v,i) => i).filter(i => vals[i] > 0).sort((a,b) => vals[a]-vals[b]); const tot = idx.reduce((s,i) => s + us[i].pop, 0);
  const cuts = []; let acc = 0, qn = 1; for (const i of idx){ acc += us[i].pop; if (acc >= tot*qn/5 && cuts.length < 4){ cuts.push(vals[i]); qn++; } }
  const cls = v => v <= 0 ? -1 : (cuts.findIndex(c => v <= c) + 5) % 5; const cols = ["--q1","--q2","--q3","--q4","--q5"];
  us.forEach((u, i) => { const p = el("path", {d:geomPath(GI.get(u.id), PX, PY), class:"u", fill: cls(vals[i]) < 0 ? "url(#hatch)" : css(cols[cls(vals[i])]), stroke:css("--bg"), "stroke-width":NAT?0.5:0.6}, svg);
    p.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(u.name)}</b> · ${esc(u.parent)}<br>${fmt(u.pop)} residents · ${fmt(u.dens)} /km²<br>${u.ch} chargers · ${fmt(u.kw)} kW · ${fmt(u.per100k,2)} per 100k${NAT ? `<br>${pct(u.within10)} within 10 km · ${pct(u.beyond25)} beyond 25 km` : `<br>${fmt(u.kwh)} kWh · ${fmt(u.trx)} sessions · ${u.ev} EV owners`}<br>spending ${fmt(u.exp)}k · HDI ${u.ipm} · poverty ${u.pov} %<br><i>${L[1]}: ${L[2](u[key])}</i>`)); p.addEventListener("pointerleave", hideTip); });
  const edges = idx.length ? [vals[idx[0]], ...cuts, vals[idx[idx.length-1]]] : [];
  document.getElementById("mapleg").innerHTML = `<div class="sw"><i style="background:repeating-linear-gradient(45deg,var(--zero) 0 3px,var(--hatch) 3px 4px)"></i>zero</div>` + (edges.length ? cols.map((c,j) => `<div class="sw"><i style="background:var(${c})"></i>${L[2](edges[j])}–${L[2](edges[j+1])}</div>`).join("") : "") + `<div style="margin-left:10px">population quintiles of ${L[1].toLowerCase()}</div>`;
  document.getElementById("map-note").textContent = `${us.length} ${UNITS} drawn`;
}
document.getElementById("layer").addEventListener("change", renderMap); renderMap();
const list = (title, items, f) => `<div class="panel" style="margin-top:0"><h3>${title}</h3><ol>${items.map(x => `<li>${f(x)}</li>`).join("")}</ol></div>`;
document.getElementById("lists").innerHTML = list("Most chargers", D.A.top.ch, x => `${esc(x.name)} <span>· ${esc(x.parent)} · ${fmt(x.v)} (${pct(100*x.share,1)})</span>`) +
  list("Most chargers per 100,000 residents", D.A.per100k_extremes.top, x => `${esc(x.name)} <span>· ${esc(x.parent)} · ${fmt(x.v,2)} · ${fmt(x.pop/1e3,0)}k people</span>`) +
  list(`Largest ${UNITS} without a charger`, D.A.largest_without, x => `${esc(x.name)} <span>· ${esc(x.parent)} · ${fmt(x.pop/1e3,0)}k people · spending ${fmt(x.exp)}k</span>`) +
  list(`Fewest chargers per resident among big ${UNITS}`, D.A.per100k_extremes.bottom_big, x => `${esc(x.name)} <span>· ${esc(x.parent)} · ${fmt(x.v,2)} · ${fmt(x.pop/1e3,0)}k people</span>`);

// ---------- Lorenz & market
function lineChart(id, series, xl, yl, diag=true){
  const W = 520, H = 360, m = {l:56, r:14, t:14, b:44}, pw = W-m.l-m.r, ph = H-m.t-m.b, X = p => m.l + p*pw, Y = p => m.t + (1-p)*ph;
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"});
  for (let i = 0; i <= 4; i++){ const p = i/4; el("line", {x1:X(0), x2:X(1), y1:Y(p), y2:Y(p), stroke:css("--grid")}, svg); el("line", {y1:Y(0), y2:Y(1), x1:X(p), x2:X(p), stroke:css("--grid")}, svg); el("text", {x:X(p), y:H-m.b+16, "text-anchor":"middle"}, svg).textContent = p*100+" %"; el("text", {x:m.l-6, y:Y(p)+4, "text-anchor":"end"}, svg).textContent = p*100+" %"; }
  el("text", {x:X(.5), y:H-6, "text-anchor":"middle"}, svg).textContent = xl; el("text", {x:14, y:Y(.5), "text-anchor":"middle", transform:`rotate(-90 14 ${Y(.5)})`}, svg).textContent = yl;
  if (diag) el("line", {x1:X(0), y1:Y(0), x2:X(1), y2:Y(1), stroke:css("--fg3"), "stroke-dasharray":"3 3"}, svg);
  const interp = (pts, x) => { for (let i = 1; i < pts.length; i++) if (pts[i][0] >= x){ const [x0,y0] = pts[i-1], [x1,y1] = pts[i]; return x1 === x0 ? y1 : y0 + (y1-y0)*(x-x0)/(x1-x0); } return 1; };
  series.forEach(s => { el("path", {d: s.pts.map((p,i) => (i?"L":"M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1)).join(""), fill:"none", stroke:css(s.col), "stroke-width":2, "stroke-linejoin":"round"}, svg); if (s.lab) el("text", {x:s.at[0], y:s.at[1], fill:css(s.col), "font-weight":600}, svg).textContent = s.lab; });
  const cross = el("line", {y1:Y(0), y2:Y(1), stroke:css("--fg3"), visibility:"hidden"}, svg); const hit = el("rect", {x:m.l, y:m.t, width:pw, height:ph, fill:"transparent"}, svg);
  hit.addEventListener("pointermove", ev => { const rc = svg.getBoundingClientRect(); const p = Math.max(0, Math.min(1, ((ev.clientX-rc.left)*W/rc.width - m.l)/pw)); cross.setAttribute("x1", X(p)); cross.setAttribute("x2", X(p)); cross.setAttribute("visibility", "visible"); showTip(ev, `<b>Bottom ${fmt(p*100)} % of residents</b><br>` + series.map(s => `${s.name}: ${fmt(interp(s.pts,p)*100,1)} %`).join("<br>")); });
  hit.addEventListener("pointerleave", () => { cross.setAttribute("visibility", "hidden"); hideTip(); });
  const box = document.getElementById(id); box.innerHTML = ""; box.appendChild(svg); return {X, Y};
}
lineChart("lorenz", [{pts: D.A.lorenz.ch, col:"--s1", name:"chargers", lab:`Chargers · Gini ${D.A.gini_pc.ch.toFixed(2)}`, at:[70, 40]}, {pts: D.A.lorenz.kw, col:"--s2", name:"capacity (kW)", lab:`Capacity · Gini ${D.A.gini_pc.kw.toFixed(2)}`, at:[70, 60]}], "Cumulative share of residents (ranked by chargers per resident, low → high)", "Cumulative share of supply");
const mk = D.A.supply; const mrows = Object.keys(mk).map(k => [OL[k] || k, mk[k]]).concat([["Residents (comparator)", D.A.pop]]);
document.getElementById("market").innerHTML = `<table><thead><tr><th>Supply</th><th>${UNITS} with &gt; 0</th><th>HHI</th><th>N<sub>eff</sub></th><th>Top 1</th><th>Top 4</th><th>Top 10</th><th>Gini (shares)</th></tr></thead><tbody>${mrows.map(([l,b]) => `<tr><td>${l}</td><td>${fmt(b.n)}</td><td>${fmt(b.hhi)}</td><td>${fmt(b.n_eff)}</td><td>${pct(100*b.cr1)}</td><td>${pct(100*b.cr4)}</td><td>${pct(100*b.cr10)}</td><td>${b.gini.toFixed(2)}</td></tr>`).join("")}</tbody></table>`;
document.getElementById("market-note").innerHTML = `Top 10 % of residents (by chargers per resident) hold <b>${pct(100*D.D.top10_share,0)}</b> of chargers; bottom 50 % hold <b>${pct(100*D.D.bottom50_share,0)}</b>. 20:20 ratio ${D.D.ratio2020 == null ? "undefined (bottom fifth has none)" : fmt(D.D.ratio2020,1)+"×"}; Palma ${D.D.palma == null ? "undefined" : fmt(D.D.palma,1)}. Residents themselves are spread with HHI ${fmt(D.A.pop.hhi)} — every supply measure is many times more concentrated than people are.`;

// ---------- forest plot
function forest(){
  const outs = M.outcomes.map(o => o.key), ranks = M.ranks.map(r => r.key);
  const rows = []; ranks.forEach(r => outs.forEach(o => { const b = B(r,o); if (b) rows.push({...b, lab: `${OL[o]}`, grp: RL[r].label}); }));
  const rowH = 22, lab = 250, W = 900, H = rows.length*rowH + ranks.length*18 + 34, lo = Math.min(-0.2, ...rows.map(x => x.lo)) - 0.05, hi = Math.max(0.3, ...rows.map(x => x.hi)) + 0.05, X = v => lab + (v-lo)/(hi-lo)*(W-lab-30);
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":"Concentration indices with 95 % bands"});
  [-0.5,-0.25,0,0.25,0.5,0.75].filter(v => v > lo && v < hi).forEach(v => { el("line", {x1:X(v), x2:X(v), y1:0, y2:H-24, stroke: v ? css("--grid") : css("--fg3")}, svg); el("text", {x:X(v), y:H-8, "text-anchor":"middle"}, svg).textContent = (v>0?"+":"") + v; });
  el("text", {x:X(hi)-4, y:12, "text-anchor":"end", "font-size":11}, svg).textContent = "→ supply concentrated at the TOP of the ranking"; el("text", {x:lab+4, y:12, "font-size":11}, svg).textContent = "← at the BOTTOM";
  let y = 20, g0 = null;
  rows.forEach(r => { if (r.grp !== g0){ y += 18; el("text", {x:4, y:y-4, "font-weight":700, fill:css("--fg")}, svg).textContent = "Ranked by " + r.grp; g0 = r.grp; }
    const yy = y + rowH/2; el("text", {x:lab-10, y:yy+4, "text-anchor":"end"}, svg).textContent = r.lab;
    const col = r.outcome === "has" || r.outcome === "within10" ? "--s3" : (NAT ? "--s1" : (["kwh","trx","ev"].includes(r.outcome) ? "--s2" : "--s1"));
    el("line", {x1:X(r.lo), x2:X(r.hi), y1:yy, y2:yy, stroke:css(col), "stroke-width":2}, svg); const c = el("circle", {cx:X(r.ci), cy:yy, r:5, fill: r.signif ? css(col) : css("--bg"), stroke:css(col), "stroke-width":2}, svg);
    el("text", {x:X(r.hi)+8, y:yy+4, "font-size":11}, svg).textContent = sgn(r.ci);
    c.addEventListener("pointermove", ev => showTip(ev, `<b>${r.lab}</b> ranked by ${r.grp}<br>CI ${sgn(r.ci)} · 95 % ${sgn(r.lo)} to ${sgn(r.hi)}<br>${r.signif ? "band excludes zero" : "not distinguishable from zero"}`)); c.addEventListener("pointerleave", hideTip); y += rowH; });
  const box = document.getElementById("forest"); box.innerHTML = ""; box.appendChild(svg);
  document.getElementById("forest-leg").innerHTML = `<span><i class="dot" style="background:var(--s1)"></i>Placement & capacity</span>${NAT ? "" : `<span><i class="dot" style="background:var(--s2)"></i>Use & demand (kWh, sessions, EV owners)</span>`}<span><i class="dot" style="background:var(--s3)"></i>Erreygers (yes/no, share)</span><span class="sig">● filled = 95 % band excludes 0 · ○ hollow = not significant</span>`;
  document.getElementById("forest-table").innerHTML = `<table><thead><tr><th>Ranked by</th><th>Supply</th><th>CI</th><th>95 % low</th><th>95 % high</th><th>Sig.</th></tr></thead><tbody>${rows.map(r => `<tr><td>${r.grp}</td><td style="text-align:left">${r.lab}</td><td class="${r.ci>0?"pos":"neg"}">${sgn(r.ci)}</td><td>${sgn(r.lo)}</td><td>${sgn(r.hi)}</td><td>${r.signif?"●":"○"}</td></tr>`).join("")}</tbody></table>`;
}
forest();

// ---------- concentration curve
const cvR = document.getElementById("cv-rank"), cvO = document.getElementById("cv-out");
cvR.innerHTML = M.ranks.map(r => `<option value="${r.key}">${r.label}</option>`).join(""); cvO.innerHTML = M.outcomes.filter(o => o.key !== "has").map(o => `<option value="${o.key}">${o.label}</option>`).join("");
function drawCurve(){ const r = cvR.value, o = cvO.value, pts = D.curves[r][o], b = B(r,o);
  lineChart("curve", [{pts, col:"--s1", name:OL[o], lab:`CI ${sgn(b.ci)}${b.signif?"":" (n.s.)"}`, at:[70, 40]}], `Cumulative share of residents, ranked by ${RL[r].label} (low → high)`, `Cumulative share of ${OL[o]}`);
  const q = D.Q[r]; document.getElementById("curve-note").innerHTML = `Bottom fifth (${RL[r].low}) receives <b>${pct(100*q[0][o]/q.reduce((s,x)=>s+x[o],0))}</b> of ${OL[o]}; top fifth (${RL[r].high}) <b>${pct(100*q[4][o]/q.reduce((s,x)=>s+x[o],0))}</b>. Band ${sgn(b.lo)} to ${sgn(b.hi)}.`; }
cvR.addEventListener("change", drawCurve); cvO.addEventListener("change", drawCurve); drawCurve();

// ---------- quintiles
const qR = document.getElementById("q-rank"); qR.innerHTML = M.ranks.map(r => `<option value="${r.key}">${r.label}</option>`).join("");
function barChart(vals, labels, col, title, fmtv){
  const W = 340, H = 240, m = {l:46, r:10, t:28, b:40}, pw = W-m.l-m.r, ph = H-m.t-m.b, top = Math.max(...vals, 1e-9)*1.15, Y = v => m.t + (1-v/top)*ph, bw = pw/vals.length;
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":title}); el("text", {x:m.l, y:14, "font-weight":600, fill:css("--fg")}, svg).textContent = title;
  [0,.25,.5,.75,1].forEach(f => { el("line", {x1:m.l, x2:W-m.r, y1:Y(f*top), y2:Y(f*top), stroke:css("--grid")}, svg); el("text", {x:m.l-5, y:Y(f*top)+4, "text-anchor":"end", "font-size":10.5}, svg).textContent = fmtv(f*top); });
  vals.forEach((v, i) => { const x = m.l + i*bw + 6, w = bw - 12, y = Y(v); el("path", {d:`M${x} ${m.t+ph}V${y+4}a4 4 0 0 1 4 -4h${w-8}a4 4 0 0 1 4 4V${m.t+ph}Z`, fill:css(col)}, svg); el("text", {x:x+w/2, y:y-5, "text-anchor":"middle", "font-size":11, fill:css("--fg")}, svg).textContent = fmtv(v); el("text", {x:x+w/2, y:H-m.b+16, "text-anchor":"middle", "font-size":11}, svg).textContent = labels[i]; });
  return svg;
}
function drawQuint(){ const r = qR.value, q = D.Q[r], labs = ["Q1 "+RL[r].low.split(" ")[0], "Q2", "Q3", "Q4", "Q5 "+RL[r].high.split(" ")[0]]; const box = document.getElementById("quint"); box.innerHTML = "";
  const panels = [[q.map(x => x.ch_per100k), "--s1", "Chargers per 100,000 residents", v => fmt(v,2)], [q.map(x => x.kw_per100k), "--s1", "Capacity kW per 100,000", v => fmt(v,0)],
    NAT ? [q.map(x => x.within10), "--s3", "Residents within 10 km of a charger (%)", v => fmt(v,0)] : [q.map(x => x.kwh_per100k/1e5*1000), "--s2", "Energy sold, Wh per resident per month", v => fmt(v,0)]];
  if (!NAT) panels.push([q.map(x => x.ev_per100k), "--s2", "EV owners per 100,000", v => fmt(v,1)]); else panels.push([q.map(x => x.beyond25), "--s3", "Residents beyond 25 km (%)", v => fmt(v,0)]);
  panels.push([q.map(x => x.pop_no_charger_pct), "--s4", `Residents whose ${UNIT} has no charger (%)`, v => fmt(v,0)]);
  panels.forEach(p => { const d = document.createElement("div"); d.appendChild(barChart(p[0], labs, p[1], p[2], p[3])); box.appendChild(d); });
  document.getElementById("q-note").innerHTML = `Each fifth ≈ ${fmt(q[0].pop/1e6,1)} million residents. ${r === "dens" || r === "ev100k" ? "This variable is measured per " + UNIT + "." : "Socio-economic variables are district-level (BPS 2024)" + (NAT ? "." : ", inherited by sub-districts — so these fifths compare districts, not neighbourhoods.")}`; }
qR.addEventListener("change", drawQuint); drawQuint();

// ---------- scatter
const scR = document.getElementById("sc-rank"); scR.innerHTML = M.ranks.map(r => `<option value="${r.key}">${r.label}</option>`).join("");
function drawScatter(){ const r = scR.value, xs = U.map(u => r === "npov" ? u.pov : u[r]); const W = 900, H = 420, m = {l:56, r:16, t:14, b:46}, pw = W-m.l-m.r, ph = H-m.t-m.b;
  const xmin = Math.min(...xs), xmax = Math.max(...xs), logx = r === "dens" || r === "ev100k"; const fx = v => logx ? Math.log10(Math.max(v, 1e-3)) : v; const lo = fx(xmin), hi = fx(xmax);
  const X = v => m.l + (fx(v)-lo)/(hi-lo||1)*pw; const ymax = Math.sqrt(Math.max(...U.map(u => u.per100k))); const Y = v => m.t + (1 - Math.sqrt(v)/ymax)*ph;
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":"Scatter"});
  [0,1,2,5,10,20,50].filter(v => Math.sqrt(v) <= ymax).forEach(v => { el("line", {x1:m.l, x2:W-m.r, y1:Y(v), y2:Y(v), stroke:css("--grid")}, svg); el("text", {x:m.l-6, y:Y(v)+4, "text-anchor":"end"}, svg).textContent = v; });
  const ticks = logx ? [1,10,100,1000,10000,100000].filter(v => v >= xmin && v <= xmax) : Array.from({length:6}, (_,i) => xmin + (xmax-xmin)*i/5);
  ticks.forEach(v => { el("line", {y1:m.t, y2:m.t+ph, x1:X(v), x2:X(v), stroke:css("--grid")}, svg); el("text", {x:X(v), y:H-m.b+16, "text-anchor":"middle"}, svg).textContent = fmt(v, logx ? 0 : (xmax-xmin > 50 ? 0 : 1)); });
  el("text", {x:m.l+pw/2, y:H-6, "text-anchor":"middle"}, svg).textContent = (r === "npov" ? "Poverty rate (%)" : RL[r].label.replace(/^./, c => c.toUpperCase())) + (logx ? " (log scale)" : ""); el("text", {x:14, y:m.t+ph/2, "text-anchor":"middle", transform:`rotate(-90 14 ${m.t+ph/2})`}, svg).textContent = "Chargers per 100,000 (√ scale)";
  const pmax = Math.max(...U.map(u => u.pop)); U.map((u,i) => [u, xs[i]]).sort((a,b) => b[0].pop - a[0].pop).forEach(([u, x]) => { const rad = 2.5 + 14*Math.sqrt(u.pop/pmax); const c = el("circle", {cx:X(x), cy:Y(u.per100k), r:rad, fill: u.ch ? css(u.kota ? "--s2" : "--s1") : css("--hatch"), "fill-opacity":.55, stroke:css("--bg"), "stroke-width":1}, svg);
    c.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(u.name)}</b> · ${esc(u.parent)}<br>${fmt(u.pop)} residents · ${u.ch} chargers · ${fmt(u.per100k,2)} per 100k<br>spending ${fmt(u.exp)}k · HDI ${u.ipm} · poverty ${u.pov} % · ${fmt(u.dens)} /km²`)); c.addEventListener("pointerleave", hideTip); });
  const box = document.getElementById("scatter"); box.innerHTML = ""; box.appendChild(svg);
  const s = D.S[r]; document.getElementById("sc-note").innerHTML = `Spearman ρ = <b>${s.rho.toFixed(2)}</b> (n = ${s.n}${s.p < 0.001 ? ", p < 0.001" : ", p = "+s.p})${r === "npov" ? " — computed on poverty reversed (poorest → least poor), so positive = more chargers where poverty is lower" : ""}.`; }
scR.addEventListener("change", drawScatter); drawScatter();

// ---------- within parent
function within(){ const rows = D.W; const rowH = 22, lab = 170, W = 900, H = rows.length*rowH + 30, lo = Math.min(-0.2, ...rows.map(x => x.ci_ch_dens)) - 0.05, hi = Math.max(0.3, ...rows.map(x => x.ci_ch_dens)) + 0.1, X = v => lab + (v-lo)/(hi-lo)*(W-lab-230);
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"}); [-0.5,-0.25,0,0.25,0.5,0.75,1].filter(v => v > lo && v < hi).forEach(v => { el("line", {x1:X(v), x2:X(v), y1:0, y2:H-24, stroke: v ? css("--grid") : css("--fg3")}, svg); el("text", {x:X(v), y:H-8, "text-anchor":"middle"}, svg).textContent = (v>0?"+":"") + v; });
  rows.forEach((x, i) => { const y = i*rowH + 4; const g = el("g", {}, svg); el("text", {x:lab-8, y:y+13, "text-anchor":"end", fill:css("--fg")}, g).textContent = x.parent;
    el("path", {d: x.ci_ch_dens >= 0 ? `M${X(0)} ${y}H${X(x.ci_ch_dens)-3}a3 3 0 0 1 3 3v10a3 3 0 0 1 -3 3H${X(0)}Z` : `M${X(0)} ${y}H${X(x.ci_ch_dens)+3}a3 3 0 0 0 -3 3v10a3 3 0 0 0 3 3H${X(0)}Z`, fill:css("--s1")}, g);
    el("text", {x:X(Math.max(x.ci_ch_dens,0))+6, y:y+13, "font-size":11}, g).textContent = `${sgn(x.ci_ch_dens)} · ${x.with_charger}/${x.n} have a charger · ${fmt(x.per100k,2)}/100k`;
    g.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(x.parent)}</b><br>${x.n} ${UNITS} · ${x.chargers} chargers · ${fmt(x.pop)} residents<br>CI chargers ~ density ${sgn(x.ci_ch_dens)} · Gini ${x.gini}${NAT ? (x.ci_ch_exp != null ? `<br>CI chargers ~ spending ${sgn(x.ci_ch_exp)} · CI ≤10 km ~ spending ${sgn(x.ci_w10_exp)}` : "") : `<br>CI kWh ~ density ${sgn(x.ci_kwh_dens)} · CI chargers ~ EV owners ${sgn(x.ci_ch_ev)}`}`)); g.addEventListener("pointerleave", hideTip); });
  const box = document.getElementById("within"); box.innerHTML = ""; box.appendChild(svg);
  const cols = NAT ? [["parent",PARENT],["n",UNITS],["chargers","Chargers"],["per100k","per 100k"],["with_charger","with charger"],["ci_ch_dens","CI ch~density"],["ci_ch_exp","CI ch~spending"],["ci_w10_exp","CI ≤10 km~spending"],["gini","Gini"]] : [["parent",PARENT],["n",UNITS],["chargers","Chargers"],["per100k","per 100k"],["with_charger","with charger"],["ci_ch_dens","CI ch~density"],["ci_kwh_dens","CI kWh~density"],["ci_ch_ev","CI ch~EV owners"],["gini","Gini"]];
  document.getElementById("within-table").innerHTML = `<table><thead><tr>${cols.map(c => `<th>${c[1]}</th>`).join("")}</tr></thead><tbody>${rows.map(x => `<tr>${cols.map(c => `<td>${typeof x[c[0]] === "number" ? (c[0].startsWith("ci") ? sgn(x[c[0]]) : fmt(x[c[0]], c[0]==="per100k"?2:(c[0]==="gini"?3:0))) : esc(x[c[0]] ?? "–")}</td>`).join("")}</tr>`).join("")}</tbody></table>`; }
within();

// ---------- Theil & groups
function theil(){ const t = D.D.theil_parent, W = 900, H = 110; const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"}); const bars = [[`Between ${PARENTS}`, t.between_share, "--s2"], [`Within ${PARENTS}`, 1 - t.between_share, "--s1"]];
  let x = 20; el("text", {x:20, y:18, "font-weight":600, fill:css("--fg")}, svg).textContent = `Theil T = ${t.T} for chargers per resident across ${UNITS}`;
  bars.forEach(([l, s, c]) => { const w = s*(W-40) - 2; el("rect", {x, y:30, width:w, height:28, rx:4, fill:css(c)}, svg); el("text", {x:x+8, y:49, fill:"#fff", "font-weight":600}, svg).textContent = `${l}: ${pct(100*s,0)}`; x += w + 2; });
  const ti = D.D.theil_island; if (ti){ el("text", {x:20, y:84, fill:css("--fg2")}, svg).textContent = `By island group: ${pct(100*ti.between_share,0)} between islands, ${pct(100*(1-ti.between_share),0)} within — province, not island, is where the gap sits.`; }
  const box = document.getElementById("theil"); box.innerHTML = ""; box.appendChild(svg);
  document.getElementById("groups").innerHTML = D.D.groups.map(g => `<div class="panel"><h3>${g.name}${g.theil ? ` · ${pct(100*g.theil.between_share,0)} of Theil is between these groups` : ""}</h3><div class="scroll" style="max-height:none"><table><thead><tr><th>Group</th><th>${UNITS}</th><th>Residents</th><th>Chargers</th><th>per 100k</th><th>kW per 100k</th><th>% in ${UNITS} with a charger</th><th>${NAT ? "% within 10 km" : "kWh per resident"}</th><th>Share of chargers / share of people</th></tr></thead><tbody>${g.rows.map(r => { const tg = g.theil.groups.find(x => x.group === r.group); return `<tr><td>${esc(r.group)}</td><td>${fmt(r.n)}</td><td>${fmt(r.pop/1e6,2)} M</td><td>${fmt(r.chargers)}</td><td><span class="bar"><i style="width:${Math.min(100, 100*r.per100k/Math.max(...g.rows.map(x=>x.per100k)))}%"></i></span>${fmt(r.per100k,2)}</td><td>${fmt(r.kw_per100k,0)}</td><td>${pct(r.cov)}</td><td>${NAT ? pct(r.within10) : fmt(r.kwh_pc,4)}</td><td>${tg ? fmt(tg.ratio,2)+"×" : "–"}</td></tr>`; }).join("")}</tbody></table></div></div>`).join(""); }
theil();

// ---------- robustness
document.getElementById("robust").innerHTML = `<table><thead><tr><th>Subset</th><th>${UNITS}</th><th>CI chargers ~ spending</th><th>CI capacity ~ spending</th><th>${NAT ? "CI ≤10 km ~ spending (Erreygers)" : "CI energy sold ~ spending"}</th></tr></thead><tbody>${D.G.robust.map(r => `<tr><td>${esc(r.subset)}</td><td>${fmt(r.n)}</td><td class="${r.ci_ch>0?"pos":"neg"}">${sgn(r.ci_ch)}</td><td class="${r.ci_kw>0?"pos":"neg"}">${sgn(r.ci_kw)}</td><td class="${(NAT?r.ci_w10:r.ci_kwh)>0?"pos":"neg"}">${sgn(NAT ? r.ci_w10 : r.ci_kwh)}</td></tr>`).join("")}</tbody></table>`;

// ---------- deficit
document.getElementById("deficit-kpi").innerHTML = [[fmt(D.G.deficit), "chargers to add", `+${pct(100*D.G.deficit/M.chargers,0)} of ${fmt(M.chargers)}`], [fmt(D.G.mean100k,2), "target: today's average per 100,000", "no charger removed anywhere"], [fmt(D.G.units_short), `${UNITS} below the average`, `of ${fmt(M.n_units)}`]].map(([v,l,s]) => `<div class="kpi"><div class="v">${v}</div><div class="l">${l}</div><div class="s">${s}</div></div>`).join("");
document.getElementById("deficit-list").innerHTML = list("Largest single needs", D.G.top, x => `${esc(x.name)} <span>· ${esc(x.parent)} · +${x.need} (has ${x.ch}; ${fmt(x.pop/1e3,0)}k people)</span>`);

// ---------- parent table
const PTC = NAT ? [["parent","Province"],["n","Districts"],["pop","Residents"],["chargers","Chargers"],["kw","kW"],["per100k","per 100k"],["cov","% in districts with charger"],["within10","% within 10 km"],["beyond25","% beyond 25 km"],["exp","Spending (k Rp)"],["ipm","HDI"]] : [["parent","District"],["n","Sub-districts"],["pop","Residents"],["chargers","Chargers"],["kw","kW"],["kwh","kWh Mar-2026"],["per100k","per 100k"],["cov","% in sub-districts with charger"],["exp","Spending (k Rp)"],["ipm","HDI"]];
let ptk = "per100k", ptd = -1;
function ptable(){ const rows = [...D.PT].sort((a,b) => { const va = a[ptk], vb = b[ptk]; return (typeof va === "string" ? va.localeCompare(vb) : va - vb) * ptd; });
  document.getElementById("pt").innerHTML = `<table><thead><tr>${PTC.map(c => `<th data-k="${c[0]}"${ptk===c[0]?` aria-sort="${ptd<0?"descending":"ascending"}"`:""}>${c[1]}${ptk===c[0]?(ptd<0?" ▾":" ▴"):""}</th>`).join("")}</tr></thead><tbody>${rows.map(r => `<tr>${PTC.map(c => { const v = r[c[0]]; return `<td>${typeof v === "number" ? (c[0]==="pop" ? fmt(v/1e6,2)+" M" : c[0]==="per100k" ? fmt(v,2) : c[0]==="ipm" ? fmt(v,1) : (["cov","within10","beyond25"].includes(c[0]) ? pct(v) : fmt(v))) : esc(v)}</td>`; }).join("")}</tr>`).join("")}</tbody></table>`;
  document.querySelectorAll("#pt th").forEach(th => th.addEventListener("click", () => { const k = th.dataset.k; if (ptk === k) ptd *= -1; else { ptk = k; ptd = k === "parent" ? 1 : -1; } ptable(); })); }
ptable();

// ---------- method
document.getElementById("method").innerHTML = `<ul>
<li><b>Units.</b> ${fmt(M.n_units)} ${UNITS} in ${fmt(M.n_parents)} ${PARENTS}; ${NAT ? "water bodies are excluded; three districts without a polygon in the BPS file appear in tables but not on the map" : "sub-districts under 500 residents and the Cirata reservoir are excluded"}.</li>
<li><b>Residents.</b> Kontur Population 2023 (H3 hexagons) summed to ${UNIT} polygons: ${fmt(M.pop/1e6,1)} million. ${NAT ? "" : "This exceeds the BPS count (≈50 million); only shares are used."}</li>
<li><b>Socio-economic ranking.</b> ${M.ses}. ${NAT ? "" : "<b>No official sub-district income exists</b>; every sub-district carries its district's value, so income-based indices at sub-district level measure the gradient <i>between districts</i> with a finer population denominator — not rich vs poor neighbourhoods inside a city. Density and EV ownership are genuinely sub-district."}</li>
<li><b>Supply.</b> ${M.sources.slice(0,2).join("; ")}.</li>
<li><b>Estimators.</b> Population-weighted concentration index (Wagstaff) with tie-averaged fractional ranks; Erreygers correction for bounded outcomes; percentile bootstrap over ${UNITS} (${fmt(M.boot)} resamples); Gini and Lorenz on supply per resident; HHI/CR on shares; Theil T decomposition; Spearman rank correlation on per-resident supply. All code: <code>scripts/concentration_explorer.py</code>.</li>
<li><b>Limits.</b> Containment is not reach — a charger across a boundary serves neighbours (the travel-time analysis addresses this). ${NAT ? "Straight-line distance bands (10/25 km) approximate reach. Chargers are counted as units regardless of uptime." : "One month of transactions is a snapshot. EV owners are proxied by completed PLN home-charger applications, which capture only owners who installed a home charger through PLN."} Corridor (toll-road) chargers are counted where they sit, inflating some low-population ${UNITS}.</li>
<li><b>Sources.</b> ${M.sources.join(" · ")}.</li></ul>`;
</script></body></html>
"""
html = (TEMPLATE.replace("__TITLE__", D["meta"]["title"]).replace("__PARENTS_CAP__", D["meta"]["parent_pl"][0].upper() + D["meta"]["parent_pl"][1:])
        .replace("__PARENTS__", D["meta"]["parent_pl"]).replace("__PARENT__", D["meta"]["parent"]).replace("__UNITS__", D["meta"]["unit_pl"]).replace("__UNIT__", D["meta"]["unit"])
        .replace("__BOOT__", f"{D['meta']['boot']:,}")
        .replace("__D__", json.dumps(D, ensure_ascii=False, separators=(",", ":"))).replace("__GEO__", json.dumps(geo, ensure_ascii=False, separators=(",", ":"))))
out = f"analysis/concentration_{scope}_en.html"
open(out, "w", encoding="utf-8").write(html)
print(out, "%.0f KB" % (len(html.encode()) / 1024))
