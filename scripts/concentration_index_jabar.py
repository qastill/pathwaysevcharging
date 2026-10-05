"""Indeks konsentrasi SPKLU Jawa Barat (Maret 2026).

    pip install numpy pandas openpyxl
    python3 scripts/concentration_index_jabar.py        # -> analysis/concentration_jabar.json + .md

Dua keluarga ukuran, sengaja dipisah:

  A. KONSENTRASI PASOKAN/PASAR — seberapa terpusat pasokan pada sedikit pemain/lokasi.
     HHI (0–10.000), CR4/CR10, ukuran efektif 1/HHI, Gini–Lorenz. Unit: SPKLU, pemilik (PLN/mitra), merek charger,
     jenis lokasi, UP3, kab/kota.

  B. INDEKS KONSENTRASI (Wagstaff/Kakwani): unit diurutkan menurut variabel peringkat r (rendah → tinggi), kurva
     konsentrasi L(p) = porsi kumulatif pasokan terhadap porsi kumulatif penduduk, C = 1 − 2·∫L dp.
     C > 0: pasokan menumpuk di unit ber-r tinggi; C < 0: di unit ber-r rendah; C = 0: tidak terkait r.
     Dihitung dengan rumus kovarians tertimbang  C = 2·cov_w(h, rank_w) / mean_w(h)  (identik dengan integral
     trapesium untuk data diskret tanpa ikatan; ikatan ditangani lewat rank tengah-kelompok), plus selang
     kepercayaan bootstrap 95 % (resampling unit).

Variabel peringkat r yang TERSEDIA di repo untuk Jabar: kepadatan penduduk (gradien urban) dan intensitas
kepemilikan EV (pengajuan home-charger berstatus 'Selesai' per 100 rb penduduk). IPM / kemiskinan / pengeluaran
BPS tingkat kab/kota Jabar BELUM ada di repo — CI sosial-ekonomi menunggu berkas itu (lihat catatan di keluaran).
"""
import json, os, re, warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
RNG = np.random.default_rng(2026)
N_BOOT = 2000


def norm(s):
    s = str(s).upper()
    s = re.sub(r"^\d+\s*-\s*", "", s)             # kode "3201 - KAB. BOGOR"
    s = s.replace("KOTA.", "KOTA").replace("KAB.", "KAB").strip()
    s = re.sub(r"\s+", " ", s)
    # Kota Cimahi tak punya heksagon penduduk sendiri (terserap ke Kota Bandung) -> satu unit analisis
    return "KOTA BANDUNG" if s == "KOTA CIMAHI" else s


# ------------------------------------------------------------------ ukuran
def hhi(shares):
    s = np.asarray(shares, float); s = s[s > 0] / s.sum()
    return float(np.sum(s ** 2) * 10000)


def conc_stats(values, labels=None):
    v = np.asarray(values, float); v = v[v > 0]
    s = np.sort(v)[::-1] / v.sum()
    h = hhi(s)
    return dict(n=int(len(v)), hhi=round(h, 1), n_effective=round(10000 / h, 2), cr1=round(float(s[:1].sum()), 4),
                cr4=round(float(s[:4].sum()), 4), cr10=round(float(s[:10].sum()), 4), gini=round(gini(v), 3))


def gini(v):
    v = np.sort(np.asarray(v, float)); n = len(v)
    return float((2 * np.sum((np.arange(1, n + 1)) * v) / (n * v.sum())) - (n + 1) / n)


def _ranks(r, w):
    """Peringkat fraksional tertimbang (titik tengah kelompok sama-r) pada [0,1]."""
    o = np.argsort(r, kind="stable"); rs = r[o]; ws = w[o]
    cum = np.cumsum(ws) / ws.sum()
    mid = cum - ws / ws.sum() / 2
    out = np.empty_like(mid)
    i = 0
    while i < len(rs):                              # ikatan -> rata-rata tertimbang peringkat
        j = i
        while j + 1 < len(rs) and rs[j + 1] == rs[i]:
            j += 1
        out[i:j + 1] = np.average(mid[i:j + 1], weights=ws[i:j + 1]); i = j + 1
    res = np.empty_like(out); res[o] = out
    return res


def ci(h, r, w):
    """Indeks konsentrasi tertimbang. h = pasokan per unit (total), r = variabel peringkat, w = penduduk."""
    h, r, w = (np.asarray(x, float) for x in (h, r, w))
    if h.sum() <= 0:
        return float("nan")
    R = _ranks(r, w)
    # h_i/w_i = pasokan per kapita; mean_w(per kapita) = total/penduduk
    pc = h / w
    mu = np.sum(w * pc) / w.sum()
    cov = np.sum(w * (pc - mu) * (R - np.sum(w * R) / w.sum())) / w.sum()
    return float(2 * cov / mu)


def ci_boot(h, r, w):
    est = ci(h, r, w); n = len(h); b = []
    for _ in range(N_BOOT):
        ix = RNG.integers(0, n, n)
        if len(np.unique(r[ix])) < 3 or h[ix].sum() <= 0:
            continue
        b.append(ci(h[ix], r[ix], w[ix]))
    lo, hi = np.percentile(b, [2.5, 97.5])
    return dict(ci=round(est, 3), lo=round(float(lo), 3), hi=round(float(hi), 3),
                signif=bool(lo > 0 or hi < 0))


def curve(h, r, w, npts=30):
    o = np.argsort(r, kind="stable"); w, h = np.asarray(w, float)[o], np.asarray(h, float)[o]
    cp = np.concatenate([[0], np.cumsum(w) / w.sum()]); cv = np.concatenate([[0], np.cumsum(h) / max(h.sum(), 1e-9)])
    return [[round(float(a), 4), round(float(b), 4)] for a, b in zip(cp, cv)]


# ------------------------------------------------------------------ data
master = pd.read_excel("Master SPKLU Maret 2026.xlsx")
master = master[master["PROVINSI"].astype(str).str.upper().str.contains("JAWA BARAT")].copy()
master["kab"] = master["KOTA/KAB"].map(norm)
master["kw"] = master["KW"].astype(str).str.extract(r"([\d.]+)")[0].astype(float)
master["merek"] = master["MEREK"].astype(str).str.replace(r"^\d+\.\s*", "", regex=True).str.strip()

rekap = pd.read_csv("Rekap_SPKLU_Jabar_ArcGIS.csv", encoding="utf-8-sig")
rekap["kab"] = rekap["Kota_Kab"].map(norm)

ev = pd.read_csv("Data pelanggan EV.txt", sep=None, engine="python", encoding="latin-1")
ev = ev[ev["Provinsi"].astype(str).str.contains("JAWA BARAT", case=False)].copy()
ev["kab"] = ev["Kabupaten"].map(norm)
ev["kec"] = ev["Kecamatan"].astype(str)
ev_done = ev[ev["Status Approval"].astype(str).str.strip() == "Selesai"]

js = open("equitymap/equity.js", encoding="utf-8").read()
E = json.loads(js[len("window.EQUITY="):].rstrip(";\n"))
pv = [p["name"] for p in E["provs"]]
kabs = [k for k in E["kab_stats"] if pv[k["prov"]] == "Jawa Barat"]


def kab_key(n):
    n = n.upper().strip()
    return ("KOTA " + n[5:]) if n.startswith("KOTA ") else "KAB " + n


unit = pd.DataFrame([dict(kab=kab_key(k["name"]), nama=k["name"], pop=k["pop"], hex=k["hex"]) for k in kabs])
assert len(unit) == 26, len(unit)
unit["density"] = unit["pop"] / unit["hex"].clip(lower=1)
g = master.groupby("kab")
unit["chargers"] = unit["kab"].map(g.size()).fillna(0)
unit["kw"] = unit["kab"].map(g["kw"].sum()).fillna(0)
unit["connectors"] = unit["kab"].map(g["JML KONEKTOR"].sum()).fillna(0)
unit["sites"] = unit["kab"].map(g["LOKASI"].nunique()).fillna(0)
gr = rekap.groupby("kab")
unit["kwh"] = unit["kab"].map(gr["Energi_kWh"].sum()).fillna(0)
unit["trx"] = unit["kab"].map(gr["Jml_Transaksi"].sum()).fillna(0)
unit["ev_owner"] = unit["kab"].map(ev_done.groupby("kab").size()).fillna(0)
unit["ev_per100k"] = 1e5 * unit["ev_owner"] / unit["pop"]
miss = set(master["kab"]) - set(unit["kab"])
assert not miss, miss

# ------------------------------------------------------------------ A. konsentrasi pasar/pasokan
A = {}
A["spklu_kwh"] = conc_stats(rekap["Energi_kWh"]); A["spklu_trx"] = conc_stats(rekap["Jml_Transaksi"])
top = rekap.sort_values("Energi_kWh", ascending=False).head(10)
A["top10_spklu"] = [dict(nama=r.Nama_SPKLU, kab=r.Kota_Kab, kwh=round(r.Energi_kWh), share=round(r.Energi_kWh / rekap.Energi_kWh.sum(), 4))
                    for r in top.itertuples()]
A["top10pct_share_kwh"] = round(float(rekap.Energi_kWh.nlargest(int(np.ceil(len(rekap) * .1))).sum() / rekap.Energi_kWh.sum()), 4)
A["kab_kwh"] = conc_stats(unit["kwh"])
A["kab_pop"] = conc_stats(unit["pop"])          # pembanding: HHI jika pasokan = penduduk
A["kab_chargers"] = conc_stats(unit["chargers"])
A["kab_kw"] = conc_stats(unit["kw"])
A["up3_kwh"] = conc_stats(rekap.groupby("UP3")["Energi_kWh"].sum())
A["jenis_lokasi_kwh"] = conc_stats(rekap.groupby("Jenis_Lokasi")["Energi_kWh"].sum())
A["jenis_lokasi_rows"] = [dict(jenis=k, sites=int(n), kwh=round(float(e)), share=round(float(e / rekap.Energi_kWh.sum()), 4))
                          for k, (n, e) in rekap.groupby("Jenis_Lokasi").agg(n=("ID_SPKLU", "size"), e=("Energi_kWh", "sum")).sort_values("e", ascending=False).iterrows()]
A["milik_kw"] = conc_stats(master.groupby("MILIK")["kw"].sum()); A["milik_chargers"] = conc_stats(master.groupby("MILIK").size())
A["milik_rows"] = [dict(milik=k, chargers=int(n), kw=round(float(w)), share_kw=round(float(w / master.kw.sum()), 4))
                   for k, (n, w) in master.groupby("MILIK").agg(n=("kw", "size"), w=("kw", "sum")).iterrows()]
A["merek_chargers"] = conc_stats(master.groupby("merek").size()); A["merek_kw"] = conc_stats(master.groupby("merek")["kw"].sum())
A["merek_rows"] = [dict(merek=k, chargers=int(n), share=round(float(n / len(master)), 4))
                   for k, n in master.groupby("merek").size().sort_values(ascending=False).head(6).items()]
A["kab_rows"] = [dict(nama=r.nama, pop_share=round(r.pop / unit["pop"].sum(), 4), kwh_share=round(r.kwh / unit["kwh"].sum(), 4),
                      charger_share=round(r.chargers / unit["chargers"].sum(), 4),
                      lq_kwh=round((r.kwh / unit["kwh"].sum()) / (r.pop / unit["pop"].sum()), 2))
                 for r in unit.sort_values("kwh", ascending=False).itertuples()]
# EV owner (sisi permintaan) pada tingkat kecamatan — 231 kecamatan ber-pemilik
A["ev_kab"] = conc_stats(unit["ev_owner"])
kec = ev_done.groupby("kec").size()
A["ev_kecamatan"] = conc_stats(kec)
A["ev_kecamatan"]["n_kecamatan_jabar_resmi"] = 627
A["ev_top_kecamatan"] = [dict(kec=k, n=int(v)) for k, v in kec.sort_values(ascending=False).head(10).items()]

# ------------------------------------------------------------------ B. indeks konsentrasi (26 unit kab/kota, tertimbang penduduk)
w = unit["pop"].to_numpy(float)
ranks = {"Kepadatan penduduk (gradien urban)": unit["density"].to_numpy(float),
         "Pemilik EV per 100 rb penduduk (intensitas permintaan)": unit["ev_per100k"].to_numpy(float),
         "Jumlah pemilik EV (volume permintaan)": unit["ev_owner"].to_numpy(float)}
outs = {"Jumlah charger": "chargers", "Kapasitas terpasang (kW)": "kw", "Energi terjual Mar-2026 (kWh)": "kwh",
        "Transaksi Mar-2026": "trx"}
B = []
for rl, rv in ranks.items():
    for ol, oc in outs.items():
        h = unit[oc].to_numpy(float)
        B.append(dict(rank=rl, outcome=ol, **ci_boot(h, rv, w)))
curves = {rl: dict(chargers=curve(unit["chargers"], rv, w), kwh=curve(unit["kwh"], rv, w)) for rl, rv in ranks.items()}

# uji kekokohan: tanpa Kota Bekasi/Depok/Bogor? -> tanpa 5 kota Jabodetabek; hanya kab/kota di luar Jabodetabek
jabo = unit["kab"].isin(["KOTA BEKASI", "KOTA DEPOK", "KOTA BOGOR", "KAB BEKASI", "KAB BOGOR"])
rob = []
for lab, mask in (("Seluruh Jabar (26)", np.ones(26, bool)), ("Tanpa Jabodetabek-Jabar (21)", ~jabo.to_numpy())):
    rob.append(dict(subset=lab, n=int(mask.sum()),
                    ci_kwh_density=round(ci(unit["kwh"].to_numpy()[mask], unit["density"].to_numpy()[mask], w[mask]), 3),
                    ci_chargers_density=round(ci(unit["chargers"].to_numpy()[mask], unit["density"].to_numpy()[mask], w[mask]), 3)))

out = dict(meta=dict(periode="Maret 2026", unit="26 unit kab/kota Jawa Barat (Kota Cimahi digabung ke Kota Bandung)", n_spklu_bertransaksi=int(len(rekap)),
                     n_charger_master=int(len(master)), n_ev_selesai=int(len(ev_done)), n_boot=N_BOOT),
           A=A, B=B, curves=curves, robust=rob,
           units=unit[["nama", "pop", "density", "chargers", "kw", "kwh", "trx", "ev_owner", "ev_per100k"]].round(2).to_dict("records"))
json.dump(out, open("analysis/concentration_jabar.json", "w"), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ ringkasan markdown
L = ["# Indeks konsentrasi SPKLU Jawa Barat — Maret 2026", ""]
L += [f"Sumber: Master SPKLU Maret 2026 ({len(master)} charger), rekap transaksi ({len(rekap)} SPKLU, "
      f"{rekap.Energi_kWh.sum():,.0f} kWh), pengajuan EV status Selesai ({len(ev_done)}), penduduk Kontur 2023.", ""]
L += ["## A. Konsentrasi pasokan/pasar (HHI 0–10.000; >2.500 = sangat terkonsentrasi)", "",
      "| Dimensi | n | HHI | N efektif | CR4 | CR10 | Gini |", "|---|---|---|---|---|---|---|"]
for lab, key in (("kWh per SPKLU", "spklu_kwh"), ("Transaksi per SPKLU", "spklu_trx"), ("kWh per kab/kota", "kab_kwh"),
                 ("Penduduk per kab/kota (pembanding)", "kab_pop"), ("Charger per kab/kota", "kab_chargers"),
                 ("kW per kab/kota", "kab_kw"), ("kWh per UP3", "up3_kwh"), ("kWh per jenis lokasi", "jenis_lokasi_kwh"),
                 ("kW per pemilik (PLN/mitra)", "milik_kw"), ("Charger per merek", "merek_chargers"),
                 ("Pemilik EV per kab/kota", "ev_kab"), ("Pemilik EV per kecamatan", "ev_kecamatan")):
    s = A[key]; L.append(f"| {lab} | {s['n']} | {s['hhi']:.0f} | {s['n_effective']} | {s['cr4']:.1%} | {s['cr10']:.1%} | {s['gini']} |")
L += ["", f"10 % SPKLU teratas menjual {A['top10pct_share_kwh']:.1%} kWh.", "",
      "## B. Indeks konsentrasi (26 unit kab/kota, tertimbang penduduk; * = 95 % CI tidak melewati 0)", "",
      "| Peringkat r | Pasokan | CI | 95 % CI |", "|---|---|---|---|"]
for b in B:
    L.append(f"| {b['rank']} | {b['outcome']} | {b['ci']:+.3f}{'*' if b['signif'] else ''} | [{b['lo']:+.3f}, {b['hi']:+.3f}] |")
L += ["", "Kekokohan: " + "; ".join(f"{r['subset']}: CI kWh~kepadatan {r['ci_kwh_density']:+.3f}, charger~kepadatan {r['ci_chargers_density']:+.3f}" for r in rob), ""]
open("analysis/concentration_jabar.md", "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L))
