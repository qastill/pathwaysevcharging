"""Unduh dua lapisan terbuka yang TIDAK ada di repositori, lalu padatkan menjadi input kecil
yang di-commit, supaya `prepare.py` bisa berjalan tanpa jaringan.

    python3 equitymap/fetch.py          # unduh (bila belum ada di cache/) + tulis input/

Sumber:
  1. Kontur Population (Indonesia, rilis 2023-11-01) — populasi per heksagon H3 resolusi 8
     (~0,74 km²), turunan dari GHSL/Microsoft Buildings/Meta HRSL, lisensi CC BY 4.0.
     https://data.humdata.org/dataset/kontur-population-indonesia
  2. geoBoundaries gbOpen IDN ADM1/ADM2 (versi *simplified*) — batas provinsi dan
     kabupaten/kota, lisensi CC BY 4.0. https://www.geoboundaries.org/

Keluaran (di-commit, dipakai prepare.py):
  input/hex_r6.csv     — h3 (res 6, ~36 km²), pop (jiwa), kab (indeks ke kabupaten.csv)
  input/kabupaten.csv  — indeks, nama kabupaten/kota, provinsi (nama BPS Indonesia), shapeID

Berkas mentah di cache/ tidak di-commit (172 MB).
"""
import csv, gzip, json, os, shutil, sqlite3, sys, urllib.request

import h3
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
INP = os.path.join(HERE, "input")
os.makedirs(CACHE, exist_ok=True)
os.makedirs(INP, exist_ok=True)

SRC = {
    "kontur_id.gpkg.gz": "https://geodata-eu-central-1-kontur-public.s3.amazonaws.com/kontur_datasets/"
                         "kontur_population_ID_20231101.gpkg.gz",
    "adm1.geojson": "https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/main/releaseData/"
                    "gbOpen/IDN/ADM1/geoBoundaries-IDN-ADM1_simplified.geojson",
    "adm2.geojson": "https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/main/releaseData/"
                    "gbOpen/IDN/ADM2/geoBoundaries-IDN-ADM2_simplified.geojson",
}

# nama provinsi geoBoundaries (Inggris) -> nama yang dipakai dashboard (D.national / POP / ECON)
PROV_ID = {
    "Aceh": "Aceh", "North Sumatra": "Sumatera Utara", "West Sumatra": "Sumatera Barat", "Riau": "Riau",
    "Riau Islands": "Kepulauan Riau", "Jambi": "Jambi", "South Sumatra": "Sumatera Selatan",
    "Bangka-Belitung Islands": "Bangka Belitung", "Bengkulu": "Bengkulu", "Lampung": "Lampung",
    "Banten": "Banten", "Jakarta Special Capital Region": "DKI Jakarta", "West Java": "Jawa Barat",
    "Central Java": "Jawa Tengah", "Special Region of Yogyakarta": "DI Yogyakarta", "East Java": "Jawa Timur",
    "Bali": "Bali", "West Nusa Tenggara": "Nusa Tenggara Barat", "East Nusa Tenggara": "Nusa Tenggara Timur",
    "West Kalimantan": "Kalimantan Barat", "Central Kalimantan": "Kalimantan Tengah",
    "South Kalimantan": "Kalimantan Selatan", "East Kalimantan": "Kalimantan Timur",
    "North Kalimantan": "Kalimantan Utara", "North Sulawesi": "Sulawesi Utara", "Gorontalo": "Gorontalo",
    "Central Sulawesi": "Sulawesi Tengah", "West Sulawesi": "Sulawesi Barat", "South Sulawesi": "Sulawesi Selatan",
    "Southeast Sulawesi": "Sulawesi Tenggara", "Maluku": "Maluku", "North Maluku": "Maluku Utara",
    "West Papua": "Papua Barat", "Papua": "Papua",
}
RES = 6


def fetch(name):
    p = os.path.join(CACHE, name)
    if os.path.exists(p) and os.path.getsize(p) > 1000:
        return p
    print("unduh", SRC[name])
    with urllib.request.urlopen(SRC[name], timeout=600) as r, open(p + ".part", "wb") as f:
        shutil.copyfileobj(r, f)
    os.replace(p + ".part", p)
    return p


def main():
    gz = fetch("kontur_id.gpkg.gz")
    gpkg = gz[:-3]
    if not os.path.exists(gpkg):
        with gzip.open(gz, "rb") as f, open(gpkg, "wb") as o:
            shutil.copyfileobj(f, o)
    adm1 = json.load(open(fetch("adm1.geojson"), encoding="utf-8"))
    adm2 = json.load(open(fetch("adm2.geojson"), encoding="utf-8"))

    # ---- 1) populasi res 8 -> res 6
    con = sqlite3.connect(gpkg)
    pop = {}
    for hx, p in con.execute("select h3, population from population"):
        k = h3.cell_to_parent(hx, RES)
        pop[k] = pop.get(k, 0.0) + p
    print(f"heksagon res {RES}: {len(pop):,}  populasi: {sum(pop.values()):,.0f}")

    # ---- 2) provinsi tiap kabupaten (titik wakil kabupaten di dalam poligon provinsi)
    provs = [(PROV_ID[f["properties"]["shapeName"]], shape(f["geometry"])) for f in adm1["features"]]
    ptree = STRtree([g for _, g in provs])
    # geoBoundaries ADM2 memuat empat badan air sebagai "kabupaten": Waduk Cirata, Wadung Kedungombo, Danau, Danau Toba.
    # Dibuang; heksagon di dalamnya dilekatkan ke kabupaten terdekat.
    WATER = {"Waduk Cirata", "Wadung Kedungombo", "Danau", "Danau Toba"}
    kabs = []
    for f in adm2["features"]:
        if f["properties"]["shapeName"] in WATER:
            continue
        g = shape(f["geometry"])
        rp = g.representative_point()
        hit = [i for i in ptree.query(rp) if provs[i][1].contains(rp)]
        if not hit:  # pulau kecil di luar poligon provinsi yang disederhanakan: ambil yang terdekat
            hit = [min(range(len(provs)), key=lambda i: provs[i][1].distance(rp))]
        kabs.append(dict(name=f["properties"]["shapeName"], prov=provs[hit[0]][0],
                         sid=f["properties"]["shapeID"], geom=g))
    kabs.sort(key=lambda k: (k["prov"], k["name"]))
    ktree = STRtree([k["geom"] for k in kabs])

    # ---- 3) kabupaten tiap heksagon (pusat heksagon; heksagon pesisir tanpa hit -> kabupaten terdekat)
    rows, miss = [], 0
    for hx, p in pop.items():
        lat, lng = h3.cell_to_latlng(hx)
        pt = Point(lng, lat)
        hit = [i for i in ktree.query(pt) if kabs[i]["geom"].contains(pt)]
        if not hit:
            miss += 1
            cand = ktree.query(pt.buffer(0.5))
            hit = [min(cand, key=lambda i: kabs[i]["geom"].distance(pt))] if len(cand) else \
                  [min(range(len(kabs)), key=lambda i: kabs[i]["geom"].distance(pt))]
        rows.append((hx, round(p, 1), hit[0]))
    print(f"heksagon di luar poligon kabupaten (dilekatkan ke terdekat): {miss:,}")

    with open(os.path.join(INP, "kabupaten.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["idx", "name", "prov", "shapeID"])
        for i, k in enumerate(kabs):
            w.writerow([i, k["name"], k["prov"], k["sid"]])
    with open(os.path.join(INP, "hex_r6.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["h3", "pop", "kab"])
        w.writerows(sorted(rows))
    print("ditulis:", os.path.join(INP, "hex_r6.csv"), os.path.join(INP, "kabupaten.csv"))


if __name__ == "__main__":
    main()
