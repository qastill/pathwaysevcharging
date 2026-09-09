"""⚖️ Ekuitas vs Kesetaraan — analisis mendalam nasional (offline, dari equitymap/equity.js).

    python3 equitymap/prepare.py       # bila equity.js belum ada
    python3 equitymap/keadilan.py      # -> equitymap/keadilan.json (payload kecil, disisipkan ke index.html)
    python3 equitymap/keadilan_inject.py

Dua konsep yang sengaja dipisah:
  * KESETARAAN (equality, horizontal): tiap orang mendapat porsi charger yang sama — Lorenz/Gini charger
    terhadap penduduk, dekomposisi Theil (antar- vs dalam-provinsi), kota vs kabupaten, rasio 20:20, defisit
    menuju kesetaraan.
  * EKUITAS (equity, vertikal): porsi mengikuti kebutuhan — indeks konsentrasi terhadap pendapatan/IPM/
    kemiskinan provinsi, kuintil pendapatan, dan dua aturan penempatan (kesetaraan vs ekuitas) yang diuji
    sebagai kurva cakupan marjinal 300 situs baru (greedy maximum coverage).
"""
import csv, heapq, json, math, os

import h3
import numpy as np
_trapz = getattr(np, "trapezoid", None) or getattr(np, "trapz")  # numpy 1.x/2.x

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)

js = open(os.path.join(HERE, "equity.js"), encoding="utf-8").read()
E = json.loads(js[len("window.EQUITY="):].rstrip(";\n"))
ci = {c: i for i, c in enumerate(E["cols"])}
R6 = E["r6"]
KS = [k for k in E["kab_stats"] if k["pop"] > 0]
PROVS = E["provs"]
KABS = E["kabs"]
COVER_KM = 10.0
N_NEW = 300
JAVA = {"Banten", "DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur"}


# ------------------------------------------------------------------ alat ukur
def lorenz(pop, val, npts=50):
    pop, val = np.asarray(pop, float), np.asarray(val, float)
    o = np.argsort(np.divide(val, np.maximum(pop, 1e-9)))
    cp = np.concatenate([[0], np.cumsum(pop[o]) / pop.sum()])
    cv = np.concatenate([[0], np.cumsum(val[o]) / max(val.sum(), 1e-9)])
    g = 1 - 2 * _trapz(cv, cp)
    step = max(1, len(cp) // npts)
    pts = [[round(float(a), 4), round(float(b), 4)] for a, b in zip(cp[::step], cv[::step])] + [[1.0, 1.0]]
    return round(float(g), 3), pts


def concentration(pop, val, rank_key, npts=40):
    """Kurva konsentrasi: unit diurutkan menurut rank_key (miskin -> kaya); CI>0 = pro-kaya."""
    o = np.argsort(rank_key)
    pop, val = np.asarray(pop, float)[o], np.asarray(val, float)[o]
    cp = np.concatenate([[0], np.cumsum(pop) / pop.sum()])
    cv = np.concatenate([[0], np.cumsum(val) / max(val.sum(), 1e-9)])
    c = 1 - 2 * _trapz(cv, cp)
    step = max(1, len(cp) // npts)
    pts = [[round(float(a), 4), round(float(b), 4)] for a, b in zip(cp[::step], cv[::step])] + [[1.0, 1.0]]
    return round(float(c), 3), pts


def theil(pop, val, group):
    """Theil T dari nilai per kapita, dengan dekomposisi antar-kelompok dan dalam-kelompok."""
    pop, val, group = np.asarray(pop, float), np.asarray(val, float), np.asarray(group)
    P, Y = pop.sum(), val.sum()
    s = (val > 0)
    T = float(np.sum((val[s] / Y) * np.log((val[s] / Y) / (pop[s] / P))))
    between = 0.0; within = 0.0; parts = []
    for g in np.unique(group):
        m = group == g
        Pg, Yg = pop[m].sum(), val[m].sum()
        if Yg <= 0:
            parts.append(dict(g=int(g), share_pop=Pg / P, share_val=0.0, T=0.0)); continue
        between += (Yg / Y) * math.log((Yg / Y) / (Pg / P))
        sg = m & s
        Tg = float(np.sum((val[sg] / Yg) * np.log((val[sg] / Yg) / (pop[sg] / Pg))))
        within += (Yg / Y) * Tg
        parts.append(dict(g=int(g), share_pop=Pg / P, share_val=Yg / Y, T=Tg))
    return dict(T=round(T, 4), between=round(between, 4), within=round(within, 4),
                between_pct=round(100 * between / T, 1) if T else 0, parts=parts)


# ------------------------------------------------------------------ 1) kesetaraan horizontal
pop_k = np.array([k["pop"] for k in KS], float)
ch_k = np.array([k["chargers"] for k in KS], float)
kw_k = np.array([k["kw"] for k in KS], float)
site_k = np.array([k["active"] for k in KS], float)
prov_k = np.array([k["prov"] for k in KS])
is_kota = np.array([k["name"].startswith("Kota ") for k in KS])
gini_ch, lor_ch = lorenz(pop_k, ch_k)
gini_kw, lor_kw = lorenz(pop_k, kw_k)
gini_site, lor_site = lorenz(pop_k, site_k)
# akses (penduduk dalam 10 km) — ukuran cakupan, bukan porsi charger
acc_k = np.array([k["pop"] * k["within10"] / 100 for k in KS])
gini_acc, lor_acc = lorenz(pop_k, acc_k)
# per heksagon (res 6): charger dalam 10 km terhadap penduduk
pop_h = np.array([r[ci["pop"]] for r in R6], float)
c10_h = np.array([r[ci["c10"]] for r in R6], float)
gini_hex, lor_hex = lorenz(pop_h, c10_h, npts=60)
# tanpa DKI · Jawa saja · luar Jawa
pi_name = [p["name"] for p in PROVS]
mask_dki = np.array([pi_name[p] == "DKI Jakarta" for p in prov_k])
mask_java = np.array([pi_name[p] in JAVA for p in prov_k])
variants = [
    ("Seluruh kabupaten/kota", gini_ch),
    ("Tanpa DKI Jakarta", lorenz(pop_k[~mask_dki], ch_k[~mask_dki])[0]),
    ("Jawa saja", lorenz(pop_k[mask_java], ch_k[mask_java])[0]),
    ("Luar Jawa saja", lorenz(pop_k[~mask_java], ch_k[~mask_java])[0]),
    ("Kota saja", lorenz(pop_k[is_kota], ch_k[is_kota])[0]),
    ("Kabupaten saja", lorenz(pop_k[~is_kota], ch_k[~is_kota])[0]),
]
th = theil(pop_k, ch_k, prov_k)
th_kota = theil(pop_k, ch_k, is_kota.astype(int))

# kota vs kabupaten
def grp(mask, label):
    p = pop_k[mask].sum(); c = ch_k[mask].sum()
    w10 = sum(k["pop"] * k["within10"] for k, m in zip(KS, mask) if m) / p
    b25 = sum(k["pop"] * k["beyond25"] for k, m in zip(KS, mask) if m) / p
    dm = sum(k["pop"] * k["d_mean"] for k, m in zip(KS, mask) if m) / p
    return dict(label=label, n=int(mask.sum()), pop=round(float(p)), chargers=int(c), per100k=round(1e5 * c / p, 2),
                within10=round(w10, 1), beyond25=round(b25, 1), d_mean=round(dm, 1),
                zero=int(sum(1 for k, m in zip(KS, mask) if m and k["chargers"] == 0)),
                dc=int(sum(k["dc"] for k, m in zip(KS, mask) if m)))
kota_kab = [grp(is_kota, "Kota"), grp(~is_kota, "Kabupaten")]
java = [grp(mask_java, "Jawa"), grp(~mask_java, "Luar Jawa")]

# rasio 20:20 & Palma (kabupaten diurut per kapita, tertimbang penduduk)
o = np.argsort(np.divide(ch_k, pop_k)); cp = np.cumsum(pop_k[o]) / pop_k.sum(); cc = np.cumsum(ch_k[o])
def share_below(q): return float(np.interp(q, cp, cc) / ch_k.sum())
s20, s80, s40, s90 = share_below(.2), share_below(.8), share_below(.4), share_below(.9)
ratio2020 = (1 - s80) / max(s20, 1e-9)
palma = (1 - s90) / max(s40, 1e-9)

# defisit menuju kesetaraan
mean100k = 1e5 * ch_k.sum() / pop_k.sum()
need = mean100k * pop_k / 1e5
deficit = np.maximum(0, need - ch_k); surplus = np.maximum(0, ch_k - need)
zero = [k for k in KS if k["chargers"] == 0]
top_def = sorted([(KS[i]["name"], pi_name[KS[i]["prov"]], float(deficit[i]), KS[i]["pop"], KS[i]["chargers"])
                  for i in range(len(KS))], key=lambda x: -x[2])[:15]
top_sur = sorted([(KS[i]["name"], pi_name[KS[i]["prov"]], float(surplus[i]), KS[i]["pop"], KS[i]["chargers"])
                  for i in range(len(KS))], key=lambda x: -x[2])[:10]
top10 = sorted(KS, key=lambda k: -k["chargers"])[:10]

# ------------------------------------------------------------------ 2) ekuitas vertikal
pop_p = np.zeros(len(PROVS)); ch_p = np.zeros(len(PROVS)); w10_p = np.zeros(len(PROVS)); b25_p = np.zeros(len(PROVS))
for k in KS:
    pop_p[k["prov"]] += k["pop"]; ch_p[k["prov"]] += k["chargers"]
    w10_p[k["prov"]] += k["pop"] * k["within10"] / 100; b25_p[k["prov"]] += k["pop"] * k["beyond25"] / 100
grdp = np.array([p["grdp"] for p in PROVS], float); hdi = np.array([p["hdi"] for p in PROVS], float)
pov = np.array([p["poverty"] for p in PROVS], float)
ci_grdp, cc_grdp = concentration(pop_p, ch_p, grdp)
ci_hdi, cc_hdi = concentration(pop_p, ch_p, hdi)
ci_pov, cc_pov = concentration(pop_p, ch_p, -pov)          # miskin (tinggi) -> kaya (rendah)
ci_acc_grdp, cc_acc_grdp = concentration(pop_p, w10_p, grdp)
# kepadatan kabupaten sebagai gradien urban (tanpa data pendapatan kabupaten)
dens = np.array([k["pop"] / max(k["hex"], 1) for k in KS])
ci_dens, cc_dens = concentration(pop_k, ch_k, dens)
# kuintil provinsi menurut PDRB/kapita (tertimbang penduduk)
op = np.argsort(grdp); cum = np.cumsum(pop_p[op]) / pop_p.sum()
quint = []
for q in range(5):
    m = [op[i] for i in range(len(op)) if (q / 5) < cum[i] <= ((q + 1) / 5) or (q == 0 and cum[i] <= .2)]
    m = sorted(set(m))
    if not m: continue
    P = pop_p[m].sum()
    quint.append(dict(q=q + 1, provs=[pi_name[i] for i in m], pop=round(float(P)),
                      per100k=round(1e5 * ch_p[m].sum() / P, 2), within10=round(100 * w10_p[m].sum() / P, 1),
                      beyond25=round(100 * b25_p[m].sum() / P, 1),
                      grdp=round(float(np.average(grdp[m], weights=pop_p[m])), 1),
                      poverty=round(float(np.average(pov[m], weights=pop_p[m])), 1)))
prov_rows = [dict(name=pi_name[i], pop=round(float(pop_p[i])), chargers=int(ch_p[i]), per100k=round(1e5 * ch_p[i] / pop_p[i], 2),
                  within10=round(100 * w10_p[i] / pop_p[i], 1), beyond25=round(100 * b25_p[i] / pop_p[i], 1),
                  grdp=float(grdp[i]), hdi=float(hdi[i]), poverty=float(pov[i])) for i in range(len(PROVS)) if pop_p[i] > 0]

# ------------------------------------------------------------------ 2b) ekuitas vertikal tingkat kabupaten (opsional)
# Membutuhkan input/kabupaten_sosek.csv dari equitymap/sosek.py (tabel BPS: kemiskinan, IPM, pengeluaran per kapita).
sosek = None
_sp = os.path.join(HERE, "input", "kabupaten_sosek.csv")
if os.path.exists(_sp):
    _rows = {int(r["idx"]): r for r in csv.DictReader(open(_sp, encoding="utf-8"))}
    _ok = [i for i, k in enumerate(KS) if k["idx"] in _rows and all(_rows[k["idx"]].get(c, "") != "" for c in ("poverty", "hdi", "expend"))]
    if len(_ok) >= 100:
        m = np.array(_ok)
        pov_k = np.array([float(_rows[KS[i]["idx"]]["poverty"]) for i in _ok]); hdi_k = np.array([float(_rows[KS[i]["idx"]]["hdi"]) for i in _ok])
        exp_k = np.array([float(_rows[KS[i]["idx"]]["expend"]) for i in _ok])
        b25_k = np.array([KS[i]["beyond25"] for i in _ok]); w10_k_ = np.array([KS[i]["within10"] for i in _ok])
        acc_m = pop_k[m] * w10_k_ / 100
        ci_kpov, cc_kpov = concentration(pop_k[m], ch_k[m], -pov_k)
        ci_khdi, cc_khdi = concentration(pop_k[m], ch_k[m], hdi_k)
        ci_kexp, cc_kexp = concentration(pop_k[m], ch_k[m], exp_k)
        ci_kacc, cc_kacc = concentration(pop_k[m], acc_m, exp_k)
        # kuintil kabupaten menurut pengeluaran per kapita, tertimbang penduduk
        oe = np.argsort(exp_k); cume = np.cumsum(pop_k[m][oe]) / pop_k[m].sum(); kq = []
        for q in range(5):
            sel = [oe[j] for j in range(len(oe)) if (q / 5) < cume[j] <= ((q + 1) / 5) or (q == 0 and cume[j] <= .2)]
            if not sel: continue
            sel = np.array(sorted(set(sel))); P = pop_k[m][sel].sum()
            kq.append(dict(q=q + 1, n=len(sel), pop=round(float(P)), per100k=round(1e5 * ch_k[m][sel].sum() / P, 2),
                           within10=round(float(np.average(w10_k_[sel], weights=pop_k[m][sel])), 1),
                           beyond25=round(float(np.average(b25_k[sel], weights=pop_k[m][sel])), 1),
                           expend=round(float(np.average(exp_k[sel], weights=pop_k[m][sel]))), poverty=round(float(np.average(pov_k[sel], weights=pop_k[m][sel])), 1),
                           hdi=round(float(np.average(hdi_k[sel], weights=pop_k[m][sel])), 1),
                           zero=int((ch_k[m][sel] == 0).sum())))
        # CI dalam-provinsi (provinsi dengan ≥8 kabupaten bernilai)
        prov_ci = []
        for p in range(len(PROVS)):
            sel = np.array([j for j, i in enumerate(_ok) if prov_k[i] == p])
            if len(sel) < 8 or ch_k[m][sel].sum() == 0: continue
            prov_ci.append(dict(name=pi_name[p], n=int(len(sel)), ci_expend=concentration(pop_k[m][sel], ch_k[m][sel], exp_k[sel])[0],
                                ci_hdi=concentration(pop_k[m][sel], ch_k[m][sel], hdi_k[sel])[0],
                                ci_poverty=concentration(pop_k[m][sel], ch_k[m][sel], -pov_k[sel])[0]))
        prov_ci.sort(key=lambda x: -x["ci_expend"])
        from scipy.stats import spearmanr as _sp_r
        rho_exp = float(_sp_r(exp_k, ch_k[m] / pop_k[m]).statistic); rho_hdi = float(_sp_r(hdi_k, ch_k[m] / pop_k[m]).statistic)
        sosek = dict(n=len(_ok), pop_pct=round(100 * pop_k[m].sum() / pop_k.sum(), 1),
                     ci=dict(poverty=ci_kpov, hdi=ci_khdi, expend=ci_kexp, access_expend=ci_kacc),
                     curves=dict(poverty=cc_kpov, hdi=cc_khdi, expend=cc_kexp, access_expend=cc_kacc),
                     quint=kq, prov_ci=prov_ci, rho=dict(expend=round(rho_exp, 3), hdi=round(rho_hdi, 3)))
        print(f"sosek kabupaten: n={len(_ok)} · CI kemiskinan {ci_kpov} · IPM {ci_khdi} · pengeluaran {ci_kexp} · akses~pengeluaran {ci_kacc} · ρ {rho_exp:.2f}/{rho_hdi:.2f}")
    else:
        print(f"sosek kabupaten: hanya {len(_ok)} kabupaten lengkap — dilewati (perlu ≥100)")

# ------------------------------------------------------------------ 3) kurva cakupan marjinal (greedy)
H = [r[ci["h3"]] for r in R6]; idx = {h: i for i, h in enumerate(H)}
d0 = np.array([r[ci["d_spklu"]] for r in R6]); kab_h = np.array([r[ci["kab"]] for r in R6])
prov_h = np.array([KABS[k]["prov"] for k in kab_h])
burden = np.array([PROVS[p]["burden"] for p in prov_h]); bw = 1 + (burden - burden.min()) / (burden.max() - burden.min() + 1e-9)  # 1..2
disk = [[idx[n] for n in h3.grid_disk(h, 2) if n in idx] for h in H]
P0 = pop_h.sum(); cov0 = pop_h[d0 <= COVER_KM].sum()


def greedy(weight):
    covered = d0 <= COVER_KM
    gain = np.array([sum(pop_h[j] * weight[j] for j in dk if not covered[j]) for dk in disk])
    heap = [(-g, i) for i, g in enumerate(gain) if g > 0]; heapq.heapify(heap)
    curve, picks = [], []
    cov = cov0
    while len(picks) < N_NEW and heap:
        g, i = heapq.heappop(heap)
        # lazy re-evaluation
        g2 = sum(pop_h[j] * weight[j] for j in disk[i] if not covered[j])
        if g2 <= 0: continue
        if heap and g2 < -heap[0][0] - 1e-9:
            heapq.heappush(heap, (-g2, i)); continue
        newpop = 0.0
        for j in disk[i]:
            if not covered[j]:
                covered[j] = True; newpop += pop_h[j]
        cov += newpop
        lat, lng = h3.cell_to_latlng(H[i])
        picks.append(dict(kab=KABS[kab_h[i]]["name"], prov=pi_name[prov_h[i]], pop=round(newpop), lat=round(lat, 3), lng=round(lng, 3)))
        curve.append(round(100 * cov / P0, 2))
    return curve, picks


curve_eq, picks_eq = greedy(np.ones(len(H)))
curve_ek, picks_ek = greedy(bw)
# cakupan penduduk provinsi termiskin (kuintil 1) sepanjang kurva ekuitas vs kesetaraan — dihitung ulang sederhana
def q1_cov(picks):
    covered = d0 <= COVER_KM
    q1 = set(i for qq in quint[:1] for i, n in enumerate(pi_name) if n in qq["provs"])
    m = np.array([p in q1 for p in prov_h]); out = []
    for p in picks:
        cell = h3.latlng_to_cell(p["lat"], p["lng"], 6); i = idx.get(cell)
        if i is None: out.append(out[-1] if out else 0); continue
        for j in disk[i]: covered[j] = True
        out.append(round(100 * pop_h[m & covered].sum() / pop_h[m].sum(), 2))
    return out
q1_eq, q1_ek = q1_cov(picks_eq), q1_cov(picks_ek)

# ------------------------------------------------------------------ 4) mengapa angka itu keluar — bahan narasi
tot_ch = ch_k.sum(); tot_pop = pop_k.sum()
share = lambda m: (100 * pop_k[m].sum() / tot_pop, 100 * ch_k[m].sum() / tot_ch)
why = dict(
    kab_zero=len(zero), pop_zero=round(float(sum(k["pop"] for k in zero))), pct_pop_zero=round(100 * sum(k["pop"] for k in zero) / tot_pop, 1),
    top10_share=round(100 * sum(k["chargers"] for k in top10) / tot_ch, 1), top10_pop_share=round(100 * sum(k["pop"] for k in top10) / tot_pop, 1),
    top10=[dict(name=k["name"], chargers=k["chargers"], per100k=k["per100k"]) for k in top10],
    java_pop=round(share(mask_java)[0], 1), java_ch=round(share(mask_java)[1], 1),
    dki_pop=round(share(mask_dki)[0], 1), dki_ch=round(share(mask_dki)[1], 1),
    kota_pop=round(share(is_kota)[0], 1), kota_ch=round(share(is_kota)[1], 1),
    median100k=round(float(np.median(ch_k / pop_k * 1e5)), 2), mean100k=round(float(mean100k), 2),
    deficit_total=round(float(deficit.sum())), surplus_total=round(float(surplus.sum())),
    kab_below_mean=int((ch_k / pop_k * 1e5 < mean100k).sum()), n_kab=len(KS),
    within10_nat=E["nat"]["within10"], beyond25_nat=E["nat"]["beyond25"],
    within10_java=kota_kab and java[0]["within10"], within10_luar=java[1]["within10"],
    beyond25_java=java[0]["beyond25"], beyond25_luar=java[1]["beyond25"],
)

payload = dict(
    meta=dict(cover_km=COVER_KM, n_new=N_NEW, source="equitymap/equity.js (master SPKLU 8 Jun 2026 · Kontur 2023 · BPS provinsi ~2023 indikatif)"),
    gini=dict(chargers=gini_ch, kw=gini_kw, sites=gini_site, access=gini_acc, hex=gini_hex, variants=variants,
              lorenz=dict(chargers=lor_ch, kw=lor_kw, sites=lor_site, access=lor_acc, hex=lor_hex)),
    theil=dict(prov=th, kota=th_kota, prov_parts=[dict(name=pi_name[p["g"]], share_pop=round(100 * p["share_pop"], 1),
                                                       share_val=round(100 * p["share_val"], 1), T=round(p["T"], 3)) for p in th["parts"]]),
    kota_kab=kota_kab, java=java, ratio2020=round(ratio2020, 1), palma=round(palma, 1), s20=round(100 * s20, 1), s80=round(100 * (1 - s80), 1),
    deficit=dict(mean100k=round(float(mean100k), 2), total=round(float(deficit.sum())), surplus=round(float(surplus.sum())),
                 top=[dict(name=n, prov=p, deficit=round(d), pop=pp, chargers=c) for n, p, d, pp, c in top_def],
                 top_surplus=[dict(name=n, prov=p, surplus=round(s), pop=pp, chargers=c) for n, p, s, pp, c in top_sur]),
    ci=dict(grdp=ci_grdp, hdi=ci_hdi, poverty=ci_pov, access_grdp=ci_acc_grdp, density=ci_dens,
            curves=dict(grdp=cc_grdp, hdi=cc_hdi, poverty=cc_pov, access_grdp=cc_acc_grdp, density=cc_dens)),
    quint=quint, prov=prov_rows, sosek=sosek,
    coverage=dict(base=round(100 * cov0 / P0, 2), eq=curve_eq, ek=curve_ek, q1_eq=q1_eq, q1_ek=q1_ek,
                  picks_eq=picks_eq[:40], picks_ek=picks_ek[:40], q1_provs=quint[0]["provs"] if quint else []),
    why=why,
)
json.dump(payload, open(os.path.join(HERE, "keadilan.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"Gini charger/kapita kab {gini_ch} · kW {gini_kw} · situs {gini_site} · akses {gini_acc} · heksagon {gini_hex}")
print("varian:", variants)
print(f"Theil T {th['T']} · antar-provinsi {th['between']} ({th['between_pct']} %) · dalam {th['within']} ; kota/kab antar {th_kota['between_pct']} %")
print("kota vs kab:", kota_kab); print("jawa:", java)
print(f"20:20 {ratio2020:.1f} · Palma {palma:.1f} · 20% terbawah {100*s20:.1f}% charger, 20% teratas {100*(1-s80):.1f}%")
print(f"CI PDRB {ci_grdp} · IPM {ci_hdi} · kemiskinan {ci_pov} · akses~PDRB {ci_acc_grdp} · kepadatan {ci_dens}")
print("kuintil:", [(q['q'], q['per100k'], q['within10']) for q in quint])
print(f"defisit {deficit.sum():.0f} charger · surplus {surplus.sum():.0f} · rata-rata {mean100k:.2f}/100k")
print(f"cakupan {100*cov0/P0:.1f}% -> +100 situs: kesetaraan {curve_eq[99]} % / ekuitas {curve_ek[99]} % · +300: {curve_eq[-1]} / {curve_ek[-1]}; kuintil-1: {q1_eq[-1]} vs {q1_ek[-1]}")
print("why:", why)
