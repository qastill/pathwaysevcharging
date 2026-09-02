"""Bangun payload peta kapasitas (CIRED 2027) dari data mentah PLN UID Jawa Barat.

Mereproduksi metode makalah "Capacity maps as an equity instrument":
  * headroom trafo distribusi & Gardu Induk pada batas pembebanan 80 %
  * koreksi pertumbuhan beban ke Maret 2026
  * agregasi ke sel 0,045 derajat (~5 km)
  * klasifikasi permintaan x headroom
  * tiga aturan penempatan 50 situs baru
  * audit kesiapan publikasi data

Keluaran: papers/capacity/capacity.json  (disisipkan sebagai D.cap oleh inject.py)

Jalankan dari akar repositori:  python3 papers/capacity/prepare.py
"""
import csv, json, math, statistics, warnings, collections, datetime, os, sys
warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "papers/capacity/capacity.json")

# ---------------------------------------------------------------- parameter
LIMIT      = 0.80          # batas pembebanan perencanaan
REF_YEAR   = 2026.2        # Maret 2026
GROWTH     = [0.0, 0.030, 0.059, 0.097]   # 0 = apa adanya, 3,0 % = kasus dasar
BASE_G     = 0.030
GI_YEAR    = 2022.3        # register beban GI/penyulang bertanggal April 2022 (Tabel 1 naskah)
CELL       = 0.045         # ~5 km
N_SITES    = 50
FEASIBLE   = 240.0         # kVA -- satu situs 4 x 60 kW
BBOX       = (-8.0, -5.0, 105.0, 109.5)   # s, n, w, e


def flo(x):
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def yr(s):
    """'2024-03-01 10:04' -> 2024.16 (tahun desimal)."""
    if not s:
        return None
    s = str(s)[:10]
    try:
        d = datetime.date.fromisoformat(s)
    except ValueError:
        return None
    if not (2015 <= d.year <= 2026):
        return None
    return d.year + (d.timetuple().tm_yday - 1) / 365.25


def cell_of(lat, lon):
    return (math.floor(lat / CELL), math.floor(lon / CELL))


def cell_center(cy, cx):
    return round((cy + 0.5) * CELL, 5), round((cx + 0.5) * CELL, 5)


# ------------------------------------------------------------- 1. trafo
print("membaca register gardu distribusi ...")
import openpyxl
wb = openpyxl.load_workbook(os.path.join(ROOT, "Gardu_Beban_Lokasi_JABAR.xlsx"), read_only=True)
ws = wb["DATA_GARDU"]
it = ws.iter_rows(values_only=True)
hdr = list(next(it))
I = {k: i for i, k in enumerate(hdr)}

total = 0
audit = collections.Counter()
T = []            # trafo layak pakai
gi_raw = {}       # (kode GI, nomor trafo) -> (MVA, %beban)

for r in it:
    if r[0] is None:
        continue
    total += 1
    lat, lon = flo(r[I["LATITUDE"]]), flo(r[I["LONGITUDE"]])
    kva = flo(r[I["KAPASITAS_KVA"]])
    pb  = flo(r[I["PERSEN_BEBAN"]])
    gik = (r[I["GI_KODE"]] or "").strip()
    jar = flo(r[I["JARAK_KE_TITIK_SSOT_M"]])

    # --- audit kesiapan publikasi (dihitung atas seluruh 53.797 catatan)
    if not gik:                                   audit["gi"] += 1
    if jar is not None and jar > 1000:            audit["koord"] += 1
    if pb is None:                                audit["beban"] += 1
    if kva is None:                               audit["kva"] += 1
    if lat is None or lon is None or r[I["STATUS_KOORDINAT"]] != "VALID":
        audit["geo"] += 1
    if (r[I["PETUGAS_SIANG"]] or r[I["PETUGAS_MALAM"]]):
        audit["pii"] += 1

    # --- saringan kelayakan
    if lat is None or lon is None or r[I["STATUS_KOORDINAT"]] != "VALID":
        continue
    if not (BBOX[0] < lat < BBOX[1] and BBOX[2] < lon < BBOX[3]):
        continue
    if kva is None or not (5 <= kva <= 3000):
        continue
    if pb is None or not (0 <= pb <= 200):
        continue

    t = yr(r[I["TGL_UKUR_MALAM"]]) or yr(r[I["TGL_UKUR_SIANG"]])
    T.append((lat, lon, kva, pb / 100.0, t, gik,
              (r[I["KOTA_KAB"]] or "").strip(), (r[I["UP3"]] or "").strip()))

    gmva, gps, gpm = flo(r[I["GI_DAYA_MVA"]]), flo(r[I["GI_PERSEN_SIANG"]]), flo(r[I["GI_PERSEN_MALAM"]])
    gtr = str(r[I["GI_TRAFO"]] or "").strip()
    if gik and gmva and 5 <= gmva <= 500:
        lam = max(gps or 0, gpm or 0) / 100.0
        if 0 <= lam <= 2:
            gi_raw[(gik, gtr)] = (gmva, lam)
wb.close()

print(f"  catatan total {total:,} | layak pakai {len(T):,}")
print(f"  trafo GI unik {len(gi_raw)} | {sum(v[0] for v in gi_raw.values()):,.0f} MVA")

ages = sorted(REF_YEAR - t[4] for t in T if t[4])
print(f"  umur survei: median {statistics.median(ages):.1f} th | tertua {max(ages):.1f} th")
med_age = statistics.median(ages)


def adj(lam, t, g):
    """Beban disusutkan-majukan ke Maret 2026."""
    if g == 0 or not t:
        return lam
    return lam * (1 + g) ** (REF_YEAR - t)


# headroom trafo per skenario pertumbuhan
scen = []
for g in GROWTH:
    h_tot = 0.0
    over = 0
    for lat, lon, kva, lam, t, *_ in T:
        l2 = adj(lam, t, g)
        if l2 > LIMIT:
            over += 1
        h_tot += max(0.0, kva * (LIMIT - l2))
    # GI: register GI bertanggal April 2022 -> dituakan (REF_YEAR - GI_YEAR) tahun
    gh = 0.0
    for mva, lam in gi_raw.values():
        l2 = lam * (1 + g) ** (REF_YEAR - GI_YEAR) if g else lam
        gh += max(0.0, mva * (LIMIT - l2))
    scen.append(dict(g=round(g * 100, 1), trafo=round(h_tot / 1000, 1), gi=round(gh, 1), over=over))
    print(f"  g={g*100:4.1f}%/th -> trafo {h_tot/1000:7.1f} MVA | GI {gh:7.1f} MVA | lewat 80 %: {over:,}")

# ---------------------------------------------------------- 2. sel 5 km
cells = collections.defaultdict(lambda: dict(h=0.0, hraw=0.0, kva=0.0, n=0,
                                             gis=set(), ev=0, chg=0, kwh=0.0,
                                             sites=0, kab=collections.Counter(),
                                             evkab=collections.Counter()))
gi_head = {k: max(0.0, mva * (LIMIT - lam * (1 + BASE_G) ** (REF_YEAR - GI_YEAR)))
           for k, (mva, lam) in gi_raw.items()}
gi_by_code = collections.defaultdict(float)
for (code, _tr), h in gi_head.items():
    gi_by_code[code] += h

for lat, lon, kva, lam, t, gik, kab, up3 in T:
    c = cells[cell_of(lat, lon)]
    l2 = adj(lam, t, BASE_G)
    c["h"] += max(0.0, kva * (LIMIT - l2))
    c["hraw"] += max(0.0, kva * (LIMIT - lam))
    c["kva"] += kva
    c["n"] += 1
    if gik:
        c["gis"].add(gik)
    if kab:
        c["kab"][kab] += 1

# --- pelanggan EV terdaftar
print("membaca register pelanggan EV ...")
rows = list(csv.reader(open(os.path.join(ROOT, "Data pelanggan EV.txt"), encoding="utf-8",
                            errors="replace"), delimiter="\t"))
ch = {k: i for i, k in enumerate(rows[0])}
nev = 0
ev_pts = []
for r in rows[1:]:
    if len(r) < len(rows[0]):
        r = r + [""] * (len(rows[0]) - len(r))
    lat, lon = flo(r[ch["Lat"]]), flo(r[ch["Long"]])
    if lat is None or lon is None:
        continue
    if not (BBOX[0] < lat < BBOX[1] and BBOX[2] < lon < BBOX[3]):
        continue
    c = cells[cell_of(lat, lon)]
    c["ev"] += 1
    kab_ev = (r[ch["Kabupaten"]] or "").strip().upper()
    if kab_ev:
        c["evkab"][kab_ev] += 1
    nev += 1
    ev_pts.append((round(lat, 4), round(lon, 4)))
print(f"  pelanggan EV tergeokode {nev:,}")

# --- SPKLU (situs) + energi Maret 2026
print("membaca rekap SPKLU ...")
sites = []
n_reg = n_nocoord = 0
with open(os.path.join(ROOT, "Rekap_SPKLU_Jabar_ArcGIS.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        n_reg += 1
        lat, lon = flo(r["Latitude"]), flo(r["Longitude"])
        if lat is None or lon is None or not (BBOX[0] < lat < BBOX[1] and BBOX[2] < lon < BBOX[3]):
            n_nocoord += 1
            continue
        kwh = flo(r["Energi_kWh"]) or 0.0
        c = cells[cell_of(lat, lon)]
        c["chg"] += 1
        c["sites"] += 1
        c["kwh"] += kwh
        sites.append(dict(lat=round(lat, 5), lon=round(lon, 5), nm=r["Nama_SPKLU"].strip(),
                          kab=r["Kota_Kab"].strip(), jl=r["Jenis_Lokasi"].strip(),
                          kwh=round(kwh), trx=int(flo(r["Jml_Transaksi"]) or 0)))
print(f"  situs SPKLU terdaftar {n_reg} | terpetakan {len(sites)} | tanpa koordinat {n_nocoord}")

# --- rakit daftar sel
CL = []
for (cy, cx), c in cells.items():
    lat, lon = cell_center(cy, cx)
    gih = statistics.mean([gi_by_code[g] for g in c["gis"] if g in gi_by_code]) if \
        [g for g in c["gis"] if g in gi_by_code] else 0.0
    CL.append(dict(y=cy, x=cx, lat=lat, lon=lon,
                   h=round(c["h"], 1), hraw=round(c["hraw"], 1), kva=round(c["kva"]),
                   n=c["n"], gi=round(gih, 1), ev=c["ev"], chg=c["chg"], kwh=round(c["kwh"]),
                   kab=(c["kab"].most_common(1)[0][0].upper() if c["kab"]
                        else (c["evkab"].most_common(1)[0][0] if c["evkab"] else ""))))
CL.sort(key=lambda d: (-d["ev"], -d["h"]))
print(f"  sel terisi {len(CL)} | dengan pemilik EV {sum(1 for c in CL if c['ev'])} | "
      f"dengan SPKLU {sum(1 for c in CL if c['chg'])}")

# ------------------------------------------------- 3. korelasi & kuadran
def spearman(a, b):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        rk = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            r = (i + j) / 2 + 1
            for k in range(i, j + 1):
                rk[order[k]] = r
            i = j + 1
        return rk
    ra, rb = rank(a), rank(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((ra[i] - ma) * (rb[i] - mb) for i in range(n))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((x - mb) ** 2 for x in rb))
    return num / den if den else 0.0


served = [c for c in CL if c["chg"] > 0 and c["kva"] > 0]
rho_abs = spearman([c["kwh"] for c in served], [c["h"] for c in served])
rho_rel = spearman([c["kwh"] for c in served], [c["h"] / c["kva"] for c in served])
print(f"  Spearman energi~headroom absolut {rho_abs:+.2f} | relatif {rho_rel:+.2f} (n={len(served)})")

evc = [c for c in CL if c["ev"] > 0]
med_ev = statistics.median([c["ev"] for c in evc])
med_h = statistics.median([c["h"] for c in evc])
quad = collections.defaultdict(lambda: dict(cells=0, ev=0, chg=0))
for c in evc:
    hi_d = c["ev"] > med_ev
    hi_h = c["h"] > med_h
    c["q"] = ("HH" if hi_h else "HL") if hi_d else ("LH" if hi_h else "LL")
    q = quad[c["q"]]
    q["cells"] += 1
    q["ev"] += c["ev"]
    q["chg"] += c["chg"]
tot_ev = sum(c["ev"] for c in evc)
tot_chg = sum(c["chg"] for c in evc)
for k, v in quad.items():
    v["evp"] = round(100 * v["ev"] / tot_ev, 1)
    v["chgp"] = round(100 * v["chg"] / tot_chg, 1) if tot_chg else 0
    print(f"  kuadran {k}: {v['cells']:3d} sel | {v['evp']:5.1f} % pemilik | {v['chgp']:5.1f} % charger")
gap_cells = [c for c in evc if c["q"] == "HL" and c["chg"] == 0]
print(f"  sel permintaan tinggi/headroom rendah tanpa charger: {len(gap_cells)} "
      f"({sum(c['ev'] for c in gap_cells)} pemilik)")

# headroom di sel tanpa charger
h_all = sum(c["h"] for c in CL)
h_nochg = sum(c["h"] for c in CL if c["chg"] == 0)
ev_nochg = sum(c["ev"] for c in CL if c["chg"] == 0)

# ----------------------------------------------- 4. aturan penempatan
pool = [c for c in evc if c["chg"] == 0]
med_pool = statistics.median([c["ev"] for c in pool])
print(f"  median permintaan kandidat: {med_pool:g} pemilik/sel")
print(f"  kolam sel belum terlayani dengan pemilik EV: {len(pool)} ({sum(c['ev'] for c in pool)} pemilik)")


def gini(vals):
    v = sorted(vals)
    n = len(v)
    s = sum(v)
    if n == 0 or s == 0:
        return 0.0
    cum = sum((i + 1) * v[i] for i in range(n))
    return (2 * cum) / (n * s) - (n + 1) / n


def coverage(extra):
    """Bagian pemilik EV yang tinggal di sel bercharger, plus Gini antar-kabupaten."""
    got = set((c["y"], c["x"]) for c in CL if c["chg"] > 0) | set((c["y"], c["x"]) for c in extra)
    by_kab = collections.defaultdict(lambda: [0, 0])   # [tercakup, total]
    tot = cov = 0
    for c in CL:
        if not c["ev"]:
            continue
        tot += c["ev"]
        inside = (c["y"], c["x"]) in got
        cov += c["ev"] if inside else 0
        k = by_kab[c["kab"] or "?"]
        k[1] += c["ev"]
        k[0] += c["ev"] if inside else 0
    shares = [a / b for a, b in by_kab.values() if b]
    return 100 * cov / tot, gini(shares)


RULES = [
    ("headroom", "Headroom-only", lambda p: sorted(p, key=lambda c: -c["h"])),
    ("demand",   "Demand-only",   lambda p: sorted(p, key=lambda c: -c["ev"])),
    ("dwh",      "Demand within headroom",
     lambda p: sorted([c for c in p if c["h"] >= FEASIBLE], key=lambda c: -c["ev"])
               + sorted([c for c in p if c["h"] < FEASIBLE], key=lambda c: -c["ev"])),
]
base_cov, base_gini = coverage([])
print(f"  baseline: cakupan {base_cov:.1f} % | Gini {base_gini:.3f}")

rules_out = []
for key, label, fn in RULES:
    sel = fn(pool)[:N_SITES]
    owners = sum(c["ev"] for c in sel)
    stranded = sum(1 for c in sel if c["ev"] < med_pool)
    infeas = sum(1 for c in sel if c["h"] < FEASIBLE)
    regen = len(set(c["kab"] for c in sel if c["kab"]))
    cov, gi_ = coverage(sel)
    rules_out.append(dict(key=key, label=label, owners=owners, stranded=stranded,
                          infeas=infeas, regen=regen, cov=round(cov, 1), gini=round(gi_, 3),
                          sel=[[c["lat"], c["lon"], c["ev"], round(c["h"])] for c in sel]))
    print(f"  {label:24s} pemilik {owners:4d} | terlantar {stranded:2d} | taklayak {infeas} | "
          f"kab {regen:2d} | cakupan {cov:5.1f} % | Gini {gi_:.3f}")

# sensitivitas pertumbuhan untuk aturan terpilih
sens = []
for g in (0.030, 0.059, 0.097):
    h2 = collections.defaultdict(float)
    for lat, lon, kva, lam, t, *_ in T:
        h2[cell_of(lat, lon)] += max(0.0, kva * (LIMIT - adj(lam, t, g)))
    p2 = [dict(c, h=round(h2[(c["y"], c["x"])], 1)) for c in pool]
    s2 = sorted([c for c in p2 if c["h"] >= FEASIBLE], key=lambda c: -c["ev"])[:N_SITES]
    sens.append(dict(g=round(g * 100, 1), owners=sum(c["ev"] for c in s2)))
print("  sensitivitas demand-within-headroom:", sens)

# ------------------------------------------------------------ 5. keluaran
payload = dict(
    meta=dict(total=total, usable=len(T), ev=nev, sites=len(sites), sites_reg=n_reg, sites_nocoord=n_nocoord,
              cells=len(CL), cells_ev=len(evc), cells_chg=sum(1 for c in CL if c["chg"]),
              gi_trafo=len(gi_raw), gi_mva=round(sum(v[0] for v in gi_raw.values())),
              med_age=round(med_age, 1), max_age=round(max(ages), 1), gi_year=GI_YEAR,
              limit=LIMIT, cell_deg=CELL, ref=REF_YEAR, base_g=BASE_G, feasible=FEASIBLE),
    cells=[[c["lat"], c["lon"], c["h"], c["hraw"], c["kva"], c["n"], c["gi"],
            c["ev"], c["chg"], c["kwh"], c.get("q", ""), c["kab"]] for c in CL],
    sites=sites,
    ev=ev_pts,
    scen=scen,
    quad={k: v for k, v in quad.items()},
    med=dict(ev=med_ev, h=round(med_h, 1), pool=med_pool),
    rho=dict(abs=round(rho_abs, 3), rel=round(rho_rel, 3), n=len(served)),
    gap=dict(cells=len(gap_cells), ev=sum(c["ev"] for c in gap_cells),
             h_nochg_pct=round(100 * h_nochg / h_all, 1),
             ev_nochg_pct=round(100 * ev_nochg / tot_ev, 1)),
    rules=rules_out,
    baseline=dict(cov=round(base_cov, 1), gini=round(base_gini, 3)),
    sens=sens,
    audit={k: round(100 * v / total, 1) for k, v in audit.items()},
    audit_n=dict(audit),
    pool=dict(cells=len(pool), ev=sum(c["ev"] for c in pool)),
)
s = json.dumps(payload, separators=(",", ":"))
open(OUT, "w").write(s)
print(f"\ncapacity.json ditulis: {len(s)/1024:.0f} KB")
