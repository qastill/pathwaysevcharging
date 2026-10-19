"""Crosswalk id desa GADM 4.1 (CC_4, dipakai r5r supervisor) -> kode desa BPS 2020 (ttm/input/villages.csv).

GADM 4.1 masih memakai kode lama untuk desa yang berganti kode setelah pemekaran (Pangandaran 3218 masih 3207 = Ciamis,
beberapa desa Kuningan, Sumedang, Indramayu, Bandung Barat). Dua langkah:
  1. kode: 3207xxxxxx -> 3218xxxxxx bila kode tujuan ada di villages.csv dan belum punya baris TTM sendiri;
  2. posisi: untuk id sisa, posisi diperkirakan dari desa-desa dikenal yang tercapai <= 15 menit (rata-rata koordinat
     tertimbang 1/(t+1)); (a) kecamatan berkode baru dengan nomor urut desa sama, maks 6 km; (b) desa terdekat yang
     belum punya baris TTM, maks 2,5 km. Sisanya dibiarkan tak terpetakan dan dilaporkan.
Keluaran: ttm/input/id_crosswalk.csv (gadm_id,bps_id,method,dist_km)
"""
import csv, gzip, math, os
INP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input")
V = {r["id"]: r for r in csv.DictReader(open(os.path.join(INP, "villages.csv")))}
for v in V.values(): v["lon"], v["lat"] = float(v["lon"]), float(v["lat"])
path = next(p for p in ("west_java_ttm_car.csv.gz", "west_java_ttm_car.csv") if os.path.exists(os.path.join(INP, p)))
seen, unk, near = set(), set(), {}
with (gzip.open if path.endswith(".gz") else open)(os.path.join(INP, path), "rt") as f:
    for r in csv.DictReader(f):
        fi = r["from_id"]
        if fi in V: seen.add(fi); continue
        unk.add(fi); t = r["travel_time_p50"]
        if t not in ("", "NA") and float(t) <= 15: near.setdefault(fi, []).append((float(t), r["to_id"]))
unseen = set(V) - seen
cw = {}
for u in sorted(unk):
    if u.startswith("3207"):
        g = "3218" + u[4:]
        if g in unseen and g not in cw.values(): cw[u] = (g, "code", 0.0)
def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[1], a[0], b[1], b[0]))
    return 6371 * 2 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
pos = {k: (v["lon"], v["lat"]) for k, v in V.items() if k in seen}
pos.update({u: (V[g]["lon"], V[g]["lat"]) for u, (g, _, _) in cw.items()})
for u in sorted(unk):
    if u in cw: continue
    pts = [(1 / (t + 1), pos[to]) for t, to in near.get(u, []) if to in pos]
    if not pts: cw[u] = ("", "no-neighbour", None); continue
    W = sum(w for w, _ in pts); lon = sum(w * p[0] for w, p in pts) / W; lat = sum(w * p[1] for w, p in pts) / W
    taken = {g for g, _, _ in cw.values()}
    # 2a. kecamatan diberi kode baru (070 -> 071, 100 -> 101): kab sama (3207 -> 3218), nomor urut desa sama, <= 6 km dari posisi
    kabs = {u[:4], "3218"} if u.startswith("3207") else {u[:4]}
    shift = [(hav((lon, lat), (V[k]["lon"], V[k]["lat"])), k) for k in unseen if k not in taken and k[:4] in kabs and k[7:] == u[7:] and k[4:7] != u[4:7]]
    if shift and min(shift)[0] <= 6: d, k = min(shift); cw[u] = (k, "code-shift", round(d, 2)); continue
    # 2b. desa terdekat yang belum punya baris, maks 2.5 km
    cand = [(hav((lon, lat), (V[k]["lon"], V[k]["lat"])), k) for k in unseen if k not in taken]
    d, k = min(cand)
    cw[u] = (k, "position", round(d, 2)) if d <= 2.5 else ("", "too-far(%.1f km)" % d, None)
with open(os.path.join(INP, "id_crosswalk.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["gadm_id", "bps_id", "method", "dist_km"])
    for u, (g, m, d) in sorted(cw.items()): w.writerow([u, g, m, "" if d is None else d])
ok = {u: x for u, x in cw.items() if x[0]}
print("id GADM tak dikenal %d -> terpetakan %d (kode %d, kode-geser %d, posisi %d); gagal %d" % (len(unk), len(ok), sum(1 for x in ok.values() if x[1] == "code"),
      sum(1 for x in ok.values() if x[1] == "code-shift"), sum(1 for x in ok.values() if x[1] == "position"), len(cw) - len(ok)))
for u, x in cw.items():
    if x[1] != "code": print(" ", u, x, V[x[0]]["village"] + "/" + V[x[0]]["district"] if x[0] else "")
print("desa BPS tanpa baris TTM setelah crosswalk:", len(unseen - {g for g, _, _ in cw.values()}))
