"""Klasifikasi tempat (venue) SPKLU dari nama situs — port Python dari `venueOf()` di index.html
(tab 🇮🇩 Indonesia), plus pengelompokan ke kategori LAHAN PARKIR yang dipakai tab 🅿️ Parkir × Charger.

Prinsipnya: setiap SPKLU publik berdiri di sebuah lahan parkir; yang membedakan ekonominya adalah
*mengapa mobil diparkir di sana* — transit (berhenti sebentar), destinasi (belanja/menginap),
kerja/publik (jam kantor), hunian (menginap semalaman), dealer (showroom).
"""
import os, re

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, "SPKLU_Indonesia_Lengkap_2026-06-08.xlsx")

VENUES = [
    ("Toll rest area", r"REST AREA|RA KM|KM \d+ ?[AB]\b|RUAS|TRAVOY| TOL |TOL$|JORR|JAGORAWI|CIPULARANG|CIPALI|PALIKANCI|KANCI|PEJAGAN|CIKAMPEK|JAKARTA - |GERBANG TOL|\bGT "),
    ("Mall / retail", r"MALL|SUMMARECON|LIPPO|PLAZA|SQUARE|LIFESTYLE|TRANS STUDIO|PVJ|PARIS VAN JAVA|CITYLINK|TRANSMART|TECHNOMART|GRAND INDONESIA|KASABLANKA|PONDOK INDAH|SENAYAN|CENTRAL PARK|AEON|\bPIM\b|GANDARIA|KELAPA GADING|BLOK M|MARGO|CIBINONG CITY|PARAGON|GALAXY|HARTONO|PAKUWON|TUNJUNGAN|CIPUTRA"),
    ("Hotel / hospitality", r"HOTEL|ASTON|\bINN\b|RESORT|DORMITORY|HOSTEL|HORISON|HARRIS|MERCURE|\bIBIS\b|SANTIKA|NOVOTEL|SWISS|FAVE|AMARIS"),
    ("Auto dealer / showroom", r"BYD|ARISTA|CHERY|GEELY|WULING|HYUNDAI|TOYOTA|DEALER|SHOWROOM|MARKETING GALLERY|SALES|AVANTE|\bAUTO\b|MITSUBISHI|NETA|DFSK|\bMG |SUZUKI|HONDA|NISSAN|DAIHATSU|ASTRA"),
    ("F&B / café", r"COFFEE|CAFE|CAF[EÉ]|CAR ?WASH|RESTO|RESTAURANT|\bKOPI\b|FOOD|TERAS|\bRM |WAROENG|WARUNG|EATERY|BAKERY"),
    ("Hospital / health", r"\bRS |RSUD|RUMAH SAKIT|MEDIKA|HOSPITAL|KLINIK|SILOAM|HERMINA|PUSKESMAS"),
    ("Transport hub", r"BANDARA|AIRPORT|STASIUN|STATION|TERMINAL|\bMRT\b|\bLRT\b|\bKRL\b|WHOOSH|PELABUHAN|HALTE"),
    ("Public / govt / edu", r"BALAI KOTA|SEKDA|PEMDA|PEMKOT|PEMKAB|DPRD|DISHUB|DINAS|SAMSAT|KECAMATAN|GEDUNG SATE|POLRES|POLSEK|POLDA|POSPOL|KODIM|KEJAKSAAN|PENGADILAN|KANTOR DESA|GBK|GELORA|ISTANA|MASJID|MESJID|ALUN|KAMPUS|UNIVERSITAS|\bITB\b|UNPAD|SEKOLAH"),
    ("PLN office", r"PLN UP3|PLN ULP|PLN UID|PLN UIP|PLN UPT|CSE PLN|\bUP3\b|\bULP\b|\bUPT\b|UPDL|KANWIL|DAYA\+|ICON ?HUB|ICON ?PLUS|\bPOSKO\b|\bUID\b|\bUIW\b|PLN CGE|MOBILE UID|GARDU INDUK|BISNIS CENTER|UIKL"),
    ("SPBU / fuel", r"SPBU|PERTAMINA|SHELL| BP |\bVIVO\b"),
    ("Tourism / leisure", r"WISATA|PUNCAK|PANTAI|BEACH|ANCOL|TMII|RAGUNAN|\bGOLF\b|SAFARI|CURUG|GLAMPING|VILLA|CANDI|TAMAN|MUSEUM|KEBUN|DANAU"),
    ("Residential / township", r"PARAHYANGAN|\bKBP\b|GARDENS|TOWNSHIP|RESIDENCE|\bPERUM\b|CLUSTER|CITRA|VERONA|HILLS|APARTEMEN|APARTMENT|HARVEST CITY|GREENLAND|GATEWAY|SUDIRMAN|SCBD|\bBSD\b|\bPIK\b|PANTAI INDAH|KOTA WISATA|SENTUL|MEIKARTA|PERUMAHAN"),
    ("Office / commercial", r"\bBTN\b|BANK|BSPACE|OFFICE|GEDUNG|TOWER|GRHA|GRAHA|KANTOR|WISMA|MENARA|BUSINESS PARK|PERKANTORAN"),
]
VENUES = [(n, re.compile(p)) for n, p in VENUES]

# kategori lahan parkir — urutan = urutan tampil
CATS = [
    dict(id="transit", label="Parkir transit", icon="🛣️", color="#d6443c",
         desc="berhenti sebentar di perjalanan: rest area tol, terminal/stasiun/bandara, SPBU"),
    dict(id="destinasi", label="Parkir destinasi", icon="🛍️", color="#e0a52b",
         desc="mobil diparkir 1–4 jam karena tujuan lain: mall, hotel, F&B, wisata, rumah sakit"),
    dict(id="kerja", label="Parkir kerja & publik", icon="🏢", color="#3a6ea5",
         desc="parkir jam kantor: gedung perkantoran, kantor pemerintah/kampus, kantor PLN"),
    dict(id="hunian", label="Parkir hunian", icon="🏘️", color="#2e9e5b",
         desc="parkir semalaman: perumahan, township, apartemen"),
    dict(id="dealer", label="Dealer / showroom", icon="🚗", color="#8a6fb0",
         desc="halaman dealer — parkir pelanggan & unit display, sering khusus merek"),
    dict(id="lainnya", label="Lainnya / campuran", icon="📍", color="#9aa6bd", desc="nama tidak terklasifikasi"),
]
VENUE_CAT = {
    "Toll rest area": "transit", "Transport hub": "transit", "SPBU / fuel": "transit",
    "Mall / retail": "destinasi", "Hotel / hospitality": "destinasi", "F&B / café": "destinasi",
    "Tourism / leisure": "destinasi", "Hospital / health": "destinasi",
    "Office / commercial": "kerja", "Public / govt / edu": "kerja", "PLN office": "kerja",
    "Residential / township": "hunian", "Auto dealer / showroom": "dealer", "Other / mixed": "lainnya",
}
# label resmi "Jenis Titik Lokasi" pada rincian transaksi PLN Jawa Barat -> kategori
JENIS_CAT = {
    "Rest Area Tol": "transit", "Publik / Pemerintah / Transportasi": "kerja",
    "Mall / Retail / Supermarket": "destinasi", "Hotel / Hospitality": "destinasi",
    "F&B / Kafe / Leisure Retail": "destinasi", "Wisata / Leisure": "destinasi", "Rumah Sakit / Kesehatan": "destinasi",
    "Kantor / Unit Layanan PLN": "kerja", "Perkantoran / Gedung Komersial": "kerja",
    "Perumahan / Township": "hunian", "Dealer / Showroom Mobil": "dealer", "Lainnya / Campuran": "lainnya",
}
PARKING_CATS = {"transit", "destinasi", "kerja"}   # "lahan parkir umum" dalam arti sempit (bukan hunian/dealer)


def venue_of(name):
    s = (name or "").upper()
    for n, rx in VENUES:
        if rx.search(s):
            return n
    return "Other / mixed"


def load_sites():
    """Master SPKLU nasional -> daftar situs dengan venue & kategori parkir."""
    wb = openpyxl.load_workbook(MASTER, read_only=True)
    ws = wb["Master SPKLU Indonesia"]
    it = ws.iter_rows(values_only=True)
    hdr = [str(c) for c in next(it)]
    col = {c: i for i, c in enumerate(hdr)}
    out = []
    for r in it:
        if r[col["Latitude"]] in (None, "") or r[col["Longitude"]] in (None, ""):
            continue
        lat, lng = float(r[col["Latitude"]]), float(r[col["Longitude"]])
        if not (-11.5 < lat < 6.5 and 94 < lng < 142):
            continue
        kw = float(re.sub(r"[^\d,\.]", "", str(r[col["Kapasitas (kW)"]] or "0")).replace(",", ".") or 0)
        st = str(r[col["Status"]] or "").strip().lower()
        cat = str(r[col["Kategori"]] or "")
        pln = cat == "PLN"
        active = (st in ("available", "inuse")) or (not pln and st == "offline mode")
        v = venue_of(r[col["Nama SPKLU"]])
        out.append(dict(id=str(r[col["ID SPKLU"]]).zfill(5), name=str(r[col["Nama SPKLU"]] or ""), lat=lat, lng=lng,
                        kw=kw, ch=int(r[col["Jumlah Charger"]] or 0), con=int(r[col["Jumlah Connector"]] or 0),
                        st=st, pln=pln, active=active, venue=v, cat=VENUE_CAT[v]))
    return out
