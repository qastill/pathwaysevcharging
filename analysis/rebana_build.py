"""Bangun ulang analysis/rebana_explorer.html (tab 🏭 Rebana) dari data mentah repo.

Langkah:
  1. Baca data mentah PLN di akar repo (Master SPKLU, transaksi Maret 2026, register charger rumah,
     register gardu distribusi, laporan beban trafo GI) dan data spasial (kab/kota BPS, kecamatan Jabar,
     jaringan Jamali hasil cocokan OSM–RUPTL).
  2. Hitung agregat Rebana dan lapisan peta Indramayu. Privasi: gardu distribusi hanya keluar sebagai
     agregat per kecamatan dan per heksagon H3 res 7 (~5 km²), tanpa nama/kode/koordinat gardu;
     charger rumah hanya sebagai hitungan per kecamatan.
  3. Tanam JSON ke analysis/rebana_explorer_src.html (penanda /*__DATA__*/) -> analysis/rebana_explorer.html.

    pip install openpyxl shapely h3 pvlib pandas xlrd
    python3 analysis/rebana_build.py           # lalu python3 analysis/inject_rebana.py bila tab belum terpasang
"""
import collections, json, os, re, warnings
import math
import openpyxl, h3, pvlib, xlrd, pandas as pd
from shapely.geometry import shape, Point, LineString, mapping
from shapely.ops import unary_union
from shapely.strtree import STRtree

warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
OUT_JSON = "analysis/rebana_data.json"
SRC, DST = "analysis/rebana_explorer_src.html", "analysis/rebana_explorer.html"
BBOX = (107.45, -7.15, 108.85, -6.05)  # lon0, lat0, lon1, lat1

REB = ["KAB. SUBANG", "KAB. CIREBON", "KAB. INDRAMAYU", "KAB. MAJALENGKA", "KAB. SUMEDANG", "KAB. KUNINGAN", "KOTA CIREBON"]
def norm(k):
    if not k: return None
    k = str(k).upper()
    for r in ("SUBANG", "INDRAMAYU", "MAJALENGKA", "KUNINGAN", "SUMEDANG"):
        if r in k: return "KAB. " + r
    if "CIREBON" in k: return "KOTA CIREBON" if "KOTA" in k else "KAB. CIREBON"
    return None
def title(k): return k.title().replace("Kab. ", "Kab. ")
def fnum(x):
    try: return float(x)
    except Exception: return 0.0
def kw(v):
    m = re.search(r"([\d.]+)", str(v)); return float(m.group(1)) if m else 0.0
def rnd(geom, tol, dec=4):
    g = mapping(geom.simplify(tol, preserve_topology=True))
    def r(c): return [round(c[0], dec), round(c[1], dec)] if isinstance(c[0], (int, float)) else [r(x) for x in c]
    return {"type": g["type"], "coordinates": r(g["coordinates"])}
def inb(x, y): return BBOX[0] <= x <= BBOX[2] and BBOX[1] <= y <= BBOX[3]

D = {}

# ---------- 1. SPKLU master (Jabar) ----------
wb = openpyxl.load_workbook("Master SPKLU Maret 2026.xlsx", read_only=True)
rows = list(wb.worksheets[0].iter_rows(values_only=True)); H = {h: i for i, h in enumerate(rows[0])}
jabar = [r for r in rows[1:] if r[H["LOKASI"]]]
reb = [r for r in jabar if norm(r[H["KOTA/KAB"]])]
units = []
for r in reb:
    try: la, lo = float(r[H["LATITUDE"]]), float(r[H["LONGITUDE"]])
    except Exception: continue
    units.append({"n": str(r[H["LOKASI"]])[:48], "k": title(norm(r[H["KOTA/KAB"]])), "la": round(la, 5), "lo": round(lo, 5),
                  "kw": kw(r[H["KW"]]), "m": r[H["MILIK"]], "j": r[H["JENIS Charging"]], "y": int(str(r[H["TAHUN OPERASI"]])[:4])})
yr = collections.Counter(u["y"] for u in units)
D["year"] = [{"year": y, "units": n} for y, n in sorted(yr.items())]

# ---------- 2. Transaksi Maret 2026 ----------
wb = openpyxl.load_workbook("Detail Transaksi SPKLU Jawa Barat - Maret 2026 (Tagging).xlsx", read_only=True)
it = wb.worksheets[0].iter_rows(values_only=True); H = {h: i for i, h in enumerate(next(it))}
tj = collections.Counter(); tr = collections.Counter(); hour = collections.Counter(); hk_rest = collections.Counter(); hk_all = collections.Counter()
loc = collections.defaultdict(collections.Counter); kab = collections.defaultdict(collections.Counter)
site = {}
EVX = {"day": collections.defaultdict(collections.Counter), "pow": [], "price": collections.Counter(), "dur": collections.Counter(), "tag": collections.defaultdict(set), "conn": collections.Counter()}
for r in it:
    e = r[H["Energi (kWh)"]]
    if e is None: continue
    e = float(e or 0); rp = float(r[H["Total Bayar (Rp)"]] or 0)
    tj["n"] += 1; tj["kwh"] += e; tj["rp"] += rp
    k = norm(r[H["Kota/Kabupaten"]])
    if not k: continue
    tr["n"] += 1; tr["kwh"] += e; tr["rp"] += rp
    kab[k]["n"] += 1; kab[k]["kwh"] += e; kab[k]["rp"] += rp
    hour[int(r[H["Jam"]] or 0)] += 1; hk_all[int(r[H["Jam"]] or 0)] += e
    if r[H["Jenis Titik Lokasi"]] == "Rest Area Tol": hk_rest[int(r[H["Jam"]] or 0)] += e
    dd = r[H["Tanggal"]]; dkey = dd.strftime("%Y-%m-%d") if hasattr(dd, "strftime") else str(dd)[:10]
    EVX["day"][dkey]["n"] += 1; EVX["day"][dkey]["kwh"] += e
    if r[H["Jenis Titik Lokasi"]] == "Rest Area Tol": EVX["day"][dkey]["rest"] += e
    ikw = kw(r[H["Daya Charger"]]); mins = fnum(r[H["Durasi (menit)"]])
    if ikw and mins > 1 and e > 0.5: EVX["pow"].append((ikw, min(e / (mins / 60), ikw * 1.05)))
    EVX["price"][int(fnum(r[H["Rp per kWh"]]))] += 1
    EVX["dur"][min(int(mins // 15), 8)] += 1
    EVX["tag"][str(r[H["Tagging SPKLU"]]).split(" ")[0]].add(r[H["ID SPKLU"]])
    EVX["conn"]["CHAdeMO" if "CHADEMO" in str(r[H["Connector"]]).upper() else "AC Type 2" if "TYPE 2" in str(r[H["Connector"]]).upper() else "CCS2"] += 1
    loc[r[H["Jenis Titik Lokasi"]]]["n"] += 1; loc[r[H["Jenis Titik Lokasi"]]]["kwh"] += e
    sid = r[H["ID SPKLU"]]
    if sid not in site:
        try: la, lo = round(float(r[H["Latitude"]]), 5), round(float(r[H["Longitude"]]), 5)
        except (TypeError, ValueError): la = lo = None
        site[sid] = {"n": str(r[H["Nama SPKLU"]])[:52], "k": title(k), "la": la, "lo": lo, "t": r[H["Jenis Titik Lokasi"]], "s": 0, "e": 0.0}
    s = site[sid]; s["s"] += 1; s["e"] += e
D["hourly"] = [{"hour": h, "sessions": hour[h]} for h in range(24)]
D["loc"] = [{"type": k, "sessions": v["n"], "mwh": round(v["kwh"] / 1000, 1)} for k, v in sorted(loc.items(), key=lambda x: -x[1]["kwh"])]
D["sites"] = sorted([{**s, "e": round(s["e"], 1)} for s in site.values() if s["la"] is not None], key=lambda s: -s["e"])
nosite = sum(1 for s in site.values() if s["la"] is None)

# ---------- 3. Register charger rumah (hitungan per kab & per kecamatan; tanpa titik) ----------
home_all = 0; home = collections.Counter(); home_pts = []; brand_reb = collections.Counter(); brand_all = collections.Counter()
with open("Data pelanggan EV.txt", encoding="utf-8", errors="ignore") as f:
    hdr = f.readline().rstrip("\n").split("\t"); H = {h: i for i, h in enumerate(hdr)}
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < len(hdr) - 2: continue
        home_all += 1; brand_all[str(p[H["Jenis Kendaraan"]]).strip() or "?"] += 1
        k = norm(p[H["Kabupaten"]]) if H["Kabupaten"] < len(p) else None
        if not k: continue
        home[k] += 1; brand_reb[str(p[H["Jenis Kendaraan"]]).strip() or "?"] += 1
        try: home_pts.append((float(p[H["Long"]]), float(p[H["Lat"]])))
        except Exception: pass

# ---------- 4. Register SPKLU nasional (deret energi) ----------
wb = openpyxl.load_workbook("SPKLU_Indonesia_Lengkap_2026-06-08.xlsx", read_only=True)
nat_units = sum(1 for r in wb.worksheets[0].iter_rows(min_row=2, values_only=True) if r[2])
MON = {"JANUARI": 1, "FEBRUARI": 2, "MARET": 3, "APRIL": 4, "MEI": 5, "JUNI": 6, "JULI": 7, "AGUSTUS": 8, "SEPTEMBER": 9, "OKTOBER": 10, "NOVEMBER": 11, "DESEMBER": 12}
D["nat"] = [{"month": f"{r[0]}-{MON[r[1]]:02d}", "sessions": r[2], "gwh": round(r[3] / 1e6, 3)}
            for r in wb["Konsumsi kWh 2024-2026"].iter_rows(min_row=2, values_only=True)
            if isinstance(r[0], int) and not (r[0] == 2026 and r[1] == "JUNI")]

# ---------- 5. Kab/kota (poligon) + tabel wilayah (publik + PLN) ----------
POP = {"KAB. SUBANG": 1.66, "KAB. CIREBON": 2.45, "KAB. INDRAMAYU": 1.95, "KAB. MAJALENGKA": 1.36, "KAB. SUMEDANG": 1.17, "KAB. KUNINGAN": 1.24, "KOTA CIREBON": 0.36}
INV = {"KAB. SUBANG": 18.2, "KAB. SUMEDANG": 5.63, "KAB. CIREBON": 4.01, "KAB. MAJALENGKA": 3.36, "KAB. INDRAMAYU": 3.35}
PDRB = {"KAB. INDRAMAYU": 59.33, "KOTA CIREBON": 95.18, "KAB. SUMEDANG": 42.65, "KAB. MAJALENGKA": 37.08}
EXP = {"KAB. KUNINGAN": 10707, "KAB. CIREBON": 11769, "KAB. MAJALENGKA": 11094, "KAB. SUMEDANG": 11963, "KAB. INDRAMAYU": 11316, "KAB. SUBANG": 12144, "KOTA CIREBON": 13341}
KPI = {"KAB. SUBANG": 3, "KAB. INDRAMAYU": 6, "KAB. MAJALENGKA": 3, "KAB. CIREBON": 1}
ukw = collections.Counter(); ucnt = collections.Counter()
for u in units: ukw[u["k"]] += u["kw"]; ucnt[u["k"]] += 1
D["regions"] = [{"region": title(k), "population_m": POP[k], "invest_2025_T": INV.get(k), "kpi_zones": KPI.get(k, 0),
                 "spklu_units": ucnt[title(k)], "spklu_kw": round(ukw[title(k)]), "sessions_mar26": kab[k]["n"],
                 "mwh_mar26": round(kab[k]["kwh"] / 1000, 1), "revenue_mar26_M": round(kab[k]["rp"] / 1e6, 1),
                 "home_charger_apps": home[k], "pdrb_capita_2025_jt": PDRB.get(k), "expenditure_capita_2025_k": EXP.get(k)} for k in REB]
CODES = {"32.09": "Kab. Cirebon", "32.08": "Kab. Kuningan", "32.10": "Kab. Majalengka", "32.11": "Kab. Sumedang", "32.12": "Kab. Indramayu", "32.13": "Kab. Subang", "32.74": "Kota Cirebon"}
D["kab"] = [{"region": CODES[f["properties"]["kode_wilayah"]], "geometry": rnd(shape(f["geometry"]), 0.003)}
            for f in json.load(open("data/kabkota_bps.geojson"))["features"] if f["properties"]["kode_wilayah"] in CODES]

# ---------- 6. Jaringan Jamali (OSM–RUPTL) di kotak Rebana ----------
txt = open("data/grid-id/data_jamali.js", encoding="utf-8").read()
dec = json.JSONDecoder(); J = {}
for key in ("substations", "generators", "transmission"):   # berkas JS: kunci tanpa tanda kutip, nilai GeoJSON
    J[key] = dec.raw_decode(txt, txt.index("{", txt.index(key + ":")))[0]
gi_osm = {}
for f in J["substations"]["features"]:
    x, y = f["geometry"]["coordinates"]; p = f["properties"]
    if inb(x, y):
        g = gi_osm.setdefault(p["name"].replace("Gardu Induk ", ""), {"name": p["name"].replace("Gardu Induk ", ""), "lo": round(x, 5), "la": round(y, 5), "v": [], "mva": 0.0})
        g["v"].append(p["voltage"]); g["mva"] += fnum(p["capacity_mva"])
gen = [{"name": f["properties"]["name"], "type": f["properties"]["type"], "mw": fnum(f["properties"]["capacity_mw"]) or None,
        "lo": round(f["geometry"]["coordinates"][0], 5), "la": round(f["geometry"]["coordinates"][1], 5)}
       for f in J["generators"]["features"] if inb(*f["geometry"]["coordinates"]) and f["properties"]["name"]]
seen = set(); gen = [g for g in gen if not (g["name"] in seen or seen.add(g["name"]))]
lines = []
for f in J["transmission"]["features"]:
    c = f["geometry"]["coordinates"]
    if any(inb(*p) for p in c):
        lines.append({"kv": f["properties"]["voltage_class"], "c": [[round(p[0], 4), round(p[1], 4)] for p in c]})

# ---------- 7. Beban trafo GI (April 2022) ----------
CODE2OSM = {"ARJWN": "Arjawinangun", "NARJW": "Arjawinangun Baru", "BBKAN": "Babakan", "CKDNG": "Cikedung", "KUNGN": "Kuningan",
            "MDRCN": "Mandirancan", "SRAGI": "Sunyaragi", "HRGLS": "Haurgeulis", "IDMYU": "Indramayu", "IDMRU": None, "JTBRG": "Jatibarang",
            "CKPAY": "Cikumpay", "PBRAN": "Pabuaran", "SBANG": "Subang", "SKMDI": "Sukamandi", "KDPTN": "Kadipaten", "NKDPT": "New Kadipaten",
            "NUBRG": "New Ujungberung", "PRKAN": "Parakan", "RCKEK": "Rancaekek", "SMDNG": "Sumedang"}
SUBANG_GI = {"SBANG", "SKMDI", "CKPAY", "PBRAN", "HRGLS"}
wb = openpyxl.load_workbook("beban GI.xlsx", read_only=True, data_only=True)
gi = []
for r in list(wb[" TOTAL TRAFO "].iter_rows(values_only=True))[14:]:
    if not r[1] or not r[2]: continue
    up, code = str(r[1]).strip().upper(), str(r[2]).strip().upper()
    if "PT." in code or "INDOCEME" in code: continue
    if up in ("CIREBON", "INDRAMAYU", "SUMEDANG") or (up == "PURWAKARTA" and code in SUBANG_GI):
        pk = max(fnum(r[8]), fnum(r[12])); av = max(fnum(r[10]), fnum(r[14]))
        gi.append({"up3": up, "gi": code, "osm": CODE2OSM.get(code), "trafo": r[3], "mva": fnum(r[4]), "voltage": str(r[5]).replace(" ", ""),
                   "peak_pct": round(pk, 1), "avg_pct": round(av, 1), "area": str(r[16] or "").strip()})
D["gi"] = gi
agg = collections.defaultdict(collections.Counter)
for g in gi:
    key = "PURWAKARTA(Subang GI)" if g["up3"] == "PURWAKARTA" else g["up3"]
    a = agg[key]; a["n"] += 1; a["mva"] += g["mva"]; a["pk"] += g["mva"] * g["peak_pct"] / 100
    if g["peak_pct"] >= 80: a["ge"] += 1; a["mvage"] += g["mva"]
D["giup3"] = [{"up3": k, "trafo": v["n"], "mva": v["mva"], "peak_mva": round(v["pk"]), "peak_pct": round(100 * v["pk"] / v["mva"], 1),
               "trafo_ge80": v["ge"], "mva_ge80": v["mvage"]} for k, v in agg.items()]
gisum = collections.defaultdict(lambda: {"n": 0, "mva": 0.0, "pk": 0.0, "max": 0.0, "codes": set()})
for g in gi:
    if not g["osm"]: continue
    s = gisum[g["osm"]]; s["n"] += 1; s["mva"] += g["mva"]; s["pk"] += g["mva"] * g["peak_pct"] / 100; s["max"] = max(s["max"], g["peak_pct"]); s["codes"].add(g["gi"])
D["grid"] = {"gi": [{**v, "v": sorted(set(v["v"])), "mva": round(v["mva"]),
                     **({"load": {"trafo": gisum[k]["n"], "mva": gisum[k]["mva"], "peak_pct": round(100 * gisum[k]["pk"] / gisum[k]["mva"], 1), "max_pct": gisum[k]["max"]}} if k in gisum else {})}
                    for k, v in gi_osm.items()],
             "gen": gen, "lines": lines}

# ---------- 8. Gardu distribusi: agregat UP3, kecamatan Indramayu, heksagon H3 ----------
wb = openpyxl.load_workbook("Gardu_Beban_Lokasi_JABAR.xlsx", read_only=True)
it = wb["DATA_GARDU"].iter_rows(values_only=True); H = {h: i for i, h in enumerate(next(it))}
up3 = collections.defaultdict(collections.Counter); idm = []
for r in it:
    u = str(r[H["UP3"]] or "")
    if u not in ("UP3 CIREBON", "UP3 INDRAMAYU", "UP3 SUMEDANG"): continue
    a = up3[u[4:]]; a["n"] += 1; a["kva"] += fnum(r[H["KAPASITAS_KVA"]]); cat = str(r[H["KATEGORI_BEBAN"]]); a[cat] += 1
    a["unb:" + str(r[H["STATUS_UNBALANCE"]])] += 1
    pb = r[H["PERSEN_BEBAN"]]
    if pb not in (None, ""): a["pb"] += fnum(pb); a["pbn"] += 1
    if u == "UP3 INDRAMAYU" and r[H["STATUS_KOORDINAT"]] == "VALID" and r[H["LATITUDE"]] and r[H["LONGITUDE"]]:
        idm.append({"lo": float(r[H["LONGITUDE"]]), "la": float(r[H["LATITUDE"]]), "kva": fnum(r[H["KAPASITAS_KVA"]]),
                    "pb": fnum(pb) if pb not in (None, "") else None, "cat": cat, "unb": str(r[H["STATUS_UNBALANCE"]]),
                    "ulp": str(r[H["ULP_KODE"]]), "gin": str(r[H["GARDU_INDUK"]] or "").upper()})
D["gardu"] = [{"up3": k, "gardu": v["n"], "mva": round(v["kva"] / 1000), "measured": v["pbn"], "avg_load_pct": round(v["pb"] / v["pbn"], 1),
               "overload": v["OVERLOAD (>=100%)"], "overload_pct": round(100 * v["OVERLOAD (>=100%)"] / v["pbn"], 1),
               "waspada": v["WASPADA (80-100%)"], "underload": v["UNDERLOAD (<30%)"], "unbalance_p1": v["unb:Prioritas 1"]} for k, v in up3.items()]
# nama ULP = GI pemasok mayoritas per kode ULP (kolom KOTA_KAB tidak andal: kode 53404 tercatat "INDRAMAYU" tetapi dipasok GI Cikedung)
ulpname = {}
for code in set(g["ulp"] for g in idm):
    c = collections.Counter(n for g in idm if g["ulp"] == code for n in ("CIKEDUNG", "HAURGEULIS", "JATIBARANG", "INDRAMAYU") if g["gin"].startswith(n))
    ulpname[code] = c.most_common(1)[0][0].title() if c else code
# kecamatan Indramayu
kecs = [f for f in json.load(open("data/jabar_kecamatan_spklu.geojson"))["features"] if f["properties"]["kab"] == "Indramayu"]
polys = [shape(f["geometry"]) for f in kecs]; tree = STRtree(polys)
def which(x, y):
    p = Point(x, y)
    for i in tree.query(p):
        if polys[i].contains(p): return int(i)
    return None
kagg = [collections.Counter() for _ in kecs]; kulp = [collections.Counter() for _ in kecs]
for g in idm:
    i = which(g["lo"], g["la"])
    if i is None: continue
    a = kagg[i]; a["n"] += 1; a["kva"] += g["kva"]; kulp[i][g["ulp"]] += 1
    if g["pb"] is not None: a["pb"] += g["pb"]; a["pbn"] += 1
    if g["cat"].startswith("OVERLOAD"): a["ol"] += 1
    if g["cat"].startswith("WASPADA"): a["wp"] += 1
    if g["unb"] == "Prioritas 1": a["p1"] += 1
khome = collections.Counter()
for x, y in home_pts:
    i = which(x, y)
    if i is not None: khome[i] += 1
kspk = collections.Counter(); kses = collections.Counter()
for s in D["sites"]:
    i = which(s["lo"], s["la"])
    if i is not None: kses[i] += s["s"]
for u in units:
    i = which(u["lo"], u["la"])
    if i is not None: kspk[i] += 1
PRIORITY = {"Sukra", "Losarang", "Gantar", "Krangkeng"}          # Peta Prioritas Pertumbuhan UP3 Indramayu, Okt 2026
KPIKEC = {"Losarang", "Patrol", "Balongan", "Krangkeng", "Tukdana"}  # nama KPI Rebana yang sama dengan nama kecamatan
kec_out = []
for i, f in enumerate(kecs):
    p = f["properties"]; a = kagg[i]
    u = kulp[i].most_common(1)[0][0] if kulp[i] else None
    kec_out.append({"kec": p["kec"], "pop": p["pop"], "dens": p["dens"], "gardu": a["n"], "mva": round(a["kva"] / 1000, 1),
                    "load": round(a["pb"] / a["pbn"], 1) if a["pbn"] else None, "measured": a["pbn"], "ol": a["ol"], "wp": a["wp"], "p1": a["p1"],
                    "kva_per_1k": round(a["kva"] / p["pop"] * 1000, 1) if p["pop"] else None, "ulp": ulpname.get(u), "spklu": kspk[i],
                    "sessions": kses[i], "home": khome[i], "priority": p["kec"] in PRIORITY, "kpi": p["kec"] in KPIKEC,
                    "geometry": rnd(polys[i], 0.0007)})
D["idm_kec"] = kec_out
# wilayah kerja ULP = gabungan kecamatan menurut ULP mayoritas gardu
byulp = collections.defaultdict(list)
for i, k in enumerate(kec_out):
    if k["ulp"]: byulp[k["ulp"]].append(polys[i])
D["idm_ulp"] = []
for name, ps in byulp.items():
    gs = [g for g in idm if ulpname.get(g["ulp"]) == name]
    meas = [g["pb"] for g in gs if g["pb"] is not None]
    D["idm_ulp"].append({"ulp": name, "gardu": len(gs), "mva": round(sum(g["kva"] for g in gs) / 1000, 1),
                         "load": round(sum(meas) / len(meas), 1) if meas else None,
                         "ol": sum(1 for g in gs if g["cat"].startswith("OVERLOAD")), "kec": sorted(k["kec"] for k in kec_out if k["ulp"] == name),
                         "geometry": rnd(unary_union(ps), 0.0012)})
hexes = collections.defaultdict(collections.Counter)
for g in idm:
    c = h3.latlng_to_cell(g["la"], g["lo"], 7); a = hexes[c]; a["n"] += 1; a["kva"] += g["kva"]
    if g["pb"] is not None: a["pb"] += g["pb"]; a["pbn"] += 1
    if g["cat"].startswith("OVERLOAD"): a["ol"] += 1
D["idm_hex"] = [{"b": [[round(lng, 4), round(lat, 4)] for lat, lng in h3.cell_to_boundary(c)], "n": a["n"], "mva": round(a["kva"] / 1000, 2),
                 "load": round(a["pb"] / a["pbn"], 1) if a["pbn"] else None, "ol": a["ol"]} for c, a in hexes.items() if a["n"] >= 3]
D["idm_meta"] = {"gardu_valid": len(idm), "gardu_total": int(up3["INDRAMAYU"]["n"]), "hex_min": 3}

# ---------- 10. Paket kerja: lapisan analitis se-Rebana ----------
REBKAB = {"Cirebon": "Kab. Cirebon", "Kota Cirebon": "Kota Cirebon", "Indramayu": "Kab. Indramayu", "Subang": "Kab. Subang",
          "Majalengka": "Kab. Majalengka", "Kuningan": "Kab. Kuningan", "Sumedang": "Kab. Sumedang"}
KPI_KEC = {("Indramayu", k) for k in KPIKEC} | {("Majalengka", "Kertajati"), ("Majalengka", "Jatitujuh"), ("Majalengka", "Jatiwangi"), ("Subang", "Pusakanagara")}
LAT0 = -6.6
def xy(lon, lat): return ((lon - 108.0) * 111.32 * math.cos(math.radians(LAT0)), (lat - LAT0) * 110.57)
def km(a, b): return math.dist(xy(*a), xy(*b))
gi_head = []
for g in D["grid"]["gi"]:
    if "load" in g:
        L = g["load"]; hr = 0.8 * L["mva"] - L["mva"] * L["peak_pct"] / 100
        gi_head.append({"name": g["name"], "lo": g["lo"], "la": g["la"], "head": round(hr, 1), "peak": L["peak_pct"], "mva": L["mva"]})
hv = [LineString([xy(*p) for p in l["c"]]) for l in D["grid"]["lines"] if l["kv"] in ("150 kV", "500 kV")]
hvtree = STRtree(hv)
sitepts = [(s["lo"], s["la"]) for s in D["sites"]] + [(u["lo"], u["la"]) for u in units]
idmload = {k["kec"]: k for k in D["idm_kec"]}
RK = []
for f in json.load(open("data/jabar_kecamatan_spklu.geojson"))["features"]:
    p = f["properties"]
    if p["kab"] not in REBKAB: continue
    g = shape(f["geometry"]); c = g.representative_point(); cc = (c.x, c.y)
    gi_ok = [x for x in gi_head if x["head"] >= 20]
    ng = min(gi_ok, key=lambda x: km(cc, (x["lo"], x["la"])))
    pxy = Point(xy(*cc)); dl = min(hv[i].distance(pxy) for i in hvtree.query(pxy.buffer(80))) if len(hvtree.query(pxy.buffer(80))) else 99
    ds = min(km(cc, q) for q in sitepts)
    il = idmload.get(p["kec"]) if p["kab"] == "Indramayu" else None
    RK.append({"code": p["code"], "kec": p["kec"], "kab": REBKAB[p["kab"]], "pop": p["pop"], "dens": p["dens"], "ipm": p["ipm"], "exp": p["exp"], "pov": p["pov"],
               "ch": p["ch"], "kwh": p["kwh"], "trx": p["trx"], "lo": round(c.x, 4), "la": round(c.y, 4),
               "d_gi": round(km(cc, (ng["lo"], ng["la"])), 1), "gi": ng["name"], "gi_head": ng["head"], "d_hv": round(dl, 1), "d_spklu": round(ds, 1),
               "load": il["load"] if il else None, "kpi": (p["kab"], p["kec"]) in KPI_KEC, "priority": bool(il and il["priority"]),
               "area": round(p["pop"] / p["dens"], 1) if p["dens"] else None, "geometry": rnd(g, 0.0015)})
D["rk"] = RK; D["gi_head"] = gi_head
# cakupan SPKLU 10 km + pemilihan rakus 12 lokasi baru (kandidat = titik pusat kecamatan dengan GI ber-ruang ≥20 MVA dalam 20 km)
R = 10.0; totpop = sum(k["pop"] for k in RK)
cov = {k["code"] for k in RK if k["d_spklu"] <= R}
base_share = sum(k["pop"] for k in RK if k["code"] in cov) / totpop
picks = []; covered = set(cov)
for _ in range(12):
    best = None
    for c in RK:
        if c["d_gi"] > 20: continue
        gain = sum(k["pop"] for k in RK if k["code"] not in covered and km((c["lo"], c["la"]), (k["lo"], k["la"])) <= R)
        if best is None or gain > best[1]: best = (c, gain)
    c, gain = best
    if gain <= 0: break
    newc = {k["code"] for k in RK if k["code"] not in covered and km((c["lo"], c["la"]), (k["lo"], k["la"])) <= R}
    covered |= newc
    picks.append({"code": c["code"], "kec": c["kec"], "kab": c["kab"], "lo": c["lo"], "la": c["la"], "gain": gain, "gi": c["gi"], "d_gi": c["d_gi"],
                  "gi_head": c["gi_head"], "share": round(sum(k["pop"] for k in RK if k["code"] in covered) / totpop, 4), "new": sorted(newc)})
D["cover"] = {"radius_km": R, "base_share": round(base_share, 4), "totpop": totpop, "picks": picks,
              "base_codes": sorted(cov), "uncov_poor": round(sum(k["pop"] for k in RK if k["code"] not in cov and k["pov"] >= 11) / totpop, 4)}
# profil rest area per jam (kWh rata-rata per hari, Maret 2026: 31 hari) + profil PV pvlib (clear-sky Ineichen, pantura)
times = pd.date_range("2026-01-01", "2026-12-31 23:00", freq="h", tz="Asia/Jakarta")
loc_ = pvlib.location.Location(-6.45, 108.2, tz="Asia/Jakarta", altitude=10)
ghi = loc_.get_clearsky(times)["ghi"]
shape_h = ghi.groupby(ghi.index.hour).mean(); shape_h = (shape_h / shape_h.sum()).round(5).tolist()
rest_sites = [s for s in D["sites"] if s["t"] == "Rest Area Tol"]
D["pv"] = {"rest_kwh_day": [round(hk_rest[h] / 31, 1) for h in range(24)], "all_kwh_day": [round(hk_all[h] / 31, 1) for h in range(24)],
           "pv_shape": shape_h, "yield_kwh_kwp_yr": 1450, "rest_sites": rest_sites,
           "assume": {"capex_pv_rp_kwp": 10_000_000, "capex_bess_rp_kwh": 6_000_000, "tariff_rp_kwh": 1444.70, "ef_kg_kwh": 0.80, "bess_eff": 0.90}}

# ---------- 11. Ekosistem EV dan ekuitas akses (riset disertasi) ----------
REBK = {"3208": "Kab. Kuningan", "3209": "Kab. Cirebon", "3210": "Kab. Majalengka", "3211": "Kab. Sumedang", "3212": "Kab. Indramayu", "3213": "Kab. Subang", "3274": "Kota Cirebon"}
TT = json.load(open("ttm/ttm.json"))
KEXP = {k["code"]: k.get("expend") for k in TT["kabs"]}
def vill(pref):
    return [{"id": v[0], "acc": v[1], "pop": v[4], "ch": v[5], "area": v[7], "cap": v[8], "rung": v[9]} for v in TT["villages"] if v[0][:4] in pref and v[1] is not None and v[4] > 0]
VR = vill(set(REBK)); VJ = vill({k["code"] for k in TT["kabs"] if k["prov"] == "Jawa Barat"})
def wshare(V, f): P = sum(v["pop"] for v in V); return round(sum(v["pop"] for v in V if f(v)) / P, 4)
def ci(V, h, rank):
    V = sorted(V, key=rank); P = sum(v["pop"] for v in V); mu = sum(v["pop"] * h(v) for v in V) / P
    if mu == 0: return None
    acc = 0.0; cov = 0.0
    for v in V:
        w = v["pop"] / P; r = acc + w / 2; acc += w; cov += w * (h(v) - mu) * (r - 0.5)
    return round(2 * cov / mu, 3)
def lorenz(V, h):
    V = sorted(V, key=lambda v: h(v) / v["pop"]); P = sum(v["pop"] for v in V); Hs = sum(h(v) for v in V)
    pts = [(0.0, 0.0)]; cp = ch = 0.0; g = 0.0
    for v in V:
        p0, c0 = cp, ch; cp += v["pop"] / P; ch += h(v) / Hs; g += (cp - p0) * (ch + c0)
        pts.append((cp, ch))
    step = max(1, len(pts) // 60); out = pts[::step] + [pts[-1]]
    return {"pts": [[round(a, 4), round(b, 4)] for a, b in out], "gini": round(1 - g, 3)}
dens = lambda v: v["pop"] / max(v["area"], 0.05)
def quint(V):
    V = sorted(V, key=dens); P = sum(v["pop"] for v in V); out = [[] for _ in range(5)]; acc = 0
    for v in V:
        q = min(4, int(5 * (acc + v["pop"] / 2) / P)); out[q].append(v); acc += v["pop"]
    res = []
    for i, Q in enumerate(out):
        pq = sum(v["pop"] for v in Q)
        res.append({"q": i + 1, "pop": pq, "r10": wshare(Q, lambda v: v["acc"] <= 10), "r15": wshare(Q, lambda v: v["acc"] <= 15),
                    "r30": wshare(Q, lambda v: v["acc"] <= 30), "per100k": round(100000 * sum(v["ch"] for v in Q) / pq, 2),
                    "dens": round(sorted(dens(v) for v in Q)[len(Q) // 2])})
    return res
def bucket(V):
    E = [(0, 10), (10, 15), (15, 30), (30, 60), (60, 1e9)]
    return [wshare(V, lambda v, a=a, b=b: (a < v["acc"] <= b) or (a == 0 and v["acc"] <= b)) for a, b in E]
def summ(V):
    return {"villages": len(V), "pop": sum(v["pop"] for v in V), "chargers": sum(v["ch"] for v in V), "vil_with": sum(1 for v in V if v["ch"] > 0),
            "r7": wshare(V, lambda v: v["acc"] <= 7), "r10": wshare(V, lambda v: v["acc"] <= 10), "r15": wshare(V, lambda v: v["acc"] <= 15), "r30": wshare(V, lambda v: v["acc"] <= 30),
            "rung": [wshare(V, lambda v, k=k: v["rung"] == k) for k in (0, 1, 2)], "buckets": bucket(V),
            "lor_ch": lorenz(V, lambda v: v["ch"]),
            "ci": {"ch_density": ci(V, lambda v: v["ch"] / v["pop"], dens), "r15_density": ci(V, lambda v: 1.0 if v["acc"] <= 15 else 0.0, dens),
                   "ch_expend": ci(V, lambda v: v["ch"] / v["pop"], lambda v: (KEXP.get(v["id"][:4]) or 0, dens(v))),
                   "r15_expend": ci(V, lambda v: 1.0 if v["acc"] <= 15 else 0.0, lambda v: (KEXP.get(v["id"][:4]) or 0, dens(v)))},
            "quint": quint(V)}
EQ = {"rebana": summ(VR), "jabar": summ(VJ), "kabs": []}
for code, name in REBK.items():
    Vk = [v for v in VR if v["id"][:4] == code]; kk = next(k for k in TT["kabs"] if k["code"] == code)
    EQ["kabs"].append({"code": code, "name": name, "villages": len(Vk), "pop": sum(v["pop"] for v in Vk), "chargers": sum(v["ch"] for v in Vk),
                       "r10": wshare(Vk, lambda v: v["acc"] <= 10), "r15": wshare(Vk, lambda v: v["acc"] <= 15), "r30": wshare(Vk, lambda v: v["acc"] <= 30),
                       "rung": [wshare(Vk, lambda v, k=k: v["rung"] == k) for k in (0, 1, 2)], "buckets": bucket(Vk), "median": kk.get("median"),
                       "per100k": kk.get("per100k"), "expend": kk.get("expend"), "ipm": kk.get("ipm"), "p0": kk.get("p0")})
# agregat desa -> kecamatan (kode BPS 7 digit) untuk peta
kv = collections.defaultdict(list)
for v in VR: kv["id" + v["id"][:7]].append(v)
for k in D["rk"]:
    Vk = kv.get(k["code"])
    if Vk:
        P = sum(v["pop"] for v in Vk)
        k["t_mean"] = round(sum(v["pop"] * v["acc"] for v in Vk) / P, 1); k["t_r15"] = wshare(Vk, lambda v: v["acc"] <= 15)
        k["t_r10"] = wshare(Vk, lambda v: v["acc"] <= 10); k["t_rung2"] = wshare(Vk, lambda v: v["rung"] == 2); k["t_vil"] = len(Vk)
EQ["ttm_meta"] = {"router": "r5r (R5) car travel-time matrix, village to village", "villages_dropped_no_access": sum(1 for v in TT["villages"] if v[0][:4] in REBK and v[1] is None),
                  "kw_per_hh": TT["summary"]["kw_per_hh"], "hh_size": TT["summary"]["hh_size"], "pop_source": "Kontur 2023", "boundary": "HDX-BPS 2020"}
D["eq"] = EQ
# pemakaian: deret harian, tangga daya, harga, durasi, tag utilisasi, konektor
pw = EVX["pow"]; PB = [(0, 11), (11, 30), (30, 60), (60, 100), (100, 400)]
D["evuse"] = {"day": [{"d": k, "n": v["n"], "kwh": round(v["kwh"], 1), "rest": round(v["rest"], 1)} for k, v in sorted(EVX["day"].items())],
              "pow": [{"band": f"{a}–{b if b < 400 else '+'} kW", "n": len([1 for i, d in pw if a < i <= b]),
                       "inst": round(sum(i for i, d in pw if a < i <= b) / max(1, len([1 for i, d in pw if a < i <= b])), 1),
                       "deliv": round(sum(d for i, d in pw if a < i <= b) / max(1, len([1 for i, d in pw if a < i <= b])), 1)} for a, b in PB],
              "pow_all": {"inst": round(sum(i for i, d in pw) / len(pw), 1), "deliv": round(sum(d for i, d in pw) / len(pw), 1)},
              "price": sorted([[k, v] for k, v in EVX["price"].items() if v >= 20], key=lambda x: -x[1])[:5],
              "dur": [EVX["dur"][i] for i in range(9)], "tag": {k: len(v) for k, v in EVX["tag"].items()}, "conn": dict(EVX["conn"])}
# pemilik EV: register charger rumah (merek) + master pelanggan KBLBB per UP3 (hanya hitungan)
wbx = xlrd.open_workbook("DataMasterPelangganKBLBB (2).xls"); shx = wbx.sheets()[0]; hx = {h: i for i, h in enumerate(shx.row_values(0))}
up3c = collections.Counter(str(shx.cell_value(r, hx["UNITAP"])) for r in range(1, shx.nrows))
D["evown"] = {"brand_reb": brand_reb.most_common(8), "brand_all": brand_all.most_common(8), "home_reb": sum(home.values()), "home_all": home_all,
              "kblbb_total": shx.nrows - 1, "kblbb_up3": up3c.most_common(), "kblbb_rebana": sum(up3c.get(c, 0) for c in ("53CRB", "53IDM", "53SMD"))}
# ruang GI per kabupaten (titik GI di dalam poligon kab)
kpoly = [(k["region"], shape(k["geometry"])) for k in D["kab"]]
gk = collections.defaultdict(lambda: {"head": 0.0, "gi": []})
for g in gi_head:
    for name, pg in kpoly:
        if pg.contains(Point(g["lo"], g["la"])): gk[name]["head"] += g["head"]; gk[name]["gi"].append([g["name"], g["head"]])
D["gi_kab"] = [{"region": r["region"], "head": round(gk[r["region"]]["head"], 1), "gi": gk[r["region"]]["gi"], "pop_m": r["population_m"]} for r in D["regions"]]

# ---------- 9. Angka publik dan UP3 Indramayu (paparan internal 15 Okt 2026) ----------
D["zones"] = [{"zone": z, "regency": r, "area_ha": a} for z, r, a in [
    ("Cipali Subang Barat", "Kab. Subang", 10408), ("Losarang", "Kab. Indramayu", 6170), ("Cipali Subang Timur", "Kab. Subang", 4806),
    ("Patrol", "Kab. Indramayu", 4141), ("Cipali Indramayu", "Kab. Indramayu", 2875), ("Balongan", "Kab. Indramayu", 2122),
    ("Kertajati (Jatitujuh)", "Kab. Majalengka", 1415), ("Patimban", "Kab. Subang", 542), ("Tukdana", "Kab. Indramayu", None),
    ("Krangkeng", "Kab. Indramayu", None), ("Jatiwangi", "Kab. Majalengka", None), ("Butom", "Kab. Majalengka / Indramayu border", None), ("Cirebon", "Kab. Cirebon", None)]]
D["invest"] = [{"period": "2024", "value_T": 23.26, "note": "derived: 36.67 / 1.5767"}, {"period": "2025", "value_T": 36.67, "note": "BKPM via BP Rebana"},
               {"period": "2026 H1", "value_T": 21.59, "note": "to Q2 2026, ~30% of West Java"}]
D["power"] = [{"plant": "PLTU Cirebon-1", "regency": "Kab. Cirebon", "mw": 660, "type": "Coal", "note": "Early retirement (2035) cancelled Dec 2025"},
              {"plant": "PLTU Cirebon-2", "regency": "Kab. Cirebon", "mw": 1000, "type": "Coal", "note": "Operating since May 2023"},
              {"plant": "PLTU Indramayu", "regency": "Kab. Indramayu", "mw": 990, "type": "Coal", "note": "3x330 MW, Sukra, since 2011"},
              {"plant": "PLTA Jatigede", "regency": "Kab. Sumedang", "mw": 110, "type": "Hydro", "note": "Operating"},
              {"plant": "PLTS Terapung Jatigede (plan)", "regency": "Kab. Sumedang", "mw": 100, "type": "Solar (planned)", "note": "PLN–Masdar MoU 2025"},
              {"plant": "PLTS Gantar Indramayu (plan)", "regency": "Kab. Indramayu", "mw": 100, "type": "Solar (planned)", "note": "Announced 2024"}]
D["sales"] = {
    "source": "PLN UP3 Indramayu, Sharing Session Best Practice Penjualan Tenaga Listrik 'Powering Growth', 15 Oct 2026 (UP3 se-UID Jawa Barat)",
    "cum": {"2024": [109.37, 210.91, 322.99, 435.84, 554.97, 667.31, 779.67, 892.60, 1005.72],
            "2025": [None, None, None, None, None, None, None, None, 1087.39],
            "2026": [123.41, 236.74, 367.51, 498.23, 636.53, 773.86, 911.26, 1050.07, 1187.73]},
    "kpi_sep26": {"target": 60.15, "real": 80.49, "pct": 110},
    "customers": [601815, 618473, 641906], "mva": [650.80, 706.63, 771.68], "revenue_bn": [929.24, 947.61, 1142.18],
    "tm": [151.39, 177.94, 249.73],
    "tariff": [{"t": "Total TM", "d": 71.80, "p": 40.35}, {"t": "I3", "d": 62.07, "p": 55.01}, {"t": "S3", "d": 1.08, "p": 9.69},
               {"t": "L", "d": -14.00, "p": -39.11}, {"t": "P3", "d": 1.07, "p": 13.85}],
    "cluster": [["Plastics", 59.85, 111.62], ["Ceramics", 24.83, 26.09], ["Oil & gas", 20.42, 19.96], ["Mall & dept. store", 7.31, 8.25],
                ["Hospitals", 6.54, 7.45], ["Footwear", 1.17, 5.17], ["Rice mills", 3.41, 3.93], ["Schools", 3.85, 3.54],
                ["Textiles", 2.36, 1.97], ["Offices", 1.56, 1.82], ["Hotels", 0.91, 0.92], ["Other", 49.05, 46.60]],
    "cluster_total": [228.06, 282.69],
    "programs": [{"n": "Growth Radar", "f": "Niaga & Pemasaran", "m": "New customers", "real": 14911, "target": 13290, "pct": 112.20, "u": "customers"},
                 {"n": "Grid to Grow", "f": "Jaringan, Perencanaan & Konstruksi", "m": "Distribution equipment failures (PHB TM, trafo)", "real": 18, "target": 20, "pct": 110, "u": "units"},
                 {"n": "First 90 Days Energy Success", "f": "Transaksi Energi, K3L, Pengadaan & Keuangan", "m": "P2TL findings", "real": 13959017, "target": 11761354.5, "pct": 118.69, "u": "kWh"}],
    "pipeline": [{"n": "New industrial connections", "e": 15, "v": 231.095, "u": "MVA"}, {"n": "Industrial upgrades", "e": 8, "v": 73.379, "u": "MVA"},
                 {"n": "LV upgrades", "e": 23, "v": 712.55, "u": "kVA"}, {"n": "Housing (± units)", "e": 1112, "v": 1.297, "u": "MVA"}],
}
D["skills"] = {
    "jobs_target_2030": 1_780_000, "losarang_jobs": 272_429, "kertajati_jobs": 57_457, "byd_jobs": 20_000, "jobs_per_ha": 200,
    "smk_unemp_jabar_may26": 10.64, "tpt_jabar_may26": 6.61,
    "polindra": [["Rekayasa Perangkat Lunak (D4)", 477], ["Perancangan Manufaktur (D4)", 418], ["Teknik Informatika (D3)", 411], ["Keperawatan (D3)", 330], ["Sistem Informasi Kota Cerdas (D4)", 319]],
    "electra": {"occupations": 380, "pathways": 16, "modules": 1117, "class_hours": 32},
    "up3_new_customers_2026": 14911, "up3_mva_growth": 65.04,
    "nodes": [["Lohbener", "Indramayu", "Politeknik Negeri Indramayu (Polindra)"], ["Arjawinangun", "Cirebon", "ITB Kampus Cirebon"],
              ["Jatinangor", "Sumedang", "Unpad, ITB Jatinangor, IPDN"], ["Indramayu", "Indramayu", "Electra Skill Academy class (Indramayu)"],
              ["Kesambi", "Kota Cirebon", "Electra Skill Academy class (Cirebon)"], ["Kertajati", "Majalengka", "Kertajati Aerocity training hub (proposed)"]]}
T = D["totals"] = {"jabar_units": len(jabar), "reb_units": len(units), "reb_kw": sum(u["kw"] for u in units), "jabar_trx": dict(tj), "reb_trx": dict(tr),
                   "reb_sites": len(site), "reb_sites_nocoord": nosite, "home_jabar": home_all, "home_reb": sum(home.values()), "nat_units": nat_units}

json.dump(D, open(OUT_JSON, "w"), separators=(",", ":"), ensure_ascii=False)
src = open(SRC, encoding="utf-8").read(); assert src.count("/*__DATA__*/") == 1
open(DST, "w", encoding="utf-8").write(src.replace("/*__DATA__*/", json.dumps(D, separators=(",", ":"), ensure_ascii=False)))
print("data %.0f KB · page %.0f KB · SPKLU %d · sites %d · kec %d · ULP %s · hex %d · GI %d · lines %d"
      % (os.path.getsize(OUT_JSON) / 1024, os.path.getsize(DST) / 1024, len(units), len(site), len(kec_out),
         {u["ulp"]: u["gardu"] for u in D["idm_ulp"]}, len(D["idm_hex"]), len(D["grid"]["gi"]), len(lines)))
