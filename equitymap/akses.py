#!/usr/bin/env python3
"""Aksesibilitas SPKLU — enam ukuran, dihitung dari equity.js.

Ukuran 1-4 (container, proximity, cumulative biner, cumulative hitungan) sudah
dipakai tab lain; skrip ini menambah ukuran 5-6 yang belum ada:

  5. Gravity / potential      A_i = sum_j S_j * exp(-beta * d_ij)
  6. E2SFCA berbobot kapasitas
       langkah 1  R_j = S_j / sum_k ( P_k * W(d_kj) )
       langkah 2  A_i = sum_j ( R_j * W(d_ij) )

W memakai pita jarak yang sudah dipakai dashboard (5 / 10 / 25 km):
  <=5 km -> 1,00 · 5-10 km -> 0,60 · 10-25 km -> 0,25 · >25 km -> 0

S_j diisi dua kali: cacah charger (pembanding) dan kW terpasang (versi kapasitas).
Keluaran: akses.json — statistik nasional, tabel kabupaten/kota, dan pergeseran
peringkat terhadap ukuran per-100rb yang dipakai sekarang.

    python3 equitymap/akses.py
"""
import json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS = [(5.0, 1.00), (10.0, 0.60), (25.0, 0.25)]      # (batas km, bobot)
BETA = 0.15                                            # gravity: exp(-0.15 d), separuh di ~4,6 km
CHUNK = 1500

js = open(os.path.join(HERE, "equity.js"), encoding="utf-8").read()
E = json.loads(js[len("window.EQUITY="):].rstrip(";\n"))
ci = {c: i for i, c in enumerate(E["cols"])}
R6, KABS, KS, PROVS = E["r6"], E["kabs"], E["kab_stats"], E["provs"]

try:
    import h3
except ImportError:
    raise SystemExit("butuh h3: pip install h3")

pop = np.array([r[ci["pop"]] for r in R6], float)
kab = np.array([r[ci["kab"]] for r in R6], int)
d10 = np.array([r[ci["d_spklu"]] for r in R6], float)
c10 = np.array([r[ci["c10"]] for r in R6], float)
p10 = np.array([r[ci["pop10"]] for r in R6], float)
ll = np.array([h3.cell_to_latlng(r[ci["h3"]]) for r in R6], float)
hlat, hlng = np.radians(ll[:, 0]), np.radians(ll[:, 1])

S = [s for s in E["spklu"] if s[4] == 1]               # situs operasional (3.072)
slat = np.radians(np.array([s[0] for s in S], float))
slng = np.radians(np.array([s[1] for s in S], float))
s_kw = np.array([s[2] for s in S], float)
s_n = np.array([s[3] for s in S], float)


def _trapz(y, x):
    y, x = np.asarray(y, float), np.asarray(x, float)
    return float(np.sum(np.diff(x) * (y[1:] + y[:-1]) / 2))


def weight(d):
    w = np.zeros_like(d)
    prev = 0.0
    for lim, wt in BANDS:
        w[(d > prev) & (d <= lim)] = wt
        prev = lim
    w[d <= 0] = BANDS[0][1]
    return w


def haversine_chunk(i0, i1):
    dlat = slat[None, :] - hlat[i0:i1, None]
    dlng = slng[None, :] - hlng[i0:i1, None]
    a = np.sin(dlat / 2) ** 2 + np.cos(hlat[i0:i1, None]) * np.cos(slat[None, :]) * np.sin(dlng / 2) ** 2
    return 6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


n_h, n_s = len(pop), len(S)
demand_kw = np.zeros(n_s)          # sum_k P_k * W  (penyebut langkah 1)
acc_grav = np.zeros(n_h)
print(f"{n_h} heksagon x {n_s} situs operasional")

# --- langkah 1: kompetisi di tiap situs, sekaligus gravity
for i0 in range(0, n_h, CHUNK):
    i1 = min(i0 + CHUNK, n_h)
    d = haversine_chunk(i0, i1)
    w = weight(d)
    demand_kw += (pop[i0:i1, None] * w).sum(axis=0)
    acc_grav[i0:i1] = (s_kw[None, :] * np.exp(-BETA * d)).sum(axis=1)

R_kw = s_kw / np.maximum(demand_kw, 1e-9)
R_unit = s_n / np.maximum(demand_kw, 1e-9)

# --- langkah 2: jumlahkan rasio yang bisa dijangkau tiap heksagon
acc_kw = np.zeros(n_h)
acc_unit = np.zeros(n_h)
for i0 in range(0, n_h, CHUNK):
    i1 = min(i0 + CHUNK, n_h)
    w = weight(haversine_chunk(i0, i1))
    acc_kw[i0:i1] = (w * R_kw[None, :]).sum(axis=1)
    acc_unit[i0:i1] = (w * R_unit[None, :]).sum(axis=1)

acc_kw_k = acc_kw * 1000.0          # kW per 1.000 jiwa
acc_unit_k = acc_unit * 1e5         # charger per 100.000 jiwa
fca1 = c10 / np.maximum(p10, 1) * 1e5   # FCA satu langkah (pembanding sederhana)


def wavg(x, m):
    return float(np.average(x[m], weights=pop[m])) if pop[m].sum() > 0 else 0.0


def lorenz_gini(p, v):
    p, v = np.asarray(p, float), np.asarray(v, float)
    o = np.argsort(np.divide(v, np.maximum(p, 1e-9)))
    cp = np.concatenate([[0], np.cumsum(p[o]) / p.sum()])
    cv = np.concatenate([[0], np.cumsum(v[o]) / max(v.sum(), 1e-9)])
    g = 1 - 2 * _trapz(cv, cp)
    step = max(1, len(cp) // 40)
    pts = [[round(float(a), 4), round(float(b), 4)] for a, b in zip(cp[::step], cv[::step])] + [[1.0, 1.0]]
    return round(float(g), 3), pts


def conc_index(p, v, rank):
    o = np.argsort(rank)
    p, v = np.asarray(p, float)[o], np.asarray(v, float)[o]
    cp = np.concatenate([[0], np.cumsum(p) / p.sum()])
    cv = np.concatenate([[0], np.cumsum(v) / max(v.sum(), 1e-9)])
    return round(float(1 - 2 * _trapz(cv, cp)), 3)


rows = []
for k in sorted(set(kab.tolist())):
    m = kab == k
    P = float(pop[m].sum())
    if P <= 0:
        continue
    st = next((x for x in KS if x["idx"] == k), None)
    rows.append(dict(
        idx=int(k), kab=KABS[k]["name"], prov=PROVS[KABS[k]["prov"]]["name"], prov_i=int(KABS[k]["prov"]),
        pop=round(P), per100k=float(st["per100k"]) if st else 0.0,
        within10=round(100 * wavg((d10 <= 10).astype(float), m), 1),
        d_mean=round(wavg(d10, m), 1), reach=round(wavg(c10, m), 1),
        fca1=round(wavg(fca1, m), 2),
        e2_unit=round(wavg(acc_unit_k, m), 2), e2_kw=round(wavg(acc_kw_k, m), 2),
        grav=round(wavg(acc_grav, m), 1)))

pop_k = np.array([r["pop"] for r in rows], float)
acc_tot_kw = np.array([r["e2_kw"] for r in rows]) * pop_k / 1000.0
acc_tot_un = np.array([r["e2_unit"] for r in rows]) * pop_k / 1e5
ch_k = np.array([r["per100k"] for r in rows]) * pop_k / 1e5
g_ch, lor_ch = lorenz_gini(pop_k, ch_k)
g_e2u, lor_e2u = lorenz_gini(pop_k, acc_tot_un)
g_e2k, lor_e2k = lorenz_gini(pop_k, acc_tot_kw)

# CI terhadap peringkat kemakmuran provinsi (sama seperti keadilan.py)
grdp = np.array([PROVS[r["prov_i"]]["grdp"] for r in rows], float)
hdi = np.array([PROVS[r["prov_i"]]["hdi"] for r in rows], float)
ci_ch_g, ci_e2_g = conc_index(pop_k, ch_k, grdp), conc_index(pop_k, acc_tot_kw, grdp)
ci_ch_h, ci_e2_h = conc_index(pop_k, ch_k, hdi), conc_index(pop_k, acc_tot_kw, hdi)


def spearman(a, b):
    ra = np.argsort(np.argsort(-np.asarray(a, float)))
    rb = np.argsort(np.argsort(-np.asarray(b, float)))
    return round(float(np.corrcoef(ra, rb)[0, 1]), 3)


big = [r for r in rows if r["pop"] > 300000]
bp = np.array([r["per100k"] for r in big]); bc = np.array([r["within10"] for r in big])
be = np.array([r["e2_kw"] for r in big]); bu = np.array([r["e2_unit"] for r in big])
rk = lambda v: {big[i]["kab"]: int(np.argsort(np.argsort(-v))[i]) + 1 for i in range(len(big))}
Rp, Rc, Re = rk(bp), rk(bc), rk(be)
for r in big:
    r["r_per100k"], r["r_within10"], r["r_e2"] = Rp[r["kab"]], Rc[r["kab"]], Re[r["kab"]]
    r["shift"] = r["r_per100k"] - r["r_e2"]
movers_up = sorted(big, key=lambda r: -r["shift"])[:8]
movers_dn = sorted(big, key=lambda r: r["shift"])[:8]
big_sorted = sorted(big, key=lambda r: -r["e2_kw"])

out = dict(
    meta=dict(hex=n_h, sites=n_s, chargers=int(s_n.sum()), kw=round(float(s_kw.sum())),
              bands=[[b, w] for b, w in BANDS], beta=BETA,
              note="E2SFCA berbobot kapasitas; jarak garis lurus (haversine) dari centroid heksagon res 6"),
    nasional=dict(
        e2_kw=round(float(np.average([r["e2_kw"] for r in rows], weights=pop_k)), 2),
        e2_unit=round(float(np.average([r["e2_unit"] for r in rows], weights=pop_k)), 2),
        gini_charger=g_ch, gini_e2_unit=g_e2u, gini_e2_kw=g_e2k,
        ci_charger_grdp=ci_ch_g, ci_e2_grdp=ci_e2_g,
        ci_charger_hdi=ci_ch_h, ci_e2_hdi=ci_e2_h,
        rho_per100k_e2=spearman(bp, be), rho_within10_e2=spearman(bc, be),
        rho_per100k_within10=spearman(bp, bc), rho_e2unit_e2kw=spearman(bu, be),
        n_big=len(big),
        shift_gt25=int(sum(1 for r in big if abs(r["shift"]) > 25)),
        shift_gt50=int(sum(1 for r in big if abs(r["shift"]) > 50))),
    lorenz=dict(charger=lor_ch, e2_unit=lor_e2u, e2_kw=lor_e2k),
    movers_up=movers_up, movers_dn=movers_dn,
    top=big_sorted[:15], bottom=big_sorted[-15:],
    kabs=rows)
json.dump(out, open(os.path.join(HERE, "akses.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(json.dumps(out["nasional"], indent=1, ensure_ascii=False))
print("\nnaik terbanyak:", [(r["kab"], r["shift"]) for r in movers_up[:5]])
print("turun terbanyak:", [(r["kab"], r["shift"]) for r in movers_dn[:5]])
