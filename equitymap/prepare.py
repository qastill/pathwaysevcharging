"""Peta Ekuitas SPKLU Indonesia — pipeline indikator per heksagon (padanan EV Equity Roadmap
Berkeley untuk Indonesia). Berjalan TANPA jaringan dari input yang sudah di-commit.

    pip install numpy openpyxl h3 shapely
    python3 equitymap/prepare.py     # -> equitymap/equity.js (payload peta) + equitymap/summary.json
    python3 equitymap/inject.py      # -> pasang tab ke index.html

Sumber di repositori:
  equitymap/input/hex_r6.csv        populasi per heksagon H3 res 6 (Kontur 2023) + kabupaten (geoBoundaries)
  equitymap/input/kabupaten.csv     515 kabupaten/kota -> provinsi
  SPKLU_Indonesia_Lengkap_2026-06-08.xlsx   master 3.212 SPKLU nasional (koordinat, daya, status, charger)
  data/grid-id/*.js                 933 gardu induk (MVA) + 4.052 ruas transmisi (RUPTL/OSM)
  konstanta POP/ECON provinsi       BPS ~2023 indikatif — identik dengan tab 🇮🇩 Indonesia (index.html)

Dua skor, meniru struktur EV Equity Roadmap (prioritas × kelayakan), dihitung dari indikator
mentah per heksagon. Skor default dihitung di sini (bobot DEFAULT); di tab, bobot bisa digeser
dan skor dihitung ulang di browser dengan rumus yang sama (render.js: score()).
"""
import csv, json, math, os, re, glob

import numpy as np
import h3
import openpyxl
from shapely.geometry import LineString
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)

MASTER = "SPKLU_Indonesia_Lengkap_2026-06-08.xlsx"
POP_MIN = 100          # heksagon yang dikirim ke peta (>= 100 jiwa: 31 ribu heksagon, 99,9 % penduduk)
RING_10KM = 2          # grid_disk k=2 pada res 6 ~ radius 10-13 km ("dalam ~10 km")
CAP_KM = 50.0          # jarak dipotong pada 50 km untuk peringkat
DC_KW = 50             # situs >= 50 kW dihitung sebagai DC/fast

# ---- provinsi: populasi (juta, BPS ~2023) dan [PDRB/kapita juta Rp, IPM, kemiskinan %] — indikatif,
#      disalin apa adanya dari tab Indonesia di index.html supaya satu angka di seluruh dashboard.
POP = {'Aceh':5.41,'Sumatera Utara':15.39,'Sumatera Barat':5.70,'Riau':6.73,'Kepulauan Riau':2.18,'Jambi':3.70,
       'Sumatera Selatan':8.74,'Bangka Belitung':1.52,'Bengkulu':2.09,'Lampung':9.18,'Banten':12.25,'DKI Jakarta':10.67,
       'Jawa Barat':49.86,'Jawa Tengah':37.54,'DI Yogyakarta':3.71,'Jawa Timur':41.15,'Bali':4.42,
       'Nusa Tenggara Barat':5.55,'Nusa Tenggara Timur':5.62,'Kalimantan Barat':5.59,'Kalimantan Tengah':2.81,
       'Kalimantan Selatan':4.20,'Kalimantan Timur':3.97,'Kalimantan Utara':0.73,'Sulawesi Utara':2.66,'Gorontalo':1.20,
       'Sulawesi Tengah':3.13,'Sulawesi Barat':1.44,'Sulawesi Selatan':9.36,'Sulawesi Tenggara':2.78,'Maluku':1.92,
       'Maluku Utara':1.36,'Papua Barat':1.18,'Papua':4.32}
ECON = {'Aceh':[40,73.0,14.4],'Sumatera Utara':[62,73.0,8.1],'Sumatera Barat':[56,74.0,5.9],'Riau':[145,74.6,6.7],
        'Kepulauan Riau':[135,77.3,5.6],'Jambi':[78,72.6,7.6],'Sumatera Selatan':[72,71.3,11.2],'Bangka Belitung':[70,73.0,4.5],
        'Bengkulu':[42,72.6,14.0],'Lampung':[53,71.4,11.1],'Banten':[55,73.8,6.2],'DKI Jakarta':[330,83.5,4.4],
        'Jawa Barat':[50,74.2,7.6],'Jawa Tengah':[48,73.4,10.8],'DI Yogyakarta':[40,81.6,11.0],'Jawa Timur':[73,73.4,10.3],
        'Bali':[60,78.0,4.3],'Nusa Tenggara Barat':[38,70.0,13.8],'Nusa Tenggara Timur':[25,66.0,19.9],
        'Kalimantan Barat':[55,69.0,6.7],'Kalimantan Tengah':[78,72.0,5.1],'Kalimantan Selatan':[70,72.0,4.3],
        'Kalimantan Timur':[270,78.2,6.1],'Kalimantan Utara':[175,72.4,6.5],'Sulawesi Utara':[60,73.8,7.4],
        'Gorontalo':[42,70.0,15.0],'Sulawesi Tengah':[95,71.0,12.4],'Sulawesi Barat':[42,67.0,11.5],
        'Sulawesi Selatan':[75,73.0,8.7],'Sulawesi Tenggara':[62,72.2,11.4],'Maluku':[33,71.0,16.0],
        'Maluku Utara':[50,70.0,6.4],'Papua Barat':[78,67.0,21.0],'Papua':[60,62.3,26.0]}

# ---- indikator & bobot default (harus sama dengan render.js: IND / DEFAULT)
PRIO = [("d_spklu", 0.30, +1), ("ppc", 0.25, +1), ("pop", 0.25, +1), ("burden", 0.20, +1)]
FEAS = [("d_gi", 0.30, -1), ("mva25", 0.20, +1), ("d_tx", 0.15, -1), ("pop10", 0.20, +1), ("c10", 0.15, +1)]


def hav(lat1, lng1, lat2, lng2):
    """Jarak haversine (km); lat/lng dalam derajat; broadcasting numpy."""
    R = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dl = np.radians(lng2 - lng1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def nearest_and_within(hlat, hlng, plat, plng, radius, weights=None, chunk=1500):
    """Untuk tiap titik heksagon: jarak terdekat ke himpunan titik, jumlah (dan bobot) dalam radius."""
    n = len(hlat)
    dmin = np.full(n, np.inf)
    cnt = np.zeros(n)
    wsum = np.zeros(n) if weights is not None else None
    if len(plat) == 0:
        return dmin, cnt, wsum
    for s in range(0, n, chunk):
        d = hav(hlat[s:s + chunk, None], hlng[s:s + chunk, None], plat[None, :], plng[None, :])
        dmin[s:s + chunk] = d.min(axis=1)
        m = d <= radius
        cnt[s:s + chunk] = m.sum(axis=1)
        if weights is not None:
            wsum[s:s + chunk] = (m * weights[None, :]).sum(axis=1)
    return dmin, cnt, wsum


def pct_rank(x):
    """Peringkat persentil 0..100 (rata-rata untuk nilai kembar)."""
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    # rata-rata rank untuk nilai sama
    _, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    sums = np.zeros(len(cnt)); np.add.at(sums, inv, r)
    r = sums[inv] / cnt[inv]
    return 100.0 * r / max(len(x) - 1, 1)


def gini_lorenz(pop, val):
    """Gini + kurva Lorenz: unit diurutkan menurut val/pop (per kapita), sumbu = kumulatif pop vs val."""
    pop, val = np.asarray(pop, float), np.asarray(val, float)
    k = (pop > 0)
    pop, val = pop[k], val[k]
    o = np.argsort(np.divide(val, pop))
    cp = np.cumsum(pop[o]) / pop.sum()
    cv = np.cumsum(val[o]) / max(val.sum(), 1e-9)
    cp0, cv0 = np.concatenate([[0], cp]), np.concatenate([[0], cv])
    area = float(np.sum((cp0[1:] - cp0[:-1]) * (cv0[1:] + cv0[:-1]) / 2))
    g = 1 - 2 * area
    pts = [[round(float(a), 3), round(float(b), 3)] for a, b in zip(cp0, cv0)]
    # jarangkan titik untuk payload
    step = max(1, len(pts) // 40)
    pts = pts[::step] + [pts[-1]]
    return round(float(g), 3), pts


# ============================================================================ 1) heksagon
kabs = list(csv.DictReader(open(os.path.join(HERE, "input", "kabupaten.csv"), encoding="utf-8")))
prov_names = sorted(set(k["prov"] for k in kabs), key=lambda p: list(POP).index(p))
prov_idx = {p: i for i, p in enumerate(prov_names)}
for k in kabs:
    k["pi"] = prov_idx[k["prov"]]

rows = list(csv.DictReader(open(os.path.join(HERE, "input", "hex_r6.csv"))))
H = np.array([r["h3"] for r in rows])
pop = np.array([float(r["pop"]) for r in rows])
kab = np.array([int(r["kab"]) for r in rows])
ll = np.array([h3.cell_to_latlng(h) for h in H])
hlat, hlng = ll[:, 0], ll[:, 1]
pi = np.array([kabs[k]["pi"] for k in kab])
print(f"heksagon res 6: {len(H):,} · populasi {pop.sum():,.0f}")

# populasi dalam ~10 km (cincin k=2)
idx = {h: i for i, h in enumerate(H)}
pop10 = np.zeros(len(H))
for i, h in enumerate(H):
    s = 0.0
    for n in h3.grid_disk(h, RING_10KM):
        j = idx.get(n)
        if j is not None:
            s += pop[j]
    pop10[i] = s

# ============================================================================ 2) SPKLU nasional
wb = openpyxl.load_workbook(MASTER, read_only=True)
ws = wb["Master SPKLU Indonesia"]
it = ws.iter_rows(values_only=True)
hdr = [str(c) for c in next(it)]
col = {c: i for i, c in enumerate(hdr)}
spk = []
for r in it:
    if r[col["Latitude"]] in (None, "") or r[col["Longitude"]] in (None, ""):
        continue
    lat, lng = float(r[col["Latitude"]]), float(r[col["Longitude"]])
    if not (-11.5 < lat < 6.5 and 94 < lng < 142):
        continue
    kw = float(re.sub(r"[^\d,\.]", "", str(r[col["Kapasitas (kW)"]] or "0")).replace(",", ".") or 0)
    st = str(r[col["Status"]] or "").strip().lower()
    cat = str(r[col["Kategori"]] or "")
    # 'offline mode' hanya muncul pada situs nonPLN: artinya tidak terpantau sistem PLN, bukan mati.
    # Operasional = PLN available/inuse + seluruh mitra nonPLN; PLN unavailable/maintenance dikecualikan.
    active = (st in ("available", "inuse")) or (cat != "PLN" and st == "offline mode")
    spk.append(dict(id=str(r[col["ID SPKLU"]]), name=str(r[col["Nama SPKLU"]] or ""), lat=lat, lng=lng, kw=kw,
                    ch=int(r[col["Jumlah Charger"]] or 0), con=int(r[col["Jumlah Connector"]] or 0),
                    st=st, active=active, pln=cat == "PLN", cat=cat))
S_ACT = [s for s in spk if s["active"]]
S_PLN = [s for s in spk if s["active"] and s["pln"]]
print(f"SPKLU: {len(spk):,} situs · operasional {len(S_ACT):,} (PLN aktif {len(S_PLN):,} + mitra {len(S_ACT)-len(S_PLN):,}) "
      f"· charger {sum(s['ch'] for s in spk):,}")

alat = np.array([s["lat"] for s in S_ACT]); alng = np.array([s["lng"] for s in S_ACT])
ach = np.array([s["ch"] for s in S_ACT], float)
adc = np.array([1.0 if s["kw"] >= DC_KW else 0.0 for s in S_ACT])
d_spklu, n10, c10 = nearest_and_within(hlat, hlng, alat, alng, 10.0, ach)
_, _, dc10 = nearest_and_within(hlat, hlng, alat, alng, 10.0, adc)
d_any, _, _ = nearest_and_within(hlat, hlng, np.array([s["lat"] for s in spk]), np.array([s["lng"] for s in spk]), 10.0)
# varian PLN saja (situs mitra tidak dihitung) — untuk sakelar "cakupan" di tab
plat_ = np.array([s["lat"] for s in S_PLN]); plng_ = np.array([s["lng"] for s in S_PLN])
d_pln, n10p, c10p = nearest_and_within(hlat, hlng, plat_, plng_, 10.0, np.array([s["ch"] for s in S_PLN], float))
_, _, dc10p = nearest_and_within(hlat, hlng, plat_, plng_, 10.0, np.array([1.0 if s["kw"] >= DC_KW else 0.0 for s in S_PLN]))

# kabupaten tiap situs (heksagon res 6 terdekat yang berpenduduk -> kabupatennya)
for s in spk:
    hh = h3.latlng_to_cell(s["lat"], s["lng"], 6)
    j = idx.get(hh)
    if j is None:
        for n in h3.grid_disk(hh, 3):
            j = idx.get(n)
            if j is not None:
                break
    if j is None:
        d = hav(s["lat"], s["lng"], hlat, hlng)
        j = int(d.argmin())
    s["kab"] = int(kab[j])

# ============================================================================ 3) jaringan (data/grid-id)
gi, tx = [], []
for f in sorted(glob.glob("data/grid-id/*.js")):
    txt = open(f, encoding="utf-8").read()
    obj = {}
    for key in ("substations", "transmission"):   # objek JS berkunci tanpa tanda kutip: ambil tiap GeoJSON-nya
        i = txt.index("{", txt.index(key + ":"))
        obj[key] = json.JSONDecoder().raw_decode(txt, i)[0]
    for ft in obj["substations"]["features"]:
        x, y = ft["geometry"]["coordinates"]
        p = ft["properties"]
        try:
            mva = float(p.get("capacity_mva") or 0)
        except ValueError:
            mva = 0.0
        gi.append(dict(lat=y, lng=x, mva=mva, name=p.get("name", ""), kv=p.get("voltage", "")))
    for ft in obj["transmission"]["features"]:
        g = ft["geometry"]
        lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        for c in lines:
            if len(c) >= 2:
                tx.append(c)
print(f"gardu induk: {len(gi):,} · ruas transmisi: {len(tx):,}")
glat = np.array([g["lat"] for g in gi]); glng = np.array([g["lng"] for g in gi]); gmva = np.array([g["mva"] for g in gi])
d_gi, _, mva25 = nearest_and_within(hlat, hlng, glat, glng, 25.0, gmva)

# jarak ke ruas transmisi: proyeksi ekuirektangular (cos lat rata-rata Indonesia), STRtree nearest
KX = 111.32 * math.cos(math.radians(-2.5)); KY = 110.574
tlines = [LineString([(x * KX, y * KY) for x, y in c]) for c in tx]
tree = STRtree(tlines)
from shapely.geometry import Point
d_tx = np.empty(len(H))
for i in range(len(H)):
    p = Point(hlng[i] * KX, hlat[i] * KY)
    j = tree.nearest(p)
    d_tx[i] = tlines[j].distance(p)

# ============================================================================ 4) indikator turunan
ppc = np.where(c10 > 0, pop10 / np.maximum(c10, 1), np.inf)   # jiwa per charger aktif dalam ~10 km
pov = np.array([ECON[prov_names[p]][2] for p in pi]); hdi = np.array([ECON[prov_names[p]][1] for p in pi])
def z(x): return (x - x.mean()) / (x.std() + 1e-9)
burden = (z(pov) - z(hdi)) / 2  # beban sosial-ekonomi provinsi: miskin tinggi & IPM rendah -> tinggi

IND = dict(d_spklu=np.minimum(d_spklu, CAP_KM), ppc=np.where(np.isinf(ppc), 1e9, ppc), pop=pop, burden=burden,
           d_gi=np.minimum(d_gi, CAP_KM), mva25=mva25, d_tx=np.minimum(d_tx, CAP_KM), pop10=pop10, c10=c10)


def scores(mask):
    """Skor 0-100 = rata-rata tertimbang peringkat persentil indikator di dalam lingkup (mask)."""
    P = np.zeros(mask.sum()); F = np.zeros(mask.sum())
    for k, w, sgn in PRIO:
        P += w * (pct_rank(sgn * IND[k][mask]))
    for k, w, sgn in FEAS:
        F += w * (pct_rank(sgn * IND[k][mask]))
    return P, F


live = pop >= POP_MIN
P, F = scores(live)
prio = np.full(len(H), np.nan); feas = np.full(len(H), np.nan)
prio[live] = P; feas[live] = F
zone = np.full(len(H), -1)
zone[live] = np.where(P >= 50, np.where(F >= 50, 0, 1), np.where(F >= 50, 2, 3))
ZONES = ["Prioritas tinggi & layak — bangun sekarang", "Prioritas tinggi, jaringan lemah — investasi jaringan dulu",
         "Layak, prioritas rendah — biarkan pasar/komersial", "Prioritas & kelayakan rendah"]

# ============================================================================ 5) agregat kabupaten & provinsi
BANDS = [5, 10, 25, 50]


def agg(mask, name):
    p = pop[mask]
    if p.sum() == 0:
        return None
    w = p / p.sum()
    d = d_spklu[mask]
    bands = [float(p[d <= 5].sum()), float(p[(d > 5) & (d <= 10)].sum()), float(p[(d > 10) & (d <= 25)].sum()),
             float(p[(d > 25) & (d <= 50)].sum()), float(p[d > 50].sum())]
    lv = mask & live
    return dict(name=name, pop=round(float(p.sum())), hex=int(mask.sum()),
                d_mean=round(float((w * np.minimum(d, 200)).sum()), 1),
                within10=round(100 * (bands[0] + bands[1]) / p.sum(), 1),
                within10_pln=round(100 * float(p[d_pln[mask] <= 10].sum()) / p.sum(), 1),
                beyond25=round(100 * (bands[3] + bands[4]) / p.sum(), 1),
                bands=[round(b) for b in bands],
                prio=round(float(np.average(prio[lv], weights=pop[lv])), 1) if lv.any() else None,
                feas=round(float(np.average(feas[lv], weights=pop[lv])), 1) if lv.any() else None,
                z0=round(float(pop[lv][zone[lv] == 0].sum())) if lv.any() else 0,
                z1=round(float(pop[lv][zone[lv] == 1].sum())) if lv.any() else 0,
                d_gi=round(float((w * np.minimum(d_gi[mask], 200)).sum()), 1))


kab_stats = []
for i, k in enumerate(kabs):
    a = agg(kab == i, k["name"])
    if a is None:
        continue
    ss = [s for s in spk if s["kab"] == i]
    sa = [s for s in ss if s["active"]]
    a.update(idx=i, prov=k["pi"], sites=len(ss), active=len(sa), chargers=sum(s["ch"] for s in sa),
             chargers_pln=sum(s["ch"] for s in sa if s["pln"]),
             dc=sum(1 for s in sa if s["kw"] >= DC_KW), kw=round(sum(s["kw"] * s["ch"] for s in sa)))
    a["per100k"] = round(1e5 * a["chargers"] / a["pop"], 2) if a["pop"] else None
    kab_stats.append(a)
# gardu induk per kabupaten (heksagon terdekat -> kabupaten)
for g in gi:
    d = hav(g["lat"], g["lng"], hlat, hlng); j = int(d.argmin())
    g["kab"] = int(kab[j])
gcount = {}
for g in gi:
    gcount[g["kab"]] = gcount.get(g["kab"], 0) + 1
for a in kab_stats:
    a["gi"] = gcount.get(a["idx"], 0)

prov_stats = []
for p, name in enumerate(prov_names):
    a = agg(pi == p, name)
    ss = [s for s in spk if kabs[s["kab"]]["pi"] == p]
    sa = [s for s in ss if s["active"]]
    a.update(idx=p, sites=len(ss), active=len(sa), chargers=sum(s["ch"] for s in sa),
             chargers_pln=sum(s["ch"] for s in sa if s["pln"]),
             dc=sum(1 for s in sa if s["kw"] >= DC_KW), pop_bps=POP[name], hdi=ECON[name][1],
             poverty=ECON[name][2], grdp=ECON[name][0], gi=sum(1 for g in gi if kabs[g["kab"]]["pi"] == p))
    a["per100k"] = round(1e5 * a["chargers"] / a["pop"], 2) if a["pop"] else None
    prov_stats.append(a)

nat = agg(np.ones(len(H), bool), "Indonesia")
nat.update(sites=len(spk), active=len(S_ACT), active_pln=len(S_PLN), chargers=int(ach.sum()), dc=int(adc.sum()),
           chargers_pln=int(sum(s["ch"] for s in S_PLN)),
           gi=len(gi), mva=round(float(gmva.sum())))
gk, lk = gini_lorenz([a["pop"] for a in kab_stats], [a["chargers"] for a in kab_stats])
gp, lp = gini_lorenz([a["pop"] for a in prov_stats], [a["chargers"] for a in prov_stats])
nat.update(gini_kab=gk, lorenz_kab=lk, gini_prov=gp, lorenz_prov=lp,
           zone_pop=[round(float(pop[live][zone[live] == zz].sum())) for zz in range(4)],
           zone_hex=[int((zone[live] == zz).sum()) for zz in range(4)],
           pop_live=round(float(pop[live].sum())), hex_live=int(live.sum()))

COLS6 = ["h3", "pop", "kab", "d_spklu", "d_any", "n10", "c10", "dc10", "pop10", "d_gi", "mva25", "d_tx",
         "d_pln", "n10p", "c10p", "dc10p"]
# ============================================================================ 7) payload
r6rows = []
for i in np.where(live)[0]:
    r6rows.append([H[i], round(float(pop[i])), int(kab[i]), round(float(d_spklu[i]), 1), round(float(d_any[i]), 1),
                   int(n10[i]), int(c10[i]), int(dc10[i]), round(float(pop10[i])), round(float(d_gi[i]), 1),
                   round(float(mva25[i])), round(float(d_tx[i]), 1),
                   round(float(d_pln[i]), 1), int(n10p[i]), int(c10p[i]), int(dc10p[i])])

payload = dict(
    meta=dict(res=6, pop_min=POP_MIN, ring=RING_10KM, cap_km=CAP_KM, dc_kw=DC_KW,
              prio=[[k, w, s] for k, w, s in PRIO], feas=[[k, w, s] for k, w, s in FEAS], zones=ZONES,
              sources=["Kontur Population ID 2023-11-01 (H3 res 8 → res 6)", "geoBoundaries gbOpen IDN ADM1/ADM2",
                       "Master SPKLU Indonesia 8 Jun 2026 (PLN)", "data/grid-id (RUPTL 2025–2034 + OSM)",
                       "BPS ~2023 provinsi (indikatif)"]),
    provs=[dict(name=p["name"], hdi=p["hdi"], poverty=p["poverty"], grdp=p["grdp"], pop_bps=p["pop_bps"],
                burden=round(float(burden[pi == p["idx"]][0]), 4) if (pi == p["idx"]).any() else 0.0) for p in prov_stats],
    kabs=[dict(name=k["name"], prov=k["pi"]) for k in kabs],
    cols=COLS6, r6=r6rows,
    spklu=[[round(s["lat"], 4), round(s["lng"], 4), s["kw"], s["ch"], 1 if s["active"] else 0,
            1 if s["pln"] else 0, s["name"][:60], s["kab"]] for s in spk],
    gi=[[round(g["lat"], 4), round(g["lng"], 4), round(g["mva"]), g["name"][:40], g["kv"]] for g in gi],
    kab_stats=kab_stats, prov_stats=prov_stats, nat=nat, bands=BANDS,
)
js = "window.EQUITY=" + json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + ";\n"
open(os.path.join(HERE, "equity.js"), "w", encoding="utf-8").write(js)

summary = dict(nat=nat, prov=prov_stats,
               kab_top_prio=sorted([a for a in kab_stats if a["prio"] is not None], key=lambda a: -a["prio"])[:25],
               kab_top_desert=sorted(kab_stats, key=lambda a: -a["beyond25"] * a["pop"])[:25],
               spklu=dict(sites=len(spk), active=len(S_ACT)), hex=dict(all=len(H), live=int(live.sum())))
json.dump(summary, open(os.path.join(HERE, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"equity.js: {len(js)/1024/1024:.2f} MB · r6 {len(r6rows):,}")
print(f"nasional: {nat['within10']} % penduduk ≤10 km dari SPKLU operasional (PLN saja {nat['within10_pln']} %) · {nat['beyond25']} % >25 km · "
      f"Gini charger/kapita antar-kabupaten {gk} · zona (jiwa) {nat['zone_pop']}")
