"""Dasbor interaktif indeks konsentrasi SPKLU Jawa Barat — semua ukuran dihitung ulang di browser.

    python3 analysis/concentration_dashboard_render.py   -> analysis/concentration_dashboard.html

Kendali: pilih wilayah (kab/kota tunggal, gabungan, atau preset kawasan), slider ambang penduduk kecamatan,
variabel peringkat dan pasokan, dan slider skenario "tambah N charger" dengan tiga aturan penempatan
(kesetaraan: kecamatan dengan charger/kapita terendah dulu; permintaan: pemilik EV per charger tertinggi dulu;
pro-miskin: pengeluaran kab terendah dulu). Data per kecamatan dari data/jabar_kecamatan_spklu.geojson
(dibuat scripts/concentration_kecamatan_jabar.py).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(HERE))
G = json.load(open("data/jabar_kecamatan_spklu.geojson", encoding="utf-8"))

TEMPLATE = r"""<title>Dasbor Konsentrasi SPKLU Jabar</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700&family=Source+Sans+3:wght@400;600&display=swap">
<style>
/* Tata letak dasbor: panel kendali lengket di kiri (280px), kanvas hasil di kanan; di ponsel kendali di atas. */
:root{
  --bg:#fcfcfb; --fg:#0b0b0b; --fg2:#52514e; --fg3:#7d7b75; --line:#e4e2dc; --panel:#f4f3ef; --grid:#ebe9e3; --chip:#e9e7e1;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --zero:#d9d7d0; --hatch:#bdbab2;
  --q1:#cde2fb; --q2:#9ec5f4; --q3:#5598e7; --q4:#256abf; --q5:#104281;
  --display:"Archivo",system-ui,sans-serif; --body:"Source Sans 3",system-ui,sans-serif;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#1a1a19; --fg:#ffffff; --fg2:#c3c2b7; --fg3:#8f8d85; --line:#34332f; --panel:#232321; --grid:#2c2b28; --chip:#2e2d2a;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --zero:#3a3936; --hatch:#5a5853;
  --q1:#184f95; --q2:#256abf; --q3:#3987e5; --q4:#6da7ec; --q5:#b7d3f6; color-scheme:dark } }
:root[data-theme="dark"]{
  --bg:#1a1a19; --fg:#ffffff; --fg2:#c3c2b7; --fg3:#8f8d85; --line:#34332f; --panel:#232321; --grid:#2c2b28; --chip:#2e2d2a;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --zero:#3a3936; --hatch:#5a5853;
  --q1:#184f95; --q2:#256abf; --q3:#3987e5; --q4:#6da7ec; --q5:#b7d3f6; color-scheme:dark }
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.45;margin:0;padding-block:20px 48px;padding-inline:clamp(16px,3vw,32px)}
h1,h2,h3{font-family:var(--display);text-wrap:balance;margin:0}
h1{font-size:clamp(22px,3vw,30px);line-height:1.1}
h2{font-size:17px;margin:0 0 8px}
h3{font-size:13px;color:var(--fg2);font-weight:600;letter-spacing:.04em;text-transform:uppercase;margin:0 0 6px}
.top{display:flex;flex-wrap:wrap;gap:6px 18px;align-items:baseline;margin-bottom:14px}
.top .sub{color:var(--fg2);font-size:14px}
.grid{display:grid;grid-template-columns:280px minmax(0,1fr);gap:18px;align-items:start}
@media (max-width:900px){.grid{grid-template-columns:1fr}.side{position:static}}
.side{position:sticky;top:env(safe-area-inset-top,0px);display:flex;flex-direction:column;gap:14px;max-height:calc(100vh - 24px);overflow:auto;padding-right:2px}
.card{background:var(--panel);border-radius:6px;padding:12px 14px;min-width:0}
.chips{display:flex;flex-wrap:wrap;gap:5px}
.chip{font:inherit;font-size:13px;padding:3px 9px;border-radius:999px;border:1px solid transparent;background:var(--chip);color:var(--fg);cursor:pointer}
.chip[aria-pressed="true"]{background:var(--s1);color:#fff;border-color:var(--s1)}
.chip.preset{background:transparent;border-color:var(--line)}
.chip.preset[aria-pressed="true"]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
button:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
label.row{display:flex;flex-direction:column;gap:3px;font-size:13px;color:var(--fg2);margin-top:8px}
label.row span b{color:var(--fg);font-variant-numeric:tabular-nums}
input[type=range]{width:100%;accent-color:var(--s1)}
select{font:inherit;font-size:14px;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:4px 8px;width:100%}
.btn{font:inherit;font-size:13px;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:4px 10px;cursor:pointer}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
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
.tip{position:fixed;pointer-events:none;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:4px;padding:6px 9px;font-size:13px;line-height:1.35;box-shadow:0 2px 10px rgba(0,0,0,.12);max-width:260px;z-index:9;font-variant-numeric:tabular-nums}
table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
th,td{padding:5px 7px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){text-align:left}
th{font-weight:600;color:var(--fg2);font-size:12px;cursor:pointer;user-select:none}
th[aria-sort]{color:var(--fg)}
.scroll{overflow-x:auto}
.note{font-size:13px;color:var(--fg2);margin:6px 0 0}
.plus{color:var(--s2);font-weight:600}
.ctrls{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;font-size:13px;color:var(--fg2);margin-bottom:6px}
.ctrls select{width:auto}
details.method{font-size:13px;color:var(--fg2)}
details.method summary{cursor:pointer;color:var(--fg)}
@media (prefers-reduced-motion:no-preference){path.kec{transition:fill .15s}}
</style>

<div class="top"><h1>Dasbor Konsentrasi SPKLU Jabar</h1><span class="sub">Maret 2026 · 629 kecamatan · 636 charger · dihitung ulang di browser tiap kendali digeser · <a href="concentration_dashboard_en.html">English version</a></span></div>
<div class="grid">
<aside class="side">
  <div class="card">
    <h3>Wilayah</h3>
    <div class="chips" id="presets"></div>
    <div class="chips" id="kabs" style="margin-top:8px"></div>
    <div class="note" id="region-sum"></div>
  </div>
  <div class="card">
    <h3>Ukuran</h3>
    <label class="row"><span>Diurut menurut (rendah → tinggi)</span><select id="rank">
      <option value="exp">Pengeluaran per kapita kab/kota (BPS 2024)</option><option value="ipm">IPM kab/kota (BPS 2024)</option>
      <option value="npov">Kemiskinan kab/kota, dibalik (miskin → kaya)</option><option value="dens">Kepadatan penduduk kecamatan</option><option value="ev100k">Pemilik EV per 100 rb kecamatan</option></select></label>
    <label class="row"><span>Pasokan yang diukur</span><select id="outcome">
      <option value="ch">Jumlah charger</option><option value="kw">Kapasitas (kW)</option><option value="kwh">Energi terjual Mar-2026 (kWh)</option><option value="trx">Transaksi Mar-2026</option></select></label>
    <label class="row"><span>Kecamatan dihitung bila penduduk ≥ <b id="minpop-v">500</b></span><input type="range" id="minpop" min="0" max="50000" step="500" value="500"></label>
  </div>
  <div class="card">
    <h3>Skenario tambah charger</h3>
    <label class="row"><span>Tambah <b id="n-v">0</b> charger baru di wilayah terpilih</span><input type="range" id="nnew" min="0" max="500" step="5" value="0"></label>
    <label class="row"><span>Aturan penempatan</span><select id="rule">
      <option value="equal">Kesetaraan: charger/kapita terendah dulu</option><option value="demand">Permintaan: pemilik EV per charger tertinggi dulu</option><option value="poor">Pro-miskin: pengeluaran kab terendah dulu</option></select></label>
    <p class="note">Satu charger baru dihitung 50 kW. Skenario hanya mengubah jumlah charger dan kW; energi dan transaksi tetap data Maret 2026.</p>
    <button class="btn" id="reset" type="button" style="margin-top:8px">Atur ulang semua</button>
  </div>
</aside>

<div class="main">
  <div class="kpis" id="kpis"></div>
  <div class="two">
    <div class="card">
      <h2>Peta kecamatan</h2>
      <div class="ctrls"><span>Lapisan</span><select id="layer"><option value="ch100k">Charger per 100 rb (dengan skenario)</option><option value="kwhpc">kWh per kapita</option><option value="ev100k">Pemilik EV per 100 rb</option><option value="dens">Kepadatan</option><option value="exp">Pengeluaran kab/kota</option></select></div>
      <div id="map"></div><div class="mapleg" id="mapleg"></div>
      <div class="legend"><span><i class="box" style="background:transparent;border:2px solid var(--s2);height:8px;width:10px"></i>kecamatan yang menerima charger baru</span></div>
    </div>
    <div class="card">
      <h2>Kurva konsentrasi</h2>
      <div id="curve"></div>
      <div class="legend"><span><i style="background:var(--s1)"></i>Data Maret 2026</span><span><i style="background:var(--s2)"></i>Dengan skenario</span><span><i style="background:var(--fg3);height:1px"></i>Kesetaraan</span></div>
    </div>
  </div>
  <div class="card">
    <h2>Perbandingan antar kab/kota di wilayah terpilih</h2>
    <p class="note">CI tiap kab/kota dihitung di dalam kab itu sendiri (kecamatan diurut menurut variabel terpilih), hanya untuk kab/kota dengan ≥ 6 kecamatan dan ≥ 3 charger. Klik batang untuk memfokuskan wilayah.</p>
    <div id="bars"></div>
  </div>
  <div class="card">
    <h2>Kecamatan</h2>
    <p class="note" id="tbl-note"></p>
    <div class="scroll" id="table"></div>
  </div>
  <details class="method"><summary>Metode dan sumber</summary>
    <p>CI = 2·cov<sub>w</sub>(pasokan per kapita, peringkat fraksional tertimbang penduduk) / rata-rata tertimbang; identik dengan 1 − 2∫L(p)dp pada kurva. Selang 95 % = bootstrap 300 ulangan atas kecamatan (dihitung ulang setelah kendali berhenti bergerak). HHI atas porsi charger antar kecamatan (0–10.000). Penduduk Kontur 2023 H3 res 8; batas kecamatan dari desa HDX-BPS 2020; IPM, pengeluaran per kapita disesuaikan dan P0 BPS 2024 per kab/kota, diwariskan ke kecamatannya karena tidak ada angka resmi per kecamatan. SPKLU: Master Maret 2026 (charger, kW), rekap transaksi Maret 2026 (kWh, transaksi), pengajuan home-charger PLN status Selesai sebagai lokasi pemilik EV.</p>
  </details>
</div>
</div>
<div class="tip" id="tip" hidden></div>

<script>
const GEO = __GEO__;
const NS = "http://www.w3.org/2000/svg";
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const fmt = (x, d=0) => (x ?? 0).toLocaleString("id-ID", {minimumFractionDigits:d, maximumFractionDigits:d});
const sgn = x => isNaN(x) ? "–" : (x>0?"+":"") + x.toFixed(3).replace(".", ",");
const el = (t, a={}, parent) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (parent) parent.appendChild(e); return e; };
const tip = document.getElementById("tip");
function showTip(ev, html){ tip.innerHTML = html; tip.hidden = false; const w = tip.offsetWidth, h = tip.offsetHeight; tip.style.left = Math.min(ev.clientX + 14, innerWidth - w - 8) + "px"; tip.style.top = (ev.clientY + 16 + h > innerHeight ? ev.clientY - h - 10 : ev.clientY + 16) + "px"; }
const hideTip = () => tip.hidden = true;

// ---------- data
const F = GEO.features.map((f, i) => ({ i, g: f.geometry, ...f.properties, npov: -f.properties.pov, ev100k: f.properties.pop ? 1e5*f.properties.ev/f.properties.pop : 0 }));
const KABS = [...new Set(F.map(f => f.kab))].sort((a,b) => a.localeCompare(b));
const PRESETS = { "Semua Jabar": [], "Jabodetabek-Jabar": ["Bogor","Kota Bogor","Kota Depok","Bekasi","Kota Bekasi"], "Bandung Raya": ["Kota Bandung","Kota Cimahi","Bandung","Bandung Barat","Sumedang"],
  "Purwasuka": ["Purwakarta","Subang","Karawang"], "Cirebon Raya": ["Kota Cirebon","Cirebon","Indramayu","Majalengka","Kuningan"], "Priangan Timur": ["Garut","Tasikmalaya","Kota Tasikmalaya","Ciamis","Kota Banjar","Pangandaran"], "Sukabumi–Cianjur": ["Sukabumi","Kota Sukabumi","Cianjur"] };
const RANKLAB = {exp:"pengeluaran per kapita kab/kota", ipm:"IPM kab/kota", npov:"kemiskinan kab/kota (dibalik)", dens:"kepadatan kecamatan", ev100k:"pemilik EV per 100 rb"};
const OUTLAB = {ch:"charger", kw:"kW", kwh:"kWh", trx:"transaksi"};

// ---------- state
const S = { regions: new Set(), rank: "exp", outcome: "ch", minpop: 500, n: 0, rule: "equal", layer: "ch100k", sortKey: "pop", sortDir: -1 };
try { Object.assign(S, JSON.parse(localStorage.getItem("spklu-dash") || "{}"), { regions: new Set(JSON.parse(localStorage.getItem("spklu-dash-regions") || "[]")) }); } catch (e) {}
function save(){ try { localStorage.setItem("spklu-dash", JSON.stringify({rank:S.rank, outcome:S.outcome, minpop:S.minpop, n:S.n, rule:S.rule, layer:S.layer})); localStorage.setItem("spklu-dash-regions", JSON.stringify([...S.regions])); } catch (e) {} }

// ---------- alat ukur
function wranks(r, w){ const n = r.length, o = [...Array(n).keys()].sort((a,b) => r[a]-r[b]); const W = w.reduce((s,x) => s+x, 0); const out = new Array(n); let cum = 0, i = 0;
  while (i < n){ let j = i, sw = 0; while (j+1 < n && r[o[j+1]] === r[o[i]]) j++; for (let k = i; k <= j; k++) sw += w[o[k]]; const mid = (cum + sw/2) / W; for (let k = i; k <= j; k++) out[o[k]] = mid; cum += sw; i = j+1; } return out; }
function ci(h, r, w){ const W = w.reduce((s,x) => s+x, 0), H = h.reduce((s,x) => s+x, 0); if (H <= 0 || W <= 0) return NaN; const R = wranks(r, w); const mu = H / W; let mR = 0; for (let i = 0; i < w.length; i++) mR += w[i]*R[i]; mR /= W; let cov = 0; for (let i = 0; i < w.length; i++) cov += w[i] * (h[i]/w[i] - mu) * (R[i] - mR); return 2 * (cov / W) / mu; }
function boot(h, r, w, reps=300){ const n = h.length, out = []; let seed = 2026; const rnd = () => (seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296;
  for (let b = 0; b < reps; b++){ const hh = [], rr = [], ww = []; for (let i = 0; i < n; i++){ const j = Math.floor(rnd()*n); hh.push(h[j]); rr.push(r[j]); ww.push(w[j]); } const c = ci(hh, rr, ww); if (!isNaN(c)) out.push(c); }
  out.sort((a,b) => a-b); return out.length ? [out[Math.floor(out.length*0.025)], out[Math.floor(out.length*0.975)]] : [NaN, NaN]; }
function curve(h, r, w){ const o = [...Array(h.length).keys()].sort((a,b) => r[a]-r[b]); const W = w.reduce((s,x) => s+x, 0), H = h.reduce((s,x) => s+x, 0) || 1; const pts = [[0,0]]; let cw = 0, ch = 0; for (const i of o){ cw += w[i]; ch += h[i]; pts.push([cw/W, ch/H]); } return pts; }
function gini(v){ const s = [...v].sort((a,b) => a-b), n = s.length, T = s.reduce((a,b) => a+b, 0); if (!n || !T) return NaN; let acc = 0; for (let i = 0; i < n; i++) acc += (i+1)*s[i]; return 2*acc/(n*T) - (n+1)/n; }
function hhi(v){ const T = v.reduce((a,b) => a+b, 0); if (!T) return NaN; return v.reduce((s,x) => s + (x/T)**2, 0) * 10000; }

// ---------- skenario
function scenario(sub){ const add = new Array(sub.length).fill(0); let n = S.n; if (!n) return add;
  const key = S.rule === "equal" ? i => (sub[i].ch + add[i]) / sub[i].pop : S.rule === "demand" ? i => -(sub[i].ev) / (sub[i].ch + add[i] + 1) : i => sub[i].exp * 1e3 + (sub[i].ch + add[i]) / sub[i].pop * 1e6;
  while (n-- > 0){ let best = -1, bv = Infinity; for (let i = 0; i < sub.length; i++){ const v = key(i); if (v < bv){ bv = v; best = i; } } if (best < 0) break; add[best]++; } return add; }

// ---------- hitung
let CUR = null, bootTimer = null;
function compute(){
  const inR = f => !S.regions.size || S.regions.has(f.kab);
  const sub = F.filter(f => inR(f) && f.pop >= S.minpop);
  const add = scenario(sub);
  const w = sub.map(f => f.pop), r = sub.map(f => f[S.rank]);
  const h0 = sub.map(f => f[S.outcome]); const h1 = sub.map((f, i) => S.outcome === "ch" ? f.ch + add[i] : S.outcome === "kw" ? f.kw + 50*add[i] : f[S.outcome]);
  const ch0 = sub.map(f => f.ch), ch1 = sub.map((f, i) => f.ch + add[i]);
  const P = w.reduce((s,x) => s+x, 0);
  const cov = c => w.reduce((s, x, i) => s + (c[i] > 0 ? x : 0), 0) / P * 100;
  CUR = { sub, add, w, r, h0, h1, ci0: ci(h0, r, w), ci1: ci(h1, r, w), cov0: cov(ch0), cov1: cov(ch1), per0: 1e5*ch0.reduce((a,b) => a+b, 0)/P, per1: 1e5*ch1.reduce((a,b) => a+b, 0)/P,
          gini0: gini(ch0.map((c,i) => c/w[i])), gini1: gini(ch1.map((c,i) => c/w[i])), hhi0: hhi(ch0), hhi1: hhi(ch1), P, lo0: NaN, hi0: NaN, lo1: NaN, hi1: NaN,
          nkec0: ch0.filter(c => c > 0).length, nkec1: ch1.filter(c => c > 0).length };
  render();
  clearTimeout(bootTimer); bootTimer = setTimeout(() => { [CUR.lo0, CUR.hi0] = boot(h0, r, w); if (S.n) [CUR.lo1, CUR.hi1] = boot(h1, r, w); renderKPI(); }, 350);
}

// ---------- render
function renderKPI(){
  const c = CUR, sc = S.n > 0; const band = (lo, hi) => isNaN(lo) ? "menghitung selang…" : `95 % ${sgn(lo)} … ${sgn(hi)}`;
  const tile = (v0, v1, l, s) => `<div class="kpi"><div class="v"><span>${v0}</span>${sc ? `<span class="after">→ ${v1}</span>` : ""}</div><div class="l">${l}</div><div class="s">${s}</div></div>`;
  document.getElementById("kpis").innerHTML =
    tile(sgn(c.ci0), sgn(c.ci1), `CI ${OUTLAB[S.outcome]} ~ ${RANKLAB[S.rank]}`, sc ? band(c.lo1, c.hi1) + " (skenario)" : band(c.lo0, c.hi0)) +
    tile(fmt(c.cov0,1)+" %", fmt(c.cov1,1)+" %", "penduduk di kecamatan berisi charger", `${c.nkec0}${sc ? " → "+c.nkec1 : ""} dari ${c.sub.length} kecamatan`) +
    tile(fmt(c.per0,2), fmt(c.per1,2), "charger per 100 rb penduduk", `${fmt(c.P)} jiwa · ${c.h0.length ? fmt(c.sub.reduce((s,f) => s+f.ch,0)) : 0} charger${sc ? " + "+S.n : ""}`) +
    tile(isNaN(c.gini0)?"–":c.gini0.toFixed(2).replace(".",","), isNaN(c.gini1)?"–":c.gini1.toFixed(2).replace(".",","), "Gini charger/kapita antar kecamatan", `HHI charger ${fmt(c.hhi0)}${sc ? " → "+fmt(c.hhi1) : ""}`);
}
function render(){ renderKPI(); renderMap(); renderCurve(); renderBars(); renderTable(); renderRegionSum(); save(); }

function renderRegionSum(){ document.getElementById("region-sum").textContent = S.regions.size ? [...S.regions].join(", ") : "Seluruh Jawa Barat (27 kab/kota)";
  document.querySelectorAll("#kabs .chip").forEach(b => b.setAttribute("aria-pressed", S.regions.has(b.dataset.k)));
  document.querySelectorAll("#presets .chip").forEach(b => { const set = PRESETS[b.dataset.p]; b.setAttribute("aria-pressed", set.length ? set.length === S.regions.size && set.every(k => S.regions.has(k)) : !S.regions.size); }); }

// peta
const MW = 1000; let mapSvg = null, mapPaths = null, hatchId = "hatch";
function geomPath(g, PX, PY){ const ring = r => r.map((c,i) => (i?"L":"M") + PX(c[0]).toFixed(1) + " " + PY(c[1]).toFixed(1)).join("") + "Z"; return g.type === "Polygon" ? g.coordinates.map(ring).join("") : g.coordinates.map(p => p.map(ring).join("")).join(""); }
function renderMap(){
  const inR = f => !S.regions.size || S.regions.has(f.kab); const sel = F.filter(inR);
  let minx=1e9, miny=1e9, maxx=-1e9, maxy=-1e9; const walk = (c, fn) => typeof c[0] === "number" ? fn(c) : c.forEach(x => walk(x, fn));
  sel.forEach(f => walk(f.g.coordinates, c => { if (c[0]<minx) minx=c[0]; if (c[0]>maxx) maxx=c[0]; if (c[1]<miny) miny=c[1]; if (c[1]>maxy) maxy=c[1]; }));
  const pad = (maxx-minx)*0.02; minx-=pad; maxx+=pad; miny-=pad; maxy+=pad;
  const k = Math.cos((miny+maxy)/2*Math.PI/180), MH = Math.max(300, Math.round(MW*(maxy-miny)/((maxx-minx)*k)));
  const PX = x => (x-minx)/(maxx-minx)*MW, PY = y => (maxy-y)/(maxy-miny)*MH;
  const box = document.getElementById("map"); box.innerHTML = "";
  mapSvg = el("svg", {viewBox:`0 0 ${MW} ${MH}`, role:"img", "aria-label":"Peta kecamatan"}); box.appendChild(mapSvg);
  const defs = el("defs", {}, mapSvg); const pat = el("pattern", {id:hatchId, width:6, height:6, patternUnits:"userSpaceOnUse", patternTransform:"rotate(45)"}, defs); el("rect", {width:6, height:6, fill:css("--zero")}, pat); el("line", {x1:0, y1:0, x2:0, y2:6, stroke:css("--hatch"), "stroke-width":1.5}, pat);
  const addMap = new Map(CUR.sub.map((f, i) => [f.i, CUR.add[i]]));
  const L = { ch100k: [f => f.pop ? 1e5*(f.ch + (addMap.get(f.i)||0))/f.pop : 0, v => fmt(v,2)], kwhpc: [f => f.pop ? f.kwh/f.pop : 0, v => fmt(v,3)], ev100k: [f => f.ev100k, v => fmt(v,2)], dens: [f => f.dens, v => fmt(v)], exp: [f => f.exp, v => fmt(v)] }[S.layer];
  const vals = sel.map(L[0]); const idx = vals.map((v,i) => i).filter(i => vals[i] > 0).sort((a,b) => vals[a]-vals[b]); const tot = idx.reduce((s,i) => s + sel[i].pop, 0);
  const cuts = []; let acc = 0, qn = 1; for (const i of idx){ acc += sel[i].pop; if (acc >= tot*qn/5 && cuts.length < 4){ cuts.push(vals[i]); qn++; } }
  const cls = v => v <= 0 ? -1 : (cuts.findIndex(c => v <= c) + 5) % 5; const cols = ["--q1","--q2","--q3","--q4","--q5"];
  // konteks: kecamatan di luar pilihan digambar pucat
  if (S.regions.size) F.filter(f => !inR(f)).forEach(f => { const inside = f.g.coordinates.flat(f.g.type === "Polygon" ? 1 : 2).some(c => c[0] > minx && c[0] < maxx && c[1] > miny && c[1] < maxy); if (inside) el("path", {d:geomPath(f.g, PX, PY), fill:css("--grid"), stroke:css("--bg"), "stroke-width":0.5}, mapSvg); });
  sel.forEach((f, i) => { const a = addMap.get(f.i) || 0; const p = el("path", {d:geomPath(f.g, PX, PY), class:"kec", fill: cls(vals[i]) < 0 ? `url(#${hatchId})` : css(cols[cls(vals[i])]), stroke: a ? css("--s2") : css("--bg"), "stroke-width": a ? 2 : 0.6}, mapSvg);
    if (a) p.parentNode.appendChild(p);
    p.addEventListener("pointermove", ev => showTip(ev, `<b>${f.kec}</b> · ${f.kab}<br>${fmt(f.pop)} jiwa · ${fmt(f.dens)} jiwa/km²<br>${f.ch} charger${a ? ` <span class="plus">+${a}</span>` : ""} · ${fmt(f.kw)} kW · ${fmt(f.kwh)} kWh<br>${f.ev} pemilik EV · pengeluaran kab ${fmt(f.exp)} rb · IPM ${f.ipm}`)); p.addEventListener("pointerleave", hideTip); });
  const edges = idx.length ? [vals[idx[0]], ...cuts, vals[idx[idx.length-1]]] : [];
  document.getElementById("mapleg").innerHTML = `<div class="sw"><i style="background:repeating-linear-gradient(45deg,var(--zero) 0 3px,var(--hatch) 3px 4px)"></i>nol</div>` + (edges.length ? cols.map((c,j) => `<div class="sw"><i style="background:var(${c})"></i>${L[1](edges[j])}–${L[1](edges[j+1])}</div>`).join("") : "") + `<div style="margin-left:10px">kuintil penduduk di wilayah terpilih</div>`;
}

// kurva
function renderCurve(){
  const W = 520, H = 360, m = {l:56, r:14, t:14, b:42}, pw = W-m.l-m.r, ph = H-m.t-m.b, X = p => m.l + p*pw, Y = p => m.t + (1-p)*ph;
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":"Kurva konsentrasi"});
  for (let i = 0; i <= 4; i++){ const p = i/4; el("line", {x1:X(0), x2:X(1), y1:Y(p), y2:Y(p), stroke:css("--grid")}, svg); el("line", {y1:Y(0), y2:Y(1), x1:X(p), x2:X(p), stroke:css("--grid")}, svg); el("text", {x:X(p), y:H-m.b+16, "text-anchor":"middle"}, svg).textContent = p*100+" %"; el("text", {x:m.l-6, y:Y(p)+4, "text-anchor":"end"}, svg).textContent = p*100+" %"; }
  el("text", {x:X(.5), y:H-6, "text-anchor":"middle"}, svg).textContent = `Porsi kumulatif penduduk, diurut ${RANKLAB[S.rank]}`;
  el("text", {x:14, y:Y(.5), "text-anchor":"middle", transform:`rotate(-90 14 ${Y(.5)})`}, svg).textContent = `Porsi kumulatif ${OUTLAB[S.outcome]}`;
  el("line", {x1:X(0), y1:Y(0), x2:X(1), y2:Y(1), stroke:css("--fg3"), "stroke-dasharray":"3 3"}, svg);
  const c0 = curve(CUR.h0, CUR.r, CUR.w), c1 = S.n ? curve(CUR.h1, CUR.r, CUR.w) : null;
  const d = pts => pts.map((p,i) => (i?"L":"M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1)).join("");
  if (c1) el("path", {d:d(c1), fill:"none", stroke:css("--s2"), "stroke-width":2}, svg);
  el("path", {d:d(c0), fill:"none", stroke:css("--s1"), "stroke-width":2}, svg);
  el("text", {x:X(.05), y:Y(.93), fill:css("--s1"), "font-weight":600}, svg).textContent = `CI ${sgn(CUR.ci0)}` + (c1 ? "" : "");
  if (c1) el("text", {x:X(.05), y:Y(.86), fill:css("--s2"), "font-weight":600}, svg).textContent = `Skenario CI ${sgn(CUR.ci1)}`;
  const cross = el("line", {y1:Y(0), y2:Y(1), stroke:css("--fg3"), visibility:"hidden"}, svg);
  const interp = (pts, x) => { for (let i = 1; i < pts.length; i++) if (pts[i][0] >= x){ const [x0,y0] = pts[i-1], [x1,y1] = pts[i]; return x1 === x0 ? y1 : y0 + (y1-y0)*(x-x0)/(x1-x0); } return 1; };
  const hit = el("rect", {x:m.l, y:m.t, width:pw, height:ph, fill:"transparent"}, svg);
  hit.addEventListener("pointermove", ev => { const rc = svg.getBoundingClientRect(); const p = Math.max(0, Math.min(1, ((ev.clientX-rc.left)*W/rc.width - m.l)/pw)); cross.setAttribute("x1", X(p)); cross.setAttribute("x2", X(p)); cross.setAttribute("visibility", "visible");
    showTip(ev, `<b>${fmt(p*100)} % penduduk</b> dari peringkat terendah<br>memperoleh ${fmt(interp(c0,p)*100,1)} % ${OUTLAB[S.outcome]}${c1 ? `<br>skenario: ${fmt(interp(c1,p)*100,1)} %` : ""}`); });
  hit.addEventListener("pointerleave", () => { cross.setAttribute("visibility", "hidden"); hideTip(); });
  const box = document.getElementById("curve"); box.innerHTML = ""; box.appendChild(svg);
}

// batang per kab
function renderBars(){
  const rows = []; const kabLevel = ["exp","ipm","npov"].includes(S.rank); const rk = kabLevel ? "dens" : S.rank;
  for (const kab of KABS){ if (S.regions.size && !S.regions.has(kab)) continue; const sub = CUR.sub.map((f,i) => [f, CUR.add[i]]).filter(([f]) => f.kab === kab); if (sub.length < 6) continue;
    const chs = sub.reduce((s,[f]) => s + f.ch, 0); if (chs < 3) continue; const w = sub.map(([f]) => f.pop), r = sub.map(([f]) => f[rk]);
    if (new Set(r).size < 2) continue;  // peringkat kab/kota tidak bervariasi di dalam satu kab
    const h0 = sub.map(([f]) => f[S.outcome]), h1 = sub.map(([f,a]) => S.outcome === "ch" ? f.ch + a : S.outcome === "kw" ? f.kw + 50*a : f[S.outcome]);
    rows.push({kab, n: sub.length, ch: chs, c0: ci(h0, r, w), c1: ci(h1, r, w)}); }
  rows.sort((a,b) => b.c0 - a.c0);
  const box = document.getElementById("bars"); box.innerHTML = "";
  if (kabLevel){ const n = document.createElement("p"); n.className = "note"; n.textContent = `${RANKLAB[S.rank][0].toUpperCase()+RANKLAB[S.rank].slice(1)} sama untuk semua kecamatan di satu kab/kota, jadi di panel ini kecamatan diurut menurut kepadatan.`; box.appendChild(n); }
  if (!rows.length){ box.insertAdjacentHTML("beforeend", `<p class="note">Tidak ada kab/kota di wilayah terpilih yang memenuhi syarat (≥ 6 kecamatan, ≥ 3 charger).</p>`); return; }
  const rowH = 24, W = 760, lab = 150, H = rows.length*rowH + 30, lo = Math.min(-0.2, ...rows.map(x => Math.min(x.c0, x.c1))) - 0.05, hi = Math.max(0.2, ...rows.map(x => Math.max(x.c0, x.c1))) + 0.05;
  const X = v => lab + (v-lo)/(hi-lo)*(W-lab-20);
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"});
  [-0.5,-0.25,0,0.25,0.5,0.75].filter(v => v > lo && v < hi).forEach(v => { el("line", {x1:X(v), x2:X(v), y1:0, y2:H-24, stroke: v ? css("--grid") : css("--fg3")}, svg); el("text", {x:X(v), y:H-8, "text-anchor":"middle"}, svg).textContent = (v>0?"+":"") + String(v).replace(".", ","); });
  rows.forEach((x, i) => { const y = i*rowH + 4; const g = el("g", {style:"cursor:pointer"}, svg);
    el("text", {x:lab-8, y:y+13, "text-anchor":"end", fill:css("--fg")}, g).textContent = x.kab;
    const bar = (v, col, yy, hh) => el("path", {d: v >= 0 ? `M${X(0)} ${yy}H${X(v)-3}a3 3 0 0 1 3 3v${hh-6}a3 3 0 0 1 -3 3H${X(0)}Z` : `M${X(0)} ${yy}H${X(v)+3}a3 3 0 0 0 -3 3v${hh-6}a3 3 0 0 0 3 3H${X(0)}Z`, fill:css(col)}, g);
    if (S.n && Math.abs(x.c1 - x.c0) > 1e-9){ bar(x.c0, "--s1", y, 7); bar(x.c1, "--s2", y+9, 7); } else bar(x.c0, "--s1", y, 16);
    el("text", {x: X(Math.max(x.c0, S.n ? x.c1 : x.c0, 0)) + 6, y:y+13, "font-size":11}, g).textContent = sgn(x.c0) + (S.n && Math.abs(x.c1-x.c0) > 1e-9 ? ` → ${sgn(x.c1)}` : "");
    g.addEventListener("pointermove", ev => showTip(ev, `<b>${x.kab}</b><br>${x.n} kecamatan · ${x.ch} charger<br>CI ${OUTLAB[S.outcome]} ~ ${RANKLAB[rk]}: ${sgn(x.c0)}${S.n ? `<br>skenario: ${sgn(x.c1)}` : ""}<br><i>klik untuk fokus</i>`)); g.addEventListener("pointerleave", hideTip);
    g.addEventListener("click", () => { S.regions = new Set([x.kab]); compute(); }); });
  box.appendChild(svg);
}

// tabel
function renderTable(){
  const cols = [["kecamatan","Kecamatan"],["kab","Kab/kota"],["pop","Penduduk"],["dens","Jiwa/km²"],["ch","Charger"],["add","Baru"],["kw","kW"],["kwh","kWh"],["trx","Transaksi"],["ev","Pemilik EV"],["ch100k","Charger/100 rb"],["exp","Pengeluaran kab"],["ipm","IPM kab"]];
  const rows = CUR.sub.map((f, i) => ({...f, kecamatan: f.kec, add: CUR.add[i], ch100k: 1e5*(f.ch + CUR.add[i])/f.pop}));
  rows.sort((a,b) => { const va = a[S.sortKey], vb = b[S.sortKey]; return (typeof va === "string" ? va.localeCompare(vb) : va - vb) * S.sortDir; });
  const shown = rows.slice(0, 40);
  document.getElementById("tbl-note").textContent = `${rows.length} kecamatan di wilayah terpilih; ditampilkan ${shown.length} teratas menurut kolom terurut. Klik judul kolom untuk mengurutkan.`;
  document.getElementById("table").innerHTML = `<table><thead><tr>${cols.map(([k,l]) => `<th data-k="${k}"${S.sortKey===k ? ` aria-sort="${S.sortDir<0?"descending":"ascending"}"` : ""}>${l}${S.sortKey===k ? (S.sortDir<0?" ▾":" ▴") : ""}</th>`).join("")}</tr></thead><tbody>` +
    shown.map(r => `<tr><td>${r.kecamatan}</td><td>${r.kab}</td><td>${fmt(r.pop)}</td><td>${fmt(r.dens)}</td><td>${r.ch}</td><td>${r.add ? `<span class="plus">+${r.add}</span>` : ""}</td><td>${fmt(r.kw)}</td><td>${fmt(r.kwh)}</td><td>${fmt(r.trx)}</td><td>${r.ev}</td><td>${fmt(r.ch100k,2)}</td><td>${fmt(r.exp)}</td><td>${r.ipm}</td></tr>`).join("") + "</tbody></table>";
  document.querySelectorAll("#table th").forEach(th => th.addEventListener("click", () => { const k = th.dataset.k; if (S.sortKey === k) S.sortDir *= -1; else { S.sortKey = k; S.sortDir = (k === "kecamatan" || k === "kab") ? 1 : -1; } renderTable(); }));
}

// ---------- kendali
const presetsBox = document.getElementById("presets"), kabsBox = document.getElementById("kabs");
presetsBox.innerHTML = Object.keys(PRESETS).map(p => `<button type="button" class="chip preset" data-p="${p}">${p}</button>`).join("");
kabsBox.innerHTML = KABS.map(k => `<button type="button" class="chip" data-k="${k}">${k}</button>`).join("");
presetsBox.addEventListener("click", e => { const b = e.target.closest(".chip"); if (!b) return; S.regions = new Set(PRESETS[b.dataset.p]); compute(); });
kabsBox.addEventListener("click", e => { const b = e.target.closest(".chip"); if (!b) return; const k = b.dataset.k; if (S.regions.has(k)) S.regions.delete(k); else S.regions.add(k); compute(); });
const bind = (id, key, parse=v => v, label) => { const i = document.getElementById(id); i.value = S[key]; if (label) document.getElementById(label).textContent = fmt(+S[key]); i.addEventListener("input", () => { S[key] = parse(i.value); if (label) document.getElementById(label).textContent = fmt(+S[key]); compute(); }); };
bind("rank", "rank"); bind("outcome", "outcome"); bind("rule", "rule"); bind("layer", "layer"); bind("minpop", "minpop", Number, "minpop-v"); bind("nnew", "n", Number, "n-v");
document.getElementById("reset").addEventListener("click", () => { Object.assign(S, {regions:new Set(), rank:"exp", outcome:"ch", minpop:500, n:0, rule:"equal", layer:"ch100k"}); ["rank","outcome","rule","layer","minpop","nnew"].forEach(id => { const i = document.getElementById(id); i.value = S[{rank:"rank",outcome:"outcome",rule:"rule",layer:"layer",minpop:"minpop",nnew:"n"}[id]]; }); document.getElementById("minpop-v").textContent = "500"; document.getElementById("n-v").textContent = "0"; compute(); });
compute();
</script>
"""

html = TEMPLATE.replace("__GEO__", json.dumps(G, ensure_ascii=False, separators=(",", ":")))
open("analysis/concentration_dashboard.html", "w", encoding="utf-8").write(html)
print("ok", len(html) // 1024, "KB")
