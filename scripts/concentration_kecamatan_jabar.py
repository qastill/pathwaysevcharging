"""Indeks konsentrasi SPKLU Jawa Barat pada tingkat KECAMATAN dan kab/kota dengan sosial-ekonomi BPS.

    pip install numpy pandas openpyxl shapely h3
    python3 scripts/concentration_kecamatan_jabar.py [--raw DIR]
        -> analysis/concentration_kecamatan_jabar.json / .md
           data/jabar_kecamatan_spklu.geojson        (poligon kecamatan + indikator, untuk peta)
           equitymap/input/jabar_sosek_kabkota.csv   (salinan BPS 2024, 27 kab/kota)
           equitymap/input/jabar_kecamatan.csv       (tabel kecamatan hasil olahan)

Sumber (semua diunduh dari cermin GitHub/S3 karena portal BPS/HDX tidak terjangkau dari lingkungan ini):
  * Batas desa Jawa Barat HDX-BPS 2020 → JfrAziz/indonesia-district, id32_jawa_barat_district.geojson;
    desa digabung (dissolve) menjadi 630 kecamatan menurut district_code.
  * Penduduk Kontur 2023 H3 res 8 (≈0,74 km²), kontur_population_ID_20231101.gpkg → titik pusat heksagon
    dijatuhkan ke poligon kecamatan.
  * Sosial-ekonomi kab/kota BPS 2024 (IPM, pengeluaran per kapita disesuaikan, P0) → tabel olahan
    MercyCantik/UAS-VISDAT-222313205 data/processed/profil_kabkota.csv (BPS Query Builder 2024).
  * SPKLU: Master SPKLU Maret 2026 (636 charger), Rekap_SPKLU_Jabar_ArcGIS.csv (331 SPKLU bertransaksi),
    Data pelanggan EV.txt (pengajuan home-charger status Selesai, titik koordinat).

Catatan metodologis — apa yang DIAM-DIAM diandaikan:
  * Tidak ada data pendapatan/kemiskinan resmi per kecamatan. Peringkat sosial-ekonomi kecamatan di sini
    adalah nilai kab/kota induknya (semua kecamatan di satu kab/kota berbagi peringkat; ikatan ditangani lewat
    rata-rata peringkat tertimbang). Jadi CI~pengeluaran pada tingkat kecamatan mengukur gradien ANTAR kab/kota
    dengan penyebut penduduk yang lebih halus, bukan gradien kaya-miskin di dalam kota.
  * Gradien DALAM kab/kota dipakai dua proksi per kecamatan: kepadatan penduduk dan pemilik EV per 100 rb.
  * Kecamatan tanpa penduduk Kontur (waduk, hutan) dibuang dari CI.
"""
import argparse, csv, json, os, re, warnings
import numpy as np
import pandas as pd
from shapely.geometry import shape, Point, mapping
from shapely.ops import unary_union
from shapely.strtree import STRtree

from concentration_lib import ci, ci_boot, conc_stats, curve, gini

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
ap = argparse.ArgumentParser()
ap.add_argument("--raw", default=os.environ.get("CONC_RAW", os.path.join(HERE, "..", "equitymap", "input", "raw")))
RAW = ap.parse_args().raw
IN = os.path.join("equitymap", "input")
SOSEK_OUT = os.path.join(IN, "jabar_sosek_kabkota.csv")
KEC_OUT = os.path.join(IN, "jabar_kecamatan.csv")
KONTUR_OUT = os.path.join(IN, "kontur_jabar_r8.csv")


def norm_kab(s):
    s = re.sub(r"^\d+\s*-\s*", "", str(s).upper()).replace("KOTA.", "KOTA").replace("KAB.", "KAB").strip()
    s = re.sub(r"\s+", " ", s)
    return s if s.startswith("KOTA ") else ("KAB " + s if not s.startswith("KAB ") else s)


def kab_from_hdx(name):  # "Kota Depok" / "Bogor"
    return norm_kab(name if name.startswith("Kota ") else "KAB " + name)


# ------------------------------------------------------------------ 1) poligon kecamatan (dissolve desa HDX)
raw_geo = os.path.join(RAW, "kec_jabar.geojson")
g = json.load(open(raw_geo, encoding="utf-8"))
parts = {}
for f in g["features"]:
    p = f["properties"]
    k = p["district_code"]
    parts.setdefault(k, dict(code=k, kec=p["district"], kab=p["regency"], geoms=[]))["geoms"].append(shape(f["geometry"]))
kecs = []
for k, d in parts.items():
    geom = unary_union(d["geoms"]).buffer(0)
    kecs.append(dict(code=d["code"], kec=d["kec"], kab_hdx=d["kab"], kab=kab_from_hdx(d["kab"]), geom=geom))
kecs = [k for k in kecs if k["kab_hdx"] != "Waduk Cirata"]  # badan air lintas-kabupaten, bukan kecamatan
geoms = [k["geom"] for k in kecs]
tree = STRtree(geoms)


def assign(lat, lng):
    """Indeks kecamatan untuk tiap titik; titik di luar poligon → kecamatan terdekat ≤ 2 km, selain itu -1."""
    out = np.full(len(lat), -1)
    pts = [Point(x, y) for x, y in zip(lng, lat)]
    for i, pt in enumerate(pts):
        if np.isnan(pt.x) or np.isnan(pt.y):
            continue
        cand = tree.query(pt, predicate="within")
        if len(cand):
            out[i] = cand[0]; continue
        j = tree.nearest(pt)
        if geoms[j].distance(pt) < 0.018:
            out[i] = j
    return out


# ------------------------------------------------------------------ 2) penduduk Kontur r8
kon = pd.read_csv(os.path.join(RAW, "kontur_jabar_r8.csv"))
kon["kec"] = assign(kon["lat"].to_numpy(), kon["lng"].to_numpy())
kon = kon[kon["kec"] >= 0]
kon.to_csv(KONTUR_OUT, index=False)
pop = kon.groupby("kec")["pop"].sum()

# ------------------------------------------------------------------ 3) SPKLU, transaksi, pemilik EV
master = pd.read_excel("Master SPKLU Maret 2026.xlsx")
master = master[master["PROVINSI"].astype(str).str.upper().str.contains("JAWA BARAT")].copy()
master["kw"] = master["KW"].astype(str).str.extract(r"([\d.]+)")[0].astype(float)
master["kec"] = assign(master["LATITUDE"].astype(float).to_numpy(), master["LONGITUDE"].astype(float).to_numpy())
rekap = pd.read_csv("Rekap_SPKLU_Jabar_ArcGIS.csv", encoding="utf-8-sig")
rekap["kec"] = assign(rekap["Latitude"].to_numpy(), rekap["Longitude"].to_numpy())
ev = pd.read_csv("Data pelanggan EV.txt", sep=None, engine="python", encoding="latin-1")
ev = ev[ev["Provinsi"].astype(str).str.contains("JAWA BARAT", case=False) & (ev["Status Approval"].astype(str).str.strip() == "Selesai")].copy()
ev["kec"] = assign(pd.to_numeric(ev["Lat"], errors="coerce").to_numpy(), pd.to_numeric(ev["Long"], errors="coerce").to_numpy())
lost = dict(charger=int((master["kec"] < 0).sum()), spklu_trx=int((rekap["kec"] < 0).sum()), ev=int((ev["kec"] < 0).sum()))

# ------------------------------------------------------------------ 4) sosial-ekonomi kab/kota BPS 2024
sos = pd.read_csv(os.path.join(RAW, "profil_kabkota.csv"))
sos = sos[sos["provinsi"] == "Jawa Barat"][["kode_wilayah", "nama_wilayah", "ipm", "pengeluaran", "miskin_p0", "kedalaman_p1", "uhh", "hls", "rls", "penduduk"]].copy()
sos["kab"] = sos["nama_wilayah"].map(lambda n: norm_kab(n if n.startswith("Kota ") else "KAB " + n))
sos.rename(columns={"penduduk": "penduduk_bps"}).to_csv(SOSEK_OUT, index=False)
sos = sos.set_index("kab")
assert len(sos) == 27

# ------------------------------------------------------------------ 5) tabel kecamatan
rows = []
for i, k in enumerate(kecs):
    lat0 = k["geom"].centroid.y
    area = k["geom"].area * (111.32 ** 2) * np.cos(np.radians(lat0))
    m = master[master["kec"] == i]; r = rekap[rekap["kec"] == i]; e = ev[ev["kec"] == i]
    s = sos.loc[k["kab"]]
    rows.append(dict(code=k["code"], kecamatan=k["kec"], kab=k["kab"], pop=float(pop.get(i, 0.0)), area_km2=area,
                     chargers=len(m), kw=float(m["kw"].sum()), sites=int(m["LOKASI"].nunique()), pln=int((m["MILIK"] == "PLN").sum()),
                     spklu_trx=len(r), kwh=float(r["Energi_kWh"].sum()), trx=int(r["Jml_Transaksi"].sum()), ev_owner=len(e),
                     ipm=float(s["ipm"]), expend=float(s["pengeluaran"]), poverty=float(s["miskin_p0"])))
kec = pd.DataFrame(rows)
kec["density"] = kec["pop"] / kec["area_km2"].clip(lower=0.01)
kec["ev_per100k"] = np.where(kec["pop"] > 0, 1e5 * kec["ev_owner"] / kec["pop"].clip(lower=1), 0)
kec["chargers_per100k"] = np.where(kec["pop"] > 0, 1e5 * kec["chargers"] / kec["pop"].clip(lower=1), 0)
kec.round(3).to_csv(KEC_OUT, index=False)
K = kec[kec["pop"] >= 500].reset_index(drop=True)      # buang kecamatan tanpa penduduk berarti (waduk/hutan)
w = K["pop"].to_numpy(float)

# ------------------------------------------------------------------ 6) kab/kota dengan SES asli (27 unit; penduduk dari Kontur r8)
kab = kec.groupby("kab").agg(pop=("pop", "sum"), chargers=("chargers", "sum"), kw=("kw", "sum"), kwh=("kwh", "sum"), trx=("trx", "sum"),
                             ev_owner=("ev_owner", "sum"), area_km2=("area_km2", "sum"), n_kec=("code", "size"),
                             kec_with_charger=("chargers", lambda x: int((x > 0).sum()))).reset_index()
kab = kab.merge(sos.reset_index()[["kab", "nama_wilayah", "ipm", "pengeluaran", "miskin_p0"]], on="kab")
kab["density"] = kab["pop"] / kab["area_km2"]; kab["per100k"] = 1e5 * kab["chargers"] / kab["pop"]
kab["ev_per100k"] = 1e5 * kab["ev_owner"] / kab["pop"]
wk = kab["pop"].to_numpy(float)
ranks_kab = {"Pengeluaran per kapita (BPS 2024)": kab["pengeluaran"].to_numpy(float), "IPM (BPS 2024)": kab["ipm"].to_numpy(float),
             "Kemiskinan P0, dibalik (miskin → kaya)": -kab["miskin_p0"].to_numpy(float),
             "Kepadatan penduduk": kab["density"].to_numpy(float), "Pemilik EV per 100 rb": kab["ev_per100k"].to_numpy(float)}
outs = {"Jumlah charger": "chargers", "Kapasitas (kW)": "kw", "Energi Mar-2026 (kWh)": "kwh", "Transaksi Mar-2026": "trx"}
B_kab = [dict(level="kab/kota", rank=rl, outcome=ol, **ci_boot(kab[oc].to_numpy(float), rv, wk)) for rl, rv in ranks_kab.items() for ol, oc in outs.items()]
curves_kab = {rl: {oc: curve(kab[oc].to_numpy(float), rv, wk) for oc in ("chargers", "kwh")} for rl, rv in ranks_kab.items()}

# ------------------------------------------------------------------ 7) kecamatan
ranks_kec = {"Pengeluaran per kapita kab/kota induk": K["expend"].to_numpy(float), "IPM kab/kota induk": K["ipm"].to_numpy(float),
             "Kemiskinan kab/kota induk, dibalik": -K["poverty"].to_numpy(float),
             "Kepadatan penduduk kecamatan": K["density"].to_numpy(float), "Pemilik EV per 100 rb kecamatan": K["ev_per100k"].to_numpy(float)}
B_kec = [dict(level="kecamatan", rank=rl, outcome=ol, **ci_boot(K[oc].to_numpy(float), rv, w)) for rl, rv in ranks_kec.items() for ol, oc in outs.items()]
curves_kec = {rl: {oc: curve(K[oc].to_numpy(float), rv, w, npts=60) for oc in ("chargers", "kwh")} for rl, rv in ranks_kec.items()}

# kuintil kecamatan menurut pengeluaran kab induk (tertimbang penduduk) dan menurut kepadatan
def quintiles(key, label):
    o = np.argsort(K[key].to_numpy(float), kind="stable"); cum = np.cumsum(w[o]) / w.sum(); out = []
    for q in range(5):
        sel = o[(cum > q / 5) & (cum <= (q + 1) / 5)] if q else o[cum <= .2]
        if not len(sel): continue
        P = w[sel].sum(); sub = K.iloc[sel]
        out.append(dict(q=q + 1, by=label, n_kec=int(len(sel)), pop=round(float(P)), chargers=int(sub["chargers"].sum()),
                        per100k=round(1e5 * sub["chargers"].sum() / P, 2), kwh_per_capita=round(float(sub["kwh"].sum() / P), 4),
                        pop_no_charger_pct=round(100 * float(w[sel][sub["chargers"].to_numpy() == 0].sum() / P), 1),
                        ev_per100k=round(1e5 * sub["ev_owner"].sum() / P, 2),
                        mean_key=round(float(np.average(K[key].to_numpy(float)[sel], weights=w[sel])), 2)))
    return out
quint = quintiles("expend", "pengeluaran kab induk") + quintiles("density", "kepadatan kecamatan")

# CI dalam-kab/kota (kab dengan ≥8 kecamatan berpenduduk dan ≥5 charger), peringkat kepadatan & pemilik EV
within = []
for name, sub in K.groupby("kab"):
    if len(sub) < 8 or sub["chargers"].sum() < 5: continue
    ws = sub["pop"].to_numpy(float)
    within.append(dict(kab=name, nama=sos.loc[name, "nama_wilayah"], n_kec=int(len(sub)), chargers=int(sub["chargers"].sum()),
                       kec_with_charger=int((sub["chargers"] > 0).sum()),
                       ci_chargers_density=round(ci(sub["chargers"].to_numpy(float), sub["density"].to_numpy(float), ws), 3),
                       ci_kwh_density=round(ci(sub["kwh"].to_numpy(float), sub["density"].to_numpy(float), ws), 3) if sub["kwh"].sum() > 0 else None,
                       ci_chargers_ev=round(ci(sub["chargers"].to_numpy(float), sub["ev_per100k"].to_numpy(float), ws), 3),
                       gini_chargers=round(gini(sub["chargers_per100k"].to_numpy(float)), 3)))
within.sort(key=lambda x: -x["chargers"])

# konsentrasi pasokan antar-kecamatan
A = dict(kec_chargers=conc_stats(K["chargers"]), kec_kwh=conc_stats(K["kwh"]), kec_pop=conc_stats(K["pop"]), kec_ev=conc_stats(K["ev_owner"]),
         n_kec=int(len(K)), n_kec_with_charger=int((K["chargers"] > 0).sum()), n_kec_with_trx=int((K["spklu_trx"] > 0).sum()),
         pop_in_kec_with_charger_pct=round(100 * float(w[K["chargers"].to_numpy() > 0].sum() / w.sum()), 1),
         pop_in_kec_with_ev_pct=round(100 * float(w[K["ev_owner"].to_numpy() > 0].sum() / w.sum()), 1),
         top10_kwh=[dict(kecamatan=r.kecamatan, kab=r.kab, kwh=round(r.kwh), share=round(r.kwh / K["kwh"].sum(), 4), pop=round(r.pop)) for r in K.sort_values("kwh", ascending=False).head(10).itertuples()],
         top10_chargers=[dict(kecamatan=r.kecamatan, kab=r.kab, chargers=int(r.chargers), pop=round(r.pop)) for r in K.sort_values("chargers", ascending=False).head(10).itertuples()],
         ev_no_charger=[dict(kecamatan=r.kecamatan, kab=r.kab, ev_owner=int(r.ev_owner), pop=round(r.pop)) for r in K[K["chargers"] == 0].sort_values("ev_owner", ascending=False).head(10).itertuples()])

out = dict(meta=dict(periode="Maret 2026", n_kecamatan=int(len(kec)), n_kecamatan_analisis=int(len(K)), n_kab=27,
                     pop_kontur=round(float(kec["pop"].sum())), n_charger=int(len(master)), n_spklu_trx=int(len(rekap)), n_ev=int(len(ev)),
                     titik_tak_terpetakan=lost, sosek="BPS 2024 kab/kota (IPM, pengeluaran per kapita disesuaikan ribu Rp/th, P0 %)",
                     catatan="SES kecamatan = nilai kab/kota induk (tidak ada data resmi per kecamatan)."),
           A=A, B_kab=B_kab, B_kec=B_kec, curves_kab=curves_kab, curves_kec=curves_kec, quintiles=quint, within=within,
           kab=kab.round(3).to_dict("records"))
json.dump(out, open("analysis/concentration_kecamatan_jabar.json", "w"), ensure_ascii=False, indent=1)

# GeoJSON kecamatan untuk peta (disederhanakan)
feats = []
for i, k in enumerate(kecs):
    r = kec.iloc[i]
    gm = k["geom"].simplify(0.0015, preserve_topology=True)
    feats.append(dict(type="Feature", geometry=mapping(gm), properties=dict(
        code=k["code"], kec=k["kec"], kab=sos.loc[k["kab"], "nama_wilayah"], pop=round(float(r["pop"])), dens=round(float(r["density"]), 1),
        ch=int(r["chargers"]), kw=round(float(r["kw"])), kwh=round(float(r["kwh"])), trx=int(r["trx"]), ev=int(r["ev_owner"]),
        ipm=r["ipm"], exp=r["expend"], pov=r["poverty"])))
json.dump(dict(type="FeatureCollection", features=feats), open("data/jabar_kecamatan_spklu.geojson", "w"), separators=(",", ":"))

# ------------------------------------------------------------------ ringkasan markdown
L = ["# Indeks konsentrasi SPKLU Jawa Barat — tingkat kecamatan (Maret 2026)", "",
     f"{len(kec)} kecamatan (dissolve desa HDX-BPS 2020), {len(K)} berpenduduk ≥500 jiwa Kontur 2023; {len(master)} charger, "
     f"{len(rekap)} SPKLU bertransaksi, {len(ev)} pemilik EV; titik tak terpetakan: {lost}.", "",
     f"Charger ada di **{A['n_kec_with_charger']}** kecamatan ({A['pop_in_kec_with_charger_pct']} % penduduk); pemilik EV ada di "
     f"{(K['ev_owner'] > 0).sum()} kecamatan ({A['pop_in_kec_with_ev_pct']} % penduduk).", "",
     "## Konsentrasi pasokan antar-kecamatan", "", "| Dimensi | n>0 | HHI | N efektif | CR10 | Gini |", "|---|---|---|---|---|---|"]
for lab, key in (("Charger", "kec_chargers"), ("kWh", "kec_kwh"), ("Pemilik EV", "kec_ev"), ("Penduduk (pembanding)", "kec_pop")):
    s = A[key]; L.append(f"| {lab} | {s['n']} | {s['hhi']:.0f} | {s['n_effective']} | {s['cr10']:.1%} | {s['gini']} |")
for title, B in (("## CI kab/kota (27 unit, SES BPS 2024; * = 95 % CI tidak melewati 0)", B_kab), ("## CI kecamatan (SES = kab/kota induk)", B_kec)):
    L += ["", title, "", "| Peringkat r | Pasokan | CI | 95 % CI |", "|---|---|---|---|"]
    for b in B:
        L.append(f"| {b['rank']} | {b['outcome']} | {b['ci']:+.3f}{'*' if b['signif'] else ''} | [{b['lo']:+.3f}, {b['hi']:+.3f}] |")
L += ["", "## Kuintil kecamatan (tertimbang penduduk)", "", "| Dasar | Q | n kec | Penduduk | Charger/100 rb | kWh/kapita | % penduduk di kec tanpa charger | EV/100 rb |", "|---|---|---|---|---|---|---|---|"]
for q in quint:
    L.append(f"| {q['by']} | Q{q['q']} | {q['n_kec']} | {q['pop']:,} | {q['per100k']} | {q['kwh_per_capita']} | {q['pop_no_charger_pct']} | {q['ev_per100k']} |")
L += ["", "## CI dalam kab/kota (kecamatan diurut kepadatan / pemilik EV)", "", "| Kab/kota | n kec | charger | kec berisi | CI charger~kepadatan | CI kWh~kepadatan | CI charger~EV | Gini charger/100 rb |", "|---|---|---|---|---|---|---|---|"]
for x in within:
    L.append(f"| {x['nama']} | {x['n_kec']} | {x['chargers']} | {x['kec_with_charger']} | {x['ci_chargers_density']:+.3f} | {x['ci_kwh_density'] if x['ci_kwh_density'] is None else format(x['ci_kwh_density'], '+.3f')} | {x['ci_chargers_ev']:+.3f} | {x['gini_chargers']} |")
open("analysis/concentration_kecamatan_jabar.md", "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L))
