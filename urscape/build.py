"""Bangun lapisan ur-scape (site "West Java") dari data repo ini — tanpa QGIS.

ur-scape membaca grid CSV UTF-16 (format persis keluaran plugin QGIS ur-scapeDataImporter) dari
Data/Sites/<site>/ dan mengonversinya sendiri ke .bin saat pertama dibuka. Skrip ini menulis format itu
langsung dari: master SPKLU nasional, transaksi PLN Jabar Mar 2026, ttm/ttm.json (akses desa), analysis/rebana_data.json
(kecamatan Rebana + GI), data/grid-id/data_jamali.js (GI, pembangkit, transmisi).

    pip install numpy pandas openpyxl geopandas pyogrio shapely
    python3 urscape/build.py            # -> urscape/out/Sites/West Java/*.csv, layers_add.csv, citations_add.csv,
                                        #    urscape/ur-scape-west-java.zip, analysis/urscape_layers.json (payload web)
"""
import base64, json, math, os, re, shutil, zipfile, zlib
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import shape, LineString

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
SITE = "West Java"; DATE = "202606"
WEST, EAST, NORTH, SOUTH = 106.30, 108.95, -5.85, -7.85          # derajat (EPSG:4326)
RES = 0.5 / 60.0                                                    # level "C" ur-scape = 0,5 menit busur (~0,93 km)
CX = int(round((EAST - WEST) / RES)); CY = int(round((NORTH - SOUTH) / RES))
EAST = WEST + CX * RES; SOUTH = NORTH - CY * RES
OUT = "urscape/out"; SITEDIR = f"{OUT}/Sites/{SITE}"
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(SITEDIR)
REPO_URL = "https://github.com/qastill/pathwaysevcharging"
SRC = "Qashtalani Haramaini - pathwaysevcharging (PLN; TTM Alyas Widita; Kontur 2023; BPS; RUPTL 2025-2034 / OSM)"
LAYERS = []   # dict(name, group, rgb, units|categories, citation, values, mask)

def cell(lon, lat):
    if not (math.isfinite(lon) and math.isfinite(lat)): return None
    x = int((lon - WEST) / RES); y = int((NORTH - lat) / RES)
    return (x, y) if 0 <= x < CX and 0 <= y < CY else None

def write_grid(L):
    fn = f"{SITEDIR}/{L['name']}_C_{SITE}@0_{DATE}_grid.csv"
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
        for fn in fs: z.write(os.path.join(dp, fn), os.path.relpath(os.path.join(dp, fn), OUT))
print("zip:", os.path.getsize("urscape/ur-scape-west-java.zip") // 1024, "KB")

# ---------------- payload web (analysis/urscape_layers.json) ----------------
# tiap layer: nilai dikuantisasi 8-bit (1..255, 0 = NoData) antara lo..hi (persentil 2-98 utk numerik), zlib+base64
print("writing web payload")
web = dict(site=SITE, west=WEST, east=EAST, north=NORTH, south=SOUTH, cx=CX, cy=CY, res=RES, source=SRC, repo=REPO_URL, generated=DATE, layers=[])
for L in LAYERS:
    v, m = L["values"], L["mask"]; vals = v[m]
    if L.get("categories"): lo, hi = 1, len(L["categories"]); q = np.where(m, v, 0).astype(np.uint8)
    else:
        lo, hi = (float(np.percentile(vals, 2)), float(np.percentile(vals, 98))) if vals.size else (0.0, 1.0)
        if hi <= lo: hi = lo + 1
        q = np.zeros((CY, CX), np.uint8); q[m] = 1 + np.clip((vals - lo) / (hi - lo) * 254, 0, 254).round().astype(np.uint8)
    raw = np.where(m, v, 0).astype(np.float32)                       # nilai asli utk hover (float32, zlib)
    web["layers"].append(dict(name=L["name"], group=L["group"], rgb=L["rgb"], units=L.get("units"), categories=L.get("categories"),
        citation=L["citation"], cells=int(m.sum()), lo=round(lo, 4), hi=round(hi, 4),
        min=round(float(vals.min()), 4) if vals.size else None, max=round(float(vals.max()), 4) if vals.size else None,
        q=base64.b64encode(zlib.compress(q.tobytes(), 9)).decode(), raw=base64.b64encode(zlib.compress(raw.tobytes(), 9)).decode()))
json.dump(web, open("analysis/urscape_layers.json", "w"), separators=(",", ":"))
print("payload:", os.path.getsize("analysis/urscape_layers.json") // 1024, "KB;", len(LAYERS), "layers")
