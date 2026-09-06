"""Bangun papers/p2p/p2p.json — payload analisis peer-to-peer EV charging (Jawa Barat).

Mereproduksi seluruh angka naskah "Charging without selling electricity" dari berkas
mentah di akar repositori:

  Detail Transaksi SPKLU Jawa Barat - Maret 2026.csv   101.020 sesi pengisian publik
  Data pelanggan EV.txt                                3.694 permohonan home charging (calon host)
  Rekap_SPKLU_Jabar_ArcGIS.csv                         331 situs SPKLU + pendapatan
  analysis/price.json                                  struktur tarif (energi + PPJ per pemda)

Blok analisis:
  A  pasar dasar        — sesi, kWh, pendapatan, harga all-in, profil jam
  B  pasokan host       — pemasangan home charging: sebaran, laju, kapasitas menganggur
  C  permintaan tersubstitusi — sesi yang secara fisik dapat dilayani AC 7 kW dekat host
  D  arsitektur tarif   — pita sewa parkir yang layak, harga efektif, titik impas dwell
  E  finansial 4 sisi   — host, pengemudi, platform, PLN/DSO
  F  jaringan           — pergeseran beban dari puncak malam ke luar puncak
  G  keadilan           — Gini host vs SPKLU vs populasi

Jalankan dari akar repositori:  python3 papers/p2p/prepare.py
"""
import csv, json, math, os, statistics, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "papers/p2p/p2p.json")
csv.field_size_limit(10 ** 7)

# ----------------------------------------------------------------- parameter
# Tarif. Komponen energi SPKLU dan PPJ per pemda dibaca dari analysis/price.json
# (dihitung dari transaksi nyata). Tarif rumah adalah tarif PLN R-1/TR >=3.500 VA.
TARIF_RUMAH   = 1699.53      # Rp/kWh, golongan rumah tangga >=3.500 VA        [VERIFY]
DISKON_MALAM  = 0.30         # diskon home charging 22.00-05.00                [VERIFY]
JAM_MALAM     = (22, 5)      # jendela diskon (mulai, selesai)

# Sisi fisik. Sambungan home charging PLN yang dominan adalah 7.700 VA satu fasa;
# wallbox lazim 7 kW dan mobil satu fasa dibatasi ~7,4 kW pada 230 V/32 A.
KW_SAMB       = 7.0          # daya AC efektif satu sambungan 7.700 VA
ETA_AC        = 0.93         # efisiensi pengisian AC (dipakai app/src/lib/model.ts)

# Biaya modal pembanding. Satu situs SPKLU DC 2 x 60 kW termasuk sipil, trafo,
# proteksi dan jaringan; wallbox rumah 7 kW termasuk instalasi dan meter baru.
CAPEX_SPKLU   = 1_200_000_000.0   # Rp per situs DC                            [VERIFY]
CAPEX_WALLBOX =    18_000_000.0   # Rp per titik AC 7 kW terpasang             [VERIFY]
OPEX_SPKLU_TH =    96_000_000.0   # Rp/tahun O&M + sewa lahan per situs        [VERIFY]
UMUR_SPKLU    = 10                # tahun

# Desain biaya platform (Model B — sewa parkir + jasa, tanpa jual-beli kWh)
FEE_LAYANAN   = 5000.0       # Rp per sesi, komponen platform
R_STAR        = 13500.0      # Rp/jam, sewa parkir acuan naskah (dipilih di tengah pita malam)
RADIUS        = [1.0, 2.0, 3.0, 5.0, 10.0]   # km, uji kedekatan host-situs

# Biaya pokok penyediaan tenaga listrik sistem Jawa-Bali, dipakai untuk menguji apakah
# sebuah tarif host masih menutup biaya PLN.                                   [VERIFY]
BPP_JAMALI    = 1150.0       # Rp/kWh
TARIF_UJI     = [1189.67, 1400.0, 1600.0, 1699.53, 1900.0]   # kandidat tarif meter host

# Profil pemakaian sendiri satu rumah tangga pemilik EV
KM_BULAN      = 1200.0       # km/bulan
JENDELA       = 8.0          # jam per malam yang dapat dibagikan (21.00-05.00)
MALAM_BULAN   = 30

# Populasi kota/kabupaten Jawa Barat (BPS, proyeksi pertengahan 2023, ribuan jiwa).
# Dipakai hanya untuk normalisasi keadilan.                                    [VERIFY]
POP = {
    "KAB. BOGOR": 5568, "KAB. SUKABUMI": 2760, "KAB. CIANJUR": 2500, "KAB. BANDUNG": 3780,
    "KAB. GARUT": 2650, "KAB. TASIKMALAYA": 1880, "KAB. CIAMIS": 1240, "KAB. KUNINGAN": 1180,
    "KAB. CIREBON": 2320, "KAB. MAJALENGKA": 1320, "KAB. SUMEDANG": 1200, "KAB. INDRAMAYU": 1860,
    "KAB. SUBANG": 1620, "KAB. PURWAKARTA": 1010, "KAB. KARAWANG": 2420, "KAB. BEKASI": 3150,
    "KAB. BANDUNG BARAT": 1830, "KAB. PANGANDARAN": 424,
    "KOTA BOGOR": 1090, "KOTA SUKABUMI": 350, "KOTA BANDUNG": 2570, "KOTA CIREBON": 340,
    "KOTA BEKASI": 2570, "KOTA DEPOK": 2120, "KOTA CIMAHI": 590, "KOTA TASIKMALAYA": 740,
    "KOTA BANJAR": 205,
}

# Daya pengisian AC maksimum per merek di pasar Indonesia (kW), dari app/src/vehicles.ts.
# Nilai >7 kW hanya tercapai pada sambungan tiga fasa, jadi dibatasi KW_SAMB di bawah.
AC_MEREK = {
    "BYD": 7.0, "Wuling": 6.6, "JAECOO": 6.6, "Geely": 11.0, "AION": 7.0, "Chery": 6.6,
    "Hyundai": 11.0, "MG": 7.0, "GWM": 11.0, "Mini": 11.0, "BMW": 11.0, "Neta": 6.6,
    "DFSK": 6.6, "Toyota": 6.6, "Maxus": 6.6, "VinFast": 7.4, "Denza": 11.0,
}
AC_DEFAULT = 6.6

# Jenis titik lokasi yang TIDAK dapat disubstitusi charger rumah: pengisian koridor
# di perjalanan antarkota, tempat kecepatan DC adalah alasan utama berhenti.
KORIDOR = {"Rest Area Tol"}


def rp(x):
    return round(float(x), 2)


def hav(a, b, c, d):
    """Jarak lingkaran besar (km)."""
    r = 6371.0
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = math.radians(c - a), math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def gini(x):
    """Gini atas daftar nilai non-negatif."""
    v = sorted(float(t) for t in x if t is not None)
    n = len(v)
    s = sum(v)
    if n == 0 or s <= 0:
        return 0.0
    cum = sum((i + 1) * t for i, t in enumerate(v))
    return (2 * cum) / (n * s) - (n + 1) / n


def lorenz(pairs):
    """Kurva Lorenz atas pasangan (bobot populasi, nilai). Kembalikan titik (x,y) dan Gini."""
    v = [(p, q) for p, q in pairs if p > 0]
    v.sort(key=lambda t: t[1] / t[0])
    tp, tq = sum(p for p, _ in v), sum(q for _, q in v)
    if tp <= 0 or tq <= 0:
        return [], 0.0
    pts, cp, cq, g = [[0.0, 0.0]], 0.0, 0.0, 0.0
    for p, q in v:
        x0, y0 = cp / tp, cq / tq
        cp += p
        cq += q
        x1, y1 = cp / tp, cq / tq
        g += (x1 - x0) * (y1 + y0)
        pts.append([round(x1, 4), round(y1, 4)])
    return pts, round(1 - g, 4)


print("== membaca transaksi ==")
TRX = os.path.join(ROOT, "Detail Transaksi SPKLU Jawa Barat - Maret 2026.csv")
sess_n = 0
tot_kwh = tot_rp = 0.0
hours = [dict(n=0, kwh=0.0) for _ in range(24)]
loctype = collections.defaultdict(lambda: dict(n=0, kwh=0.0, rp=0.0))
kab = collections.defaultdict(lambda: dict(n=0, kwh=0.0, rp=0.0, sites=set()))
sites = {}
dur_all, kwh_all = [], []
days = set()
# ringkasan per sesi yang dipakai blok C dan F (ringan: id situs, jam, kWh, menit)
slim = []

with open(TRX, encoding="utf-8-sig", newline="") as f:
    for d in csv.DictReader(f):
        e = float(d["Energi (kWh)"] or 0)
        t = float(d["Total Bayar (Rp)"] or 0)
        if e <= 0:
            continue
        sess_n += 1
        tot_kwh += e
        tot_rp += t
        h = int(d["Jam"])
        hours[h]["n"] += 1
        hours[h]["kwh"] += e
        days.add(d["Tanggal"])
        jt = d["Jenis Titik Lokasi"].strip()
        a = loctype[jt]
        a["n"] += 1
        a["kwh"] += e
        a["rp"] += t
        kb = d["Kota/Kabupaten"].strip()
        b = kab[kb]
        b["n"] += 1
        b["kwh"] += e
        b["rp"] += t
        sid = d["ID SPKLU"]
        b["sites"].add(sid)
        if sid not in sites:
            sites[sid] = dict(id=sid, nama=d["Nama SPKLU"].strip(), jt=jt, kab=kb,
                              lat=float(d["Latitude"] or 0), lon=float(d["Longitude"] or 0),
                              n=0, kwh=0.0, rp=0.0)
        s = sites[sid]
        s["n"] += 1
        s["kwh"] += e
        s["rp"] += t
        try:
            mnt = float(d["Durasi (menit)"] or 0)
        except ValueError:
            mnt = 0.0
        dur_all.append(mnt)
        kwh_all.append(e)
        slim.append((sid, h, e, mnt, jt))

DAYS = len(days)
ALLIN = tot_rp / tot_kwh
print(f"   {sess_n:,} sesi · {tot_kwh:,.0f} kWh · Rp {tot_rp:,.0f} · {DAYS} hari · {len(sites)} situs")
print(f"   harga all-in Rp {ALLIN:,.0f}/kWh")

PRICE = json.load(open(os.path.join(ROOT, "analysis/price.json")))
ENERGI = PRICE["price"]["energi"]          # komponen energi SPKLU, Rp/kWh
PPJ_RP = PRICE["price"]["ppj"]
HOME_MALAM = TARIF_RUMAH * (1 - DISKON_MALAM)

print("== membaca pemohon home charging ==")
HOSTS = os.path.join(ROOT, "Data pelanggan EV.txt")
hrows = list(csv.DictReader(open(HOSTS, encoding="utf-8-sig", errors="replace"), delimiter="\t"))
def kabname(r):
    return (r.get("Kabupaten") or "").split(" - ")[-1].strip().upper()
hosts = []
for r in hrows:
    try:
        la, lo = float(r["Lat"]), float(r["Long"])
    except (ValueError, KeyError, TypeError):
        la = lo = 0.0
    hosts.append(dict(kab=kabname(r), kec=(r.get("Kecamatan") or "").split(" - ")[-1].strip(),
                      kel=(r.get("Kelurahan") or "").split(" - ")[-1].strip(),
                      lat=la, lon=lo, st=(r.get("Status Approval") or "").strip(),
                      merek=(r.get("Jenis Kendaraan") or "").strip(),
                      daya=(r.get("tarif/Daya") or "").strip(),
                      bulan=(r.get("Tgl Pengajuan") or "")[3:10]))
H_DONE = [h for h in hosts if h["st"] == "Selesai"]
H_GEO = [h for h in hosts if h["lat"] and h["lon"]]
print(f"   {len(hosts):,} permohonan · {len(H_DONE):,} selesai · {len(H_GEO):,} bergeokode")
print(f"   {len({(h['kab'], h['kec']) for h in hosts}):,} kecamatan · "
      f"{len({(h['kab'], h['kec'], h['kel']) for h in hosts}):,} kelurahan")

# ------------------------------------------------------------------ A. pasar
A = dict(sessions=sess_n, kwh=rp(tot_kwh), rev=rp(tot_rp), days=DAYS, sites=len(sites),
         allin=rp(ALLIN), energi=rp(ENERGI), ppj=rp(PPJ_RP),
         kwh_sesi=rp(tot_kwh / sess_n), kwh_med=rp(statistics.median(kwh_all)),
         menit=rp(statistics.mean(dur_all)), menit_med=rp(statistics.median(dur_all)))
HRS = [dict(h=i, n=hours[i]["n"], kwh=rp(hours[i]["kwh"]),
            share=rp(100 * hours[i]["kwh"] / tot_kwh)) for i in range(24)]
LT = sorted([dict(k=k, n=v["n"], kwh=rp(v["kwh"]), rp=rp(v["rp"] / v["kwh"]),
                  koridor=k in KORIDOR) for k, v in loctype.items()],
            key=lambda x: -x["kwh"])

# --------------------------------------------------------------- B. host
hk = collections.Counter(h["kab"] for h in hosts)
hkd = collections.Counter(h["kab"] for h in H_DONE)
bulan = collections.Counter(h["bulan"] for h in hosts if h["bulan"])
def mkey(s):
    m, y = s.split("/")
    return int(y) * 100 + int(m)
BULAN = [dict(m=k, n=v) for k, v in sorted(bulan.items(), key=lambda x: mkey(x[0]))]
merek = collections.Counter(h["merek"] for h in hosts if h["merek"])
FLEET = []
wsum = wn = 0.0
for m, n in merek.most_common():
    ac = min(AC_MEREK.get(m, AC_DEFAULT), KW_SAMB)
    FLEET.append(dict(merek=m, n=n, ac=ac))
    wsum += ac * n
    wn += n
AC_FLEET = wsum / wn
print(f"   daya AC efektif tertimbang armada: {AC_FLEET:.2f} kW")

# --------------------------------- C. permintaan tersubstitusi (kedekatan host)
print("== uji kedekatan situs-host ==")
HG = [(h["lat"], h["lon"]) for h in H_GEO]
site_min = {}
for sid, s in sites.items():
    if not (s["lat"] and s["lon"]):
        site_min[sid] = 9e9
        continue
    best = 9e9
    la, lo = s["lat"], s["lon"]
    for a, b in HG:
        if abs(a - la) > 0.12 or abs(b - lo) > 0.12:      # saring kasar ~13 km
            continue
        d = hav(la, lo, a, b)
        if d < best:
            best = d
    site_min[sid] = best

# sesi tersubstitusi: bukan koridor tol DAN energinya muat dalam satu malam AC
E_MALAM = KW_SAMB * 7 * ETA_AC          # kWh yang dapat diberikan jendela 22.00-05.00
ADDR = []
for R in RADIUS:
    n = k = 0
    for sid, h, e, mnt, jt in slim:
        if jt in KORIDOR:
            continue
        if site_min.get(sid, 9e9) > R:
            continue
        if e > E_MALAM:
            continue
        n += 1
        k += e
    ADDR.append(dict(r=R, n=n, kwh=rp(k), share_n=rp(100 * n / sess_n),
                     share_kwh=rp(100 * k / tot_kwh)))
    print(f"   r={R:>4} km: {n:,} sesi ({100*n/sess_n:.1f} %) · {k:,.0f} kWh ({100*k/tot_kwh:.1f} %)")

# dekomposisi penyaring pada radius basis 3 km
R_BASE = 3.0
f_all = sess_n
f_nonkoridor = sum(1 for _, _, _, _, jt in slim if jt not in KORIDOR)
f_near = sum(1 for sid, _, _, _, jt in slim if jt not in KORIDOR and site_min.get(sid, 9e9) <= R_BASE)
f_fit = sum(1 for sid, _, e, _, jt in slim
            if jt not in KORIDOR and site_min.get(sid, 9e9) <= R_BASE and e <= E_MALAM)
FUNNEL = [dict(k="Seluruh sesi Maret 2026", n=f_all),
          dict(k="Bukan pengisian koridor tol", n=f_nonkoridor),
          dict(k="Situs ≤3 km dari host terpasang", n=f_near),
          dict(k="Energi muat satu jendela malam AC", n=f_fit)]
BASE = next(a for a in ADDR if a["r"] == R_BASE)

# ---------------------------------------------------- D. arsitektur tarif
# Model B: pengemudi membayar sewa parkir r (Rp/jam) + jasa platform F (Rp/sesi).
# Tidak ada kWh yang diperjualbelikan; energi tetap penjualan PLN kepada host.
#   biaya efektif  c(t) = F/(P·t) + r/P
#   lantai         c(inf) = r/P     -> r < P·p_spklu agar pernah lebih murah
#   pulang pokok   r > P·p_rumah    -> host tidak menombok energi
def band(p_home, P=KW_SAMB, eta=ETA_AC):
    """Pita sewa parkir yang layak, Rp/jam.

    Batas bawah  = biaya energi host per jam  = P x p_home       (kWh TERMETER)
    Batas atas   = titik saat lantai harga efektif menyamai SPKLU = P x eta x p_spklu
                   (kWh BATERAI -- yang dibandingkan pengemudi)
    """
    return dict(lo=rp(P * p_home), hi=rp(P * eta * ALLIN),
                lebar=rp(P * eta * ALLIN - P * p_home))
BAND_SIANG = band(TARIF_RUMAH)
BAND_MALAM = band(HOME_MALAM)
SURPLUS_KWH = ALLIN - TARIF_RUMAH
SURPLUS_KWH_MALAM = ALLIN - HOME_MALAM

def c_eff(t, r, F=FEE_LAYANAN, P=KW_SAMB, eta=ETA_AC):
    e = P * t * eta
    return (F + r * t) / e if e > 0 else float("inf")

def t_star(r, F=FEE_LAYANAN, P=KW_SAMB, eta=ETA_AC):
    """Dwell terpendek yang masih lebih murah daripada SPKLU."""
    den = P * eta * ALLIN - r
    return F / den if den > 0 else float("inf")

R_GRID = sorted({11000, 12000, 13000, 14000, 15000, 16000, 17000, int(R_STAR)})
CURVE = []
for r in R_GRID:
    CURVE.append(dict(r=r,
                      t=[[rp(t), rp(c_eff(t, r))] for t in (0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 10, 12)],
                      tstar=rp(t_star(r)),
                      floor=rp(r / (KW_SAMB * ETA_AC)),
                      margin_siang=rp(r - KW_SAMB * TARIF_RUMAH),
                      margin_malam=rp(r - KW_SAMB * HOME_MALAM)))

# desain acuan yang dipakai naskah: r dipilih di dalam pita malam
DES = dict(r=R_STAR, F=FEE_LAYANAN, P=KW_SAMB, eta=ETA_AC,
           floor=rp(R_STAR / (KW_SAMB * ETA_AC)), tstar=rp(t_star(R_STAR)),
           kwh_tstar=rp(KW_SAMB * ETA_AC * t_star(R_STAR)))
SES = []
for t in (2, 4, 6, 8, 10):
    e = KW_SAMB * ETA_AC * t          # kWh masuk baterai -- yang dinilai pengemudi
    m = KW_SAMB * t                   # kWh termeter      -- yang dibayar host ke PLN
    bayar = FEE_LAYANAN + R_STAR * t
    spklu = e * ALLIN
    SES.append(dict(t=t, kwh=rp(e), meter=rp(m), bayar=rp(bayar), eff=rp(bayar / e),
                    spklu=rp(spklu), hemat=rp(spklu - bayar),
                    hemat_pct=rp(100 * (spklu - bayar) / spklu),
                    energi_siang=rp(m * TARIF_RUMAH), energi_malam=rp(m * HOME_MALAM),
                    host_siang=rp(R_STAR * t - m * TARIF_RUMAH),
                    host_malam=rp(R_STAR * t - m * HOME_MALAM)))

# Model A (jual-beli kWh, belum sah): host memasang p_h Rp/kWh, platform ambil theta
THETA = 0.15
# Host menjual kWh baterai tetapi membayar PLN untuk kWh termeter (= e/eta).
MODEL_A = []
for ph in (1900, 2000, 2100, 2200, 2300, 2400):
    MODEL_A.append(dict(ph=ph, driver=rp(100 * (ALLIN - ph) / ALLIN),
                        host_siang=rp((1 - THETA) * ph - TARIF_RUMAH / ETA_AC),
                        host_malam=rp((1 - THETA) * ph - HOME_MALAM / ETA_AC),
                        platform=rp(THETA * ph)))

# Bandingkan A dan B pada HARGA PENGEMUDI YANG SAMA (sesi 8 jam pada desain acuan).
_e8 = KW_SAMB * ETA_AC * 8
_p8 = (FEE_LAYANAN + R_STAR * 8) / _e8
AB = dict(t=8, kwh=rp(_e8), driver_rp=rp(FEE_LAYANAN + R_STAR * 8), driver_kwh=rp(_p8),
          B=dict(host=rp(R_STAR * 8 - KW_SAMB * 8 * HOME_MALAM), plat=rp(FEE_LAYANAN)),
          A=dict(host=rp(((1 - THETA) * _p8 - HOME_MALAM / ETA_AC) * _e8),
                 plat=rp(THETA * _p8 * _e8)))

# ------------------------------------------------------- E. finansial 4 sisi
def host_bulan(sesi_per_minggu, t, malam=True):
    n = sesi_per_minggu * 52 / 12.0
    m = KW_SAMB * t                                   # kWh termeter
    biaya = m * (HOME_MALAM if malam else TARIF_RUMAH)
    return n * (R_STAR * t - biaya)
HOST = []
for spm in (2, 3, 5, 7, 10, 14):
    for t in (4, 8):
        pend = host_bulan(spm, t)
        HOST.append(dict(spm=spm, t=t, sesi=rp(spm * 52 / 12.0), net=rp(pend),
                         # payback penuh: seolah wallbox dibeli untuk disewakan
                         payback=rp(CAPEX_WALLBOX / pend) if pend > 0 else None,
                         # imbal hasil atas aset yang SUDAH terpasang untuk mobil sendiri
                         yld=rp(100 * pend * 12 / CAPEX_WALLBOX) if pend > 0 else None,
                         kwh=rp(spm * 52 / 12.0 * KW_SAMB * ETA_AC * t)))

# Pengemudi: profil 1.200 km/bulan, konsumsi 0,17 kWh/km (analysis/price.json assume)
KM = 1200.0
KWH_KM = PRICE["assume"]["kwh_km"]
BBM = PRICE["assume"]["bbm"]
KMPL = PRICE["assume"]["ice_kmpl"]
E_BULAN = KM * KWH_KM
DRIVER = dict(km=KM, kwh=rp(E_BULAN),
              spklu=rp(E_BULAN * ALLIN),
              p2p=rp(E_BULAN * (R_STAR / (KW_SAMB * ETA_AC)) + FEE_LAYANAN * (E_BULAN / (KW_SAMB * ETA_AC * 8))),
              rumah=rp(E_BULAN * TARIF_RUMAH), rumah_malam=rp(E_BULAN * HOME_MALAM),
              bbm=rp(KM / KMPL * BBM))
DRIVER["hemat_vs_spklu"] = rp(DRIVER["spklu"] - DRIVER["p2p"])
DRIVER["hemat_pct"] = rp(100 * DRIVER["hemat_vs_spklu"] / DRIVER["spklu"])

# Platform: GMV & pendapatan pada beberapa tingkat penetrasi segmen tersubstitusi
PLAT = []
for pen in (0.05, 0.10, 0.20, 0.35, 0.50):
    kwh = BASE["kwh"] * pen                     # kWh/bulan yang berpindah ke P2P
    n = BASE["n"] * pen
    jam = kwh / (KW_SAMB * ETA_AC)
    gmv = jam * R_STAR + n * FEE_LAYANAN
    PLAT.append(dict(pen=rp(100 * pen), kwh=rp(kwh), sesi=rp(n), gmv=rp(gmv),
                     fee=rp(n * FEE_LAYANAN),
                     host=rp(jam * R_STAR - (kwh / ETA_AC) * HOME_MALAM),
                     host_n=rp(n / (5 * 52 / 12.0))))

# PLN / DSO
PLN = []
for pen in (0.05, 0.10, 0.20, 0.35, 0.50):
    kwh = BASE["kwh"] * pen
    # kWh pindah dari tarif SPKLU (komponen energi) ke tarif rumah malam
    dilusi = kwh * ENERGI - (kwh / ETA_AC) * HOME_MALAM
    situs = kwh / (tot_kwh / len(sites))        # setara berapa situs SPKLU rata-rata
    capex = situs * CAPEX_SPKLU
    opex = situs * OPEX_SPKLU_TH
    PLN.append(dict(pen=rp(100 * pen), kwh=rp(kwh), dilusi_bln=rp(dilusi),
                    dilusi_th=rp(dilusi * 12), situs=rp(situs),
                    capex=rp(capex), opex_th=rp(opex),
                    anuitas=rp(capex / UMUR_SPKLU + opex),
                    net_th=rp(capex / UMUR_SPKLU + opex - dilusi * 12)))

# --------------------------------------------------------------- F. jaringan
PEAK_H = list(range(17, 22))                       # 17.00-21.59, puncak sistem Jawa-Bali
OFF_H = [22, 23, 0, 1, 2, 3, 4]
kwh_peak = sum(hours[h]["kwh"] for h in PEAK_H)
kwh_off = sum(hours[h]["kwh"] for h in OFF_H)
GRID = dict(peak_kwh=rp(kwh_peak), peak_share=rp(100 * kwh_peak / tot_kwh),
            off_kwh=rp(kwh_off), off_share=rp(100 * kwh_off / tot_kwh),
            peak_mw=rp(kwh_peak / len(PEAK_H) / DAYS / 1000.0),
            off_mw=rp(kwh_off / len(OFF_H) / DAYS / 1000.0))
# berapa MW puncak yang hilang bila segmen tersubstitusi pindah ke jendela malam
SHIFT = []
for pen in (0.05, 0.10, 0.20, 0.35, 0.50):
    # sesi tersubstitusi yang jatuh pada jam puncak
    k = sum(e for sid, h, e, mnt, jt in slim
            if jt not in KORIDOR and site_min.get(sid, 9e9) <= R_BASE
            and e <= E_MALAM and h in PEAK_H) * pen
    mw = k / len(PEAK_H) / DAYS / 1000.0
    SHIFT.append(dict(pen=rp(100 * pen), kwh=rp(k), mw=rp(mw),
                      pct_peak=rp(100 * mw / GRID["peak_mw"])))
# Konsentrasi daya: satu situs DC vs sebaran host AC
GRID["dc_kw_situs"] = 120.0
GRID["ac_kw_host"] = KW_SAMB
GRID["host_setara"] = rp(120.0 / KW_SAMB)

# ---------------------------------------------------------------- G. keadilan
KAB = []
for k, v in kab.items():
    p = POP.get(k)
    KAB.append(dict(kab=k, pop=p, sesi=v["n"], kwh=rp(v["kwh"]), rev=rp(v["rp"]),
                    situs=len(v["sites"]), host=hk.get(k, 0), host_done=hkd.get(k, 0),
                    kwh_kapita=rp(v["kwh"] / p) if p else None,
                    host_100k=rp(1e2 * hk.get(k, 0) / p) if p else None))
for k, n in hk.items():
    if k and k not in kab:
        p = POP.get(k)
        KAB.append(dict(kab=k, pop=p, sesi=0, kwh=0.0, rev=0.0, situs=0,
                        host=n, host_done=hkd.get(k, 0), kwh_kapita=0.0,
                        host_100k=rp(1e2 * n / p) if p else None))
KAB.sort(key=lambda x: -x["kwh"])
pk = [(x["pop"], x["kwh"]) for x in KAB if x["pop"]]
ph = [(x["pop"], x["host"]) for x in KAB if x["pop"]]
ps = [(x["pop"], x["situs"]) for x in KAB if x["pop"]]
L_KWH, G_KWH = lorenz(pk)
L_HOST, G_HOST = lorenz(ph)
L_SITE, G_SITE = lorenz(ps)
EQ = dict(gini_kwh=G_KWH, gini_host=G_HOST, gini_situs=G_SITE,
          lorenz_kwh=L_KWH, lorenz_host=L_HOST, lorenz_situs=L_SITE,
          n_kab=len([x for x in KAB if x["pop"]]),
          kab_tanpa_host=[x["kab"] for x in KAB if x["pop"] and x["host"] == 0],
          kab_tanpa_situs=[x["kab"] for x in KAB if x["pop"] and x["situs"] == 0])
# korelasi peringkat host vs kWh publik
def spearman(a, b):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for i, j in enumerate(o):
            r[j] = i + 1.0
        return r
    ra, rb = rank(a), rank(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else 0.0
sub = [x for x in KAB if x["pop"]]
EQ["rho_host_kwh"] = rp(spearman([x["host"] for x in sub], [x["kwh"] for x in sub]))
EQ["rho_host_situs"] = rp(spearman([x["host"] for x in sub], [x["situs"] for x in sub]))


# ------------------------------- B2. kapasitas menganggur charger rumah
# Satu rumah tangga pemilik EV yang menempuh KM_BULAN km/bulan hanya memakai
# chargernya beberapa jam per minggu. Sisanya adalah pasokan P2P yang sudah terpasang.
E_SENDIRI_BAT = KM_BULAN * PRICE["assume"]["kwh_km"]        # kWh masuk baterai
E_SENDIRI_MTR = E_SENDIRI_BAT / ETA_AC                      # kWh termeter
JAM_SENDIRI = E_SENDIRI_MTR / KW_SAMB                       # jam charger per bulan
JAM_TERSEDIA = JENDELA * MALAM_BULAN                        # jam malam yang dapat dibagi
JAM_IDLE = max(0.0, JAM_TERSEDIA - JAM_SENDIRI)
KWH_IDLE = JAM_IDLE * KW_SAMB * ETA_AC                      # kWh baterai/host/bulan
KWH_SITUS = tot_kwh / len(sites)                            # keluaran rata-rata satu situs SPKLU
IDLE = dict(km=KM_BULAN, kwh_sendiri=rp(E_SENDIRI_BAT), meter_sendiri=rp(E_SENDIRI_MTR),
            jam_sendiri=rp(JAM_SENDIRI), malam_sendiri=rp(JAM_SENDIRI / JENDELA),
            jendela=JENDELA, malam=MALAM_BULAN, jam_idle=rp(JAM_IDLE),
            idle_pct=rp(100 * JAM_IDLE / JAM_TERSEDIA), kwh_host=rp(KWH_IDLE),
            kwh_situs=rp(KWH_SITUS))
for lbl, n in (("terpasang", len(H_DONE)), ("seluruh permohonan", len(hosts))):
    IDLE[lbl] = dict(n=n, kwh=rp(n * KWH_IDLE), rasio=rp(n * KWH_IDLE / tot_kwh),
                     situs=rp(n * KWH_IDLE / KWH_SITUS),
                     capex=rp(n * KWH_IDLE / KWH_SITUS * CAPEX_SPKLU))
print(f"   pemakaian sendiri {JAM_SENDIRI:.1f} jam/bln = {JAM_SENDIRI/JENDELA:.1f} malam; "
      f"idle {IDLE['idle_pct']:.0f} % dari {JAM_TERSEDIA:.0f} jam malam")
print(f"   headroom malam {len(H_DONE):,} host terpasang: {len(H_DONE)*KWH_IDLE/1e6:.2f} GWh/bln "
      f"= {IDLE['terpasang']['rasio']:.2f}x keluaran seluruh jaringan publik")

# ------------------------------- D2. kelayakan menurut jendela waktu
# Jendela malam menikmati diskon home charging; jendela siang tidak. Selisih itu
# menentukan apakah berbagi di luar malam masuk akal secara ekonomi.
WIN = []
for lbl, p_h, jam in (("Malam 22.00-05.00 (diskon berlaku)", HOME_MALAM, 7),
                      ("Sore-malam 18.00-22.00 (tarif penuh)", TARIF_RUMAH, 4),
                      ("Siang 09.00-15.00 (tarif penuh)", TARIF_RUMAH, 6)):
    b = band(p_h)
    WIN.append(dict(win=lbl, p=rp(p_h), jam=jam, lo=b["lo"], hi=b["hi"], lebar=b["lebar"],
                    margin=rp(R_STAR - KW_SAMB * p_h),
                    layak=bool(R_STAR > KW_SAMB * p_h),
                    disk=rp(100 * (ALLIN - R_STAR / (KW_SAMB * ETA_AC)) / ALLIN)))

# ------------------------------- E2. batas depan desain tarif meter host
# Tiga pihak berbagi selisih Rp/kWh antara harga SPKLU dan tarif meter host.
# Tarif yang terlalu rendah menggerus pendapatan PLN; terlalu tinggi menutup pasar.
FRONT = []
for p_h in TARIF_UJI:
    lo, hi = KW_SAMB * p_h, KW_SAMB * ETA_AC * ALLIN
    row = dict(p=rp(p_h), lo=rp(lo), hi=rp(hi), lebar=rp(hi - lo),
               atas_bpp=rp(p_h - BPP_JAMALI), dilusi=rp(ENERGI - p_h / ETA_AC), r=[])
    for r in (12000, 13500, 15000, 16000):
        row["r"].append(dict(r=r, margin=rp(r - lo),
                             eff=rp(r / (KW_SAMB * ETA_AC)),
                             disk=rp(100 * (ALLIN - r / (KW_SAMB * ETA_AC)) / ALLIN),
                             layak=bool(lo < r < hi)))
    FRONT.append(row)


# ---------------- D3. risiko daya: siapa yang menanggung mobil yang mengisi pelan
# Di bawah tarif berbasis waktu, harga efektif per kWh berbanding terbalik dengan
# daya yang benar-benar diterima mobil. Mobil ber-onboard charger kecil membayar
# jauh lebih mahal untuk energi yang sama -- risiko yang tidak ada pada tarif per kWh.
POW = []
for kw in (3.3, 4.0, 5.0, 6.6, 7.0):
    k = min(kw, KW_SAMB)
    eff = R_STAR / (k * ETA_AC)
    POW.append(dict(kw=kw, eff=rp(eff), rel=rp(100 * (eff - ALLIN) / ALLIN),
                    jam8=rp(k * ETA_AC * 8),
                    bayar8=rp(FEE_LAYANAN + R_STAR * 8),
                    eff8=rp((FEE_LAYANAN + R_STAR * 8) / (k * ETA_AC * 8))))
# harga efektif menurut merek pada armada host nyata (kapasitas 8 jam)
POW_MEREK = []
for f in FLEET[:10]:
    k = min(f["ac"], KW_SAMB)
    POW_MEREK.append(dict(merek=f["merek"], n=f["n"], kw=k,
                          eff8=rp((FEE_LAYANAN + R_STAR * 8) / (k * ETA_AC * 8))))

# ------------------------------------------------------------------- keluaran
out = dict(
    meta=dict(gen="papers/p2p/prepare.py", bulan="Maret 2026", prov="Jawa Barat",
              hosts=len(hosts), hosts_done=len(H_DONE), hosts_geo=len(H_GEO),
              kec=len({(h["kab"], h["kec"]) for h in hosts}),
              kel=len({(h["kab"], h["kec"], h["kel"]) for h in hosts}),
              daya7700=sum(1 for h in hosts if h["daya"] == "7700"),
              ac_fleet=rp(AC_FLEET), e_malam=rp(E_MALAM), r_base=R_BASE),
    A=A, hours=HRS, loctype=LT, bulan=BULAN, fleet=FLEET,
    price=dict(allin=rp(ALLIN), energi=rp(ENERGI), ppj=rp(PPJ_RP), rumah=TARIF_RUMAH,
               rumah_malam=rp(HOME_MALAM), diskon=DISKON_MALAM,
               surplus=rp(SURPLUS_KWH), surplus_malam=rp(SURPLUS_KWH_MALAM)),
    addr=ADDR, funnel=FUNNEL, base=BASE,
    band=dict(siang=BAND_SIANG, malam=BAND_MALAM),
    curve=CURVE, des=DES, ses=SES, modelA=MODEL_A, theta=THETA,
    host=HOST, driver=DRIVER, plat=PLAT, pln=PLN, ab=AB,
    grid=GRID, shift=SHIFT, kab=KAB, eq=EQ, idle=IDLE, win=WIN, front=FRONT,
    pow=POW, pow_merek=POW_MEREK,
    par=dict(tarif_rumah=TARIF_RUMAH, diskon=DISKON_MALAM, kw=KW_SAMB, eta=ETA_AC,
             capex_spklu=CAPEX_SPKLU, capex_wallbox=CAPEX_WALLBOX,
             opex_spklu=OPEX_SPKLU_TH, umur=UMUR_SPKLU, fee=FEE_LAYANAN, r=R_STAR,
             theta=THETA, radius=RADIUS, koridor=sorted(KORIDOR),
             bpp=BPP_JAMALI, km=KM_BULAN, jendela=JENDELA, malam=MALAM_BULAN),
)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"\ntertulis: {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")

# ------------------------------------------------------------------- ringkasan
print(f"""
=== RINGKASAN ===
Harga SPKLU all-in            Rp {ALLIN:,.0f}/kWh   (energi Rp {ENERGI:,.0f} + PPJ Rp {PPJ_RP:,.0f})
Tarif rumah siang / malam     Rp {TARIF_RUMAH:,.0f} / Rp {HOME_MALAM:,.0f} per kWh
Surplus per kWh siang/malam   Rp {SURPLUS_KWH:,.0f} / Rp {SURPLUS_KWH_MALAM:,.0f}
Pita sewa parkir layak (7 kW) siang Rp {BAND_SIANG['lo']:,.0f}-{BAND_SIANG['hi']:,.0f}/jam
                              malam Rp {BAND_MALAM['lo']:,.0f}-{BAND_MALAM['hi']:,.0f}/jam
Segmen tersubstitusi (3 km)   {BASE['n']:,} sesi ({BASE['share_n']:.1f} %) · {BASE['kwh']:,.0f} kWh ({BASE['share_kwh']:.1f} %)
Desain r=Rp {R_STAR:,.0f}/jam        lantai Rp {DES['floor']:,.0f}/kWh · impas dwell {DES['tstar']:.2f} jam ({DES['kwh_tstar']:.1f} kWh)
Gini vs populasi              kWh {G_KWH:.3f} · situs {G_SITE:.3f} · host {G_HOST:.3f}
rho host-kWh {EQ['rho_host_kwh']:.2f} · host-situs {EQ['rho_host_situs']:.2f}
Puncak 17-22 {GRID['peak_share']:.1f} % energi ({GRID['peak_mw']:.2f} MW rata-rata)
""")
