"""Sisipkan (atau perbarui) tab '🎯 Concentration Index Jabar' di index.html (grup Analisis SPKLU, setelah Ekuitas vs Kesetaraan).

Idempoten. Batas blok: <!-- CONC:BEGIN/END -->. Halaman statis (analysis/conc_page.html) diisi angka dari
analysis/concentration_kecamatan_jabar.json dan analysis/concentration_jabar.json; dasbor interaktif disematkan lewat iframe.

    python3 scripts/concentration_kecamatan_jabar.py --raw <dir>   # bila data berubah
    python3 analysis/concentration_dashboard_render.py
    python3 analysis/conc_inject.py
"""
import csv, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
D = json.load(open("analysis/concentration_kecamatan_jabar.json", encoding="utf-8"))
A = json.load(open("analysis/concentration_jabar.json", encoding="utf-8"))
page = open("analysis/conc_page.html", encoding="utf-8").read()

TAB = '["conc","🎯 Concentration Index Jabar"]'
BEG, END = "<!-- CONC:BEGIN -->", "<!-- CONC:END -->"


def s(x, d=3):
    return ("+" if x > 0 else "") + f"{x:.{d}f}".replace(".", ",")


def band(b):
    return f"[{s(b['lo'])}, {s(b['hi'])}]"


def f(x, d=0):
    return f"{x:,.{d}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def find(B, rank_prefix, outcome_prefix):
    return next(b for b in B if b["rank"].startswith(rank_prefix) and b["outcome"].startswith(outcome_prefix))


Bk, Bc, E = D["B_kab"], D["B_kec"], D["E_kec"]
ci_ch = find(Bk, "Pengeluaran", "Jumlah"); ci_kw = find(Bk, "Pengeluaran", "Kapasitas"); ci_kwh = find(Bk, "Pengeluaran", "Energi")
e_has = next(e for e in E if e["rank"].startswith("IPM") and e["var"].startswith("akses"))
e_dep = next(e for e in E if e["rank"].startswith("IPM") and e["var"].startswith("kekurangan"))
Q = [q for q in D["quintiles"] if q["by"].startswith("pengeluaran")]
cov = D["A"]["pop_in_kec_with_charger_pct"]; n_kec = D["meta"]["n_kecamatan_analisis"]; n_ch_kec = D["A"]["n_kec_with_charger"]

# ---------------------------------------------------------------- skenario (aturan sama dengan dasbor interaktif)
rows = [r for r in csv.DictReader(open("equitymap/input/jabar_kecamatan.csv", encoding="utf-8")) if float(r["pop"]) >= 500]
import numpy as np
from sys import path as _p; _p.insert(0, "scripts")
from concentration_lib import ci, erreygers
pop = np.array([float(r["pop"]) for r in rows]); ch0 = np.array([float(r["chargers"]) for r in rows]); ev = np.array([float(r["ev_owner"]) for r in rows])
ipm = np.array([float(r["ipm"]) for r in rows]); exp_ = np.array([float(r["expend"]) for r in rows])
SCEN_N = 300


def scenario(rule, n=SCEN_N):
    add = np.zeros(len(rows))
    for _ in range(n):
        if rule == "equal": k = (ch0 + add) / pop
        elif rule == "demand": k = -ev / (ch0 + add + 1)
        else: k = exp_ * 1e3 + (ch0 + add) / pop * 1e6
        add[int(np.argmin(k))] += 1
    return ch0 + add


scen = [("Sekarang (Maret 2026)", ch0)] + [(lab, scenario(r)) for lab, r in (("Kesetaraan: charger/kapita terendah dulu", "equal"), ("Permintaan: pemilik EV per charger tertinggi dulu", "demand"), ("Pro-miskin: pengeluaran kab terendah dulu", "poor"))]
scen_rows = []
for lab, c in scen:
    has = (c > 0).astype(float)
    scen_rows.append(dict(lab=lab, cov=100 * pop[has > 0].sum() / pop.sum(), nkec=int(has.sum()), e=erreygers(has, ipm, pop), ci=ci(c, exp_, pop),
                          q1=100 * pop[(has == 0) & (exp_ <= np.percentile(exp_, 20))].sum() / pop[exp_ <= np.percentile(exp_, 20)].sum()))
tbl_scen = "<table><thead><tr><th>Skenario (+%d charger)</th><th>Kecamatan berisi charger</th><th>%% penduduk tercakup</th><th>E akses ~ IPM</th><th>CI charger ~ pengeluaran</th><th>%% penduduk kuintil termiskin tanpa charger</th></tr></thead><tbody>" % SCEN_N
for r in scen_rows:
    tbl_scen += f"<tr><td><b>{r['lab']}</b></td><td class=n>{r['nkec']}</td><td class=n>{f(r['cov'],1)} %</td><td class=n>{s(r['e'])}</td><td class=n>{s(r['ci'])}</td><td class=n>{f(r['q1'],1)} %</td></tr>"
tbl_scen += "</tbody></table>"
se = scen_rows[1]; sd = scen_rows[2]

# ---------------------------------------------------------------- tabel hasil
def star(b, key="ci"):
    return f"<b class=sig>{s(b[key])} ★</b>" if b["signif"] else f"<span class=ns>{s(b[key])}</span>"


def tbl_ci(B):
    out = "<table><thead><tr><th>Peringkat (rendah → tinggi)</th><th>Charger</th><th>kW</th><th>kWh Mar-26</th><th>Transaksi</th></tr></thead><tbody>"
    for rk in dict.fromkeys(b["rank"] for b in B):
        cells = "".join(f"<td class=n>{star(b)}<br><span class=ns style='font-size:10.5px'>{band(b)}</span></td>" for b in B if b["rank"] == rk)
        out += f"<tr><td>{rk}</td>{cells}</tr>"
    return out + "</tbody></table>"


tbl_err = "<table><thead><tr><th>Peringkat</th><th>Variabel 0/1</th><th>E</th><th>95 %</th></tr></thead><tbody>" + "".join(
    f"<tr><td>{e['rank']}</td><td>{e['var']}</td><td class=n>{star(e, 'e')}</td><td class=n>{band(e)}</td></tr>" for e in E) + "</tbody></table>"
tbl_quint = "<table><thead><tr><th>Q</th><th>Kec</th><th>Penduduk</th><th>Charger/100 rb</th><th>kWh/jiwa</th><th>% tanpa charger</th><th>EV/100 rb</th></tr></thead><tbody>" + "".join(
    f"<tr><td>Q{q['q']}</td><td class=n>{q['n_kec']}</td><td class=n>{f(q['pop'])}</td><td class=n>{f(q['per100k'],2)}</td><td class=n>{f(q['kwh_per_capita'],4)}</td><td class=n>{f(q['pop_no_charger_pct'],1)}</td><td class=n>{f(q['ev_per100k'],2)}</td></tr>" for q in Q) + "</tbody></table>"
tbl_within = "<table><thead><tr><th>Kab/kota</th><th>Kec</th><th>Charger</th><th>Kec berisi</th><th>CI charger ~ kepadatan</th><th>CI kWh ~ kepadatan</th><th>CI charger ~ EV</th><th>Gini charger/100 rb</th></tr></thead><tbody>" + "".join(
    f"<tr><td>{w['nama']}</td><td class=n>{w['n_kec']}</td><td class=n>{w['chargers']}</td><td class=n>{w['kec_with_charger']}</td><td class=n>{s(w['ci_chargers_density'])}</td><td class=n>{'–' if w['ci_kwh_density'] is None else s(w['ci_kwh_density'])}</td><td class=n>{s(w['ci_chargers_ev'])}</td><td class=n>{f(w['gini_chargers'],3)}</td></tr>" for w in D["within"]) + "</tbody></table>"
kv = [(s(ci_ch["ci"]), "CI charger ~ pengeluaran " + band(ci_ch), "ok" if not ci_ch["signif"] else "r"),
      (s(ci_kw["ci"]), "CI kW ~ pengeluaran " + band(ci_kw), "g"),
      (s(ci_kwh["ci"]), "CI kWh ~ pengeluaran " + band(ci_kwh), "r"),
      (s(e_has["e"]), "Erreygers E akses ~ IPM " + band(e_has) + " — aturan lulus: GAGAL", "r"),
      (s(e_dep["e"]), "Erreygers E kekurangan ~ IPM " + band(e_dep), "r"),
      (f"{f(cov,1)} %", f"penduduk di kecamatan berisi charger ({n_ch_kec} dari {n_kec})", ""),
      (f(D["A"]["kec_chargers"]["gini"], 2), "Gini charger antar kecamatan (penduduk: " + f(D["A"]["kec_pop"]["gini"], 2) + ")", ""),
      (f(D["A"]["kec_kwh"]["gini"], 2), "Gini kWh antar kecamatan", "")]
kv_html = "".join(f"<div class='{c}'><div class='v'>{v}</div><div class='t'>{t}</div></div>" for v, t, c in kv)

top10 = D["A"]["top10_kwh"]
rep = {
    "n_kec": str(n_kec), "n_charger": str(D["meta"]["n_charger"]), "n_spklu": str(D["meta"]["n_spklu_trx"]), "n_ev": f(D["meta"]["n_ev"]),
    "ci_ch_exp": s(ci_ch["ci"]), "ci_ch_exp_band": band(ci_ch), "ci_kw_exp": s(ci_kw["ci"]), "ci_kwh_exp": s(ci_kwh["ci"]), "ci_kwh_exp_band": band(ci_kwh),
    "e_has_ipm": s(e_has["e"]), "e_has_ipm_band": band(e_has), "e_dep_ipm": s(e_dep["e"]), "e_dep_ipm_band": band(e_dep),
    "n_kec_ch": str(n_ch_kec), "n_kec_no": str(n_kec - n_ch_kec), "cov_pct": f(cov, 1), "nocov_pct": f(100 - cov, 1),
    "q_ratio": f(Q[4]["kwh_per_capita"] / Q[0]["kwh_per_capita"], 1), "q1_none": f(Q[0]["pop_no_charger_pct"], 1), "q5_none": f(Q[4]["pop_no_charger_pct"], 1),
    "q1_kwhpc": f(Q[0]["kwh_per_capita"], 4), "q5_kwhpc": f(Q[4]["kwh_per_capita"], 4), "gap": s(ci_kwh["ci"] - ci_ch["ci"]),
    "top10pct": f(A["A"]["top10pct_share_kwh"] * 100, 1), "top10kec_share": f(sum(t["share"] for t in top10) * 100, 1),
    "kv_results": kv_html, "tbl_ci_kec": tbl_ci(Bc), "tbl_ci_kab": tbl_ci(Bk), "tbl_err": tbl_err, "tbl_quint": tbl_quint, "tbl_within": tbl_within, "tbl_scen": tbl_scen,
    "scen_n": str(SCEN_N), "scen_equal_cov": f(se["cov"], 1), "scen_equal_e": s(se["e"]), "scen_demand_cov": f(sd["cov"], 1), "scen_demand_e": s(sd["e"]),
}
page = re.sub(r"\{\{(\w+)\}\}", lambda m: rep[m.group(1)], page)
assert "{{" not in page

# ---------------------------------------------------------------- injeksi ke index.html
src = open("index.html", encoding="utf-8").read()


def once(hay, needle):
    assert hay.count(needle) == 1, "anchor tidak unik/tidak ditemukan: " + needle[:70]


had = BEG in src
src = src.replace("," + TAB, "")
src = re.sub(r'(\["analisis","📊 Analisis SPKLU",\[[^\]]*\])', lambda m: m.group(1).replace('"conc",', ''), src, count=1)
src = re.sub(re.escape(BEG) + r".*?" + re.escape(END) + r"\n?", "", src, flags=re.S)
assert 'id="p-conc"' not in src
print("blok lama dicopot" if had else "injeksi pertama")

anchor_tab = '["keadilan","⚖️ Ekuitas vs Kesetaraan"]'; once(src, anchor_tab)
src = src.replace(anchor_tab, anchor_tab + "," + TAB, 1)
nav_re = re.compile(r'(\["analisis","📊 Analisis SPKLU",\[[^\]]*"keadilan",)'); assert len(nav_re.findall(src)) == 1
src = nav_re.sub(lambda m: m.group(0) + '"conc",', src, count=1)
anchor_page = "<!-- SUMMARY (paper) -->"; once(src, anchor_page)
src = src.replace(anchor_page, BEG + "\n" + page + END + "\n" + anchor_page, 1)
open("index.html", "w", encoding="utf-8").write(src)
print("tab terpasang; index.html %.0f KB" % (len(src) / 1024))
