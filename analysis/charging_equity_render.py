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
:root{--bg:#fcfcfb;--fg:#0b0b0b;--fg2:#52514e;--fg3:#7d7b75;--line:#e4e2dc;--panel:#f4f3ef;--grid:#ebe9e3;--chip:#e9e7e1;--side:#f4f3ef;
 --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--zero:#d9d7d0;--hatch:#bdbab2;--good:#0ca30c;--crit:#d03b3b;--mid:#f0efec;
 --q1:#cde2fb;--q2:#9ec5f4;--q3:#5598e7;--q4:#256abf;--q5:#104281;--q6:#2a1a5e;--display:"Archivo",system-ui,sans-serif;--body:"Source Sans 3",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1a1a19;--fg:#fff;--fg2:#c3c2b7;--fg3:#8f8d85;--line:#34332f;--panel:#232321;--grid:#2c2b28;--chip:#2e2d2a;--side:#202020;
 --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--zero:#3a3936;--hatch:#5a5853;--mid:#383835;--q1:#184f95;--q2:#256abf;--q3:#3987e5;--q4:#6da7ec;--q5:#b7d3f6;--q6:#eef4ff;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#1a1a19;--fg:#fff;--fg2:#c3c2b7;--fg3:#8f8d85;--line:#34332f;--panel:#232321;--grid:#2c2b28;--chip:#2e2d2a;--side:#202020;
 --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--zero:#3a3936;--hatch:#5a5853;--mid:#383835;--q1:#184f95;--q2:#256abf;--q3:#3987e5;--q4:#6da7ec;--q5:#b7d3f6;--q6:#eef4ff;color-scheme:dark}
*{box-sizing:border-box}
html,body{height:100%}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:14px;line-height:1.4;margin:0;display:grid;grid-template-columns:250px minmax(0,1fr);overflow:hidden}
h1,h2,h3{font-family:var(--display);text-wrap:balance;margin:0}
h1{font-size:clamp(24px,2.6vw,34px);line-height:1.08;font-weight:800;letter-spacing:-.01em}
h2{font-size:20px;font-weight:700;display:flex;gap:10px;align-items:baseline;margin:0 0 4px}
h2 .n{font-size:12px;color:var(--fg3);font-weight:500;letter-spacing:.08em}
h3{font-size:13px;font-weight:600;color:var(--fg2);margin:0 0 6px}
p{margin:4px 0}
a{color:var(--s1)}
/* ---- sidebar */
.side{background:var(--side);border-right:1px solid var(--line);display:flex;flex-direction:column;padding:14px 14px 12px;gap:10px;overflow:hidden;min-height:0}
.brand{font-family:var(--display);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--fg3)}
.seg{display:flex;flex-direction:column;gap:4px}
.seg button{font:inherit;font-size:13px;font-weight:600;padding:6px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg2);cursor:pointer;text-align:left}
.seg button[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.seg button small{display:block;font-weight:400;font-size:11px;opacity:.75}
.chapters{display:flex;flex-direction:column;gap:1px;flex:1;min-height:0;overflow:auto}
.chapters button{font:inherit;font-size:12.5px;padding:5px 9px;border:none;border-radius:8px;background:transparent;color:var(--fg2);cursor:pointer;text-align:left;display:grid;grid-template-columns:22px 1fr;gap:8px;align-items:center}
.chapters button .k{font-family:var(--display);font-size:11px;color:var(--fg3);text-align:right}
.chapters button b{font-weight:600;color:var(--fg)}
.chapters button small{display:block;font-size:10.5px;color:var(--fg3);line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.chapters button:hover{background:var(--chip)}
.chapters button[aria-pressed="true"]{background:var(--fg);color:var(--bg)}.chapters button[aria-pressed="true"] b,.chapters button[aria-pressed="true"] .k,.chapters button[aria-pressed="true"] small{color:var(--bg)}
.pager{display:flex;gap:6px;align-items:center;justify-content:space-between;font-size:12px;color:var(--fg3)}
.pager button{font:inherit;font-size:12px;padding:5px 10px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);cursor:pointer}
.pager button:disabled{opacity:.4;cursor:default}
/* ---- main */
.main{height:100vh;overflow:hidden;display:flex;flex-direction:column;padding:18px 24px 14px;min-width:0}
.eyebrow{font-family:var(--display);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--fg3);font-weight:500}
section.ch{display:none;flex:1;min-height:0;flex-direction:column;gap:10px;animation:fade .18s ease}section.ch[data-ch="overview"]{justify-content:center;gap:14px}section.ch.active{display:flex}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.note{font-size:12.5px;color:var(--fg2);max-width:110ch;margin:0}
.take{font-size:13.5px;color:var(--fg);background:var(--mid);border-left:4px solid var(--s1);border-radius:6px;padding:8px 12px;margin:0}
.take b{font-weight:700}
.fill{flex:1;min-height:0;display:flex;flex-direction:column;gap:10px}
.row{display:grid;gap:12px;min-height:0;flex:1}
.row.c2{grid-template-columns:1fr 1fr}.row.c21{grid-template-columns:1.4fr 1fr}.row.c3{grid-template-columns:repeat(3,1fr)}.row.c5{grid-template-columns:repeat(5,1fr)}
.panel{background:var(--panel);border-radius:10px;padding:12px 14px;min-width:0;min-height:0;display:flex;flex-direction:column;gap:6px}
.panel .chart{flex:1;min-height:0;display:flex;align-items:center;justify-content:center}
.panel .chart svg{width:100%;height:100%;max-height:100%}
svg{display:block;max-width:100%}
svg text{font-family:var(--body);fill:var(--fg2);font-size:12px}
.controls{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;font-size:12.5px;color:var(--fg2)}
.controls label{display:flex;gap:6px;align-items:center}
select{font:inherit;font-size:12.5px;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:3px 7px}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;color:var(--fg2)}
.legend i{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:5px;border-radius:2px}
.legend i.dot{width:10px;height:10px;border-radius:50%}
.tip{position:fixed;pointer-events:none;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px 9px;font-size:12.5px;line-height:1.35;box-shadow:0 2px 10px rgba(0,0,0,.12);max-width:290px;z-index:9;font-variant-numeric:tabular-nums}
.big{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.big .t{background:var(--panel);border-radius:10px;padding:18px 16px;display:flex;gap:10px;align-items:flex-start;min-width:0}
.big .t svg.ic{width:28px;height:28px;flex:none;color:var(--s1)}
.big .t .v{font-family:var(--display);font-size:clamp(26px,2.6vw,38px);font-weight:800;font-variant-numeric:tabular-nums;line-height:1}
.big .t .l{color:var(--fg2);font-size:12.5px;margin-top:6px;line-height:1.35}
.story{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.story .st{position:relative;background:var(--panel);border-radius:10px;padding:16px 14px 14px 52px;font-size:13.5px;color:var(--fg2);line-height:1.4}
.story .st > b.h{display:block;color:var(--fg);font-size:15px;margin-bottom:3px}.story .st b{color:var(--fg)}
.story .st .k{position:absolute;left:12px;top:12px;width:26px;height:26px;border-radius:50%;background:var(--fg);color:var(--bg);display:grid;place-items:center;font-family:var(--display);font-weight:800;font-size:13px}
.lede{color:var(--fg2);font-size:15px;max-width:95ch;margin:4px 0 0}
/* waffles */
.waffles{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;flex:1;min-height:0}
.waffle{display:flex;flex-direction:column;gap:6px;min-height:0}
.waffle .grid{display:grid;grid-template-columns:repeat(10,1fr);gap:3px;flex:1;min-height:0;aspect-ratio:1;max-height:100%;margin:0 auto;width:100%;max-width:min(100%,52vh)}
.waffle .p{border-radius:3px;background:var(--grid)}
.waffle .sum{display:flex;gap:10px;flex-wrap:wrap;font-size:12px;color:var(--fg2)}.waffle .sum b{color:var(--fg)}
.waffle .sum i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:4px}
/* stairs */
.stairs{display:flex;gap:8px;align-items:flex-end;flex:none;margin:auto 0}
.stairs .col{flex:1;min-width:0;text-align:center;font-size:12px;color:var(--fg2);display:flex;flex-direction:column;justify-content:flex-end}
.stairs .icons{display:flex;flex-wrap:wrap;gap:3px;justify-content:center;align-content:flex-end;max-width:150px;margin:0 auto}
.stairs .icons svg{width:26px;height:26px;color:var(--s1)}.stairs .icons svg.half{opacity:.45}
.stairs .v{font-family:var(--display);font-weight:800;font-size:17px;color:var(--fg);margin-top:4px}
/* evidence */
.ev{display:grid;grid-template-columns:repeat(2,1fr);grid-auto-rows:1fr;gap:10px;min-height:0}.evwrap{display:grid;grid-template-columns:1.6fr 1fr;gap:12px;flex:1;min-height:0}.evside{display:flex;flex-direction:column;gap:12px;min-height:0}.evside .panel{flex:none}.evside table{font-size:12px}.evside th,.evside td{padding:3px 6px}
.ev .card{background:var(--panel);border-radius:10px;padding:10px 12px;border-left:5px solid var(--s1);display:flex;flex-direction:column;gap:4px;min-height:0;overflow:hidden}
.ev .card .hd{display:flex;flex-direction:column;gap:2px;min-width:0}.ev .card .viz{width:100%;height:38px}.ev .card .viz svg{width:100%;height:100%;display:block}
.ev .card .bigv{font-family:var(--display);font-size:21px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1.1}
.ev .card .bigv small{font-size:11.5px;font-weight:500;color:var(--fg2)}
.ev .card .t{font-weight:600;font-size:13px;line-height:1.25}.ev .card .d{font-size:11.5px;color:var(--fg2);line-height:1.3}
.ev .card .so{font-size:11px;line-height:1.3;color:var(--fg);background:var(--mid);border-radius:6px;padding:4px 7px;margin-top:auto}
.rob svg{width:100%;display:block}.def-bar{display:flex;height:22px;border-radius:6px;overflow:hidden;margin:6px 0 4px}.def-bar div{display:flex;align-items:center;justify-content:center;color:#fff;font-size:11px;font-weight:700;white-space:nowrap}.def-need{display:grid;grid-template-columns:auto 1fr auto;gap:4px 8px;font-size:11.5px;align-items:center}.def-need i{display:block;height:9px;border-radius:4px;background:var(--s2)}
.ev .card.crit{border-left-color:var(--crit)}.ev .card.good{border-left-color:var(--good)}.ev .card.warn{border-left-color:var(--s4)}
/* lists & tables */
.lists ol{margin:0;padding-left:18px;font-size:12.5px;font-variant-numeric:tabular-nums}.lists li{margin:1px 0}.lists li span{color:var(--fg3)}
table{border-collapse:collapse;width:100%;font-size:12.5px;font-variant-numeric:tabular-nums}
th,td{padding:4px 7px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
th{font-weight:600;color:var(--fg2);font-size:11.5px}
.pos{color:var(--crit);font-weight:600}.neg{color:var(--s3);font-weight:600}
.bar{display:inline-block;height:7px;border-radius:4px;background:var(--grid);width:60px;vertical-align:middle;margin-right:5px;overflow:hidden}.bar i{display:block;height:100%;background:var(--s1)}
.mapleg{display:flex;gap:2px;align-items:flex-end;font-size:11px;color:var(--fg2);flex-wrap:wrap}
.tt-tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}.tt-tiles .t{background:var(--mid);border-radius:8px;padding:6px 9px;min-width:0}.tt-tiles .v{font-family:var(--display);font-size:19px;font-weight:800;line-height:1.05;font-variant-numeric:tabular-nums}.tt-tiles .l{font-size:10.5px;color:var(--fg2);margin-top:2px;line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tt-bar{display:flex;height:22px;border-radius:7px;overflow:hidden;margin:8px 0 4px}.tt-bar div{display:flex;align-items:center;justify-content:center;color:#fff;font-size:11px;font-weight:700;white-space:nowrap;overflow:hidden}
.tt-leg{display:flex;gap:12px;flex-wrap:wrap;font-size:11.5px;color:var(--fg2);margin-bottom:6px}.tt-leg i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:-1px}
#tt-table table{font-size:11.5px}#tt-table th,#tt-table td{padding:3px 5px}#tt-table td:first-child{text-align:left}
#cm-map{position:relative;cursor:grab;touch-action:none}#cm-map:active{cursor:grabbing}#cm-map svg{user-select:none}#cm-map path{transition:fill .5s ease,opacity .35s ease}#cm-map path.dim{opacity:.22}#cm-map path.sel{stroke:var(--fg);stroke-width:1.4;animation:cmPulse 1.4s ease-in-out infinite}
@keyframes cmPulse{0%,100%{stroke-opacity:1}50%{stroke-opacity:.25}}
.cm-tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}.cm-tiles .t{background:var(--mid);border-radius:8px;padding:6px 9px;min-width:0}.cm-tiles .v{font-family:var(--display);font-size:18px;font-weight:800;line-height:1.05;font-variant-numeric:tabular-nums}.cm-tiles .l{font-size:10.5px;color:var(--fg2);margin-top:2px;line-height:1.2}
.cm-cmp{font-size:11px;color:var(--fg2)}.cm-cmp .r{display:grid;grid-template-columns:118px 1fr 56px;gap:6px;align-items:center;margin:2px 0}.cm-cmp .bar{height:9px;border-radius:4px;background:var(--mid);position:relative}.cm-cmp .bar i{position:absolute;left:0;top:0;height:100%;border-radius:4px;background:var(--s1);width:0;transition:width .7s cubic-bezier(.2,.7,.2,1)}.cm-cmp .bar em{position:absolute;top:-2px;width:2px;height:13px;background:var(--s2)}.cm-cmp .bar b{position:absolute;top:-2px;width:2px;height:13px;background:var(--fg)}
.cm-gauge{position:relative;height:24px;margin:3px 0 2px;border-radius:6px;background:linear-gradient(90deg,var(--crit) 0%,var(--zero) 50%,var(--good) 100%);opacity:.95}.cm-gauge i{position:absolute;top:-4px;width:4px;height:32px;border-radius:2px;background:var(--fg);transition:left .7s cubic-bezier(.2,.7,.2,1)}.cm-gauge span{position:absolute;top:5px;font-size:10px;color:#fff;font-weight:700}
.cm-read{font-size:10.8px;line-height:1.33;color:var(--fg)}.cm-read p{margin:0 0 3px}
.cm-sc{width:100%;height:112px}.tt-card .cm-sc{height:78px}.cm-sc svg{width:100%;height:100%;display:block}.cm-sc circle{transition:r .25s ease,opacity .3s ease;cursor:pointer}
.cm-list{display:grid;grid-template-columns:1fr 1fr;gap:4px 12px;font-size:11px}.cm-list div{display:flex;justify-content:space-between;gap:6px;border-bottom:1px dotted var(--line);padding:1px 0;cursor:pointer}.cm-list div:hover{color:var(--s1)}.cm-list h4{grid-column:1/-1;margin:4px 0 0;font-size:11px;color:var(--fg3);font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.cm-find{font:inherit;font-size:12px;padding:5px 8px;border:1px solid var(--line);border-radius:7px;background:var(--bg);color:var(--fg);width:150px}
#tt-map{position:relative;cursor:grab;touch-action:none}#tt-map:active{cursor:grabbing}#tt-map svg{user-select:none}#tt-map path.dim{opacity:.18}#tt-map path.sel{stroke:var(--fg);stroke-width:.9}
.tt-zoom{position:absolute;top:8px;right:8px;display:flex;flex-direction:column;gap:3px;z-index:2}.tt-zoom button{width:26px;height:26px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);font:inherit;font-size:15px;line-height:1;cursor:pointer}.tt-zoom button:hover{background:var(--chip)}
.tt-hint{position:absolute;left:8px;top:8px;font-size:10.5px;color:var(--fg3);background:var(--bg);border-radius:5px;padding:2px 6px;opacity:.9;z-index:2}
.tt-ins{margin:0;padding-left:16px;font-size:11px;color:var(--fg2);line-height:1.33}.tt-ins li{margin:3px 0}#cm-side .tt-ins li{margin:2px 0}.tt-ins b{color:var(--fg)}
.tt-seg{display:flex;gap:4px;margin:6px 0}.tt-seg button{font:inherit;font-size:11.5px;font-weight:600;padding:4px 10px;border:1px solid var(--line);border-radius:999px;background:var(--bg);color:var(--fg2);cursor:pointer}.tt-seg button[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.tt-card h3{margin:0 0 2px;font-size:14px}.tt-card .sub{font-size:11px;color:var(--fg3);margin-bottom:6px}.tt-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:8px}.tt-stats div{background:var(--mid);border-radius:6px;padding:4px 7px}.tt-stats .v{font-family:var(--display);font-weight:800;font-size:16px;line-height:1.05}.tt-stats .l{font-size:10.5px;color:var(--fg2);margin-top:2px}
.tt-cmp{font-size:11px;color:var(--fg2);margin:4px 0 8px}.tt-cmp .r{display:grid;grid-template-columns:52px 1fr 44px;gap:6px;align-items:center;margin:1px 0}.tt-cmp .bar{height:8px;border-radius:4px;background:var(--mid);position:relative;overflow:visible}.tt-cmp .bar i{position:absolute;left:0;top:0;height:100%;border-radius:4px;background:var(--s1)}.tt-cmp .bar em{position:absolute;top:-2px;width:2px;height:12px;background:var(--fg);opacity:.7}
.tt-read{font-size:11.3px;line-height:1.35;color:var(--fg)}.tt-read p{margin:0 0 4px}.tt-read b{font-weight:700}
.mapleg .sw{display:flex;flex-direction:column;gap:2px}.mapleg .sw i{display:block;width:48px;height:9px}
ul.m{margin:0;padding-left:18px;font-size:12.5px;color:var(--fg2)}ul.m li{margin:3px 0}ul.m b{color:var(--fg)}
@media (max-width:980px){body{grid-template-columns:1fr;overflow:auto}.side{flex-direction:row;flex-wrap:wrap}.main{height:auto;overflow:visible}.row.c2,.row.c21,.row.c3,.row.c5,.big,.story,.ev,.evwrap,.waffles{grid-template-columns:1fr}.chapters{flex-direction:row;flex-wrap:wrap}}
@media (prefers-reduced-motion:no-preference){path.u{transition:fill .15s}}
</style></head><body data-scope="national">
<aside class="side">
 <div class="brand">Charging equity story</div>
 <div class="seg" role="group" aria-label="Scope"><button type="button" data-s="national" aria-pressed="true">🇮🇩 Indonesia<small>508 districts · June 2026</small></button><button type="button" data-s="jabar" aria-pressed="false">West Java<small>629 sub-districts · March 2026</small></button></div>
 <nav class="chapters" id="chapters" aria-label="Chapters"></nav>
 <div class="pager"><button type="button" id="prev">← Prev</button><span id="pager-pos"></span><button type="button" id="next">Next →</button></div>
</aside>
<main class="main">
<div class="eyebrow" id="eyebrow"></div>

<section class="ch" data-ch="overview">
 <h1 id="h1"></h1><p class="lede" id="lede"></p>
 <div class="big" id="big"></div>
 <div class="story" id="story"></div>
 <p class="take" id="ov-take"></p>
</section>

<section class="ch" data-ch="people">
 <h2><span class="n">01</span>If there were 100 residents…</h2><p class="note" id="w-note"></p>
 <div class="panel fill"><div class="waffles" id="waffles"></div></div>
 <p class="take" id="w-take"></p>
</section>

<section class="ch" data-ch="gap">
 <h2><span class="n">02</span><span id="gap-title"></span></h2>
 <div class="controls"><label>Measure <select id="gap-metric"></select></label><span class="note" id="gap-sum"></span></div>
 <div class="row c21"><div class="panel"><div class="chart" id="lolli"></div><div class="legend" id="lolli-leg"></div></div>
  <div class="panel"><h3 id="slope-title"></h3><div class="chart" id="slope"></div><p class="note">Left: share of residents · right: share of chargers (√ scale). Red climbs = more than its share; blue falls = less.</p></div></div>
 <p class="take" id="gap-take"></p>
</section>

<section class="ch" data-ch="map">
 <h2><span class="n">03</span>Where the supply is</h2>
 <div class="controls"><label>Layer <select id="layer"></select></label><span class="note" id="map-note"></span></div>
 <div class="row c21"><div class="panel"><div class="chart" id="map"></div><div class="mapleg" id="mapleg"></div></div><div class="panel lists" id="lists" style="overflow:auto"></div></div>
</section>

<section class="ch" data-ch="travel">
 <h2><span class="n">04</span>Who can reach a charger in 10 minutes, and is there enough power when they do?</h2>
 <p class="note" id="tt-note"></p>
 <div class="controls"><label>Layer <select id="tt-layer"><option value="min">Minutes by car to the nearest village with a charger</option><option value="rung">Service ladder rung (0 / 1 / 2)</option><option value="unreached">Residents beyond 10 minutes (people, not area)</option><option value="dens">Residents per km²</option></select></label><label>Region <select id="tt-region"></select></label><label>Sites <select id="tt-sites"><option value="none">hidden</option><option value="all">all 1,556 sites</option><option value="PLN">PLN only</option><option value="nonPLN">partner only</option><option value="fast">≥ 50 kW (fast)</option><option value="available">status: available</option><option value="offline">status: offline mode</option></select></label><span class="note" id="tt-meta"></span></div>
 <div class="row c21"><div class="panel" style="position:relative"><div class="chart" id="tt-map"></div><div class="mapleg" id="tt-leg"></div></div>
  <div class="panel" style="overflow:auto;gap:8px"><div class="tt-tiles" id="tt-big"></div><div id="tt-side"></div></div></div>
 <p class="take" id="tt-take"></p>
</section>

<section class="ch" data-ch="cities">
 <h2><span class="n">05</span>Which cities are served, and which are left behind?</h2>
 <p class="note" id="cm-note"></p>
 <div class="controls"><label>Layer <select id="cm-layer"></select></label><label>Find <input id="cm-find" class="cm-find" list="cm-dl" placeholder="type a city…"><datalist id="cm-dl"></datalist></label><label>Province <select id="cm-prov"></select></label><span class="note" id="cm-meta"></span></div>
 <div class="row c21"><div class="panel" style="position:relative"><div class="chart" id="cm-map"></div><div class="mapleg" id="cm-leg"></div></div>
  <div class="panel" style="overflow:auto;gap:7px" id="cm-side"></div></div>
 <p class="take" id="cm-take"></p>
</section>

<section class="ch" data-ch="fifths">
 <h2><span class="n">04</span>Fifths of the population</h2><p class="note" id="q-note"></p>
 <div class="row c21"><div class="panel"><h3 id="stairs-title"></h3><div class="stairs" id="stairs"></div></div>
  <div class="panel"><div class="controls"><label>Rank by <select id="q-rank"></select></label></div><div class="row c2" id="quint" style="flex:1"></div></div></div>
 <p class="take" id="q-take"></p>
</section>

<section class="ch" data-ch="inequitable">
 <h2><span class="n">05</span>Does supply follow advantage?</h2><p class="note" id="forest-note"></p>
 <div class="controls"><label>Within <select id="f-within"></select></label><span class="note" id="f-within-note"></span></div>
 <div class="row c21"><div class="panel"><div class="chart" id="forest"></div><div class="legend" id="forest-leg"></div></div>
  <div class="panel"><div class="controls"><label>Rank by <select id="cv-rank"></select></label><label>Supply <select id="cv-out"></select></label></div><div class="chart" id="curve"></div><p class="note" id="curve-note"></p></div></div>
 <p class="take" id="f-take"></p>
</section>

<section class="ch" data-ch="sources">
 <h2><span class="n">06</span>Where the inequality comes from</h2><p class="note">Theil's T of chargers per resident splits exactly into inequality <i>between</i> groups and <i>within</i> them — the share tells you which level of government holds the lever.</p>
 <div class="panel" style="flex:none"><div id="theil"></div></div>
 <div class="row c2" id="groups"></div>
 <p class="take" id="s-take"></p>
</section>

<section class="ch" data-ch="evidence">
 <h2><span class="n">07</span>Evidence and what it would take</h2><p class="note">Six computed findings with their implication for the thesis (red = equity concern, amber = mixed, green = reassuring), and the robustness check.</p>
 <div class="evwrap"><div class="ev" id="evidence"></div>
 <div class="evside"><div class="panel"><h3>Does the verdict survive subsetting?</h3><div id="robust"></div></div><div class="panel"><h3>What it would take to equalise</h3><div id="deficit"></div></div></div></div>
</section>

<section class="ch" data-ch="method">
 <h2><span class="n">08</span>Data, method and limits</h2>
 <div class="row c2"><div class="panel" id="method"></div><div class="panel"><h3>Glossary</h3><ul class="m">
  <li><b>Concentration index (CI)</b> — 2·cov<sub>w</sub>(supply per resident, population-weighted rank)/mean. +1 = all supply at the top of the ranking, 0 = proportional, −1 = all at the bottom.</li>
  <li><b>Erreygers CI</b> — the same for a yes/no or 0–100 % outcome: 8·cov<sub>w</sub>(y, rank)/(max−min).</li>
  <li><b>95 % band</b> — percentile bootstrap over units, 1,000 resamples; "significant" = band excludes zero.</li>
  <li><b>Gini</b> — inequality of chargers per resident across units, weighted by residents; blind to who is rich or poor.</li>
  <li><b>Theil T</b> — entropy inequality measure that splits exactly into between- and within-group parts.</li>
  <li><b>20:20</b> — chargers held by the best-served 20 % of residents over the worst-served 20 %.</li></ul>
  <p class="note" style="margin-top:8px">Full evidence pages: <a href="concentration_national_en.html">national</a> · <a href="concentration_jabar_en.html">West Java</a> · <a href="concentration_dashboard_en.html">interactive explorer with scenarios</a> · <a href="../index.html#tab=ttm">travel-time pilot</a>. Code: <code>scripts/concentration_explorer.py</code>.</p></div></div>
</section>
</main>
<div class="tip" id="tip" hidden></div>
<script>
const ALL = __ALL__; const GEOS = __GEO__; const TT = __TT__;
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
function load(scope){ S = scope; D = ALL[scope]; GEO = GEOS[scope]; M = D.meta; NAT = scope === "national"; bbox = null; FW = "all"; FD = null;
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
  $("ov-take").innerHTML = NAT ? `<b>Read it in order:</b> the network is unequal (a few places hold most of it) <i>and</i> inequitable (it follows income, development and density), the gap sits mostly <i>between provinces</i>, and it survives every change of frame. Use the chapters on the left, or ← → keys.` : `<b>Read it in order:</b> West Java places chargers almost regardless of income, but capacity and especially <i>use</i> follow income — and the gap lives <i>inside</i> districts. Use the chapters on the left, or ← → keys.`;
  const tp = D.D.theil_parent;
  $("story").innerHTML = [["Unequal", `Top 20 % of residents by supply hold <b>${pct(100*D.D.top20_share,0)}</b> of chargers; Gini ${D.A.gini_pc.ch.toFixed(2)}.`], ["Inequitable", `${exCh.signif ? "Chargers follow income: CI " + sgn(exCh.ci) + ", band excludes zero." : "Placement is income-neutral (CI " + sgn(exCh.ci) + "), but capacity (" + sgn(B("exp","kw").ci) + ") and use (" + sgn(B("exp","kwh").ci) + ") are not."}`],
    ["Where", `${pct(100*tp.between_share,0)} of the inequality is <b>between ${PARENTS}</b>; ${pct(100*(1-tp.between_share),0)} inside them.`], ["What it takes", `<b>${fmt(D.G.deficit)}</b> more chargers (+${pct(100*D.G.deficit/M.chargers,0)}) to lift every ${UNIT} to today's average.`]]
    .map((s, i) => `<div class="st"><span class="k">${i+1}</span><b class="h">${s[0]}</b>${s[1]}</div>`).join("");
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
    box.appendChild(d); });
  $("w-take").innerHTML = NAT ? `<b>${Math.round(q[0].beyond25)} of 100 poorest residents live more than 25 km from any charger; ${Math.round(q[4].beyond25)} of 100 richest do.</b> Reach is not a few points apart — it is a different country.` : `<b>${Math.round(100-q[0].pop_no_charger_pct)} of 100 poorest residents have a charger in their sub-district; ${Math.round(100-q[4].pop_no_charger_pct)} of 100 richest do.</b> Flatter than the national picture — placement here is only mildly income-tilted.`; }

// ---------- quintile staircase
function stairs(){ const q = D.Q.exp, box = $("stairs"); box.innerHTML = ""; const unit = NAT ? 0.25 : 0.1; $("stairs-title").textContent = `Chargers per 100,000 residents by spending fifth · one icon ≈ ${unit}`;
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
  const rows = [...PT].sort((a,b) => b[key] - a[key]); const avg = rows.reduce((s,r) => s + r[key]*r.pop, 0) / rows.reduce((s,r) => s + r.pop, 0);
  const rowH = NAT ? 17 : 19, lab = 150, W = 760, H = rows.length*rowH + 34, vmax = Math.max(...rows.map(r => r[key])) * 1.08, X = v => lab + v/vmax*(W-lab-70), pmax = Math.max(...rows.map(r => r.pop));
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":"Ranking"});
  const ticks = 5; for (let i = 0; i <= ticks; i++){ const v = vmax*i/ticks; el("line", {x1:X(v), x2:X(v), y1:0, y2:H-24, stroke:css("--grid")}, svg); el("text", {x:X(v), y:H-8, "text-anchor":"middle"}, svg).textContent = MT[2](v); }
  el("line", {x1:X(avg), x2:X(avg), y1:0, y2:H-24, stroke:css("--fg3"), "stroke-dasharray":"4 3"}, svg); el("text", {x:X(avg)+4, y:12, "font-size":11, fill:css("--fg")}, svg).textContent = `${NAT ? "Indonesia" : "West Java"} ${MT[2](avg)}`;
  rows.forEach((r, i) => { const y = i*rowH + 22, col = NAT ? (r.java ? "--s1" : "--s2") : (r.parent.startsWith("Kota") ? "--s2" : "--s1");
    el("text", {x:lab-8, y:y+4, "text-anchor":"end", fill:css("--fg"), "font-size":11}, svg).textContent = r.parent;
    el("line", {x1:lab, x2:X(r[key]), y1:y, y2:y, stroke:css(col), "stroke-width":2, "stroke-opacity":.5}, svg);
    const c = el("circle", {cx:X(r[key]), cy:y, r: 3 + 7*Math.sqrt(r.pop/pmax), fill:css(col), stroke:css("--bg"), "stroke-width":1.2}, svg);
    el("text", {x:X(r[key]) + 6 + 7*Math.sqrt(r.pop/pmax), y:y+4, "font-size":11}, svg).textContent = MT[2](r[key]);
    c.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(r.parent)}</b><br>${fmt(r.pop/1e6,2)} M residents · ${fmt(r.chargers)} chargers · ${fmt(r.per100k,2)} per 100k${NAT ? `<br>${pct(r.within10)} within 10 km · ${pct(r.beyond25)} beyond 25 km` : `<br>${fmt(r.kwh)} kWh sold`}<br>spending ${fmt(r.exp)}k · HDI ${fmt(r.ipm,1)} · ${pct(r.cov)} in ${UNITS} with a charger`)); c.addEventListener("pointerleave", hideTip); });
  $("lolli").innerHTML = ""; $("lolli").appendChild(svg);
  $("lolli-leg").innerHTML = NAT ? `<span><i class="dot" style="background:var(--s1)"></i>Java</span><span><i class="dot" style="background:var(--s2)"></i>Outside Java</span><span><i style="background:var(--fg3);height:1px"></i>national value</span>` : `<span><i class="dot" style="background:var(--s1)"></i>Regency</span><span><i class="dot" style="background:var(--s2)"></i>City</span><span><i style="background:var(--fg3);height:1px"></i>West Java value</span>`;
  const top = rows[0], bot = rows[rows.length-1], below = rows.filter(r => r[key] < avg).length; $("gap-sum").innerHTML = `Top <b>${esc(top.parent)}</b> ${MT[2](top[key])} · bottom <b>${esc(bot.parent)}</b> ${MT[2](bot[key])}${key === "per100k" ? ` · <b>${fmt(top[key]/Math.max(bot[key],1e-6),0)}×</b>` : ""} · ${below} of ${rows.length} below the ${NAT ? "national" : "West Java"} value`;
  const dki = D.D.theil_parent.groups.find(g => g.group === (NAT ? "DKI Jakarta" : "Kota Bandung"));
  $("gap-take").innerHTML = NAT ? `<b>${below} of 34 provinces sit below the national average</b> — the average is pulled up by Jakarta, which holds ${pct(100*dki.supply_share,0)} of chargers for ${pct(100*dki.pop_share,1)} of people (${fmt(dki.ratio,1)}×). Java's big provinces (Jawa Timur, Jawa Tengah) hold <i>less</i> than their share.` : `<b>${below} of 27 districts sit below the West Java value.</b> Cities are covered (Cimahi, Depok, Kota Bandung); the southern regencies — Ciamis, Pangandaran, Tasikmalaya — are where the supply thins out.`;
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
  if (!$("reach")) return;
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
  else { const bw = B("exp","within10"); cards.push({c: cls(bw), big: sgn(bw.ci), small: "Erreygers CI, reach ≤ 10 km", t: "Reach, not just counts, follows income", d: `Within 10 km of a charger: ${pct(qe[4].within10,0)} of the richest fifth vs ${pct(qe[0].within10,0)} of the poorest; ${pct(qe[0].beyond25,0)} of the poorest fifth are beyond 25 km.`, so: `<b>Step 1 of the service ladder (reachable) already fails</b> for a large poor minority.`}); }
  cards.push({c: "warn", big: pct(100*D.D.top20_share,0), small: "of chargers go to the best-served fifth", t: `Unequal by any standard: ${D.D.ratio2020 == null ? "the bottom fifth has none" : "20:20 ratio "+fmt(D.D.ratio2020,1)+"×"}`, d: `Ranked by chargers per resident, the best-served fifth holds ${pct(100*D.D.top20_share,0)} and the worst-served half ${pct(100*D.D.bottom50_share,0)}; Gini ${D.A.gini_pc.ch.toFixed(2)}, HHI ${fmt(D.A.supply.ch.hhi)} (≈ ${fmt(D.A.supply.ch.n_eff)} equal-sized ${UNITS}).`, so: `<b>Unequal and inequitable are different questions</b> — this card is the first, the CI cards are the second.`});
  cards.push({c: "crit", big: `${fmt(cov.pop_without/1e6,1)} M`, small: `in ${NAT ? "districts" : "sub-districts"} with no charger`, t: `${fmt(cov.units_without)} ${UNITS} have zero chargers`, d: `Largest: ${D.A.largest_without.slice(0,3).map(x => `${x.name} (${fmt(x.pop/1e3,0)}k)`).join(", ")}${NAT ? "." : " — dense commuter sub-districts: gaps are not only a poverty story."}`, so: `<b>Containment ≠ reach</b>: a charger across the boundary may serve them — the travel-time analysis tests this.`});
  const tp = D.D.theil_parent; cards.push({c: tp.between_share > 0.5 ? "crit" : "warn", big: pct(100*tp.between_share,0), small: `of inequality is between ${NAT ? "provinces" : "districts"}`, t: tp.between_share > 0.5 ? `The gap is mostly ${PARENT} vs ${PARENT}` : `The gap lives inside every ${PARENT}`, d: tp.between_share > 0.5 ? `Theil T ${tp.T}: ${pct(100*tp.between_share,0)} between, ${pct(100*(1-tp.between_share),0)} within. ${NAT ? "DKI Jakarta holds "+pct(100*tp.groups.find(g=>g.group==="DKI Jakarta").supply_share,0)+" of chargers for "+pct(100*tp.groups.find(g=>g.group==="DKI Jakarta").pop_share,1)+" of people." : ""}` : `Theil T ${tp.T}: only ${pct(100*tp.between_share,0)} is between ${PARENTS}; ${pct(100*(1-tp.between_share),0)} is between ${UNITS} of the same ${PARENT}.`, so: tp.between_share > 0.5 ? `<b>${PARENT.charAt(0).toUpperCase()+PARENT.slice(1)}-level allocation is the lever.</b>` : `<b>Allocation inside each ${PARENT} is the lever</b>, not transfers between them.`});
  const cr = grp("City vs regency").rows, city = cr.find(r => r.group.startsWith("City")), reg = cr.find(r => r.group.startsWith("Regency"));
  cards.push({c: "warn", big: `${fmt(city.per100k/Math.max(reg.per100k,1e-6),1)}×`, small: "city vs regency, chargers per resident", t: "Cities are served, regencies are not", d: `Cities: ${fmt(city.per100k,2)} per 100,000, ${pct(city.cov)} covered${NAT ? ", "+pct(city.within10)+" within 10 km" : ""}. Regencies: ${fmt(reg.per100k,2)}, ${pct(reg.cov)}${NAT ? ", "+pct(reg.within10)+" within 10 km" : ""}; they hold ${pct(100*reg.pop/(city.pop+reg.pop),0)} of the population.`, so: `<b>Urban form explains part of the income gradient</b> — density and income are entangled; see robustness.`});
  const dch = B("dens","ch"); cards.push({c: cls(dch), big: sgn(dch.ci), small: "CI chargers ~ density", t: "Density gradient", d: `Ranked by density alone the index is ${sgn(dch.ci)}; by spending ${sgn(exCh.ci)}; by HDI ${sgn(B("ipm","ch").ci)}; by poverty ${sgn(B("npov","ch").ci)}.`, so: `<b>${Math.abs(dch.ci) > Math.abs(exCh.ci) ? "Density explains more of the pattern than income" : "Income explains at least as much as density"}</b> — the proposal ranks by HDI, not income, for this reason.`});
  const COL = {crit:"--crit", good:"--good", warn:"--s4"};
  const vizCI = (b, c) => { const lo = Math.min(-0.25, b.lo - 0.08), hi = Math.max(0.6, b.hi + 0.08), X = v => 14 + (v-lo)/(hi-lo)*272, col = css(COL[c]);
    return `<svg viewBox="0 0 300 40"><rect x="${X(0)}" y="8" width="${X(hi)-X(0)}" height="14" fill="${col}" opacity=".10"/><line x1="${X(lo)}" x2="${X(hi)}" y1="15" y2="15" stroke="${css("--grid")}"/><line x1="${X(0)}" x2="${X(0)}" y1="4" y2="26" stroke="${css("--fg3")}"/><line x1="${X(b.lo)}" x2="${X(b.hi)}" y1="15" y2="15" stroke="${col}" stroke-width="3"/><circle cx="${X(b.ci)}" cy="15" r="5" fill="${b.signif ? col : css("--bg")}" stroke="${col}" stroke-width="2"/><text x="${X(lo)}" y="37" font-size="9" fill="${css("--fg3")}">pro-poor</text><text x="${X(0)}" y="37" font-size="9" text-anchor="middle" fill="${css("--fg3")}">0</text><text x="${X(hi)}" y="37" font-size="9" text-anchor="end" fill="${css("--fg3")}">pro-rich →</text>${X(b.hi) > 235 ? `<text x="${X(b.lo)-4}" y="19" font-size="9.5" text-anchor="end" fill="${css("--fg2")}">95 % band</text>` : `<text x="${X(b.hi)+4}" y="19" font-size="9.5" fill="${css("--fg2")}">95 % band</text>`}</svg>`; };
  const vizLorenz = (pts, mark, c, gini) => { const X = p => 4 + p*34, Y = p => 37 - p*34, col = css(COL[c]), d = pts.map((p,i) => (i ? "L" : "M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1)).join(""), m = pts.reduce((a, p) => Math.abs(p[0]-mark) < Math.abs(a[0]-mark) ? p : a, pts[0]);
    return `<svg viewBox="0 0 300 40"><path d="${d}L${X(1)} ${Y(0)}Z" fill="${col}" opacity=".15"/><line x1="${X(0)}" y1="${Y(0)}" x2="${X(1)}" y2="${Y(1)}" stroke="${css("--fg3")}" stroke-dasharray="2 2"/><path d="${d}" fill="none" stroke="${col}" stroke-width="1.6"/><circle cx="${X(mark)}" cy="${Y(m[1])}" r="2.4" fill="${col}"/><text x="48" y="15" font-size="10.5" fill="${css("--fg")}">best-served <tspan font-weight="700">${fmt(100*(1-mark),0)} %</tspan> hold <tspan font-weight="700">${fmt(100*(1-m[1]),0)} %</tspan> of chargers</text><text x="48" y="31" font-size="10" fill="${css("--fg2")}">Lorenz curve · dashed = equality · Gini ${gini.toFixed(2)}</text></svg>`; };
  const vizWaffle = (share, c) => { const n = Math.round(100*share), col = css(COL[c]); let r = ""; for (let i = 0; i < 100; i++){ const x = 2 + (i % 20)*5, y = 3 + Math.floor(i/20)*7; r += `<rect x="${x}" y="${y}" width="4.3" height="6" rx=".9" fill="${i < n ? col : css("--zero")}"/>`; } return `<svg viewBox="0 0 300 40">${r}<text x="108" y="15" font-size="10.5" fill="${css("--fg")}">100 squares = all residents</text><text x="108" y="31" font-size="10" fill="${css("--fg2")}"><tspan font-weight="700" fill="${col}">${n}</tspan> live where there is no charger</text></svg>`; };
  const vizSplit = (between, c) => { const col = css(COL[c]), a = 300*between; return `<svg viewBox="0 0 300 40"><rect x="0" y="8" width="${a}" height="20" rx="4" fill="${col}"/><rect x="${a+2}" y="8" width="${298-a}" height="20" rx="4" fill="${css("--s1")}" opacity=".85"/><text x="${a/2}" y="22" font-size="10" font-weight="700" text-anchor="middle" fill="#fff">${between > 0.12 ? pct(100*between,0) : ""}</text><text x="${a + (300-a)/2}" y="22" font-size="10" font-weight="700" text-anchor="middle" fill="#fff">${pct(100*(1-between),0)} within</text><text x="0" y="38" font-size="9" fill="${css("--fg3")}">between ${NAT ? "provinces" : "districts"}</text><text x="300" y="38" font-size="9" text-anchor="end" fill="${css("--fg3")}">within ${NAT ? "provinces" : "districts"}</text></svg>`; };
  const vizRatio = (a, b, la, lb, c) => { const mx = Math.max(a, b) * 1.1, W = 220, col = css(COL[c]); return `<svg viewBox="0 0 300 40"><text x="0" y="13" font-size="9.5" fill="${css("--fg2")}">${la}</text><rect x="70" y="4" width="${W*a/mx}" height="12" rx="3" fill="${col}"/><text x="${74+W*a/mx}" y="13" font-size="9.5" fill="${css("--fg")}">${fmt(a,2)}</text><text x="0" y="33" font-size="9.5" fill="${css("--fg2")}">${lb}</text><rect x="70" y="24" width="${W*b/mx}" height="12" rx="3" fill="${css("--zero")}" stroke="${col}" stroke-width=".8"/><text x="${74+W*b/mx}" y="33" font-size="9.5" fill="${css("--fg")}">${fmt(b,2)}</text></svg>`; };
  cards[0].viz = vizCI(exCh, cards[0].c); cards[1].viz = vizCI(exKw, cards[1].c); cards[2].viz = vizCI(B("exp", NAT ? "within10" : "kwh"), cards[2].c);
  cards[3].viz = vizLorenz(D.A.lorenz.ch, 0.8, cards[3].c, D.A.gini_pc.ch); cards[4].viz = vizWaffle(cov.pop_without/M.pop, cards[4].c); cards[5].viz = vizSplit(tp.between_share, cards[5].c);
  cards[6].viz = vizRatio(city.per100k, reg.per100k, "cities", "regencies", cards[6].c); cards[7].viz = vizCI(dch, cards[7].c);
  const cap = {3: "Lorenz curve of chargers per resident: residents sorted from worst- to best-served; the dashed line is perfect equality", 4: `100 squares = all residents; coloured = living in a ${UNIT} with no charger`, 5: "Theil T split: share of inequality between vs within"};
  $("evidence").innerHTML = cards.slice(0,6).map((c,i) => `<div class="card ${c.c}"><div class="hd"><div class="bigv">${c.big} <small>${c.small}</small></div><div class="viz" title="${cap[i] || "Concentration index with its 95 % bootstrap band; 0 = proportional to population"}">${c.viz}</div></div><div class="t">${c.t}</div><div class="d">${c.d}</div><div class="so">${c.so}</div></div>`).join(""); }

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
  const l2 = (title, items, f) => `<h3>${title}</h3><ol>${items.slice(0,8).map(x => `<li>${f(x)}</li>`).join("")}</ol>`;
  $("lists").innerHTML = l2("Most chargers per 100,000 residents", D.A.per100k_extremes.top, x => `${esc(x.name)} <span>· ${esc(x.parent)} · ${fmt(x.v,2)}</span>`) + `<div style="height:8px"></div>` + l2(`Largest ${UNITS} without a charger`, D.A.largest_without, x => `${esc(x.name)} <span>· ${esc(x.parent)} · ${fmt(x.pop/1e3,0)}k people</span>`) + `<div style="height:8px"></div>` + l2(`Fewest per resident among big ${UNITS}`, D.A.per100k_extremes.bottom_big, x => `${esc(x.name)} <span>· ${esc(x.parent)} · ${fmt(x.v,2)}</span>`); }

// ---------- Lorenz & market
function lineChart(id, series, xl, yl){ const W = 520, H = 340, m = {l:50, r:12, t:12, b:40}, pw = W-m.l-m.r, ph = H-m.t-m.b, X = p => m.l + p*pw, Y = p => m.t + (1-p)*ph; const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"});
  for (let i = 0; i <= 4; i++){ const p = i/4; el("line", {x1:X(0), x2:X(1), y1:Y(p), y2:Y(p), stroke:css("--grid")}, svg); el("line", {y1:Y(0), y2:Y(1), x1:X(p), x2:X(p), stroke:css("--grid")}, svg); el("text", {x:X(p), y:H-m.b+16, "text-anchor":"middle"}, svg).textContent = p*100+" %"; el("text", {x:m.l-6, y:Y(p)+4, "text-anchor":"end"}, svg).textContent = p*100+" %"; }
  el("text", {x:X(.5), y:H-6, "text-anchor":"middle"}, svg).textContent = xl; el("text", {x:14, y:Y(.5), "text-anchor":"middle", transform:`rotate(-90 14 ${Y(.5)})`}, svg).textContent = yl; el("line", {x1:X(0), y1:Y(0), x2:X(1), y2:Y(1), stroke:css("--fg3"), "stroke-dasharray":"3 3"}, svg);
  const interp = (pts, x) => { for (let i = 1; i < pts.length; i++) if (pts[i][0] >= x){ const [x0,y0] = pts[i-1], [x1,y1] = pts[i]; return x1 === x0 ? y1 : y0 + (y1-y0)*(x-x0)/(x1-x0); } return 1; };
  series.forEach(s => { el("path", {d: s.pts.map((p,i) => (i?"L":"M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1)).join(""), fill:"none", stroke:css(s.col), "stroke-width":2, "stroke-linejoin":"round"}, svg); if (s.lab) el("text", {x:s.at[0], y:s.at[1], fill:css(s.col), "font-weight":600}, svg).textContent = s.lab; });
  const cross = el("line", {y1:Y(0), y2:Y(1), stroke:css("--fg3"), visibility:"hidden"}, svg); const hit = el("rect", {x:m.l, y:m.t, width:pw, height:ph, fill:"transparent"}, svg);
  hit.addEventListener("pointermove", ev => { const rc = svg.getBoundingClientRect(); const p = Math.max(0, Math.min(1, ((ev.clientX-rc.left)*W/rc.width - m.l)/pw)); cross.setAttribute("x1", X(p)); cross.setAttribute("x2", X(p)); cross.setAttribute("visibility", "visible"); showTip(ev, `<b>Bottom ${fmt(p*100)} % of residents</b><br>` + series.map(s => `${s.name}: ${fmt(interp(s.pts,p)*100,1)} %`).join("<br>")); });
  hit.addEventListener("pointerleave", () => { cross.setAttribute("visibility", "hidden"); hideTip(); }); const box = $(id); box.innerHTML = ""; box.appendChild(svg); }

// ---------- forest
// ---------- within-area re-estimation (client side, same estimators as scripts/concentration_explorer.py)
let FW = "all", FD = null;
function wranksJS(r, w){ const n = r.length, o = [...r.keys()].sort((a,b) => r[a]-r[b] || a-b), W = w.reduce((s,x) => s+x, 0), out = new Array(n); let cum = 0, i = 0;
  while (i < n){ let j = i; while (j+1 < n && r[o[j+1]] === r[o[i]]) j++; let sw = 0; for (let k = i; k <= j; k++) sw += w[o[k]]; for (let k = i; k <= j; k++) out[o[k]] = (cum + sw/2)/W; cum += sw; i = j+1; } return out; }
function concJS(h, r, w){ const W = w.reduce((s,x) => s+x, 0), H = h.reduce((s,x) => s+x, 0); if (!(H > 0) || !(W > 0)) return NaN; const R = wranksJS(r, w), mu = H/W; let mR = 0; for (let i = 0; i < w.length; i++) mR += w[i]*R[i]; mR /= W; let t = 0; for (let i = 0; i < w.length; i++) t += w[i]*(h[i]/w[i] - mu)*(R[i] - mR); return 2*t/W/mu; }
function errJS(y, r, w){ const W = w.reduce((s,x) => s+x, 0), R = wranksJS(r, w); let t = 0; for (let i = 0; i < w.length; i++) t += w[i]*y[i]*(R[i]-0.5); return 8*t/W; }
function rng32(seed){ let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function bootJS(h, r, w, fn, reps){ const n = h.length, rnd = rng32(2026), out = []; for (let b = 0; b < reps; b++){ const hh = [], rr = [], ww = []; for (let i = 0; i < n; i++){ const k = Math.floor(rnd()*n); hh.push(h[k]); rr.push(r[k]); ww.push(w[k]); } const c = fn(hh, rr, ww); if (!isNaN(c)) out.push(c); } out.sort((a,b) => a-b); return out.length ? [out[Math.floor(out.length*.025)], out[Math.floor(out.length*.975)]] : [NaN, NaN]; }
function curveJS(h, r, w, k=40){ const o = [...r.keys()].sort((a,b) => r[a]-r[b] || a-b), W = w.reduce((s,x) => s+x, 0), H = Math.max(h.reduce((s,x) => s+x, 0), 1e-9), cw = [0], ch = [0]; let a = 0, b = 0; o.forEach(i => { a += w[i]; b += h[i]; cw.push(a/W); ch.push(b/H); });
  const interp = p => { let j = 1; while (j < cw.length && cw[j] < p) j++; if (j >= cw.length) return 1; const x0 = cw[j-1], x1 = cw[j]; return x1 === x0 ? ch[j] : ch[j-1] + (ch[j]-ch[j-1])*(p-x0)/(x1-x0); };
  return Array.from({length:k+1}, (_,i) => [i/k, interp(i/k)]); }
function fifthsJS(h, r, w){ const o = [...r.keys()].sort((a,b) => r[a]-r[b] || a-b), W = w.reduce((s,x) => s+x, 0), out = [0,0,0,0,0]; let cum = 0; o.forEach(i => { cum += w[i]; const q = Math.min(4, Math.max(0, Math.ceil(cum/W*5 - 1e-9) - 1)); out[q] += h[i]; }); return out; }
const OUTV = u => ({ch:u.ch, kw:u.kw, kwh:u.kwh, trx:u.trx, ev:u.ev, sites:u.sites, dc:u.dc});
function buildFD(){ if (FW === "all"){ FD = null; return; } const us = U.filter(u => u.parent === FW && u.pop > 0), w = us.map(u => u.pop), reps = 600;
  const valid = M.ranks.filter(rk => { const v = us.map(u => rk.key === "npov" ? u.pov : u[rk.key]); return v.every(x => x != null && !isNaN(x)) && new Set(v).size > 1; }).map(rk => rk.key);
  const Bm = {}, Cv = {}, Qf = {};
  valid.forEach(rk => { const r = us.map(u => rk === "npov" ? -u.pov : u[rk]); Cv[rk] = {}; Qf[rk] = {};
    M.outcomes.forEach(o => { let h, fn; if (o.key === "has"){ h = us.map(u => u.ch > 0 ? 1 : 0); fn = errJS; } else if (o.key === "within10"){ h = us.map(u => u.within10/100); fn = errJS; } else { h = us.map(u => OUTV(u)[o.key] || 0); fn = concJS; }
      const ci = fn(h, r, w); if (isNaN(ci)) return; const [lo, hi] = bootJS(h, r, w, fn, reps); Bm[rk + "|" + o.key] = {rank:rk, outcome:o.key, ci, lo, hi, signif: !(lo <= 0 && hi >= 0)};
      if (o.key !== "has" && o.key !== "within10"){ Cv[rk][o.key] = curveJS(h, r, w); Qf[rk][o.key] = fifthsJS(h, r, w); } }); });
  FD = {n: us.length, ranks: valid, B: Bm, curves: Cv, fifths: Qf, reps, name: FW, nAll: M.ranks.length}; }
const FB = (r, o) => FD ? FD.B[r + "|" + o] : B(r, o);
function withinInit(){ const sel = $("f-within"); if (sel.dataset.scope === S) return; sel.dataset.scope = S; FW = "all"; FD = null;
  const cnt = {}; U.forEach(u => { cnt[u.parent] = (cnt[u.parent] || 0) + 1; }); const minN = NAT ? 8 : 12;
  const opts = Object.keys(cnt).filter(k => cnt[k] >= minN).sort((a,b) => a.localeCompare(b));
  sel.innerHTML = `<option value="all">All ${fmt(U.length)} ${UNITS} (${M.n_parents} ${PARENTS})</option>` + opts.map(k => `<option value="${esc(k)}">${esc(k)} · ${cnt[k]} ${UNITS}</option>`).join("");
  sel.onchange = () => { FW = sel.value; buildFD(); forest(); curveInit(); }; }
function forest(){ withinInit(); $("forest-note").innerHTML = `The concentration index (CI) ranks residents by a socio-economic variable (low → high) and reads how much of the supply the bottom x % receive. +1 = everything at the top, 0 = proportional, −1 = everything at the bottom. Dots are estimates, bars are 95 % bootstrap bands (${fmt(M.boot)} resamples of ${UNITS}); filled dots do not cross zero. For yes/no and share outcomes the Erreygers-corrected index is shown.`;
  const outs = M.outcomes.map(o => o.key), ranks = FD ? FD.ranks : M.ranks.map(r => r.key); const rows = []; ranks.forEach(r => outs.forEach(o => { const b = FB(r,o); if (b) rows.push({...b, lab: OL[o], grp: RL[r].label}); }));
  const skipped = FD ? M.ranks.filter(r => !FD.ranks.includes(r.key)).map(r => r.label) : [];
  $("f-within-note").innerHTML = FD ? `${FD.n} ${UNITS} inside ${esc(FD.name)} re-estimated in the browser (${FD.reps} bootstrap resamples, seed 2026).${skipped.length ? ` <b>Not estimable here:</b> ${skipped.join(", ")} — ${NAT ? "no variation" : "these are district-level BPS variables, identical for every sub-district of one district"}.` : ""}` : `Pick a ${PARENT} to re-estimate every index inside it; ${NAT ? "socio-economic variables are district-level, so they vary within a province" : "spending, HDI and poverty are district-level, so inside one district only density and EV ownership can rank sub-districts"}.`;
  if (!rows.length){ $("forest").innerHTML = `<div class="note">No index can be estimated inside ${esc(FD ? FD.name : "")}.</div>`; $("forest-leg").innerHTML = ""; $("f-take").innerHTML = ""; return; }
  const rowH = FD ? 22 : 17, lab = 215, W = 760, H = rows.length*rowH + ranks.length*16 + 30, lo = Math.min(-0.2, ...rows.map(x => x.lo)) - 0.05, hi = Math.max(0.3, ...rows.map(x => x.hi)) + 0.05, X = v => lab + (v-lo)/(hi-lo)*(W-lab-30);
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"}); [-0.5,-0.25,0,0.25,0.5,0.75].filter(v => v > lo && v < hi).forEach(v => { el("line", {x1:X(v), x2:X(v), y1:0, y2:H-24, stroke: v ? css("--grid") : css("--fg3")}, svg); el("text", {x:X(v), y:H-8, "text-anchor":"middle"}, svg).textContent = (v>0?"+":"") + v; });
  el("text", {x:X(hi)-4, y:12, "text-anchor":"end", "font-size":11}, svg).textContent = "→ supply concentrated at the TOP of the ranking"; el("text", {x:lab+4, y:12, "font-size":11}, svg).textContent = "← at the BOTTOM";
  let y = 18, g0 = null; rows.forEach(r => { if (r.grp !== g0){ y += 16; el("text", {x:4, y:y-3, "font-weight":700, "font-size":11.5, fill:css("--fg")}, svg).textContent = "Ranked by " + r.grp; g0 = r.grp; }
    const yy = y + rowH/2; el("text", {x:lab-10, y:yy+4, "text-anchor":"end", "font-size":11}, svg).textContent = r.lab; const col = r.outcome === "has" || r.outcome === "within10" ? "--s3" : (NAT ? "--s1" : (["kwh","trx","ev"].includes(r.outcome) ? "--s2" : "--s1"));
    el("line", {x1:X(r.lo), x2:X(r.hi), y1:yy, y2:yy, stroke:css(col), "stroke-width":2}, svg); const c = el("circle", {cx:X(r.ci), cy:yy, r:5, fill: r.signif ? css(col) : css("--bg"), stroke:css(col), "stroke-width":2}, svg); el("text", {x:X(r.hi)+8, y:yy+4, "font-size":11}, svg).textContent = sgn(r.ci);
    c.addEventListener("pointermove", ev => showTip(ev, `<b>${r.lab}</b> ranked by ${r.grp}<br>CI ${sgn(r.ci)} · 95 % ${sgn(r.lo)} to ${sgn(r.hi)}<br>${r.signif ? "band excludes zero" : "not distinguishable from zero"}`)); c.addEventListener("pointerleave", hideTip); y += rowH; });
  $("forest").innerHTML = ""; $("forest").appendChild(svg);
  $("forest-leg").innerHTML = `<span><i class="dot" style="background:var(--s1)"></i>Placement & capacity</span>${NAT ? "" : `<span><i class="dot" style="background:var(--s2)"></i>Use & demand (kWh, sessions, EV owners)</span>`}<span><i class="dot" style="background:var(--s3)"></i>Erreygers (yes/no, share)</span><span class="sig">● filled = 95 % band excludes 0 · ○ hollow = not significant</span>`;
  const nsig = rows.filter(r => r.signif && r.ci > 0).length, exCh = B("exp","ch");
  if (FD){ const neg = rows.filter(r => r.signif && r.ci < 0).length, dCh = FB("dens","ch"), lead = rows.filter(r => r.signif).sort((a,b) => Math.abs(b.ci) - Math.abs(a.ci))[0];
    $("f-take").innerHTML = `<b>Inside ${esc(FD.name)} (${FD.n} ${UNITS}): ${nsig} of ${rows.length} indices are positive and significant${neg ? `, ${neg} negative` : ""}.</b> ${dCh ? `Chargers vs density ${sgn(dCh.ci)}${dCh.signif ? "" : " (n.s.)"}: ${dCh.signif && dCh.ci > 0 ? "supply sits in the denser " + UNITS : dCh.signif ? "supply sits in the sparser " + UNITS : "no measurable tilt by density"}. ` : ""}${lead ? `Strongest tilt: ${lead.lab} by ${lead.grp} (${sgn(lead.ci)}). ` : "No index is distinguishable from zero at this sample size. "}Within-${PARENT} bands are wide (${FD.n} units); read the sign, not the third decimal.`; return; }
  $("f-take").innerHTML = NAT ? `<b>${nsig} of ${rows.length} indices are positive and significant.</b> Whatever you rank residents by and whatever you count, supply sits with the advantaged — and the tilt grows from units (${sgn(exCh.ci)}) to capacity (${sgn(B("exp","kw").ci)}) to reach (${sgn(B("exp","within10").ci)}).` : `<b>Placement is income-neutral (${sgn(exCh.ci)}, hollow dot), but capacity (${sgn(B("exp","kw").ci)}) and use (${sgn(B("exp","kwh").ci)}) are not.</b> ${nsig} of ${rows.length} indices are positive and significant — the ones that fail are about <i>where units stand</i>, the ones that pass are about <i>how big they are and who uses them</i>.`; }

// ---------- curve
function curveInit(){ const cvR = $("cv-rank"), cvO = $("cv-out"), ranks = FD ? M.ranks.filter(r => FD.ranks.includes(r.key)) : M.ranks; cvR.innerHTML = ranks.map(r => `<option value="${r.key}">${r.label}</option>`).join(""); cvO.innerHTML = M.outcomes.filter(o => o.key !== "has" && o.key !== "within10").map(o => `<option value="${o.key}">${o.label}</option>`).join(""); drawCurve(); }
function drawCurve(){ const r = $("cv-rank").value, o = $("cv-out").value; if (!r){ $("curve").innerHTML = ""; $("curve-note").textContent = ""; return; } const pts = FD ? FD.curves[r][o] : D.curves[r][o], b = FB(r,o); if (!pts || !b){ $("curve").innerHTML = ""; $("curve-note").textContent = `No ${OL[o]} inside ${esc(FD ? FD.name : "")}.`; return; }
  lineChart("curve", [{pts, col:"--s1", name:OL[o], lab:`CI ${sgn(b.ci)}${b.signif?"":" (n.s.)"}`, at:[70, 40]}], `Cumulative share of residents${FD ? " of " + esc(FD.name) : ""}, ranked by ${RL[r].label} (low → high)`, `Cumulative share of ${OL[o]}`);
  const f = FD ? FD.fifths[r][o] : D.Q[r].map(x => x[o]), tot = f.reduce((s,x) => s+x, 0) || 1; $("curve-note").innerHTML = `Bottom fifth (${RL[r].low}) gets <b>${pct(100*f[0]/tot)}</b>, top fifth (${RL[r].high}) <b>${pct(100*f[4]/tot)}</b> of ${OL[o]}${FD ? " in " + esc(FD.name) : ""}. Band ${sgn(b.lo)} to ${sgn(b.hi)}.`; }

// ---------- quintiles
function barChart(vals, labels, col, title, fmtv){ const W = 340, H = 200, m = {l:44, r:8, t:26, b:34}, pw = W-m.l-m.r, ph = H-m.t-m.b, top = Math.max(...vals, 1e-9)*1.15, Y = v => m.t + (1-v/top)*ph, bw = pw/vals.length; const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":title}); el("text", {x:m.l, y:14, "font-weight":600, fill:css("--fg")}, svg).textContent = title;
  [0,.25,.5,.75,1].forEach(f => { el("line", {x1:m.l, x2:W-m.r, y1:Y(f*top), y2:Y(f*top), stroke:css("--grid")}, svg); el("text", {x:m.l-5, y:Y(f*top)+4, "text-anchor":"end", "font-size":10.5}, svg).textContent = fmtv(f*top); });
  vals.forEach((v, i) => { const x = m.l + i*bw + 6, w = bw - 12, y = Y(v); el("path", {d:`M${x} ${m.t+ph}V${y+4}a4 4 0 0 1 4 -4h${w-8}a4 4 0 0 1 4 4V${m.t+ph}Z`, fill:css(col)}, svg); el("text", {x:x+w/2, y:y-5, "text-anchor":"middle", "font-size":11, fill:css("--fg")}, svg).textContent = fmtv(v); el("text", {x:x+w/2, y:H-m.b+16, "text-anchor":"middle", "font-size":11}, svg).textContent = labels[i]; }); return svg; }
function quintInit(){ const qR = $("q-rank"); qR.innerHTML = M.ranks.map(r => `<option value="${r.key}">${r.label}</option>`).join(""); drawQuint(); }
function drawQuint(){ const r = $("q-rank").value, q = D.Q[r], labs = ["Q1 "+RL[r].low.split(" ")[0], "Q2", "Q3", "Q4", "Q5 "+RL[r].high.split(" ")[0]]; const box = $("quint"); box.innerHTML = "";
  const panels = [[q.map(x => x.ch_per100k), "--s1", "Chargers per 100,000", v => fmt(v,2)], [q.map(x => x.kw_per100k), "--s1", "Capacity kW per 100,000", v => fmt(v,0)], NAT ? [q.map(x => x.within10), "--s3", "Within 10 km of a charger (%)", v => fmt(v,0)] : [q.map(x => x.kwh_per100k/1e5*1000), "--s2", "Energy sold, Wh per resident", v => fmt(v,0)],
    [q.map(x => x.pop_no_charger_pct), "--s4", `In a ${UNIT} with no charger (%)`, v => fmt(v,0)]];
  panels.forEach(p => { const d = document.createElement("div"); d.className = "chart"; d.appendChild(barChart(p[0], labs, p[1], p[2], p[3])); box.appendChild(d); });
  $("q-note").innerHTML = `Residents in five equal groups (≈ ${fmt(q[0].pop/1e6,1)} M each) by the chosen variable; Q1 = lowest. If supply were proportional to people, every bar would be level. ${r === "dens" || r === "ev100k" ? "Measured per " + UNIT + "." : "Socio-economic variables are district-level (BPS 2024)" + (NAT ? "." : ", inherited by sub-districts.")}`;
  const qe = D.Q.exp; $("q-take").innerHTML = NAT ? `<b>Not a staircase but a cliff:</b> ${fmt(qe[0].ch_per100k,2)} → ${fmt(qe[1].ch_per100k,2)} → ${fmt(qe[2].ch_per100k,2)} → ${fmt(qe[3].ch_per100k,2)} → <b>${fmt(qe[4].ch_per100k,2)}</b> chargers per 100,000. The richest fifth holds ${pct(100*qe[4].ch/M.chargers,0)} of all chargers for 20 % of people.` : `<b>Almost flat:</b> ${fmt(qe[0].ch_per100k,2)} → ${fmt(qe[4].ch_per100k,2)} chargers per 100,000 from poorest to richest fifth — but energy sold per resident is ${fmt(qe[4].kwh_per100k/Math.max(qe[0].kwh_per100k,1e-6),1)}× higher at the top. Placement is level; use is not.`; }

// ---------- Theil & groups
function theil(){ const t = D.D.theil_parent, W = 900, H = 86; const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"}); const bars = [[`Between ${PARENTS}`, t.between_share, "--s2"], [`Within ${PARENTS}`, 1 - t.between_share, "--s1"]]; let x = 20; el("text", {x:20, y:18, "font-weight":600, fill:css("--fg")}, svg).textContent = `Theil T = ${t.T} for chargers per resident across ${UNITS}`;
  bars.forEach(([l, s, c]) => { const w = s*(W-40) - 2; el("rect", {x, y:30, width:w, height:28, rx:4, fill:css(c)}, svg); const inside = w > 260; el("text", inside ? {x:x+8, y:49, fill:"#fff", "font-weight":600} : {x, y:72, fill:css(c), "font-weight":600, "font-size":12}, svg).textContent = `${l}: ${pct(100*s,0)}`; x += w + 2; });
  const ti = D.D.theil_island; if (ti) el("text", {x:20, y:76, fill:css("--fg2"), "font-size":12}, svg).textContent = `By island group only ${pct(100*ti.between_share,0)} is between islands — province, not island, is where the gap sits.`;
  $("theil").innerHTML = ""; $("theil").appendChild(svg);
  const pick = NAT ? ["Metropolitan areas vs outside", "By island group"] : ["Metropolitan areas vs outside", "City vs regency"];
  $("groups").innerHTML = D.D.groups.filter(g => pick.includes(g.name)).map(g => `<div class="panel" style="overflow:auto"><h3>${g.name}${g.theil ? ` · ${pct(100*g.theil.between_share,0)} of Theil between these groups` : ""}</h3><table><thead><tr><th>Group</th><th>Residents</th><th>Chargers</th><th>per 100k</th><th>${NAT ? "≤ 10 km" : "kWh / resident"}</th><th title="share of chargers ÷ share of residents">Ratio</th></tr></thead><tbody>${g.rows.slice().sort((a,b) => b.per100k - a.per100k).map(r => { const tg = g.theil.groups.find(x => x.group === r.group); return `<tr><td>${esc(r.group)}</td><td>${fmt(r.pop/1e6,1)} M</td><td>${fmt(r.chargers)}</td><td><span class="bar"><i style="width:${Math.min(100, 100*r.per100k/Math.max(...g.rows.map(x=>x.per100k)))}%"></i></span>${fmt(r.per100k,2)}</td><td>${NAT ? pct(r.within10,0) : fmt(r.kwh_pc,3)}</td><td>${tg ? fmt(tg.ratio,1)+"×" : "–"}</td></tr>`; }).join("")}</tbody></table></div>`).join("");
  const cr = D.D.groups.find(g => g.name === "City vs regency").rows, city = cr.find(r => r.group.startsWith("City")), reg = cr.find(r => r.group.startsWith("Regency"));
  $("s-take").innerHTML = NAT ? `<b>${pct(100*t.between_share,0)} of the inequality is between provinces</b> — so the lever is national allocation across provinces, not planning inside them. Cities have ${fmt(city.per100k/reg.per100k,1)}× the chargers per resident of regencies, which hold ${pct(100*reg.pop/(city.pop+reg.pop),0)} of the population.` : `<b>Only ${pct(100*t.between_share,0)} is between districts; ${pct(100*(1-t.between_share),0)} is between sub-districts of the same district</b> — the lever is allocation inside each city and regency, not transfers between them.`; }

// ---------- robust, deficit, table, method
function rest(){ const rob = D.G.robust, k3 = NAT ? "ci_w10" : "ci_kwh", l3 = NAT ? "≤ 10 km" : "kWh";
  { const rowH = 19, lab = 200, W = 460, H = rob.length*rowH + 22, vals = rob.flatMap(r => [r.ci_ch, r.ci_kw, r[k3]]), lo = Math.min(-0.1, ...vals) - 0.05, hi = Math.max(...vals) + 0.08, X = v => lab + (v-lo)/(hi-lo)*(W-lab-10);
    const dots = rob.map((r, i) => { const y = 12 + i*rowH; return `<text x="${lab-8}" y="${y+4}" font-size="10" text-anchor="end" fill="${css("--fg")}">${esc(r.subset.replace("metropolitan", "metro").replace("residents", "res."))} <tspan fill="${css("--fg3")}">· ${fmt(r.n)}</tspan></text><line x1="${X(lo)}" x2="${X(hi)}" y1="${y}" y2="${y}" stroke="${css("--grid")}"/><line x1="${X(Math.min(r.ci_ch, r.ci_kw, r[k3]))}" x2="${X(Math.max(r.ci_ch, r.ci_kw, r[k3]))}" y1="${y}" y2="${y}" stroke="${css("--fg3")}" stroke-width="1.2"/><circle cx="${X(r.ci_ch)}" cy="${y}" r="4" fill="${css("--s1")}"/><circle cx="${X(r.ci_kw)}" cy="${y}" r="4" fill="${css("--s3")}"/><circle cx="${X(r[k3])}" cy="${y}" r="4" fill="${css("--s2")}"/>`; }).join("");
    $("robust").innerHTML = `<div class="rob"><svg viewBox="0 0 ${W} ${H}"><rect x="${X(0)}" y="2" width="${X(hi)-X(0)}" height="${H-18}" fill="${css("--crit")}" opacity=".06"/><line x1="${X(0)}" x2="${X(0)}" y1="2" y2="${H-16}" stroke="${css("--fg3")}"/>${dots}<text x="${X(0)}" y="${H-3}" font-size="9" text-anchor="middle" fill="${css("--fg3")}">0</text><text x="${X(hi)}" y="${H-3}" font-size="9" text-anchor="end" fill="${css("--fg3")}">pro-rich → ${sgn(hi-0.08)}</text></svg></div><div class="tt-leg" style="margin:4px 0 0"><span><i style="background:var(--s1)"></i>CI chargers</span><span><i style="background:var(--s3)"></i>CI kW</span><span><i style="background:var(--s2)"></i>CI ${l3}</span></div><p class="note" style="margin-top:6px">All against spending per person. ${rob.every(r => r.ci_ch > 0) ? "The sign never flips" : "The sign flips in some subsets"} — the finding is not an artefact of ${NAT ? "Jakarta" : "the metro"}.</p>`; }
  const tot = M.chargers + D.G.deficit, mxn = Math.max(...D.G.top.slice(0,4).map(x => x.need));
  $("deficit").innerHTML = `<div class="big" style="grid-template-columns:1fr 1fr;gap:8px"><div class="t" style="padding:10px 12px"><div><div class="v" style="font-size:26px">${fmt(D.G.deficit)}</div><div class="l">chargers to add · +${pct(100*D.G.deficit/M.chargers,0)} of ${fmt(M.chargers)}</div></div></div><div class="t" style="padding:10px 12px"><div><div class="v" style="font-size:26px">${fmt(D.G.units_short)}</div><div class="l">${UNITS} below today's average of ${fmt(D.G.mean100k,2)} per 100,000</div></div></div></div>
  <div class="def-bar"><div style="width:${100*M.chargers/tot}%;background:var(--s1)">today ${fmt(M.chargers)}</div><div style="width:${100*D.G.deficit/tot}%;background:var(--s2)">+${fmt(D.G.deficit)}</div></div>
  <div class="def-need">${D.G.top.slice(0,4).map(x => `<span>${esc(x.name)}</span><i style="width:${100*x.need/mxn}%"></i><b>+${x.need}</b>`).join("")}</div><p class="note" style="margin-top:6px">Water-filling to the current average, no charger removed. Largest needs: ${D.G.top.slice(0,4).map(x => `${esc(x.name)} +${x.need}`).join(", ")}. A yardstick, not a recommendation — the thesis asks whether counts are the right target at all.</p>`;
  $("method").innerHTML = `<h3>Data</h3><ul class="m"><li><b>Supply:</b> ${M.sources[0]}.</li>${NAT ? `<li><b>Reach:</b> share of residents within 10 km / beyond 25 km of an operational charger, straight-line from population hexagons (to be replaced by r5r travel time).</li>` : `<li><b>Use & demand:</b> ${M.sources[1]}; ${M.sources[2]}.</li>`}<li><b>Residents:</b> Kontur Population 2023 (H3 hexagons) summed to ${UNIT} polygons — ${fmt(M.pop/1e6,1)} M.</li><li><b>Ranking variables:</b> ${M.ses}${NAT ? "" : " — no official sub-district income exists, so income indices here compare districts with a finer denominator"}.</li></ul>
  <h3 style="margin-top:8px">Estimators</h3><ul class="m"><li>Population-weighted concentration index (Wagstaff), Erreygers correction for bounded outcomes, ${fmt(M.boot)}-resample bootstrap bands.</li><li>Gini and Lorenz on supply per resident; Theil T decomposition; quintiles split by cumulative population.</li></ul>
  <h3 style="margin-top:8px">Limits</h3><ul class="m"><li>Containment ≠ reach: a charger across a boundary serves neighbours.</li><li>Corridor (toll-road) chargers are counted where they sit.</li><li>${NAT ? "Chargers counted regardless of uptime; distance is straight-line." : "One month of transactions; EV owners proxied by completed PLN home-charger applications."}</li></ul>`; }

// ---------- chapters (one at a time)
const CH = [["overview","Overview","The question, five numbers, the story"],["people","100 residents","Poorest vs richest fifth, one square per person"],["gap","The gap","Provinces / districts ranked; who holds more than their share"],["map","Map","Where the supply sits"],["travel","Reach & capacity","10-min reach by car, E2SFCA power; rungs 0–2"],["cities","City equity map","508 districts of Indonesia: click a city for its equity profile"],["fifths","Fifths","Five equal groups of residents"],["inequitable","Follow advantage?","Concentration indices with 95 % bands"],["sources","Sources","Between vs within; cities, metros, Java"],["evidence","Evidence","Six findings, robustness, what it takes"],["method","Method","Data, estimators, limits, glossary"]];
let CUR_CH = "overview";
// ---------- travel time (r5r matrix, West Java + Jakarta + Tangerang pilot)
let ttCuts = null, TTV = null, TTN = null, TTG = null, TTS = null, ttBusy = false, ttSvg = null, ttVB = null, ttSel = "all", ttPaths = new Map(), ttKabBox = new Map(), ttSiteG = null, ttPX = null, ttPY = null;
const RUNGC = ["--crit","--s4","--good"], RUNGL = ["rung 0 · not reachable (> 10 min)", "rung 1 · reachable, capacity short", "rung 2 · reachable and capacity sufficient"];
const METROL = {jabodetabek:"Jabodetabek", bandung:"Bandung Raya", cirebon:"Cirebon Raya", luar:"outside the metros"};
function ttKab(code){ return TT.kabs.find(k => k.code === code); }
function travel(){ const r = TT.reach, l = TT.ladder;
  $("tt-note").innerHTML = `<b>Purpose · rungs 1–2 of the service ladder (RQ1).</b> Rung 1 <i>reachable</i>: nearest village with a public charger ≤ 10 min by car (r5r, OSM roads, Tuesday 14:00; 7 and 15 min test the threshold); failing it is rung 0. Rung 2 <i>sufficient capacity</i>: ≥ 0.03 kW per household from chargers in the same 10-min catchment (E2SFCA), so rung 2 ⊂ rung 1 <b>by construction</b>, not as a finding. Map area ≠ population: reachable villages look small because they are dense. Pilot: ${fmt(TT.n_villages)} villages, ${fmt(TT.pop/1e6,1)} M residents, ${TT.kabs.length} districts (Kepulauan Seribu excluded: islands without a road link).`;
  $("tt-big").innerHTML = ["7","10","15","30"].map(t => `<div class="t"><div class="v">${pct(100*r[t].share,0)}</div><div class="l">≤ ${t} min${t === "10" ? " · <b>rung 1</b>" : " by car"}</div></div>`).join("");
  const sel = $("tt-region"); if (!sel.options.length){ sel.innerHTML = `<option value="all">Whole pilot area (${TT.kabs.length} districts)</option>` + [...TT.kabs].sort((a,b) => a.name.localeCompare(b.name)).map(k => `<option value="${k.code}">${esc(k.name)}${k.prov !== "Jawa Barat" ? " · " + esc(k.prov.replace("DKI Jakarta","Jakarta")) : ""}</option>`).join(""); sel.addEventListener("change", () => ttSelect(sel.value)); }
  ttSide(); if (TTV) ttDraw(); else $("tt-map").innerHTML = `<div class="note">Open this chapter to load the village map (6,669 polygons, ≈ 4.7 MB).</div>`; }
let ttView = "insights";
function ttSide(){ const r = TT.reach, l = TT.ladder, A = TT.avg; $("tt-big").style.display = ttSel === "all" ? "" : "none";
  if (ttSel === "all"){ const q = TT.quintiles;
    const row = (name, o) => `<tr><td>${name}</td><td>${pct(100*o.reach7,0)}</td><td><b>${pct(100*o.share1,0)}</b></td><td>${pct(100*o.reach15,0)}</td><td>${pct(100*o.share2,0)}</td><td>${pct(100*o.suff10,1)}</td></tr>`;
    $("tt-side").innerHTML = `<div class="tt-bar">${l.rungs.map((x,i) => `<div style="width:${100*x.share}%;background:var(${RUNGC[i]})" title="${RUNGL[i]}: ${pct(100*x.share,1)}">${x.share > 0.08 ? pct(100*x.share,0) : ""}</div>`).join("")}</div><div class="tt-leg" style="gap:8px">${["rung 0 · > 10 min", "rung 1 · capacity short", "rung 2 · capacity ok"].map((t,i) => `<span><i style="background:var(${RUNGC[i]})"></i>${t} ${pct(100*l.rungs[i].share,0)}</span>`).join("")}</div>
      <div class="tt-seg"><button type="button" data-v="insights" aria-pressed="${ttView === "insights"}">Five insights</button><button type="button" data-v="numbers" aria-pressed="${ttView === "numbers"}">Numbers by area</button></div>
      ${ttView === "numbers" ? `<div id="tt-table"><table><thead><tr><th style="text-align:left">Residents within…</th><th>7 min</th><th>10 min</th><th>15 min</th><th>30 min</th><th title="rung 2: E2SFCA capacity sufficient">cap. ok</th></tr></thead><tbody>${TT.metros.map(m => row(m.label, m)).join("")}${q ? row("West Java · poorest fifth", q[0]) + row("West Java · richest fifth", q[4]) : ""}</tbody></table><div class="note" style="margin-top:6px">Share of residents whose nearest village with a public charger is within N minutes by car; cap. ok = rung 2 (E2SFCA ≥ 0.03 kW per household, 10-minute catchment, all-household denominator). Rung 2 uses the same catchment as rung 1, so it is a subset of the 10-minute column by construction.</div></div>`
        : `<ol class="tt-ins">${TT.insights.map(t => `<li>${t}</li>`).join("")}</ol>`}`;
    $("tt-side").querySelectorAll(".tt-seg button").forEach(b => b.addEventListener("click", () => { ttView = b.dataset.v; ttSide(); }));
    const jb = TT.metros.find(m => m.key === "jabodetabek"), lu = TT.metros.find(m => m.key === "luar"), e = TT.e2sfca["10"];
    $("tt-take").innerHTML = `<b>${pct(100*r["10"].share,0)} of residents can reach a charger village within 10 minutes by car</b>; ${pct(100*r["7"].share,0)} at 7 min, ${pct(100*r["15"].share,0)} at 15, and the ranking of places never changes. The gap is a metro cliff (Jabodetabek ${pct(100*jb.share1,0)} vs outside the metros ${pct(100*lu.share1,0)}) and an income gradient (West Java's poorest fifth ${pct(100*TT.quintiles[0].share1,0)} vs richest ${pct(100*TT.quintiles[4].share1,0)}). Capacity (rung 2) is near zero by construction with an all-household denominator; its tilt to spending (CI ${sgn(e.ci_expend)}) is the reading.`; return; }
  const k = ttKab(ttSel); if (!k) return;
  const ranked = [...TT.kabs].sort((a,b) => b.share1 - a.share1), rank = ranked.findIndex(x => x.code === k.code) + 1, n = TT.kabs.length;
  const unreached = k.pop * (1 - k.share1), cls = k.share1 >= 0.75 ? "high" : k.share1 >= 0.4 ? "mid" : "low", capRatio = k.suff10 / A.suff10, capcls = capRatio >= 1.5 ? "high" : capRatio >= 0.67 ? "mid" : "low", capOfReached = k.share1 > 0 ? k.suff10 / k.share1 : 0;
  const cmp = (lab, v, a) => `<div class="r"><span>${lab}</span><div class="bar"><i style="width:${100*v}%"></i><em style="left:${100*a}%" title="pilot average ${pct(100*a,0)}"></em></div><span><b>${pct(100*v,0)}</b></span></div>`;
  let read = "";
  const capLine = `Of the residents who are reachable, <b>${pct(100*capOfReached,0)}</b> also have sufficient capacity (rung 2: ${pct(100*k.suff10,1)} of all residents, ${capRatio >= 1.5 ? "above" : capRatio >= 0.67 ? "around" : capRatio >= 0.05 ? "well below" : "far below"} the pilot average of ${pct(100*A.suff10,1)}${capRatio > 0 && capRatio < 0.67 ? `, about ${capRatio >= 0.1 ? fmt(100*capRatio,0) + " %" : "one-" + fmt(1/Math.max(capRatio,1e-6),0) + "th"} of it` : ""}).`;
  if (cls === "high") read = `<p><b>Reach is largely solved here.</b> ${pct(100*k.share1,0)} of residents are within 10 minutes of a charger village (rank ${rank} of ${n}); the median resident is ${fmt(k.median,0)} min away. ${capLine} The question for ${esc(k.name)} moves up the ladder: capacity (rung 2) and use (rung 3, from transactions).</p>`;
  else if (cls === "mid") read = `<p><b>A reach gap inside the district.</b> ${pct(100*k.share1,0)} of residents are within 10 minutes (rank ${rank} of ${n}) but ${pct(100*k.share2,0)} within 30: the network exists at the district scale, served from a few charger villages, while ${fmt(unreached/1e6,2)} M residents in the periphery are beyond the 10-minute line. ${capLine} Both rungs bind: siting inside ${esc(k.name)} for reach, and more kW at the existing sites for capacity.</p>`;
  else read = `<p><b>Reach is the first constraint, and capacity binds behind it.</b> Only ${pct(100*k.share1,0)} of residents are within 10 minutes (rank ${rank} of ${n}); ${fmt(unreached/1e6,2)} M people live beyond the line${k.share2 < 0.6 ? `, and ${pct(100*(1-k.share2),0)} are beyond even 30 minutes` : ``}. ${capLine} "First" is the ladder order, not a claim that capacity is fine: ${esc(k.name)} fails rung 1 for most residents and rung 2 for nearly all of the rest.</p>`;
  read += `<p>${k.chargers ? `${fmt(k.chargers)} chargers at ${fmt(k.sites)} sites (${fmt(k.per100k,2)} per 100,000 residents vs pilot ${fmt(A.per100k,2)})` : `No public charger inside the district`}; ${k.metro === "luar" ? "outside the metropolitan areas" : "part of " + METROL[k.metro]}${k.expend ? `; spending ${fmt(k.expend)}k Rp per person, HDI ${k.ipm}, poverty ${k.p0} %` : ""}.</p>`;
  read += `<p><b>For the thesis.</b> ${cls === "high" ? "A rung-1 pass: this district is where rungs 2–5 (capacity, reliability, congestion, experience) decide whether residents are really served." : cls === "mid" ? "A within-district inequality case: Theil's within share, not the between share, explains this gap; the 7/15-minute tests show whether the periphery is near the line or far from it (" + pct(100*k.reach15,0) + " at 15 min)." : "A rung-0 case for most residents: counted by chargers per resident this district may look merely sparse; counted by reach it is unserved. This is the difference between containment and reach the proposal is about."} Rung 2 ⊂ rung 1 by construction (same catchment): the two shares are ordered, not correlated.</p>`;
  $("tt-side").innerHTML = `<div class="tt-card"><h3>${esc(k.name)}</h3><div class="sub">${esc(k.prov)} · ${k.metro === "luar" ? "outside the metros" : METROL[k.metro]} · ${fmt(k.n)} villages · ${fmt(k.pop/1e6,2)} M residents</div>
    <div class="tt-stats"><div><div class="v">${pct(100*k.share1,0)}</div><div class="l">within 10 min · rank ${rank}/${n}</div></div><div><div class="v">${fmt(k.median,0)} min</div><div class="l">median resident to a charger village</div></div><div><div class="v">${fmt(unreached/1e6,2)} M</div><div class="l">residents beyond 10 min</div></div></div>
    <div class="tt-cmp">${cmp("≤ 7 min", k.reach7, A.reach7)}${cmp("≤ 10 min", k.share1, A.share1)}${cmp("≤ 15 min", k.reach15, A.reach15)}${cmp("≤ 30 min", k.share2, A.share2)}<div style="margin-top:3px">bar = this district · tick = pilot average</div></div>
    <div class="tt-read">${read}</div></div>`;
  $("tt-take").innerHTML = `<b>${esc(k.name)}: ${pct(100*k.share1,0)} of residents within 10 minutes (rank ${rank} of ${n}); of those, ${pct(100*capOfReached,0)} also have sufficient capacity.</b> ${cls === "high" ? "Reach is solved; capacity and use are the open questions." : cls === "mid" ? "Served at district scale, not at neighbourhood scale: the last ten minutes are missing for " + fmt(unreached/1e6,2) + " M residents, and capacity is short for most of the rest." : "Reach is missing for " + fmt(unreached/1e6,2) + " M residents (rung 0) and capacity for nearly all who are reached (rung 1)."} Pick "Whole pilot area" or ⟲ to return to the overview.`; }
function ttSelect(code){ ttSel = code; $("tt-region").value = code; ttSide(); ttLegend();
  if (!ttSvg) return; ttPaths.forEach((p, id) => { const kc = p.dataset.k; p.classList.toggle("dim", code !== "all" && kc !== code); p.classList.toggle("sel", code !== "all" && kc === code); });
  if (code === "all") ttReset(); else { const b = ttKabBox.get(code); if (b) ttZoomTo(b); } }
async function ttLoad(){ if (TTV || ttBusy) return; ttBusy = true; $("tt-map").innerHTML = `<div class="note">Loading 6,669 village polygons…</div>`;
  try { const [j, g] = await Promise.all([fetch("../ttm/ttm.json").then(r => { if (!r.ok) throw new Error("ttm.json " + r.status); return r.json(); }), fetch("../ttm/input/villages_simplified.geojson").then(r => { if (!r.ok) throw new Error("geojson " + r.status); return r.json(); })]);
    TTV = new Map(j.villages.map(a => { const o = {}; j.village_cols.forEach((c,i) => o[c] = a[i]); return [o.id, o]; })); TTN = j.names; TTG = g.features;
    try { const t = await fetch("../ttm/input/spklu_sites.csv").then(r => r.ok ? r.text() : ""); TTS = t.trim().split("\n").slice(1).map(l => { const c = l.match(/("[^"]*"|[^,]*)(,|$)/g).map(x => x.replace(/,$/, "").replace(/^"|"$/g, "")); return {name:c[1], lon:+c[2], lat:+c[3], kab:c[5], kw:+c[6], ch:+c[7], cat:c[8], status:c[9]}; }).filter(x => isFinite(x.lon) && isFinite(x.lat)); } catch (e){ TTS = null; }
    ttDraw(); }
  catch (e){ $("tt-map").innerHTML = `<div class="note">Village map not available here (${esc(e.message)}). It loads on the deployed site, where ttm/ttm.json and the village polygons sit next to this page.</div>`; }
  ttBusy = false; }
function ttApply(){ ttSvg.setAttribute("viewBox", ttVB.join(" ")); if (ttSiteG){ const k = (+ttSvg.dataset.w) / ttVB[2]; ttSiteG.querySelectorAll("circle").forEach(c => { c.setAttribute("r", (+c.dataset.r) / Math.sqrt(k)); c.setAttribute("stroke-width", 0.6 / Math.sqrt(k)); }); } }
function ttSites(){ if (!ttSvg) return; if (ttSiteG){ ttSiteG.remove(); ttSiteG = null; } const f = $("tt-sites").value; if (f === "none" || !TTS) { $("tt-meta").textContent = `${fmt(TTG.length)} villages drawn · ${fmt(TT.rows/1e6,2)} M travel-time pairs`; return; }
  const keep = TTS.filter(x => f === "all" || (f === "PLN" && x.cat === "PLN") || (f === "nonPLN" && x.cat !== "PLN") || (f === "fast" && x.kw >= 50) || (f === "available" && x.status === "available") || (f === "offline" && x.status === "offline mode"));
  ttSiteG = el("g", {class:"sites"}, ttSvg);
  keep.forEach(x => { const r = 1.6 + 1.2*Math.sqrt(Math.max(x.ch,1)); const c = el("circle", {cx:ttPX(x.lon), cy:ttPY(x.lat), r:r, "data-r":r, fill:x.cat === "PLN" ? css("--s4") : css("--s1"), stroke:css("--bg"), "stroke-width":0.6, "fill-opacity":x.status === "offline mode" ? .55 : .95, "data-k":x.kab}, ttSiteG);
    c.addEventListener("pointermove", ev => { ev.stopPropagation(); showTip(ev, `<b>${esc(x.name)}</b><br>${fmt(x.kw)} kW · ${x.ch} charger${x.ch > 1 ? "s" : ""} · ${x.cat === "PLN" ? "PLN" : "partner"} · status: ${esc(x.status)}`); }); c.addEventListener("pointerleave", hideTip); });
  const kw = keep.reduce((s,x) => s + x.kw, 0), ch = keep.reduce((s,x) => s + x.ch, 0);
  $("tt-meta").textContent = `${fmt(keep.length)} sites shown · ${fmt(ch)} chargers · ${fmt(kw/1e3,1)} MW · gold = PLN, blue = partner, size = chargers, faded = offline mode`; ttApply(); }
$("tt-sites").addEventListener("change", ttSites);
function ttReset(){ if (!ttSvg) return; ttVB = [0, 0, +ttSvg.dataset.w, +ttSvg.dataset.h]; ttApply(); }
function ttZoomTo(b){ const W = +ttSvg.dataset.w, H = +ttSvg.dataset.h, bw = Math.max(b[2]-b[0], 1), bh = Math.max(b[3]-b[1], 1), k = Math.min(W/(bw*1.25), H/(bh*1.25), 40), w = W/k, h = H/k; ttVB = [(b[0]+b[2])/2 - w/2, (b[1]+b[3])/2 - h/2, w, h]; ttApply(); }
function ttZoomAt(cx, cy, f){ const [x, y, w, h] = ttVB, W = +ttSvg.dataset.w, H = +ttSvg.dataset.h; let nw = w/f, nh = h/f; if (nw > W){ nw = W; nh = H; } if (nw < W/40){ nw = W/40; nh = H/40; } const g = nw/w; ttVB = [cx - (cx - x)*g, cy - (cy - y)*g, nw, nh]; ttApply(); }
function ttPt(ev){ const p = ttSvg.createSVGPoint(); p.x = ev.clientX; p.y = ev.clientY; const q = p.matrixTransform(ttSvg.getScreenCTM().inverse()); return [q.x, q.y]; }
function ttDraw(){ if (!TTG) return; const key = $("tt-layer").value; let minx=1e9,miny=1e9,maxx=-1e9,maxy=-1e9; const walk = (c, fn) => typeof c[0] === "number" ? fn(c) : c.forEach(x => walk(x, fn));
  TTG.forEach(f => walk(f.geometry.coordinates, c => { if (c[0]<minx) minx=c[0]; if (c[0]>maxx) maxx=c[0]; if (c[1]<miny) miny=c[1]; if (c[1]>maxy) maxy=c[1]; }));
  const MW = 1000, k = Math.cos((miny+maxy)/2*Math.PI/180), MH = Math.round(MW*(maxy-miny)/((maxx-minx)*k)), PX = x => (x-minx)/(maxx-minx)*MW, PY = y => (maxy-y)/(maxy-miny)*MH;
  const box = $("tt-map"); const keepVB = ttSvg && ttVB; box.innerHTML = ""; ttSvg = el("svg", {viewBox:`0 0 ${MW} ${MH}`, role:"img", "aria-label":"Travel-time map", "data-w":MW, "data-h":MH}, box); if (!keepVB) ttVB = [0, 0, MW, MH]; ttApply();
  ttPX = PX; ttPY = PY; ttSiteG = null;
  const MINC = [5, 10, 15, 30, 60], MCOL = ["--q5","--q4","--q3","--q2","--q1"], SIX = ["--q1","--q2","--q3","--q4","--q5","--q6"];
  const qcuts = vals => { const v = vals.filter(x => x > 0).sort((a,b) => a-b); return [1,2,3,4,5].map(i => v[Math.min(v.length-1, Math.floor(v.length*i/6))]); };   // village sextiles
  const allV = [...TTV.values()], UNC = qcuts(allV.filter(v => !(v.access != null && v.access <= 10)).map(v => v.pop)), DNC = qcuts(allV.map(v => v.pop/Math.max(v.area||1,.01)));
  ttCuts = {UNC, DNC};
  const seq = (x, cuts) => { if (!(x > 0)) return css("--zero"); const i = cuts.findIndex(c => x <= c); return css(SIX[i < 0 ? 5 : i]); };
  const colorOf = v => { if (key === "rung") return v.rung == null ? css("--zero") : css(RUNGC[v.rung]); if (key === "unreached") return v.access != null && v.access <= 10 ? css("--zero") : seq(v.pop, UNC); if (key === "dens") return seq(v.pop/Math.max(v.area||1,.01), DNC); if (v.access == null) return css("--zero"); const i = MINC.findIndex(c => v.access <= c); return css(i < 0 ? "--zero" : MCOL[i]); };
  ttPaths = new Map(); ttKabBox = new Map();
  TTG.forEach(f => { const v = TTV.get(f.properties.id); if (!v) return; const kc = f.properties.k; const p = el("path", {d:geomPath(f.geometry, PX, PY), fill:colorOf(v), stroke:css("--bg"), "stroke-width":0.35, "data-k":kc, "vector-effect":"non-scaling-stroke"}, ttSvg); ttPaths.set(v.id, p);
    let bx = ttKabBox.get(kc) || [1e9,1e9,-1e9,-1e9]; walk(f.geometry.coordinates, c => { const x = PX(c[0]), y = PY(c[1]); if (x<bx[0]) bx[0]=x; if (x>bx[2]) bx[2]=x; if (y<bx[1]) bx[1]=y; if (y>bx[3]) bx[3]=y; }); ttKabBox.set(kc, bx);
    const nm = TTN[v.id] || ["","",""], kb = ttKab(kc);
    p.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(nm[0])}</b> · ${esc(nm[1])}, ${esc(nm[2])}<br>${fmt(v.pop)} residents · ${v.chargers} chargers here<br>nearest charger village: <b>${v.access == null ? "> 60 min" : fmt(v.access,0) + " min"}</b><br>chargers within 10 min: ${fmt(v.near)} · within 30 min: ${fmt(v.far)}<br>E2SFCA capacity: ${fmt(v.cap10,3)} kW/household · <i>${RUNGL[v.rung]}</i>${v.pop ? ` · ${fmt(v.pop/Math.max(v.area||1,.01))} /km²` : ""}${kb ? `<br><span style="opacity:.75">${esc(kb.name)}: ${pct(100*kb.share1,0)} within 10 min · click for the district reading</span>` : ""}`)); p.addEventListener("pointerleave", hideTip); });
  // controls: wheel zoom, drag pan, buttons, click to select district
  const hint = document.createElement("div"); hint.className = "tt-hint"; hint.textContent = "scroll = zoom · drag = pan · click a village = its district"; box.appendChild(hint);
  const z = document.createElement("div"); z.className = "tt-zoom"; z.innerHTML = `<button type="button" title="zoom in">+</button><button type="button" title="zoom out">−</button><button type="button" title="reset view" style="font-size:12px">⟲</button>`; box.appendChild(z);
  const [bi, bo, br] = z.querySelectorAll("button"); bi.onclick = () => ttZoomAt(ttVB[0]+ttVB[2]/2, ttVB[1]+ttVB[3]/2, 1.6); bo.onclick = () => ttZoomAt(ttVB[0]+ttVB[2]/2, ttVB[1]+ttVB[3]/2, 1/1.6); br.onclick = () => ttSelect("all");
  ttSvg.addEventListener("wheel", ev => { ev.preventDefault(); const [cx, cy] = ttPt(ev); ttZoomAt(cx, cy, ev.deltaY < 0 ? 1.3 : 1/1.3); }, {passive:false});
  let drag = null; ttSvg.addEventListener("pointerdown", ev => { drag = {p: ttPt(ev), vb: [...ttVB], moved: false, x: ev.clientX, y: ev.clientY, t: ev.target}; ttSvg.setPointerCapture(ev.pointerId); });
  ttSvg.addEventListener("pointermove", ev => { if (!drag) return; if (Math.abs(ev.clientX - drag.x) + Math.abs(ev.clientY - drag.y) > 3) drag.moved = true; if (!drag.moved) return; const [px, py] = ttPt(ev); ttVB[0] -= px - drag.p[0]; ttVB[1] -= py - drag.p[1]; ttApply(); });
  ttSvg.addEventListener("pointerup", ev => { if (drag && !drag.moved){ const t = drag.t; if (t && t.dataset && t.dataset.k) ttSelect(t.dataset.k); } drag = null; });
  ttSvg.addEventListener("pointercancel", () => { drag = null; });
  if (ttSel !== "all") ttSelect(ttSel);
  $("tt-meta").textContent = `${fmt(TTG.length)} villages drawn · ${fmt(TT.rows/1e6,2)} M travel-time pairs`;
  ttLegend(); ttSites(); }
function ttLegend(){ if (!ttCuts) return; const key = $("tt-layer").value, {UNC, DNC} = ttCuts, MINC = [5, 10, 15, 30, 60], MCOL = ["--q5","--q4","--q3","--q2","--q1"], SIX = ["--q1","--q2","--q3","--q4","--q5","--q6"];
  const k = ttSel === "all" ? null : ttKab(ttSel), who = k ? esc(k.name) : "the pilot area", reach10 = k ? k.share1 : TT.reach["10"].share, unr = k ? k.pop*(1-k.share1) : TT.pop*(1-TT.reach["10"].share);
  const seqLeg = cuts => SIX.map((c,i) => `<div class="sw"><i style="background:var(${c})"></i>${i === 0 ? "≤ " + fmt(cuts[0]) : i === 5 ? "> " + fmt(cuts[4]) : fmt(cuts[i-1]) + "–" + fmt(cuts[i])}</div>`).join("");
  $("tt-leg").innerHTML = key === "rung" ? `<div class="tt-leg" style="margin:0">${RUNGC.map((c,i) => `<span><i style="background:var(${c})"></i>${RUNGL[i]}</span>`).join("")}</div><div style="margin-left:10px">rung 1 = ≤ 10 min · rung 2 = rung 1 and ≥ ${TT.ladder.kw_per_hh} kW per household (E2SFCA, same 10-min catchment) · area ≠ population: in ${who} the orange/green villages hold ${pct(100*reach10,0)} of residents</div>`
    : key === "unreached" ? seqLeg(UNC) + `<div class="sw"><i style="background:var(--zero)"></i>reached ≤ 10 min</div><div style="margin-left:10px">residents per village beyond the 10-minute line (sextiles of unreached villages): where ${who}'s ${fmt(unr/1e6,2)} M unreached people live</div>`
    : key === "dens" ? seqLeg(DNC) + `<div style="margin-left:10px">residents per km², sextiles of all 6,669 villages (Kontur 2023 ÷ area): why small map areas carry large population shares</div>`
    : MCOL.map((c,i) => `<div class="sw"><i style="background:var(${c})"></i>${i ? MINC[i-1] + "–" + MINC[i] : "≤ " + MINC[0]} min</div>`).join("") + `<div class="sw"><i style="background:var(--zero)"></i>> 60 / none</div><div style="margin-left:10px">car travel time (p50) to the nearest village with a public charger · dark = close${k ? ` · ${who}: ${pct(100*reach10,0)} of residents ≤ 10 min` : ""}</div>`; }
$("tt-layer").addEventListener("change", ttDraw);
// ---------- city equity map (always national: 508 districts, every province)
let cmView = "insights", cmCityView = "curve", CM = null, cmSvg = null, cmVB = null, cmSel = null, cmPaths = new Map(), cmProvBox = new Map(), cmPX = null, cmPY = null;
const CML = [["per100k","Chargers per 100,000 residents","seq"],["kw100k","Charging capacity, kW per 100,000","seq"],["within10","Residents within 10 km of a charger (%)","seq"],["beyond25","Residents beyond 25 km of any charger (%)","seqr"],["eqpos","Equity position: supply rank minus spending rank","div"],["provci","Province tilt: within-province CI chargers ~ spending","div2"],["exp","Spending per person (k Rp/month)","seq"]];
function cmInit(){ if (CM) return; const Dn = ALL.national, units = Dn.units.map(a => { const o = {}; Dn.unit_cols.forEach((c,i) => o[c] = a[i]); o.per100k = 1e5*o.ch/o.pop; o.kw100k = 1e5*o.kw/o.pop; return o; }).filter(u => u.pop > 0);
  const n = units.length, pctl = key => { const o = [...units].sort((a,b) => a[key]-b[key]); const r = new Map(); let i = 0; while (i < n){ let j = i; while (j+1 < n && o[j+1][key] === o[i][key]) j++; const v = (i + j)/2/(n-1); for (let k = i; k <= j; k++) r.set(o[k].id, v); i = j+1; } return r; };
  const pS = pctl("per100k"), pE = pctl("exp"), pW = pctl("within10"), pK = pctl("kw100k"), pH = pctl("ipm");
  units.forEach(u => { u.p_supply = pS.get(u.id); u.p_exp = pE.get(u.id); u.p_reach = pW.get(u.id); u.p_kw = pK.get(u.id); u.p_ipm = pH.get(u.id); u.eqpos = 100*(u.p_supply - u.p_exp); });
  // income peers: districts within ±7.5 percentile points of spending
  units.forEach(u => { const peers = units.filter(v => v !== u && Math.abs(v.p_exp - u.p_exp) <= 0.075); const med = a => { const s = [...a].sort((x,y) => x-y); return s.length ? s[Math.floor(s.length/2)] : NaN; }; u.peer_n = peers.length; u.peer_per100k = med(peers.map(v => v.per100k)); u.peer_within10 = med(peers.map(v => v.within10)); });
  // within-province CI chargers ~ spending (provinces with >= 8 districts)
  const prov = {}; units.forEach(u => (prov[u.parent] = prov[u.parent] || []).push(u));
  const provCI = {}; Object.entries(prov).forEach(([k, us]) => { if (us.length >= 8 && new Set(us.map(u => u.exp)).size > 1) provCI[k] = concJS(us.map(u => u.ch), us.map(u => u.exp), us.map(u => u.pop)); });
  units.forEach(u => { u.provci = provCI[u.parent] == null ? null : provCI[u.parent]; });
  const rankOf = key => { const o = [...units].sort((a,b) => b[key]-a[key]); const r = new Map(); o.forEach((u,i) => r.set(u.id, i+1)); return r; };
  const P = units.reduce((s,u) => s+u.pop, 0), avg = {per100k: 1e5*units.reduce((s,u) => s+u.ch,0)/P, kw100k: 1e5*units.reduce((s,u) => s+u.kw,0)/P, within10: units.reduce((s,u) => s+u.within10*u.pop,0)/P, beyond25: units.reduce((s,u) => s+u.beyond25*u.pop,0)/P};
  const pavg = {}; Object.entries(prov).forEach(([k, us]) => { const p = us.reduce((s,u) => s+u.pop,0); pavg[k] = {n: us.length, per100k: 1e5*us.reduce((s,u) => s+u.ch,0)/p, kw100k: 1e5*us.reduce((s,u) => s+u.kw,0)/p, within10: us.reduce((s,u) => s+u.within10*u.pop,0)/p, beyond25: us.reduce((s,u) => s+u.beyond25*u.pop,0)/p, ci: provCI[k]}; });
  CM = {units, byId: new Map(units.map(u => [u.id, u])), rank: {per100k: rankOf("per100k"), within10: rankOf("within10"), kw100k: rankOf("kw100k"), eqpos: rankOf("eqpos")}, avg, pavg, provCI, prov, n, GEO: GEOS.national};
  CM.curveAll = curveJS(units.map(u => u.ch), units.map(u => u.exp), units.map(u => u.pop)); CM.ciAll = concJS(units.map(u => u.ch), units.map(u => u.exp), units.map(u => u.pop));
  CM.insights = cmInsights(units, null);
  const sel = $("cm-layer"); sel.innerHTML = CML.map(l => `<option value="${l[0]}">${l[1]}</option>`).join(""); sel.value = "eqpos"; sel.addEventListener("change", cmDraw);
  $("cm-dl").innerHTML = units.map(u => `<option value="${esc(u.name)} · ${esc(u.parent)}"></option>`).join("");
  $("cm-find").addEventListener("change", () => { const v = $("cm-find").value.toLowerCase().split(" · ")[0].trim(); const u = units.find(x => x.name.toLowerCase() === v) || units.find(x => x.name.toLowerCase().includes(v)); if (u) cmSelect(u.id); });
  const pv = $("cm-prov"); pv.innerHTML = `<option value="all">All Indonesia</option>` + Object.keys(prov).sort().map(k => `<option value="${esc(k)}">${esc(k)} · ${prov[k].length}</option>`).join(""); pv.addEventListener("change", () => cmProv(pv.value)); }
function cmInsights(pool, pn){ const mean = a => a.length ? a.reduce((x,y) => x+y, 0)/a.length : NaN, z = v => fmt(Math.abs(v) < 0.5 ? 0 : v, 0), fb = a => a.length ? pct(100*a.filter(u => u.eqpos <= -24).length/a.length, 0) : "–", P = pool.reduce((s,u) => s+u.pop, 0);
  const far = pool.filter(u => u.eqpos <= -24), up = pool.filter(u => u.eqpos >= 24), farPop = far.reduce((s,u) => s+u.pop, 0), farPoor = far.filter(u => u.p_exp < 0.5).length;
  const byProv = {}; far.forEach(u => byProv[u.parent] = (byProv[u.parent] || 0) + 1); const topProv = Object.entries(byProv).sort((a,b) => b[1]-a[1]).slice(0,3);
  const kota = pool.filter(u => u.kota), kab = pool.filter(u => !u.kota), metro = pool.filter(u => u.metro !== "Outside metro"), out = pool.filter(u => u.metro === "Outside metro"), java = pool.filter(u => u.island === "Jawa"), nonj = pool.filter(u => u.island !== "Jawa");
  // Spearman between equity position and HDI percentile
  const n = pool.length, rk = key => { const o = [...pool].sort((a,b) => a[key]-b[key]); const r = new Map(); o.forEach((u,i) => r.set(u.id, i)); return r; }, r1 = rk("eqpos"), r2 = rk("p_ipm"); let d2 = 0; pool.forEach(u => { const d = r1.get(u.id) - r2.get(u.id); d2 += d*d; }); const rho = n > 2 ? 1 - 6*d2/(n*(n*n-1)) : NaN;
  const ciS = Object.entries(CM ? CM.provCI : {}).sort((a,b) => b[1]-a[1]), proRich = ciS.slice(0,3), proPoor = ciS.filter(x => x[1] < 0);
  const where = pn ? esc(pn) : "Indonesia", out_ = [];
  out_.push(`<b>Who is far below their income rank.</b> ${far.length} ${pn ? "of " + esc(pn) + "'s " : ""}districts (${fmt(farPop/1e6,1)} M residents) are served far below what their spending predicts. Only ${farPoor} are in the poorer half: mostly <i>affluent districts where operators have not built</i>, not poor ones.${!pn && topProv.length ? ` They cluster in ${topProv.map(x => `${esc(x[0])} (${x[1]})`).join(", ")}.` : ""}`);
  if (!pn) out_.push(`<b>Java is not the gap.</b> ${fb(java)} of Java's ${java.length} districts are far below their income rank against ${fb(nonj)} of the ${nonj.length} outside Java; ${pct(100*nonj.filter(u => u.eqpos <= -24).length/Math.max(far.length,1),0)} of all far-below districts are outside Java.`);
  out_.push(`<b>Cities vs regencies.</b> ${fb(kota)} of the ${kota.length} cities (kota) are far below their income rank against ${fb(kab)} of the ${kab.length} regencies. ${mean(kota.map(u => u.eqpos)) > mean(kab.map(u => u.eqpos)) + 5 ? "Cities are served beyond their income rank, regencies below it: urban form, not only income, decides placement." : "Net of income, being a city buys no extra supply: the gradient is income, not urban status."}`);
  if (metro.length && out.length) out_.push(`<b>Metropolitan areas.</b> ${fb(metro)} of the ${metro.length} metro districts and ${fb(out)} of the ${out.length} outside are far below their income rank; ${up.filter(u => u.metro === "Outside metro").length} of the ${up.length} served far <i>above</i> it are outside any metro: corridor and tourism chargers, not city demand.`);
  if (!pn && proRich.length) out_.push(`<b>Province tilt.</b> Charger placement is most pro-rich inside ${proRich.map(x => `${esc(x[0])} (${sgn(x[1])})`).join(", ")}${proPoor.length ? `; ${proPoor.map(x => `${esc(x[0])} (${sgn(x[1])})`).join(", ")} ${proPoor.length > 1 ? "are" : "is"} the only pro-poor province${proPoor.length > 1 ? "s" : ""}` : "; no province is pro-poor"}.`);
  out_.push(`<b>Development does not rescue it.</b> Spearman ρ between equity position and HDI is ${fmt(rho,2)}: ${Math.abs(rho) < 0.2 ? "being more developed does not make a district more likely to be served above its income rank; the residual is operator placement, not readiness." : rho > 0 ? "more developed districts tend to be served above their income rank." : "the more developed a district, the more likely it is served <i>below</i> its income rank: supply has not kept up with the most developed places."}`);
  return out_; }
function cmCurve(series, mark, H = 128){ const W = 300, m = {l:44, r:8, t:8, b:22}, pw = W-m.l-m.r, ph = H-m.t-m.b, X = p => m.l + p*pw, Y = p => m.t + (1-p)*ph;
  const path = pts => pts.map((p,i) => (i ? "L" : "M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1)).join("");
  let mk = ""; if (mark){ const pts = series[0].pts, q = pts.reduce((a, p) => Math.abs(p[0]-mark.x) < Math.abs(a[0]-mark.x) ? p : a, pts[0]); mk = `<line x1="${X(mark.x)}" x2="${X(mark.x)}" y1="${Y(0)}" y2="${Y(q[1])}" stroke="${css("--fg")}" stroke-dasharray="2 2"/><circle cx="${X(mark.x)}" cy="${Y(q[1])}" r="4" fill="${css("--s1")}" stroke="${css("--bg")}" stroke-width="1.5"/><text x="${X(mark.x) + (mark.x > 0.6 ? -6 : 6)}" y="${Y(q[1]) - 7}" font-size="9" font-weight="700" text-anchor="${mark.x > 0.6 ? "end" : "start"}" fill="${css("--fg")}">${esc(mark.name)}</text>`; }
  return `<div class="cm-sc" style="height:${H}px"><svg viewBox="0 0 ${W} ${H}"><line x1="${X(0)}" y1="${Y(0)}" x2="${X(1)}" y2="${Y(1)}" stroke="${css("--fg3")}" stroke-dasharray="3 3"/>${[0.25,0.5,0.75].map(p => `<line x1="${X(p)}" x2="${X(p)}" y1="${Y(0)}" y2="${Y(1)}" stroke="${css("--grid")}"/><line y1="${Y(p)}" y2="${Y(p)}" x1="${X(0)}" x2="${X(1)}" stroke="${css("--grid")}"/>`).join("")}${series.map(sr => `<path d="${path(sr.pts)}" fill="none" stroke="${css(sr.col)}" stroke-width="${sr.w || 2}" ${sr.dash ? `stroke-dasharray="${sr.dash}"` : ""}/>`).join("")}${mk}<text x="${X(0.5)}" y="${H-5}" font-size="9" text-anchor="middle" fill="${css("--fg3")}">residents, poorest → richest (cumulative share)</text><text transform="rotate(-90)" x="${-Y(0.5)}" y="10" font-size="9" text-anchor="middle" fill="${css("--fg3")}">${H < 120 ? "chargers" : "share of chargers"}</text>${[0,0.5,1].map(p => `<text x="${X(0)-3}" y="${Y(p)+3}" font-size="8" text-anchor="end" fill="${css("--fg3")}">${p*100}%</text>`).join("")}${series.map((sr,i) => `<text x="${X(0.03)}" y="${Y(1) + 12 + 11*i}" font-size="9.5" fill="${css(sr.col)}" font-weight="600">${sr.lab}</text>`).join("")}</svg></div>`; }
function cmProvCurve(pn){ const us = CM.prov[pn]; if (!us || us.length < 3) return null; return {pts: curveJS(us.map(u => u.ch), us.map(u => u.exp), us.map(u => u.pop)), ci: CM.provCI[pn] != null ? CM.provCI[pn] : concJS(us.map(u => u.ch), us.map(u => u.exp), us.map(u => u.pop))}; }
function cmPosIn(pool, u){ const o = [...pool].sort((a,b) => a.exp-b.exp), P = pool.reduce((s,x) => s+x.pop, 0); let cum = 0; for (const x of o){ if (x.id === u.id) return (cum + x.pop/2)/P; cum += x.pop; } return 0.5; }
function cmQ(vals){ const v = vals.filter(x => x != null && !isNaN(x)).sort((a,b) => a-b); return [1,2,3,4,5].map(i => v[Math.min(v.length-1, Math.floor(v.length*i/6))]); }
function cmColor(u, key, cuts){ const SIX = ["--q1","--q2","--q3","--q4","--q5","--q6"], lay = CML.find(l => l[0] === key)[2], v = u[key];
  if (v == null || isNaN(v)) return css("--zero");
  if (lay === "div"){ const t = Math.max(-1, Math.min(1, v/40)); return t < -0.6 ? "#b3261e" : t < -0.2 ? "#e6705f" : t <= 0.2 ? css("--zero") : t <= 0.6 ? "#5fb46f" : "#1d7a33"; }
  if (lay === "div2"){ return v < 0 ? "#2a7fd6" : v < 0.15 ? "#dfe6ee" : v < 0.3 ? "#f3b7ae" : v < 0.45 ? "#e6705f" : "#b3261e"; }
  if (key === "per100k" || key === "kw100k"){ if (!(v > 0)) return css("--zero"); } const i = cuts.findIndex(c => v <= c); const idx = i < 0 ? 5 : i; return css(SIX[lay === "seqr" ? 5-idx : idx]); }
function cmDraw(){ cmInit(); const key = $("cm-layer").value, L = CML.find(l => l[0] === key), G = new Map(CM.GEO); let minx=1e9,miny=1e9,maxx=-1e9,maxy=-1e9; const walk = (c, fn) => typeof c[0] === "number" ? fn(c) : c.forEach(x => walk(x, fn));
  CM.GEO.forEach(([id,g]) => walk(g.coordinates, c => { if (c[0]<minx) minx=c[0]; if (c[0]>maxx) maxx=c[0]; if (c[1]<miny) miny=c[1]; if (c[1]>maxy) maxy=c[1]; }));
  const MW = 1000, k = Math.cos((miny+maxy)/2*Math.PI/180), MH = Math.round(MW*(maxy-miny)/((maxx-minx)*k)), PX = x => (x-minx)/(maxx-minx)*MW, PY = y => (maxy-y)/(maxy-miny)*MH; cmPX = PX; cmPY = PY;
  const cuts = cmQ(CM.units.map(u => u[key]).filter(v => !(key === "per100k" || key === "kw100k") || v > 0));
  const fresh = !cmSvg || !$("cm-map").contains(cmSvg);
  if (fresh){ const box = $("cm-map"); box.innerHTML = ""; cmSvg = el("svg", {viewBox:`0 0 ${MW} ${MH}`, role:"img", "aria-label":"City equity map", "data-w":MW, "data-h":MH}, box); cmVB = [0, 0, MW, MH]; cmPaths = new Map(); cmProvBox = new Map();
    CM.units.forEach(u => { const g = G.get(u.id); if (!g) return; const p = el("path", {d:geomPath(g, PX, PY), fill:css("--zero"), stroke:css("--bg"), "stroke-width":0.5, "data-id":u.id, "vector-effect":"non-scaling-stroke"}, cmSvg); cmPaths.set(u.id, p);
      let bx = cmProvBox.get(u.parent) || [1e9,1e9,-1e9,-1e9]; walk(g.coordinates, c => { const x = PX(c[0]), y = PY(c[1]); if (x<bx[0]) bx[0]=x; if (x>bx[2]) bx[2]=x; if (y<bx[1]) bx[1]=y; if (y>bx[3]) bx[3]=y; }); cmProvBox.set(u.parent, bx);
      p.addEventListener("pointermove", ev => showTip(ev, `<b>${esc(u.name)}</b> · ${esc(u.parent)}${u.metro !== "Outside metro" ? " · " + esc(u.metro) : ""}<br>${fmt(u.pop)} residents · ${u.ch} chargers · ${fmt(u.kw)} kW<br>${fmt(u.per100k,2)} per 100k (rank ${CM.rank.per100k.get(u.id)}/${CM.n}) · ${pct(u.within10,0)} within 10 km<br>spending ${fmt(u.exp)}k · HDI ${u.ipm} · poverty ${u.pov} %<br>equity position <b>${u.eqpos > 0 ? "+" : ""}${fmt(u.eqpos,0)}</b> (supply rank − spending rank)<br><i>click for the equity profile</i>`)); p.addEventListener("pointerleave", hideTip); });
    const hint = document.createElement("div"); hint.className = "tt-hint"; hint.textContent = "scroll = zoom · drag = pan · click = city profile"; box.appendChild(hint);
    const z = document.createElement("div"); z.className = "tt-zoom"; z.innerHTML = `<button type="button" title="zoom in">+</button><button type="button" title="zoom out">−</button><button type="button" title="reset" style="font-size:12px">⟲</button>`; box.appendChild(z);
    const [bi, bo, br] = z.querySelectorAll("button"); bi.onclick = () => cmZoomAt(cmVB[0]+cmVB[2]/2, cmVB[1]+cmVB[3]/2, 1.6); bo.onclick = () => cmZoomAt(cmVB[0]+cmVB[2]/2, cmVB[1]+cmVB[3]/2, 1/1.6); br.onclick = () => { cmSelect(null); $("cm-prov").value = "all"; cmProv("all"); };
    cmSvg.addEventListener("wheel", ev => { ev.preventDefault(); const [cx, cy] = cmPt(ev); cmZoomAt(cx, cy, ev.deltaY < 0 ? 1.3 : 1/1.3); }, {passive:false});
    let drag = null; cmSvg.addEventListener("pointerdown", ev => { drag = {p: cmPt(ev), moved:false, x:ev.clientX, y:ev.clientY, t:ev.target}; cmSvg.setPointerCapture(ev.pointerId); });
    cmSvg.addEventListener("pointermove", ev => { if (!drag) return; if (Math.abs(ev.clientX-drag.x) + Math.abs(ev.clientY-drag.y) > 3) drag.moved = true; if (!drag.moved) return; const [px, py] = cmPt(ev); cmVB[0] -= px - drag.p[0]; cmVB[1] -= py - drag.p[1]; cmApply(); });
    cmSvg.addEventListener("pointerup", () => { if (drag && !drag.moved){ const t = drag.t; if (t && t.dataset && t.dataset.id) cmSelect(t.dataset.id); } drag = null; }); cmSvg.addEventListener("pointercancel", () => { drag = null; }); cmApply(); }
  CM.units.forEach(u => { const p = cmPaths.get(u.id); if (p) p.setAttribute("fill", cmColor(u, key, cuts)); });
  const SIX = ["--q1","--q2","--q3","--q4","--q5","--q6"], f = v => key === "per100k" || key === "kw100k" ? fmt(v,2) : fmt(v,0);
  $("cm-leg").innerHTML = L[2] === "div" ? [["#b3261e","far below income rank (≤ −24)"],["#e6705f","below (−24 … −8)"],[css("--zero"),"in line (±8)"],["#5fb46f","above (+8 … +24)"],["#1d7a33","far above income rank (≥ +24)"]].map(x => `<div class="sw"><i style="background:${x[0]}"></i>${x[1]}</div>`).join("") + `<div style="margin-left:10px">percentile of chargers per resident minus percentile of spending per person; green = served above what its income rank predicts, red = below</div>`
    : L[2] === "div2" ? [["#2a7fd6","pro-poor (CI < 0)"],["#dfe6ee","neutral (0 … 0.15)"],["#f3b7ae","mild pro-rich"],["#e6705f","pro-rich (0.30 … 0.45)"],["#b3261e","strongly pro-rich (≥ 0.45)"]].map(x => `<div class="sw"><i style="background:${x[0]}"></i>${x[1]}</div>`).join("") + `<div class="sw"><i style="background:var(--zero)"></i>&lt; 8 districts</div><div style="margin-left:10px">each district coloured by its province's concentration index of chargers against spending, estimated across the province's districts</div>`
    : SIX.map((c,i) => `<div class="sw"><i style="background:var(${L[2] === "seqr" ? SIX[5-i] : c})"></i>${i === 0 ? "≤ " + f(cuts[0]) : i === 5 ? "> " + f(cuts[4]) : f(cuts[i-1]) + "–" + f(cuts[i])}</div>`).join("") + ((key === "per100k" || key === "kw100k") ? `<div class="sw"><i style="background:var(--zero)"></i>zero</div>` : "") + `<div style="margin-left:10px">${L[1]} · sextiles of 508 districts${L[2] === "seqr" ? " · dark = worse" : " · dark = more"}</div>`;
  $("cm-meta").textContent = `${CM.n} districts · ${Object.keys(CM.pavg).length} provinces · ${Object.values(CM.provCI).length} provinces with a within-province CI`;
  if (cmSel) cmSelect(cmSel, true); else cmSide(); }
function cmApply(){ cmSvg.setAttribute("viewBox", cmVB.join(" ")); }
function cmPt(ev){ const p = cmSvg.createSVGPoint(); p.x = ev.clientX; p.y = ev.clientY; const q = p.matrixTransform(cmSvg.getScreenCTM().inverse()); return [q.x, q.y]; }
function cmZoomAt(cx, cy, f){ const [x, y, w, h] = cmVB, W = +cmSvg.dataset.w, H = +cmSvg.dataset.h; let nw = w/f, nh = h/f; if (nw > W){ nw = W; nh = H; } if (nw < W/60){ nw = W/60; nh = H/60; } const g = nw/w; cmVB = [cx - (cx-x)*g, cy - (cy-y)*g, nw, nh]; cmApply(); }
function cmZoomTo(b, pad=1.3){ const W = +cmSvg.dataset.w, H = +cmSvg.dataset.h, bw = Math.max(b[2]-b[0], 4), bh = Math.max(b[3]-b[1], 4), k = Math.min(W/(bw*pad), H/(bh*pad), 60), w = W/k, h = H/k; cmVB = [(b[0]+b[2])/2 - w/2, (b[1]+b[3])/2 - h/2, w, h]; cmApply(); }
function cmProv(name){ if (!cmSvg) return; cmPaths.forEach((p, id) => { const u = CM.byId.get(id); p.classList.toggle("dim", name !== "all" && u.parent !== name); }); if (name === "all"){ cmVB = [0, 0, +cmSvg.dataset.w, +cmSvg.dataset.h]; cmApply(); } else { const b = cmProvBox.get(name); if (b) cmZoomTo(b); } if (!cmSel) cmSide(name); }
function cmSelect(id, keepView){ cmSel = id; cmPaths.forEach((p, pid) => p.classList.toggle("sel", pid === id)); if (id && cmSvg && !keepView){ const p = cmPaths.get(id); if (p){ const b = p.getBBox(); const u = CM.byId.get(id); const pb = cmProvBox.get(u.parent); cmZoomTo([Math.min(b.x, pb ? pb[0] : b.x), Math.min(b.y, pb ? pb[1] : b.y), Math.max(b.x+b.width, pb ? pb[2] : b.x+b.width), Math.max(b.y+b.height, pb ? pb[3] : b.y+b.height)], 1.15); cmPaths.forEach((q, qid) => q.classList.toggle("dim", CM.byId.get(qid).parent !== u.parent)); } } cmSide(); }
function cmBar(label, v, avg, pavg, f, max){ const w = Math.min(100, 100*v/max), a = Math.min(100, 100*avg/max), pa = pavg == null ? null : Math.min(100, 100*pavg/max); return `<div class="r"><span>${label}</span><div class="bar"><i data-w="${w}"></i><em style="left:${a}%" title="Indonesia ${f(avg)}"></em>${pa == null ? "" : `<b style="left:${pa}%" title="province ${f(pavg)}"></b>`}</div><span><b>${f(v)}</b></span></div>`; }
function cmAnimate(){ requestAnimationFrame(() => $("cm-side").querySelectorAll(".bar i[data-w]").forEach(i => { i.style.width = i.dataset.w + "%"; })); }
function cmScatter(sel, H = 118){ const W = 300, m = {l:30, r:8, t:8, b:22}, pw = W-m.l-m.r, ph = H-m.t-m.b, X = p => m.l + p*pw, Y = p => m.t + (1-p)*ph;
  const dots = CM.units.map(u => { const s = u.id === sel; const col = u.eqpos > 8 ? "#1d7a33" : u.eqpos < -8 ? "#b3261e" : css("--fg3"); return `<circle cx="${X(u.p_exp).toFixed(1)}" cy="${Y(u.p_supply).toFixed(1)}" r="${s ? 5 : 2.2}" fill="${s ? css("--s1") : col}" opacity="${s ? 1 : .55}" stroke="${s ? css("--bg") : "none"}" stroke-width="1.5" data-id="${u.id}"><title>${esc(u.name)} · ${esc(u.parent)}</title></circle>`; }).join("");
  return `<div class="cm-sc" style="height:${H}px"><svg viewBox="0 0 ${W} ${H}"><line x1="${X(0)}" y1="${Y(0)}" x2="${X(1)}" y2="${Y(1)}" stroke="${css("--fg3")}" stroke-dasharray="3 3"/><text x="${X(0.5)}" y="${H-6}" font-size="9" text-anchor="middle" fill="${css("--fg3")}">spending per person · percentile (poorer → richer)</text><text transform="rotate(-90)" x="${-Y(0.5)}" y="10" font-size="9" text-anchor="middle" fill="${css("--fg3")}">chargers per resident · percentile</text>${dots}<text x="${X(0.03)}" y="${Y(0.93)}" font-size="9" fill="#1d7a33">served above income rank</text><text x="${X(0.97)}" y="${Y(0.06)}" font-size="9" text-anchor="end" fill="#b3261e">served below income rank</text></svg></div>`; }
function cmSide(provName){ cmInit(); const side = $("cm-side"), A = CM.avg, u = cmSel ? CM.byId.get(cmSel) : null;
  if (!u){ const pn = provName && provName !== "all" ? provName : null, pool = pn ? CM.units.filter(x => x.parent === pn) : CM.units, top = [...pool].sort((a,b) => b.eqpos - a.eqpos).slice(0,4), bot = [...pool].sort((a,b) => a.eqpos - b.eqpos).slice(0,4), pci = pn ? CM.provCI[pn] : null;
    const over = CM.units.filter(x => x.eqpos >= 24).length, under = CM.units.filter(x => x.eqpos <= -24).length, inl = CM.units.filter(x => Math.abs(x.eqpos) <= 8).length;
    const ins = pn ? cmInsights(pool, pn) : CM.insights, pc = pn ? cmProvCurve(pn) : null;
    const curve = cmCurve([{pts: CM.curveAll, col:"--fg3", lab:`Indonesia · CI ${sgn(CM.ciAll)}`, w:1.6, dash:"4 3"}].concat(pc ? [{pts: pc.pts, col:"--s1", lab:`${esc(pn)} · CI ${sgn(pc.ci)}`}] : []), null);
    side.innerHTML = `<div class="cm-tiles"><div class="t"><div class="v" style="color:#1d7a33">${over}</div><div class="l">districts served far above their income rank</div></div><div class="t"><div class="v">${inl}</div><div class="l">in line with income rank (±8)</div></div><div class="t"><div class="v" style="color:#b3261e">${under}</div><div class="l">served far below their income rank</div></div></div>
      <div class="tt-seg">${[["insights","Insights from the map"],["curve","Equity curve"],["lists","Top & bottom"]].map(v => `<button type="button" data-v="${v[0]}" aria-pressed="${cmView === v[0]}">${v[1]}</button>`).join("")}</div>
      ${cmView === "insights" ? `<ol class="tt-ins">${ins.map(t => `<li>${t}</li>`).join("")}</ol>`
        : cmView === "curve" ? `${curve}<div class="note">Concentration curve: districts sorted from poorest to richest; the curve shows what share of chargers the poorest x % of residents hold. Below the diagonal = chargers sit with the richer districts. ${pn && pc ? `${esc(pn)} is ${pc.ci > CM.ciAll + 0.05 ? "more pro-rich than Indonesia" : pc.ci < CM.ciAll - 0.05 ? "less pro-rich than Indonesia" : "about as pro-rich as Indonesia"}.` : "Pick a province to overlay its own curve."}</div>`
        : `${cmScatter(null, 92)}<div class="cm-list"><h4>${pn ? esc(pn) + " · most above income rank" : "Most above income rank"}</h4>${top.map(x => `<div data-id="${x.id}"><span>${esc(x.name)}</span><b style="color:#1d7a33">+${fmt(x.eqpos,0)}</b></div>`).join("")}<h4>${pn ? esc(pn) + " · most below income rank" : "Most below income rank"}</h4>${bot.map(x => `<div data-id="${x.id}"><span>${esc(x.name)}</span><b style="color:#b3261e">${fmt(x.eqpos,0)}</b></div>`).join("")}</div>`}
      ${pn && pci != null && cmView !== "curve" ? `<div class="note">${esc(pn)}: within-province CI chargers ~ spending <b>${sgn(pci)}</b> across ${CM.pavg[pn].n} districts · ${fmt(CM.pavg[pn].per100k,2)} per 100k (Indonesia ${fmt(A.per100k,2)}).</div>` : ""}`;
    side.querySelectorAll(".tt-seg button").forEach(b => b.addEventListener("click", () => { cmView = b.dataset.v; cmSide(provName); }));
    side.querySelectorAll(".cm-list div[data-id]").forEach(d => d.addEventListener("click", () => cmSelect(d.dataset.id))); side.querySelectorAll(".cm-sc circle").forEach(c => c.addEventListener("click", () => cmSelect(c.dataset.id)));
    $("cm-take").innerHTML = `<b>Equity position = where a district ranks on chargers per resident minus where it ranks on spending per person.</b> ${over} districts sit far above their income rank (served better than their wealth predicts), ${under} far below. The diagonal in the scatter is "supply follows income exactly"; the thesis question is who sits off it. Click a district, pick a province, or type a name.`; return; }
  const pv = CM.pavg[u.parent], rS = CM.rank.per100k.get(u.id), rW = CM.rank.within10.get(u.id), rE = CM.rank.eqpos.get(u.id), pos = u.eqpos, posCls = pos >= 24 ? "far above" : pos >= 8 ? "above" : pos <= -24 ? "far below" : pos <= -8 ? "below" : "in line with";
  const vsPeer = u.peer_per100k > 0 ? u.per100k/u.peer_per100k : null, gauge = Math.max(2, Math.min(98, 50 + pos/2));
  let read = `<p><b>${esc(u.name)} is served ${posCls} its income rank.</b> It sits at the ${fmt(100*u.p_exp,0)}th percentile of spending but the ${fmt(100*u.p_supply,0)}th percentile of chargers per resident (${fmt(u.per100k,2)} per 100,000, rank ${rS} of ${CM.n}${u.ch === 0 ? ", no public charger at all" : ""}). ${vsPeer != null ? `Its ${u.peer_n} income peers average ${fmt(u.peer_per100k,2)} per 100,000; it has ${vsPeer >= 1 ? fmt(vsPeer,1) + "× that" : fmt(100*vsPeer,0) + " % of that"}.` : ""}</p>`;
  read += `<p>${pct(u.beyond25,0)} of residents live beyond 25 km of any charger${u.kw100k > 0 ? `; ${u.dc ? u.dc + " DC fast charger" + (u.dc > 1 ? "s" : "") : "no DC fast charger"}` : ""}.</p>`;
  const posIn = cmPosIn(CM.prov[u.parent], u);
  read += `<p><b>Reading.</b> On ${esc(u.parent)}'s curve it sits at the ${fmt(100*posIn,0)}th percentile of residents by spending. ${pos <= -8 ? (u.p_exp >= 0.5 ? "A relatively affluent district with thin supply: the gap here is not about ability to pay but about where operators have chosen to build — a placement decision, not an income story." : "Poor and under-served: the double disadvantage the vertical-equity test is designed to catch. Counted by chargers per resident it looks merely sparse; counted against need it is the bottom of the ladder.") : pos >= 8 ? (u.p_exp >= 0.5 ? "Affluent and well served: supply follows income here, which is exactly the pro-rich pattern the national CI (+0.469) summarises." : "Served above what its income predicts — a counter-example to the national gradient worth examining: corridor chargers, a provincial capital, or a tourism node usually explain it.") : "Supply is roughly what its income rank predicts: this district is on the national gradient, neither a success nor a gap case."}${u.provci != null ? ` Inside ${esc(u.parent)} the tilt of chargers towards richer districts is ${sgn(u.provci)} (${u.provci >= 0.3 ? "strongly pro-rich" : u.provci >= 0.15 ? "pro-rich" : u.provci >= 0 ? "near neutral" : "pro-poor"}).` : ""}</p>`;
  const mx = Math.max(u.per100k, A.per100k, pv.per100k, 0.01)*1.1, mk = Math.max(u.kw100k, A.kw100k, pv.kw100k, 1)*1.1;
  side.innerHTML = `<div class="tt-card"><h3>${esc(u.name)}</h3><div class="sub">${esc(u.parent)}${u.metro !== "Outside metro" ? " · " + esc(u.metro) : ""} · ${u.kota ? "kota" : "kabupaten"} · ${fmt(u.pop/1e6,2)} M residents · ${u.ch} chargers, ${u.sites} sites</div>
    <div class="cm-tiles"><div class="t"><div class="v">${fmt(u.per100k,2)}</div><div class="l">per 100,000 · rank ${rS}/${CM.n}</div></div><div class="t"><div class="v">${pct(u.within10,0)}</div><div class="l">within 10 km · rank ${rW}</div></div><div class="t"><div class="v" style="color:${pos >= 8 ? "#1d7a33" : pos <= -8 ? "#b3261e" : "inherit"}">${pos > 0 ? "+" : ""}${fmt(pos,0)}</div><div class="l">equity position · rank ${rE}</div></div></div>
    <div class="cm-cmp">${cmBar("chargers / 100k", u.per100k, A.per100k, pv.per100k, v => fmt(v,2), mx)}${cmBar("kW / 100k", u.kw100k, A.kw100k, pv.kw100k, v => fmt(v,0), mk)}${cmBar("within 10 km", u.within10, A.within10, pv.within10, v => pct(v,0), 100)}<div style="margin-top:1px">bar = this district · <span style="color:var(--s2)">|</span> Indonesia · <span style="color:var(--fg)">|</span> ${esc(u.parent)}</div></div>
    <div class="tt-seg" style="margin:0">${[["curve","Equity curve"],["scatter","All 508 districts"]].map(v => `<button type="button" data-v="${v[0]}" aria-pressed="${cmCityView === v[0]}">${v[1]}</button>`).join("")}</div>
    ${cmCityView === "scatter" ? cmScatter(u.id, 96) : (() => { const pc = cmProvCurve(u.parent); return pc ? cmCurve([{pts: pc.pts, col:"--s1", lab:`${esc(u.parent)} · CI ${sgn(pc.ci)}`}, {pts: CM.curveAll, col:"--fg3", lab:`Indonesia · CI ${sgn(CM.ciAll)}`, w:1.4, dash:"4 3"}], {x: cmPosIn(CM.prov[u.parent], u), name: u.name}, 100) : `<div class="note">${esc(u.parent)} has too few districts for a curve.</div>`; })()}
    <div class="cm-read">${read}</div></div>`;
  side.querySelectorAll(".tt-seg button").forEach(b => b.addEventListener("click", () => { cmCityView = b.dataset.v; cmSide(); }));
  side.querySelectorAll(".cm-sc circle").forEach(c => c.addEventListener("click", () => cmSelect(c.dataset.id))); cmAnimate(); requestAnimationFrame(() => { const g = side.querySelector(".cm-gauge i"); if (g) g.style.left = g.dataset.l + "%"; });
  $("cm-take").innerHTML = `<b>${esc(u.name)}: ${fmt(u.per100k,2)} chargers per 100,000 (rank ${rS} of ${CM.n}), ${pct(u.within10,0)} within 10 km, served ${posCls} its income rank (${pos > 0 ? "+" : ""}${fmt(pos,0)}).</b> ${vsPeer != null ? `Income peers average ${fmt(u.peer_per100k,2)} per 100,000. ` : ""}Press ⟲ or pick "All Indonesia" to return.`; }
function cities(){ cmInit(); $("cm-note").innerHTML = `<b>Purpose · the national comparison (RQ4).</b> All ${CM.n} districts (kabupaten/kota) on one map, always national. Default layer <b>equity position</b> = percentile rank on chargers per resident minus percentile rank on spending per person: 0 = supply matches what income predicts, red = below, green = above. Other layers: supply, reach, capacity, and the province's own pro-rich tilt (within-province CI). Scroll to zoom, drag to pan, click a district for its profile.`; if (CUR_CH === "cities") cmDraw(); }
function chapters(){ const nav = $("chapters"); if (!nav.children.length){ nav.innerHTML = CH.map((c,i) => `<button type="button" data-ch="${c[0]}" aria-pressed="false"><span class="k">${String(i).padStart(2,"0")}</span><span><b>${c[1]}</b><small>${c[2]}</small></span></button>`).join(""); nav.querySelectorAll("button").forEach(b => b.addEventListener("click", () => showChapter(b.dataset.ch))); $("prev").addEventListener("click", () => step(-1)); $("next").addEventListener("click", () => step(1)); } }
function step(d){ const i = CH.findIndex(c => c[0] === CUR_CH); const j = Math.min(CH.length-1, Math.max(0, i + d)); showChapter(CH[j][0]); }
document.addEventListener("keydown", e => { if (e.target.tagName === "SELECT") return; if (e.key === "ArrowRight") step(1); if (e.key === "ArrowLeft") step(-1); });
function showChapter(ch){ CUR_CH = ch; const c = CH.find(x => x[0] === ch); document.querySelectorAll("section.ch").forEach(s => s.classList.toggle("active", s.dataset.ch === ch)); document.querySelectorAll("#chapters button").forEach(b => b.setAttribute("aria-pressed", b.dataset.ch === ch));
  const i = CH.indexOf(c); $("prev").disabled = i === 0; $("next").disabled = i === CH.length-1; $("pager-pos").textContent = `${i+1} / ${CH.length}`; history.replaceState(null, "", `#${S}/${ch}`);
  document.querySelectorAll("section.ch").forEach(s => { const n = s.querySelector("h2 .n"), j = CH.findIndex(x => x[0] === s.dataset.ch); if (n && j >= 0) n.textContent = String(j).padStart(2,"0"); });
  if (ch === "cities"){ cmDraw(); $("eyebrow").textContent = `City equity map · Indonesia · ${fmt(ALL.national.meta.chargers)} chargers · 508 districts in 34 provinces · ${fmt(ALL.national.meta.pop/1e6,1)} million residents · June 2026`; }
  else if (ch === "travel"){ ttLoad(); $("eyebrow").textContent = `Travel-time pilot · ${fmt(TT.n_villages)} villages · ${TT.kabs.length} districts (West Java 27 · Jakarta 5, Kepulauan Seribu excluded · Tangerang 3) · ${fmt(TT.pop/1e6,1)} million residents`; } else hero(); }

// ---------- render all
function renderAll(scope){ load(scope); hero(); waffles(); stairs(); gap(); evidence(); renderMap(); travel(); cities(); forest(); curveInit(); quintInit(); theil(); rest(); chapters(); showChapter(CUR_CH); }
document.querySelectorAll(".seg button").forEach(b => b.addEventListener("click", () => { if (b.dataset.s !== S) renderAll(b.dataset.s); }));
$("layer").addEventListener("change", renderMap); $("gap-metric").addEventListener("change", gap); $("cv-rank").addEventListener("change", drawCurve); $("cv-out").addEventListener("change", drawCurve); $("q-rank").addEventListener("change", drawQuint);
{ const h = location.hash.slice(1).split("/"); if (h[1] && CH.some(c => c[0] === h[1])) CUR_CH = h[1]; renderAll(h[0] === "jabar" ? "jabar" : "national"); }
</script></body></html>
"""
_tt = json.load(open("ttm/ttm.json", encoding="utf-8"))["summary"]
assert _tt["mode"] == "ttm", "ttm/ttm.json must be in travel-time mode (run ttm/compute.py with the r5r matrix)"
TT = dict(reach=_tt["reach"], ladder=_tt["ladder"], e2sfca=_tt["e2sfca"], n_villages=_tt["n_villages"], pop=_tt["pop"], rows=_tt["rows"],
          metros=[{k: m.get(k) for k in ("key", "label", "pop", "share1", "share2", "reach7", "reach15", "suff10")} for m in _tt["metros"]],
          quintiles=[{k: q.get(k) for k in ("q", "share1", "share2", "reach7", "reach15", "suff10")} for q in _tt.get("quintiles_expend", [])] or None)
for m in TT["metros"]: m["label"] = {"Luar metropolitan": "Outside the metros"}.get(m["label"], m["label"])
_kabs = [r for r in json.load(open("ttm/ttm.json", encoding="utf-8"))["kabs"] if r["n"] >= 5 and not r["name"].startswith("Waduk")]   # drop the Cirata reservoir pseudo-district (1 polygon)
TT["kabs"] = [{k: r.get(k) for k in ("code", "name", "prov", "metro", "n", "pop", "chargers", "sites", "per100k", "share1", "share2", "median", "reach7", "reach15", "suff10", "gini_far", "ipm", "expend", "p0")} for r in _kabs]
_P = sum(r["pop"] for r in _kabs); _unr = sorted(_kabs, key=lambda r: -r["pop"] * (1 - r["share1"]))
_unr_tot = sum(r["pop"] * (1 - r["share1"]) for r in _kabs)
_gap = sorted([r for r in _kabs if r["pop"] > 500000], key=lambda r: -(r["share2"] - r["share1"]))
_top = sorted(_kabs, key=lambda r: -r["share1"]); _bot = sorted(_kabs, key=lambda r: r["share1"])
import numpy as _np
from scipy.stats import spearmanr as _sp
_rho7 = _sp([r["share1"] for r in _kabs], [r["reach7"] for r in _kabs]).correlation; _rho15 = _sp([r["share1"] for r in _kabs], [r["reach15"] for r in _kabs]).correlation
_mj = next(m for m in _tt["metros"] if m["key"] == "jabodetabek"); _ml = next(m for m in _tt["metros"] if m["key"] == "luar")
_p = lambda x, d=0: ("{:.%df} %%" % d).format(100 * x)
_M = lambda x: "%.1f M" % (x / 1e6)
TT["insights"] = [
  "<b>Where the unreached live.</b> %s residents are more than 10 minutes from any village with a charger. Five districts hold %s of them: %s." % (
      _M(_unr_tot), _p(sum(r["pop"] * (1 - r["share1"]) for r in _unr[:5]) / _unr_tot), ", ".join("%s (%s)" % (r["name"], _M(r["pop"] * (1 - r["share1"]))) for r in _unr[:5])),
  "<b>A metro cliff, not a gradient.</b> Jabodetabek %s and Bandung Raya %s of residents within 10 minutes, Cirebon Raya %s, everywhere else %s. Bottom of the table: %s." % (
      _p(_mj["share1"]), _p(next(m for m in _tt["metros"] if m["key"] == "bandung")["share1"]), _p(next(m for m in _tt["metros"] if m["key"] == "cirebon")["share1"]), _p(_ml["share1"]),
      ", ".join("%s %s" % (r["name"], _p(r["share1"])) for r in _bot[:3])),
  "<b>The threshold moves the level, not the order.</b> District ranking at 10 minutes correlates ρ = %.2f with the ranking at 7 and %.2f at 15: whichever threshold is preferred, the same places sit at the bottom." % (_rho7, _rho15),
  "<b>Reach at district scale is not reach at neighbourhood scale.</b> %s: most residents are within 30 minutes of a charger village but far fewer within 10. The network exists at the regency level; the last ten minutes are missing." % (
      "; ".join("%s %s → %s" % (r["name"], _p(r["share2"]), _p(r["share1"])) for r in _gap[:3])),
  "<b>Capacity is a separate rung.</b> Only %s of residents sit in villages with ≥ 0.03 kW per household within 10 minutes (highest: %s). Reach can be solved while capacity is not; the two are reported apart." % (
      _p(_tt["ladder"]["rungs"][2]["share"], 1), ", ".join("%s %s" % (r["name"], _p(r["suff10"], 1)) for r in sorted(_kabs, key=lambda r: -r["suff10"])[:3])),
]
TT["avg"] = dict(share1=_tt["reach"]["10"]["share"], reach7=_tt["reach"]["7"]["share"], reach15=_tt["reach"]["15"]["share"], share2=_tt["reach"]["30"]["share"], suff10=_tt["ladder"]["rungs"][2]["share"], per100k=round(1e5 * _tt["chargers"] / _tt["pop"], 2))
html = TEMPLATE.replace("__ALL__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))).replace("__GEO__", json.dumps(GEO, ensure_ascii=False, separators=(",", ":"))).replace("__TT__", json.dumps(TT, separators=(",", ":")))
open("analysis/charging_equity_en.html", "w", encoding="utf-8").write(html)
print("analysis/charging_equity_en.html %.0f KB" % (len(html.encode()) / 1024))
