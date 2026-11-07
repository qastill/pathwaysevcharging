"""Penguatan temuan makalah "Capacity maps as an equity instrument".

Membaca keluaran prepare.py (capacity.json) dan menambahkan uji yang tidak ada di pipeline asal:

  1. Penugasan kabupaten/kota yang benar: titik pemilik EV dan pusat sel dijatuhkan ke 27 poligon
     BPS Jawa Barat (data/kabkota_bps.geojson). Field "kab" di capacity.json berisi 47 label campuran
     (nama UP3/ULP, duplikat) sehingga Gini "antar-kabupaten" di pipeline asal tidak dihitung atas kabupaten.
  2. Ekuitas pendapatan: indeks konsentrasi (CI) cakupan pemilik terhadap pengeluaran per kapita
     kabupaten/kota, dan cakupan per tersil pengeluaran.
  3. Temuan 1 dengan selang kepercayaan bootstrap, dan AUC: apakah kVA terpasang, atau headroom relatif,
     yang membedakan sel bercharger dari sel tanpa charger.
  4. Baseline acak: 5.000 portofolio 50 situs acak dari kolam yang sama.
  5. Sapuan ukuran portofolio (N), ambang kelayakan (kVA) dan ukuran sel (0,03/0,045/0,06/0,09 derajat).
  6. Dua tingkat jaringan: korelasi headroom trafo vs GI di sel terlayani, dibanding nol independen.

Jalankan dari akar repositori:
    python3 papers/capacity/v3/strengthen.py            # hanya sel 0,045 derajat
    python3 papers/capacity/v3/strengthen.py --variants # + jalankan prepare.py pada 0,03/0,06/0,09 derajat
Keluaran: papers/capacity/v3/strengthen.json
"""
import csv, json, math, os, random, statistics, collections, subprocess, sys, tempfile
from shapely.geometry import shape, Point
from shapely.prepared import prep

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BASE = os.path.join(ROOT, "papers/capacity/capacity.json")
OUT = os.path.join(ROOT, "papers/capacity/v3/strengthen.json")
SEED = 42
N_RANDOM = 5000
N_BOOT = 2000
N_SITES = 50

# ------------------------------------------------------------------ wilayah & sosial-ekonomi
geo = json.load(open(os.path.join(ROOT, "data/kabkota_bps.geojson")))
POLYS = []
for f in geo["features"]:
    code = str(f["properties"]["kode_wilayah"])
    if code.startswith("32."):
        code = f"{float(code):.2f}"
        g = shape(f["geometry"])
        POLYS.append((code, g, prep(g)))
SOSEK = {}
with open(os.path.join(ROOT, "equitymap/input/jabar_sosek_kabkota.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        # kode tersimpan sebagai angka di CSV: "32.1" = Majalengka (32.10)
        SOSEK[f"{float(r['kode_wilayah']):.2f}"] = dict(nama=r["kab"].title().replace("Kab ", "Kab. ").replace("Kota ", "Kota "),
                                        ipm=float(r["ipm"]), exp=float(r["pengeluaran"]),
                                        pov=float(r["miskin_p0"]), pop=int(float(r["penduduk_bps"])))
assert len(POLYS) == 27 and len(SOSEK) == 27, (len(POLYS), len(SOSEK))
_cache = {}


def regency(lat, lon):
    k = (round(lat, 4), round(lon, 4))
    if k in _cache:
        return _cache[k]
    p = Point(lon, lat)
    hit = next((c for c, g, pg in POLYS if pg.contains(p)), None)
    if hit is None:  # titik pesisir/batas: poligon terdekat
        hit = min(POLYS, key=lambda t: t[1].distance(p))[0]
    _cache[k] = hit
    return hit


# ------------------------------------------------------------------ statistik dasar
def rankdata(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a, b):
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return num / den if den else 0.0


def spearman(a, b):
    return pearson(rankdata(a), rankdata(b))


def boot_ci(a, b, rng, n=N_BOOT):
    idx = range(len(a))
    vals = []
    for _ in range(n):
        s = [rng.choice(idx) for _ in idx]
        vals.append(spearman([a[i] for i in s], [b[i] for i in s]))
    vals.sort()
    return [round(vals[int(0.025 * n)], 3), round(vals[int(0.975 * n) - 1], 3)]


def auc(pos, neg):
    """Peluang sel bercharger acak punya nilai lebih tinggi daripada sel tanpa charger acak."""
    r = rankdata(pos + neg)
    rp = sum(r[: len(pos)])
    return (rp - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def gini(vals):
    v = sorted(vals)
    n, s = len(v), sum(v)
    if n == 0 or s == 0:
        return 0.0
    return (2 * sum((i + 1) * x for i, x in enumerate(v))) / (n * s) - (n + 1) / n


def conc_index(y, x):
    """Indeks konsentrasi y menurut peringkat x (tingkat individu). >0 = condong ke x tinggi."""
    n = len(y)
    my = statistics.fmean(y)
    if my == 0:
        return 0.0
    fr = [(r - 0.5) / n for r in rankdata(x)]
    mr = statistics.fmean(fr)
    cov = sum((yi - my) * (ri - mr) for yi, ri in zip(y, fr)) / n
    return 2 * cov / my


def pct(v, x):
    return 100.0 * sum(1 for t in v if t <= x) / len(v)


# ------------------------------------------------------------------ analisis satu payload
def analyse(P, rng, full=True):
    CELL = P["meta"]["cell_deg"]
    FEAS = P["meta"]["feasible"]
    cell_of = lambda lat, lon: (math.floor(lat / CELL), math.floor(lon / CELL))
    C = {}
    for lat, lon, h, hraw, kva, n, gi, ev, chg, kwh, q, kab in P["cells"]:
        C[cell_of(lat, lon)] = dict(lat=lat, lon=lon, h=h, kva=kva, n=n, gi=gi, ev=ev, chg=chg, kwh=kwh,
                                    reg=regency(lat, lon))
    # pemilik: dari titik; kunci sel dihitung ulang dengan rumus yang sama
    owners = []
    miss = 0
    for lat, lon in P["ev"]:
        k = cell_of(lat, lon)
        if k not in C:
            miss += 1
            continue
        owners.append((k, regency(lat, lon)))
    evcells = [k for k, c in C.items() if c["ev"] > 0]
    pool = [k for k in evcells if C[k]["chg"] == 0]
    med_pool = statistics.median([C[k]["ev"] for k in pool]) if pool else 0
    exp_of = {code: SOSEK[code]["exp"] for code in SOSEK}

    def equity(extra):
        got = set(k for k, c in C.items() if c["chg"] > 0) | set(extra)
        cov = [1 if k in got else 0 for k, _ in owners]
        by = collections.defaultdict(lambda: [0, 0])
        for (k, r), y in zip(owners, cov):
            by[r][0] += y
            by[r][1] += 1
        shares = {r: a / b for r, (a, b) in by.items()}
        ci = conc_index(cov, [exp_of[r] for _, r in owners])
        # tersil pengeluaran (tingkat kabupaten, 9 per tersil)
        ranked = sorted(SOSEK, key=lambda c: SOSEK[c]["exp"])
        terc = {c: i // 9 for i, c in enumerate(ranked)}
        tt = [[0, 0], [0, 0], [0, 0]]
        for (k, r), y in zip(owners, cov):
            tt[terc[r]][0] += y
            tt[terc[r]][1] += 1
        return dict(cov=round(100 * sum(cov) / len(cov), 1), gini=round(gini(list(shares.values())), 3),
                    ci=round(ci, 3), terc=[round(100 * a / b, 1) if b else None for a, b in tt],
                    regs=len(shares), shares={r: round(s, 3) for r, s in shares.items()})

    def evaluate(sel):
        owners_n = sum(C[k]["ev"] for k in sel)
        e = equity(sel)
        return dict(owners=owners_n, stranded=sum(1 for k in sel if C[k]["ev"] < med_pool),
                    infeas=sum(1 for k in sel if C[k]["h"] < FEAS),
                    regs_new=len(set(C[k]["reg"] for k in sel)), cov=e["cov"], gini=e["gini"], ci=e["ci"],
                    terc=e["terc"])

    def pick(rule, N, feas=FEAS):
        if rule == "headroom":
            return sorted(pool, key=lambda k: (-C[k]["h"], k))[:N]
        if rule == "demand":
            return sorted(pool, key=lambda k: (-C[k]["ev"], k))[:N]
        ok = sorted([k for k in pool if C[k]["h"] >= feas], key=lambda k: (-C[k]["ev"], k))
        no = sorted([k for k in pool if C[k]["h"] < feas], key=lambda k: (-C[k]["ev"], k))
        return (ok + no)[:N]

    N_prop = max(1, round(len(pool) * N_SITES / 132))  # 50 dari 132 = 38 % kolam, seperti kasus dasar
    res = dict(cell=CELL, cells=len(C), cells_ev=len(evcells), cells_chg=sum(1 for c in C.values() if c["chg"]),
               pool=len(pool), pool_ev=sum(C[k]["ev"] for k in pool), med_pool=med_pool,
               owners_mapped=len(owners), owners_missing=miss, n_prop=N_prop)
    res["baseline"] = {k: v for k, v in equity([]).items()}
    res["rules"] = {r: dict(evaluate(pick(r, N_SITES)), sel=[[C[k]["lat"], C[k]["lon"], C[k]["ev"], round(C[k]["h"])]
                                                             for k in pick(r, N_SITES)])
                    for r in ("headroom", "demand", "dwh")}
    res["rules_prop"] = {r: evaluate(pick(r, N_prop)) for r in ("headroom", "demand", "dwh")}

    # --- temuan 1: kepadatan vs ruang sisa
    served = [c for c in C.values() if c["chg"] > 0 and c["kva"] > 0]
    kwh = [c["kwh"] for c in served]
    f1 = dict(n=len(served))
    for name, xs in (("abs", [c["h"] for c in served]), ("rel", [c["h"] / c["kva"] for c in served]),
                     ("kva", [c["kva"] for c in served]), ("ntr", [c["n"] for c in served])):
        f1[name] = round(spearman(kwh, xs), 3)
        if full:
            f1[name + "_ci"] = boot_ci(kwh, xs, rng)
    tr = [c for c in C.values() if c["kva"] > 0]
    pos = [c for c in tr if c["chg"] > 0]
    neg = [c for c in tr if c["chg"] == 0]
    f1["auc"] = {name: round(auc([fn(c) for c in pos], [fn(c) for c in neg]), 3) for name, fn in (
        ("kva", lambda c: c["kva"]), ("ntr", lambda c: c["n"]), ("abs", lambda c: c["h"]),
        ("rel", lambda c: c["h"] / c["kva"]), ("ev", lambda c: c["ev"]))}
    f1["n_pos"], f1["n_neg"] = len(pos), len(neg)
    f1["med_rel"] = dict(chg=round(statistics.median([c["h"] / c["kva"] for c in pos]), 3),
                         nochg=round(statistics.median([c["h"] / c["kva"] for c in neg]), 3))
    f1["med_kva"] = dict(chg=round(statistics.median([c["kva"] for c in pos])),
                         nochg=round(statistics.median([c["kva"] for c in neg])))
    res["f1"] = f1

    # --- celah & kuadran (dihitung ulang supaya sama untuk tiap ukuran sel)
    h_all = sum(c["h"] for c in C.values())
    res["gap"] = dict(h_nochg=round(100 * sum(c["h"] for c in C.values() if c["chg"] == 0) / h_all, 1),
                      ev_nochg=round(100 * sum(c["ev"] for c in C.values() if c["chg"] == 0)
                                     / sum(c["ev"] for c in C.values()), 1))
    if evcells:
        mev = statistics.median([C[k]["ev"] for k in evcells])
        mh = statistics.median([C[k]["h"] for k in evcells])
        tev = sum(C[k]["ev"] for k in evcells)
        tch = sum(C[k]["chg"] for k in evcells)
        hl = [k for k in evcells if C[k]["ev"] > mev and C[k]["h"] <= mh]
        res["hl"] = dict(cells=len(hl), evp=round(100 * sum(C[k]["ev"] for k in hl) / tev, 1),
                         chgp=round(100 * sum(C[k]["chg"] for k in hl) / tch, 1),
                         unserved=sum(1 for k in hl if C[k]["chg"] == 0),
                         unserved_ev=sum(C[k]["ev"] for k in hl if C[k]["chg"] == 0))

    if not full:
        return res

    # --- baseline acak
    rnd = collections.defaultdict(list)
    for _ in range(N_RANDOM):
        s = rng.sample(pool, N_SITES)
        rnd["owners"].append(sum(C[k]["ev"] for k in s))
        rnd["stranded"].append(sum(1 for k in s if C[k]["ev"] < med_pool))
        rnd["infeas"].append(sum(1 for k in s if C[k]["h"] < FEAS))
    res["random"] = dict(n=N_RANDOM, owners=rnd["owners"], stranded=rnd["stranded"], infeas=rnd["infeas"],
                         owners_mean=round(statistics.fmean(rnd["owners"]), 1),
                         owners_p95=sorted(rnd["owners"])[int(0.95 * N_RANDOM)],
                         stranded_mean=round(statistics.fmean(rnd["stranded"]), 1),
                         infeas_mean=round(statistics.fmean(rnd["infeas"]), 2),
                         pct={r: dict(owners=round(pct(rnd["owners"], res["rules"][r]["owners"]), 1),
                                      stranded=round(pct(rnd["stranded"], res["rules"][r]["stranded"]), 1))
                              for r in res["rules"]})
    # baseline acak untuk Gini & CI (lebih mahal; 1.000 undian)
    g_r, ci_r = [], []
    for _ in range(1000):
        e = equity(rng.sample(pool, N_SITES))
        g_r.append(e["gini"])
        ci_r.append(e["ci"])
    res["random"]["gini_mean"] = round(statistics.fmean(g_r), 3)
    res["random"]["ci_mean"] = round(statistics.fmean(ci_r), 3)

    # --- sapuan N
    res["nsweep"] = []
    for N in list(range(5, len(pool) + 1, 5)) + ([len(pool)] if len(pool) % 5 else []):
        row = dict(N=N)
        for r in ("headroom", "demand", "dwh"):
            s = pick(r, N)
            row[r] = dict(owners=sum(C[k]["ev"] for k in s), stranded=sum(1 for k in s if C[k]["ev"] < med_pool),
                          infeas=sum(1 for k in s if C[k]["h"] < FEAS))
        res["nsweep"].append(row)

    # --- sapuan ambang kelayakan
    res["feas"] = []
    for fz in (120, 240, 480, 960):
        row = dict(kva=fz, feasible_pool=sum(1 for k in pool if C[k]["h"] >= fz))
        for r in ("headroom", "demand", "dwh"):
            s = pick(r, N_SITES, fz)
            row[r] = dict(owners=sum(C[k]["ev"] for k in s), infeas=sum(1 for k in s if C[k]["h"] < fz))
        res["feas"].append(row)

    # --- dua tingkat jaringan (sel terlayani dengan GI tertaut)
    two = [c for c in served if c["gi"] > 0]
    mh = statistics.median([c["h"] for c in two])
    mg = statistics.median([c["gi"] for c in two])
    lo_hi = sum(1 for c in two if c["h"] <= mh and c["gi"] > mg)
    hi_lo = sum(1 for c in two if c["h"] > mh and c["gi"] <= mg)
    res["two"] = dict(n=len(two), n_served=len(served), rho=round(spearman([c["h"] for c in two], [c["gi"] for c in two]), 3),
                      rho_ci=boot_ci([c["h"] for c in two], [c["gi"] for c in two], rng),
                      tight_tr_ample_gi=lo_hi, ample_tr_tight_gi=hi_lo,
                      discord=round(100 * (lo_hi + hi_lo) / len(two), 1),
                      pts=[[round(c["h"]), round(c["gi"], 1), c["kwh"]] for c in two])
    # --- kabupaten: tabel
    base_sh = res["baseline"]["shares"]
    owners_by = collections.Counter(r for _, r in owners)
    res["regencies"] = sorted([dict(code=c, nama=SOSEK[c]["nama"], exp=SOSEK[c]["exp"], ipm=SOSEK[c]["ipm"],
                                    owners=owners_by.get(c, 0), cov=base_sh.get(c))
                               for c in SOSEK], key=lambda d: -d["exp"])
    return res


def run_variant(cell, tmp):
    src = open(os.path.join(ROOT, "papers/capacity/prepare.py"), encoding="utf-8").read()
    out = os.path.join(tmp, f"cap_{cell}.json")
    lines = []
    for ln in src.splitlines():
        if ln.startswith("ROOT = "):
            ln = f"ROOT = {ROOT!r}"
        elif ln.startswith("OUT = "):
            ln = f"OUT = {out!r}"
        elif ln.startswith("CELL "):
            ln = f"CELL = {cell}"
        lines.append(ln)
    path = os.path.join(tmp, f"prep_{cell}.py")
    open(path, "w").write("\n".join(lines))
    subprocess.run([sys.executable, path], check=True, stdout=subprocess.DEVNULL)
    return json.load(open(out))


if __name__ == "__main__":
    rng = random.Random(SEED)
    P = json.load(open(BASE))
    out = dict(base=analyse(P, rng, full=True), variants=[])
    if "--variants" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            for cell in (0.03, 0.06, 0.09):
                print(f"  varian sel {cell} derajat ...")
                out["variants"].append(analyse(run_variant(cell, tmp), rng, full=False))
    b = out["base"]
    out["variants"].insert(0 if False else 0, {k: v for k, v in b.items() if k in (
        "cell", "cells", "cells_ev", "cells_chg", "pool", "pool_ev", "n_prop", "baseline", "rules_prop", "f1", "gap", "hl")})
    out["variants"].sort(key=lambda v: v["cell"])
    json.dump(out, open(OUT, "w"), separators=(",", ":"))
    print(f"ditulis {OUT}")
    print(json.dumps({k: b[k] for k in ("cells", "pool", "owners_mapped", "owners_missing")}))
    print("baseline", {k: v for k, v in b["baseline"].items() if k != "shares"})
    for r, v in b["rules"].items():
        print(r, {k: x for k, x in v.items() if k != "sel"})
    print("f1", {k: v for k, v in b["f1"].items()})
    print("random", {k: v for k, v in b["random"].items() if k not in ("owners", "stranded", "infeas")})
    print("two", {k: v for k, v in b["two"].items() if k != "pts"})
    print("feas", b["feas"])
    for v in out["variants"]:
        print("cell", v["cell"], "pool", v["pool"], "N", v["n_prop"], "f1", {k: v["f1"][k] for k in ("abs", "rel")},
              "auc", v["f1"]["auc"], "gap", v["gap"], "hl", v.get("hl"),
              {r: (x["owners"], x["stranded"], x["infeas"], x["gini"], x["ci"]) for r, x in v["rules_prop"].items()},
              "base", (v["baseline"]["cov"], v["baseline"]["gini"], v["baseline"]["ci"]))
