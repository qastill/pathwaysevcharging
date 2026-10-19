"""One-page, two-scope charging equity story with a West Java / Indonesia switch and infographics.

    python3 analysis/charging_equity_render.py   -> analysis/charging_equity_en.html

Embeds analysis/concentration_explorer_{jabar,national}.json and both polygon sets. Sections: hero with big
numbers · 4-step story strip · "if there were 100 residents" waffles (poorest vs richest fifth) · quintile
stairs pictogram · province / district gap (lollipop vs average, slope chart people → chargers) · evidence
cards · map · Lorenz + concentration table · forest plot · curve · quintiles · scatter · inside each parent ·
Theil & groups · robustness · what it would take · table · method & glossary.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); os.chdir(ROOT)
DATA = {s: json.load(open(f"analysis/concentration_explorer_{s}.json", encoding="utf-8")) for s in ("jabar", "national")}
def rnd(o):
    if isinstance(o, list): return [rnd(x) for x in o]
    return round(o, 4) if isinstance(o, float) else o
GJ = json.load(open("data/jabar_kecamatan_spklu.geojson", encoding="utf-8"))
GN = json.load(open("data/kabkota_bps.geojson", encoding="utf-8"))
GEO = {"jabar": [[f["properties"]["code"], f["geometry"]] for f in GJ["features"]],
       "national": [[f["properties"]["kode_wilayah"], dict(type=f["geometry"]["type"], coordinates=rnd(f["geometry"]["coordinates"]))] for f in GN["features"]]}

TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Charging Equity Story</title>
<meta name="description" content="Who gets public EV chargers in Indonesia and in West Java? Switch scope, see the province gap, and read the evidence: concentration indices, quintiles, maps, decompositions.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=Source+Sans+3:wght@400;600&display=swap">
<style>
:root{--bg:#fcfcfb;--fg:#0b0b0b;--fg2:#52514e;--fg3:#7d7b75;--line:#e4e2dc;--panel:#f4f3ef;--grid:#ebe9e3;--chip:#e9e7e1;
 --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;--zero:#d9d7d0;--hatch:#bdbab2;--good:#0ca30c;--crit:#d03b3b;--mid:#f0efec;
 --q1:#cde2fb;--q2:#9ec5f4;--q3:#5598e7;--q4:#256abf;--q5:#104281;--display:"Archivo",system-ui,sans-serif;--body:"Source Sans 3",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1a1a19;--fg:#fff;--fg2:#c3c2b7;--fg3:#8f8d85;--line:#34332f;--panel:#232321;--grid:#2c2b28;--chip:#2e2d2a;
 --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--zero:#3a3936;--hatch:#5a5853;--mid:#383835;--q1:#184f95;--q2:#256abf;--q3:#3987e5;--q4:#6da7ec;--q5:#b7d3f6;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#1a1a19;--fg:#fff;--fg2:#c3c2b7;--fg3:#8f8d85;--line:#34332f;--panel:#232321;--grid:#2c2b28;--chip:#2e2d2a;
 --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--zero:#3a3936;--hatch:#5a5853;--mid:#383835;--q1:#184f95;--q2:#256abf;--q3:#3987e5;--q4:#6da7ec;--q5:#b7d3f6;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16px;line-height:1.5;margin:0;padding-block:0 64px}
.wrap{max-width:1140px;margin:0 auto;padding-inline:clamp(16px,4vw,40px)}
h1,h2,h3{font-family:var(--display);text-wrap:balance;margin:0}
h1{font-size:clamp(30px,4.6vw,46px);line-height:1.05;font-weight:800;letter-spacing:-.01em}
h2{font-size:23px;font-weight:700;margin-top:52px;display:flex;gap:10px;align-items:baseline}
h2 .n{font-size:13px;color:var(--fg3);font-weight:500;letter-spacing:.08em}
h3{font-size:15px;font-weight:600;color:var(--fg2)}
p{max-width:78ch;margin:8px 0}
.topbar{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 0}
.topbar .wrap{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:space-between}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:999px;overflow:hidden;background:var(--panel)}
.seg button{font:inherit;font-size:14px;font-weight:600;padding:7px 16px;border:none;background:transparent;color:var(--fg2);cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--fg);color:var(--bg)}
.nav{display:flex;flex-wrap:wrap;gap:5px;font-size:12.5px}
.nav a{color:var(--fg2);text-decoration:none;background:var(--chip);padding:2px 9px;border-radius:999px}
.hero{padding:34px 0 10px}
.eyebrow{font-family:var(--display);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--fg3);font-weight:500}
.lede{color:var(--fg2);font-size:17.5px;max-width:80ch}
.big{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:22px}
.big .t{background:var(--panel);border-radius:10px;padding:16px 16px 14px;display:flex;gap:12px;align-items:flex-start;min-width:0}
.big .t svg.ic{width:34px;height:34px;flex:none;color:var(--s1)}
.big .t .v{font-family:var(--display);font-size:30px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1}
.big .t .l{color:var(--fg2);font-size:13.5px;margin-top:5px;line-height:1.35}
.story{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px;margin-top:18px}
.story .st{position:relative;background:var(--panel);border-radius:10px;padding:14px 14px 12px 52px;font-size:14px;color:var(--fg2);line-height:1.45}
.story .st > b{display:block;color:var(--fg);font-size:15px;margin-bottom:3px}
.story .st .k{position:absolute;left:14px;top:14px;width:28px;height:28px;border-radius:50%;background:var(--fg);color:var(--bg);display:grid;place-items:center;font-family:var(--display);font-weight:800;font-size:14px}
.panel{background:var(--panel);border-radius:10px;padding:16px;margin-top:14px;min-width:0}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}.three{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
@media (max-width:880px){.two,.three{grid-template-columns:1fr}}
.controls{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin-bottom:10px;font-size:14px}
.controls label{display:flex;gap:6px;align-items:center;color:var(--fg2)}
select,button.btn{font:inherit;font-size:14px;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:4px 8px}
button:focus-visible,select:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
svg{display:block;width:100%;height:auto;max-width:100%}
svg text{font-family:var(--body);fill:var(--fg2);font-size:12px}
#curve svg{max-width:680px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px;color:var(--fg2);margin:8px 0 0}
.legend i{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:6px;border-radius:2px}
.legend i.dot{width:10px;height:10px;border-radius:50%}.legend i.box{width:14px;height:12px;border-radius:2px}
.tip{position:fixed;pointer-events:none;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px 9px;font-size:13px;line-height:1.35;box-shadow:0 2px 10px rgba(0,0,0,.12);max-width:290px;z-index:9;font-variant-numeric:tabular-nums}
table{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums}
th,td{padding:5px 8px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
th:first-child,td:first-child{text-align:left;white-space:normal}
th{font-weight:600;color:var(--fg2);font-size:12.5px;position:sticky;top:0;background:var(--panel);cursor:pointer}
th[aria-sort]{color:var(--fg)}
.scroll{overflow:auto;max-height:460px}
details{margin-top:10px;font-size:14px}summary{cursor:pointer;color:var(--fg2)}
.note{font-size:13.5px;color:var(--fg2);max-width:84ch}
.sig{color:var(--fg3);font-size:12px}
ul{max-width:84ch;padding-left:20px}li{margin:4px 0}
a{color:var(--s1)}
.mapleg{display:flex;gap:2px;align-items:flex-end;margin-top:8px;font-size:12px;color:var(--fg2);flex-wrap:wrap}
.mapleg .sw{display:flex;flex-direction:column;align-items:flex-start;gap:3px}.mapleg .sw i{display:block;width:56px;height:10px}
.lists{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin-top:14px}
.lists ol{margin:4px 0 0;padding-left:20px;font-size:13.5px;font-variant-numeric:tabular-nums}.lists li{margin:2px 0}.lists li span{color:var(--fg3)}
.bar{display:inline-block;height:8px;border-radius:4px;background:var(--grid);width:80px;vertical-align:middle;margin-right:6px;overflow:hidden}.bar i{display:block;height:100%;background:var(--s1)}
.pos{color:var(--crit);font-weight:600}.neg{color:var(--s3);font-weight:600}
.ev{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin-top:16px}
.ev .card{background:var(--panel);border-radius:10px;padding:14px 16px;border-left:5px solid var(--s1);display:flex;flex-direction:column;gap:6px}
.ev .card .bigv{font-family:var(--display);font-size:25px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1.1}
.ev .card .bigv small{font-size:13px;font-weight:500;color:var(--fg2)}
.ev .card .t{font-weight:600;font-size:15px}.ev .card .d{font-size:13.5px;color:var(--fg2);line-height:1.45}
.ev .card .so{font-size:13px;color:var(--fg);background:var(--mid);border-radius:6px;padding:5px 8px;margin-top:auto}.ev .card .so b{font-weight:600}
.ev .card.crit{border-left-color:var(--crit)}.ev .card.good{border-left-color:var(--good)}.ev .card.warn{border-left-color:var(--s4)}
.waffles{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.waffle h3{margin-bottom:8px}.waffle .grid{display:grid;grid-template-columns:repeat(10,1fr);gap:3px;max-width:340px}
.waffle .p{aspect-ratio:1;border-radius:3px;background:var(--grid)}
.waffle .sum{display:flex;gap:14px;flex-wrap:wrap;font-size:13px;color:var(--fg2);margin-top:10px}.waffle .sum b{color:var(--fg);font-variant-numeric:tabular-nums}
.stairs{display:flex;gap:10px;align-items:flex-end;margin-top:10px;overflow-x:auto;padding-bottom:4px}
.stairs .col{flex:1;min-width:110px;text-align:center;font-size:12.5px;color:var(--fg2)}
.stairs .icons{display:flex;flex-wrap:wrap;gap:2px;justify-content:center;align-content:flex-end;min-height:150px}
.stairs .icons svg{width:22px;height:22px;color:var(--s1)}.stairs .icons svg.half{opacity:.45}
.stairs .v{font-family:var(--display);font-weight:800;font-size:18px;color:var(--fg);font-variant-numeric:tabular-nums;margin-top:6px}
.stairs .lab{margin-top:2px}
dl.gloss{display:grid;grid-template-columns:max-content 1fr;gap:4px 14px;font-size:14px;margin:8px 0 0;max-width:90ch}dl.gloss dt{font-weight:600}dl.gloss dd{margin:0;color:var(--fg2)}
.chapters{display:flex;flex-wrap:wrap;gap:6px;margin:22px 0 6px;position:sticky;top:54px;z-index:4;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line)}
.chapters button{font:inherit;font-size:13px;font-weight:600;padding:6px 12px;border-radius:999px;border:1px solid var(--line);background:var(--panel);color:var(--fg2);cursor:pointer;display:inline-flex;gap:6px;align-items:center}
.chapters button .k{font-family:var(--display);font-size:11px;color:var(--fg3)}
.chapters button[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}.chapters button[aria-pressed="true"] .k{color:var(--bg);opacity:.7}
.chdesc{font-size:14px;color:var(--fg2);margin:8px 0 0;min-height:22px}
section.ch{display:none;animation:fade .18s ease}section.ch.active{display:block}
section.ch h2{margin-top:22px}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.pager{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:28px;padding-top:14px;border-top:1px solid var(--line)}
.only-nat,.only-jab{display:none}body[data-scope="national"] .only-nat{display:revert}body[data-scope="jabar"] .only-jab{display:revert}
.hidden{display:none !important}
@media (prefers-reduced-motion:no-preference){path.u{transition:fill .15s}}
</style></head><body data-scope="national">
<div class="topbar"><div class="wrap"><div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap"><span class="eyebrow">Charging equity story</span><div class="seg" role="group" aria-label="Scope"><button type="button" data-s="national" aria-pressed="true">🇮🇩 Indonesia · 508 districts</button><button type="button" data-s="jabar" aria-pressed="false">West Java · 629 sub-districts</button></div></div>
<span class="note" style="margin:0">One chapter at a time — pick a tab, or use Previous / Next.</span></div></div>
<div class="wrap">
<div class="hero"><div class="eyebrow" id="eyebrow"></div><h1 id="h1"></h1><p class="lede" id="lede"></p>
<div class="big" id="big"></div></div>

<nav class="chapters" id="chapters" aria-label="Chapters"></nav>
<div class="chdesc" id="chdesc"></div>

<section class="ch" data-ch="overview">
<div class="story" id="story"></div>
<h2><span class="n">00</span>If there were 100 residents…</h2>
<p class="note" id="w-note"></p>
<div class="panel"><div class="waffles" id="waffles"></div></div>
</section>

<section class="ch" data-ch="gap">
<h2><span class="n">01</span><span id="gap-title"></span></h2>
<p class="note" id="gap-note"></p>
<div class="panel"><div class="controls"><label>Show <select id="gap-metric"></select></label><span class="note" id="gap-sum"></span></div><div id="lolli"></div><div class="legend" id="lolli-leg"></div></div>
<div class="two"><div class="panel"><h3 id="slope-title"></h3><div id="slope"></div><p class="note">Left: share of residents. Right: share of chargers (square-root scale). Red lines climb: the group holds more than its population share; blue lines fall: less. Five largest over-served and six most populous under-served shown.</p></div>
<div class="panel"><h3>Reach by group <span class="sig" id="reach-sub"></span></h3><div id="reach"></div><p class="note" id="reach-note"></p></div></div>
</section>

<section class="ch" data-ch="evidence">
<h2><span class="n">02</span>Key evidence</h2>
<p class="note">Each card is one finding computed from the data, with what it implies for the thesis. Red = equity concern, amber = mixed, green = reassuring. Numbers are population-weighted unless stated.</p>
<div class="ev" id="evidence"></div>
</section>

<section class="ch" data-ch="map">
<h2><span class="n">03</span>Where the supply is</h2>
<p class="note">Colour classes are population-weighted quintiles of the selected layer; hatched = zero. Hover or tap for numbers.</p>
<div class="panel"><div class="controls"><label>Layer <select id="layer"></select></label><span class="note" id="map-note"></span></div><div id="map"></div><div class="mapleg" id="mapleg"></div></div>
<div class="lists" id="lists"></div>
</section>

<section class="ch" data-ch="unequal">
<h2><span class="n">04</span>How unequal is the supply?</h2>
<p class="note">Equality asks whether supply is spread in proportion to people, without asking who the people are. Lorenz curves line units up from the lowest to the highest chargers per resident; the Gini is twice the area between the curve and the diagonal.</p>
<div class="two"><div class="panel"><h3>Lorenz curves — supply per resident vs population</h3><div id="lorenz"></div><div class="legend"><span><i style="background:var(--s1)"></i>Chargers</span><span><i style="background:var(--s2)"></i>Capacity (kW)</span><span><i style="background:var(--fg3);height:1px"></i>Perfect equality</span></div></div>
<div class="panel"><h3>Concentration of supply</h3><div class="scroll" style="max-height:none" id="market"></div><p class="note" id="market-note"></p></div></div>
</section>

<section class="ch" data-ch="inequitable">
<h2><span class="n">05</span>Is it inequitable — does supply follow advantage?</h2>
<p class="note" id="forest-note"></p>
<div class="panel"><div id="forest"></div><div class="legend" id="forest-leg"></div><details><summary>Table of values</summary><div class="scroll" id="forest-table"></div></details></div>
<div class="panel"><div class="controls"><label>Rank residents by <select id="cv-rank"></select></label><label>Supply <select id="cv-out"></select></label></div><div id="curve"></div><p class="note" id="curve-note"></p></div>
</section>

<section class="ch" data-ch="fifths">
<h2><span class="n">06</span>Fifths of the population</h2>
<p class="note">Residents are split into five groups of equal population by the ranking variable (Q1 = lowest). If supply were proportional to people, every bar would be the same height. Each staircase icon ≈ <span id="stair-unit"></span>.</p>
<div class="panel"><h3>The quintile staircase — by spending per person</h3><div class="stairs" id="stairs"></div></div>
<div class="panel"><div class="controls"><label>Rank by <select id="q-rank"></select></label></div><div class="three" id="quint"></div><p class="note" id="q-note"></p></div>
</section>

<section class="ch" data-ch="scatter">
<h2><span class="n">07</span>Every unit at once</h2>
<p class="note">Each bubble is one unit (size = residents). Horizontal axis: the ranking variable. Vertical: chargers per 100,000 residents (square-root scale). Spearman's ρ measures the rank association.</p>
<div class="panel"><div class="controls"><label>Horizontal axis <select id="sc-rank"></select></label><span id="sc-note" class="note"></span></div><div id="scatter"></div><div class="legend"><span><i class="dot" style="background:var(--s1)"></i>Regency (kabupaten)</span><span><i class="dot" style="background:var(--s2)"></i>City (kota)</span><span><i class="dot" style="background:var(--hatch)"></i>No charger</span></div></div>
</section>

<section class="ch" data-ch="inside">
<h2><span class="n">08</span><span id="within-title"></span></h2>
<p class="note" id="within-note"></p>
<div class="panel"><div id="within"></div><details><summary>Table</summary><div class="scroll" id="within-table"></div></details></div>
</section>

<section class="ch" data-ch="sources">
<h2><span class="n">09</span>Where the inequality comes from</h2>
<p class="note">Theil's T of chargers per resident splits exactly into inequality <i>between</i> groups and <i>within</i> them.</p>
<div class="panel"><div id="theil"></div></div><div id="groups"></div>
</section>

<section class="ch" data-ch="robust">
<h2><span class="n">10</span>Does the verdict survive subsetting?</h2>
<p class="note">The headline indices recomputed on subsets. If a sign flips, the finding depends on which units are in the frame.</p>
<div class="panel"><div class="scroll" style="max-height:none" id="robust"></div></div>
</section>

<section class="ch" data-ch="equalise">
<h2><span class="n">11</span>What it would take to equalise</h2>
<p class="note">Chargers to add so that every unit reaches today's average per 100,000 residents, holding existing chargers in place (water-filling). A yardstick, not a recommendation.</p>
<div class="panel"><div class="big" id="deficit-kpi" style="margin-top:0"></div><div class="lists" id="deficit-list"></div></div>
</section>

<section class="ch" data-ch="table">
<h2><span class="n">12</span><span id="pt-title"></span></h2>
<div class="panel"><div class="scroll" id="pt"></div><p class="note">Click a header to sort.</p></div>
</section>

<section class="ch" data-ch="method">
<h2><span class="n">13</span>Method, sources and limits</h2>
<div class="panel" id="method"></div>
<details open><summary>Glossary</summary><dl class="gloss">
<dt>Concentration index (CI)</dt><dd>C = 2·cov<sub>w</sub>(supply per resident, population-weighted fractional rank) / mean; equivalent to 1 − 2∫L(p)dp on the concentration curve. Positive = supply concentrated among residents high on the ranking.</dd>
<dt>Erreygers CI</dt><dd>Correction for bounded outcomes (a yes/no flag or a 0–100 % share): 8·cov<sub>w</sub>(y, R)/(max−min).</dd>
<dt>95 % band</dt><dd>Percentile bootstrap over units (1,000 resamples). "Significant" = band excludes zero.</dd>
<dt>Gini (per resident)</dt><dd>Inequality of chargers per resident across units, weighted by residents; blind to who is rich or poor.</dd>
<dt>HHI / N<sub>eff</sub> / CR<sub>k</sub></dt><dd>Herfindahl index of supply shares (0–10,000), its inverse, and the share held by the top k units.</dd>
<dt>Theil T</dt><dd>Entropy inequality measure that decomposes exactly into between- and within-group parts.</dd>
<dt>20:20, Palma</dt><dd>Share of chargers held by the best-served 20 % of residents over the worst-served 20 %; Palma = top 10 % over bottom 40 %.</dd>
</dl></details>
<p class="note" style="margin-top:20px">Companion pages: <a href="concentration_national_en.html">national evidence</a> · <a href="concentration_jabar_en.html">West Java evidence</a> · <a href="concentration_dashboard_en.html">interactive West Java explorer with scenarios</a> · <a href="../index.html#tab=ttm">travel-time access pilot</a>.</p>
</section>

<div class="pager"><button type="button" class="btn" id="prev">← Previous</button><span id="pager-pos" class="note"></span><button type="button" class="btn" id="next">Next →</button></div>
</div>
<div class="tip" id="tip" hidden></div>
<script>
const ALL = __ALL__; const GEOS = __GEO__;
const NS = "http://www.w3.org/2000/svg"; const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const fmt = (x, d=0) => (x==null||isNaN(x)) ? "–" : (+x).toLocaleString("en-US", {minimumFractionDigits:d, maximumFractionDigits:d});
const sgn = x => (x==null||isNaN(x)) ? "–" : (x>0?"+":"") + (+x).toFixed(3);
const pct = (x, d=1) => fmt(x, d) + " %";
const esc = s => String(s??"").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const el = (t, a={}, parent) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (parent) parent.appendChild(e); return e; };
const $ = id => document.getElementById(id);
const tip = $("tip");
function showTip(ev, html){ tip.innerHTML = html; tip.hidden = false; const w = tip.offsetWidth, h = tip.offsetHeight; tip.style.left = Math.min(ev.clientX + 14, innerWidth - w - 8) + "px"; tip.style.top = (ev.clientY + 16 + h > innerIndexHeight() ? ev.clientY - h - 10 : ev.clientY + 16) + "px"; }
const innerIndexHeight = () => innerHeight; const hideTip = () => tip.hidden = true;
const ICON = { plug: '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 2v5M15 2v5M6 7h12v4a6 6 0 0 1-12 0zM12 17v5"/></svg>',
  people: '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="9" cy="8" r="3.2"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="9" r="2.6"/><path d="M15.5 20a4.5 4.5 0 0 1 6 0" /></svg>',
  scale: '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18M4 21h16M4 7l8-2 8 2M4 7l-2 7a4 4 0 0 0 8 0L8 7M20 7l-2 7a4 4 0 0 0 8 0l-2-7" transform="translate(-2 0) scale(.92 1)"/></svg>',
  pin: '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s7-6.5 7-12a7 7 0 1 0-14 0c0 5.5 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>',
  gap: '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 20V10M10 20V4M16 20v-7M22 20V14"/></svg>',
  person: '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="3.2"/><path d="M7 22v-8a5 5 0 0 1 10 0v8z"/></svg>',
  charger: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 3h9a2 2 0 0 1 2 2v16H4V5a2 2 0 0 1 2-2zm1.5 3v5h6V6zM12 12l-3 5h2.5L11 21l4-6h-2.5z"/><path d="M18 8h2v6a2 2 0 0 0 4 0V9l-2-2" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>' };

let S = "national", D, GEO, M, U, RL, OL, NAT, UNIT, UNITS, PARENT, PARENTS, bbox = null;
const B = (r, o) => D.B.find(b => b.rank === r && b.outcome === o);
function load(scope){ S = scope; D = ALL[scope]; GEO = GEOS[scope]; M = D.meta; NAT = scope === "national"; bbox = null;
  U = D.units.map(a => { const o = {}; D.unit_cols.forEach((c, i) => o[c] = a[i]); o.per100k = 1e5*o.ch/o.pop; o.kw100k = 1e5*o.kw/o.pop; o.npov = -o.pov; if (!NAT){ o.ev100k = 1e5*o.ev/o.pop; o.kwhpc = o.kwh/o.pop; } return o; });
  RL = Object.fromEntries(M.ranks.map(r => [r.key, r])); OL = Object.fromEntries(M.outcomes.map(o => [o.key, o.label])); UNIT = M.unit; UNITS = M.unit_pl; PARENT = M.parent; PARENTS = M.parent_pl;
  document.body.dataset.scope = scope; document.querySelectorAll(".seg button").forEach(b => b.setAttribute("aria-pressed", b.dataset.s === scope)); }

// ---------- hero
function hero(){ const cov = D.A.coverage, exCh = B("exp","ch"), qe = D.Q.exp;
  $("eyebrow").textContent = `${M.title} · ${M.period} · ${fmt(M.chargers)} chargers · ${fmt(M.n_units)} ${UNITS} in ${fmt(M.n_parents)} ${PARENTS} · ${fmt(M.pop/1e6,1)} million residents`;
  $("h1").textContent = NAT ? "Who gets Indonesia's public EV chargers?" : "Who gets West Java's public EV chargers?";
  $("lede").innerHTML = NAT ? `Indonesia's public charging network grew to ${fmt(M.chargers)} chargers at ${fmt(M.sites)} sites by June 2026. Counted per resident it is <b>unequal</b> (a few districts hold most of it) and <b>inequitable</b> (it follows income, development and density). This page separates those two claims, shows where the gap sits — mostly <i>between provinces</i> — and tests whether the verdict survives changing the frame.` :
    `West Java has ${fmt(M.chargers)} chargers across ${fmt(M.n_units)} sub-districts. Counted per resident, <b>placement</b> is spread almost regardless of income — but <b>capacity</b> and especially <b>use</b> (energy actually sold) tilt sharply toward richer districts. The gap here sits <i>inside</i> districts, not between them.`;
  const tiles = [[ICON.plug, fmt(M.chargers), `public chargers · ${fmt(1e5*M.chargers/M.pop,2)} per 100,000 residents`], [ICON.people, pct(cov.pop_share,0), `of residents live in a ${UNIT} that has at least one charger`],
    [ICON.scale, sgn(exCh.ci), `concentration index, chargers vs spending per person — ${exCh.signif ? "significantly pro-rich" : "not distinguishable from zero"}`], [ICON.gap, `${fmt(qe[4].ch_per100k/Math.max(qe[0].ch_per100k,1e-6),1)}×`, `chargers per resident: richest fifth vs poorest fifth`],
    NAT ? [ICON.pin, pct(M.beyond25,0), `of residents live more than 25 km from any charger (${fmt(M.pop*M.beyond25/100/1e6,1)} M people)`] : [ICON.pin, `${fmt(qe[4].kwh_per100k/Math.max(qe[0].kwh_per100k,1e-6),1)}×`, `energy sold per resident: richest fifth vs poorest fifth`]];
  $("big").innerHTML = tiles.map(t => `<div class="t">${t[0]}<div><div class="v">${t[1]}</div><div class="l">${t[2]}</div></div></div>`).join("");
  const tp = D.D.theil_parent;
  $("story").innerHTML = [["Unequal", `Top 20 % of residents by supply hold <b>${pct(100*D.D.top20_share,0)}</b> of chargers; Gini ${D.A.gini_pc.ch.toFixed(2)}.`], ["Inequitable", `${exCh.signif ? "Chargers follow income: CI " + sgn(exCh.ci) + ", band excludes zero." : "Placement is income-neutral (CI " + sgn(exCh.ci) + "), but capacity (" + sgn(B("exp","kw").ci) + ") and use (" + sgn(B("exp","kwh").ci) + ") are not."}`],
    ["Where", `${pct(100*tp.between_share,0)} of the inequality is <b>between ${PARENTS}</b>; ${pct(100*(1-tp.between_share),0)} inside them.`], ["What it takes", `<b>${fmt(D.G.deficit)}</b> more chargers (+${pct(100*D.G.deficit/M.chargers,0)}) to lift every ${UNIT} to today's average.`]]
    .map((s, i) => `<div class="st"><span class="k">${i+1}</span><b>${s[0]}</b>${s[1]}</div>`).join("");
}

// ---------- waffles: 100 residents
function waffles(){ const q = D.Q.exp, box = $("waffles"); box.innerHTML = "";
  const groups = [["The poorest fifth", q[0], "--crit"], ["The middle fifth", q[2], "--s4"], ["The richest fifth", q[4], "--good"]];
  $("w-note").textContent = NAT ? "Each square is 1 % of that group's residents, coloured by how far they live from the nearest public charger (straight-line, operational chargers, June 2026). Groups are fifths of the population by spending per person in their district." : "Each square is 1 % of that group's residents, coloured by whether their own sub-district has a public charger (containment, not distance). Groups are fifths of the population by spending per person in their district.";
  groups.forEach(([lab, g, col]) => { const cells = []; let a, b, c;
    if (NAT){ a = Math.round(g.within10); c = Math.round(g.beyond25); b = Math.max(0, 100 - a - c); for (let i = 0; i < 100; i++) cells.push(i < a ? "--s3" : i < a + b ? "--s4" : "--crit"); }
    else { a = Math.round(100 - g.pop_no_charger_pct); b = 0; c = 100 - a; for (let i = 0; i < 100; i++) cells.push(i < a ? "--s3" : "--crit"); }
    const d = document.createElement("div"); d.className = "waffle";
    d.innerHTML = `<h3>${lab} <span class="sig">· ${fmt(g.pop/1e6,1)} M people · ${fmt(g.ch_per100k,2)} chargers per 100k</span></h3><div class="grid">${cells.map(cc => `<div class="p" style="background:var(${cc})"></div>`).join("")}</div>
      <div class="sum">${NAT ? `<span><i class="dot" style="display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--s3);margin-right:5px"></i><b>${a}</b> within 10 km</span><span><i style="display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--s4);margin-right:5px"></i><b>${b}</b> 10–25 km</span><span><i style="display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--crit);margin-right:5px"></i><b>${c}</b> beyond 25 km</span>` : `<span><i style="display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--s3);margin-right:5px"></i><b>${a}</b> live in a sub-district with a charger</span><span><i style="display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--crit);margin-right:5px"></i><b>${c}</b> in one without</span>`}</div>`;
    box.appendChild(d); }); }

// ---------- quintile staircase
function stairs(){ const q = D.Q.exp, box = $("stairs"); box.innerHTML = ""; const unit = NAT ? 0.25 : 0.1; $("stair-unit").textContent = `${unit} chargers per 100,000 residents`;
  const labs = ["Q1 poorest", "Q2", "Q3", "Q4", "Q5 richest"];
  q.forEach((g, i) => { const n = g.ch_per100k/unit, full = Math.floor(n), half = n - full >= 0.5; const d = document.createElement("div"); d.className = "col";
    d.innerHTML = `<div class="icons">${Array.from({length: full}, () => ICON.charger).join("")}${half ? ICON.charger.replace("<svg", '<svg class="half"') : ""}</div><div class="v">${fmt(g.ch_per100k,2)}</div><div class="lab">${labs[i]}<br><span class="sig">${fmt(g.ch)} chargers · ${fmt(g.pop/1e6,1)} M people</span></div>`; box.appendChild(d); }); }

// ---------- province / district gap
function gap(){ const PT = D.PT, m = $("gap-metric");
  const metrics = NAT ? [["per100k","Chargers per 100,000 residents", v => fmt(v,2)], ["within10","Residents within 10 km of a charger (%)", v => fmt(v,1)], ["beyond25","Residents beyond 25 km (%)", v => fmt(v,1)], ["cov","Residents in districts with a charger (%)", v => fmt(v,1)], ["kw","Charging capacity (kW)", v => fmt(v)], ["exp","Spending per person (k Rp)", v => fmt(v)]]
    : [["per100k","Chargers per 100,000 residents", v => fmt(v,2)], ["cov","Residents in sub-districts with a charger (%)", v => fmt(v,1)], ["kwh","Energy sold Mar-2026 (kWh)", v => fmt(v)], ["kw","Charging capacity (kW)", v => fmt(v)], ["exp","Spending per person (k Rp)", v => fmt(v)]];
  if (!m.dataset.scope || m.dataset.scope !== S){ m.innerHTML = metrics.map(x => `<option value="${x[0]}">${x[1]}</option>`).join(""); m.dataset.scope = S; }
  const key = m.value || "per100k", MT = metrics.find(x => x[0] === key);
  $("gap-title").textContent = NAT ? "The province gap" : "The district gap";
  $("gap-note").textContent = NAT ? "Every province ranked on the chosen measure. The dashed line is the population-weighted national value; bubble size is population; blue = Java, orange = outside Java." : "Every district (kabupaten/kota) ranked on the chosen measure; dashed line = West Java value; bubble size = population; orange = city (kota).";
  const rows = [...PT].sort((a,b) => b[key] - a[key]); const avg = rows.reduce((s,r) => s + r[key]*r.pop, 0) / rows.reduce((s,r) => s + r.pop, 0);
  const rowH = 20, lab = 170, W = 980, H = rows.length*rowH + 34, vmax = Math.max(...rows.map(r => r[key])) * 1.08, X = v => lab + v/vmax*(W-lab-80), pmax = Math.max(...rows.map(r => r.pop));
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":"Ranking"});
  const ticks = 5; for (let i = 0; i <= ticks; i++){ const v = vmax*i/ticks; el("line", {x1:X(v), x2:X(v), y1:0, y2:H-24, stroke:css("--grid")}, svg); el("text", {x:X(v), y:H-8, "text-anchor":"middle"}, svg).textContent = MT[2](v); }
  el("line", {x1:X(avg), x2:X(avg), y1:0, y2:H-24, stroke:css("--fg3"), "stroke-dasharray":"4 3"}, svg); el("text", {x:X(avg)+4, y:12, "font-size":11, fill:css("--fg")}, svg).textContent = `${NAT ? "Indonesia" : "West Java"} ${MT[2](avg)}`;
  rows.forEach((r, i) => { const y = i*rowH + 22, col = NAT ? (r.java ? "--s1" : "--s2") : (r.parent.startsWith("Kota") ? "--s2" : "--s1");
    el("text", {x:lab-8, y:y+4, "text-anchor":"end", fill:css("--fg"), "font-size":11.5}, svg).textContent = r.parent;
    el("line", {x1:lab, x2:X(r[key]), y1:y, y2:y, stroke:css(col), "stroke-width":2, "stroke-opacity":.5}, svg);
    const c = el("circle", {cx:X(r[key]), cy:y, r: 3 + 7*Math.sqrt(r.pop/pmax), fill:css(col), stroke:css("--bg"), "stroke-width":1.2}, svg);
    el("text", {x:X(r[key]) + 6 + 7*Math.sqrt(r.pop/pmax), y:y+4, "font-size":11}, svg).textContent = MT[2](r[key]);
    c.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(r.parent)}</b><br>${fmt(r.pop/1e6,2)} M residents · ${fmt(r.chargers)} chargers · ${fmt(r.per100k,2)} per 100k${NAT ? `<br>${pct(r.within10)} within 10 km · ${pct(r.beyond25)} beyond 25 km` : `<br>${fmt(r.kwh)} kWh sold`}<br>spending ${fmt(r.exp)}k · HDI ${fmt(r.ipm,1)} · ${pct(r.cov)} in ${UNITS} with a charger`)); c.addEventListener("pointerleave", hideTip); });
  $("lolli").innerHTML = ""; $("lolli").appendChild(svg);
  $("lolli-leg").innerHTML = NAT ? `<span><i class="dot" style="background:var(--s1)"></i>Java</span><span><i class="dot" style="background:var(--s2)"></i>Outside Java</span><span><i style="background:var(--fg3);height:1px"></i>national value</span>` : `<span><i class="dot" style="background:var(--s1)"></i>Regency</span><span><i class="dot" style="background:var(--s2)"></i>City</span><span><i style="background:var(--fg3);height:1px"></i>West Java value</span>`;
  const top = rows[0], bot = rows[rows.length-1]; $("gap-sum").innerHTML = `Top: <b>${esc(top.parent)}</b> ${MT[2](top[key])} · bottom: <b>${esc(bot.parent)}</b> ${MT[2](bot[key])}${key === "per100k" ? ` · <b>${fmt(top[key]/Math.max(bot[key],1e-6),0)}×</b>` : ""}`;
  // slope chart: share of people -> share of chargers, top 6 & bottom 6 parents by ratio
  const tg = D.D.theil_parent.groups.slice(); const over = tg.filter(g => g.ratio >= 1.15).sort((a,b) => b.supply_share - a.supply_share).slice(0,5), under = tg.filter(g => g.ratio < 0.85).sort((a,b) => b.pop_share - a.pop_share).slice(0,6); const pick = [...over, ...under];
  const W2 = 520, H2 = 400, m2 = {l:150, r:150, t:24, b:20}, smax = Math.max(...pick.map(g => Math.max(g.pop_share, g.supply_share)));
  const Y2 = v => m2.t + (1 - Math.sqrt(v/smax))*(H2-m2.t-m2.b); const svg2 = el("svg", {viewBox:`0 0 ${W2} ${H2}`, role:"img"});
  const dodge = arr => { const o = arr.map((v,i) => [v,i]).sort((a,b) => a[0]-b[0]); for (let k = 1; k < o.length; k++) if (o[k][0] - o[k-1][0] < 13) o[k][0] = o[k-1][0] + 13; const out = []; o.forEach(([v,i]) => out[i] = v); return out; };
  const yl = dodge(pick.map(g => Y2(g.pop_share))), yr = dodge(pick.map(g => Y2(g.supply_share)));
  el("text", {x:m2.l, y:14, "text-anchor":"middle", "font-weight":600, fill:css("--fg")}, svg2).textContent = "share of residents"; el("text", {x:W2-m2.r, y:14, "text-anchor":"middle", "font-weight":600, fill:css("--fg")}, svg2).textContent = "share of chargers";
  el("line", {x1:m2.l, x2:m2.l, y1:m2.t, y2:H2-m2.b, stroke:css("--line")}, svg2); el("line", {x1:W2-m2.r, x2:W2-m2.r, y1:m2.t, y2:H2-m2.b, stroke:css("--line")}, svg2);
  pick.forEach((g, i) => { const up = g.ratio >= 1, col = up ? "--crit" : "--s1"; el("line", {x1:m2.l, y1:Y2(g.pop_share), x2:W2-m2.r, y2:Y2(g.supply_share), stroke:css(col), "stroke-width":2, "stroke-opacity":.8}, svg2);
    el("circle", {cx:m2.l, cy:Y2(g.pop_share), r:3.5, fill:css(col)}, svg2); el("circle", {cx:W2-m2.r, cy:Y2(g.supply_share), r:3.5, fill:css(col)}, svg2);
    el("text", {x:m2.l-8, y:yl[i]+4, "text-anchor":"end", "font-size":11}, svg2).textContent = `${g.group} ${pct(100*g.pop_share,1)}`;
    el("text", {x:W2-m2.r+8, y:yr[i]+4, "font-size":11, fill:css(col)}, svg2).textContent = `${pct(100*g.supply_share,1)} (${fmt(g.ratio,1)}×)`; });
  $("slope").innerHTML = ""; $("slope").appendChild(svg2); $("slope-title").textContent = `People → chargers: the most over- and under-served ${PARENTS}`;
  // reach by group (national: within10/10-25/beyond25 by island; jabar: coverage by metro)
  const grp = NAT ? D.D.groups.find(g => g.name === "By island group") : D.D.groups.find(g => g.name === "Metropolitan areas vs outside"); const rr = grp.rows.slice().sort((a,b) => (NAT ? b.within10 - a.within10 : b.cov - a.cov));
  const W3 = 520, rowH3 = 26, H3 = rr.length*rowH3 + 30, lab3 = 150, X3 = v => lab3 + v/100*(W3-lab3-10); const svg3 = el("svg", {viewBox:`0 0 ${W3} ${H3}`, role:"img"});
  rr.forEach((r, i) => { const y = i*rowH3 + 6; el("text", {x:lab3-8, y:y+13, "text-anchor":"end", fill:css("--fg"), "font-size":11.5}, svg3).textContent = r.group;
    if (NAT){ const a = r.within10, c = Math.max(0, 100 - a - 0); // beyond25 not in group rows; show within10 vs rest
      el("rect", {x:X3(0), y, width:X3(a)-X3(0)-1, height:16, rx:3, fill:css("--s3")}, svg3); el("rect", {x:X3(a)+1, y, width:Math.max(0,X3(100)-X3(a)-1), height:16, rx:3, fill:css("--grid")}, svg3); el("text", {x:X3(a)+(a>50?-6:6), y:y+12, "text-anchor":a>50?"end":"start", "font-size":11, fill:a>50?"#fff":css("--fg")}, svg3).textContent = pct(a,0) + " within 10 km"; }
    else { const a = r.cov; el("rect", {x:X3(0), y, width:X3(a)-X3(0)-1, height:16, rx:3, fill:css("--s3")}, svg3); el("rect", {x:X3(a)+1, y, width:Math.max(0,X3(100)-X3(a)-1), height:16, rx:3, fill:css("--grid")}, svg3); el("text", {x:X3(a)+(a>50?-6:6), y:y+12, "text-anchor":a>50?"end":"start", "font-size":11, fill:a>50?"#fff":css("--fg")}, svg3).textContent = pct(a,0) + " covered"; } });
  $("reach").innerHTML = ""; $("reach").appendChild(svg3); $("reach-sub").textContent = NAT ? "· by island group" : "· by metropolitan area"; $("reach-note").textContent = NAT ? "Share of residents living within 10 km of an operational charger. Papua and Maluku are the reach deserts; Java is the only island above 75 %." : "Share of residents whose sub-district contains a charger. Greater Cirebon is metropolitan in name only for charging.";
}

// ---------- evidence cards
function evidence(){ const cards = [], cov = D.A.coverage, exCh = B("exp","ch"), exKw = B("exp","kw"), qe = D.Q.exp, grp = n => D.D.groups.find(g => g.name === n), cls = b => b.signif ? (b.ci > 0 ? "crit" : "good") : "warn";
  cards.push({c: cls(exCh), big: sgn(exCh.ci), small: "CI chargers ~ spending", t: exCh.signif ? `Chargers are concentrated in ${exCh.ci>0?"richer":"poorer"} ${UNITS}` : "Charger placement is not measurably tilted by income", d: `${pct(100*qe[0].ch/M.chargers)} of chargers serve the poorest fifth of residents, ${pct(100*qe[4].ch/M.chargers)} the richest fifth (band ${sgn(exCh.lo)} to ${sgn(exCh.hi)}).`, so: exCh.signif ? `<b>Vertical-equity pass rule fails</b> (proposal §5.8: CI ≤ 0 with band not crossing zero).` : `<b>Placement passes the equity test on counts</b> — but see capacity and use.`});
  cards.push({c: cls(exKw), big: sgn(exKw.ci), small: "CI capacity (kW) ~ spending", t: exKw.ci > exCh.ci + 0.05 ? "Capacity is more pro-rich than counts" : "Capacity tracks counts", d: `Counting kilowatts instead of units ${exKw.ci > exCh.ci + 0.05 ? "raises the index from "+sgn(exCh.ci)+" to "+sgn(exKw.ci)+": the bigger, faster chargers go where spending is higher." : "leaves the index at "+sgn(exKw.ci)+"."}`, so: `<b>A 7 kW and a 200 kW unit are not the same service</b> — the thesis measures capacity, not counts.`});
  if (!NAT){ const bk = B("exp","kwh"); cards.push({c: cls(bk), big: sgn(bk.ci), small: "CI energy sold ~ spending", t: "Use is far more pro-rich than placement", d: `Energy actually dispensed has an index of ${sgn(bk.ci)} against ${sgn(exCh.ci)} for charger counts; the richest fifth draws ${fmt(qe[4].kwh_per100k/Math.max(qe[0].kwh_per100k,1e-6),1)}× the energy per resident of the poorest fifth.`, so: `<b>Access does not convert into use</b> for poorer areas — the capability gap RQ3 is about.`}); }
  else { const bw = B("exp","within10"); cards.push({c: cls(bw), big: sgn(bw.ci), small: "Erreygers CI, residents ≤ 10 km", t: "Reach, not just counts, follows income", d: `${pct(qe[4].within10)} of the richest fifth live within 10 km of a charger against ${pct(qe[0].within10)} of the poorest fifth; ${pct(qe[0].beyond25)} of the poorest fifth live beyond 25 km.`, so: `<b>Step 1 of the service ladder (reachable) already fails</b> for a large poor minority.`}); }
  cards.push({c: "warn", big: pct(100*D.D.top20_share,0), small: "of chargers go to the best-served 20 % of residents", t: `Unequal by any standard: ${D.D.ratio2020 == null ? "the bottom fifth has none" : "20:20 ratio "+fmt(D.D.ratio2020,1)+"×"}`, d: `Ranked by chargers per resident, the best-served fifth holds ${pct(100*D.D.top20_share,0)} and the worst-served half ${pct(100*D.D.bottom50_share,0)}; Gini ${D.A.gini_pc.ch.toFixed(2)}, HHI ${fmt(D.A.supply.ch.hhi)} (≈ ${fmt(D.A.supply.ch.n_eff)} equal-sized ${UNITS}).`, so: `<b>Unequal and inequitable are different questions</b> — this card is the first, the CI cards are the second.`});
  cards.push({c: "crit", big: `${fmt(cov.pop_without/1e6,1)} M`, small: `people in ${UNITS} with no charger at all`, t: `${fmt(cov.units_without)} ${UNITS} have zero chargers`, d: `Largest: ${D.A.largest_without.slice(0,3).map(x => `${x.name} (${fmt(x.pop/1e3,0)}k)`).join(", ")}. ${NAT ? "" : "Several are dense, affluent commuter sub-districts — gaps are not only a poverty story."}`, so: `<b>Containment ≠ reach</b>: a charger across the boundary may serve them — the travel-time analysis tests this.`});
  const tp = D.D.theil_parent; cards.push({c: tp.between_share > 0.5 ? "crit" : "warn", big: pct(100*tp.between_share,0), small: `of inequality is between ${PARENTS}`, t: tp.between_share > 0.5 ? `The gap is mostly ${PARENT} vs ${PARENT}` : `The gap lives inside every ${PARENT}`, d: tp.between_share > 0.5 ? `Theil T ${tp.T}: ${pct(100*tp.between_share,0)} between, ${pct(100*(1-tp.between_share),0)} within. ${NAT ? "DKI Jakarta holds "+pct(100*tp.groups.find(g=>g.group==="DKI Jakarta").supply_share,0)+" of chargers for "+pct(100*tp.groups.find(g=>g.group==="DKI Jakarta").pop_share,1)+" of people." : ""}` : `Theil T ${tp.T}: only ${pct(100*tp.between_share,0)} is between ${PARENTS}; ${pct(100*(1-tp.between_share),0)} is between ${UNITS} of the same ${PARENT}.`, so: tp.between_share > 0.5 ? `<b>${PARENT.charAt(0).toUpperCase()+PARENT.slice(1)}-level allocation is the lever.</b>` : `<b>Allocation inside each ${PARENT} is the lever</b>, not transfers between them.`});
  const cr = grp("City vs regency").rows, city = cr.find(r => r.group.startsWith("City")), reg = cr.find(r => r.group.startsWith("Regency"));
  cards.push({c: "warn", big: `${fmt(city.per100k/Math.max(reg.per100k,1e-6),1)}×`, small: "city vs regency, chargers per resident", t: "Cities are served, regencies are not", d: `Cities: ${fmt(city.per100k,2)} per 100,000, ${pct(city.cov)} covered${NAT ? ", "+pct(city.within10)+" within 10 km" : ""}. Regencies: ${fmt(reg.per100k,2)}, ${pct(reg.cov)}${NAT ? ", "+pct(reg.within10)+" within 10 km" : ""}; they hold ${pct(100*reg.pop/(city.pop+reg.pop),0)} of the population.`, so: `<b>Urban form explains part of the income gradient</b> — density and income are entangled; see robustness.`});
  const dch = B("dens","ch"); cards.push({c: cls(dch), big: sgn(dch.ci), small: "CI chargers ~ density", t: "Density gradient", d: `Ranked by density alone the index is ${sgn(dch.ci)}; by spending ${sgn(exCh.ci)}; by HDI ${sgn(B("ipm","ch").ci)}; by poverty ${sgn(B("npov","ch").ci)}.`, so: `<b>${Math.abs(dch.ci) > Math.abs(exCh.ci) ? "Density explains more of the pattern than income" : "Income explains at least as much as density"}</b> — the proposal ranks by HDI, not income, for this reason.`});
  const rob = D.G.robust, flips = rob.filter(r => Math.sign(r.ci_ch) !== Math.sign(exCh.ci) && Math.abs(r.ci_ch) > 0.03);
  cards.push({c: flips.length ? "warn" : "good", big: `${rob.length - flips.length}/${rob.length}`, small: "subsets keep the sign of the headline index", t: flips.length ? "The verdict depends on the frame" : "The verdict is stable across subsets", d: flips.length ? `Sign flips in: ${flips.map(r => r.subset).join(", ")}.` : `Range of CI chargers ~ spending across subsets: ${sgn(Math.min(...rob.map(r=>r.ci_ch)))} to ${sgn(Math.max(...rob.map(r=>r.ci_ch)))}.`, so: `<b>Report the specification curve, not a single number</b> (proposal §5.8).`});
  cards.push({c: "warn", big: fmt(D.G.deficit), small: `chargers to lift every ${UNIT} to the average`, t: `+${pct(100*D.G.deficit/M.chargers,0)} of today's stock`, d: `${fmt(D.G.units_short)} ${UNITS} are below ${fmt(D.G.mean100k,2)} per 100,000. Largest single needs: ${D.G.top.slice(0,3).map(x => `${x.name} (+${x.need})`).join(", ")}.`, so: `<b>Equalising counts is cheap relative to the network's growth rate</b> — the harder question is whether counts are the right target.`});
  $("evidence").innerHTML = cards.map(c => `<div class="card ${c.c}"><div class="bigv">${c.big} <small>${c.small}</small></div><div class="t">${c.t}</div><div class="d">${c.d}</div><div class="so">${c.so}</div></div>`).join(""); }

// ---------- map
function geomPath(g, PX, PY){ const ring = r => r.map((c,i) => (i?"L":"M") + PX(c[0]).toFixed(1) + " " + PY(c[1]).toFixed(1)).join("") + "Z"; return g.type === "Polygon" ? g.coordinates.map(ring).join("") : g.coordinates.map(p => p.map(ring).join("")).join(""); }
function layersFor(){ return [["per100k","Chargers per 100,000 residents", v => fmt(v,2)], ["kw100k","Capacity kW per 100,000", v => fmt(v,0)], ["exp","Spending per person (k Rp/month, district)", v => fmt(v)], ["ipm","HDI (district)", v => fmt(v,1)], ["pov","Poverty rate % (district)", v => fmt(v,1)], ["dens","Residents per km²", v => fmt(v)]].concat(NAT ? [["within10","Residents within 10 km of a charger (%)", v => fmt(v,1)], ["beyond25","Residents beyond 25 km (%)", v => fmt(v,1)], ["dc","DC fast chargers", v => fmt(v)]] : [["kwhpc","kWh sold per resident", v => fmt(v,4)], ["ev100k","EV owners per 100,000", v => fmt(v,2)]]); }
function renderMap(){ const LAYERS = layersFor(), sel = $("layer"); if (sel.dataset.scope !== S){ sel.innerHTML = LAYERS.map(l => `<option value="${l[0]}">${l[1]}</option>`).join(""); sel.dataset.scope = S; }
  const key = sel.value, L = LAYERS.find(l => l[0] === key); const GI = new Map(GEO);
  if (!bbox){ let minx=1e9,miny=1e9,maxx=-1e9,maxy=-1e9; const walk = (c, fn) => typeof c[0] === "number" ? fn(c) : c.forEach(x => walk(x, fn)); GEO.forEach(([id,g]) => walk(g.coordinates, c => { if (c[0]<minx) minx=c[0]; if (c[0]>maxx) maxx=c[0]; if (c[1]<miny) miny=c[1]; if (c[1]>maxy) maxy=c[1]; })); bbox = [minx,miny,maxx,maxy]; }
  const [minx,miny,maxx,maxy] = bbox, MW = 1000, k = Math.cos((miny+maxy)/2*Math.PI/180), MH = Math.round(MW*(maxy-miny)/((maxx-minx)*k)); const PX = x => (x-minx)/(maxx-minx)*MW, PY = y => (maxy-y)/(maxy-miny)*MH;
  const box = $("map"); box.innerHTML = ""; const svg = el("svg", {viewBox:`0 0 ${MW} ${MH}`, role:"img", "aria-label":"Map"}); box.appendChild(svg);
  const defs = el("defs", {}, svg); const pat = el("pattern", {id:"hatch", width:6, height:6, patternUnits:"userSpaceOnUse", patternTransform:"rotate(45)"}, defs); el("rect", {width:6, height:6, fill:css("--zero")}, pat); el("line", {x1:0, y1:0, x2:0, y2:6, stroke:css("--hatch"), "stroke-width":1.5}, pat);
  const us = U.filter(u => GI.has(u.id)); const vals = us.map(u => u[key]); const idx = vals.map((v,i) => i).filter(i => vals[i] > 0).sort((a,b) => vals[a]-vals[b]); const tot = idx.reduce((s,i) => s + us[i].pop, 0);
  const cuts = []; let acc = 0, qn = 1; for (const i of idx){ acc += us[i].pop; if (acc >= tot*qn/5 && cuts.length < 4){ cuts.push(vals[i]); qn++; } }
  const cls = v => v <= 0 ? -1 : (cuts.findIndex(c => v <= c) + 5) % 5; const cols = ["--q1","--q2","--q3","--q4","--q5"];
  us.forEach((u, i) => { const p = el("path", {d:geomPath(GI.get(u.id), PX, PY), class:"u", fill: cls(vals[i]) < 0 ? "url(#hatch)" : css(cols[cls(vals[i])]), stroke:css("--bg"), "stroke-width":NAT?0.5:0.6}, svg);
    p.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(u.name)}</b> · ${esc(u.parent)}<br>${fmt(u.pop)} residents · ${fmt(u.dens)} /km²<br>${u.ch} chargers · ${fmt(u.kw)} kW · ${fmt(u.per100k,2)} per 100k${NAT ? `<br>${pct(u.within10)} within 10 km · ${pct(u.beyond25)} beyond 25 km` : `<br>${fmt(u.kwh)} kWh · ${fmt(u.trx)} sessions · ${u.ev} EV owners`}<br>spending ${fmt(u.exp)}k · HDI ${u.ipm} · poverty ${u.pov} %<br><i>${L[1]}: ${L[2](u[key])}</i>`)); p.addEventListener("pointerleave", hideTip); });
  const edges = idx.length ? [vals[idx[0]], ...cuts, vals[idx[idx.length-1]]] : [];
  $("mapleg").innerHTML = `<div class="sw"><i style="background:repeating-linear-gradient(45deg,var(--zero) 0 3px,var(--hatch) 3px 4px)"></i>zero</div>` + (edges.length ? cols.map((c,j) => `<div class="sw"><i style="background:var(${c})"></i>${L[2](edges[j])}–${L[2](edges[j+1])}</div>`).join("") : "") + `<div style="margin-left:10px">population quintiles of ${L[1].toLowerCase()}</div>`;
  $("map-note").textContent = `${us.length} ${UNITS} drawn`;
  const list = (title, items, f) => `<div class="panel" style="margin-top:0"><h3>${title}</h3><ol>${items.map(x => `<li>${f(x)}</li>`).join("")}</ol></div>`;
  $("lists").innerHTML = list("Most chargers", D.A.top.ch, x => `${esc(x.name)} <span>· ${esc(x.parent)} · ${fmt(x.v)} (${pct(100*x.share,1)})</span>`) + list("Most chargers per 100,000 residents", D.A.per100k_extremes.top, x => `${esc(x.name)} <span>· ${esc(x.parent)} · ${fmt(x.v,2)} · ${fmt(x.pop/1e3,0)}k people</span>`) + list(`Largest ${UNITS} without a charger`, D.A.largest_without, x => `${esc(x.name)} <span>· ${esc(x.parent)} · ${fmt(x.pop/1e3,0)}k people · spending ${fmt(x.exp)}k</span>`) + list(`Fewest chargers per resident among big ${UNITS}`, D.A.per100k_extremes.bottom_big, x => `${esc(x.name)} <span>· ${esc(x.parent)} · ${fmt(x.v,2)} · ${fmt(x.pop/1e3,0)}k people</span>`); }

// ---------- Lorenz & market
function lineChart(id, series, xl, yl){ const W = 520, H = 360, m = {l:56, r:14, t:14, b:44}, pw = W-m.l-m.r, ph = H-m.t-m.b, X = p => m.l + p*pw, Y = p => m.t + (1-p)*ph; const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"});
  for (let i = 0; i <= 4; i++){ const p = i/4; el("line", {x1:X(0), x2:X(1), y1:Y(p), y2:Y(p), stroke:css("--grid")}, svg); el("line", {y1:Y(0), y2:Y(1), x1:X(p), x2:X(p), stroke:css("--grid")}, svg); el("text", {x:X(p), y:H-m.b+16, "text-anchor":"middle"}, svg).textContent = p*100+" %"; el("text", {x:m.l-6, y:Y(p)+4, "text-anchor":"end"}, svg).textContent = p*100+" %"; }
  el("text", {x:X(.5), y:H-6, "text-anchor":"middle"}, svg).textContent = xl; el("text", {x:14, y:Y(.5), "text-anchor":"middle", transform:`rotate(-90 14 ${Y(.5)})`}, svg).textContent = yl; el("line", {x1:X(0), y1:Y(0), x2:X(1), y2:Y(1), stroke:css("--fg3"), "stroke-dasharray":"3 3"}, svg);
  const interp = (pts, x) => { for (let i = 1; i < pts.length; i++) if (pts[i][0] >= x){ const [x0,y0] = pts[i-1], [x1,y1] = pts[i]; return x1 === x0 ? y1 : y0 + (y1-y0)*(x-x0)/(x1-x0); } return 1; };
  series.forEach(s => { el("path", {d: s.pts.map((p,i) => (i?"L":"M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1)).join(""), fill:"none", stroke:css(s.col), "stroke-width":2, "stroke-linejoin":"round"}, svg); if (s.lab) el("text", {x:s.at[0], y:s.at[1], fill:css(s.col), "font-weight":600}, svg).textContent = s.lab; });
  const cross = el("line", {y1:Y(0), y2:Y(1), stroke:css("--fg3"), visibility:"hidden"}, svg); const hit = el("rect", {x:m.l, y:m.t, width:pw, height:ph, fill:"transparent"}, svg);
  hit.addEventListener("pointermove", ev => { const rc = svg.getBoundingClientRect(); const p = Math.max(0, Math.min(1, ((ev.clientX-rc.left)*W/rc.width - m.l)/pw)); cross.setAttribute("x1", X(p)); cross.setAttribute("x2", X(p)); cross.setAttribute("visibility", "visible"); showTip(ev, `<b>Bottom ${fmt(p*100)} % of residents</b><br>` + series.map(s => `${s.name}: ${fmt(interp(s.pts,p)*100,1)} %`).join("<br>")); });
  hit.addEventListener("pointerleave", () => { cross.setAttribute("visibility", "hidden"); hideTip(); }); const box = $(id); box.innerHTML = ""; box.appendChild(svg); }
function lorenz(){ lineChart("lorenz", [{pts: D.A.lorenz.ch, col:"--s1", name:"chargers", lab:`Chargers · Gini ${D.A.gini_pc.ch.toFixed(2)}`, at:[70, 40]}, {pts: D.A.lorenz.kw, col:"--s2", name:"capacity (kW)", lab:`Capacity · Gini ${D.A.gini_pc.kw.toFixed(2)}`, at:[70, 60]}], "Cumulative share of residents (ranked by chargers per resident, low → high)", "Cumulative share of supply");
  const mk = D.A.supply; const mrows = Object.keys(mk).map(k => [OL[k] || k, mk[k]]).concat([["Residents (comparator)", D.A.pop]]);
  $("market").innerHTML = `<table><thead><tr><th>Supply</th><th>${UNITS} &gt; 0</th><th>HHI</th><th>N<sub>eff</sub></th><th>Top 1</th><th>Top 4</th><th>Top 10</th><th>Gini</th></tr></thead><tbody>${mrows.map(([l,b]) => `<tr><td>${l}</td><td>${fmt(b.n)}</td><td>${fmt(b.hhi)}</td><td>${fmt(b.n_eff)}</td><td>${pct(100*b.cr1)}</td><td>${pct(100*b.cr4)}</td><td>${pct(100*b.cr10)}</td><td>${b.gini.toFixed(2)}</td></tr>`).join("")}</tbody></table>`;
  $("market-note").innerHTML = `Top 10 % of residents (by chargers per resident) hold <b>${pct(100*D.D.top10_share,0)}</b> of chargers; bottom 50 % hold <b>${pct(100*D.D.bottom50_share,0)}</b>. 20:20 ratio ${D.D.ratio2020 == null ? "undefined (bottom fifth has none)" : fmt(D.D.ratio2020,1)+"×"}; Palma ${D.D.palma == null ? "undefined" : fmt(D.D.palma,1)}. Residents themselves are spread with HHI ${fmt(D.A.pop.hhi)} — every supply measure is many times more concentrated than people are.`; }

// ---------- forest
function forest(){ $("forest-note").innerHTML = `The concentration index (CI) ranks residents by a socio-economic variable (low → high) and reads how much of the supply the bottom x % receive. +1 = everything at the top, 0 = proportional, −1 = everything at the bottom. Dots are estimates, bars are 95 % bootstrap bands (${fmt(M.boot)} resamples of ${UNITS}); filled dots do not cross zero. For yes/no and share outcomes the Erreygers-corrected index is shown.`;
  const outs = M.outcomes.map(o => o.key), ranks = M.ranks.map(r => r.key); const rows = []; ranks.forEach(r => outs.forEach(o => { const b = B(r,o); if (b) rows.push({...b, lab: OL[o], grp: RL[r].label}); }));
  const rowH = 22, lab = 250, W = 900, H = rows.length*rowH + ranks.length*18 + 34, lo = Math.min(-0.2, ...rows.map(x => x.lo)) - 0.05, hi = Math.max(0.3, ...rows.map(x => x.hi)) + 0.05, X = v => lab + (v-lo)/(hi-lo)*(W-lab-30);
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"}); [-0.5,-0.25,0,0.25,0.5,0.75].filter(v => v > lo && v < hi).forEach(v => { el("line", {x1:X(v), x2:X(v), y1:0, y2:H-24, stroke: v ? css("--grid") : css("--fg3")}, svg); el("text", {x:X(v), y:H-8, "text-anchor":"middle"}, svg).textContent = (v>0?"+":"") + v; });
  el("text", {x:X(hi)-4, y:12, "text-anchor":"end", "font-size":11}, svg).textContent = "→ supply concentrated at the TOP of the ranking"; el("text", {x:lab+4, y:12, "font-size":11}, svg).textContent = "← at the BOTTOM";
  let y = 20, g0 = null; rows.forEach(r => { if (r.grp !== g0){ y += 18; el("text", {x:4, y:y-4, "font-weight":700, fill:css("--fg")}, svg).textContent = "Ranked by " + r.grp; g0 = r.grp; }
    const yy = y + rowH/2; el("text", {x:lab-10, y:yy+4, "text-anchor":"end"}, svg).textContent = r.lab; const col = r.outcome === "has" || r.outcome === "within10" ? "--s3" : (NAT ? "--s1" : (["kwh","trx","ev"].includes(r.outcome) ? "--s2" : "--s1"));
    el("line", {x1:X(r.lo), x2:X(r.hi), y1:yy, y2:yy, stroke:css(col), "stroke-width":2}, svg); const c = el("circle", {cx:X(r.ci), cy:yy, r:5, fill: r.signif ? css(col) : css("--bg"), stroke:css(col), "stroke-width":2}, svg); el("text", {x:X(r.hi)+8, y:yy+4, "font-size":11}, svg).textContent = sgn(r.ci);
    c.addEventListener("pointermove", ev => showTip(ev, `<b>${r.lab}</b> ranked by ${r.grp}<br>CI ${sgn(r.ci)} · 95 % ${sgn(r.lo)} to ${sgn(r.hi)}<br>${r.signif ? "band excludes zero" : "not distinguishable from zero"}`)); c.addEventListener("pointerleave", hideTip); y += rowH; });
  $("forest").innerHTML = ""; $("forest").appendChild(svg);
  $("forest-leg").innerHTML = `<span><i class="dot" style="background:var(--s1)"></i>Placement & capacity</span>${NAT ? "" : `<span><i class="dot" style="background:var(--s2)"></i>Use & demand (kWh, sessions, EV owners)</span>`}<span><i class="dot" style="background:var(--s3)"></i>Erreygers (yes/no, share)</span><span class="sig">● filled = 95 % band excludes 0 · ○ hollow = not significant</span>`;
  $("forest-table").innerHTML = `<table><thead><tr><th>Ranked by</th><th>Supply</th><th>CI</th><th>95 % low</th><th>95 % high</th><th>Sig.</th></tr></thead><tbody>${rows.map(r => `<tr><td>${r.grp}</td><td style="text-align:left">${r.lab}</td><td class="${r.ci>0?"pos":"neg"}">${sgn(r.ci)}</td><td>${sgn(r.lo)}</td><td>${sgn(r.hi)}</td><td>${r.signif?"●":"○"}</td></tr>`).join("")}</tbody></table>`; }

// ---------- curve
function curveInit(){ const cvR = $("cv-rank"), cvO = $("cv-out"); cvR.innerHTML = M.ranks.map(r => `<option value="${r.key}">${r.label}</option>`).join(""); cvO.innerHTML = M.outcomes.filter(o => o.key !== "has").map(o => `<option value="${o.key}">${o.label}</option>`).join(""); drawCurve(); }
function drawCurve(){ const r = $("cv-rank").value, o = $("cv-out").value, pts = D.curves[r][o], b = B(r,o); lineChart("curve", [{pts, col:"--s1", name:OL[o], lab:`CI ${sgn(b.ci)}${b.signif?"":" (n.s.)"}`, at:[70, 40]}], `Cumulative share of residents, ranked by ${RL[r].label} (low → high)`, `Cumulative share of ${OL[o]}`);
  const q = D.Q[r]; $("curve-note").innerHTML = `Bottom fifth (${RL[r].low}) receives <b>${pct(100*q[0][o]/q.reduce((s,x)=>s+x[o],0))}</b> of ${OL[o]}; top fifth (${RL[r].high}) <b>${pct(100*q[4][o]/q.reduce((s,x)=>s+x[o],0))}</b>. Band ${sgn(b.lo)} to ${sgn(b.hi)}.`; }

// ---------- quintiles
function barChart(vals, labels, col, title, fmtv){ const W = 340, H = 240, m = {l:46, r:10, t:28, b:40}, pw = W-m.l-m.r, ph = H-m.t-m.b, top = Math.max(...vals, 1e-9)*1.15, Y = v => m.t + (1-v/top)*ph, bw = pw/vals.length; const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":title}); el("text", {x:m.l, y:14, "font-weight":600, fill:css("--fg")}, svg).textContent = title;
  [0,.25,.5,.75,1].forEach(f => { el("line", {x1:m.l, x2:W-m.r, y1:Y(f*top), y2:Y(f*top), stroke:css("--grid")}, svg); el("text", {x:m.l-5, y:Y(f*top)+4, "text-anchor":"end", "font-size":10.5}, svg).textContent = fmtv(f*top); });
  vals.forEach((v, i) => { const x = m.l + i*bw + 6, w = bw - 12, y = Y(v); el("path", {d:`M${x} ${m.t+ph}V${y+4}a4 4 0 0 1 4 -4h${w-8}a4 4 0 0 1 4 4V${m.t+ph}Z`, fill:css(col)}, svg); el("text", {x:x+w/2, y:y-5, "text-anchor":"middle", "font-size":11, fill:css("--fg")}, svg).textContent = fmtv(v); el("text", {x:x+w/2, y:H-m.b+16, "text-anchor":"middle", "font-size":11}, svg).textContent = labels[i]; }); return svg; }
function quintInit(){ const qR = $("q-rank"); qR.innerHTML = M.ranks.map(r => `<option value="${r.key}">${r.label}</option>`).join(""); drawQuint(); }
function drawQuint(){ const r = $("q-rank").value, q = D.Q[r], labs = ["Q1 "+RL[r].low.split(" ")[0], "Q2", "Q3", "Q4", "Q5 "+RL[r].high.split(" ")[0]]; const box = $("quint"); box.innerHTML = "";
  const panels = [[q.map(x => x.ch_per100k), "--s1", "Chargers per 100,000 residents", v => fmt(v,2)], [q.map(x => x.kw_per100k), "--s1", "Capacity kW per 100,000", v => fmt(v,0)], NAT ? [q.map(x => x.within10), "--s3", "Residents within 10 km (%)", v => fmt(v,0)] : [q.map(x => x.kwh_per100k/1e5*1000), "--s2", "Energy sold, Wh per resident per month", v => fmt(v,0)]];
  if (!NAT) panels.push([q.map(x => x.ev_per100k), "--s2", "EV owners per 100,000", v => fmt(v,1)]); else panels.push([q.map(x => x.beyond25), "--s3", "Residents beyond 25 km (%)", v => fmt(v,0)]);
  panels.push([q.map(x => x.pop_no_charger_pct), "--s4", `Residents whose ${UNIT} has no charger (%)`, v => fmt(v,0)]);
  panels.forEach(p => { const d = document.createElement("div"); d.appendChild(barChart(p[0], labs, p[1], p[2], p[3])); box.appendChild(d); });
  $("q-note").innerHTML = `Each fifth ≈ ${fmt(q[0].pop/1e6,1)} million residents. ${r === "dens" || r === "ev100k" ? "This variable is measured per " + UNIT + "." : "Socio-economic variables are district-level (BPS 2024)" + (NAT ? "." : ", inherited by sub-districts — so these fifths compare districts, not neighbourhoods.")}`; }

// ---------- scatter
function scatterInit(){ const s = $("sc-rank"); s.innerHTML = M.ranks.map(r => `<option value="${r.key}">${r.label}</option>`).join(""); drawScatter(); }
function drawScatter(){ const r = $("sc-rank").value, xs = U.map(u => r === "npov" ? u.pov : u[r]); const W = 900, H = 420, m = {l:56, r:16, t:14, b:46}, pw = W-m.l-m.r, ph = H-m.t-m.b; const xmin = Math.min(...xs), xmax = Math.max(...xs), logx = r === "dens" || r === "ev100k"; const fx = v => logx ? Math.log10(Math.max(v, 1e-3)) : v; const lo = fx(xmin), hi = fx(xmax);
  const X = v => m.l + (fx(v)-lo)/(hi-lo||1)*pw; const ymax = Math.sqrt(Math.max(...U.map(u => u.per100k))); const Y = v => m.t + (1 - Math.sqrt(v)/ymax)*ph; const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"});
  [0,1,2,5,10,20,50].filter(v => Math.sqrt(v) <= ymax).forEach(v => { el("line", {x1:m.l, x2:W-m.r, y1:Y(v), y2:Y(v), stroke:css("--grid")}, svg); el("text", {x:m.l-6, y:Y(v)+4, "text-anchor":"end"}, svg).textContent = v; });
  const ticks = logx ? [1,10,100,1000,10000,100000].filter(v => v >= xmin && v <= xmax) : Array.from({length:6}, (_,i) => xmin + (xmax-xmin)*i/5); ticks.forEach(v => { el("line", {y1:m.t, y2:m.t+ph, x1:X(v), x2:X(v), stroke:css("--grid")}, svg); el("text", {x:X(v), y:H-m.b+16, "text-anchor":"middle"}, svg).textContent = fmt(v, logx ? 0 : (xmax-xmin > 50 ? 0 : 1)); });
  el("text", {x:m.l+pw/2, y:H-6, "text-anchor":"middle"}, svg).textContent = (r === "npov" ? "Poverty rate (%)" : RL[r].label.replace(/^./, c => c.toUpperCase())) + (logx ? " (log scale)" : ""); el("text", {x:14, y:m.t+ph/2, "text-anchor":"middle", transform:`rotate(-90 14 ${m.t+ph/2})`}, svg).textContent = "Chargers per 100,000 (√ scale)";
  const pmax = Math.max(...U.map(u => u.pop)); U.map((u,i) => [u, xs[i]]).sort((a,b) => b[0].pop - a[0].pop).forEach(([u, x]) => { const rad = 2.5 + 14*Math.sqrt(u.pop/pmax); const c = el("circle", {cx:X(x), cy:Y(u.per100k), r:rad, fill: u.ch ? css(u.kota ? "--s2" : "--s1") : css("--hatch"), "fill-opacity":.55, stroke:css("--bg"), "stroke-width":1}, svg);
    c.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(u.name)}</b> · ${esc(u.parent)}<br>${fmt(u.pop)} residents · ${u.ch} chargers · ${fmt(u.per100k,2)} per 100k<br>spending ${fmt(u.exp)}k · HDI ${u.ipm} · poverty ${u.pov} % · ${fmt(u.dens)} /km²`)); c.addEventListener("pointerleave", hideTip); });
  $("scatter").innerHTML = ""; $("scatter").appendChild(svg); const s = D.S[r]; $("sc-note").innerHTML = `Spearman ρ = <b>${s.rho.toFixed(2)}</b> (n = ${s.n}${s.p < 0.001 ? ", p < 0.001" : ", p = "+s.p})${r === "npov" ? " — on poverty reversed, so positive = more chargers where poverty is lower" : ""}.`; }

// ---------- within
function within(){ $("within-title").textContent = `Inside each ${PARENT}`; $("within-note").textContent = `The same index recomputed within each ${PARENT} (its ${UNITS} ranked by population density). Large positive = that ${PARENT}'s chargers sit in its densest ${UNITS}. Only ${PARENTS} with ≥ 6 ${UNITS} and ≥ 5 chargers.`;
  const rows = D.W; const rowH = 22, lab = 170, W = 900, H = rows.length*rowH + 30, lo = Math.min(-0.2, ...rows.map(x => x.ci_ch_dens)) - 0.05, hi = Math.max(0.3, ...rows.map(x => x.ci_ch_dens)) + 0.1, X = v => lab + (v-lo)/(hi-lo)*(W-lab-230);
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"}); [-0.5,-0.25,0,0.25,0.5,0.75,1].filter(v => v > lo && v < hi).forEach(v => { el("line", {x1:X(v), x2:X(v), y1:0, y2:H-24, stroke: v ? css("--grid") : css("--fg3")}, svg); el("text", {x:X(v), y:H-8, "text-anchor":"middle"}, svg).textContent = (v>0?"+":"") + v; });
  rows.forEach((x, i) => { const y = i*rowH + 4; const g = el("g", {}, svg); el("text", {x:lab-8, y:y+13, "text-anchor":"end", fill:css("--fg")}, g).textContent = x.parent; el("path", {d: x.ci_ch_dens >= 0 ? `M${X(0)} ${y}H${X(x.ci_ch_dens)-3}a3 3 0 0 1 3 3v10a3 3 0 0 1 -3 3H${X(0)}Z` : `M${X(0)} ${y}H${X(x.ci_ch_dens)+3}a3 3 0 0 0 -3 3v10a3 3 0 0 0 3 3H${X(0)}Z`, fill:css("--s1")}, g);
    el("text", {x:X(Math.max(x.ci_ch_dens,0))+6, y:y+13, "font-size":11}, g).textContent = `${sgn(x.ci_ch_dens)} · ${x.with_charger}/${x.n} have a charger · ${fmt(x.per100k,2)}/100k`;
    g.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(x.parent)}</b><br>${x.n} ${UNITS} · ${x.chargers} chargers · ${fmt(x.pop)} residents<br>CI chargers ~ density ${sgn(x.ci_ch_dens)} · Gini ${x.gini}${NAT ? (x.ci_ch_exp != null ? `<br>CI chargers ~ spending ${sgn(x.ci_ch_exp)} · CI ≤10 km ~ spending ${sgn(x.ci_w10_exp)}` : "") : `<br>CI kWh ~ density ${sgn(x.ci_kwh_dens)} · CI chargers ~ EV owners ${sgn(x.ci_ch_ev)}`}`)); g.addEventListener("pointerleave", hideTip); });
  $("within").innerHTML = ""; $("within").appendChild(svg);
  const cols = NAT ? [["parent",PARENT],["n",UNITS],["chargers","Chargers"],["per100k","per 100k"],["with_charger","with charger"],["ci_ch_dens","CI ch~density"],["ci_ch_exp","CI ch~spending"],["ci_w10_exp","CI ≤10 km~spending"],["gini","Gini"]] : [["parent",PARENT],["n",UNITS],["chargers","Chargers"],["per100k","per 100k"],["with_charger","with charger"],["ci_ch_dens","CI ch~density"],["ci_kwh_dens","CI kWh~density"],["ci_ch_ev","CI ch~EV owners"],["gini","Gini"]];
  $("within-table").innerHTML = `<table><thead><tr>${cols.map(c => `<th>${c[1]}</th>`).join("")}</tr></thead><tbody>${rows.map(x => `<tr>${cols.map(c => `<td>${typeof x[c[0]] === "number" ? (c[0].startsWith("ci") ? sgn(x[c[0]]) : fmt(x[c[0]], c[0]==="per100k"?2:(c[0]==="gini"?3:0))) : esc(x[c[0]] ?? "–")}</td>`).join("")}</tr>`).join("")}</tbody></table>`; }

// ---------- Theil & groups
function theil(){ const t = D.D.theil_parent, W = 900, H = 110; const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"}); const bars = [[`Between ${PARENTS}`, t.between_share, "--s2"], [`Within ${PARENTS}`, 1 - t.between_share, "--s1"]]; let x = 20; el("text", {x:20, y:18, "font-weight":600, fill:css("--fg")}, svg).textContent = `Theil T = ${t.T} for chargers per resident across ${UNITS}`;
  bars.forEach(([l, s, c]) => { const w = s*(W-40) - 2; el("rect", {x, y:30, width:w, height:28, rx:4, fill:css(c)}, svg); el("text", {x:x+8, y:49, fill:"#fff", "font-weight":600}, svg).textContent = `${l}: ${pct(100*s,0)}`; x += w + 2; });
  const ti = D.D.theil_island; if (ti) el("text", {x:20, y:84, fill:css("--fg2")}, svg).textContent = `By island group: ${pct(100*ti.between_share,0)} between islands, ${pct(100*(1-ti.between_share),0)} within — province, not island, is where the gap sits.`;
  $("theil").innerHTML = ""; $("theil").appendChild(svg);
  $("groups").innerHTML = D.D.groups.map(g => `<div class="panel"><h3>${g.name}${g.theil ? ` · ${pct(100*g.theil.between_share,0)} of Theil is between these groups` : ""}</h3><div class="scroll" style="max-height:none"><table><thead><tr><th>Group</th><th>${UNITS}</th><th>Residents</th><th>Chargers</th><th>per 100k</th><th>kW per 100k</th><th>% in ${UNITS} with a charger</th><th>${NAT ? "% within 10 km" : "kWh per resident"}</th><th>Share of chargers / share of people</th></tr></thead><tbody>${g.rows.map(r => { const tg = g.theil.groups.find(x => x.group === r.group); return `<tr><td>${esc(r.group)}</td><td>${fmt(r.n)}</td><td>${fmt(r.pop/1e6,2)} M</td><td>${fmt(r.chargers)}</td><td><span class="bar"><i style="width:${Math.min(100, 100*r.per100k/Math.max(...g.rows.map(x=>x.per100k)))}%"></i></span>${fmt(r.per100k,2)}</td><td>${fmt(r.kw_per100k,0)}</td><td>${pct(r.cov)}</td><td>${NAT ? pct(r.within10) : fmt(r.kwh_pc,4)}</td><td>${tg ? fmt(tg.ratio,2)+"×" : "–"}</td></tr>`; }).join("")}</tbody></table></div></div>`).join(""); }

// ---------- robust, deficit, table, method
function rest(){ $("robust").innerHTML = `<table><thead><tr><th>Subset</th><th>${UNITS}</th><th>CI chargers ~ spending</th><th>CI capacity ~ spending</th><th>${NAT ? "CI ≤10 km ~ spending (Erreygers)" : "CI energy sold ~ spending"}</th></tr></thead><tbody>${D.G.robust.map(r => `<tr><td>${esc(r.subset)}</td><td>${fmt(r.n)}</td><td class="${r.ci_ch>0?"pos":"neg"}">${sgn(r.ci_ch)}</td><td class="${r.ci_kw>0?"pos":"neg"}">${sgn(r.ci_kw)}</td><td class="${(NAT?r.ci_w10:r.ci_kwh)>0?"pos":"neg"}">${sgn(NAT ? r.ci_w10 : r.ci_kwh)}</td></tr>`).join("")}</tbody></table>`;
  $("deficit-kpi").innerHTML = [[ICON.plug, fmt(D.G.deficit), `chargers to add · +${pct(100*D.G.deficit/M.chargers,0)} of ${fmt(M.chargers)}`], [ICON.scale, fmt(D.G.mean100k,2), "target: today's average per 100,000 · no charger removed anywhere"], [ICON.pin, fmt(D.G.units_short), `${UNITS} below the average, of ${fmt(M.n_units)}`]].map(t => `<div class="t">${t[0]}<div><div class="v">${t[1]}</div><div class="l">${t[2]}</div></div></div>`).join("");
  $("deficit-list").innerHTML = `<div class="panel" style="margin-top:0"><h3>Largest single needs</h3><ol>${D.G.top.map(x => `<li>${esc(x.name)} <span>· ${esc(x.parent)} · +${x.need} (has ${x.ch}; ${fmt(x.pop/1e3,0)}k people)</span></li>`).join("")}</ol></div>`;
  $("pt-title").textContent = `${PARENTS.charAt(0).toUpperCase()+PARENTS.slice(1)} side by side`; ptk = "per100k"; ptd = -1; ptable();
  $("method").innerHTML = `<ul><li><b>Units.</b> ${fmt(M.n_units)} ${UNITS} in ${fmt(M.n_parents)} ${PARENTS}; ${NAT ? "water bodies are excluded; three districts without a polygon in the BPS file appear in tables but not on the map" : "sub-districts under 500 residents and the Cirata reservoir are excluded"}.</li>
<li><b>Residents.</b> Kontur Population 2023 (H3 hexagons) summed to ${UNIT} polygons: ${fmt(M.pop/1e6,1)} million. ${NAT ? "" : "This exceeds the BPS count (≈50 million); only shares are used."}</li>
<li><b>Socio-economic ranking.</b> ${M.ses}. ${NAT ? "" : "<b>No official sub-district income exists</b>; every sub-district carries its district's value, so income-based indices at sub-district level measure the gradient <i>between districts</i> with a finer population denominator. Density and EV ownership are genuinely sub-district."}</li>
<li><b>Estimators.</b> Population-weighted concentration index (Wagstaff) with tie-averaged fractional ranks; Erreygers correction for bounded outcomes; percentile bootstrap over ${UNITS} (${fmt(M.boot)} resamples); Gini and Lorenz on supply per resident; HHI/CR on shares; Theil T decomposition; Spearman rank correlation. Code: <code>scripts/concentration_explorer.py</code>.</li>
<li><b>Limits.</b> Containment is not reach — a charger across a boundary serves neighbours (the travel-time pilot addresses this). ${NAT ? "Straight-line distance bands (10/25 km) approximate reach; chargers are counted as units regardless of uptime." : "One month of transactions is a snapshot; EV owners are proxied by completed PLN home-charger applications."} Corridor (toll-road) chargers are counted where they sit, inflating some low-population ${UNITS}.</li>
<li><b>Sources.</b> ${M.sources.join(" · ")}.</li></ul>`; }
let ptk = "per100k", ptd = -1;
function ptable(){ const PTC = NAT ? [["parent","Province"],["n","Districts"],["pop","Residents"],["chargers","Chargers"],["kw","kW"],["per100k","per 100k"],["cov","% in districts with charger"],["within10","% within 10 km"],["beyond25","% beyond 25 km"],["exp","Spending (k Rp)"],["ipm","HDI"]] : [["parent","District"],["n","Sub-districts"],["pop","Residents"],["chargers","Chargers"],["kw","kW"],["kwh","kWh Mar-2026"],["per100k","per 100k"],["cov","% in sub-districts with charger"],["exp","Spending (k Rp)"],["ipm","HDI"]];
  const rows = [...D.PT].sort((a,b) => { const va = a[ptk], vb = b[ptk]; return (typeof va === "string" ? va.localeCompare(vb) : va - vb) * ptd; });
  $("pt").innerHTML = `<table><thead><tr>${PTC.map(c => `<th data-k="${c[0]}"${ptk===c[0]?` aria-sort="${ptd<0?"descending":"ascending"}"`:""}>${c[1]}${ptk===c[0]?(ptd<0?" ▾":" ▴"):""}</th>`).join("")}</tr></thead><tbody>${rows.map(r => `<tr>${PTC.map(c => { const v = r[c[0]]; return `<td>${typeof v === "number" ? (c[0]==="pop" ? fmt(v/1e6,2)+" M" : c[0]==="per100k" ? fmt(v,2) : c[0]==="ipm" ? fmt(v,1) : (["cov","within10","beyond25"].includes(c[0]) ? pct(v) : fmt(v))) : esc(v)}</td>`; }).join("")}</tr>`).join("")}</tbody></table>`;
  document.querySelectorAll("#pt th").forEach(th => th.addEventListener("click", () => { const k = th.dataset.k; if (ptk === k) ptd *= -1; else { ptk = k; ptd = k === "parent" ? 1 : -1; } ptable(); })); }

// ---------- chapters (one at a time)
const CH = [["overview","Overview","Big numbers, the four-step story and the 100-residents picture."],["gap","Gap","Every province / district ranked against the national value; who holds more than their share."],["evidence","Evidence","Ten computed findings with what each implies for the thesis."],["map","Map","Where the supply sits, with selectable layers and top / bottom lists."],["unequal","Unequal","Lorenz curves, Gini, HHI — how uneven supply is, regardless of who."],["inequitable","Inequitable","Concentration indices with bootstrap bands — does supply follow advantage?"],["fifths","Fifths","The population in five equal groups: the staircase and the quintile panels."],["scatter","Scatter","Every unit as a bubble: ranking variable vs chargers per resident."],["inside","Inside","The same index recomputed within each province / district."],["sources","Sources","Theil decomposition: between vs within groups, metros, Java, islands."],["robust","Robust","Does the headline survive subsetting?"],["equalise","Equalise","How many chargers it would take to lift every unit to today's average."],["table","Table","Provinces / districts side by side, sortable."],["method","Method","Data, estimators, limits and glossary."]];
let CUR_CH = "overview";
function chapters(){ const nav = $("chapters"); if (!nav.children.length){ nav.innerHTML = CH.map((c,i) => `<button type="button" data-ch="${c[0]}" aria-pressed="false"><span class="k">${String(i).padStart(2,"0")}</span>${c[1]}</button>`).join(""); nav.querySelectorAll("button").forEach(b => b.addEventListener("click", () => showChapter(b.dataset.ch))); $("prev").addEventListener("click", () => step(-1)); $("next").addEventListener("click", () => step(1)); } }
function step(d){ const i = CH.findIndex(c => c[0] === CUR_CH); const j = Math.min(CH.length-1, Math.max(0, i + d)); showChapter(CH[j][0]); window.scrollTo({top: $("chapters").offsetTop - 60, behavior: "smooth"}); }
function showChapter(ch){ CUR_CH = ch; const c = CH.find(x => x[0] === ch); document.querySelectorAll("section.ch").forEach(s => s.classList.toggle("active", s.dataset.ch === ch)); document.querySelectorAll("#chapters button").forEach(b => b.setAttribute("aria-pressed", b.dataset.ch === ch));
  $("chdesc").textContent = c[2]; const i = CH.indexOf(c); $("prev").disabled = i === 0; $("next").disabled = i === CH.length-1; $("pager-pos").textContent = `Chapter ${i} of ${CH.length-1} · ${c[1]}`; history.replaceState(null, "", `#${S}/${ch}`); }

// ---------- render all
function renderAll(scope){ load(scope); hero(); waffles(); stairs(); gap(); evidence(); renderMap(); lorenz(); forest(); curveInit(); quintInit(); scatterInit(); within(); theil(); rest(); chapters(); showChapter(CUR_CH); }
document.querySelectorAll(".seg button").forEach(b => b.addEventListener("click", () => { if (b.dataset.s !== S) renderAll(b.dataset.s); }));
$("layer").addEventListener("change", renderMap); $("gap-metric").addEventListener("change", gap); $("cv-rank").addEventListener("change", drawCurve); $("cv-out").addEventListener("change", drawCurve); $("q-rank").addEventListener("change", drawQuint); $("sc-rank").addEventListener("change", drawScatter);
{ const h = location.hash.slice(1).split("/"); if (h[1] && CH.some(c => c[0] === h[1])) CUR_CH = h[1]; renderAll(h[0] === "jabar" ? "jabar" : "national"); }
</script></body></html>
"""
html = TEMPLATE.replace("__ALL__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))).replace("__GEO__", json.dumps(GEO, ensure_ascii=False, separators=(",", ":")))
open("analysis/charging_equity_en.html", "w", encoding="utf-8").write(html)
print("analysis/charging_equity_en.html %.0f KB" % (len(html.encode()) / 1024))
