"""Siapkan data terbuka (solar, tutupan lahan, lahan terbangun, penduduk, banjir, angin) untuk West Java/Rebana.

Sumber mentah diunduh terpisah (lihat README.md di folder ini); skrip ini memotong & meringkasnya ke satu grid
0,0025 derajat (~278 m) seluas site West Java dan menulis GeoTIFF kecil di data/open/*.tif yang dipakai urscape/build.py.

    python3 data/open/prep.py <folder_mentah>
"""
import glob, json, os, sys
import numpy as np, rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling
from rasterio.windows import from_bounds

RAW = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
W, N, RES = 106.30, -5.85, 0.0025; CX, CY = 1060, 800; E, S = W + CX * RES, N - CY * RES
TR = from_origin(W, N, RES, RES)

def save(name, arr, nodata=-9999.0, dtype="float32", tags=None):
    arr = np.where(np.isfinite(arr), arr, nodata).astype(dtype)
    with rasterio.open(f"{HERE}/{name}.tif", "w", driver="GTiff", height=CY, width=CX, count=1, dtype=dtype, crs="EPSG:4326",
                       transform=TR, nodata=nodata, compress="deflate", predictor=2) as d:
        d.write(arr, 1); d.update_tags(**(tags or {}))
    print(f"  {name}: {np.isfinite(np.where(arr == nodata, np.nan, arr)).sum()} cells, {os.path.getsize(f'{HERE}/{name}.tif') // 1024} KB")

def warp(src_arr, src_tr, src_crs, resampling, nodata=np.nan):
    dst = np.full((CY, CX), nodata, "float32")
    reproject(src_arr.astype("float32"), dst, src_transform=src_tr, src_crs=src_crs, dst_transform=TR, dst_crs="EPSG:4326",
              resampling=resampling, src_nodata=nodata, dst_nodata=nodata)
    return dst

def read_window(path, pad=0.01):
    with rasterio.open(path) as s:
        win = from_bounds(max(W - pad, s.bounds.left), max(S - pad, s.bounds.bottom), min(E + pad, s.bounds.right), min(N + pad, s.bounds.top), s.transform)
        win = win.round_offsets().round_lengths()
        return s.read(1, window=win), s.window_transform(win), s.crs, s.nodata

# 1. Global Solar Atlas (Solargis) point samples 0.025 deg -> raster 0.025 -> bilinear 0.0025
print("solar")
rows = [json.loads(l) for l in open(f"{RAW}/solar_grid.jsonl") if l.strip()]
rows = [r for r in rows if "err" not in r]
lats = sorted({r["lat"] for r in rows}, reverse=True); lons = sorted({r["lon"] for r in rows})
step = 0.025; tr_s = from_origin(min(lons) - step / 2, max(lats) + step / 2, step, step)
def solar_raster(key, fn=lambda r, k: r[k]):
    a = np.full((len(lats), len(lons)), np.nan, "float32"); li = {v: i for i, v in enumerate(lats)}; lo = {v: i for i, v in enumerate(lons)}
    for r in rows:
        v = fn(r, key)
        if v is not None: a[li[r["lat"]], lo[r["lon"]]] = v
    return a
for key, name in [("PVOUT_csi", "solar_pvout"), ("GHI", "solar_ghi"), ("DNI", "solar_dni"), ("DIF", "solar_dif"), ("TEMP", "air_temp"), ("ELE", "elevation")]:
    save(name, warp(solar_raster(key), tr_s, "EPSG:4326", Resampling.bilinear), tags=dict(source="Global Solar Atlas 2.0 / Solargis (point API, 0.025 deg samples)"))
# musim: rasio PVOUT bulan terendah / tertinggi, dan bulan terendah
mon = solar_raster("PVOUT_m", lambda r, k: (min(r[k]) / max(r[k])) if r.get(k) else None)
save("solar_season_ratio", warp(mon, tr_s, "EPSG:4326", Resampling.bilinear), tags=dict(source="Global Solar Atlas monthly PVOUT: lowest month / highest month"))
pv_m = np.stack([solar_raster("PVOUT_m", lambda r, k, i=i: r[k][i] if r.get(k) else None) for i in range(12)])
save("solar_pvout_min_month", warp(np.nanmin(pv_m, 0), tr_s, "EPSG:4326", Resampling.bilinear), tags=dict(source="GSA monthly PVOUT, lowest month (kWh/kWp/day x days)"))

# 2. ESA WorldCover 2021 (10 m) -> fraksi per kelas pada blok 30x30 px (0.0025 deg)
print("worldcover")
classes = {10: "tree", 20: "shrub", 30: "grass", 40: "crop", 50: "built", 60: "bare", 80: "water", 90: "wetland", 95: "mangrove"}
frac = {c: np.full((CY, CX), np.nan, "float32") for c in classes}
for f in sorted(glob.glob(f"{RAW}/worldcover_*.tif")):
    with rasterio.open(f) as s:
        left, bottom, right, top = max(W, s.bounds.left), max(S, s.bounds.bottom), min(E, s.bounds.right), min(N, s.bounds.top)
        if left >= right or bottom >= top: continue
        # snap to the 0.0025 grid
        c0 = int(round((left - W) / RES)); c1 = int(round((right - W) / RES)); r0 = int(round((N - top) / RES)); r1 = int(round((N - bottom) / RES))
        win = from_bounds(W + c0 * RES, N - r1 * RES, W + c1 * RES, N - r0 * RES, s.transform).round_offsets().round_lengths()
        a = s.read(1, window=win)
        nb_r, nb_c = (r1 - r0), (c1 - c0); k = 30
        a = a[: nb_r * k, : nb_c * k].reshape(nb_r, k, nb_c, k)
        valid = (a != 0).sum(axis=(1, 3)).astype("float32")
        for c in classes:
            cnt = (a == c).sum(axis=(1, 3)).astype("float32")
            blk = np.where(valid > 0, 100 * cnt / np.maximum(valid, 1), np.nan)
            cur = frac[c][r0:r1, c0:c1]; frac[c][r0:r1, c0:c1] = np.where(np.isnan(cur), blk, cur)
        print("  tile", os.path.basename(f), a.shape)
for c, nm in classes.items():
    if nm in ("tree", "crop", "built", "water", "grass", "bare", "mangrove", "wetland"): save(f"lc_{nm}_pct", frac[c], tags=dict(source="ESA WorldCover 2021 v200 (10 m), share of 0.0025-deg cell"))
dom = np.full((CY, CX), np.nan, "float32"); st = np.stack([frac[c] for c in classes]); ok = np.isfinite(st).all(0)
dom[ok] = np.array(list(classes))[np.argmax(st[:, ok], 0)]; save("lc_dominant", dom, tags=dict(source="ESA WorldCover 2021 dominant class code per cell", codes=json.dumps(classes)))

# 3. GHSL built-up surface (m2 per 3-arcsec cell) 1975/2000/2020 -> % terbangun; population 2000/2025/2030 -> jiwa per sel
print("ghsl")
for yr in ("1975", "2000", "2020"):
    fs = glob.glob(f"{RAW}/**/GHS_BUILT_S_E{yr}_*.tif", recursive=True)
    if not fs: print("  (no built", yr, ")"); continue
    a, tr, crs, nd = read_window(fs[0]); cell_m2 = (tr.a * 111320 * np.cos(np.deg2rad(-6.8))) * (abs(tr.e) * 111320)
    save(f"built_{yr}_pct", warp(100.0 * a / cell_m2, tr, crs, Resampling.average), tags=dict(source=f"GHSL GHS-BUILT-S R2023A epoch {yr} (3 arcsec), % of cell built-up"))
for yr in ("2000", "2025", "2030"):
    fs = glob.glob(f"{RAW}/**/GHS_POP_E{yr}_*.tif", recursive=True)
    if not fs: print("  (no pop", yr, ")"); continue
    a, tr, crs, nd = read_window(fs[0]); a = np.where(a < 0, 0, a)
    save(f"pop_{yr}", warp(a, tr, crs, Resampling.sum, nodata=0.0), nodata=-9999.0, tags=dict(source=f"GHSL GHS-POP R2023A epoch {yr} (3 arcsec), residents per cell"))

# 4. JRC global flood hazard, 100-year return period depth (m) -> mean & max per cell
print("flood")
fs = glob.glob(f"{RAW}/flood_rp100*.tif")
if fs:
    a, tr, crs, nd = read_window(fs[0]); a = np.where(a == nd, 0, a); a = np.where(a < 0, 0, a)
    save("flood_rp100_max_m", warp(a, tr, crs, Resampling.max), tags=dict(source="JRC Global Flood Hazard Map, RP100 depth (m), max per cell; 0 = not flooded"))
    save("flood_rp100_mean_m", warp(a, tr, crs, Resampling.average), tags=dict(source="JRC Global Flood Hazard Map, RP100 depth (m), mean per cell"))

# 5. Global Wind Atlas 3, mean wind speed 100 m (m/s), 250 m
print("wind")
fs = glob.glob(f"{RAW}/gwa_wind100.tif")
if fs:
    a, tr, crs, nd = read_window(fs[0]); a = np.where((a == nd) | (a < 0), np.nan, a)
    save("wind_100m", warp(a, tr, crs, Resampling.average), tags=dict(source="Global Wind Atlas 3.0 (DTU/World Bank), mean wind speed at 100 m, m/s"))
print("done")
