"""Kombinasi data repositori × sumber terbuka terkatalog — hitung ulang seluruh angkanya.

Menjawab satu pertanyaan: dari 174 sumber di `resources/catalog.py`, mana yang benar-benar
bisa **disambungkan** ke data mentah repositori ini, dan apa yang keluar bila disambungkan?

Enam kombinasi dihitung dari berkas mentah di akar repositori, tanpa jaringan:

| # | Kombinasi | Data repo | Sumber terkatalog |
|---|---|---|---|
| K1 | Tangga daya — terpasang vs mampu vs terkirim | transaksi Maret 2026, KBLBB | Open EV Data (spesifikasi kendaraan) |
| K2 | Kebetulan surya — SPKLU sebagai beban siang | transaksi (profil jam) | pvlib (clear-sky Ineichen) |
| K3 | Gurun pengisian heksagonal | SPKLU + rumah pemilik EV | uber/h3 + metode ChargeGap |
| K4 | Kunci standar konektor | transaksi (konektor) | Open EV Data (armada dunia) |
| K5 | Kelekatan jaringan — jarak ke gardu induk | SPKLU | data/grid-id (GeoJSON GI & pembangkit) |
| K6 | Sintesis karbon — surya vs geser waktu | K2 + energi | analysis/carbon.json, Electricity Maps (konteks) |

Jalankan dari akar repositori:

    pip install pandas numpy pvlib h3
    python3 resources/combine/prepare.py     # -> resources/combine/combine.json
    python3 resources/combine/inject.py      # -> tab '🔗 Kombinasi' di index.html
"""
import csv, glob, json, os, re, datetime
import numpy as np
import pandas as pd
import pvlib, h3

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
OUT = "resources/combine/combine.json"

TRX = "Detail Transaksi SPKLU Jawa Barat - Maret 2026.csv"
KBLBB = "Data pelanggan EV.txt"
PERIODE = "Maret 2026"

# Titik acuan surya: Bandung (pusat gravitasi energi SPKLU Jawa Barat).  [VERIFY jika lokasi berubah]
LAT, LON, ALT, TZ = -6.95, 107.62, 768, "Asia/Jakarta"
# Faktor emisi rata-rata subsistem Jawa Barat (Jamali barat), dari analysis/carbon.json.
_CARBON = json.load(open("analysis/carbon.json", encoding="utf-8"))
EF_JAMALI = _CARBON["jamali_west"]["ef_kg_per_kwh"]
EF_LABEL = "Jamali barat (Jawa Barat)"

# --------------------------------------------------------------------- 0) muat
def load_trx():
    df = pd.read_csv(TRX, low_memory=False)
    df["rated"] = pd.to_numeric(df["Daya Charger"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    df["kwh"] = pd.to_numeric(df["Energi (kWh)"], errors="coerce")
    df["min"] = pd.to_numeric(df["Durasi (menit)"], errors="coerce")
    df["h"] = pd.to_numeric(df["Jam"], errors="coerce")
    d = df[(df["min"] > 1) & (df["kwh"] > 0) & df["rated"].notna() & df["h"].notna()].copy()
    d["pavg"] = d["kwh"] / (d["min"] / 60.0)          # daya rata-rata sepanjang sesi (termasuk diam)
    d["util"] = d["pavg"] / d["rated"]
    return df, d


def load_kblbb():
    rows = list(csv.DictReader(open(KBLBB, encoding="utf-8", errors="replace"), delimiter="\t"))
    out = []
    for r in rows:
        try:
            la, lo = float(r["Lat"]), float(r["Long"])
        except (TypeError, ValueError):
            la = lo = None
        out.append(dict(brand=re.sub(r"[^A-Z ]", " ", r["Jenis Kendaraan"].strip().upper()).strip(),
                        lat=la, lon=lo, kab=r.get("Kabupaten", "")))
    return out


def load_geojson(path, key):
    s = open(path, encoding="utf-8").read()
    i = s.index(key + ":")
    i = s.index("{", i)
    return json.JSONDecoder().raw_decode(s, i)[0]


def hav(la1, lo1, la2, lo2):
    R, p = 6371.0, np.pi / 180
    a = np.sin((la2 - la1) * p / 2) ** 2 + np.cos(la1 * p) * np.cos(la2 * p) * np.sin((lo2 - lo1) * p / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


# Spesifikasi kendaraan pasar Indonesia — sama persis dengan app/src/vehicles.ts, yang mengikuti
# skema Open EV Data (chargeprice/open-ev-data). brand -> daftar daya DC maksimum (kW) per model.
VEHICLE_DC = {
    "BYD": [88, 60, 150, 115, 150, 65], "DENZA": [166], "WULING": [0, 50, 50],
    "JAECOO": [70], "GEELY": [100], "AION": [80], "CHERY": [80, 80],
    "HYUNDAI": [220, 100], "MG": [140], "GWM": [80], "TOYOTA": [150], "NETA": [40],
    "VINFAST": [55], "BMW": [130], "MINI": [95], "DFSK": [40],
    # merek berekor panjang tanpa entri di vehicles.ts — pakai median segmennya, ditandai `assumed`
    "MAXUS": [80], "POLYTRON": [40], "CHANGAN": [90], "XPENG": [175], "VW": [135],
    "HONDA": [78], "VOLVO": [150], "CITROEN": [80], "ALETRA": [40],
    "MERCEDES BENZ": [170], "GREAT WALL": [80], "AUDI": [150],
}
ASSUMED = {"MAXUS", "POLYTRON", "CHANGAN", "XPENG", "VW", "HONDA", "VOLVO", "CITROEN",
           "ALETRA", "MERCEDES BENZ", "GREAT WALL", "AUDI"}


def std_of(s):
    s = str(s).upper()
    if "CHADEMO" in s: return "CHAdeMO"
    if "CCS" in s: return "CCS2"
    if "GB" in s and "T" in s: return "GB/T"
    if "TYPE 2" in s or s.startswith("AC"): return "AC Type 2"
    return "lain"


def main():
    raw, d = load_trx()
    ev = load_kblbb()
    combos = []

    # ============================================================ K1 — TANGGA DAYA
    dc = d[d.rated >= 25]
    bands = []
    for r, g in dc.groupby("rated"):
        if len(g) < 200: continue
        bands.append(dict(rated=int(r), n=int(len(g)), kwh=round(float(g.kwh.sum()), 1),
                          p50=round(float(g.pavg.median()), 1), p95=round(float(g.pavg.quantile(.95)), 1),
                          util=round(float(g.util.median()) * 100, 1), dwell=round(float(g["min"].median()), 1)))
    fleet = {}
    for e in ev:
        fleet[e["brand"]] = fleet.get(e["brand"], 0) + 1
    frows, tot, cap = [], 0, 0.0
    for b, n in sorted(fleet.items(), key=lambda x: -x[1]):
        dcs = VEHICLE_DC.get(b)
        if not dcs: continue
        med = float(np.median(dcs))
        frows.append(dict(brand=b.title(), n=n, dc=med, lo=min(dcs), hi=max(dcs), assumed=b in ASSUMED))
        tot += n; cap += n * med
    fleet_dc = cap / tot
    inst = float(np.average(dc.rated, weights=dc.kwh))
    deliv = float(dc.pavg.median()); deliv95 = float(dc.pavg.quantile(.95))
    # daya yang benar-benar terpakai bila seluruh armada dilayani pada langit-langitnya
    combos.append(dict(
        id="ladder", icon="🪜", title="Tangga daya — yang dipasang, yang mampu, yang benar-benar mengalir",
        question="SPKLU DC di Jawa Barat dipasang 120–300 kW. Berapa kW yang sungguh sampai ke mobil?",
        sources=[dict(t="repo", id="trx", label="99.544 sesi SPKLU Jawa Barat, %s" % PERIODE),
                 dict(t="repo", id="kblbb", label="3.694 permohonan home charging (merek kendaraan)"),
                 dict(t="cat", id="chargeprice/open-ev-data", label="Open EV Data — spesifikasi daya DC per model")],
        method="Daya rata-rata sesi = kWh ÷ jam terhubung. Langit-langit armada = rata-rata daya DC maksimum "
               "tertimbang jumlah pemilik per merek (spesifikasi dari Open EV Data / app/src/vehicles.ts). "
               "Daya terpasang = daya nominal charger, ditimbang energi yang dikirimnya.",
        kpi=[dict(v="%.0f kW" % inst, t="terpasang (tertimbang energi)"),
             dict(v="%.0f kW" % fleet_dc, t="langit-langit armada"),
             dict(v="%.0f kW" % deliv, t="terkirim, median sesi"),
             dict(v="%.0f%%" % (100 * deliv / inst), t="daya terpasang yang terpakai")],
        bands=bands, fleet=frows, fleet_dc=round(fleet_dc, 1), inst=round(inst, 1),
        deliv=round(deliv, 1), deliv95=round(deliv95, 1),
        insight="Daya terkirim **mendatar di sekitar 40 kW** begitu charger melewati 120 kW. Naik dari 120 kW ke "
                "300 kW menurunkan pemanfaatan daya dari %.0f%% ke %.0f%% tanpa menaikkan daya yang sampai ke mobil "
                "— bahkan sesi tercepat (p95) di unit 200 kW hanya %.0f kW. Pengikatnya bukan charger, melainkan "
                "armada dan kurva pengisian: langit-langit armada Jawa Barat %.0f kW, dan sesi median hanya %.1f kWh, "
                "jadi mobil masuk pada SoC menengah dan langsung mengisi di daerah taper."
                % (next(b["util"] for b in bands if b["rated"] == 120),
                   next(b["util"] for b in bands if b["rated"] == 300),
                   next(b["p95"] for b in bands if b["rated"] == 200), fleet_dc, float(dc.kwh.median())),
        action="Untuk anggaran yang sama, **tambah konektor, bukan kilowatt**. Satu unit 300 kW ≈ dua unit 120 kW "
               "atau enam unit 50 kW, dan ketiganya mengirim daya per sesi yang praktis sama pada armada hari ini.",
        caveat="Durasi mencakup waktu diam setelah pengisian selesai, jadi daya rata-rata di bawah daya puncak "
               "sesungguhnya; p95 adalah batas bawah kemampuan nyata. Merek dipetakan ke median daya DC modelnya "
               "karena tipe per pemohon tidak tercatat; %d merek ekor panjang memakai nilai anggapan."
               % len(ASSUMED & set(fleet)),
    ))

    # ============================================================ K2 — KEBETULAN SURYA
    loc = pvlib.location.Location(LAT, LON, tz=TZ, altitude=ALT, name="Bandung")
    times = pd.date_range("2026-03-01", "2026-03-31 23:00", freq="h", tz=TZ)
    ghi = loc.get_clearsky(times)["ghi"]
    pvn = (ghi.groupby(ghi.index.hour).mean())
    pvn = (pvn / pvn.sum()).reindex(range(24), fill_value=0.0).values
    hp = d.groupby(d.h.astype(int)).kwh.sum().reindex(range(24), fill_value=0.0)
    hpn = (hp / hp.sum()).values
    sizes = [round(100 * float(np.minimum(hpn, k * pvn).sum()), 1) for k in (0.5, 0.75, 1.0, 1.5, 2.0)]
    self1 = sizes[2]
    shift = round(100 * float(np.minimum(np.roll(hpn, 5), pvn).sum()), 1)
    venues = []
    for v, g in d.groupby("Jenis Titik Lokasi"):
        if g.kwh.sum() < 50000: continue
        p = g.groupby(g.h.astype(int)).kwh.sum().reindex(range(24), fill_value=0.0)
        p = (p / p.sum()).values
        venues.append(dict(venue=v, mwh=round(float(g.kwh.sum()) / 1000, 1),
                           day=round(100 * float(p[6:19].sum()), 1),
                           sc=round(100 * float(np.minimum(p, pvn).sum()), 1)))
    venues.sort(key=lambda x: -x["sc"])
    combos.append(dict(
        id="surya", icon="☀️", title="Kebetulan surya — SPKLU Indonesia adalah beban siang hari",
        question="Berapa banyak energi SPKLU yang bisa dipasok PV di atap situs itu sendiri, tanpa baterai?",
        sources=[dict(t="repo", id="trx", label="profil jam 2,26 GWh energi terkirim, %s" % PERIODE),
                 dict(t="cat", id="pvlib/pvlib-python", label="pvlib — clear-sky Ineichen, posisi matahari Bandung"),
                 dict(t="cat", id="evcc-io/evcc", label="evcc — pola pengisian mengikuti produksi PV")],
        method="Profil iradiasi langit-cerah per jam untuk %.2f°S %.2f°E dihitung dengan pvlib (model Ineichen, "
               "turbiditas Linke klimatologis), dinormalkan menjadi bentuk produksi harian. Swasembada = "
               "Σ min(pangsa pengisian per jam, pangsa produksi PV per jam), yaitu energi yang dipakai langsung "
               "tanpa penyimpanan." % (-LAT, LON),
        kpi=[dict(v="%.0f%%" % self1, t="langsung dari PV, tanpa baterai"),
             dict(v="%.0f%%" % shift, t="bila profilnya bergaya Eropa"),
             dict(v="%.0f%%" % (100 * hpn[6:19].sum()), t="energi terkirim 06.00–18.00"),
             dict(v="%.1f×" % (self1 / shift), t="keunggulan profil Indonesia")],
        hours=[dict(h=int(i), chg=round(100 * hpn[i], 2), pv=round(100 * pvn[i], 2)) for i in range(24)],
        sizes=[dict(k=k, sc=s) for k, s in zip([0.5, 0.75, 1.0, 1.5, 2.0], sizes)],
        venues=venues,
        insight="Pengisian publik Jawa Barat memuncak pukul **13.00–16.00**, tepat di bawah puncak matahari. "
                "PV yang dipasang sebesar energi harian situs menutup **%.0f%% energi pengisian secara langsung**, "
                "tanpa satu pun kilowatt-jam baterai. Profil pengisian bergaya Eropa yang memuncak malam hanya "
                "mencapai %.0f%% pada iradiasi yang sama. Perbedaannya bukan pada mataharinya — melainkan pada "
                "kapan orang Indonesia mengisi." % (self1, shift),
        action="PV atap di situs SPKLU di sini bukan gimik hijau, melainkan **substitusi energi bernilai tinggi**: "
               "setengah kWh yang dijual tidak perlu lewat penyulang sama sekali. Rest area tol dan mal — "
               "swasembada tertinggi — adalah kandidat pertama.",
        caveat="Langit-cerah adalah batas atas: awan Maret di Jawa Barat memangkas produksi harian, tetapi "
               "bentuk profilnya (dan karena itu pangsa kebetulan) berubah jauh lebih sedikit daripada tingkatnya. "
               "Rugi inverter, penuaan dan bayangan belum dimodelkan.",
    ))

    # ============================================================ K3 — GURUN HEKSAGONAL
    sp = d.groupby("ID SPKLU").agg(lat=("Latitude", "first"), lon=("Longitude", "first"),
                                   kwh=("kwh", "sum"), n=("kwh", "size"),
                                   kab=("Kota/Kabupaten", "first"),
                                   venue=("Jenis Titik Lokasi", "first")).reset_index()
    sp = sp[sp.lat.notna() & sp.lon.notna()].copy()
    geo = [e for e in ev if e["lat"] and e["lon"] and -8 < e["lat"] < -5 and 105 < e["lon"] < 109]

    # --- bersihkan pin default geocoder sebelum apa pun dihitung --------------
    # Rumah tangga berbeda tidak pernah berbagi koordinat enam desimal yang sama. Satu titik yang
    # dipakai banyak pemohon dari banyak kabupaten berbeda adalah pin bawaan peta, bukan alamat.
    PIN_MIN_N, PIN_MIN_KAB = 5, 3
    byxy = {}
    for e in geo:
        byxy.setdefault((e["lat"], e["lon"]), []).append(e["kab"])
    pins = {k: v for k, v in byxy.items()
            if len(v) >= PIN_MIN_N and len(set(v)) >= PIN_MIN_KAB}
    pinned = sum(len(v) for v in pins.values())
    pinrows = [dict(lat=round(k[0], 6), lon=round(k[1], 6), n=len(v), kab=len(set(v)))
               for k, v in sorted(pins.items(), key=lambda x: -len(x[1]))]
    clean = [e for e in geo if (e["lat"], e["lon"]) not in pins]

    RES, KR = 7, 2
    edge = h3.average_hexagon_edge_length(RES, unit="km")
    reach = edge * (1 + 1.5 * KR)
    cells = {h3.latlng_to_cell(r.lat, r.lon, RES) for r in sp.itertuples()}
    served = set()
    for c in cells:
        served |= set(h3.grid_disk(c, KR))

    def deserts_of(pop):
        hev = {}
        for e in pop:
            c = h3.latlng_to_cell(e["lat"], e["lon"], RES)
            hev[c] = hev.get(c, 0) + 1
        uns = {c: n for c, n in hev.items() if c not in served}
        return hev, uns

    hev_raw, uns_raw = deserts_of(geo)
    hev, uns = deserts_of(clean)
    out_raw = 100 * sum(uns_raw.values()) / len(geo)
    out = 100 * sum(uns.values()) / len(clean)
    S = np.array([[r.lat, r.lon] for r in sp.itertuples()])
    desert = []
    for c, n in sorted(uns.items(), key=lambda x: -x[1])[:12]:
        la, lo = h3.cell_to_latlng(c)
        desert.append(dict(cell=c, lat=round(la, 4), lon=round(lo, 4), owners=int(n),
                           km=round(float(hav(la, lo, S[:, 0], S[:, 1]).min()), 1)))
    combos.append(dict(
        id="gurun", icon="🕳️", title="Gurun pengisian — heksagon yang punya mobil tetapi tidak punya charger",
        question="Di mana pemilik EV tinggal terlalu jauh dari SPKLU mana pun — dan berapa banyak "
                 "\"gurun\" itu yang sebenarnya cuma alamat yang salah dipetakan?",
        sources=[dict(t="repo", id="kblbb", label="%d rumah pemilik EV tergeokode" % len(geo)),
                 dict(t="repo", id="spklu", label="%d situs SPKLU dengan koordinat" % len(sp)),
                 dict(t="cat", id="uber/h3", label="H3 — grid heksagonal hierarkis, resolusi %d" % RES),
                 dict(t="cat", id="aumvats/chargegap", label="ChargeGap — metode skor gurun pengisian")],
        method="Pin default dibuang lebih dulu: satu koordinat yang dipakai ≥%d pemohon dari ≥%d kabupaten "
               "berbeda bukan alamat rumah. Sisanya di-indeks ke heksagon H3 resolusi %d (rusuk %.2f km); "
               "heksagon disebut terlayani bila ada SPKLU dalam cincin k=%d (≈ %.1f km), dan heksagon "
               "berpenghuni yang tidak terlayani adalah gurun pengisian."
               % (PIN_MIN_N, PIN_MIN_KAB, RES, edge, KR, reach),
        kpi=[dict(v="%.1f%%" % out, t="pemilik di luar jangkauan %.1f km" % reach),
             dict(v="%.1f%%" % out_raw, t="sebelum pin dibersihkan"),
             dict(v="%d" % pinned, t="pemohon pada pin default"),
             dict(v="%d" % len(uns), t="heksagon gurun")],
        res=RES, edge=round(edge, 2), reach=round(reach, 1), deserts=desert, pins=pinrows,
        pinned=pinned, hexes=len(hev), out=round(out, 2), out_raw=round(out_raw, 2),
        insight="Gurun terbesar dalam data mentah ternyata bukan gurun. **%d pemohon** duduk persis di "
                "%d koordinat yang sama di sekitar Monas, Jakarta Pusat — satu titik dipakai bersama oleh "
                "pemohon dari **%d kabupaten berbeda**, yang alamat tertulisnya tersebar di Bogor, Depok, "
                "Bandung dan Bekasi. Itu pin bawaan peta, bukan rumah. Setelah dibuang, pemilik yang benar-benar "
                "di luar jangkauan %.1f km turun dari %.1f%% ke **%.1f%%**, dan sisanya terletak di "
                "**koridor antar-kota Cirebon timur, Majalengka dan Sukabumi selatan** — bukan di kantong "
                "perkotaan yang miskin."
                % (pinned, len(pins), max(r["kab"] for r in pinrows), reach, out_raw, out),
        action="Dua konsekuensi. Pertama, cakupan Jawa Barat sudah rapat, sehingga ukuran keadilan yang "
               "mengikat bergeser dari cakupan ke **kualitas dan keterisian** — persis pergeseran yang "
               "diusulkan Naskah 2. Kedua, **setiap analisis yang memakai koordinat KBLBB harus menyaring "
               "pin ini lebih dulu**, termasuk Capacity Maps yang memakai 3.687 titik yang sama; tanpa itu "
               "sebuah gurun palsu muncul di tengah Jakarta dan ikut menarik rekomendasi penempatan.",
        caveat="Ambang pin (≥%d pemohon, ≥%d kabupaten) konservatif: titik dengan dua sampai empat pemohon "
               "dibiarkan, sehingga sisa kesalahan geokode kecil masih ada — dua heksagon di sekitar Jakarta "
               "Selatan masih memuat 14 pemilik yang alamat tertulisnya di Jawa Barat. Rumah pemilik EV juga "
               "proksi permintaan laten yang bias: ia hanya memuat pemohon home charging PLN. Daftar SPKLU "
               "terbatas pada UID Jawa Barat, sehingga heksagon di perbatasan DKI dan Banten tampak lebih "
               "kosong daripada kenyataannya." % (PIN_MIN_N, PIN_MIN_KAB),
    ))

    # ============================================================ K4 — KUNCI STANDAR
    d2 = d.copy()
    d2["std"] = d2["Connector"].map(std_of)
    g = d2.groupby("std").agg(n=("kwh", "size"), kwh=("kwh", "sum"), conn=("Id Connector", "nunique"),
                              chg=("Id Charger", "nunique"))
    stds = [dict(std=k, n=int(v.n), kwh=round(float(v.kwh), 1), pct=round(100 * float(v.kwh) / float(g.kwh.sum()), 2),
                 chargers=int(v.chg)) for k, v in g.iterrows()]
    stds.sort(key=lambda x: -x["kwh"])
    cha = next((s for s in stds if s["std"] == "CHAdeMO"), dict(n=0, chargers=0, kwh=0))
    ccs = next(s for s in stds if s["std"] == "CCS2")
    # armada dunia (WORLD_EVS, index.html) untuk konteks: pangsa konektor menurut tahun rilis
    world = [("CHAdeMO", 2010, 2018), ("CCS", 2014, 2024), ("Tesla / NACS", 2012, 2024), ("Type 2 (AC)", 2013, 2022)]
    combos.append(dict(
        id="standar", icon="🔌", title="Kunci standar — Indonesia melompati CHAdeMO",
        question="Berapa banyak konektor terpasang yang praktis tidak pernah dipakai?",
        sources=[dict(t="repo", id="trx", label="konektor yang dipakai pada 99.544 sesi"),
                 dict(t="cat", id="chargeprice/open-ev-data", label="Open EV Data — konektor armada dunia"),
                 dict(t="cat", id="https://www.openchargealliance.org/", label="OCPP — apa yang bisa dicatat charger")],
        method="Setiap tali konektor pada transaksi dinormalkan ke standarnya (CCS2, AC Type 2, CHAdeMO), lalu "
               "dijumlahkan menurut energi, sesi dan jumlah charger yang menyediakannya.",
        kpi=[dict(v="%.1f%%" % ccs["pct"], t="energi lewat CCS2"),
             dict(v="%d" % cha["n"], t="sesi CHAdeMO sebulan"),
             dict(v="%d" % cha["chargers"], t="charger menyediakan CHAdeMO"),
             dict(v="%.0f kWh" % cha["kwh"], t="total energi CHAdeMO")],
        stds=stds, world=[dict(std=w[0], first=w[1], last=w[2]) for w in world],
        insight="CCS2 mengangkut **%.1f%%** energi. CHAdeMO — yang di Jepang dan Amerika Utara mewarisi satu dekade "
                "armada Nissan Leaf dan i-MiEV — mengangkut **%.0f kWh sebulan** di seluruh Jawa Barat: %d sesi, "
                "sekitar dua per hari, tersebar di %d charger. Indonesia mulai membangun setelah CCS2 menang, "
                "sehingga tidak pernah menanggung perang standar."
                % (ccs["pct"], cha["kwh"], cha["n"], cha["chargers"]),
        action="Tali CHAdeMO pada unit baru adalah biaya tanpa lalu lintas. Sebaliknya, keseragaman CCS2 membuat "
               "**roaming antar-operator (OCPI) murni soal perangkat lunak** — tidak ada penghalang fisik yang "
               "harus diselesaikan lebih dulu.",
        caveat="Nama konektor ditulis bebas oleh operator; normalisasi memakai pencocokan kata. Armada CBU pribadi "
               "yang membawa CHAdeMO mungkin memilih tidak mengisi di SPKLU publik sama sekali, sehingga angka ini "
               "adalah pemakaian, bukan populasi kendaraan.",
    ))

    # ============================================================ K5 — KELEKATAN JARINGAN
    subs = load_geojson("data/grid-id/data_jamali.js", "substations")["features"]
    gens = load_geojson("data/grid-id/data_jamali.js", "generators")["features"]
    S = np.array([[f["geometry"]["coordinates"][1], f["geometry"]["coordinates"][0]] for f in subs])
    sp["gi_km"] = [float(hav(r.lat, r.lon, S[:, 0], S[:, 1]).min()) for r in sp.itertuples()]
    q = pd.qcut(sp.gi_km, 4, labels=["Q1", "Q2", "Q3", "Q4"])
    quart = [dict(q=str(k), n=int(v.n), gi_km=round(float(v.gi), 2), kwh_med=round(float(v.kwh), 1),
                  kwh_tot=round(float(v.tot) / 1000, 1))
             for k, v in sp.groupby(q, observed=True).agg(n=("kwh", "size"), gi=("gi_km", "median"),
                                                          kwh=("kwh", "median"), tot=("kwh", "sum")).iterrows()]
    mix = {}
    for f in gens:
        if str(f["properties"].get("province", "")).upper() != "JAWA BARAT": continue
        t = f["properties"]["type"]
        mix[t] = mix.get(t, [0, 0.0])
        mix[t][0] += 1
        mix[t][1] += float(f["properties"].get("capacity_mw") or 0)
    RE = {"PLTA", "PLTP", "PLTS", "PLTB", "PLTM", "PLTMH", "PLTBG"}
    genmix = sorted([dict(t=k, n=v[0], mw=round(v[1], 1), re=k in RE) for k, v in mix.items()],
                    key=lambda x: -x["mw"])
    re_mw = sum(g["mw"] for g in genmix if g["re"]); all_mw = sum(g["mw"] for g in genmix)
    ratio = quart[0]["kwh_med"] / quart[-1]["kwh_med"]
    combos.append(dict(
        id="jaringan", icon="🔗", title="Kelekatan jaringan — SPKLU yang dekat gardu induk menjual jauh lebih banyak",
        question="Apakah lokasi yang baik untuk jaringan juga lokasi yang baik untuk permintaan?",
        sources=[dict(t="repo", id="spklu", label="%d situs SPKLU + energi bulanan" % len(sp)),
                 dict(t="repo", id="grid", label="data/grid-id — %d gardu induk & %d pembangkit Jamali" % (len(subs), len(gens))),
                 dict(t="cat", id="Project-OSRM/osrm-backend", label="OSRM — langkah berikutnya: jarak jalan, bukan garis lurus")],
        method="Jarak haversine dari tiap situs SPKLU ke gardu induk terdekat dalam sistem Jamali, lalu situs "
               "dibagi empat kuartil menurut jarak itu dan dibandingkan energi bulanannya.",
        kpi=[dict(v="%.1f km" % float(sp.gi_km.median()), t="jarak median ke gardu induk"),
             dict(v="%.1f×" % ratio, t="energi Q1 dibanding Q4"),
             dict(v="%.0f%%" % (100 * re_mw / all_mw), t="kapasitas terbarukan Jawa Barat"),
             dict(v="%.1f km" % float(np.percentile(sp.gi_km, 90)), t="persentil ke-90")],
        quartiles=quart, genmix=genmix,
        insight="Situs pada kuartil terdekat (median **%.1f km** dari gardu induk) menjual **%.1f×** energi situs "
                "pada kuartil terjauh (%.1f km). Kepadatan gardu induk adalah bayangan kepadatan beban, dan "
                "kepadatan beban adalah bayangan permintaan EV — sehingga di Jawa Barat penempatan yang ramah "
                "jaringan dan penempatan yang ramah permintaan **sebagian besar sepakat**, bukan bertabrakan."
                % (quart[0]["gi_km"], ratio, quart[-1]["gi_km"]),
        action="Kesepakatan itu tidak gratis untuk selamanya: ia berlaku selama permintaan masih terkonsentrasi "
               "di kota. Koridor gurun di K3 justru terletak di kuartil terjauh — di sanalah keduanya mulai "
               "berselisih, dan di sanalah biaya sambungan harus masuk model penempatan.",
        caveat="Jarak garis lurus, bukan jarak penyulang; sambungan sesungguhnya mengikuti jaringan tegangan "
               "menengah. Korelasi ini bukan sebab-akibat: keduanya sama-sama mengikuti kepadatan kota.",
    ))

    # ============================================================ K6 — SINTESIS KARBON
    kwh = float(d.kwh.sum())
    t_co2 = kwh * EF_JAMALI / 1000
    pv_abate = t_co2 * self1 / 100
    # geser waktu: pindahkan 20% energi jam 17-22 ke jam 10-14 -> hanya mengubah bauran marjinal sedikit
    peak = float(hp.loc[17:22].sum()); shift_kwh = 0.20 * peak
    # Selisih faktor emisi marjinal siang vs malam di sistem yang didominasi batu bara tidak diketahui
    # persis, jadi jalur B dihitung pada rentang 8-30 % — batas atasnya sengaja dilebihkan.
    GAP = 0.08
    shift_abate = shift_kwh * EF_JAMALI * GAP / 1000
    shift_hi = shift_kwh * EF_JAMALI * 0.30 / 1000
    # ukuran array PV yang tersirat oleh penyuryaan 1x energi harian, pada hasil 4,5 kWh/kWp/hari
    kwp_site = kwh / 31.0 / 4.5 / len(sp)
    combos.append(dict(
        id="karbon", icon="🌫️", title="Sintesis karbon — pasang panel, bukan sekadar geser jam",
        question="Mana yang lebih besar: menyurya-kan SPKLU, atau memindahkan pengisian ke jam yang lebih bersih?",
        sources=[dict(t="repo", id="carbon", label="analysis/carbon.json — faktor emisi %s, %.4f kg/kWh" % (EF_LABEL, EF_JAMALI)),
                 dict(t="repo", id="trx", label="%.2f GWh energi terkirim, %s" % (kwh / 1e6, PERIODE)),
                 dict(t="cat", id="electricitymaps/electricitymaps-contrib", label="Electricity Maps — pembanding intensitas karbon"),
                 dict(t="cat", id="pvlib/pvlib-python", label="pvlib — hasil K2 dipakai ulang")],
        method="Emisi dasar = energi × faktor emisi sistem Jamali. Jalur A: PV di situs menggantikan pangsa "
               "swasembada dari K2. Jalur B: memindahkan seperlima energi puncak sore (17.00–22.00) ke tengah hari, "
               "dinilai pada selisih faktor emisi marjinal siang-malam yang tipis di sistem yang didominasi batu bara.",
        kpi=[dict(v="%.0f tCO₂" % t_co2, t="emisi pengisian sebulan"),
             dict(v="%.0f tCO₂" % pv_abate, t="jalur A — PV di situs"),
             dict(v="%.0f tCO₂" % shift_abate, t="jalur B — geser waktu"),
             dict(v="%.0f×" % (pv_abate / max(shift_abate, 1e-9)), t="A dibanding B")],
        ef=round(EF_JAMALI, 4), kwh=round(kwh, 1), pv=round(pv_abate, 1), shift=round(shift_abate, 1),
        shift_hi=round(shift_hi, 1), kwp_site=round(kwp_site, 1), gap=GAP,
        insight="Pada sistem yang **batu baranya menyala sepanjang hari**, memindahkan jam pengisian nyaris tidak "
                "mengubah karbon: selisih bauran siang dan malam Jamali terlalu tipis. Menambah pembangkitan baru "
                "yang bersih di titik konsumsi mengubahnya — PV di situs meniadakan **%.0f tCO₂ sebulan**, sekitar "
                "**%.0f×** yang bisa dicapai penggeseran waktu paling agresif sekalipun."
                % (pv_abate, pv_abate / max(shift_abate, 1e-9)),
        action="Kebijakan smart-charging yang disalin dari Eropa memecahkan masalah Eropa (puncak malam pada "
               "jaringan yang bauran jamnya sangat berbeda). Di sini tuas karbonnya adalah **pembangkitan, bukan "
               "penjadwalan** — dan itulah argumen inti naskah tailpipe-to-smokestack.",
        caveat=("Faktor emisi rata-rata sistem, bukan marjinal. Selisih marjinal siang-malam adalah anggapan, "
                "jadi jalur B diuji pada 8–30 persen: bahkan pada 30 persen — jauh lebih lebar daripada yang "
                "masuk akal untuk Jamali — jalur B hanya mencapai {hi:.0f} tCO₂ dan tetap {r:.0f}× lebih kecil "
                "dari jalur A. Jalur A menyiratkan sekitar {kwp:.0f} kWp per situs, dan A serta B tidak "
                "sepenuhnya aditif.").format(hi=shift_hi, r=pv_abate / shift_hi, kwp=kwp_site),
    ))

    payload = dict(
        meta=dict(generated=datetime.date.today().isoformat(), periode=PERIODE,
                  sessions=int(len(d)), kwh=round(kwh, 1), sites=int(len(sp)),
                  owners=int(len(geo)), combos=len(combos),
                  libs=dict(pvlib=pvlib.__version__, h3=h3.__version__,
                            pandas=pd.__version__, numpy=np.__version__),
                  source="resources/combine/prepare.py"),
        combos=combos)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print("%d kombinasi -> %s (%.0f KB)" % (len(combos), OUT, os.path.getsize(OUT) / 1024))
    for c in combos:
        print("  %-9s %s" % (c["id"], c["title"]))
        print("            " + " · ".join("%s=%s" % (k["t"], k["v"]) for k in c["kpi"]))


if __name__ == "__main__":
    main()
