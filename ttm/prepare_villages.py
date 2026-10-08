"""Siapkan lapisan desa/kelurahan area studi TTM (Jabar + Jakarta + Banten-daratan) dan
tandai desa yang memuat SPKLU dari master nasional.

Area studi mengikuti skrip r5r supervisor (java_ttm_01.R): provinsi Jakarta Raya, Jawa Barat,
Banten; kab/kota Cilegon, Kota Serang, Lebak, Pandeglang, Serang, Kepulauan Seribu dibuang.

Masukan
  --villages DIR   klon JfrAziz/indonesia-district (HDX-BPS 2020, kode desa BPS 10 digit)
  master SPKLU     SPKLU_Indonesia_Lengkap_2026-06-08.xlsx (3.212 lokasi, lat/lon)

Keluaran (ttm/input/)
  villages.csv     id, nama desa/kec/kab/prov, lon/lat titik di dalam poligon, luas km2
  spklu_village.csv  SPKLU per desa (jumlah lokasi, charger, kW, status, kategori PLN/nonPLN)
  spklu_sites.csv    daftar lokasi SPKLU di area studi dengan koordinat dan kode desa
  villages_simplified.geojson  poligon disederhanakan (toleransi ~60 m) untuk peta dashboard

Jalankan dari akar repo:
  python3 ttm/prepare_villages.py --villages /home/user/jfraziz/indonesia-district
"""
import argparse, csv, glob, json, os, re, sys
import openpyxl
from shapely.geometry import shape, Point, mapping
from shapely.strtree import STRtree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ttm", "input")
os.makedirs(OUT, exist_ok=True)

PROV = {"id31": "DKI Jakarta", "id32": "Jawa Barat", "id36": "Banten"}
# kab/kota yang dibuang (kode BPS 4 digit): Kep. Seribu, Pandeglang, Lebak, Serang, Cilegon, Kota Serang
KAB_DROP = {"3101", "3601", "3602", "3604", "3672", "3673"}

ap = argparse.ArgumentParser()
ap.add_argument("--villages", required=True)
ap.add_argument("--master", default=os.path.join(ROOT, "SPKLU_Indonesia_Lengkap_2026-06-08.xlsx"))
a = ap.parse_args()

# ------------------------------------------------------------------ desa
villages, geoms = [], []
for pcode, pname in PROV.items():
    pdir = glob.glob(os.path.join(a.villages, pcode + "_*"))
    assert len(pdir) == 1, pcode
    # hanya berkas kecamatan (id + 7 digit); berkas kab/kota (id + 4 digit) mengulang desa yang sama
    files = [f for f in glob.glob(os.path.join(pdir[0], "id*", "id*.geojson"))
             if re.match(r"id\d{7}_", os.path.basename(f))]
    for f in sorted(files):
        for ft in json.load(open(f))["features"]:
            p = ft["properties"]
            vid = p["village_code"][2:]            # 'id3202220008' -> '3202220008'
            if vid[:4] in KAB_DROP:
                continue
            g = shape(ft["geometry"])
            if not g.is_valid:
                g = g.buffer(0)
            rp = g.representative_point()
            villages.append(dict(id=vid, village=p["village"], district=p["district"],
                                 regency=p["regency"], regency_code=vid[:4], province=pname,
                                 lon=round(rp.x, 6), lat=round(rp.y, 6),
                                 area_km2=round(g.area * 111.32 * 111.32 * 0.9934, 4)))
            geoms.append(g)
ids = [v["id"] for v in villages]
assert len(ids) == len(set(ids)), "kode desa ganda"
print("desa area studi:", len(villages))

# ------------------------------------------------------------------ SPKLU -> desa
wb = openpyxl.load_workbook(a.master, read_only=True)
rows = list(wb["Master SPKLU Indonesia"].iter_rows(values_only=True))
hdr = rows[0]; ix = {h: i for i, h in enumerate(hdr)}
tree = STRtree(geoms)

def kw(s):
    m = re.search(r"[\d,.]+", str(s or ""))
    return float(m.group(0).replace(",", ".")) if m else 0.0

per = {}
sites = []
n_in, n_total = 0, 0
for r in rows[1:]:
    try:
        lat, lon = float(r[ix["Latitude"]]), float(r[ix["Longitude"]])
    except (TypeError, ValueError):
        continue
    n_total += 1
    pt = Point(lon, lat)
    hits = [i for i in tree.query(pt) if geoms[i].covers(pt)]
    if not hits:
        continue
    n_in += 1
    v = villages[hits[0]]
    sites.append(dict(spklu_id=r[ix["ID SPKLU"]], name=r[ix["Nama SPKLU"]], lon=lon, lat=lat, village_id=v["id"],
                      regency_code=v["regency_code"], kw=kw(r[ix["Kapasitas (kW)"]]),
                      chargers=int(r[ix["Jumlah Charger"]] or 0), kategori=r[ix["Kategori"]], status=r[ix["Status"]]))
    d = per.setdefault(v["id"], dict(id=v["id"], sites=0, chargers=0, connectors=0, kw=0.0,
                                     pln=0, nonpln=0, available=0, offline=0, maxkw=0.0))
    d["sites"] += 1
    d["chargers"] += int(r[ix["Jumlah Charger"]] or 0)
    d["connectors"] += int(r[ix["Jumlah Connector"]] or 0)
    k = kw(r[ix["Kapasitas (kW)"]])
    d["kw"] += k * max(1, int(r[ix["Jumlah Charger"]] or 1))
    d["maxkw"] = max(d["maxkw"], k)
    d["pln" if str(r[ix["Kategori"]]).upper() == "PLN" else "nonpln"] += 1
    st = str(r[ix["Status"]]).lower()
    d["offline" if st in ("offline mode", "unavailable", "maintenance") else "available"] += 1
print("SPKLU nasional dengan koordinat: %d; di area studi: %d; desa ber-SPKLU: %d" % (n_total, n_in, len(per)))

# ------------------------------------------------------------------ tulis
with open(os.path.join(OUT, "villages.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(villages[0].keys())); w.writeheader(); w.writerows(villages)
with open(os.path.join(OUT, "spklu_village.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(next(iter(per.values())).keys())); w.writeheader()
    w.writerows(sorted(per.values(), key=lambda d: d["id"]))
with open(os.path.join(OUT, "spklu_sites.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(sites[0].keys())); w.writeheader(); w.writerows(sites)

feats = []
for v, g in zip(villages, geoms):
    gs = g.simplify(0.0006, preserve_topology=True)
    feats.append(dict(type="Feature", properties=dict(id=v["id"], n=v["village"], k=v["regency_code"]),
                      geometry=json.loads(json.dumps(mapping(gs)))))
# bulatkan koordinat ke 4 desimal (~11 m) agar berkas kecil
def rnd(o):
    if isinstance(o, list): return [rnd(x) for x in o]
    if isinstance(o, float): return round(o, 4)
    return o
for ft in feats: ft["geometry"]["coordinates"] = rnd(ft["geometry"]["coordinates"])
json.dump(dict(type="FeatureCollection", features=feats), open(os.path.join(OUT, "villages_simplified.geojson"), "w"), separators=(",", ":"))
print("ditulis ke", OUT, "| geojson %.1f MB" % (os.path.getsize(os.path.join(OUT, "villages_simplified.geojson")) / 1e6))
