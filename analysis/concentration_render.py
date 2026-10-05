"""Halaman visual indeks konsentrasi SPKLU Jawa Barat.

    python3 analysis/concentration_render.py   -> analysis/concentration_jabar.html (mandiri, data disematkan)

Membaca analysis/concentration_jabar.json (pasar/pasokan), analysis/concentration_kecamatan_jabar.json (CI kab/kota +
kecamatan) dan data/jabar_kecamatan_spklu.geojson (peta).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
A = json.load(open("analysis/concentration_jabar.json", encoding="utf-8"))
D = json.load(open("analysis/concentration_kecamatan_jabar.json", encoding="utf-8"))
G = json.load(open("data/jabar_kecamatan_spklu.geojson", encoding="utf-8"))

TEMPLATE = r"""<title>Konsentrasi SPKLU Jabar</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700&family=Source+Sans+3:wght@400;600&display=swap">
<style>
/* Tata letak: satu kolom baca ~72ch untuk teks, panel grafik melebar sampai 1080px; peta dan kurva berdampingan di layar lebar. */
:root{
  --bg:#fcfcfb; --fg:#0b0b0b; --fg2:#52514e; --fg3:#7d7b75; --line:#e4e2dc; --panel:#f4f3ef; --grid:#ebe9e3;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --zero:#d9d7d0; --hatch:#bdbab2;
  --q1:#cde2fb; --q2:#9ec5f4; --q3:#5598e7; --q4:#256abf; --q5:#104281;
  --display:"Archivo",system-ui,sans-serif; --body:"Source Sans 3",system-ui,sans-serif;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#1a1a19; --fg:#ffffff; --fg2:#c3c2b7; --fg3:#8f8d85; --line:#34332f; --panel:#232321; --grid:#2c2b28;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --zero:#3a3936; --hatch:#5a5853;
  --q1:#184f95; --q2:#256abf; --q3:#3987e5; --q4:#6da7ec; --q5:#b7d3f6; color-scheme:dark } }
:root[data-theme="dark"]{
  --bg:#1a1a19; --fg:#ffffff; --fg2:#c3c2b7; --fg3:#8f8d85; --line:#34332f; --panel:#232321; --grid:#2c2b28;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --zero:#3a3936; --hatch:#5a5853;
  --q1:#184f95; --q2:#256abf; --q3:#3987e5; --q4:#6da7ec; --q5:#b7d3f6; color-scheme:dark }
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16px;line-height:1.5;margin:0;padding-block:28px 64px;padding-inline:clamp(16px,4vw,40px)}
.wrap{max-width:1080px;margin:0 auto}
h1,h2,h3{font-family:var(--display);text-wrap:balance;margin:0}
h1{font-size:clamp(28px,4vw,40px);line-height:1.1;font-weight:700}
h2{font-size:22px;font-weight:700;margin-top:48px}
h3{font-size:16px;font-weight:600;color:var(--fg2)}
p{max-width:72ch;margin:8px 0}
.lede{color:var(--fg2);font-size:17px}
.eyebrow{font-family:var(--display);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--fg3);font-weight:500}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin-top:24px}
.kpi{background:var(--panel);padding:14px 16px;border-radius:6px;min-width:0}
.kpi .v{font-family:var(--display);font-size:30px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.1}
.kpi .l{color:var(--fg2);font-size:14px;margin-top:4px}
.kpi .s{color:var(--fg3);font-size:13px;font-variant-numeric:tabular-nums}
.panel{background:var(--panel);border-radius:6px;padding:16px;margin-top:16px;min-width:0}
.controls{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin-bottom:10px;font-size:14px}
.controls label{display:flex;gap:6px;align-items:center;color:var(--fg2)}
select,button{font:inherit;font-size:14px;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:4px 8px}
button[aria-pressed="true"]{border-color:var(--fg);font-weight:600}
button:focus-visible,select:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px;color:var(--fg2);margin:6px 0 0}
.legend i{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:6px;border-radius:2px}
.legend i.dot{width:10px;height:10px;border-radius:50%}
.legend i.box{width:14px;height:12px;border-radius:2px}
svg{display:block;width:100%;height:auto;max-width:100%}
svg text{font-family:var(--body);fill:var(--fg2);font-size:12px}
svg .ax line,svg .ax path{stroke:var(--line)}
svg .grid line{stroke:var(--grid)}
.tip{position:fixed;pointer-events:none;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:4px;padding:6px 9px;font-size:13px;line-height:1.35;box-shadow:0 2px 10px rgba(0,0,0,.12);max-width:260px;z-index:9;font-variant-numeric:tabular-nums}
.tip b{font-weight:600}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:820px){.two{grid-template-columns:1fr}}
table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
th,td{padding:6px 8px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
th:first-child,td:first-child{text-align:left;white-space:normal}
th{font-weight:600;color:var(--fg2);font-size:13px}
.scroll{overflow-x:auto}
details{margin-top:10px;font-size:14px}
summary{cursor:pointer;color:var(--fg2)}
.note{font-size:14px;color:var(--fg2);max-width:72ch}
.sig{color:var(--fg3);font-size:12px}
ul{max-width:72ch;padding-left:20px}
li{margin:4px 0}
a{color:var(--s1)}
.map-wrap{position:relative}
.mapleg{display:flex;gap:2px;align-items:flex-end;margin-top:8px;font-size:12px;color:var(--fg2);flex-wrap:wrap}
.mapleg .sw{display:flex;flex-direction:column;align-items:flex-start;gap:3px}
.mapleg .sw i{display:block;width:56px;height:10px}
@media (prefers-reduced-motion:no-preference){path.kec{transition:fill .2s}}
</style>

<div class="wrap">
<div class="eyebrow">Jawa Barat · Maret 2026 · 636 charger · 331 SPKLU bertransaksi · 629 kecamatan</div>
<h1>Siapa yang dilayani SPKLU Jawa Barat?</h1>
<p class="lede">Dua keluarga ukuran untuk satu pertanyaan. <b>Konsentrasi pasokan</b> (HHI, CR, Gini) menjawab seberapa menumpuk pasokan pada sedikit lokasi. <b>Indeks konsentrasi</b> (Wagstaff) menjawab apakah tumpukan itu jatuh di wilayah kaya atau miskin: kecamatan diurut dari termiskin ke terkaya, lalu dibaca porsi kumulatif charger terhadap porsi kumulatif penduduk. Nilai +1 berarti seluruh pasokan ada di wilayah terkaya, 0 berarti tidak terkait, −1 berarti seluruhnya di wilayah termiskin.</p>

<div class="kpis" id="kpis"></div>

<h2>1 · Kurva konsentrasi</h2>
<p class="note">Garis diagonal adalah kesetaraan sempurna. Semakin kurva melengkung di bawah diagonal, semakin pasokan menumpuk di ujung kanan (wilayah peringkat tinggi). Dua garis: <b>jumlah charger</b> (penempatan) dan <b>energi terjual</b> (pemakaian).</p>
<div class="panel">
  <div class="controls">
    <label>Tingkat <select id="cv-level"><option value="kec">Kecamatan (629)</option><option value="kab">Kab/kota (27)</option></select></label>
    <label>Diurut menurut <select id="cv-rank"></select></label>
  </div>
  <div id="curve"></div>
  <div class="legend"><span><i style="background:var(--s1)"></i>Jumlah charger</span><span><i style="background:var(--s2)"></i>Energi terjual (kWh)</span><span><i style="background:var(--fg3);height:1px"></i>Kesetaraan</span></div>
</div>

<h2>2 · Indeks konsentrasi dengan selang kepercayaan 95 %</h2>
<p class="note">Titik = taksiran CI, garis = selang bootstrap 2.000 ulangan. Selang yang tidak menyentuh nol ditandai. <b>Biru</b> dihitung atas 27 kab/kota, <b>jingga</b> atas 629 kecamatan. Untuk tiga peringkat sosial-ekonomi, nilai kecamatan memakai angka kab/kota induknya sehingga taksirannya sama persis dengan tingkat kab/kota; yang berubah hanya selangnya. Dua peringkat terbawah (kepadatan, pemilik EV) benar-benar diukur per kecamatan.</p>
<div class="panel">
  <div id="forest"></div>
  <div class="legend"><span><i class="dot" style="background:var(--s1)"></i>Kab/kota (SES BPS 2024)</span><span><i class="dot" style="background:var(--s2)"></i>Kecamatan</span><span class="sig">● penuh = 95 % CI tidak melewati 0 · ○ kosong = tidak signifikan</span></div>
  <details><summary>Tabel nilai</summary><div class="scroll" id="forest-table"></div></details>
</div>

<h2>3 · Peta kecamatan</h2>
<p class="note">Setiap kecamatan diwarnai menurut lapisan yang dipilih. Kelas warna adalah kuintil tertimbang penduduk; kecamatan bernilai nol diarsir abu-abu. Arahkan kursor atau sentuh kecamatan untuk angkanya.</p>
<div class="panel">
  <div class="controls" id="map-controls"></div>
  <div class="map-wrap" id="map"></div>
  <div class="mapleg" id="mapleg"></div>
</div>

<h2>4 · Kuintil kecamatan</h2>
<p class="note">Kecamatan dikelompokkan lima kuintil berpenduduk sama (≈10,9 juta jiwa tiap kuintil), sekali menurut pengeluaran per kapita kab/kota induk dan sekali menurut kepadatan kecamatan. Q1 = termiskin / terjarang.</p>
<div class="two">
  <div class="panel"><h3>Energi terjual per kapita (kWh/jiwa/bulan)</h3><div id="q-kwh"></div></div>
  <div class="panel"><h3>Penduduk yang kecamatannya tanpa charger (%)</h3><div id="q-none"></div></div>
</div>
<div class="legend" style="margin-top:8px"><span><i class="box" style="background:var(--s1)"></i>Kuintil pengeluaran kab induk</span><span><i class="box" style="background:var(--s2)"></i>Kuintil kepadatan kecamatan</span></div>

<h2>5 · Di dalam kab/kota</h2>
<p class="note">CI dihitung ulang di dalam tiap kab/kota yang punya ≥8 kecamatan dan ≥5 charger, dengan kecamatan diurut menurut kepadatan dan menurut pemilik EV per 100 ribu. Nilai positif besar berarti charger kab itu menumpuk di kecamatan padat/ber-EV; nilai negatif berarti sebaliknya.</p>
<div class="panel"><div class="scroll" id="within"></div></div>

<h2>6 · Konsentrasi pasokan dan pasar</h2>
<div class="panel"><div class="scroll" id="market"></div>
<p class="note" id="market-note"></p></div>

<h2>Metode, sumber, dan batas</h2>
<ul>
  <li><b>CI tertimbang penduduk</b>: C = 2·cov<sub>w</sub>(h<sub>i</sub>/w<sub>i</sub>, R<sub>i</sub>) / μ, dengan h = pasokan unit, w = penduduk, R = peringkat fraksional tertimbang (ikatan memakai rata-rata peringkat). Identik dengan 1 − 2∫L(p)dp pada kurva konsentrasi; diverifikasi sama dengan metode trapesium di <code>equitymap/keadilan.py</code>. Selang: bootstrap unit, persentil 2,5–97,5.</li>
  <li><b>Penduduk</b>: Kontur Population 2023, H3 res 8 (≈0,74 km²), titik pusat heksagon dijatuhkan ke poligon kecamatan. Totalnya 54,5 juta, lebih tinggi dari BPS (≈50 juta); yang dipakai hanya porsinya.</li>
  <li><b>Batas kecamatan</b>: desa HDX-BPS 2020 (JfrAziz/indonesia-district) digabung per kode kecamatan, 629 kecamatan setelah Waduk Cirata dibuang.</li>
  <li><b>Sosial-ekonomi</b>: BPS 2024 per kab/kota (IPM, pengeluaran per kapita disesuaikan, persentase penduduk miskin P0) dari tabel olahan BPS Query Builder (MercyCantik/UAS-VISDAT-222313205). <b>Tidak ada angka resmi per kecamatan</b>; semua kecamatan memakai nilai kab/kota induknya. Akibatnya CI~pengeluaran di tingkat kecamatan mengukur gradien antar kab/kota dengan penyebut penduduk yang lebih halus, bukan kaya-miskin di dalam kota. Meta Relative Wealth Index (2,4 km) akan menutup celah ini; sumbernya (HDX) tidak terjangkau saat halaman ini dibuat.</li>
  <li><b>SPKLU</b>: Master SPKLU Maret 2026 (636 charger PLN+mitra, kW), rekap transaksi Maret 2026 (331 SPKLU bertransaksi, kWh), pengajuan home-charger status Selesai (2.181 titik) sebagai proksi lokasi pemilik EV. Satu SPKLU dan dua pemilik EV tidak terpetakan ke kecamatan mana pun.</li>
  <li>Satu bulan transaksi adalah potret, bukan tren. Pemilik EV dari pengajuan PLN hanya menangkap yang memasang charger rumah lewat PLN.</li>
</ul>
</div>
<div class="tip" id="tip" hidden></div>

<script>
const D = __D__;
const A = __A__;
const GEO = __GEO__;
const NS = "http://www.w3.org/2000/svg";
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const fmt = (x, d=0) => x.toLocaleString("id-ID", {minimumFractionDigits:d, maximumFractionDigits:d});
const sgn = x => (x>0?"+":"") + x.toFixed(3).replace(".", ",");
const el = (t, a={}, parent) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (parent) parent.appendChild(e); return e; };
const tip = document.getElementById("tip");
function showTip(ev, html){ tip.innerHTML = html; tip.hidden = false; const x = ev.clientX, y = ev.clientY; const w = tip.offsetWidth, h = tip.offsetHeight; tip.style.left = Math.min(x + 14, innerWidth - w - 8) + "px"; tip.style.top = (y + 16 + h > innerHeight ? y - h - 10 : y + 16) + "px"; }
function hideTip(){ tip.hidden = true; }

// ---------- KPI
const bk = D.B_kab, bc = D.B_kec;
const find = (B, r, o) => B.find(b => b.rank.startsWith(r) && b.outcome === o);
const kwhExp = find(bk, "Pengeluaran", "Energi Mar-2026 (kWh)"), chExp = find(bk, "Pengeluaran", "Jumlah charger");
const chEvKec = find(bc, "Pemilik EV", "Jumlah charger");
const q = D.quintiles.filter(x => x.by.startsWith("pengeluaran"));
document.getElementById("kpis").innerHTML = [
  [sgn(kwhExp.ci), "CI energi terjual ~ pengeluaran per kapita", `95 % CI ${sgn(kwhExp.lo)} … ${sgn(kwhExp.hi)} · pro-kaya, signifikan`],
  [sgn(chExp.ci), "CI jumlah charger ~ pengeluaran per kapita", `95 % CI ${sgn(chExp.lo)} … ${sgn(chExp.hi)} · tidak bisa dibedakan dari nol`],
  [`${D.A.n_kec_with_charger} / ${D.meta.n_kecamatan}`, "kecamatan yang punya charger", `${fmt(D.A.pop_in_kec_with_charger_pct,1)} % penduduk tinggal di kecamatan berisi charger`],
  [`${(q[4].kwh_per_capita / q[0].kwh_per_capita).toFixed(1).replace(".", ",")}×`, "energi per kapita kuintil terkaya vs termiskin", `${q[4].kwh_per_capita.toFixed(4)} vs ${q[0].kwh_per_capita.toFixed(4)} kWh/jiwa/bulan`],
].map(([v,l,s]) => `<div class="kpi"><div class="v">${v}</div><div class="l">${l}</div><div class="s">${s}</div></div>`).join("");

// ---------- kurva konsentrasi
const cvLevel = document.getElementById("cv-level"), cvRank = document.getElementById("cv-rank");
function fillRanks(){ const C = cvLevel.value === "kab" ? D.curves_kab : D.curves_kec; cvRank.innerHTML = Object.keys(C).map(k => `<option>${k}</option>`).join(""); }
fillRanks();
function drawCurve(){
  const C = (cvLevel.value === "kab" ? D.curves_kab : D.curves_kec)[cvRank.value];
  const B = (cvLevel.value === "kab" ? D.B_kab : D.B_kec).filter(b => b.rank === cvRank.value);
  const W = 640, H = 420, m = {l:70, r:16, t:12, b:44}, pw = W - m.l - m.r, ph = H - m.t - m.b;
  const X = p => m.l + p * pw, Y = p => m.t + (1 - p) * ph;
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":"Kurva konsentrasi"});
  const grid = el("g", {class:"grid"}, svg);
  for (let i = 0; i <= 4; i++){ const p = i/4; el("line", {x1:X(0), x2:X(1), y1:Y(p), y2:Y(p)}, grid); el("line", {y1:Y(0), y2:Y(1), x1:X(p), x2:X(p)}, grid);
    el("text", {x:X(p), y:H-m.b+16, "text-anchor":"middle"}, svg).textContent = (p*100)+" %"; el("text", {x:m.l-6, y:Y(p)+4, "text-anchor":"end"}, svg).textContent = (p*100)+" %"; }
  el("text", {x:X(.5), y:H-6, "text-anchor":"middle"}, svg).textContent = "Porsi kumulatif penduduk, diurut " + cvRank.value.toLowerCase() + " (rendah → tinggi)";
  const yl = el("text", {x:16, y:Y(.5), "text-anchor":"middle", transform:`rotate(-90 14 ${Y(.5)})`}, svg); yl.textContent = "Porsi kumulatif pasokan";
  el("line", {x1:X(0), y1:Y(0), x2:X(1), y2:Y(1), stroke:css("--fg3"), "stroke-width":1, "stroke-dasharray":"3 3"}, svg);
  const series = [["chargers", "--s1", "Jumlah charger"], ["kwh", "--s2", "Energi terjual"]];
  const paths = {};
  for (const [k, col, lab] of series){ const pts = C[k]; const d = pts.map((p,i) => (i?"L":"M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1)).join(""); paths[k] = el("path", {d, fill:"none", stroke:css(col), "stroke-width":2, "stroke-linejoin":"round"}, svg);
    const b = B.find(b => (k === "chargers" ? b.outcome === "Jumlah charger" : b.outcome.startsWith("Energi")));
    const pos = k === "chargers" ? [X(.06), Y(.9)] : [X(.5), Y(.07)]; const t = el("text", {x:pos[0], y:pos[1], fill:css(col), "font-weight":600}, svg); t.textContent = `${lab} · CI ${sgn(b.ci)}${b.signif?"":" (n.s.)"}`; }
  // crosshair
  const cross = el("line", {y1:Y(0), y2:Y(1), stroke:css("--fg3"), "stroke-width":1, visibility:"hidden"}, svg);
  const dots = series.map(([k,col]) => el("circle", {r:4, fill:css(col), stroke:css("--bg"), "stroke-width":2, visibility:"hidden"}, svg));
  const hit = el("rect", {x:m.l, y:m.t, width:pw, height:ph, fill:"transparent"}, svg);
  const interp = (pts, x) => { for (let i = 1; i < pts.length; i++) if (pts[i][0] >= x){ const [x0,y0] = pts[i-1], [x1,y1] = pts[i]; return x1 === x0 ? y1 : y0 + (y1-y0)*(x-x0)/(x1-x0); } return 1; };
  const move = ev => { const r = svg.getBoundingClientRect(); const p = Math.max(0, Math.min(1, ((ev.clientX - r.left) * W / r.width - m.l) / pw)); cross.setAttribute("x1", X(p)); cross.setAttribute("x2", X(p)); cross.setAttribute("visibility", "visible");
    const vals = series.map(([k], i) => { const y = interp(C[k], p); dots[i].setAttribute("cx", X(p)); dots[i].setAttribute("cy", Y(y)); dots[i].setAttribute("visibility", "visible"); return y; });
    showTip(ev, `<b>${fmt(p*100)} % penduduk</b> dari peringkat terendah<br>memperoleh ${fmt(vals[0]*100,1)} % charger<br>dan ${fmt(vals[1]*100,1)} % energi terjual`); };
  const out = () => { cross.setAttribute("visibility", "hidden"); dots.forEach(d => d.setAttribute("visibility", "hidden")); hideTip(); };
  hit.addEventListener("pointermove", move); hit.addEventListener("pointerleave", out);
  const box = document.getElementById("curve"); box.innerHTML = ""; box.appendChild(svg);
}
cvLevel.addEventListener("change", () => { fillRanks(); drawCurve(); }); cvRank.addEventListener("change", drawCurve); drawCurve();

// ---------- forest plot
function drawForest(){
  const outs = ["Jumlah charger", "Kapasitas (kW)", "Energi Mar-2026 (kWh)", "Transaksi Mar-2026"];
  const ranks = [["Pengeluaran per kapita", "Pengeluaran per kapita (BPS 2024)"], ["IPM", "IPM (BPS 2024)"], ["Kemiskinan (dibalik)", "Kemiskinan P0, dibalik (miskin → kaya)"], ["Kepadatan penduduk", "Kepadatan penduduk"], ["Pemilik EV / 100 rb", "Pemilik EV per 100 rb"]];
  const kecRank = { "Pengeluaran per kapita (BPS 2024)":"Pengeluaran per kapita kab/kota induk", "IPM (BPS 2024)":"IPM kab/kota induk", "Kemiskinan P0, dibalik (miskin → kaya)":"Kemiskinan kab/kota induk, dibalik", "Kepadatan penduduk":"Kepadatan penduduk kecamatan", "Pemilik EV per 100 rb":"Pemilik EV per 100 rb kecamatan" };
  const W = 1100, colW = 230, lab = 180, rowH = 30, m = {t:34, l:lab}, H = m.t + ranks.length*rowH + 30;
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img", "aria-label":"Indeks konsentrasi dengan selang kepercayaan"});
  const lo = -0.35, hi = 0.75;
  ranks.forEach(([short], i) => { const y = m.t + i*rowH + rowH/2; el("text", {x:lab-10, y:y+4, "text-anchor":"end", fill:css("--fg")}, svg).textContent = short; el("line", {x1:lab, x2:W-10, y1:y+rowH/2, y2:y+rowH/2, stroke:css("--grid")}, svg); });
  const rows = [];
  outs.forEach((o, j) => {
    const x0 = m.l + j*colW + 10, pw = colW - 24; const X = v => x0 + (v - lo)/(hi - lo)*pw;
    el("text", {x:x0 + pw/2, y:16, "text-anchor":"middle", fill:css("--fg"), "font-weight":600}, svg).textContent = o;
    el("line", {x1:X(0), x2:X(0), y1:m.t-4, y2:m.t + ranks.length*rowH, stroke:css("--fg3"), "stroke-width":1}, svg);
    [-0.25, 0.25, 0.5].forEach(v => { el("line", {x1:X(v), x2:X(v), y1:m.t + ranks.length*rowH, y2:m.t + ranks.length*rowH + 4, stroke:css("--line")}, svg); el("text", {x:X(v), y:m.t + ranks.length*rowH + 16, "text-anchor":"middle"}, svg).textContent = (v>0?"+":"") + v.toString().replace(".", ","); });
    el("text", {x:X(0), y:m.t + ranks.length*rowH + 16, "text-anchor":"middle"}, svg).textContent = "0";
    ranks.forEach(([short, rk], i) => {
      const y = m.t + i*rowH + rowH/2;
      [[D.B_kab.find(b => b.rank === rk && b.outcome === o), "--s1", -5, "Kab/kota"], [D.B_kec.find(b => b.rank === kecRank[rk] && b.outcome === o), "--s2", 5, "Kecamatan"]].forEach(([b, col, dy, lvl]) => {
        if (!b) return; rows.push([lvl, short, o, b]);
        const g = el("g", {}, svg);
        el("line", {x1:X(b.lo), x2:X(b.hi), y1:y+dy, y2:y+dy, stroke:css(col), "stroke-width":2}, g);
        el("circle", {cx:X(b.ci), cy:y+dy, r:4.5, fill:b.signif?css(col):css("--panel"), stroke:css(col), "stroke-width":2}, g);
        const hitr = el("rect", {x:X(Math.min(b.lo,b.ci))-6, y:y+dy-8, width:Math.max(12, X(b.hi)-X(b.lo)+12), height:16, fill:"transparent"}, g);
        hitr.addEventListener("pointermove", ev => showTip(ev, `<b>${lvl} · ${o}</b><br>diurut ${short.toLowerCase()}<br>CI ${sgn(b.ci)} [${sgn(b.lo)}, ${sgn(b.hi)}]${b.signif?"<br>signifikan pada 95 %":"<br>tidak signifikan"}`)); hitr.addEventListener("pointerleave", hideTip);
      });
    });
  });
  const box = document.getElementById("forest"); box.innerHTML = ""; const sc = document.createElement("div"); sc.className = "scroll"; sc.style.minWidth = "0"; sc.appendChild(svg); svg.style.minWidth = "720px"; box.appendChild(sc);
  document.getElementById("forest-table").innerHTML = `<table><thead><tr><th>Tingkat</th><th>Peringkat</th><th>Pasokan</th><th>CI</th><th>95 % bawah</th><th>95 % atas</th></tr></thead><tbody>` +
    rows.map(([l,r,o,b]) => `<tr><td>${l}</td><td>${r}</td><td>${o}</td><td>${sgn(b.ci)}${b.signif?"*":""}</td><td>${sgn(b.lo)}</td><td>${sgn(b.hi)}</td></tr>`).join("") + "</tbody></table>";
}
drawForest();

// ---------- peta kecamatan
const LAYERS = [
  ["ch100k", "Charger per 100 rb penduduk", f => f.pop ? 1e5*f.ch/f.pop : 0, v => fmt(v,2)],
  ["kwhpc", "Energi terjual per kapita (kWh/jiwa)", f => f.pop ? f.kwh/f.pop : 0, v => fmt(v,3)],
  ["ev100k", "Pemilik EV per 100 rb penduduk", f => f.pop ? 1e5*f.ev/f.pop : 0, v => fmt(v,2)],
  ["dens", "Kepadatan (jiwa/km²)", f => f.dens, v => fmt(v)],
  ["exp", "Pengeluaran per kapita kab/kota (ribu Rp/th)", f => f.exp, v => fmt(v)],
];
let layer = "ch100k";
const feats = GEO.features;
let minx=1e9, miny=1e9, maxx=-1e9, maxy=-1e9;
const eachCoord = (geom, fn) => { const walk = c => typeof c[0] === "number" ? fn(c) : c.forEach(walk); walk(geom.coordinates); };
feats.forEach(f => eachCoord(f.geometry, c => { if (c[0]<minx) minx=c[0]; if (c[0]>maxx) maxx=c[0]; if (c[1]<miny) miny=c[1]; if (c[1]>maxy) maxy=c[1]; }));
const MW = 1000, k = Math.cos((miny+maxy)/2*Math.PI/180), MH = Math.round(MW*(maxy-miny)/((maxx-minx)*k));
const PX = x => (x-minx)/(maxx-minx)*MW, PY = y => (maxy-y)/(maxy-miny)*MH;
const ringPath = r => r.map((c,i) => (i?"L":"M") + PX(c[0]).toFixed(1) + " " + PY(c[1]).toFixed(1)).join("") + "Z";
const geomPath = g => g.type === "Polygon" ? g.coordinates.map(ringPath).join("") : g.coordinates.map(p => p.map(ringPath).join("")).join("");
const msvg = el("svg", {viewBox:`0 0 ${MW} ${MH}`, role:"img", "aria-label":"Peta kecamatan Jawa Barat"});
const defs = el("defs", {}, msvg); const pat = el("pattern", {id:"hatch", width:6, height:6, patternUnits:"userSpaceOnUse", patternTransform:"rotate(45)"}, defs); el("rect", {width:6, height:6, fill:css("--zero")}, pat); el("line", {x1:0, y1:0, x2:0, y2:6, stroke:css("--hatch"), "stroke-width":1.5}, pat);
const paths = feats.map(f => { const p = el("path", {d:geomPath(f.geometry), class:"kec", stroke:css("--bg"), "stroke-width":0.6}, msvg);
  const P = f.properties; p.addEventListener("pointermove", ev => showTip(ev, `<b>${P.kec}</b> · ${P.kab}<br>Penduduk ${fmt(P.pop)} · ${fmt(P.dens)} jiwa/km²<br>${P.ch} charger · ${fmt(P.kw)} kW · ${fmt(P.kwh)} kWh/bulan<br>${P.ev} pemilik EV · pengeluaran kab ${fmt(P.exp)} rb/th · IPM ${P.ipm}`)); p.addEventListener("pointerleave", hideTip); return p; });
document.getElementById("map").appendChild(msvg);
const mc = document.getElementById("map-controls"); mc.innerHTML = `<span style="color:var(--fg2)">Lapisan</span>` + LAYERS.map(([id, lab]) => `<button type="button" id="ly-${id}" aria-pressed="${id===layer}">${lab}</button>`).join("");
function paintMap(){
  const L = LAYERS.find(l => l[0] === layer); const vals = feats.map(f => L[2](f.properties));
  // kuintil tertimbang penduduk di antara kecamatan bernilai > 0
  const idx = vals.map((v,i) => i).filter(i => vals[i] > 0).sort((a,b) => vals[a]-vals[b]); const tot = idx.reduce((s,i) => s + feats[i].properties.pop, 0);
  const cuts = []; let acc = 0, qn = 1; for (const i of idx){ acc += feats[i].properties.pop; if (acc >= tot*qn/5 && cuts.length < 4){ cuts.push(vals[i]); qn++; } }
  const cls = v => v <= 0 ? -1 : cuts.findIndex(c => v <= c) === -1 ? 4 : cuts.findIndex(c => v <= c);
  const cols = ["--q1","--q2","--q3","--q4","--q5"];
  paths.forEach((p,i) => { const c = cls(vals[i]); p.setAttribute("fill", c < 0 ? "url(#hatch)" : css(cols[c])); });
  const lg = document.getElementById("mapleg"); const edges = [Math.min(...idx.map(i => vals[i])), ...cuts, Math.max(...vals)];
  lg.innerHTML = `<div class="sw"><i style="background:url(#hatch);background:repeating-linear-gradient(45deg,var(--zero) 0 3px,var(--hatch) 3px 4px)"></i>nol</div>` + cols.map((c,j) => `<div class="sw"><i style="background:var(${c})"></i>${L[3](edges[j])}–${L[3](edges[j+1])}</div>`).join("") + `<div style="margin-left:12px">${L[1]}, kuintil penduduk</div>`;
  LAYERS.forEach(([id]) => document.getElementById("ly-"+id).setAttribute("aria-pressed", id === layer));
}
LAYERS.forEach(([id]) => document.getElementById("ly-"+id).addEventListener("click", () => { layer = id; paintMap(); }));
paintMap();

// ---------- kuintil
function drawQ(id, key, fmtv){
  const groups = [["pengeluaran", "--s1"], ["kepadatan", "--s2"]];
  const W = 500, H = 240, m = {l:44, r:10, t:10, b:30}, pw = W-m.l-m.r, ph = H-m.t-m.b;
  const data = groups.map(([g]) => D.quintiles.filter(x => x.by.startsWith(g)));
  const raw = Math.max(...data.flat().map(x => x[key])) * 1.1; const pow = Math.pow(10, Math.floor(Math.log10(raw))); const max = Math.ceil(raw / pow * 2) / 2 * pow;
  const svg = el("svg", {viewBox:`0 0 ${W} ${H}`, role:"img"});
  const Y = v => m.t + ph - v/max*ph;
  for (let i = 0; i <= 4; i++){ const v = max*i/4; el("line", {x1:m.l, x2:W-m.r, y1:Y(v), y2:Y(v), stroke:css("--grid")}, svg); el("text", {x:m.l-6, y:Y(v)+4, "text-anchor":"end"}, svg).textContent = fmtv(v); }
  const bw = pw/5, barw = bw*0.32;
  for (let qi = 0; qi < 5; qi++){ const cx = m.l + bw*qi + bw/2; el("text", {x:cx, y:H-8, "text-anchor":"middle", fill:css("--fg")}, svg).textContent = "Q"+(qi+1);
    groups.forEach(([g,col], gi) => { const row = data[gi][qi]; if (!row) return; const x = cx + (gi?2:-barw-2), v = row[key], y = Y(v), h = m.t+ph-y;
      const r = el("path", {d:`M${x} ${m.t+ph}V${y+3}a3 3 0 0 1 3 -3h${barw-6}a3 3 0 0 1 3 3V${m.t+ph}Z`, fill:css(col)}, svg);
      r.addEventListener("pointermove", ev => showTip(ev, `<b>Q${qi+1} menurut ${g}</b><br>${row.n_kec} kecamatan · ${fmt(row.pop)} jiwa<br>${fmtv(v)} · ${row.chargers} charger · ${fmt(row.per100k,2)} charger/100 rb`)); r.addEventListener("pointerleave", hideTip);
      if (qi === 0 || qi === 4) el("text", {x:x+barw/2, y:y-4, "text-anchor":"middle", "font-size":11}, svg).textContent = fmtv(v); }); }
  el("line", {x1:m.l, x2:W-m.r, y1:m.t+ph, y2:m.t+ph, stroke:css("--line")}, svg);
  document.getElementById(id).appendChild(svg);
}
drawQ("q-kwh", "kwh_per_capita", v => v.toFixed(3).replace(".", ","));
drawQ("q-none", "pop_no_charger_pct", v => fmt(v,0)+" %");

// ---------- dalam kab/kota
document.getElementById("within").innerHTML = `<table><thead><tr><th>Kab/kota</th><th>Kecamatan</th><th>Charger</th><th>Kecamatan berisi charger</th><th>CI charger ~ kepadatan</th><th>CI kWh ~ kepadatan</th><th>CI charger ~ pemilik EV</th><th>Gini charger/100 rb antar-kecamatan</th></tr></thead><tbody>` +
  D.within.map(x => `<tr><td>${x.nama}</td><td>${x.n_kec}</td><td>${x.chargers}</td><td>${x.kec_with_charger}</td><td>${sgn(x.ci_chargers_density)}</td><td>${x.ci_kwh_density==null?"–":sgn(x.ci_kwh_density)}</td><td>${sgn(x.ci_chargers_ev)}</td><td>${x.gini_chargers.toFixed(3).replace(".", ",")}</td></tr>`).join("") + "</tbody></table>";

// ---------- pasar
const M = A.A; const rowsM = [["kWh per SPKLU", M.spklu_kwh], ["Transaksi per SPKLU", M.spklu_trx], ["Charger per kecamatan", D.A.kec_chargers], ["kWh per kecamatan", D.A.kec_kwh], ["kWh per kab/kota", M.kab_kwh], ["Penduduk per kab/kota (pembanding)", M.kab_pop], ["kWh per UP3", M.up3_kwh], ["kWh per jenis lokasi", M.jenis_lokasi_kwh], ["kW per pemilik (PLN/mitra)", M.milik_kw], ["Pemilik EV per kecamatan", D.A.kec_ev]];
document.getElementById("market").innerHTML = `<table><thead><tr><th>Dimensi</th><th>n</th><th>HHI</th><th>N efektif</th><th>CR4</th><th>CR10</th><th>Gini</th></tr></thead><tbody>` +
  rowsM.map(([l,s]) => `<tr><td>${l}</td><td>${s.n}</td><td>${fmt(s.hhi)}</td><td>${fmt(s.n_effective,1)}</td><td>${fmt(s.cr4*100,1)} %</td><td>${fmt(s.cr10*100,1)} %</td><td>${s.gini.toFixed(3).replace(".", ",")}</td></tr>`).join("") + "</tbody></table>";
document.getElementById("market-note").textContent = `HHI 0–10.000; di atas 2.500 lazim disebut sangat terkonsentrasi. 10 % SPKLU teratas menjual ${fmt(M.top10pct_share_kwh*100,1)} % energi; sepuluh kecamatan teratas (${D.A.top10_kwh.slice(0,3).map(x => x.kecamatan).join(", ")}, …) menjual ${fmt(D.A.top10_kwh.reduce((s,x) => s + x.share, 0)*100,1)} %. Jumlah charger antar-kecamatan (Gini 0,43) hampir setersebar penduduk (0,39); energinya tidak (0,76).`;
</script>
"""

html = TEMPLATE.replace("__D__", json.dumps(D, ensure_ascii=False, separators=(",", ":"))) \
               .replace("__A__", json.dumps(A, ensure_ascii=False, separators=(",", ":"))) \
               .replace("__GEO__", json.dumps(G, ensure_ascii=False, separators=(",", ":")))
open("analysis/concentration_jabar.html", "w", encoding="utf-8").write(html)
print("ok", len(html) // 1024, "KB")
