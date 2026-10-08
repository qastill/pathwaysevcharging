"""Hitung aksesibilitas desa -> SPKLU dan ukuran (ke)setaraan/(ke)adilan untuk tab ⏱️ Akses Waktu Tempuh.

Dua mode, dipilih otomatis:
  TTM     bila ttm/input/west_java_ttm_car.csv[.gz] ada (keluaran r5r supervisor: from_id,to_id,travel_time_p50,
          menit, mobil, maks 60 menit): waktu tempuh ke desa ber-SPKLU terdekat, charger terjangkau <=15/30 menit,
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
import h3
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = os.path.join(ROOT, "ttm", "input")
ap = argparse.ArgumentParser()
ap.add_argument("--kontur", default=None)
ap.add_argument("--pop-cache", default=os.path.join(INP, "village_pop.csv"))
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
    MODE = "ttm"; UNIT = "menit"; TH = (15, 30); CUT = 60
    best = np.full(n, np.inf); c15 = np.zeros(n); c30 = np.zeros(n); v30 = np.zeros(n); seen = np.zeros(n, bool)
    unknown_from, unknown_to, rows = set(), set(), 0
    op = gzip.open if ttm_path.endswith(".gz") else open
    with op(ttm_path, "rt") as f:
        rd = csv.DictReader(f)
        tcol = "travel_time_p50" if "travel_time_p50" in rd.fieldnames else [c for c in rd.fieldnames if c.startswith("travel_time")][0]
        for r in rd:
            rows += 1
            fi = vid.get(str(r["from_id"]).strip())
            if fi is None: unknown_from.add(r["from_id"]); continue
            t = r[tcol]
            if t in ("", "NA"): continue
            t = float(t); seen[fi] = True
            if t <= 30: v30[fi] += 1
            to = str(r["to_id"]).strip()
            if to not in spk_ids:
                if to not in vid: unknown_to.add(to)
                continue
            c = SP[to]["chargers"]
            if t < best[fi]: best[fi] = t
            if t <= 15: c15[fi] += c
            if t <= 30: c30[fi] += c
    print("TTM baris %d; asal tak dikenal %d; tujuan tak dikenal %d; desa tanpa baris %d" % (rows, len(unknown_from), len(unknown_to), int((~seen).sum())))
    access = best                      # menit ke desa ber-SPKLU terdekat; inf = >60 menit / tak terjangkau
    near, far = c15, c30
    extra = dict(villages30=v30.tolist(), rows=rows, unknown_from=len(unknown_from), unknown_to=len(unknown_to), unseen=int((~seen).sum()))
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

# ----------------------------------------------------------------- per desa (untuk peta)
villages = [[v["id"], round(float(acc_cap[i]), 1) if np.isfinite(access[i]) else None, int(near[i]), int(far[i]), round(float(pop[i])),
             int(chg[i]), (int(extra["villages30"][i]) if MODE == "ttm" else None), round(v["area_km2"], 2)] for i, v in enumerate(V)]
out = dict(summary=summary, kabs=kk, village_cols=["id", "access", "near", "far", "pop", "chargers", "villages30", "area"], villages=villages,
           names={v["id"]: [v["village"], v["district"], v["regency"]] for v in V})
json.dump(out, open(os.path.join(ROOT, "ttm", "ttm.json"), "w"), separators=(",", ":"), ensure_ascii=False)
print("mode:", MODE, "| penduduk %.2f jt | <=%d %s: %.1f%% | <=%d %s: %.1f%% | Gini charger terjangkau %.3f | CI~kepadatan %.3f"
      % (P / 1e6, TH[0], UNIT, 100 * summary["pop_within1"] / P, TH[1], UNIT, 100 * summary["pop_within2"] / P, summary["gini_far"], ci["density"]))
if SOSEK: print("CI~pengeluaran (Jabar) %.3f | CI~IPM %.3f | kuintil: %s" % (ci["expend"], ci["ipm"], [(q["q"], q["share2"]) for q in summary["quintiles_expend"]]))
print("ttm/ttm.json %.0f KB" % (os.path.getsize(os.path.join(ROOT, "ttm", "ttm.json")) / 1024))
