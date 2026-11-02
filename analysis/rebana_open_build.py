"""Statistik kecamatan/kabupaten Rebana dari data terbuka (data/open/*.tif) -> analysis/rebana_open_data.json
(dipakai analysis/rebana_territory.html). Jalankan setelah data/open/prep.py.

    python3 analysis/rebana_open_build.py
"""
import json, math, os
import numpy as np, pandas as pd, geopandas as gpd, rasterio
from shapely.geometry import shape

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = json.load(open("analysis/rebana_data.json"))
rk = pd.DataFrame(D["rk"]); rk["geometry"] = rk["geometry"].apply(shape); rk = gpd.GeoDataFrame(rk, geometry="geometry", crs="EPSG:4326")

def rd(name):
    with rasterio.open(f"data/open/{name}.tif") as s:
        a = s.read(1).astype("float64"); a[a == s.nodata] = np.nan; return a, s.transform
R = {n: rd(n)[0] for n in ["solar_pvout", "solar_ghi", "solar_dni", "solar_season_ratio", "air_temp", "elevation", "lc_crop_pct", "lc_tree_pct",
                            "lc_built_pct", "lc_grass_pct", "lc_bare_pct", "lc_water_pct", "built_2020_pct", "built_2000_pct", "built_1975_pct",
                            "pop_2025", "pop_2030", "pop_2000", "flood_rp100_max_m"] + (["wind_100m"] if os.path.exists("data/open/wind_100m.tif") else [])}
_, TR = rd("solar_pvout"); W, N, RES = TR.c, TR.f, TR.a; CY, CX = R["solar_pvout"].shape
km2 = (RES * 111320 * math.cos(math.radians(-6.8))) * (RES * 111320) / 1e6
xs = W + (np.arange(CX) + 0.5) * RES; ys = N - (np.arange(CY) + 0.5) * RES; XX, YY = np.meshgrid(xs, ys)
cells = gpd.GeoDataFrame({"row": np.repeat(np.arange(CY), CX), "col": np.tile(np.arange(CX), CY)}, geometry=gpd.points_from_xy(XX.ravel(), YY.ravel()), crs="EPSG:4326")
hit = gpd.sjoin(cells, rk[["code", "geometry"]], how="inner", predicate="within"); hit = hit[~hit.index.duplicated()]
idx = hit.row.to_numpy() * CX + hit.col.to_numpy()
flat = {k: v.ravel()[idx] for k, v in R.items()}
df = pd.DataFrame(flat); df["code"] = hit.code.to_numpy()
df["roof_mwh"] = df.lc_built_pct / 100 * km2 * 1e6 * 0.25 * 0.15 * df.solar_pvout / 1000
df["flood"] = (df.flood_rp100_max_m >= 0.5)
df["pop25_flood"] = np.where(df.flood, df.pop_2025, 0)
df["openland"] = df.lc_crop_pct + df.lc_grass_pct.fillna(0) + df.lc_bare_pct.fillna(0)
df["growth"] = df.built_2020_pct - df.built_2000_pct
df["builtkm2_20"] = df.built_2020_pct / 100 * km2; df["builtkm2_00"] = df.built_2000_pct / 100 * km2; df["builtkm2_75"] = df.built_1975_pct / 100 * km2
# kelayakan PLTS utilitas (sama dengan urscape/build.py): skor >= 70 dan lahan terbuka >= 50%, terbangun < 20%, air < 10%, pohon < 30%
pv = df.solar_pvout; lo, hi = np.nanpercentile(pv, 2), np.nanpercentile(pv, 98); pvn = np.clip((pv - lo) / (hi - lo), 0, 1)
dgi = rk.set_index("code").d_gi.reindex(df.code).to_numpy(); near = np.clip(1 - dgi / 15, 0, 1)
df["score"] = 100 * (0.35 * pvn + 0.30 * np.clip(df.openland / 100, 0, 1) + 0.15 * (~df.flood) + 0.20 * near)
df["suit"] = (df.openland >= 50) & (df.lc_built_pct < 20) & (df.lc_water_pct.fillna(0) < 10) & (df.lc_tree_pct.fillna(0) < 30)
df["suit70km2"] = np.where(df.suit & (df.score >= 70), km2, 0)
df["mw_suit"] = df.suit70km2 * 100 * 0.5   # ~1 MWp per ha = 100 MWp/km2; asumsi hanya 50% lahan layak benar-benar bisa dipakai

agg = df.groupby("code").agg(cells=("code", "size"), pvout=("solar_pvout", "mean"), ghi=("solar_ghi", "mean"), dni=("solar_dni", "mean"), season=("solar_season_ratio", "mean"),
    temp=("air_temp", "mean"), ele=("elevation", "mean"), crop=("lc_crop_pct", "mean"), tree=("lc_tree_pct", "mean"), built21=("lc_built_pct", "mean"),
    built20=("built_2020_pct", "mean"), built00=("built_2000_pct", "mean"), built75=("built_1975_pct", "mean"), bkm2_20=("builtkm2_20", "sum"), bkm2_00=("builtkm2_00", "sum"), bkm2_75=("builtkm2_75", "sum"),
    pop25=("pop_2025", "sum"), pop30=("pop_2030", "sum"), pop00=("pop_2000", "sum"), roof_gwh=("roof_mwh", lambda x: x.sum() / 1000),
    flood_share=("flood", "mean"), pop25_flood=("pop25_flood", "sum"), suit70km2=("suit70km2", "sum"), mw_suit=("mw_suit", "sum"),
    **({"wind": ("wind_100m", "mean")} if "wind_100m" in df else {}))
agg["area_km2"] = agg.cells * km2
agg = agg.join(rk.set_index("code")[["kec", "kab", "pop", "ch", "kpi", "priority", "d_gi", "gi", "gi_head", "t_mean", "lo", "la", "ipm", "pov"]])
agg["pop_ch_25_30"] = 100 * (agg.pop30 - agg.pop25) / agg.pop25; agg["pop_ch_00_25"] = 100 * (agg.pop25 - agg.pop00) / agg.pop00
agg["flood_pop_share"] = 100 * agg.pop25_flood / agg.pop25
agg["growth_pp"] = agg.built20 - agg.built00
agg["roof_gwh_per_1000"] = 1000 * agg.roof_gwh / agg.pop25
agg = agg.round(2)
kab = agg.groupby("kab").agg(kec=("kec", "size"), area_km2=("area_km2", "sum"), pop25=("pop25", "sum"), pop30=("pop30", "sum"), pop00=("pop00", "sum"),
    pvout=("pvout", "mean"), ghi=("ghi", "mean"), roof_gwh=("roof_gwh", "sum"), bkm2_20=("bkm2_20", "sum"), bkm2_00=("bkm2_00", "sum"), bkm2_75=("bkm2_75", "sum"),
    pop25_flood=("pop25_flood", "sum"), suit70km2=("suit70km2", "sum"), mw_suit=("mw_suit", "sum"), crop=("crop", "mean"), ch=("ch", "sum"))
kab["flood_pop_share"] = 100 * kab.pop25_flood / kab.pop25; kab["pop_ch_25_30"] = 100 * (kab.pop30 - kab.pop25) / kab.pop25
kab["pop_ch_00_25"] = 100 * (kab.pop25 - kab.pop00) / kab.pop00; kab["built_growth_pct"] = 100 * (kab.bkm2_20 - kab.bkm2_00) / kab.bkm2_00
kab = kab.round(2)
tot = dict(area_km2=float(agg.area_km2.sum()), pop25=float(agg.pop25.sum()), pop30=float(agg.pop30.sum()), pop00=float(agg.pop00.sum()),
    pvout=float(df.solar_pvout.mean()), ghi=float(df.solar_ghi.mean()), pvout_min=float(df.solar_pvout.min()), pvout_max=float(df.solar_pvout.max()),
    roof_gwh=float(df.roof_mwh.sum() / 1000), bkm2_20=float(df.builtkm2_20.sum()), bkm2_00=float(df.builtkm2_00.sum()), bkm2_75=float(df.builtkm2_75.sum()),
    flood_km2=float(df.flood.sum() * km2), pop25_flood=float(df.pop25_flood.sum()), suit70km2=float(df.suit70km2.sum()), mw_suit=float(df.mw_suit.sum()),
    crop=float(df.lc_crop_pct.mean()), tree=float(df.lc_tree_pct.mean()), built21=float(df.lc_built_pct.mean()), season=float(df.solar_season_ratio.mean()), temp=float(df.air_temp.mean()),
    wind=float(df.wind_100m.mean()) if "wind_100m" in df else None)
# aset di zona banjir: SPKLU (register nasional) & GI
sp = pd.read_excel("SPKLU_Indonesia_Lengkap_2026-06-08.xlsx", sheet_name=0)
sp["Latitude"] = pd.to_numeric(sp["Latitude"], errors="coerce"); sp["Longitude"] = pd.to_numeric(sp["Longitude"], errors="coerce"); sp = sp.dropna(subset=["Latitude", "Longitude"])
def at(a, lon, lat):
    x = int((lon - W) / RES); y = int((N - lat) / RES)
    return float(a[y, x]) if 0 <= x < CX and 0 <= y < CY and np.isfinite(a[y, x]) else None
REB = rk.geometry.buffer(0).unary_union
sp = sp[[REB.contains(g) for g in gpd.points_from_xy(sp.Longitude, sp.Latitude)]].copy()
sp["flood_m"] = [at(R["flood_rp100_max_m"], lo, la) for lo, la in zip(sp.Longitude, sp.Latitude)]
sp["pvout"] = [at(R["solar_pvout"], lo, la) for lo, la in zip(sp.Longitude, sp.Latitude)]
sp_fl = sp[sp.flood_m.fillna(0) >= 0.5][["Nama SPKLU", "Alamat", "Jumlah Charger", "Latitude", "Longitude", "flood_m"]].rename(columns={"Nama SPKLU": "name", "Alamat": "addr", "Jumlah Charger": "chg", "Latitude": "la", "Longitude": "lo"})
gi = pd.DataFrame(D["grid"]["gi"]); gi = gi[[REB.contains(g) for g in gpd.points_from_xy(gi.lo, gi.la)]].copy()
gi["flood_m"] = [at(R["flood_rp100_max_m"], lo, la) for lo, la in zip(gi.lo, gi.la)]
gi_fl = gi[gi.flood_m.fillna(0) >= 0.5][["name", "mva", "lo", "la", "flood_m"]]
gnc = agg[(agg.t_mean > 30) & (agg.growth_pp > 0.3)].sort_values("growth_pp", ascending=False)[["kec", "kab", "growth_pp", "t_mean", "pop25", "pop_ch_25_30"]]
out = dict(cell_km2=km2, totals=tot, growth_nocharge=gnc.reset_index().to_dict("records"), kab=kab.reset_index().to_dict("records"), kec=agg.reset_index().to_dict("records"),
           spklu_in_rebana=int(len(sp)), spklu_flood=sp_fl.round(2).to_dict("records"), gi_in_rebana=int(len(gi)), gi_flood=gi_fl.round(2).to_dict("records"),
           spklu_pvout_mean=float(sp.pvout.mean()),
           assumptions=dict(roof="built-up area (WorldCover 2021) x 25% usable roof x 0.15 kWp/m2 x PVOUT", utility="score >= 70 on open land (crop/grass/bare >= 50%, built < 20%, water < 10%, tree < 30%); 1 MWp/ha x 50% usable",
                            flood="JRC Global Flood Hazard RP100 river flood depth >= 0.5 m (no coastal flooding, no defences)"))
json.dump(out, open("analysis/rebana_open_data.json", "w"), default=lambda o: None if (isinstance(o, float) and math.isnan(o)) else (o.item() if hasattr(o, "item") else str(o)))
print(json.dumps(tot, indent=1)); print(kab[["kec", "pop25", "pop_ch_25_30", "pvout", "roof_gwh", "flood_pop_share", "suit70km2", "mw_suit", "built_growth_pct"]])
print("spklu flood", len(sp_fl), "/", len(sp), "; gi flood", len(gi_fl), "/", len(gi))
