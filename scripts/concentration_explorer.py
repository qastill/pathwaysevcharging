"""Concentration & equity evidence for public EV charging — one estimator set, two scopes.

    python3 scripts/concentration_explorer.py jabar      -> analysis/concentration_explorer_jabar.json
    python3 scripts/concentration_explorer.py national   -> analysis/concentration_explorer_national.json

jabar     unit = kecamatan (629), parent = kabupaten/kota (27). Input data/jabar_kecamatan_spklu.geojson
          (chargers, kW, kWh and sessions Mar-2026, EV owners, Kontur population, BPS 2024 district SES).
national  unit = kabupaten/kota (508), parent = province (34). Inputs equitymap/equity.js (kab_stats: Kontur
          population, chargers/kW/sites/DC from the June 2026 master, share of residents within 10 km / beyond
          25 km of a charger), BPS 2024 district profile (--bps CSV: HDI, adjusted spending per person, poverty
          P0, island) and the district GeoJSON that ships with it (--geo). Four renamed districts are aliased.

Every measure is population-weighted. CI = 2·cov_w(supply per resident, weighted fractional rank)/mean
(Wagstaff); Erreygers correction for bounded shares; 95 % bands from a vectorised bootstrap over units.
"""
import argparse, csv, json, math, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "equitymap"))
from sosek import key, match  # noqa: E402  (BPS <-> geoBoundaries name matching)

SCRATCH_BPS = os.path.join(ROOT, "data")
ap = argparse.ArgumentParser()
ap.add_argument("scope", choices=["jabar", "national"])
ap.add_argument("--bps", default=os.path.join(SCRATCH_BPS, "bps_profil_kabkota_2024.csv"))
ap.add_argument("--geo", default=os.path.join(SCRATCH_BPS, "kabkota_bps.geojson"))
ap.add_argument("--boot", type=int, default=1000)
a = ap.parse_args()
rng = np.random.default_rng(2026)

JAVA = {"Banten", "DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur"}
METRO_JABAR = {"Jabodetabek": {"Bogor", "Kota Bogor", "Kota Depok", "Bekasi", "Kota Bekasi"},
               "Greater Bandung": {"Kota Bandung", "Kota Cimahi", "Bandung", "Bandung Barat", "Sumedang"},
               "Greater Cirebon": {"Kota Cirebon", "Cirebon", "Indramayu", "Majalengka", "Kuningan"}}
METRO_NAT = {  # national metropolitan areas (kab/kota by geoBoundaries name)
    "Jabodetabek": {"Kota Jakarta Pusat", "Kota Jakarta Utara", "Kota Jakarta Barat", "Kota Jakarta Selatan", "Kota Jakarta Timur", "Bogor", "Kota Bogor", "Kota Depok", "Bekasi", "Kota Bekasi", "Tangerang", "Kota Tangerang", "Kota Tangerang Selatan"},
    "Greater Bandung": {"Kota Bandung", "Kota Cimahi", "Bandung", "Bandung Barat", "Sumedang"},
    "Greater Surabaya": {"Kota Surabaya", "Gresik", "Sidoarjo", "Bangkalan", "Mojokerto", "Kota Mojokerto", "Lamongan"},
    "Greater Semarang": {"Kota Semarang", "Kendal", "Demak", "Semarang", "Kota Salatiga", "Grobogan"},
    "Greater Yogyakarta": {"Kota Yogyakarta", "Sleman", "Bantul"},
    "Greater Medan": {"Kota Medan", "Kota Binjai", "Deli Serdang", "Karo"},
    "Greater Makassar": {"Kota Makassar", "Maros", "Gowa", "Takalar"},
    "Greater Denpasar": {"Kota Denpasar", "Badung", "Gianyar", "Tabanan"},
    "Greater Palembang": {"Kota Palembang", "Banyuasin", "Ogan Ilir", "Ogan Komering Ilir"},
    "Greater Cirebon": {"Kota Cirebon", "Cirebon", "Indramayu", "Majalengka", "Kuningan"}}


# ----------------------------------------------------------------- estimators
def wgini(x, w):
    x, w = np.asarray(x, float), np.asarray(w, float)
    o = np.argsort(x / np.maximum(w, 1e-9)); x, w = x[o], w[o]
    cw = np.concatenate([[0], np.cumsum(w) / w.sum()]); cx = np.concatenate([[0], np.cumsum(x) / max(x.sum(), 1e-9)])
    return float(1 - np.sum((cw[1:] - cw[:-1]) * (cx[1:] + cx[:-1])))


def lorenz(x, w, k=40):
    x, w = np.asarray(x, float), np.asarray(w, float)
    o = np.argsort(x / np.maximum(w, 1e-9)); x, w = x[o], w[o]
    cw = np.concatenate([[0], np.cumsum(w) / w.sum()]); cx = np.concatenate([[0], np.cumsum(x) / max(x.sum(), 1e-9)])
    q = np.linspace(0, 1, k + 1)
    return [[round(float(p), 3), round(float(np.interp(p, cw, cx)), 3)] for p in q]


def wranks(r, w):
    """Population-weighted fractional rank, ties get the mean rank."""
    o = np.argsort(r, kind="stable"); r, w = r[o], w[o]; W = w.sum()
    out = np.empty(len(r)); cum = 0.0; i = 0
    while i < len(r):
        j = i
        while j + 1 < len(r) and r[j + 1] == r[i]: j += 1
        sw = w[i:j + 1].sum(); out[o[i:j + 1]] = (cum + sw / 2) / W; cum += sw; i = j + 1
    return out


def conc(h, r, w):
    h, r, w = np.asarray(h, float), np.asarray(r, float), np.asarray(w, float)
    W, H = w.sum(), h.sum()
    if H <= 0 or W <= 0: return float("nan")
    R = wranks(r, w); mu = H / W; mR = np.sum(w * R) / W
    return float(2 * np.sum(w * (h / w - mu) * (R - mR)) / W / mu)


def erreygers(y, r, w, lo=0.0, hi=1.0):
    """CI of a bounded variable y (share per unit in [lo,hi]), units ranked by r, weights w."""
    y, r, w = np.asarray(y, float), np.asarray(r, float), np.asarray(w, float)
    R = wranks(r, w); W = w.sum()
    return float(8 * np.sum(w * y * (R - 0.5)) / W / (hi - lo))


def boot_ci(h, r, w, reps, fn=conc):
    n = len(h); out = []
    idx = rng.integers(0, n, size=(reps, n))
    for b in range(reps):
        i = idx[b]; c = fn(h[i], r[i], w[i])
        if not math.isnan(c): out.append(c)
    out.sort()
    return (out[int(len(out) * .025)], out[int(len(out) * .975)]) if out else (float("nan"), float("nan"))


def curve(h, r, w, k=40):
    o = np.argsort(r, kind="stable"); h, w = np.asarray(h, float)[o], np.asarray(w, float)[o]
    cw = np.concatenate([[0], np.cumsum(w) / w.sum()]); ch = np.concatenate([[0], np.cumsum(h) / max(h.sum(), 1e-9)])
    q = np.linspace(0, 1, k + 1)
    return [[round(float(p), 3), round(float(np.interp(p, cw, ch)), 3)] for p in q]


def quint(h_dict, r, w, extra=None):
    o = np.argsort(r, kind="stable"); cw = np.cumsum(w[o]) / w.sum()
    rows = []
    for q in range(5):
        sel = o[(cw > q / 5) & (cw <= (q + 1) / 5 + (1e-9 if q == 4 else 0))]
        P = w[sel].sum(); row = dict(q=q + 1, n=int(len(sel)), pop=round(float(P)), mean_rank=round(float(np.average(r[sel], weights=w[sel])), 2) if P else None)
        for k, h in h_dict.items(): row[k] = round(float(h[sel].sum()), 2); row[k + "_per100k"] = round(float(1e5 * h[sel].sum() / max(P, 1)), 3)
        if extra:
            for k, fn in extra.items(): row[k] = fn(sel)
        rows.append(row)
    return rows


def theil_decomp(h, w, group):
    """Theil T of supply per capita across units, split between/within groups. Returns shares."""
    h, w = np.asarray(h, float), np.asarray(w, float); H, W = h.sum(), w.sum()
    if H <= 0: return None
    s = h / H; p = w / W; m = (s > 0)
    T = float(np.sum(s[m] * np.log(s[m] / p[m])))
    groups = sorted(set(group)); between = 0.0; within = 0.0; per = []
    for g in groups:
        gm = np.array([x == g for x in group]); Sg, Pg = s[gm].sum(), p[gm].sum()
        if Sg > 0: between += Sg * math.log(Sg / Pg)
        mm = gm & m
        if Sg > 0 and mm.any(): within += Sg * float(np.sum((s[mm] / Sg) * np.log((s[mm] / Sg) / (p[mm] / Pg))))
        per.append(dict(group=g, pop_share=round(float(Pg), 4), supply_share=round(float(Sg), 4), ratio=round(float(Sg / Pg), 2) if Pg > 0 else None))
    return dict(T=round(T, 4), between=round(between, 4), within=round(within, 4), between_share=round(between / T, 3) if T > 0 else None, groups=per)


def hhi_block(x, n_top=10):
    x = np.asarray(x, float); T = x.sum(); s = np.sort(x[x > 0])[::-1] / max(T, 1e-9)
    return dict(n=int((x > 0).sum()), hhi=round(float(np.sum(s ** 2) * 1e4), 1), n_eff=round(float(1 / max(np.sum(s ** 2), 1e-9)), 1),
                cr1=round(float(s[:1].sum()), 4), cr4=round(float(s[:4].sum()), 4), cr10=round(float(s[:10].sum()), 4), gini=round(wgini(x, np.ones(len(x))), 3))


def spearman(x, y):
    from scipy.stats import spearmanr
    r = spearmanr(x, y); return round(float(r.statistic), 3), float(r.pvalue)


def poly_area_km2(geom):
    def ring(c):
        a = 0.0
        for i in range(len(c)):
            x1, y1 = c[i]; x2, y2 = c[(i + 1) % len(c)]; a += (x2 - x1) * (y2 + y1)
        return abs(a / 2)
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    s = 0.0
    for p in polys:
        s += ring(p[0]) - sum(ring(r) for r in p[1:])
    lat = np.mean([c[1] for p in polys for c in p[0]])
    return s * 111.32 * 111.32 * math.cos(math.radians(lat))


# ----------------------------------------------------------------- load units
def load_jabar():
    G = json.load(open("data/jabar_kecamatan_spklu.geojson", encoding="utf-8"))
    units = []
    for f in G["features"]:
        p = f["properties"]
        if p["pop"] < 500: continue
        kab = p["kab"]
        units.append(dict(id=p["code"], name=p["kec"], parent=kab, pop=p["pop"], dens=p["dens"], area=round(p["pop"] / max(p["dens"], 1e-6), 2),
                          ch=p["ch"], kw=p["kw"], kwh=p["kwh"], trx=p["trx"], ev=p["ev"], exp=p["exp"], ipm=p["ipm"], pov=p["pov"],
                          kota=kab.startswith("Kota"), metro=next((m for m, s in METRO_JABAR.items() if kab in s), "Outside metro")))
    meta = dict(scope="jabar", title="West Java", unit="sub-district", unit_pl="sub-districts", parent="district", parent_pl="districts (kabupaten/kota)",
                period="March 2026", n_units=len(units), n_parents=len({u["parent"] for u in units}),
                ses="BPS 2024 by district (kabupaten/kota), inherited by every sub-district inside it",
                sources=["PLN master SPKLU March 2026 (chargers, kW)", "March 2026 transaction recap (kWh, sessions, 331 sites)",
                         "Completed PLN home-charger applications (EV owner locations, 2,181)", "Kontur Population 2023 (H3 r8) aggregated to sub-districts",
                         "Sub-district boundaries dissolved from HDX–BPS 2020 villages", "BPS 2024: HDI, adjusted spending per person, poverty P0 by district"])
    return units, meta


def load_national():
    s = open("equitymap/equity.js", encoding="utf-8").read(); E = json.loads(s[len("window.EQUITY="):].rstrip(";\n"))
    provs = [p["name"] for p in E["provs"]]
    bps = list(csv.DictReader(open(a.bps, encoding="utf-8")))
    alias = {}
    by = {}
    for r in bps:                       # BPS writes renamed districts as "Old name / New name"; index both
        for nm in r["nama_wilayah"].split("/"):
            by[key(nm.strip())] = r
    by["kepulauanseribu"] = next(r for r in bps if "seribu" in r["nama_wilayah"].lower())
    keys = list(by)
    geo = {f["properties"]["kode_wilayah"]: f["geometry"] for f in json.load(open(a.geo, encoding="utf-8"))["features"]}
    units = []; miss = []
    for k in E["kab_stats"]:
        if k["pop"] <= 0: continue
        kk = key(k["name"]); r = by.get(alias.get(kk, "")) or match(kk, by, keys)
        if not r: miss.append(k["name"]); continue
        g = geo.get(r["kode_wilayah"]); area = poly_area_km2(g) if g else None
        prov = provs[k["prov"]]
        units.append(dict(id=r["kode_wilayah"], name=k["name"], parent=prov, pop=k["pop"], area=round(area, 1) if area else None,
                          dens=round(k["pop"] / area, 1) if area else None, ch=k["chargers"], kw=k.get("kw", 0), sites=k["sites"], dc=k.get("dc", 0),
                          pln=k.get("chargers_pln", 0), within10=k["within10"], beyond25=k["beyond25"], d_mean=k["d_mean"],
                          exp=float(r["pengeluaran"]), ipm=float(r["ipm"]), pov=float(r["miskin_p0"]), island=r["pulau"],
                          kota=k["name"].startswith("Kota"), java=prov in JAVA, metro=next((m for m, s in METRO_NAT.items() if k["name"] in s), "Outside metro")))
    print("national units", len(units), "unmatched", miss)
    # density where geometry missing: use parent median
    for u in units:
        if u["dens"] is None:
            sib = [v["dens"] for v in units if v["parent"] == u["parent"] and v["dens"]]; u["dens"] = round(float(np.median(sib)), 1) if sib else 100.0; u["area"] = round(u["pop"] / u["dens"], 1)
    meta = dict(scope="national", title="Indonesia", unit="district", unit_pl="districts (kabupaten/kota)", parent="province", parent_pl="provinces",
                period="June 2026", n_units=len(units), n_parents=len({u["parent"] for u in units}),
                ses="BPS 2024 by district (kabupaten/kota)",
                sources=["PLN master SPKLU 8 June 2026 (3,212 sites; chargers, kW, DC, PLN vs partner)", "Kontur Population 2023 (H3 r6/r8) aggregated to districts",
                         "Share of residents within 10 km / beyond 25 km of an operational charger (equitymap, straight-line)", "geoBoundaries ADM2 / BPS district polygons",
                         "BPS 2024: HDI, adjusted spending per person, poverty P0, island by district"])
    return units, meta


units, meta = load_jabar() if a.scope == "jabar" else load_national()
U = units; n = len(U)
pop = np.array([u["pop"] for u in U], float); ch = np.array([u["ch"] for u in U], float); kw = np.array([u["kw"] for u in U], float)
RANKS = [("exp", "spending per person", "richer", "poorer", np.array([u["exp"] for u in U], float)),
         ("ipm", "Human Development Index", "more developed", "less developed", np.array([u["ipm"] for u in U], float)),
         ("npov", "poverty rate (poorest → least poor)", "less poor", "poorer", -np.array([u["pov"] for u in U], float)),
         ("dens", "population density", "denser", "sparser", np.array([u["dens"] for u in U], float))]
OUT = [("ch", "chargers", ch), ("kw", "charging capacity (kW)", kw)]
if a.scope == "jabar":
    kwh = np.array([u["kwh"] for u in U], float); trx = np.array([u["trx"] for u in U], float); ev = np.array([u["ev"] for u in U], float)
    RANKS.append(("ev100k", "EV owners per 100,000", "more EV owners", "fewer EV owners", 1e5 * ev / pop))
    OUT += [("kwh", "energy sold (kWh)", kwh), ("trx", "charging sessions", trx), ("ev", "EV owners", ev)]
else:
    sites = np.array([u["sites"] for u in U], float); dc = np.array([u["dc"] for u in U], float); within10 = np.array([u["within10"] for u in U], float) / 100
    OUT += [("sites", "charging sites", sites), ("dc", "DC fast chargers", dc)]
    OUT_SHARE = [("within10", "residents within 10 km of a charger", within10)]

# ----------------------------------------------------------------- A. supply concentration
A = dict(supply={k: hhi_block(v) for k, _, v in OUT}, pop=hhi_block(pop))
A["coverage"] = dict(units_with_charger=int((ch > 0).sum()), pop_share=round(float(pop[ch > 0].sum() / pop.sum() * 100), 1),
                     pop_without=round(float(pop[ch == 0].sum())), units_without=int((ch == 0).sum()))
A["lorenz"] = {k: lorenz(v, pop) for k, _, v in OUT[:2]}
A["gini_pc"] = {k: round(wgini(v, pop), 3) for k, _, v in OUT}
top = lambda v, k=10: [dict(name=U[i]["name"], parent=U[i]["parent"], v=float(v[i]), pop=U[i]["pop"], share=round(float(v[i] / max(v.sum(), 1e-9)), 4)) for i in np.argsort(-v)[:k] if v[i] > 0]
A["top"] = {k: top(v) for k, _, v in OUT}
A["largest_without"] = [dict(name=U[i]["name"], parent=U[i]["parent"], pop=U[i]["pop"], exp=U[i]["exp"]) for i in np.argsort(-pop) if ch[i] == 0][:12]
per100k = 1e5 * ch / pop
A["per100k_extremes"] = dict(top=[dict(name=U[i]["name"], parent=U[i]["parent"], v=round(float(per100k[i]), 2), pop=U[i]["pop"]) for i in np.argsort(-per100k)[:10]],
                             bottom_big=[dict(name=U[i]["name"], parent=U[i]["parent"], v=round(float(per100k[i]), 2), pop=U[i]["pop"]) for i in sorted(np.where(pop > np.percentile(pop, 75))[0], key=lambda i: per100k[i])[:10]])

# ----------------------------------------------------------------- B. concentration indices
B = []; curves = {}
for rk, rl, hi_w, lo_w, r in RANKS:
    curves[rk] = {}
    for ok, ol, h in OUT:
        c = conc(h, r, pop); lo, hi = boot_ci(h, r, pop, a.boot)
        B.append(dict(rank=rk, outcome=ok, ci=round(c, 3), lo=round(lo, 3), hi=round(hi, 3), signif=bool(lo > 0 or hi < 0)))
        curves[rk][ok] = curve(h, r, pop)
    # binary "unit has a charger" (Erreygers)
    y = (ch > 0).astype(float); e = erreygers(y, r, pop); lo, hi = boot_ci(y, r, pop, a.boot, fn=erreygers)
    B.append(dict(rank=rk, outcome="has", ci=round(e, 3), lo=round(lo, 3), hi=round(hi, 3), signif=bool(lo > 0 or hi < 0)))
    if a.scope == "national":
        for ok, ol, y in OUT_SHARE:
            e = erreygers(y, r, pop); lo, hi = boot_ci(y, r, pop, a.boot, fn=erreygers)
            B.append(dict(rank=rk, outcome=ok, ci=round(e, 3), lo=round(lo, 3), hi=round(hi, 3), signif=bool(lo > 0 or hi < 0)))
            curves[rk][ok] = curve(y * pop, r, pop)

# ----------------------------------------------------------------- C. quintiles
Q = {}
for rk, rl, hi_w, lo_w, r in RANKS:
    hd = {k: v for k, _, v in OUT}
    extra = {"pop_no_charger_pct": lambda sel: round(float(pop[sel][ch[sel] == 0].sum() / max(pop[sel].sum(), 1) * 100), 1)}
    if a.scope == "national":
        extra["within10"] = lambda sel: round(float(np.average(within10[sel], weights=pop[sel]) * 100), 1)
        extra["beyond25"] = lambda sel: round(float(np.average(np.array([u["beyond25"] for u in U])[sel], weights=pop[sel])), 1)
    Q[rk] = quint(hd, r, pop, extra)

# ----------------------------------------------------------------- D. correlation (scatter)
S = {}
for rk, rl, hi_w, lo_w, r in RANKS:
    rho, p = spearman(r, per100k); S[rk] = dict(rho=rho, p=round(p, 4), n=n)
scatter = [[U[i]["name"], U[i]["parent"], U[i]["pop"], round(float(per100k[i]), 2), U[i]["exp"], U[i]["ipm"], U[i]["pov"], U[i]["dens"], int(ch[i]), int(U[i].get("kota", False))] + ([round(U[i]["within10"], 1)] if a.scope == "national" else [round(float(kwh[i] / pop[i]), 4)]) for i in range(n)]

# ----------------------------------------------------------------- E. within-parent
W = []
parents = sorted({u["parent"] for u in U})
for p in parents:
    m = np.array([u["parent"] == p for u in U]); n_u = int(m.sum()); chs = ch[m].sum()
    if n_u < 6 or chs < 5: continue
    dens = np.array([u["dens"] for u in U], float)[m]
    row = dict(parent=p, n=n_u, chargers=int(chs), pop=round(float(pop[m].sum())), with_charger=int((ch[m] > 0).sum()), per100k=round(float(1e5 * chs / pop[m].sum()), 2),
               ci_ch_dens=round(conc(ch[m], dens, pop[m]), 3), gini=round(wgini(ch[m], pop[m]), 3))
    if a.scope == "jabar":
        row["ci_kwh_dens"] = round(conc(kwh[m], dens, pop[m]), 3); row["ci_ch_ev"] = round(conc(ch[m], 1e5 * ev[m] / pop[m], pop[m]), 3)
    else:
        ex = np.array([u["exp"] for u in U], float)[m]
        if len(set(ex)) > 1: row["ci_ch_exp"] = round(conc(ch[m], ex, pop[m]), 3); row["ci_w10_exp"] = round(erreygers(within10[m], ex, pop[m]), 3)
    W.append(row)
W.sort(key=lambda x: -x["ci_ch_dens"])

# ----------------------------------------------------------------- F. decomposition & groups
D = dict(theil_parent=theil_decomp(ch, pop, [u["parent"] for u in U]))
def group_table(label_fn, name):
    labs = [label_fn(u) for u in U]; rows = []
    for g in sorted(set(labs), key=lambda x: str(x)):
        m = np.array([l == g for l in labs]); P = pop[m].sum()
        rows.append(dict(group=str(g), n=int(m.sum()), pop=round(float(P)), chargers=int(ch[m].sum()), per100k=round(float(1e5 * ch[m].sum() / max(P, 1)), 2),
                         kw_per100k=round(float(1e5 * kw[m].sum() / max(P, 1)), 1), cov=round(float(pop[m][ch[m] > 0].sum() / max(P, 1) * 100), 1),
                         **({"within10": round(float(np.average(within10[m], weights=pop[m]) * 100), 1)} if a.scope == "national" else {"kwh_pc": round(float(kwh[m].sum() / max(P, 1)), 4)})))
    return dict(name=name, rows=rows, theil=theil_decomp(ch, pop, labs))
D["groups"] = [group_table(lambda u: "City (kota)" if u["kota"] else "Regency (kabupaten)", "City vs regency"),
               group_table(lambda u: u["metro"], "Metropolitan areas vs outside")]
if a.scope == "national":
    D["groups"] += [group_table(lambda u: "Java" if u["java"] else "Outside Java", "Java vs outside Java"), group_table(lambda u: u["island"], "By island group")]
    D["theil_island"] = theil_decomp(ch, pop, [u["island"] for u in U])
# 20:20 ratio and Palma on per-capita chargers
o = np.argsort(per100k); cw = np.cumsum(pop[o]) / pop.sum(); cs = np.cumsum(ch[o]) / max(ch.sum(), 1e-9)
sh = lambda q: float(np.interp(q, cw, cs))
D["ratio2020"] = round((1 - sh(.8)) / sh(.2), 1) if sh(.2) > 1e-4 else None; D["palma"] = round((1 - sh(.9)) / sh(.4), 1) if sh(.4) > 1e-4 else None
D["bottom20_share"] = round(sh(.2), 4); D["top20_share"] = round(1 - sh(.8), 4)
D["top10_share"] = round(1 - sh(.9), 3); D["bottom50_share"] = round(sh(.5), 3)

# ----------------------------------------------------------------- G. deficit & robustness
mean100k = 1e5 * ch.sum() / pop.sum(); need = np.maximum(0, mean100k * pop / 1e5 - ch)
G = dict(mean100k=round(float(mean100k), 2), deficit=int(round(need.sum())), units_short=int((need > 0.5).sum()),
         top=[dict(name=U[i]["name"], parent=U[i]["parent"], need=int(round(need[i])), ch=int(ch[i]), pop=U[i]["pop"]) for i in np.argsort(-need)[:12]])
rob = []
main_r = next(r for rk, *_, r in RANKS if rk == "exp")
def rob_row(label, m):
    if m.sum() < 8 or ch[m].sum() < 3: return
    rob.append(dict(subset=label, n=int(m.sum()), ci_ch=round(conc(ch[m], main_r[m], pop[m]), 3), ci_kw=round(conc(kw[m], main_r[m], pop[m]), 3),
                    **({"ci_kwh": round(conc(kwh[m], main_r[m], pop[m]), 3)} if a.scope == "jabar" else {"ci_w10": round(erreygers(within10[m], main_r[m], pop[m]), 3)})))
rob_row("All units", np.ones(n, bool)); rob_row("Regencies only", np.array([not u["kota"] for u in U])); rob_row("Cities only", np.array([u["kota"] for u in U]))
rob_row("Outside metropolitan areas", np.array([u["metro"] == "Outside metro" for u in U])); rob_row("Metropolitan areas only", np.array([u["metro"] != "Outside metro" for u in U]))
if a.scope == "national":
    rob_row("Java only", np.array([u["java"] for u in U])); rob_row("Outside Java", np.array([not u["java"] for u in U]))
    rob_row("Excluding Jabodetabek", np.array([u["metro"] != "Jabodetabek" for u in U]))
else:
    rob_row("Excluding Jabodetabek", np.array([u["metro"] != "Jabodetabek" for u in U]))
    rob_row("Units with ≥ 20,000 residents", pop >= 20000)
G["robust"] = rob
# parent-level CI (national: province table)
PT = []
for p in parents:
    m = np.array([u["parent"] == p for u in U]); P = pop[m].sum()
    PT.append(dict(parent=p, n=int(m.sum()), pop=round(float(P)), chargers=int(ch[m].sum()), kw=int(kw[m].sum()), per100k=round(float(1e5 * ch[m].sum() / max(P, 1)), 2),
                   cov=round(float(pop[m][ch[m] > 0].sum() / max(P, 1) * 100), 1), exp=round(float(np.average(np.array([u["exp"] for u in U])[m], weights=pop[m])), 0),
                   ipm=round(float(np.average(np.array([u["ipm"] for u in U])[m], weights=pop[m])), 1),
                   **({"within10": round(float(np.average(within10[m], weights=pop[m]) * 100), 1), "beyond25": round(float(np.average(np.array([u["beyond25"] for u in U])[m], weights=pop[m])), 1), "java": bool(U[int(np.argmax(m))]["java"])} if a.scope == "national" else {"kwh": int(kwh[m].sum())})))

out = dict(meta=dict(**meta, pop=round(float(pop.sum())), chargers=int(ch.sum()), kw=int(kw.sum()), boot=a.boot,
                     ranks=[dict(key=rk, label=rl, high=hw, low=lw) for rk, rl, hw, lw, _ in RANKS],
                     outcomes=[dict(key=k, label=l) for k, l, _ in OUT] + ([dict(key="has", label="sub-district has a charger (yes/no)")] if a.scope == "jabar" else [dict(key="has", label="district has a charger (yes/no)"), dict(key="within10", label="residents within 10 km of a charger")]),
                     **({"sites": int(sites.sum()), "dc": int(dc.sum()), "pln": int(sum(u["pln"] for u in U)), "within10": round(float(np.average(within10, weights=pop) * 100), 1),
                         "beyond25": round(float(np.average(np.array([u["beyond25"] for u in U]), weights=pop)), 1)} if a.scope == "national" else
                        {"kwh": int(kwh.sum()), "trx": int(trx.sum()), "ev": int(ev.sum()), "sites_trx": int((trx > 0).sum())})),
           A=A, B=B, curves=curves, Q=Q, S=S, scatter=scatter, W=W, D=D, G=G, PT=PT,
           units=[[u["id"], u["name"], u["parent"], u["pop"], round(u["dens"], 1), int(u["ch"]), int(u["kw"]), u["exp"], u["ipm"], u["pov"], int(u["kota"]), u["metro"]] +
                  ([int(u["kwh"]), int(u["trx"]), int(u["ev"])] if a.scope == "jabar" else [round(u["within10"], 1), round(u["beyond25"], 1), int(u["sites"]), int(u["dc"]), int(u["pln"]), u["island"]]) for u in U],
           unit_cols=["id", "name", "parent", "pop", "dens", "ch", "kw", "exp", "ipm", "pov", "kota", "metro"] + (["kwh", "trx", "ev"] if a.scope == "jabar" else ["within10", "beyond25", "sites", "dc", "pln", "island"]))
path = f"analysis/concentration_explorer_{a.scope}.json"
json.dump(out, open(path, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
print(path, "%.0f KB" % (os.path.getsize(path) / 1024))
print("CI chargers~exp %.3f [%s] · kW~exp %.3f · coverage %.1f%% · Gini pc %.3f · 20:20 %s · Theil between-parent share %s" % (
    next(b["ci"] for b in B if b["rank"] == "exp" and b["outcome"] == "ch"), [b for b in B if b["rank"] == "exp" and b["outcome"] == "ch"][0]["signif"],
    next(b["ci"] for b in B if b["rank"] == "exp" and b["outcome"] == "kw"), A["coverage"]["pop_share"], A["gini_pc"]["ch"], D["ratio2020"], D["theil_parent"]["between_share"]))
