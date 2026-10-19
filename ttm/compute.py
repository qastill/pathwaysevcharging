"""Hitung aksesibilitas desa -> SPKLU dan ukuran (ke)setaraan/(ke)adilan untuk tab ⏱️ Akses Waktu Tempuh.

Dua mode, dipilih otomatis:
  TTM     bila ttm/input/west_java_ttm_car.csv[.gz] ada (keluaran r5r supervisor: from_id,to_id,travel_time_p50,
          menit, mobil, maks 60 menit): waktu tempuh ke desa ber-SPKLU terdekat, charger terjangkau <=10/30 menit (uji 7/15),
          E2SFCA kW per rumah tangga (catchment 7/10/15 menit) dan tangga layanan anak tangga 1-2,
          desa terjangkau <=30 menit (replikasi peta WestJava_Access30_Car.png).
  JARAK   bila belum ada: jarak garis lurus (km) ke lokasi SPKLU terdekat dan charger dalam 5/10 km. Ukuran antara,
          diberi label; bukan pengganti waktu tempuh.

Kebutuhan dihitung dari penduduk Kontur 2023 (H3 res 8, ~0,74 km2) yang dijatuhkan ke poligon desa.

Masukan: ttm/input/{villages.csv, spklu_village.csv, spklu_sites.csv, villages_simplified.geojson}
         --kontur PATH  GeoPackage Kontur Indonesia (kontur_population_ID_20231101.gpkg)
Keluaran: ttm/ttm.json (ringkasan, tabel kab/kota & metropolitan, nilai per desa untuk peta)

  python3 ttm/compute.py --kontur /path/kontur_ID.gpkg
"""
import argparse, csv, gzip, json, math, os, sqlite3, sys
import numpy as np
from scipy import sparse
import h3
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = os.path.join(ROOT, "ttm", "input")
ap = argparse.ArgumentParser()
ap.add_argument("--kontur", default=None)
ap.add_argument("--pop-cache", default=os.path.join(INP, "village_pop.csv"))
ap.add_argument("--hh-size", type=float, default=3.6, help="jiwa per rumah tangga (BPS 2020 Jabar ~3,6) untuk E2SFCA")
ap.add_argument("--kw-per-hh", type=float, default=0.03, help="ambang kecukupan daya E2SFCA, kW per rumah tangga")
a = ap.parse_args()

V = list(csv.DictReader(open(os.path.join(INP, "villages.csv"))))
for v in V:
    v["lon"], v["lat"], v["area_km2"] = float(v["lon"]), float(v["lat"]), float(v["area_km2"])
vid = {v["id"]: i for i, v in enumerate(V)}
SP = {r["id"]: r for r in csv.DictReader(open(os.path.join(INP, "spklu_village.csv")))}
for r in SP.values():
    for k in ("sites", "chargers", "connectors", "pln", "nonpln", "available", "offline"): r[k] = int(r[k])
    r["kw"] = float(r["kw"])
SITES = list(csv.DictReader(open(os.path.join(INP, "spklu_sites.csv"))))
for s in SITES:
    s["lon"], s["lat"], s["kw"], s["chargers"] = float(s["lon"]), float(s["lat"]), float(s["kw"]), int(s["chargers"])
chg = np.array([SP[v["id"]]["chargers"] if v["id"] in SP else 0 for v in V], float)
n = len(V)

# ----------------------------------------------------------------- penduduk per desa (Kontur -> desa)
if os.path.exists(a.pop_cache):
    pop = np.array([float(r["pop"]) for r in csv.DictReader(open(a.pop_cache))])
    assert len(pop) == n
else:
    assert a.kontur, "butuh --kontur saat village_pop.csv belum ada"
    gj = json.load(open(os.path.join(INP, "villages_simplified.geojson")))
    geoms = [shape(f["geometry"]) for f in gj["features"]]
    gid = [f["properties"]["id"] for f in gj["features"]]
    assert gid == [v["id"] for v in V]
    tree = STRtree(geoms)
    minx, miny, maxx, maxy = 105.0, -8.0, 109.2, -5.6
    pop = np.zeros(n)
    con = sqlite3.connect(a.kontur)
    miss = 0.0
    for hx, p in con.execute("select h3, population from population"):
        lat, lng = h3.cell_to_latlng(hx)
        if not (minx <= lng <= maxx and miny <= lat <= maxy): continue
        pt = Point(lng, lat)
        hit = [i for i in tree.query(pt) if geoms[i].covers(pt)]
        if hit: pop[hit[0]] += p
        else: miss += p
    with open(a.pop_cache, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "pop"]); w.writerows((v["id"], round(pop[i])) for i, v in enumerate(V))
    print("penduduk area studi: %.1f jt; heksagon di kotak tapi di luar desa: %.1f jt" % (pop.sum() / 1e6, miss / 1e6))
dens = pop / np.maximum(V_area := np.array([v["area_km2"] for v in V]), 0.01)

# ----------------------------------------------------------------- akses
ttm_path = next((p for p in (os.path.join(INP, "west_java_ttm_car.csv.gz"), os.path.join(INP, "west_java_ttm_car.csv")) if os.path.exists(p)), None)
spk_ids = set(SP)
if ttm_path:
    MODE = "ttm"; UNIT = "menit"; TH = (10, 30); CUT = 60; REACH_T = (7, 10, 15, 30)
    # crosswalk id GADM 4.1 -> BPS 2020 (ttm/crosswalk.py)
    CW = {}
    cwp = os.path.join(INP, "id_crosswalk.csv")
    if os.path.exists(cwp):
        CW = {r["gadm_id"]: r["bps_id"] for r in csv.DictReader(open(cwp)) if r["bps_id"]}
    FI, TI, TT = [], [], []
    unknown_from, unknown_to, rows = set(), set(), 0
    op = gzip.open if ttm_path.endswith(".gz") else open
    with op(ttm_path, "rt") as f:
        rd = csv.DictReader(f)
        tcol = "travel_time_p50" if "travel_time_p50" in rd.fieldnames else [c for c in rd.fieldnames if c.startswith("travel_time")][0]
        for r in rd:
            rows += 1
            a_, b_ = str(r["from_id"]).strip(), str(r["to_id"]).strip()
            fi = vid.get(a_); fi = vid.get(CW.get(a_, "")) if fi is None else fi
            if fi is None: unknown_from.add(a_); continue
            ti = vid.get(b_); ti = vid.get(CW.get(b_, "")) if ti is None else ti
            if ti is None: unknown_to.add(b_); continue
            t = r[tcol]
            if t in ("", "NA"): continue
            FI.append(fi); TI.append(ti); TT.append(float(t))
    FI = np.array(FI, np.int32); TI = np.array(TI, np.int32); TT = np.array(TT, np.float32)
    seen = np.zeros(n, bool); seen[FI] = True
    is_sp = np.array([v["id"] in SP for v in V])
    kw_v = np.array([SP[v["id"]]["kw"] if v["id"] in SP else 0.0 for v in V])
    # waktu ke desa ber-SPKLU terdekat; charger terjangkau per ambang; desa terjangkau <=30
    best = np.full(n, np.inf); tosp = is_sp[TI]
    np.minimum.at(best, FI[tosp], TT[tosp])
    reach_ch = {}
    for T in REACH_T:
        m = tosp & (TT <= T); c = np.zeros(n); np.add.at(c, FI[m], chg[TI[m]]); reach_ch[T] = c
    v30 = np.zeros(n); np.add.at(v30, FI[TT <= 30], 1)
    # E2SFCA (binary catchment): langkah 1 rasio kW per rumah tangga di tiap desa ber-SPKLU, langkah 2 jumlah rasio yang tercapai
    HH = pop / a.hh_size
    cap = {}
    for T in (7, 10, 15):
        m = TT <= T
        M = sparse.csr_matrix((np.ones(m.sum(), np.float32), (FI[m], TI[m])), shape=(n, n))
        demand = np.asarray(M.T @ HH).ravel()                      # rumah tangga dalam catchment tiap desa tujuan j
        R = np.where(demand > 0, kw_v / np.maximum(demand, 1e-9), 0.0)
        cap[T] = np.asarray(M @ R).ravel()                         # kW per rumah tangga yang tercapai dari desa i
    # desa tanpa baris (GADM/BPS tak cocok): nilai diambil dari desa ber-baris terdekat <= 5 km, ditandai
    imputed = 0; dropped = 0
    sx = np.radians(np.array([v["lon"] for v in V])); sy = np.radians(np.array([v["lat"] for v in V]))
    for i in np.where(~seen)[0]:
        d = 6371.0 * np.arccos(np.clip(np.sin(sy[i]) * np.sin(sy) + np.cos(sy[i]) * np.cos(sy) * np.cos(sx - sx[i]), -1, 1)); d[~seen] = np.inf
        j = int(np.argmin(d))
        if d[j] <= 5:
            best[i] = best[j]; v30[i] = v30[j]
            for T in REACH_T: reach_ch[T][i] = reach_ch[T][j]
            for T in cap: cap[T][i] = cap[T][j]
            imputed += 1
        else: dropped += 1
    print("TTM baris %d; asal tak dikenal %d; tujuan tak dikenal %d; desa tanpa baris %d (diimputasi %d, tak terjangkau %d)"
          % (rows, len(unknown_from), len(unknown_to), int((~seen).sum()), imputed, dropped))
    access = best                      # menit ke desa ber-SPKLU terdekat; inf = >60 menit / tak terjangkau
    near, far = reach_ch[TH[0]], reach_ch[TH[1]]
    extra = dict(villages30=v30.tolist(), rows=rows, unknown_from=len(unknown_from), unknown_to=len(unknown_to), unseen=int((~seen).sum()),
                 imputed=imputed, dropped=dropped, crosswalk=len(CW), hh_size=a.hh_size, kw_per_hh=a.kw_per_hh)
else:
    MODE = "jarak"; UNIT = "km"; TH = (5, 10); CUT = 50
    sx = np.radians(np.array([s["lon"] for s in SITES])); sy = np.radians(np.array([s["lat"] for s in SITES]))
    sc = np.array([max(1, s["chargers"]) for s in SITES], float)
    vx = np.radians(np.array([v["lon"] for v in V])); vy = np.radians(np.array([v["lat"] for v in V]))
    access = np.zeros(n); near = np.zeros(n); far = np.zeros(n)
    for i in range(n):
        d = 6371.0 * np.arccos(np.clip(np.sin(vy[i]) * np.sin(sy) + np.cos(vy[i]) * np.cos(sy) * np.cos(sx - vx[i]), -1, 1))
        access[i] = d.min(); near[i] = sc[d <= TH[0]].sum(); far[i] = sc[d <= TH[1]].sum()
    extra = {}
acc_cap = np.where(np.isfinite(access), access, CUT)

# ----------------------------------------------------------------- ukuran
def wgini(x, w):
    o = np.argsort(x); x, w = x[o], w[o]
    cw = np.cumsum(w) / w.sum(); cx = np.cumsum(x * w) / (x * w).sum() if (x * w).sum() > 0 else cw
    return float(1 - np.sum((cw[1:] - cw[:-1]) * (cx[1:] + cx[:-1])) - cw[0] * cx[0])

def lorenz(x, w, k=40):
    o = np.argsort(x); x, w = x[o], w[o]
    cw = np.concatenate([[0], np.cumsum(w) / w.sum()]); cx = np.concatenate([[0], np.cumsum(x * w) / max((x * w).sum(), 1e-9)])
    q = np.linspace(0, 1, k + 1)
    return [[round(float(p), 3), round(float(np.interp(p, cw, cx)), 3)] for p in q]

def conc_index(h, rank, w):
    """Indeks konsentrasi (Wagstaff) variabel h, unit diurut menaik menurut rank, bobot w (penduduk)."""
    o = np.argsort(rank, kind="stable"); h, w = h[o], w[o]
    w = w / w.sum(); r = np.cumsum(w) - w / 2
    mu = np.sum(w * h)
    return float(2 * np.sum(w * h * (r - 0.5)) / mu) if mu > 0 else 0.0

def erreygers(h, rank, w, lo, hi):
    o = np.argsort(rank, kind="stable"); h, w = h[o], w[o]
    w = w / w.sum(); r = np.cumsum(w) - w / 2
    return float(8 * np.sum(w * h * (r - 0.5)) / (hi - lo))

within1 = acc_cap <= TH[0]; within2 = acc_cap <= TH[1]
P = pop.sum()
summary = dict(mode=MODE, unit=UNIT, th=list(TH), cut=CUT, n_villages=n, pop=round(P),
               n_spklu_villages=len(SP), sites=len(SITES), chargers=int(chg.sum()),
               pop_within1=round(float(pop[within1].sum())), pop_within2=round(float(pop[within2].sum())),
               vil_within1=int(within1.sum()), vil_within2=int(within2.sum()),
               pop_beyond=round(float(pop[~np.isfinite(access) if MODE == "ttm" else acc_cap > TH[1]].sum())),
               median_access_pop=float(np.interp(0.5, np.cumsum(pop[np.argsort(acc_cap)]) / P, np.sort(acc_cap))),
               mean_access_pop=float(np.sum(acc_cap * pop) / P),
               gini_far=wgini(far, pop), gini_near=wgini(near, pop),
               gini_chargers_village=wgini(chg, pop), **extra)

# distribusi akses (histogram penduduk & desa)
edges = list(range(0, CUT + 1, 5 if MODE == "ttm" else 5))
hist_pop = np.histogram(acc_cap, bins=edges, weights=pop)[0]; hist_vil = np.histogram(acc_cap, bins=edges)[0]
summary["hist"] = dict(edges=edges, pop=[round(float(x)) for x in hist_pop], villages=[int(x) for x in hist_vil])
summary["lorenz_far"] = lorenz(far, pop)
summary["lorenz_pop_vs_chargers"] = lorenz(chg / np.maximum(pop, 1), pop)

# ----------------------------------------------------------------- kab/kota
SOSEK = {}
try:
    for r in csv.DictReader(open(os.path.join(ROOT, "equitymap", "input", "jabar_sosek_kabkota.csv"))):
        SOSEK[r["kode_wilayah"].replace(".", "")] = dict(ipm=float(r["ipm"]), expend=float(r["pengeluaran"]), p0=float(r["miskin_p0"]))
except FileNotFoundError:
    pass
METRO = {"jabodetabek": ("Jabodetabek", {"3171", "3172", "3173", "3174", "3175", "3201", "3271", "3216", "3275", "3276", "3603", "3671", "3674"}),
         "bandung": ("Bandung Raya", {"3204", "3217", "3273", "3277", "3211"}),
         "cirebon": ("Cirebon Raya", {"3209", "3274", "3208", "3210", "3212"})}
def metro_of(k):
    for m, (_, s) in METRO.items():
        if k in s: return m
    return "luar"
kabs = {}
kcode = np.array([v["regency_code"] for v in V])
for k in sorted(set(kcode)):
    m = kcode == k; pk = pop[m].sum()
    v0 = V[int(np.argmax(m))]
    row = dict(code=k, name=v0["regency"], prov=v0["province"], metro=metro_of(k), n=int(m.sum()), pop=round(float(pk)),
               chargers=int(chg[m].sum()), sites=sum(1 for s in SITES if s["regency_code"] == k),
               per100k=round(float(chg[m].sum() / max(pk, 1) * 1e5), 2),
               share1=round(float(pop[m & within1].sum() / max(pk, 1)), 4), share2=round(float(pop[m & within2].sum() / max(pk, 1)), 4),
               vil_share2=round(float((m & within2).sum() / m.sum()), 4),
               median=float(np.interp(0.5, np.cumsum(pop[m][np.argsort(acc_cap[m])]) / max(pk, 1), np.sort(acc_cap[m]))) if pk > 0 else None,
               far_mean=round(float(np.sum(far[m] * pop[m]) / max(pk, 1)), 1),
               area=round(float(V_area[m].sum())), gini_far=wgini(far[m], pop[m]) if pk > 0 and far[m].sum() > 0 else None)
    row.update(SOSEK.get(k, {}))
    kabs[k] = row
# ekuitas: CI menurut peringkat kab/kota (variabel peringkat tingkat kab/kota, unit = desa, bobot penduduk)
rank_dens = dens
ci = dict(density=conc_index(far, rank_dens, pop), density_share2=erreygers(within2.astype(float), rank_dens, pop, 0, 1),
          density_access=conc_index(acc_cap, rank_dens, pop))
if SOSEK:
    jb = np.array([v["regency_code"] in SOSEK for v in V])
    exp_r = np.array([SOSEK[v["regency_code"]]["expend"] if v["regency_code"] in SOSEK else np.nan for v in V])
    ipm_r = np.array([SOSEK[v["regency_code"]]["ipm"] if v["regency_code"] in SOSEK else np.nan for v in V])
    ci.update(expend=conc_index(far[jb], exp_r[jb], pop[jb]), expend_share2=erreygers(within2[jb].astype(float), exp_r[jb], pop[jb], 0, 1),
              expend_access=conc_index(acc_cap[jb], exp_r[jb], pop[jb]),
              ipm=conc_index(far[jb], ipm_r[jb], pop[jb]), ipm_share2=erreygers(within2[jb].astype(float), ipm_r[jb], pop[jb], 0, 1),
              n_jabar_pop=round(float(pop[jb].sum())))
    # kuintil penduduk menurut pengeluaran per kapita kab/kota (Jabar)
    o = np.argsort(exp_r[jb], kind="stable"); cp = np.cumsum(pop[jb][o]) / pop[jb].sum()
    qs = []
    for q in range(5):
        sel = (cp > q / 5) & (cp <= (q + 1) / 5); idx = np.where(jb)[0][o][sel]
        qs.append(dict(q=q + 1, pop=round(float(pop[idx].sum())), share2=round(float(pop[idx][within2[idx]].sum() / max(pop[idx].sum(), 1)), 4),
                       share1=round(float(pop[idx][within1[idx]].sum() / max(pop[idx].sum(), 1)), 4),
                       far=round(float(np.sum(far[idx] * pop[idx]) / max(pop[idx].sum(), 1)), 1),
                       median=float(np.interp(0.5, np.cumsum(pop[idx][np.argsort(acc_cap[idx])]) / max(pop[idx].sum(), 1), np.sort(acc_cap[idx]))),
                       per100k=round(float(chg[idx].sum() / max(pop[idx].sum(), 1) * 1e5), 2)))
    summary["quintiles_expend"] = qs
summary["ci"] = ci
# kesetaraan antar kab/kota: Gini charger per kapita (unit kab/kota, bobot penduduk) dan Gini pangsa terjangkau
kk = list(kabs.values())
summary["gini_kab_per100k"] = wgini(np.array([r["per100k"] for r in kk]), np.array([r["pop"] for r in kk], float))
summary["gini_kab_share2"] = wgini(np.array([r["share2"] for r in kk]), np.array([r["pop"] for r in kk], float))
# metropolitan
metros = []
for m, (label, _) in list(METRO.items()) + [("luar", ("Luar metropolitan", None))]:
    sel = np.array([metro_of(k) == m for k in kcode]); pm = pop[sel].sum()
    metros.append(dict(key=m, label=label, n_kab=len({k for k in kcode[sel]}), pop=round(float(pm)), chargers=int(chg[sel].sum()),
                       per100k=round(float(chg[sel].sum() / max(pm, 1) * 1e5), 2),
                       share1=round(float(pop[sel & within1].sum() / max(pm, 1)), 4), share2=round(float(pop[sel & within2].sum() / max(pm, 1)), 4),
                       median=float(np.interp(0.5, np.cumsum(pop[sel][np.argsort(acc_cap[sel])]) / max(pm, 1), np.sort(acc_cap[sel]))),
                       far_mean=round(float(np.sum(far[sel] * pop[sel]) / max(pm, 1)), 1),
                       gini_far=wgini(far[sel], pop[sel]) if far[sel].sum() > 0 else None))
summary["metros"] = metros

if MODE == "ttm":
    # jangkauan menurut ambang (RQ1 anak tangga 1: <=10 menit, uji 7 dan 15; 30 = replikasi peta supervisor)
    summary["reach"] = {str(T): dict(pop=round(float(pop[acc_cap <= T].sum())), share=round(float(pop[acc_cap <= T].sum() / P), 4), villages=int((acc_cap <= T).sum()),
                                     chargers_mean=round(float(np.sum(reach_ch[T] * pop) / P), 1)) for T in REACH_T}
    # kecukupan daya E2SFCA (anak tangga 2): kW per rumah tangga dalam catchment waktu tempuh, ambang kw_per_hh
    summary["e2sfca"] = {}
    for T, A in cap.items():
        suff = A >= a.kw_per_hh
        summary["e2sfca"][str(T)] = dict(pop_sufficient=round(float(pop[suff].sum())), share=round(float(pop[suff].sum() / P), 4), villages=int(suff.sum()),
                                         median_pop=round(float(np.interp(0.5, np.cumsum(pop[np.argsort(A)]) / P, np.sort(A))), 4),
                                         mean_pop=round(float(np.sum(A * pop) / P), 4), gini=wgini(A, pop),
                                         ci_density=conc_index(A, rank_dens, pop))
        if SOSEK: summary["e2sfca"][str(T)].update(ci_expend=conc_index(A[jb], exp_r[jb], pop[jb]), ci_ipm=conc_index(A[jb], ipm_r[jb], pop[jb]),
                                                   ci_suff_expend=erreygers(suff[jb].astype(float), exp_r[jb], pop[jb], 0, 1))
    A10 = cap[10]; rung = np.where(acc_cap > 10, 0, np.where(A10 >= a.kw_per_hh, 2, 1))
    summary["ladder"] = dict(th_min=10, kw_per_hh=a.kw_per_hh, hh_size=a.hh_size,
                             rungs=[dict(rung=k, label=l, pop=round(float(pop[rung == k].sum())), share=round(float(pop[rung == k].sum() / P), 4), villages=int((rung == k).sum()))
                                    for k, l in ((0, "tidak terjangkau (>10 menit)"), (1, "terjangkau, daya tidak cukup"), (2, "terjangkau dan daya cukup"))])
    for k, row in kabs.items():
        m = kcode == k; pk = max(pop[m].sum(), 1)
        row.update(reach7=round(float(pop[m & (acc_cap <= 7)].sum() / pk), 4), reach15=round(float(pop[m & (acc_cap <= 15)].sum() / pk), 4),
                   suff10=round(float(pop[m & (A10 >= a.kw_per_hh)].sum() / pk), 4), cap10_med=round(float(np.interp(0.5, np.cumsum(pop[m][np.argsort(A10[m])]) / pk, np.sort(A10[m]))), 4))
    for mrow in summary["metros"]:
        sel = np.array([metro_of(k) == mrow["key"] for k in kcode]); pm = max(pop[sel].sum(), 1)
        mrow.update(reach7=round(float(pop[sel & (acc_cap <= 7)].sum() / pm), 4), reach15=round(float(pop[sel & (acc_cap <= 15)].sum() / pm), 4),
                    suff10=round(float(pop[sel & (A10 >= a.kw_per_hh)].sum() / pm), 4))
    if SOSEK:
        o = np.argsort(exp_r[jb], kind="stable"); cp = np.cumsum(pop[jb][o]) / pop[jb].sum()
        for q, qrow in enumerate(summary["quintiles_expend"]):
            sel = (cp > q / 5) & (cp <= (q + 1) / 5); idx = np.where(jb)[0][o][sel]; pq = max(pop[idx].sum(), 1)
            qrow.update(reach7=round(float(pop[idx][acc_cap[idx] <= 7].sum() / pq), 4), reach15=round(float(pop[idx][acc_cap[idx] <= 15].sum() / pq), 4),
                        suff10=round(float(pop[idx][A10[idx] >= a.kw_per_hh].sum() / pq), 4), cap10_mean=round(float(np.sum(A10[idx] * pop[idx]) / pq), 4))

# ----------------------------------------------------------------- per desa (untuk peta)
villages = [[v["id"], round(float(acc_cap[i]), 1) if np.isfinite(access[i]) else None, int(near[i]), int(far[i]), round(float(pop[i])),
             int(chg[i]), (int(extra["villages30"][i]) if MODE == "ttm" else None), round(v["area_km2"], 2),
             (round(float(cap[10][i]), 4) if MODE == "ttm" else None), (int(rung[i]) if MODE == "ttm" else None)] for i, v in enumerate(V)]
out = dict(summary=summary, kabs=kk, village_cols=["id", "access", "near", "far", "pop", "chargers", "villages30", "area", "cap10", "rung"], villages=villages,
           names={v["id"]: [v["village"], v["district"], v["regency"]] for v in V})
json.dump(out, open(os.path.join(ROOT, "ttm", "ttm.json"), "w"), separators=(",", ":"), ensure_ascii=False)
print("mode:", MODE, "| penduduk %.2f jt | <=%d %s: %.1f%% | <=%d %s: %.1f%% | Gini charger terjangkau %.3f | CI~kepadatan %.3f"
      % (P / 1e6, TH[0], UNIT, 100 * summary["pop_within1"] / P, TH[1], UNIT, 100 * summary["pop_within2"] / P, summary["gini_far"], ci["density"]))
if MODE == "ttm": print("jangkauan:", {T: r["share"] for T, r in summary["reach"].items()}, "| E2SFCA cukup (>=%.2f kW/RT):" % a.kw_per_hh, {T: r["share"] for T, r in summary["e2sfca"].items()},
                       "| tangga:", [(r["rung"], r["share"]) for r in summary["ladder"]["rungs"]])
if SOSEK: print("CI~pengeluaran (Jabar) %.3f | CI~IPM %.3f | kuintil: %s" % (ci["expend"], ci["ipm"], [(q["q"], q["share2"]) for q in summary["quintiles_expend"]]))
print("ttm/ttm.json %.0f KB" % (os.path.getsize(os.path.join(ROOT, "ttm", "ttm.json")) / 1024))
