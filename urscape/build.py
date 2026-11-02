"""Bangun lapisan ur-scape (site "West Java") dari data repo ini — tanpa QGIS.

ur-scape membaca grid CSV UTF-16 (format persis keluaran plugin QGIS ur-scapeDataImporter) dari
Data/Sites/<site>/ dan mengonversinya sendiri ke .bin saat pertama dibuka. Skrip ini menulis format itu
langsung dari: master SPKLU nasional, transaksi PLN Jabar Mar 2026, ttm/ttm.json (akses desa), analysis/rebana_data.json
(kecamatan Rebana + GI), data/grid-id/data_jamali.js (GI, pembangkit, transmisi).

    pip install numpy pandas openpyxl geopandas pyogrio shapely rasterio
    python3 urscape/build.py            # site West Java (0,5') -> urscape/out/Sites/West Java/*.csv, layers_add.csv, citations_add.csv,
    python3 urscape/build.py Rebana --keep   # site Rebana (300 m), ditambahkan ke paket yang sama
                                        #    urscape/ur-scape-west-java.zip, analysis/urscape_layers.json (payload web)
"""
import base64, json, math, os, re, shutil, sys, zipfile, zlib
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import shape, LineString

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
DATE = "202606"
SITES = {   # extent (derajat), ukuran sel, kode resolusi ur-scape (C = 0,5 menit busur; D = metrik, di sini 300 m)
    "West Java": dict(west=106.30, east=108.95, north=-5.85, south=-7.85, res=0.5 / 60.0, sign="C", web="analysis/urscape_layers.json"),
    "Rebana":    dict(west=107.45, east=108.85, north=-6.05, south=-7.15, res=300 / 111320.0, sign="D", web="analysis/urscape_layers_rebana.json"),
}
SITE = sys.argv[1] if len(sys.argv) > 1 else "West Java"; CFG = SITES[SITE]
WEST, EAST, NORTH, SOUTH, RES, SIGN = CFG["west"], CFG["east"], CFG["north"], CFG["south"], CFG["res"], CFG["sign"]
CX = int(round((EAST - WEST) / RES)); CY = int(round((NORTH - SOUTH) / RES))
EAST = WEST + CX * RES; SOUTH = NORTH - CY * RES
OUT = "urscape/out"; SITEDIR = f"{OUT}/Sites/{SITE}"
if "--keep" not in sys.argv: shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(SITEDIR, exist_ok=True)
REPO_URL = "https://github.com/qastill/pathwaysevcharging"
SRC = "Qashtalani Haramaini - pathwaysevcharging (PLN; TTM Alyas Widita; Kontur 2023; BPS; RUPTL 2025-2034 / OSM)"
LAYERS = []   # dict(name, group, rgb, units|categories, citation, values, mask)

def cell(lon, lat):
    if not (math.isfinite(lon) and math.isfinite(lat)): return None
    x = int((lon - WEST) / RES); y = int((NORTH - lat) / RES)
    return (x, y) if 0 <= x < CX and 0 <= y < CY else None

def write_grid(L):
    fn = f"{SITEDIR}/{L['name']}_{SIGN}_{SITE}@0_{DATE}_grid.csv"
    with open(fn, "w", newline="", encoding="utf-16") as f:
        f.write(f"METADATA,TRUE\nLayer Name,{L['name']}\nSource,{SRC}\nCitation,\"{L['citation']}\"\nLink,{REPO_URL}\nColouring,Multi\n")
        if L.get("categories"):
            f.write("CATEGORIES,TRUE\n" + "".join(f"{c},{i+1}\n" for i, c in enumerate(L["categories"])))
        else:
            f.write(f"CATEGORIES,FALSE\nUnits,{L['units']}\n")
        f.write(f"West,{WEST}\nNorth,{NORTH}\nEast,{EAST}\nSouth,{SOUTH}\nCount X,{CX}\nCount Y,{CY}\nVALUE,MASK\n")
        v, m = L["values"], L["mask"]
        for y in range(CY):
            for x in range(CX):
                if m[y, x]:
                    val = v[y, x]; val = int(val) if float(val).is_integer() else round(float(val), 3)
                    f.write(f"{val},1\n")
                else: f.write("0,0\n")

def add(name, group, rgb, citation, values, mask, units=None, categories=None):
    LAYERS.append(dict(name=name, group=group, rgb=rgb, citation=citation, values=values, mask=mask, units=units, categories=categories))
    print(f"  {name}: {int(mask.sum())} cells")

def point_grid(df, loncol, latcol, valcol, how="sum"):
    v = np.zeros((CY, CX)); m = np.zeros((CY, CX), bool)
    for lon, lat, val in zip(df[loncol], df[latcol], df[valcol]):
        c = cell(float(lon), float(lat))
        if c and val == val:
            x, y = c; v[y, x] = (v[y, x] + val) if how == "sum" or not m[y, x] else max(v[y, x], val); m[y, x] = True
    return v, m

def cells_of_polygons(gdf, cols):
    xs = WEST + (np.arange(CX) + 0.5) * RES; ys = NORTH - (np.arange(CY) + 0.5) * RES
    XX, YY = np.meshgrid(xs, ys)
    c = gpd.GeoDataFrame({"row": np.repeat(np.arange(CY), CX), "col": np.tile(np.arange(CX), CY)},
                         geometry=gpd.points_from_xy(XX.ravel(), YY.ravel()), crs="EPSG:4326")
    h = gpd.sjoin(c, gdf[cols + ["geometry"]], how="inner", predicate="within")
    return h[~h.index.duplicated()]

def to_grid(h, col):
    v = np.zeros((CY, CX)); m = np.zeros((CY, CX), bool)
    vals = pd.to_numeric(h[col], errors="coerce").to_numpy(); ok = ~np.isnan(vals)
    v[h.row.to_numpy()[ok], h.col.to_numpy()[ok]] = vals[ok]; m[h.row.to_numpy()[ok], h.col.to_numpy()[ok]] = True
    return v, m

# ---------------- 1. SPKLU ----------------
print("SPKLU")
d = pd.read_excel("SPKLU_Indonesia_Lengkap_2026-06-08.xlsx", sheet_name=0)
d["Latitude"] = pd.to_numeric(d["Latitude"], errors="coerce"); d["Longitude"] = pd.to_numeric(d["Longitude"], errors="coerce")
d = d.dropna(subset=["Latitude", "Longitude"]); d["chg"] = pd.to_numeric(d["Jumlah Charger"], errors="coerce").fillna(0); d["one"] = 1
cit = "PLN Charge.IN master list of public EV charging stations (SPKLU), status June 2026"
add("EV Charging Stations", "EV Charging", (60, 220, 120), cit, *point_grid(d, "Longitude", "Latitude", "one"), units="stations")
add("EV Chargers", "EV Charging", (60, 200, 170), cit, *point_grid(d, "Longitude", "Latitude", "chg"), units="chargers")
r = pd.read_csv("Rekap_SPKLU_Jabar_ArcGIS.csv", encoding="utf-8-sig").dropna(subset=["Latitude", "Longitude"])
r["util"] = r["Tagging_SPKLU"].str.split().str[0].map({"Merah": 1, "Kuning": 2, "Hijau": 3})
cit = "PLN UID Jawa Barat - SPKLU transaction records, March 2026 (station-level aggregate)"
add("EV Charging Energy", "EV Charging", (255, 170, 40), cit, *point_grid(r, "Longitude", "Latitude", "Energi_kWh"), units="kWh/month")
add("EV Charging Sessions", "EV Charging", (255, 120, 40), cit, *point_grid(r, "Longitude", "Latitude", "Jml_Transaksi"), units="sessions/month")
add("EV Charging Utilisation", "EV Charging", (230, 60, 60), cit, *point_grid(r, "Longitude", "Latitude", "util", how="max"),
    categories=["Low (<10 sessions)", "Medium (11-50 sessions)", "High (>50 sessions)"])

# ---------------- 2. Akses desa (ttm/ttm.json) ----------------
print("village access")
t = json.load(open("ttm/ttm.json")); S = t["summary"]
V = pd.DataFrame(t["villages"], columns=t["village_cols"]).set_index("id")
geo = gpd.read_file("ttm/input/villages_simplified.geojson").merge(V, left_on="id", right_index=True, how="inner")
geo["dens"] = geo["pop"] / geo["area"]; geo["rung1"] = geo["rung"] + 1
geo["cls"] = pd.cut(geo["access"].fillna(999), [-1, 15, 30, 60, 1e9], labels=[1, 2, 3, 4]).astype(int)
h = cells_of_polygons(geo, ["access", "near", "far", "dens", "cap10", "rung1", "cls"])
cit = (f"Village-level car travel time to nearest public charger (r5r on OSM, max {S['cut']} min; origins GADM 4.1 villages, "
       f"TTM by Alyas Widita); chargers from PLN Charge.IN Jun 2026 ({S['sites']} sites). ttm/compute.py")
add("Travel Time to Nearest Charger", "EV Charging", (120, 200, 255), cit, *to_grid(h, "access"), units="min by car")
add("Chargers within 10 min", "EV Charging", (100, 180, 255), cit, *to_grid(h, "near"), units="chargers")
add("Chargers within 30 min", "EV Charging", (80, 160, 255), cit, *to_grid(h, "far"), units="chargers")
add("Charger Access Class", "EV Charging", (255, 90, 160), cit, *to_grid(h, "cls"), categories=["Within 15 min", "15-30 min", "30-60 min", "None within 60 min"])
add("Charging Capacity per Household", "EV Charging", (200, 120, 255),
    "E2SFCA: charger kW reachable within 10 min per household (3.6 persons, Kontur 2023); sufficiency threshold 0.03 kW/household",
    *to_grid(h, "cap10"), units="kW per household (10 min)")
add("Charging Service Ladder", "EV Charging", (255, 140, 220),
    "Service ladder: rung 0 = no charger within 10 min; rung 1 = reachable but < 0.03 kW/household; rung 2 = reachable and sufficient",
    *to_grid(h, "rung1"), categories=["No charger within 10 min", "Reachable - capacity short", "Reachable - capacity sufficient"])
add("Population Density", "Society and Economy", (240, 220, 120), "Kontur Population 2023 (H3 res 8) aggregated to village polygons / village area",
    *to_grid(h, "dens"), units="people per km2")

# ---------------- 3. Kecamatan Rebana (analysis/rebana_data.json) ----------------
print("Rebana kecamatan")
D = json.load(open("analysis/rebana_data.json"))
rk = pd.DataFrame(D["rk"]); rk["geometry"] = rk["geometry"].apply(shape); rk = gpd.GeoDataFrame(rk, geometry="geometry", crs="EPSG:4326")
hk = cells_of_polygons(rk, ["ipm", "pov", "exp", "d_gi", "gi_head", "d_spklu", "ch"])
cit = "Rebana metropolitan kecamatan (190): BPS Profil Kab/Kota 2024, PLN UID Jabar substation loading, charger register; analysis/rebana_build.py"
G = "Society and Economy"
add("Rebana HDI (IPM)", G, (255, 200, 80), cit, *to_grid(hk, "ipm"), units="index")
add("Rebana Poverty Rate", G, (255, 120, 80), cit, *to_grid(hk, "pov"), units="%")
add("Rebana Expenditure per Capita", G, (255, 170, 90), cit, *to_grid(hk, "exp"), units="Rp thousand/month")
add("Rebana Distance to Substation", G, (160, 160, 255), cit, *to_grid(hk, "d_gi"), units="km")
add("Rebana Substation Headroom", G, (140, 220, 200), cit, *to_grid(hk, "gi_head"), units="% of MVA free at peak")
add("Rebana Distance to Charger", G, (120, 200, 160), cit, *to_grid(hk, "d_spklu"), units="km")
add("Rebana Chargers per Kecamatan", G, (90, 220, 140), cit, *to_grid(hk, "ch"), units="chargers")

# ---------------- 4. Jaringan (data/grid-id/data_jamali.js) ----------------
print("power grid")
js = open("data/grid-id/data_jamali.js", encoding="utf-8").read(); body = js[js.index("{"): js.rindex("}") + 1]
body = re.sub(r"(\w+):\s*\{\"type\"", r'"\1": {"type"', body); body = re.sub(r",\s*}\s*$", "}", body); J = json.loads(body)
def fc_df(fc):
    df = pd.DataFrame([{**f["properties"], "geometry": f["geometry"]} for f in fc["features"]])
    df["lo"] = df.geometry.apply(lambda g: g["coordinates"][0]); df["la"] = df.geometry.apply(lambda g: g["coordinates"][1]); return df
cit = "Jamali grid: substations and transmission lines from RUPTL 2025-2034 tables matched to OpenStreetMap (qastill/electraskillacademy); loading from PLN UID Jabar peak reports"
sub = fc_df(J["substations"]); sub["mva"] = pd.to_numeric(sub["capacity_mva"], errors="coerce")
add("Substation Capacity", "Power Grid", (255, 255, 120), cit, *point_grid(sub, "lo", "la", "mva"), units="MVA")
gi = pd.DataFrame(D["grid"]["gi"]); gi["peak"] = gi["load"].apply(lambda L: L.get("peak_pct") if isinstance(L, dict) else np.nan)
add("Substation Peak Loading", "Power Grid", (255, 160, 60), cit, *point_grid(gi.dropna(subset=["peak"]), "lo", "la", "peak", how="max"), units="% of capacity")
gen = fc_df(J["generators"]); gen["mw"] = pd.to_numeric(gen["capacity_mw"], errors="coerce")
add("Power Plant Capacity", "Power Grid", (255, 100, 100), cit, *point_grid(gen, "lo", "la", "mw"), units="MW")
v = np.zeros((CY, CX)); m = np.zeros((CY, CX), bool); kvmap = {"500": 3, "150": 2, "70": 1}
for f in J["transmission"]["features"]:
    cat = max((kvmap.get(k, 0) for k in re.findall(r"\d+", str(f["properties"].get("voltage_class", "")))), default=0)
    if not cat or f["geometry"]["type"] not in ("LineString", "MultiLineString"): continue
    for coords in ([f["geometry"]["coordinates"]] if f["geometry"]["type"] == "LineString" else f["geometry"]["coordinates"]):
        ln = LineString(coords); n = max(2, int(ln.length / (RES / 2)))
        for i in range(n + 1):
            p = ln.interpolate(i / n, normalized=True); c = cell(p.x, p.y)
            if c: v[c[1], c[0]] = max(v[c[1], c[0]], cat); m[c[1], c[0]] = True
add("Transmission Lines", "Power Grid", (255, 230, 150), cit, v, m, categories=["70 kV", "150 kV", "500 kV"])

# ---------------- 5. Insights (lapisan turunan yang menjawab pertanyaan) ----------------
print("insights")
G = "Insights"
nz = lambda x: (x - x.min()) / (x.max() - x.min() + 1e-9)
# 5a. Prioritas penempatan charger per kecamatan Rebana: kebutuhan (waktu tempuh & jarak ke charger) x permintaan (penduduk)
#     x kesiapan jaringan (headroom GI). 0-100, makin tinggi makin layak dibangun duluan.
rk["need"] = (nz(rk["t_mean"]) + nz(rk["d_spklu"])) / 2
rk["prio"] = (100 * (0.5 * rk["need"] + 0.25 * nz(np.log(rk["pop"])) + 0.25 * nz(rk["gi_head"]))).round(1)
rk["kpi_cls"] = np.where(rk["priority"], 2, np.where(rk["kpi"], 1, np.nan))
hp = cells_of_polygons(rk, ["prio", "kpi_cls"])
add("Charger Siting Priority", G, (255, 80, 40),
    "Siting priority 0-100 per Rebana kecamatan = 0.5 x need (mean of normalised population-weighted travel time to nearest charger and distance to charger) "
    "+ 0.25 x demand (normalised log population) + 0.25 x grid readiness (normalised substation headroom). Inputs: analysis/rebana_data.json (rk)",
    *to_grid(hp, "prio"), units="score 0-100")
add("Rebana KPI Kecamatan", G, (255, 210, 60), "Kecamatan hosting designated Rebana industrial zones (KPI) and the four priority zones; analysis/rebana_data.json (rk.kpi, rk.priority)",
    *to_grid(hp, "kpi_cls"), categories=["Hosts a KPI zone", "Priority KPI zone"])
# 5b. Access gap: penduduk desa yang charger terdekatnya > 30 menit (DV riset: kebutuhan yang belum terlayani)
geo["gap"] = np.where(geo["access"].fillna(999) > 30, geo["pop"], np.nan)
hg = cells_of_polygons(geo, ["gap"])
add("Population Beyond 30 min", G, (255, 60, 120),
    f"Access gap: residents (Kontur 2023) of villages whose nearest public charger is more than 30 min by car or unreachable within {S['cut']} min; NoData = village within 30 min. ttm/ttm.json",
    *to_grid(hg, "gap"), units="people")
# 5c. Usulan lokasi model cakupan 10 km (greedy, rebana_data cover.picks): tiap titik = tambahan penduduk yang masuk radius 10 km
cp = pd.DataFrame(D["cover"]["picks"])
add("Coverage Model Picks", G, (120, 255, 120),
    f"Greedy 10-km coverage model: the next kecamatan centroids that add the most Rebana residents within {D['cover']['radius_km']:.0f} km of a charger "
    f"(baseline share {D['cover']['base_share']:.0%}); value = residents newly covered. analysis/rebana_build.py", *point_grid(cp, "lo", "la", "gain"), units="residents newly covered")
# 5d. Trafo distribusi overload (Indramayu, H3 res 7): persen trafo >100% beban
from shapely.geometry import Polygon
hx = gpd.GeoDataFrame([{"ol_pct": 100.0 * h["ol"] / max(h["n"], 1), "load": h["load"], "geometry": Polygon(h["b"])} for h in D["idm_hex"]], crs="EPSG:4326")
hh = cells_of_polygons(hx, ["ol_pct", "load"])
add("Transformer Overload Share", G, (255, 140, 0),
    f"Share of measured distribution transformers loaded above 100% per H3 res-7 hexagon (~5 km2), PLN UP3 Indramayu register ({D['idm_meta']['gardu_valid']} transformers); aggregated, no transformer identities",
    *to_grid(hh, "ol_pct"), units="% of transformers")

# ---------------- 6. Data terbuka: surya, lahan, terbangun, penduduk, banjir, angin (data/open/*.tif) ----------------
print("open data (solar, land, flood)")
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
TR_SITE = from_origin(WEST, NORTH, RES, RES)
def open_raster(name, resampling=Resampling.average):
    """Baca data/open/<name>.tif (0,0025 deg, West Java) ke grid site. Mengembalikan (values, mask)."""
    fn = f"data/open/{name}.tif"
    if not os.path.exists(fn): return None
    with rasterio.open(fn) as src:
        a = src.read(1).astype("float32"); nd = src.nodata; a = np.where(a == nd, np.nan, a)
        dst = np.full((CY, CX), np.nan, "float32")
        reproject(a, dst, src_transform=src.transform, src_crs=src.crs, dst_transform=TR_SITE, dst_crs="EPSG:4326",
                  resampling=resampling, src_nodata=np.nan, dst_nodata=np.nan)
    m = np.isfinite(dst); return np.where(m, dst, 0.0), m
def addr(name, group, rgb, citation, src, units=None, categories=None, resampling=Resampling.average, fn=None, mask_fn=None):
    r = open_raster(src, resampling)
    if r is None: print("  (skip", name, "- no", src, ")"); return None
    v, m = r
    if fn is not None: v = fn(v)
    if mask_fn is not None: m = m & mask_fn(v)
    add(name, group, rgb, citation, np.where(m, v, 0.0), m, units=units, categories=categories); return v, m
G = "Energy Resources"
gsa = "Global Solar Atlas 2.0 (Solargis, World Bank/ESMAP), long-term annual average sampled every 0.025 deg via the GSA point API; data/open/prep.py"
pv = addr("Solar PV Yield", G, (255, 220, 0), gsa + ". PVOUT: specific photovoltaic power output of a fixed, optimally tilted crystalline-silicon system", "solar_pvout", units="kWh/kWp/year")
addr("Global Horizontal Irradiation", G, (255, 190, 0), gsa + ". GHI", "solar_ghi", units="kWh/m2/year")
addr("Direct Normal Irradiation", G, (255, 150, 0), gsa + ". DNI (relevant for CSP/tracking)", "solar_dni", units="kWh/m2/year")
addr("Solar Seasonality", G, (255, 240, 150), gsa + ". Ratio of the lowest to the highest monthly PV output (100 = flat profile, lower = stronger wet-season dip)", "solar_season_ratio", units="% lowest/highest month", fn=lambda v: 100 * v)
addr("Air Temperature", G, (255, 120, 120), gsa + ". Mean annual air temperature at 2 m (PV output falls ~0.4%/degC above 25 degC)", "air_temp", units="degC")
addr("Wind Speed 100 m", G, (150, 220, 255), "Global Wind Atlas 3.0 (DTU Wind Energy / World Bank), mean wind speed at 100 m height, 250 m resolution", "wind_100m", units="m/s")
addr("Elevation", G, (200, 200, 200), gsa + ". Terrain elevation (ELE)", "elevation", units="m above sea level")
G = "Land and Hazard"
wc = "ESA WorldCover 2021 v200 (10 m Sentinel-1/2 land cover), aggregated to share of each cell; data/open/prep.py"
crop = addr("Cropland Share", G, (220, 200, 80), wc + ". Class 40 cropland", "lc_crop_pct", units="% of cell")
addr("Tree Cover Share", G, (60, 160, 60), wc + ". Class 10 tree cover", "lc_tree_pct", units="% of cell")
bu21 = addr("Built-up Share 2021", G, (230, 100, 100), wc + ". Class 50 built-up", "lc_built_pct", units="% of cell")
addr("Dominant Land Cover", G, (160, 200, 120), wc + ". Most frequent class in the cell", "lc_dominant", resampling=Resampling.mode,
     fn=lambda v: np.select([v == 10, v == 20, v == 30, v == 40, v == 50, v == 60, v == 80, v == 90, v == 95], [1, 2, 3, 4, 5, 6, 7, 8, 9], 0),
     categories=["Tree cover", "Shrubland", "Grassland", "Cropland", "Built-up", "Bare", "Water", "Wetland", "Mangrove"], mask_fn=lambda v: v > 0)
ghs = "GHSL R2023A (JRC): GHS-BUILT-S built-up surface (3 arcsec) and GHS-POP residents (3 arcsec); data/open/prep.py"
b20 = addr("Built-up 2020 (GHSL)", G, (240, 130, 90), ghs + ". Share of cell surface built in 2020", "built_2020_pct", units="% of cell")
b00 = open_raster("built_2000_pct"); b75 = open_raster("built_1975_pct")
if b20 and b00:
    g = b20[0] - b00[0]; m = b20[1] & b00[1] & (g > 0.5)
    add("Built-up Growth 2000-2020", G, (255, 90, 60), ghs + ". Percentage-point increase of built-up share between 2000 and 2020 (cells with > 0.5 pp)", np.where(m, g, 0), m, units="pp of cell")
if b00 and b75:
    g = b00[0] - b75[0]; m = b00[1] & b75[1] & (g > 0.5)
    add("Built-up Growth 1975-2000", G, (255, 150, 100), ghs + ". Percentage-point increase of built-up share between 1975 and 2000", np.where(m, g, 0), m, units="pp of cell")
km2 = (RES * 111320 * math.cos(math.radians(-6.8))) * (RES * 111320) / 1e6   # luas sel (km2) di lintang Rebana
p25 = open_raster("pop_2025", Resampling.sum); p30 = open_raster("pop_2030", Resampling.sum); p00 = open_raster("pop_2000", Resampling.sum)
if p25:
    add("Population 2025 (GHSL)", G, (250, 230, 140), ghs + ". Residents 2025 per cell, expressed as density", p25[0] / km2, p25[1] & (p25[0] > 0), units="people per km2")
if p25 and p30:
    m = p25[1] & p30[1] & (p25[0] > 50); ch = np.where(m, 100 * (p30[0] - p25[0]) / np.maximum(p25[0], 1), 0)
    add("Population Change 2025-2030", G, (255, 200, 120), ghs + ". Projected change of residents 2025 -> 2030 (cells with > 50 residents)", ch, m, units="%")
if p25 and p00:
    m = p25[1] & p00[1] & (p00[0] > 50); ch = np.where(m, 100 * (p25[0] - p00[0]) / np.maximum(p00[0], 1), 0)
    add("Population Change 2000-2025", G, (255, 170, 110), ghs + ". Change of residents 2000 -> 2025 (cells with > 50 residents in 2000)", ch, m, units="%")
jrc = "JRC Global Flood Hazard Maps (CEMS-GloFAS, Dottori et al.), river flood depth for a 100-year return period, 30 arcsec; data/open/prep.py"
fl = addr("Flood Depth RP100", G, (80, 140, 255), jrc + ". Maximum depth in the cell; NoData = not flooded", "flood_rp100_max_m", resampling=Resampling.max, units="m", mask_fn=lambda v: v > 0.05)
if fl:
    v = fl[0]; cls = np.select([v <= 0.05, v < 0.5, v < 1.0, v < 2.0], [0, 1, 2, 3], 4); m = cls > 0
    add("Flood Hazard Class", G, (40, 100, 255), jrc + ". Depth classes", cls, m, categories=["Shallow (< 0.5 m)", "Moderate (0.5-1 m)", "Deep (1-2 m)", "Very deep (> 2 m)"])

# ---------------- 7. Insights dari data terbuka ----------------
print("open-data insights")
G = "Insights"
if pv and bu21:
    # Potensi PLTS atap: luas terbangun (WorldCover) x 25% atap terpakai x 0.15 kWp/m2 x PVOUT -> MWh/tahun per sel
    roof_kwp = bu21[0] / 100 * (km2 * 1e6) * 0.25 * 0.15; mwh = roof_kwp * pv[0] / 1000; m = bu21[1] & pv[1] & (roof_kwp > 5)
    add("Rooftop PV Potential", G, (255, 230, 60), "Technical rooftop PV potential per cell = built-up area (WorldCover 2021) x 25% usable roof x 0.15 kWp/m2 x PVOUT (GSA). Indicative; no shading/structural screening", np.where(m, mwh, 0), m, units="MWh/year per cell")
if pv and crop and fl is not None:
    # Kelayakan PLTS skala utilitas: PVOUT tinggi + lahan terbuka (sawah/rumput/tanah kosong) + bebas banjir + dekat GI (Rebana) / headroom
    grass = open_raster("lc_grass_pct"); bare = open_raster("lc_bare_pct"); tree = open_raster("lc_tree_pct"); water = open_raster("lc_water_pct")
    openland = crop[0] + (grass[0] if grass else 0) + (bare[0] if bare else 0)
    flood_ok = np.where(fl[1] & (fl[0] >= 0.5), 0.0, 1.0)
    dgi = next((L for L in LAYERS if L["name"] == "Rebana Distance to Substation"), None)
    near_gi = np.clip(1 - dgi["values"] / 15.0, 0, 1) if dgi is not None else np.full((CY, CX), 0.5)
    pvn = np.where(pv[1], (pv[0] - np.nanpercentile(pv[0][pv[1]], 2)) / (np.nanpercentile(pv[0][pv[1]], 98) - np.nanpercentile(pv[0][pv[1]], 2) + 1e-9), 0); pvn = np.clip(pvn, 0, 1)
    sc = 100 * (0.35 * pvn + 0.30 * np.clip(openland / 100, 0, 1) + 0.15 * flood_ok + 0.20 * near_gi)
    m = pv[1] & crop[1] & (openland >= 50) & ((bu21[0] if bu21 else 0) < 20) & ((water[0] if water else 0) < 10) & ((tree[0] if tree else 0) < 30)
    add("Utility Solar Site Score", G, (255, 180, 0), "Screening score 0-100 for ground-mounted PV: 0.35 x PV yield + 0.30 x open land share (cropland/grass/bare, WorldCover) + 0.15 x flood-free (RP100 depth < 0.5 m) + 0.20 x proximity to a substation (< 15 km, Rebana kecamatan mean). Shown only where open land >= 50%, built-up < 20%, water < 10%, tree < 30%. Agricultural-land policy not screened", np.where(m, sc, 0), m, units="score 0-100")
if fl is not None:
    # Aset pengisian & GI di zona banjir
    st = next(L for L in LAYERS if L["name"] == "EV Chargers"); sub_ = next(L for L in LAYERS if L["name"] == "Substation Capacity")
    deep = fl[1] & (fl[0] >= 0.5); cls = np.select([st["mask"] & deep & sub_["mask"], st["mask"] & deep, sub_["mask"] & deep], [3, 1, 2], 0); m = cls > 0
    add("Grid Assets in Flood Zone", G, (0, 200, 255), "Cells with a public charging station and/or a substation where the JRC 100-year river flood depth is >= 0.5 m", cls, m, categories=["Charging station", "Substation", "Both"])
    tt = next((L for L in LAYERS if L["name"] == "Travel Time to Nearest Charger"), None)
    if p25 and tt is not None:
        m = p25[1] & deep & (p25[0] > 20); add("Population in Flood Zone", G, (120, 160, 255), "Residents (GHSL 2025) living in cells with 100-year flood depth >= 0.5 m", np.where(m, p25[0], 0), m, units="people per cell")
if b20 and b00:
    tt = next((L for L in LAYERS if L["name"] == "Travel Time to Nearest Charger"), None)
    if tt is not None:
        g = b20[0] - b00[0]; m = b20[1] & b00[1] & (g > 2) & tt["mask"] & (tt["values"] > 30)
        add("Growth Without Charging", G, (255, 60, 200), "Cells that gained > 2 pp of built-up surface 2000-2020 (GHSL) but whose village is still > 30 min by car from the nearest public charger (TTM): new settlement/industrial frontier without charging", np.where(m, g, 0), m, units="pp built-up gained")

# ---------------- tulis paket ur-scape ----------------
print("writing ur-scape package")
for L in LAYERS: write_grid(L)
groups = {}
for L in LAYERS: groups.setdefault(L["group"], []).append(L)
with open(f"{OUT}/layers_add.csv", "w", encoding="utf-16", newline="") as f:
    f.write("Type,Name,Color (red),Color (green),Color (blue)\r\n")
    for g, Ls in groups.items():
        f.write(f",,,,\r\nGroup,{g},,,\r\n" + "".join(f"Layer,{L['name']},{L['rgb'][0]},{L['rgb'][1]},{L['rgb'][2]}\r\n" for L in Ls))
with open(f"{OUT}/citations_add.csv", "w", encoding="utf-16", newline="") as f:
    f.write("Layer,Source,Mandatory,Citation,Link\r\n" + "".join(f'{L["name"]},{SRC},FALSE,"{L["citation"]}",{REPO_URL}\r\n' for L in LAYERS))
shutil.copy("urscape/install.py", f"{OUT}/install.py"); shutil.copy("urscape/PACKAGE_README.md", f"{OUT}/README.md")
with zipfile.ZipFile("urscape/ur-scape-west-java.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(OUT):
        if os.path.basename(dp) == "qgis": continue
        for fn in fs: z.write(os.path.join(dp, fn), os.path.relpath(os.path.join(dp, fn), OUT))
print("zip:", os.path.getsize("urscape/ur-scape-west-java.zip") // 1024, "KB")

# ---------------- paket QGIS: GeoTIFF per lapisan + titik SPKLU (urscape/west-java-layers-qgis.zip) ----------------
if SITE != "West Java": QDIR = None
else:
  print("writing QGIS package (GeoTIFF)")
  import rasterio
  from rasterio.transform import from_origin
  QDIR = f"{OUT}/qgis"; os.makedirs(QDIR, exist_ok=True)
  tr = from_origin(WEST, NORTH, RES, RES)
  for L in LAYERS:
      arr = np.where(L["mask"], L["values"], -9999).astype("float32")
      tags = dict(layer=L["name"], group=L["group"], units=L.get("units") or "", citation=L["citation"], source=SRC,
                  categories="; ".join(f"{i+1}={c}" for i, c in enumerate(L["categories"])) if L.get("categories") else "")
      fn = f"{QDIR}/{re.sub(r'[^A-Za-z0-9]+', '_', L['name']).strip('_')}.tif"
      with rasterio.open(fn, "w", driver="GTiff", height=CY, width=CX, count=1, dtype="float32", crs="EPSG:4326", transform=tr,
                         nodata=-9999, compress="deflate") as dst:
          dst.write(arr, 1); dst.update_tags(**tags); dst.set_band_description(1, L["name"])
  pts = gpd.GeoDataFrame(d[["ID SPKLU", "Nama SPKLU", "Alamat", "Kapasitas (kW)", "Status", "Jumlah Charger", "Jumlah Connector", "Kategori", "Latitude", "Longitude"]],
                         geometry=gpd.points_from_xy(d.Longitude, d.Latitude), crs="EPSG:4326")
  pts = pts.cx[WEST:EAST, SOUTH:NORTH]; pts.to_file(f"{QDIR}/spklu_stations_jun2026.geojson", driver="GeoJSON")
  rj = gpd.GeoDataFrame(r, geometry=gpd.points_from_xy(r.Longitude, r.Latitude), crs="EPSG:4326"); rj.to_file(f"{QDIR}/spklu_pln_jabar_mar2026.geojson", driver="GeoJSON")
  open(f"{QDIR}/README.md", "w").write(f"# West Java layers for QGIS\n\nGeoTIFF (EPSG:4326, 0.5 arc-minute cells, nodata -9999) of the {len(LAYERS)} ur-scape layers + SPKLU points.\n"
      "Drag the .tif files into QGIS; layer name, units, citation and category codes are in the file tags (Layer Properties > Metadata). "
      "To push any of them into ur-scape through its official QGIS plugin, use GIS/Plugins/ur-scapeDataImporter from the ur-scape download "
      "(resolution 'C', location 'West Java'); the ur-scape package in this repo already contains the same grids.\n\n"
      f"Source: {SRC}\n{REPO_URL}\n")
  with zipfile.ZipFile("urscape/west-java-layers-qgis.zip", "w", zipfile.ZIP_DEFLATED) as z:
      for fn in sorted(os.listdir(QDIR)): z.write(os.path.join(QDIR, fn), fn)
  print("qgis zip:", os.path.getsize("urscape/west-java-layers-qgis.zip") // 1024, "KB")

# ---------------- payload web (analysis/urscape_layers.json) ----------------
# tiap layer: nilai dikuantisasi 8-bit (1..255, 0 = NoData) antara lo..hi (persentil 2-98 utk numerik), zlib+base64
print("writing web payload")
web = dict(site=SITE, sign=SIGN, west=WEST, east=EAST, north=NORTH, south=SOUTH, cx=CX, cy=CY, res=RES, source=SRC, repo=REPO_URL, generated=DATE, layers=[])
for L in LAYERS:
    v, m = L["values"], L["mask"]; vals = v[m]
    if L.get("categories"): lo, hi = 1, len(L["categories"]); q = np.where(m, v, 0).astype(np.uint8)
    else:
        lo, hi = (float(np.percentile(vals, 2)), float(np.percentile(vals, 98))) if vals.size else (0.0, 1.0)
        if hi <= lo: hi = lo + 1
        q = np.zeros((CY, CX), np.uint8); q[m] = 1 + np.clip((vals - lo) / (hi - lo) * 254, 0, 254).round().astype(np.uint8)
    vmin, vmax = (float(vals.min()), float(vals.max())) if vals.size else (0.0, 1.0)
    raw = np.zeros((CY, CX), np.uint16)                               # nilai asli utk hover/area summary: uint16 antara min..max (zlib)
    raw[m] = np.round((vals - vmin) / (vmax - vmin if vmax > vmin else 1) * 65535).astype(np.uint16)
    web["layers"].append(dict(name=L["name"], group=L["group"], rgb=L["rgb"], units=L.get("units"), categories=L.get("categories"),
        citation=L["citation"], cells=int(m.sum()), lo=round(lo, 4), hi=round(hi, 4),
        min=round(vmin, 4) if vals.size else None, max=round(vmax, 4) if vals.size else None,
        q=base64.b64encode(zlib.compress(q.tobytes(), 9)).decode(), raw16=base64.b64encode(zlib.compress(raw.tobytes(), 9)).decode()))
# data tiap lapisan dipisah (dimuat web saat lapisan diklik) agar indeks tetap kecil
DDIR = CFG["web"].replace(".json", "_data"); shutil.rmtree(DDIR, ignore_errors=True); os.makedirs(DDIR)
tot = 0
for i, L in enumerate(web["layers"]):
    fn = f"{DDIR}/{i:02d}.json"; json.dump(dict(q=L.pop("q"), raw16=L.pop("raw16")), open(fn, "w"), separators=(",", ":")); L["file"] = os.path.relpath(fn, "analysis"); tot += os.path.getsize(fn)
json.dump(web, open(CFG["web"], "w"), separators=(",", ":"))
print("payload:", CFG["web"], os.path.getsize(CFG["web"]) // 1024, "KB index +", tot // 1024, "KB data;", len(LAYERS), "layers")
