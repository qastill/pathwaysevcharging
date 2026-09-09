"""Akses 10 menit ke SPKLU — transfer metode ParkServe (Trust for Public Land) ke charger.

ParkServe menghitung persentase penduduk yang tinggal dalam 10 menit berjalan kaki (≈0,5 mil = 0,8 km)
dari taman, memakai jaringan jalan, dan menandai "park priority areas" = blok sensus di luar jangkauan
itu. Skrip ini menghitung padanannya untuk SPKLU pada heksagon Kontur H3 resolusi 8 (≈0,74 km²,
874.919 heksagon berpenduduk): jarak garis lurus ke situs operasional terdekat, lalu dua ambang —
**10 menit jalan kaki = 0,8 km** dan **10 menit berkendara = 5 km** (≈30 km/jam dalam kota).

Butuh berkas mentah Kontur di equitymap/cache/ (diunduh sekali oleh equitymap/fetch.py); hasilnya
dipadatkan ke parkir/input/access.json (di-commit) supaya parkir/prepare.py berjalan tanpa jaringan.

    python3 parkir/access.py
"""
import csv, json, math, os, sqlite3, sys

import h3
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
from venue import load_sites, PARKING_CATS  # noqa: E402

GPKG = "equitymap/cache/kontur_id.gpkg"
WALK_KM, DRIVE_KM = 0.8, 5.0
BANDS = [0.4, 0.8, 2.0, 5.0, 10.0]
TOP_PRIO = 25          # heksagon prioritas per kabupaten yang dikirim ke peta
PRIO_MIN_POP = 150     # heksagon res 8 dengan penduduk < ini tidak dijadikan prioritas

if not os.path.exists(GPKG):
    sys.exit("Kontur belum ada: jalankan `python3 equitymap/fetch.py` dulu (unduh sekali).")


def proj(lat, lng):
    lat, lng = np.asarray(lat, float), np.asarray(lng, float)
    return np.c_[lng * 111.32 * np.cos(np.radians(lat)), lat * 110.574]


# ---- kabupaten per heksagon res 6 (dari equitymap/input, sudah di-commit)
kab6 = {r["h3"]: int(r["kab"]) for r in csv.DictReader(open("equitymap/input/hex_r6.csv"))}
kabs = list(csv.DictReader(open("equitymap/input/kabupaten.csv", encoding="utf-8")))

# ---- situs operasional
sites = [s for s in load_sites() if s["active"]]
S = proj([s["lat"] for s in sites], [s["lng"] for s in sites])
tree_all = cKDTree(S)
park = [i for i, s in enumerate(sites) if s["cat"] in PARKING_CATS]
tree_park = cKDTree(S[park])
dc = [i for i, s in enumerate(sites) if s["kw"] >= 50]
tree_dc = cKDTree(S[dc])
print(f"situs operasional {len(sites):,} · di lahan parkir {len(park):,} · DC≥50 kW {len(dc):,}")

# ---- heksagon res 8
con = sqlite3.connect(GPKG)
rows = con.execute("select h3, population from population").fetchall()
H = [r[0] for r in rows]
pop = np.array([r[1] for r in rows], float)
ll = np.array([h3.cell_to_latlng(h) for h in H])
P = proj(ll[:, 0], ll[:, 1])
d_all, _ = tree_all.query(P)
d_park, _ = tree_park.query(P)
d_dc, _ = tree_dc.query(P)
kab = np.array([kab6.get(h3.cell_to_parent(h, 6), -1) for h in H])
print(f"heksagon res 8: {len(H):,} · populasi {pop.sum():,.0f} · tanpa kabupaten {(kab < 0).sum():,}")


def share(mask_pop, d, km):
    return float(pop[mask_pop][d[mask_pop] <= km].sum())


out_kab = []
prio = {}
for i, k in enumerate(kabs):
    m = kab == i
    p = pop[m]
    if p.sum() <= 0:
        continue
    tot = float(p.sum())
    rec = dict(idx=i, pop=round(tot),
               walk=round(100 * share(m, d_all, WALK_KM) / tot, 1),
               drive=round(100 * share(m, d_all, DRIVE_KM) / tot, 1),
               walk_park=round(100 * share(m, d_park, WALK_KM) / tot, 1),
               drive_park=round(100 * share(m, d_park, DRIVE_KM) / tot, 1),
               drive_dc=round(100 * share(m, d_dc, DRIVE_KM) / tot, 1),
               d_med=round(float(np.median(d_all[m])), 2))
    # heksagon prioritas: di luar 10 menit jalan kaki, penduduk terbanyak (padanan park priority areas)
    idx = np.where(m & (d_all > WALK_KM) & (pop >= PRIO_MIN_POP))[0]
    idx = idx[np.argsort(-pop[idx])][:TOP_PRIO]
    prio[i] = [[H[j], round(float(pop[j])), round(float(d_all[j]), 2), round(float(d_park[j]), 2)] for j in idx]
    rec["prio_pop"] = round(float(pop[m][d_all[m] > WALK_KM].sum()))   # seluruh penduduk di luar jangkauan jalan kaki
    out_kab.append(rec)

bands = []
edges = [0] + BANDS + [1e9]
for a, b in zip(edges[:-1], edges[1:]):
    bands.append(round(float(pop[(d_all > a) & (d_all <= b)].sum())))
nat = dict(pop=round(float(pop.sum())), hex=len(H),
           walk=round(100 * float(pop[d_all <= WALK_KM].sum()) / pop.sum(), 1),
           drive=round(100 * float(pop[d_all <= DRIVE_KM].sum()) / pop.sum(), 1),
           walk_park=round(100 * float(pop[d_park <= WALK_KM].sum()) / pop.sum(), 1),
           drive_park=round(100 * float(pop[d_park <= DRIVE_KM].sum()) / pop.sum(), 1),
           drive_dc=round(100 * float(pop[d_dc <= DRIVE_KM].sum()) / pop.sum(), 1),
           d_med=round(float(np.median(d_all)), 2),
           d_med_w=round(float(np.average(np.minimum(d_all, 100), weights=pop)), 2),
           bands=bands, band_edges=BANDS)
json.dump(dict(meta=dict(walk_km=WALK_KM, drive_km=DRIVE_KM, res=8, top_prio=TOP_PRIO, prio_min_pop=PRIO_MIN_POP,
                         sites=len(sites), sites_park=len(park), sites_dc=len(dc),
                         source="Kontur Population ID 2023-11-01 (H3 res 8) · master SPKLU 8 Jun 2026"),
               nat=nat, kab=out_kab, prio=prio),
          open(os.path.join(HERE, "input", "access.json"), "w", encoding="utf-8"), separators=(",", ":"))
print(f"nasional: {nat['walk']} % penduduk ≤0,8 km (10 menit jalan kaki) · {nat['drive']} % ≤5 km (10 menit berkendara) "
      f"· parkir-venue {nat['walk_park']} % / {nat['drive_park']} % · median jarak {nat['d_med']} km")
print("ditulis parkir/input/access.json")
