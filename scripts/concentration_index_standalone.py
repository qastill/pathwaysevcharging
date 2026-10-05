#!/usr/bin/env python3
"""Concentration Index SPKLU — skrip mandiri, siap unduh dan siap jalan.

Hanya butuh numpy. Masukan: satu CSV dengan satu baris per wilayah (kecamatan / kab/kota / grid) dan minimal
tiga kolom: penduduk (bobot), pasokan (charger, kW, kWh, dst.), dan variabel peringkat (IPM, pengeluaran, dst.).

    pip install numpy
    python3 concentration_index_standalone.py data.csv --pop pop --supply chargers --rank ipm
    python3 concentration_index_standalone.py jabar_kecamatan.csv --pop pop --supply kwh --rank expend --group kab
    python3 concentration_index_standalone.py --demo            # contoh sintetis 20 wilayah, untuk melihat keluaran

Keluaran (stdout + --out hasil.json):
  1. Indeks konsentrasi (Wagstaff/Kakwani) tertimbang penduduk, C ∈ [−1, 1]
       C = 2·cov_w(y_i, R_i) / μ ;  y_i = pasokan per kapita wilayah i, R_i = peringkat fraksional tertimbang
       (0 = termiskin … 1 = terkaya), μ = rata-rata tertimbang y.  C > 0 pro-kaya, C < 0 pro-miskin.
       Identik dengan C = 1 − 2·∫L(p)dp di bawah kurva konsentrasi.
  2. Erreygers CI untuk variabel terbatas 0/1 (mis. "wilayah punya charger"): E = 8·cov_w(ind, R).
       Mengikuti Erreygers (2009) seperti dipakai proposal "Who Is Really Served" §5.7 (RQ4).
  3. Selang kepercayaan 95 % bootstrap (resampling wilayah, 2.000 ulangan).
  4. Kurva konsentrasi (titik), kuintil penduduk, Gini pasokan/kapita, HHI porsi pasokan, CR4/CR10.
  5. Dekomposisi antar/dalam kelompok bila --group diberikan (CI dalam tiap kelompok ≥ 6 wilayah).

Rujukan: Wagstaff, Paci & van Doorslaer (1991); Kakwani, Wagstaff & van Doorslaer (1997); Erreygers (2009);
O'Donnell et al. (2008) "Analyzing Health Equity Using Household Survey Data", bab 8.
"""
import argparse, csv, json, sys
import numpy as np


# ----------------------------------------------------------------------------- alat ukur
def weighted_ranks(r, w):
    """Peringkat fraksional tertimbang pada [0, 1]; wilayah dengan r sama berbagi rata-rata peringkatnya."""
    r, w = np.asarray(r, float), np.asarray(w, float)
    o = np.argsort(r, kind="stable"); rs, ws = r[o], w[o]
    cum = np.cumsum(ws) / ws.sum(); mid = cum - ws / ws.sum() / 2
    out = np.empty_like(mid); i = 0
    while i < len(rs):
        j = i
        while j + 1 < len(rs) and rs[j + 1] == rs[i]:
            j += 1
        out[i:j + 1] = np.average(mid[i:j + 1], weights=ws[i:j + 1]); i = j + 1
    res = np.empty_like(out); res[o] = out
    return res


def concentration_index(supply, rank, pop):
    """C = 2·cov_w(y, R)/μ dengan y = supply/pop. NaN bila total pasokan nol."""
    supply, rank, pop = (np.asarray(x, float) for x in (supply, rank, pop))
    if supply.sum() <= 0:
        return float("nan")
    R = weighted_ranks(rank, pop); y = supply / pop
    W = pop.sum(); mu = np.sum(pop * y) / W; mR = np.sum(pop * R) / W
    return float(2 * (np.sum(pop * (y - mu) * (R - mR)) / W) / mu)


def erreygers_index(indicator, rank, pop, lo=0.0, hi=1.0):
    """E = 8·cov_w(ind, R)/(hi − lo) untuk variabel terbatas (Erreygers 2009)."""
    ind, rank, pop = (np.asarray(x, float) for x in (indicator, rank, pop))
    R = weighted_ranks(rank, pop); W = pop.sum()
    mu = np.sum(pop * ind) / W; mR = np.sum(pop * R) / W
    return float(8 * (np.sum(pop * (ind - mu) * (R - mR)) / W) / (hi - lo))


def bootstrap(fn, arrays, n_boot=2000, seed=2026):
    rng = np.random.default_rng(seed); n = len(arrays[0]); vals = []
    for _ in range(n_boot):
        ix = rng.integers(0, n, n)
        v = fn(*[a[ix] for a in arrays])
        if not np.isnan(v):
            vals.append(v)
    lo, hi = np.percentile(vals, [2.5, 97.5]) if vals else (np.nan, np.nan)
    return float(lo), float(hi)


def concentration_curve(supply, rank, pop, npts=40):
    o = np.argsort(np.asarray(rank, float), kind="stable")
    pop, supply = np.asarray(pop, float)[o], np.asarray(supply, float)[o]
    cp = np.r_[0, np.cumsum(pop) / pop.sum()]; cs = np.r_[0, np.cumsum(supply) / max(supply.sum(), 1e-9)]
    step = max(1, len(cp) // npts)
    pts = [[round(float(a), 4), round(float(b), 4)] for a, b in zip(cp[::step], cs[::step])]
    return pts if pts[-1] == [1.0, 1.0] else pts + [[1.0, 1.0]]


def gini(values):
    v = np.sort(np.asarray(values, float)); n = len(v)
    return float("nan") if n == 0 or v.sum() == 0 else float(2 * np.sum(np.arange(1, n + 1) * v) / (n * v.sum()) - (n + 1) / n)


def market_stats(values):
    v = np.asarray(values, float); v = v[v > 0]; s = np.sort(v)[::-1] / v.sum(); h = float(np.sum(s ** 2) * 10000)
    return dict(n_positive=int(len(v)), hhi=round(h, 1), n_effective=round(10000 / h, 2), cr4=round(float(s[:4].sum()), 4), cr10=round(float(s[:10].sum()), 4))


def quintiles(supply, rank, pop):
    o = np.argsort(np.asarray(rank, float), kind="stable"); cum = np.cumsum(pop[o]) / pop.sum(); out = []
    for q in range(5):
        sel = o[(cum > q / 5) & (cum <= (q + 1) / 5)] if q else o[cum <= .2]
        if not len(sel):
            continue
        P = pop[sel].sum()
        out.append(dict(q=q + 1, n=int(len(sel)), pop=round(float(P)), supply=round(float(supply[sel].sum()), 2),
                        per100k=round(1e5 * supply[sel].sum() / P, 3), pop_without_supply_pct=round(100 * float(pop[sel][supply[sel] == 0].sum() / P), 1)))
    return out


# ----------------------------------------------------------------------------- jalankan
def analyse(rows, pop_col, supply_col, rank_col, group_col=None, n_boot=2000, min_pop=0.0):
    rows = [r for r in rows if float(r[pop_col] or 0) >= max(min_pop, 1e-9) and r[rank_col] not in ("", None)]
    pop = np.array([float(r[pop_col]) for r in rows]); sup = np.array([float(r[supply_col] or 0) for r in rows]); rk = np.array([float(r[rank_col]) for r in rows])
    has = (sup > 0).astype(float)
    C = concentration_index(sup, rk, pop); lo, hi = bootstrap(concentration_index, (sup, rk, pop), n_boot)
    E_has = erreygers_index(has, rk, pop); elo, ehi = bootstrap(erreygers_index, (has, rk, pop), n_boot)
    res = dict(n_units=len(rows), population=round(float(pop.sum())), supply_total=round(float(sup.sum()), 2),
               supply_per100k=round(1e5 * sup.sum() / pop.sum(), 3), units_with_supply=int(has.sum()),
               pop_in_units_with_supply_pct=round(100 * float(pop[has > 0].sum() / pop.sum()), 1),
               concentration_index=dict(C=round(C, 4), ci95=[round(lo, 4), round(hi, 4)], significant=bool(lo > 0 or hi < 0),
                                        reading="pro-kaya (menumpuk di peringkat tinggi)" if C > 0 else "pro-miskin (menumpuk di peringkat rendah)"),
               erreygers_has_supply=dict(E=round(E_has, 4), ci95=[round(elo, 4), round(ehi, 4)], significant=bool(elo > 0 or ehi < 0),
                                         erreygers_deprivation=round(-E_has, 4),
                                         vertical_equity_pass_rule="LULUS (E akses ≤ 0 atau selang melewati 0)" if not (elo > 0) else "GAGAL (akses menumpuk di wilayah peringkat tinggi)"),
               gini_supply_per_capita=round(gini(sup / pop), 4), market=market_stats(sup),
               quintiles=quintiles(sup, rk, pop), curve=concentration_curve(sup, rk, pop))
    if group_col:
        groups = {}
        for r, p, s, k in zip(rows, pop, sup, rk):
            groups.setdefault(r[group_col], []).append((p, s, k))
        res["within_groups"] = sorted([dict(group=g, n=len(v), supply=round(sum(x[1] for x in v), 2),
                                            C=round(concentration_index([x[1] for x in v], [x[2] for x in v], [x[0] for x in v]), 4))
                                       for g, v in groups.items() if len(v) >= 6 and len({x[2] for x in v}) >= 2 and sum(x[1] for x in v) > 0],
                                      key=lambda d: -d["C"])
        # antar kelompok: tiap kelompok diringkas menjadi satu unit (penduduk dan pasokan dijumlah, peringkat = rata-rata tertimbang)
        gp = np.array([sum(x[0] for x in v) for v in groups.values()]); gs = np.array([sum(x[1] for x in v) for v in groups.values()])
        gr = np.array([np.average([x[2] for x in v], weights=[x[0] for x in v]) for v in groups.values()])
        res["between_groups_C"] = round(concentration_index(gs, gr, gp), 4)
    return res


def demo_rows():
    rng = np.random.default_rng(1); rows = []
    for i in range(20):
        ipm = 65 + i * 1.0 + rng.normal(0, .8); pop = int(rng.integers(50_000, 600_000))
        chargers = int(max(0, rng.poisson(pop / 1e5 * (0.3 + 0.08 * i))))     # sengaja dibuat pro-kaya
        rows.append(dict(unit=f"W{i+1:02d}", pop=pop, chargers=chargers, ipm=round(ipm, 2), group="A" if i % 2 else "B"))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?", help="berkas CSV, satu baris per wilayah")
    ap.add_argument("--pop", default="pop", help="kolom penduduk/bobot (default: pop)")
    ap.add_argument("--supply", default="chargers", help="kolom pasokan (default: chargers)")
    ap.add_argument("--rank", default="ipm", help="kolom variabel peringkat, rendah → tinggi (default: ipm)")
    ap.add_argument("--group", help="kolom kelompok untuk dekomposisi (opsional, mis. kab)")
    ap.add_argument("--invert-rank", action="store_true", help="balik arah peringkat (mis. kemiskinan: tinggi = miskin)")
    ap.add_argument("--min-pop", type=float, default=0.0, help="buang wilayah berpenduduk di bawah ambang ini")
    ap.add_argument("--boot", type=int, default=2000, help="ulangan bootstrap (default 2000)")
    ap.add_argument("--out", help="simpan hasil JSON ke berkas ini")
    ap.add_argument("--demo", action="store_true", help="jalankan pada data sintetis 20 wilayah")
    a = ap.parse_args()
    if a.demo:
        rows, a.pop, a.supply, a.rank, a.group = demo_rows(), "pop", "chargers", "ipm", a.group or "group"
    elif a.csv:
        rows = list(csv.DictReader(open(a.csv, encoding="utf-8-sig")))
    else:
        ap.error("berikan berkas CSV atau --demo")
    if a.invert_rank:
        for r in rows:
            r[a.rank] = -float(r[a.rank]) if r[a.rank] not in ("", None) else r[a.rank]
    res = analyse(rows, a.pop, a.supply, a.rank, a.group, a.boot, a.min_pop)
    ci_ = res["concentration_index"]; er = res["erreygers_has_supply"]
    print(f"Wilayah: {res['n_units']}  penduduk: {res['population']:,}  pasokan: {res['supply_total']:,} ({res['supply_per100k']} per 100 rb)")
    print(f"Wilayah berisi pasokan: {res['units_with_supply']} ({res['pop_in_units_with_supply_pct']} % penduduk)")
    print(f"Concentration index C = {ci_['C']:+.3f}  95 % [{ci_['ci95'][0]:+.3f}, {ci_['ci95'][1]:+.3f}]  {'signifikan' if ci_['significant'] else 'tidak signifikan'}  → {ci_['reading']}")
    print(f"Erreygers E (punya pasokan) = {er['E']:+.3f}  95 % [{er['ci95'][0]:+.3f}, {er['ci95'][1]:+.3f}]  → ekuitas vertikal: {er['vertical_equity_pass_rule']}")
    print(f"Gini pasokan/kapita = {res['gini_supply_per_capita']:.3f}   HHI porsi pasokan = {res['market']['hhi']}  CR10 = {res['market']['cr10']:.1%}")
    print("Kuintil (Q1 = peringkat terendah):")
    for q in res["quintiles"]:
        print(f"  Q{q['q']}: {q['n']:>4} wilayah  {q['pop']:>12,} jiwa  {q['per100k']:>8} per 100 rb  {q['pop_without_supply_pct']:>5} % penduduk tanpa pasokan")
    if "within_groups" in res:
        print(f"CI antar kelompok = {res['between_groups_C']:+.3f}; CI dalam kelompok (≥6 wilayah):")
        for g in res["within_groups"]:
            print(f"  {g['group']:<24} n={g['n']:<3} pasokan={g['supply']:<8} C={g['C']:+.3f}")
    if a.out:
        json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("tersimpan:", a.out)


if __name__ == "__main__":
    main()
