"""Database repositori & sumber terbuka untuk riset SPKLU — sumber kebenaran tunggal (SSOT).

Sunting DI SINI (bukan di resources.json), lalu jalankan:

    python3 resources/catalog.py          # -> resources/resources.json
    python3 resources/inject.py           # -> sisipkan/perbarui tab di index.html

Aturan:
* satu entri per repositori/sumber — tidak ada dobel. Bila satu proyek punya beberapa repo
  turunan yang tidak perlu entri sendiri, taruh di `links`.
* setiap entri wajib punya tepat satu kategori (`cat`); sub-kategori (`sub`) opsional.
* `themes` memakai kunci tema Perpustakaan (papers/library/build.py: CATEGORIES) supaya
  repositori bisa disaring menurut tema riset yang sama dengan naskah.
* `tabs` = tab dashboard yang benar-benar memakai sumber itu (bukan sekadar terkait).
"""
import json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resources", "resources.json")

# --------------------------------------------------------------------------- taksonomi
GROUPS = [
    dict(id="ev", label="EV charging — lapisan domain", icon="🔌",
         desc="Empat lapisan yang menyusun sistem pengisian: di mana chargernya, siapa yang memakai, "
              "kendaraan apa yang datang, dan bagaimana stasiun ditempatkan serta dioperasikan."),
    dict(id="metode", label="Metode & alat analisis", icon="🧮",
         desc="Pustaka yang mengubah data lapisan domain menjadi jawaban: lokasi fasilitas, GIS, "
              "sistem tenaga, cuaca & emisi, statistik/kausal/Bayesian, dan rekayasa data."),
    dict(id="riset", label="Riset, penulisan & belajar", icon="📖",
         desc="Alat kerja peneliti: tinjauan pustaka, LLM untuk riset, penulisan/publikasi/visualisasi, "
              "dan bahan belajar."),
]

CATS = [
    # ---- lapisan domain (dipertahankan persis seperti pengelompokan awal: Lapisan 1–4)
    dict(id="L1", group="ev", label="Lapisan 1 — Lokasi & inventori charger", color="#16305f",
         desc="Registri dan dataset lokasi stasiun pengisian (global & Indonesia), plus statistik stok "
              "infrastruktur. Pembanding langsung untuk master SPKLU PLN di dashboard ini."),
    dict(id="L2", group="ev", label="Lapisan 2 — Sesi charging, demand & mobilitas", color="#3a6ea5",
         desc="Data sesi pengisian riil, dataset permintaan spatio-temporal, simulator sesi, dan pustaka "
              "mobilitas untuk mengestimasi permintaan laten di lokasi tanpa stasiun."),
    dict(id="L3", group="ev", label="Lapisan 3 — Spesifikasi kendaraan", color="#2e9e5b",
         desc="Spesifikasi pengisian kendaraan (baterai, daya AC/DC, konektor, kurva) — menentukan apa "
              "yang sebenarnya dibutuhkan armada dari sebuah SPKLU."),
    dict(id="L4", group="ev", label="Lapisan 4 — Siting, simulasi & operasi", color="#d4af37",
         desc="Dari pemilihan lokasi dan simulasi profil beban sampai perangkat lunak yang menjalankan "
              "stasiun: CSMS, OCPP, firmware, roaming, ISO 15118, metering, dan standar yang mengikatnya.",
         subs=["Siting & optimasi", "Simulasi & profil beban", "CSMS & back-office",
               "Pustaka OCPP", "Server & simulator OCPP", "Firmware, hardware & manajemen energi",
               "Roaming (OCPI/OICP), ISO 15118 & metering", "Standar & protokol", "Katalog & pintu gali"]),
    # ---- metode & alat
    dict(id="siting", group="metode", label="Facility location, siting & equity", color="#8a6fb0",
         desc="Optimasi lokasi fasilitas, ukuran segregasi/ketimpangan, interpolasi areal, grid heksagonal, "
              "routing & geocoding — inti metode penempatan SPKLU dan pengukuran keadilan akses."),
    dict(id="gis", group="metode", label="GIS core & geo-AI", color="#5b937a",
         desc="Fondasi geospasial Python/desktop dan pembelajaran mesin geospasial."),
    dict(id="power", group="metode", label="Sistem tenaga & pemodelan energi", color="#e8742c",
         desc="Aliran daya, optimasi jaringan, simulasi distribusi, pemodelan sistem energi, dan prakiraan "
              "beban — untuk menyambungkan permintaan EV ke kondisi jaringan."),
    dict(id="solar", group="metode", label="Surya, cuaca & emisi", color="#e0a52b",
         desc="Produksi PV, data cuaca, intensitas karbon, dan data energi terbuka — bahan Sun Ice dan "
              "naskah tailpipe-to-smokestack."),
    dict(id="indonesia", group="metode", label="Data Indonesia", color="#d6443c",
         desc="Kode wilayah administratif dan API pendukung untuk menggabungkan data PLN, BPS, dan pelanggan."),
    dict(id="stats", group="metode", label="Statistik, kausal, Bayesian & ML", color="#3a6ea5",
         desc="Pemodelan statistik, inferensi kausal, probabilistik/Bayesian, interpretabilitas, tuning, dan "
              "prakiraan deret waktu."),
    dict(id="dataeng", group="metode", label="Data engineering & experiment tracking", color="#67748c",
         desc="Pemrosesan data besar di laptop dan pelacakan eksperimen agar hasil bisa direproduksi."),
    # ---- riset & penulisan
    dict(id="litrev", group="riset", label="Lit review & manajemen referensi", color="#16305f",
         desc="Penyaringan sistematis, ekstraksi PDF, akses OpenAlex/Scholar, dan pengelola referensi."),
    dict(id="llm", group="riset", label="LLM untuk riset (RAG, deep research)", color="#8a6fb0",
         desc="Model lokal, kerangka RAG, knowledge-graph RAG, dan agen riset otomatis."),
    dict(id="writing", group="riset", label="Menulis, publikasi & visualisasi", color="#2e9e5b",
         desc="Konversi dokumen, typesetting, buku/notebook eksekutabel, gaya plot ilmiah, dan aplikasi demo."),
    dict(id="belajar", group="riset", label="Belajar (mahasiswa)", color="#e0a52b",
         desc="Kurikulum, buku, dan kursus terbuka untuk memperkuat dasar pemrograman, matematika ML, dan LLM."),
]

# Tema riset — kunci & warna sama dengan Perpustakaan (papers/library/build.py: CATEGORIES)
THEMES = {
    "akses":    ["Akses & keadilan infrastruktur pengisian", "#3a6ea5"],
    "jaringan": ["Jaringan distribusi & perencanaan", "#2e9e5b"],
    "emisi":    ["Emisi & dekarbonisasi", "#d6443c"],
    "bisnis":   ["Model bisnis, pasar & kebijakan", "#e0a52b"],
}

# Tab dashboard yang boleh dirujuk oleh `tabs`
TAB_LABELS = {
    "ocm": "Open Charge Map", "evmodels": "EV Models", "insight": "World EV Insight",
    "jaringan": "EV × Jaringan", "capacity": "Capacity Maps", "equity": "Spatial Equity",
    "locint": "Location Intelligence", "p2p": "P2P Charging", "national": "Indonesia",
    "ekuitas": "Peta Ekuitas", "parkir": "Parkir × Charger",
}

ITEMS = []


def R(cat, url, name, desc, role, sub=None, kind=None, themes=(), tabs=(), tags=(), featured=False,
      links=(), alias=None):
    """Daftarkan satu sumber. `kind` diturunkan dari URL bila tidak diberi."""
    if kind is None:
        m = re.match(r"https://github\.com/([^/]+)(?:/([^/]+))?/?$", url)
        if url.startswith("https://github.com/topics/"):
            kind = "topic"
        elif m and m.group(2):
            kind = "repo"
        elif m:
            kind = "org"
        else:
            kind = "portal"
    ident = alias or re.sub(r"^https?://(www\.)?", "", url).rstrip("/").lower()
    ident = re.sub(r"^github\.com/", "", ident)
    path = re.sub(r"^https://github\.com/", "", url).rstrip("/") if kind in ("repo", "org") else None
    ITEMS.append(dict(id=ident, path=path, cat=cat, sub=sub, kind=kind, url=url, name=name, desc=desc, role=role,
                      themes=list(themes), tabs=list(tabs), tags=list(tags), featured=bool(featured),
                      links=[list(l) for l in links]))


# =============================================================================== LAPISAN 1
R("L1", "https://github.com/tarekmasryo/global-ev-infra-dataset", "Global EV Infra Dataset",
  "Dataset global stasiun pengisian EV siap analisis (lokasi, jumlah port, daya, operator, negara), "
  "dibersihkan dari sumber terbuka.",
  "Pembanding global untuk inventori SPKLU: kepadatan charger per kapita dan bauran daya negara lain.",
  themes=["akses"], tags=["dataset", "global"], featured=True)
R("L1", "https://github.com/tarekmasryo/ev-charging-eda", "EV Charging EDA",
  "Notebook eksplorasi data (EDA) turunan Global EV Infra Dataset: sebaran negara, daya, operator.",
  "Templat eksplorasi awal yang bisa ditiru untuk master SPKLU.",
  tags=["notebook", "EDA"])
R("L1", "https://github.com/tarekmasryo/ev-charging-dashboard", "EV Charging Dashboard",
  "Dashboard interaktif turunan dataset yang sama.",
  "Referensi pola tampilan inventori charger.",
  tags=["dashboard"])
R("L1", "https://github.com/aumvats/chargegap", "ChargeGap — charging desert score",
  "Analisis kesenjangan charger di AS: skor 'charging desert' per wilayah dari pasokan charger vs "
  "kebutuhan penduduk/kendaraan.",
  "Analog langsung Equity Priority Index; ide skor defisit per kabupaten untuk RQ2 dan RQ4.",
  themes=["akses"], tags=["equity", "gap analysis"], featured=True)
R("L1", "https://data.mendeley.com/datasets/z2bvd5r574/1", "Dataset SPKLU Indonesia (Mendeley Data)",
  "Dataset lokasi dan atribut stasiun pengisian umum di Indonesia yang dipublikasikan di Mendeley Data.",
  "Pembanding independen terhadap master SPKLU PLN: cek cakupan, koordinat, dan jeda pemutakhiran.",
  kind="dataset", themes=["akses"], tabs=["national"], tags=["Indonesia", "dataset"], featured=True)
R("L1", "https://github.com/openchargemap/ocm-system", "Open Charge Map (ocm-system)",
  "Platform dan API publik Open Charge Map — registri lokasi charger terbuka (crowd-sourced) terbesar di dunia.",
  "Menggerakkan tab Open Charge Map: benchmark SPKLU Jawa Barat terhadap data stasiun global/Indonesia.",
  themes=["akses"], tabs=["ocm", "insight"], tags=["API", "registri"], featured=True,
  links=[["openchargemap (org)", "https://github.com/openchargemap"]])
R("L1", "https://github.com/openchargemap/ocm-data", "OCM Data (ekspor)",
  "Ekspor data Open Charge Map berkala untuk analisis offline.",
  "Dataset massal untuk analisis batch tanpa memukul API.",
  tags=["dataset"])
R("L1", "https://github.com/andreibesleaga/ocm-sdk", "ocm-sdk",
  "SDK klien untuk API Open Charge Map.",
  "Mempercepat integrasi OCM ke skrip analisis.",
  tags=["SDK"])
R("L1", "https://github.com/topics/open-charge-map", "Topic: open-charge-map",
  "Halaman topik GitHub berisi repo yang dibangun di atas Open Charge Map (SDK, klien, analisis).",
  "Pintu gali integrasi OCM lanjutan.",
  tags=["pintu gali"])
R("L1", "https://github.com/ev-map/EVMap", "EVMap",
  "Aplikasi Android peta charger berbasis data Open Charge Map / GoingElectric.",
  "Contoh klien OCM matang; rujukan UX pencari charger untuk aplikasi Ngecas.",
  tags=["Android", "aplikasi"])
R("L1", "https://github.com/globalevdata", "Global EV Data Initiative (org)",
  "Organisasi GitHub Global EV Data Initiative: tooling WebGIS lokasi charger.",
  "Rujukan pemetaan charger berbasis web.",
  tags=["WebGIS"],
  links=[["EVChargerSite (Vue WebGIS)", "https://github.com/globalevdata/globalevdata.github.io"],
         ["USCharger / ChargeFlow", "https://github.com/globalevdata/USCharger"],
         ["GlobalCharger (templat webGIS)", "https://github.com/globalevdata/GlobalCharger"]])
R("L1", "https://openchargemap.org", "openchargemap.org (portal & kunci API)",
  "Situs Open Charge Map: peta, unduhan, dan pendaftaran kunci API gratis.",
  "Kunci API diperlukan oleh tab Open Charge Map.",
  kind="portal", tabs=["ocm"], tags=["portal"])
R("L1", "https://www.iea.org/reports/global-ev-outlook-2024", "IEA Global EV Outlook",
  "Laporan tahunan IEA: stok, penjualan, dan infrastruktur pengisian EV global per wilayah.",
  "Angka konteks global di tab World EV Insight dan Global Benchmark.",
  kind="portal", tabs=["insight"], tags=["statistik", "global"], featured=True)
R("L1", "https://alternative-fuels-observatory.ec.europa.eu", "EAFO — European Alternative Fuels Observatory",
  "Data terbuka Uni Eropa tentang armada EV dan titik pengisian per negara.",
  "Pembanding rasio EV per charger untuk benchmark kebijakan.",
  kind="portal", themes=["bisnis"], tags=["statistik", "Eropa"])
R("L1", "https://afdc.energy.gov/fuels/electricity-locations", "AFDC — US DOE Alternative Fuels Data Center",
  "Pencari stasiun dan dataset terbuka infrastruktur pengisian Amerika Serikat.",
  "Sumber data yang dipakai ChargeGap; pembanding struktur atribut stasiun.",
  kind="portal", tags=["dataset", "AS"])

# =============================================================================== LAPISAN 2
R("L2", "https://github.com/IntelligentSystemsLab/ST-EVCDP", "ST-EVCDP",
  "Dataset dan kode prediksi permintaan pengisian EV spatio-temporal (Shenzhen): okupansi charger per "
  "jam, harga, dan kovariat lingkungan.",
  "Pola jam/musiman untuk model permintaan RQ1; baseline prediksi yang bisa dibandingkan dengan Jawa Barat.",
  themes=["akses", "jaringan"], tags=["dataset", "prediksi", "spatio-temporal"], featured=True)
R("L2", "https://github.com/IntelligentSystemsLab/UrbanEV", "UrbanEV",
  "Dataset terbuka permintaan pengisian skala kota (Shenzhen, beberapa bulan, ribuan stasiun) lengkap "
  "dengan benchmark model prediksi.",
  "Data pembanding terbesar untuk validasi eksternal model permintaan per stasiun.",
  themes=["akses", "jaringan"], tags=["dataset", "benchmark"], featured=True)
R("L2", "https://github.com/zach401/acnportal", "ACN-Portal (ACN-Data + ACN-Sim)",
  "API Python untuk ACN-Data (sesi pengisian riil Caltech/JPL) dan simulator ACN-Sim untuk menguji "
  "algoritma penjadwalan pengisian.",
  "Uji algoritma smart charging / penjadwalan malam (P2P) sebelum diterapkan pada data SPKLU.",
  themes=["jaringan", "bisnis"], tabs=["p2p"], tags=["simulator", "dataset"], featured=True,
  links=[["ACN-Data (unduhan & API)", "https://ev.caltech.edu/dataset"]])
R("L2", "https://github.com/yvenn-amara/ev-load-open-data", "EV Load Open Data (kurasi review)",
  "Kurasi dataset beban/sesi pengisian EV terbuka dari tinjauan Amara-Ouali dkk., beserta kode pembaca.",
  "Peta jalan dataset sesi terbuka dunia; pembanding untuk 100 ribu sesi Jawa Barat.",
  themes=["akses"], tags=["dataset", "review"], featured=True)
R("L2", "https://github.com/Indigma-Innovations/federated-learning-ev-charging-demand",
  "Federated learning — EV charging demand",
  "Prediksi permintaan pengisian dengan federated learning di atas ACN-Data.",
  "Skema pelatihan lintas operator tanpa berbagi data mentah — relevan bila data PLN dan swasta tak bisa disatukan.",
  themes=["bisnis"], tags=["federated learning"])
R("L2", "https://github.com/anitagraser/movingpandas", "MovingPandas",
  "Analisis trajektori pergerakan di atas pandas/GeoPandas (kecepatan, berhenti, segmentasi).",
  "Mengolah jejak perjalanan / asal-tujuan untuk estimasi permintaan laten di lokasi tanpa stasiun.",
  themes=["akses"], tags=["mobilitas", "trajektori"])
R("L2", "https://github.com/scikit-mobility/scikit-mobility", "scikit-mobility",
  "Analisis dan pembangkitan data mobilitas manusia: trajektori, aliran, model gravitasi/radiasi.",
  "Model gravitasi/radiasi sebagai prior permintaan antar-wilayah untuk RQ1.",
  themes=["akses"], tags=["mobilitas", "model gravitasi"])

# =============================================================================== LAPISAN 3
R("L3", "https://github.com/open-ev-data/open-ev-data-dataset", "Open EV Data (dataset)",
  "Dataset spesifikasi pengisian EV (kapasitas baterai, daya AC/DC, port, kurva DC) yang dirilis berversi "
  "lewat GitHub Releases.",
  "Menggerakkan tab EV Models; memadankan daya DC SPKLU dengan armada yang beredar.",
  tabs=["evmodels", "insight"], tags=["dataset", "spesifikasi"], featured=True,
  links=[["open-ev-data (org: api & ui)", "https://github.com/open-ev-data"]])
R("L3", "https://github.com/chargeprice/open-ev-data", "open-ev-data (chargeprice, versi asal)",
  "Versi asal dataset dari Chargeprice: skema dan sampel yang menjadi acuan.",
  "Skema dasar dan fallback offline tab EV Models.",
  tabs=["evmodels"], tags=["dataset", "skema"])

# =============================================================================== LAPISAN 4
S1, S2, S3, S4, S5, S6, S7, S8, S9 = CATS[3]["subs"]
R("L4", "https://github.com/ccubc/ChargeUp", "ChargeUp",
  "Proyek siting stasiun pengisian berbasis optimasi (studi kasus kota Kanada): POI, estimasi permintaan, "
  "pemilihan lokasi.",
  "Templat pipeline siting ujung-ke-ujung yang mudah dipindahkan ke Jawa Barat.",
  sub=S1, themes=["akses"], tags=["siting", "optimasi"], featured=True)
R("L4", "https://github.com/EVKG", "EVKG — EV Knowledge Graph (org)",
  "Knowledge graph yang menautkan stasiun pengisian, kendaraan, dan jaringan listrik dalam satu skema.",
  "Skema integrasi lintas lapisan; inspirasi model data dashboard ini.",
  sub=S1, themes=["jaringan"], tags=["knowledge graph"], featured=True)
R("L4", "https://github.com/rl-institut/simbev", "SimBEV",
  "Simulasi profil pengisian armada EV dari perilaku mobilitas (Reiner Lemoine Institut).",
  "Membangkitkan profil beban EV untuk skenario jaringan di Capacity Maps dan naskah DNDP.",
  sub=S2, themes=["jaringan"], tabs=["capacity"], tags=["simulasi", "profil beban"], featured=True)
R("L4", "https://github.com/steve-community/steve", "SteVe",
  "CSMS OCPP 1.6 sumber terbuka yang matang (Java).",
  "Back-office rujukan untuk mengoperasikan charge point bergaya SPKLU.",
  sub=S3, tags=["CSMS", "OCPP 1.6"], featured=True,
  links=[["steve-pluggable", "https://github.com/parklapp/steve-pluggable"],
         ["ocpp-jaxb", "https://github.com/steve-community/ocpp-jaxb"]])
R("L4", "https://github.com/citrineos/citrineos-core", "CitrineOS",
  "CSMS OCPP 2.0.1 modern (TypeScript) dari organisasi CitrineOS.",
  "Rujukan sistem manajemen generasi baru; punya modul OCPI untuk roaming.",
  sub=S3, tags=["CSMS", "OCPP 2.0.1"], featured=True,
  links=[["citrineos (umbrella)", "https://github.com/citrineos/citrineos"],
         ["citrineos-ocpi", "https://github.com/citrineos/citrineos-ocpi"]])
R("L4", "https://github.com/thoughtworks/maeve-csms", "MaEVe",
  "CSMS rujukan OCPP 2.0.1 dengan OCPI dan ISO 15118 Plug&Charge (Thoughtworks).",
  "Contoh Plug&Charge ujung-ke-ujung.",
  sub=S3, tags=["CSMS", "Plug&Charge"])
R("L4", "https://github.com/juherr/evolve", "evolve",
  "CSMS OCPP sumber terbuka turunan SteVe.",
  "Alternatif back-office ringan.", sub=S3, tags=["CSMS"])
R("L4", "https://github.com/lbbrhzn/ocpp", "Home Assistant OCPP",
  "Integrasi OCPP untuk Home Assistant: mengelola charger rumah lewat OCPP.",
  "Prototipe kendali charger rumah untuk skema sewa P2P.",
  sub=S3, themes=["bisnis"], tabs=["p2p"], tags=["Home Assistant", "charger rumah"])
R("L4", "https://github.com/sap-labs-france/ev-server", "SAP e-Mobility (ev-server)",
  "Backend CSMS terbuka dari SAP Labs France; ada frontend ev-dashboard.",
  "Rujukan arsitektur CSMS skala perusahaan.",
  sub=S3, tags=["CSMS"], links=[["ev-dashboard", "https://github.com/sap-labs-france/ev-dashboard"]])
R("L4", "https://github.com/motown-io/motown", "Motown",
  "Platform back-office OCPP (Java) yang lebih lama.",
  "Rujukan historis desain CSMS.", sub=S3, tags=["CSMS"])
for u, n, d in [
    ("https://github.com/EVerest/libocpp", "libocpp (EVerest)", "Implementasi C++ OCPP 1.6, 2.0.1, dan 2.1."),
    ("https://github.com/mobilityhouse/ocpp", "ocpp (Python, Mobility House)", "Pustaka OCPP Python (1.6 & 2.0.1) yang paling banyak dipakai."),
    ("https://github.com/ChargeTimeEU/Java-OCA-OCPP", "Java-OCA-OCPP", "Pustaka OCPP Java klien & server."),
    ("https://github.com/lorenzodonini/ocpp-go", "ocpp-go", "Pustaka OCPP 1.6/2.0.1 untuk Go."),
    ("https://github.com/matth-x/MicroOcpp", "MicroOcpp", "Klien OCPP untuk mikrokontroler (ESP32/Arduino)."),
    ("https://github.com/voltbras/ts-ocpp", "ts-ocpp", "Pustaka OCPP TypeScript."),
    ("https://github.com/IZIVIA/ocpp-toolkit", "ocpp-toolkit (IZIVIA)", "Toolkit OCPP Kotlin/JVM."),
    ("https://github.com/codelabsab/rust-ocpp", "rust-ocpp", "Tipe & pustaka OCPP untuk Rust."),
]:
    R("L4", u, n, d, "Bahan membangun prototipe charge point / CSMS uji.", sub=S4, tags=["OCPP", "pustaka"])
for u, n, d in [
    ("https://github.com/dallmann-consulting/OCPP.Core", "OCPP.Core", "Server OCPP .NET dengan UI manajemen."),
    ("https://github.com/v-bodnar/ocpp-server", "ocpp-server", "Server OCPP ringan (Java)."),
    ("https://github.com/gregszalay/ocpp-csms", "ocpp-csms", "CSMS OCPP sederhana untuk eksperimen."),
    ("https://github.com/codelabsab/ocpp-csms-server", "ocpp-csms-server", "Server CSMS Rust."),
]:
    R("L4", u, n, d, "Server uji untuk simulasi operasi stasiun.", sub=S5, tags=["OCPP", "server"])
for u, n, d in [
    ("https://github.com/SAP/e-mobility-charging-stations-simulator", "SAP charging-stations simulator", "Simulator banyak charge point OCPP untuk uji beban CSMS."),
    ("https://github.com/matth-x/MicroOcppSimulator", "MicroOcppSimulator", "Simulator charge point berbasis MicroOcpp."),
    ("https://github.com/evbox/station-simulator", "EVBox station-simulator", "Simulator stasiun OCPP 2.0.1."),
    ("https://github.com/solidstudiosh/ocpp-virtual-charge-point", "ocpp-virtual-charge-point", "Charge point virtual OCPP 1.6/2.0.1 (Node)."),
    ("https://github.com/ShellRechargeSolutionsEU/docile-charge-point", "docile-charge-point", "Charge point OCPP yang bisa diskrip (Scala)."),
    ("https://github.com/victormunoz/OCPP-1.6-Chargebox-Simulator", "OCPP 1.6 Chargebox Simulator", "Simulator chargebox OCPP 1.6 berbasis browser."),
]:
    R("L4", u, n, d, "Membangkitkan sesi sintetis untuk menguji CSMS / model permintaan.", sub=S5, tags=["OCPP", "simulator"])
R("L4", "https://github.com/openevse", "OpenEVSE (org)",
  "Organisasi hardware EVSE (charger AC) sumber terbuka; firmware WiFi/ESP32 dengan manajemen beban, MQTT, OCPP.",
  "Basis charger rumah terbuka untuk uji coba sewa charger P2P.",
  sub=S6, themes=["bisnis"], tabs=["p2p"], tags=["hardware", "firmware"], featured=True,
  links=[["openevse_esp32_firmware", "https://github.com/OpenEVSE/openevse_esp32_firmware"]])
R("L4", "https://github.com/EVerest/EVerest", "EVerest (LF Energy)",
  "Stack perangkat lunak stasiun pengisian lengkap dari firmware sampai cloud (OCPP, ISO 15118).",
  "Rujukan charger terbuka ujung-ke-ujung.",
  sub=S6, tags=["stack charger", "LF Energy"], featured=True)
R("L4", "https://github.com/EVerest/everest-core", "everest-core",
  "Modul inti dan runtime stack EVerest.",
  "Blok bangunan pengendali charger modular.", sub=S6, tags=["stack charger"])
R("L4", "https://github.com/SmartEVSE/SmartEVSE-3", "SmartEVSE-3",
  "Pengendali EVSE terbuka dengan load balancing dan solar charging.",
  "Alternatif OpenEVSE untuk charger rumah.", sub=S6, tags=["hardware"])
R("L4", "https://github.com/dzurikmiroslav/esp32-evse", "esp32-evse",
  "Firmware EVSE berbasis ESP32.", "Prototipe charger murah.", sub=S6, tags=["firmware"])
R("L4", "https://github.com/evcc-io/evcc", "evcc",
  "Manajer energi/pengisian sadar-surya untuk rumah (Go), mendukung ratusan charger & inverter.",
  "Logika pengisian mengikuti produksi PV — inti skema Sun Ice.",
  sub=S6, themes=["emisi", "bisnis"], tags=["manajemen energi", "solar"], featured=True)
R("L4", "https://github.com/SolarNetwork/solarnetwork-central", "SolarNetwork",
  "Platform pengumpulan data energi terdistribusi.",
  "Telemetri PV + charger untuk pilot.", sub=S6, tags=["telemetri"])
for u, n, d in [
    ("https://github.com/ChargeMap/ocpi-protocol", "ocpi-protocol (ChargeMap)", "Implementasi OCPI (roaming CPO ↔ eMSP)."),
    ("https://github.com/IZIVIA/ocpi-toolkit", "ocpi-toolkit (IZIVIA)", "Toolkit OCPI Kotlin."),
    ("https://github.com/TECHS-Technological-Solutions/ocpi", "ocpi (TECHS)", "Pustaka OCPI Python."),
    ("https://github.com/ocpi/ocpi-tool", "ocpi-tool", "Alat uji/ekspor OCPI."),
    ("https://github.com/tandemdrive/ocpi-tariffs", "ocpi-tariffs", "Perhitungan tarif OCPI (Rust)."),
    ("https://github.com/hubject/oicp", "OICP (Hubject)", "Spesifikasi Open InterCharge Protocol untuk roaming Hubject."),
    ("https://github.com/energywebfoundation/ocn-node", "OCN node (Energy Web)", "Node Open Charging Network — roaming terdesentralisasi."),
]:
    R("L4", u, n, d, "Model data tarif & roaming antar operator SPKLU (PLN, swasta).", sub=S7,
      themes=["bisnis"], tags=["OCPI", "roaming"])
for u, n, d in [
    ("https://github.com/EVerest/libiso15118", "libiso15118 (EVerest)", "Implementasi ISO 15118-2/-20 C++."),
    ("https://github.com/SwitchEV/RISE-V2G", "RISE-V2G", "Implementasi rujukan ISO 15118 (Java)."),
    ("https://github.com/EcoG-io/iso15118", "iso15118 (EcoG)", "Implementasi ISO 15118 Python."),
    ("https://github.com/uhi22/pyPLC", "pyPLC", "Eksperimen komunikasi PLC kendaraan–charger."),
    ("https://github.com/FlUxIuS/V2GInjector", "V2GInjector", "Alat riset keamanan komunikasi V2G."),
]:
    R("L4", u, n, d, "Plug&Charge dan V2G — kesiapan SPKLU generasi berikut.", sub=S7, tags=["ISO 15118", "V2G"])
for u, n, d in [
    ("https://github.com/SAFE-eV/OCMF-Open-Charge-Metering-Format", "OCMF (SAFE e.V.)", "Spesifikasi Open Charge Metering Format — nilai meter bertanda tangan."),
    ("https://github.com/SAFE-eV/transparenzsoftware", "Transparenzsoftware", "Perangkat lunak verifikasi meter bertanda tangan (Eichrecht)."),
    ("https://github.com/ChargePi/ocmf-go", "ocmf-go", "Pustaka OCMF Go."),
    ("https://github.com/road-labs/ocmf-js", "ocmf-js", "Pustaka OCMF JavaScript."),
]:
    R("L4", u, n, d, "Integritas kWh termeter — dasar kepercayaan transaksi (termasuk skema P2P).", sub=S7,
      themes=["bisnis"], tags=["OCMF", "metering"])
R("L4", "https://github.com/dalathegreat/Battery-Emulator", "Battery-Emulator",
  "Emulasi baterai EV untuk penyimpanan stasioner.", "Pemanfaatan baterai bekas untuk buffer SPKLU.",
  sub=S7, themes=["jaringan"], tags=["baterai"])
R("L4", "https://github.com/mnh-jansson/open-battery-information", "Open Battery Information",
  "Diagnostik baterai EV terbuka.", "Data degradasi baterai untuk model kurva pengisian.",
  sub=S7, tags=["baterai"])
R("L4", "https://www.openchargealliance.org/", "OCPP — Open Charge Point Protocol",
  "Protokol charge point ↔ sistem manajemen (Open Charge Alliance). Versi 1.6, 2.0.1, 2.1.",
  "Protokol de-facto; menentukan data sesi apa yang bisa dikumpulkan dari SPKLU.",
  sub=S8, kind="standard", tags=["standar"], featured=True)
R("L4", "https://evroaming.org/", "OCPI — Open Charge Point Interface",
  "Protokol roaming antar operator (CPO ↔ eMSP), 2.1.1 → 2.3.0.",
  "Kerangka interoperabilitas tarif & lokasi antar operator SPKLU.",
  sub=S8, kind="standard", themes=["bisnis"], tags=["standar"])
R("L4", "https://en.wikipedia.org/wiki/ISO_15118", "ISO 15118",
  "Standar komunikasi kendaraan ↔ charger: Plug & Charge dan V2G.",
  "Peta jalan fitur SPKLU generasi berikut.", sub=S8, kind="standard", tags=["standar"])
R("L4", "https://github.com/juherr/awesome-ev-charging", "awesome-ev-charging",
  "Indeks terkurasi ekosistem sumber terbuka EV charging.",
  "Sumber asal katalog CSMS/OCPP/firmware di database ini.",
  sub=S9, tags=["katalog"], featured=True)
for slug, note in [
    ("ev-charging-infrastructure", "Di sini biasanya muncul repo kecil seperti penilaian situs Hamburg dan aksesibilitas Norwegia."),
    ("ev-charging-stations", "Di sini biasanya muncul repo Varanasi GIS-MCDM dan studi aksesibilitas Norwegia."),
    ("ev-charging-optimization", "Repo optimasi penjadwalan/siting, termasuk lingkungan RL seperti Chargym."),
    ("electric-vehicle-charging-station", "Varian penamaan; banyak proyek mahasiswa & aplikasi pencari charger."),
    ("charging-stations", "Topik paling umum; saring dengan kata kunci GIS/optimization."),
]:
    R("L4", "https://github.com/topics/" + slug, "Topic: " + slug,
      "Halaman topik GitHub untuk menggali repo kecil. " + note,
      "Pintu gali — URL repo Varanasi/Norway/Hamburg/Chargym belum diverifikasi, jadi tidak dimasukkan sebagai entri.",
      sub=S9, tags=["pintu gali"])

# =============================================================================== METODE
R("siting", "https://github.com/pysal/spopt", "spopt (PySAL)",
  "Optimasi spasial: p-median, LSCP, MCLP, p-center, regionalisasi.",
  "Inti formulasi siting SPKLU — cakupan vs kapabilitas (CUPUM bab 1); fungsi tujuan sebagai keputusan perencanaan.",
  themes=["akses"], tabs=["locint"], tags=["facility location"], featured=True)
R("siting", "https://github.com/pysal/segregation", "segregation (PySAL)",
  "Indeks segregasi spasial & non-spasial beserta inferensi.",
  "Mengukur ketimpangan horizontal/vertikal akses charger (RQ4).",
  themes=["akses"], tabs=["equity"], tags=["equity"], featured=True)
R("siting", "https://github.com/pysal/tobler", "tobler (PySAL)",
  "Interpolasi areal dan dasimetrik antar unit spasial.",
  "Memindahkan populasi BPS ke sel grid 5 km / area layanan stasiun.",
  themes=["akses"], tabs=["capacity"], tags=["interpolasi"])
R("siting", "https://github.com/pysal/momepy", "momepy (PySAL)",
  "Morfometri urban: bentuk kota dari jaringan jalan dan bangunan.",
  "Fitur morfologi kota sebagai kovariat permintaan laten.",
  themes=["akses"], tags=["morfologi"])
R("siting", "https://github.com/uber/h3", "H3 (Uber)",
  "Sistem grid heksagonal hierarkis untuk indeks spasial.",
  "Sel analisis Peta Ekuitas (res 6 nasional, agregat res 5) dan alternatif sel 0,045° untuk agregasi permintaan × headroom.",
  themes=["akses", "jaringan"], tabs=["ekuitas"], tags=["grid", "heksagon"], featured=True,
  links=[["h3-js (dipakai di browser, di-vendor di equitymap/vendor)", "https://github.com/uber/h3-js"]])
R("siting", "https://www.tpl.org/park-data-downloads", "ParkServe / ParkScore data (Trust for Public Land)",
  "Basis data taman >15.000 kota AS: poligon taman, area layanan 10 menit jalan kaki (jaringan jalan), park priority "
  "areas (blok sensus di luar jangkauan), dan indeks ParkScore 100 kota (akses, luas, investasi, fasilitas, keadilan).",
  "Cetak biru tab Parkir × Charger: ukuran akses 10 menit, area prioritas sebagai kantong penduduk di luar jangkauan, "
  "indeks kota relatif berkategori; intisarinya di Perpustakaan (bacaan-parkserve).",
  kind="portal", themes=["akses"], tabs=["parkir"], tags=["akses", "10-minute walk", "indeks kota", "AS"], featured=True,
  links=[["Tentang basis data ParkServe", "https://www.tpl.org/parkserve/about"],
         ["ArcGIS REST — 10-minute walk service areas",
          "https://services9.arcgis.com/FF3qnCUixr5w9JQi/arcgis/rest/services/ServiceAreas_Clip/FeatureServer/0"],
         ["Galeri alat 10-Minute Walk (TPL GIS)", "https://web.tplgis.org/10minwalk-project-gallery/"]])
R("siting", "https://evmap.climateplans.org/", "EV Equity Roadmap (CLEE UC Berkeley)",
  "Peta keputusan terbuka: piksel 100 m di seluruh California diwarnai lapisan prioritas (CalEnviroScreen, pendapatan, "
  "penyewa/hunian multi-keluarga, akses charger) dan kelayakan (hosting capacity utilitas, dana federal, ruang publik), "
  "plus kandidat hub komunitas.",
  "Cetak biru tab Peta Ekuitas: pemisahan prioritas × kelayakan, normalisasi per yurisdiksi, bobot sebagai keluaran; "
  "intisarinya ada di Perpustakaan (bacaan-evmap).",
  kind="portal", themes=["akses", "bisnis"], tabs=["ekuitas", "equity"], tags=["equity", "siting", "California"], featured=True,
  links=[["CLEE EV Equity Initiative — mapping", "https://www.law.berkeley.edu/research/clee/ev-equity/mapping/"],
         ["Equitable EV Action Plan Framework (PDF, Des 2024)",
          "https://www.law.berkeley.edu/wp-content/uploads/archive/2024/12/Equitable-EV-Action-Plan-Framework_CLEE.pdf"],
         ["Legal Planet — Mapping City Priorities (2023)",
          "https://legal-planet.org/2023/06/23/mapping-city-priorities-for-an-equitable-ev-infrastructure-rollout/"]])
R("siting", "https://github.com/Project-OSRM/osrm-backend", "OSRM",
  "Mesin routing OSM sangat cepat: rute, matriks jarak/waktu.",
  "Matriks waktu tempuh ke SPKLU terdekat untuk aksesibilitas (2SFCA).",
  themes=["akses"], tags=["routing"], featured=True)
R("siting", "https://github.com/valhalla/valhalla", "Valhalla",
  "Mesin routing multimoda OSM dengan isochrone dan matriks.",
  "Isochrone 10/15 menit sebagai area layanan stasiun.",
  themes=["akses"], tags=["routing", "isochrone"])
R("siting", "https://github.com/GIScience/openrouteservice", "openrouteservice",
  "Layanan routing, isochrone, dan matriks (API publik & self-host).",
  "Cara termudah mendapat isochrone tanpa memasang mesin sendiri.",
  themes=["akses"], tags=["routing", "API"])
R("siting", "https://github.com/osm-search/Nominatim", "Nominatim",
  "Geocoder OpenStreetMap.", "Geokode alamat pelanggan KBLBB dan SPKLU.",
  tags=["geocoding"])
R("siting", "https://github.com/geopy/geopy", "geopy",
  "Klien Python untuk banyak geocoder dan jarak geodesik.",
  "Geocoding batch & jarak haversine di pipeline.", tags=["geocoding"])

R("gis", "https://github.com/geopandas/geopandas", "GeoPandas", "DataFrame geospasial untuk Python.",
  "Tulang punggung semua pengolahan spasial di repositori ini.", tags=["inti"], featured=True)
R("gis", "https://github.com/shapely/shapely", "Shapely", "Geometri planar (buffer, overlay, predikat).",
  "Operasi geometri dasar.", tags=["inti"])
R("gis", "https://github.com/rasterio/rasterio", "Rasterio", "Baca/tulis raster geospasial.",
  "Populasi grid (WorldPop) dan raster lain sebagai kovariat.", tags=["raster"])
R("gis", "https://github.com/qgis/QGIS", "QGIS", "GIS desktop sumber terbuka.",
  "Inspeksi visual dan kartografi untuk naskah.", tags=["desktop"], featured=True)
R("gis", "https://github.com/keplergl/kepler.gl", "kepler.gl", "Visualisasi geospasial skala besar di browser.",
  "Eksplorasi cepat titik transaksi & pelanggan.", tags=["visualisasi"])
R("gis", "https://github.com/microsoft/torchgeo", "TorchGeo", "Dataset & model deep learning geospasial (PyTorch).",
  "Ekstraksi fitur citra satelit untuk permintaan laten.", tags=["geo-AI"])
R("gis", "https://github.com/opengeos/geoai", "GeoAI (opengeos)", "Alat AI geospasial: segmentasi, deteksi objek.",
  "Deteksi bangunan/parkir dari citra untuk kandidat lokasi.", tags=["geo-AI"])
R("gis", "https://github.com/sacridini/Awesome-Geospatial", "Awesome Geospatial", "Daftar kurasi pustaka geospasial.",
  "Pintu gali alat GIS lain.", tags=["katalog"])

R("power", "https://github.com/MATPOWER/matpower", "MATPOWER", "Aliran daya & OPF (MATLAB/Octave).",
  "Uji dampak beban EV pada penyulang dan GI.", themes=["jaringan"], tags=["aliran daya"])
R("power", "https://github.com/lanl-ansi/PowerModels.jl", "PowerModels.jl", "Optimasi jaringan tenaga di Julia (OPF, relaksasi).",
  "Formulasi OPF untuk hosting capacity.", themes=["jaringan"], tags=["OPF", "Julia"])
R("power", "https://github.com/SanPen/GridCal", "GridCal", "Simulasi & analisis jaringan (GUI + Python).",
  "Aliran daya distribusi untuk headroom trafo.", themes=["jaringan"], tabs=["jaringan"], tags=["aliran daya"], featured=True)
R("power", "https://github.com/dss-extensions/dss_python", "OpenDSS (dss_python)", "OpenDSS untuk Python: simulasi distribusi time-series.",
  "Simulasi beban EV per jam pada penyulang (naskah DNDP, Capacity Maps).",
  themes=["jaringan"], tabs=["jaringan", "capacity"], tags=["distribusi", "time-series"], featured=True)
R("power", "https://github.com/Grid2op/grid2op", "Grid2Op", "Lingkungan RL untuk operasi jaringan.",
  "Eksperimen kendali beban EV berbasis RL.", themes=["jaringan"], tags=["RL"])
R("power", "https://github.com/PyPSA/linopy", "linopy (PyPSA)", "Pemodel optimasi linear cepat berbasis xarray.",
  "Formulasi optimasi besar (siting + jaringan) yang ringkas.", themes=["jaringan"], tags=["optimasi"])
R("power", "https://github.com/calliope-project/calliope", "Calliope", "Kerangka pemodelan sistem energi multi-skala.",
  "Skenario sistem energi provinsi.", themes=["jaringan", "emisi"], tags=["sistem energi"])
R("power", "https://github.com/OSeMOSYS/OSeMOSYS", "OSeMOSYS", "Pemodelan sistem energi jangka panjang.",
  "Skenario bauran pembangkit untuk faktor emisi 2030.", themes=["emisi"], tags=["sistem energi"])
R("power", "https://github.com/OpenSTEF/openstef", "OpenSTEF (LF Energy)", "Prakiraan beban jangka pendek otomatis.",
  "Prakiraan energi per stasiun/penyulang (RQ1, DNDP).", themes=["jaringan"], tags=["prakiraan"], featured=True)
R("power", "https://github.com/NREL/OpenStudio", "OpenStudio (NREL)", "Pemodelan energi bangunan (EnergyPlus).",
  "Beban gedung tempat SPKLU menumpang (mal, kantor).", themes=["jaringan"], tags=["bangunan"])

R("solar", "https://github.com/pvlib/pvlib-python", "pvlib-python", "Pemodelan sistem fotovoltaik.",
  "Profil produksi PV untuk skema solar charging (Sun Ice).", themes=["emisi"], tags=["PV"], featured=True)
R("solar", "https://github.com/NREL/pysam", "PySAM (NREL)", "API System Advisor Model: tekno-ekonomi PV/baterai.",
  "Kelayakan finansial PV + penyimpanan di SPKLU.", themes=["emisi", "bisnis"], tags=["PV", "tekno-ekonomi"])
R("solar", "https://github.com/open-meteo/open-meteo", "Open-Meteo", "API cuaca & radiasi historis/prakiraan gratis.",
  "Radiasi dan suhu untuk model PV dan permintaan.", tags=["cuaca", "API"])
R("solar", "https://github.com/electricitymaps/electricitymaps-contrib", "Electricity Maps", "Intensitas karbon listrik per zona (real-time & historis).",
  "Pembanding faktor emisi marjinal Jamali (naskah tailpipe-to-smokestack).",
  themes=["emisi"], tabs=["jaringan"], tags=["karbon"], featured=True)
R("solar", "https://github.com/Open-Power-System-Data/datapackage_timeseries", "Open Power System Data — time series",
  "Deret waktu beban & pembangkitan Eropa.", "Pembanding profil beban harian.", themes=["jaringan"], tags=["deret waktu"])
R("solar", "https://github.com/owid/etl", "Our World in Data — ETL", "Pipeline data OWID (energi, emisi, EV).",
  "Deret panjang penjualan EV dan bauran energi negara.", themes=["emisi", "bisnis"], tags=["data global"])

R("indonesia", "https://data.humdata.org/dataset/kontur-population-indonesia", "Kontur Population — Indonesia (H3 res 8)",
  "Populasi per heksagon H3 resolusi 8 (~0,7 km²) seluruh Indonesia, turunan GHSL + jejak bangunan Microsoft + HRSL; "
  "GeoPackage, CC BY 4.0, rilis 2023-11-01.",
  "Penyebut penduduk Peta Ekuitas: 874.919 heksagon → 47.793 heksagon res 6 (277,5 juta jiwa); diunduh equitymap/fetch.py "
  "dari bucket S3 publik Kontur.",
  kind="dataset", themes=["akses"], tabs=["ekuitas"], tags=["populasi", "H3", "dataset"], featured=True,
  links=[["Bucket S3 publik (gpkg.gz)",
          "https://geodata-eu-central-1-kontur-public.s3.amazonaws.com/kontur_datasets/kontur_population_ID_20231101.gpkg.gz"]])
R("indonesia", "https://www.geoboundaries.org/", "geoBoundaries (gbOpen IDN ADM1/ADM2)",
  "Batas administratif terbuka seluruh dunia; untuk Indonesia 34 provinsi (ADM1) dan 515 kabupaten/kota (ADM2), "
  "CC BY 4.0, versi simplified.",
  "Menempelkan tiap heksagon dan situs SPKLU ke kabupaten/kota dan provinsi di Peta Ekuitas (equitymap/fetch.py).",
  kind="dataset", themes=["akses"], tabs=["ekuitas"], tags=["batas wilayah", "GeoJSON"],
  links=[["Repositori data (GitHub, LFS)", "https://github.com/wmgeolab/geoBoundaries"]])
R("indonesia", "https://github.com/cahyadsn/wilayah", "wilayah (cahyadsn)", "Kode & nama wilayah administratif Indonesia (Kepmendagri) beserta batas.",
  "Kunci gabung kabupaten/kota untuk BPS, PLN, dan pelanggan KBLBB.", themes=["akses"], tabs=["national"], tags=["wilayah"], featured=True)
R("indonesia", "https://github.com/emsifa/api-wilayah-indonesia", "api-wilayah-indonesia", "API statis provinsi/kabupaten/kecamatan/desa.",
  "Pengisian otomatis form wilayah di aplikasi.", tags=["API"])

R("stats", "https://github.com/scikit-learn/scikit-learn", "scikit-learn", "Pustaka ML klasik.",
  "Model pendorong Service Quality Index dan baseline prediksi.", tags=["ML"], featured=True)
R("stats", "https://github.com/statsmodels/statsmodels", "statsmodels", "Regresi, GLM, deret waktu, uji statistik.",
  "Model ekonometrik untuk paper equity dan siting.", themes=["akses"], tags=["statistik"], featured=True)
R("stats", "https://github.com/pyro-ppl/numpyro", "NumPyro", "Pemrograman probabilistik di JAX (NUTS cepat).",
  "Model Bayesian permintaan laten vs pasokan (poster BAM 2026).", themes=["akses"], tabs=["locint"], tags=["Bayesian"], featured=True)
R("stats", "https://github.com/stan-dev/stan", "Stan", "Bahasa & sampler inferensi Bayesian.",
  "Alternatif NumPyro untuk model hierarkis spasial.", themes=["akses"], tags=["Bayesian"])
R("stats", "https://github.com/py-why/dowhy", "DoWhy", "Kerangka inferensi kausal empat langkah (model, identifikasi, estimasi, refutasi).",
  "RQ3: apakah stasiun baru menciptakan atau memindahkan permintaan.", themes=["akses"], tabs=["equity"], tags=["kausal"], featured=True)
R("stats", "https://github.com/microsoft/EconML", "EconML", "Estimasi efek heterogen (DML, causal forest).",
  "Efek heterogen pembangunan stasiun menurut pendapatan/urban-rural (RQ4).", themes=["akses"], tags=["kausal"])
R("stats", "https://github.com/shap/shap", "SHAP", "Interpretasi model berbasis nilai Shapley.",
  "Menjelaskan pendorong konsumsi per stasiun.", tags=["interpretabilitas"])
R("stats", "https://github.com/interpretml/interpret", "InterpretML", "Model glass-box (EBM) & alat interpretasi.",
  "Model dapat-dijelaskan untuk pembuat kebijakan.", tags=["interpretabilitas"])
R("stats", "https://github.com/optuna/optuna", "Optuna", "Optimasi hiperparameter.",
  "Tuning model prediksi permintaan.", tags=["tuning"])
R("stats", "https://github.com/Nixtla/statsforecast", "StatsForecast (Nixtla)", "Model statistik deret waktu cepat (ETS, ARIMA, Theta).",
  "Prakiraan konsumsi bulanan per stasiun.", themes=["jaringan"], tags=["deret waktu"])
R("stats", "https://github.com/facebook/prophet", "Prophet", "Prakiraan deret waktu dengan musiman & hari libur.",
  "Baseline prakiraan pertumbuhan nasional.", tags=["deret waktu"])

R("dataeng", "https://github.com/pola-rs/polars", "Polars", "DataFrame sangat cepat (Rust).",
  "Memproses jutaan baris transaksi SPKLU di laptop.", tags=["dataframe"], featured=True)
R("dataeng", "https://github.com/duckdb/duckdb", "DuckDB", "Basis data analitik in-process (SQL di atas CSV/Parquet).",
  "Kueri langsung berkas CSV/XLSX besar tanpa server.", tags=["SQL"], featured=True)
R("dataeng", "https://github.com/ray-project/ray", "Ray", "Komputasi terdistribusi Python.",
  "Menjalankan simulasi/skenario secara paralel.", tags=["paralel"])
R("dataeng", "https://github.com/mlflow/mlflow", "MLflow", "Pelacakan eksperimen & registri model.",
  "Reproduksibilitas model di setiap naskah.", tags=["eksperimen"])
R("dataeng", "https://github.com/wandb/wandb", "Weights & Biases", "Pelacakan eksperimen berbasis cloud.",
  "Alternatif MLflow dengan dashboard kolaboratif.", tags=["eksperimen"])

# =============================================================================== RISET
R("litrev", "https://github.com/asreview/asreview", "ASReview", "Penyaringan tinjauan sistematis dengan active learning.",
  "Systematic review keadilan akses charger.", tags=["review"], featured=True)
R("litrev", "https://github.com/kermitt2/grobid", "GROBID", "Ekstraksi metadata & struktur dari PDF ilmiah.",
  "Membangun korpus referensi terstruktur.", tags=["PDF"])
R("litrev", "https://github.com/J535D165/pyalex", "pyalex", "Klien Python OpenAlex.",
  "Pencarian & bibliometrik literatur.", tags=["OpenAlex"], featured=True)
R("litrev", "https://github.com/scholarly-python-package/scholarly", "scholarly", "Akses Google Scholar dari Python.",
  "Pelengkap pyalex untuk sitasi.", tags=["Scholar"])
R("litrev", "https://github.com/jabref/jabref", "JabRef", "Pengelola referensi BibTeX.",
  "Basis referensi untuk naskah LaTeX/Typst.", tags=["referensi"])
R("litrev", "https://github.com/papis/papis", "papis", "Pengelola referensi berbasis command line.",
  "Alternatif ringan JabRef.", tags=["referensi"])
R("litrev", "https://github.com/microsoft/markitdown", "MarkItDown", "Konversi PDF/DOCX/PPTX ke Markdown.",
  "Menyiapkan naskah & referensi untuk LLM.", tags=["konversi"])

R("llm", "https://github.com/ollama/ollama", "Ollama", "Menjalankan LLM lokal.",
  "Analisis ulasan (ABSA) tanpa mengirim data ke luar.", tags=["LLM lokal"], featured=True)
R("llm", "https://github.com/run-llama/llama_index", "LlamaIndex", "Kerangka RAG & agen data.",
  "Tanya-jawab di atas naskah dan data dashboard.", tags=["RAG"], featured=True)
R("llm", "https://github.com/infiniflow/ragflow", "RAGFlow", "Mesin RAG dengan pemahaman dokumen mendalam.",
  "RAG di atas perpustakaan naskah.", tags=["RAG"])
R("llm", "https://github.com/microsoft/graphrag", "GraphRAG", "RAG berbasis knowledge graph.",
  "Menautkan naskah, data, dan repo dalam satu graf.", tags=["RAG", "knowledge graph"])
R("llm", "https://github.com/stanford-oval/storm", "STORM (Stanford)", "Penulisan artikel panjang berbasis riset LLM.",
  "Draf tinjauan pustaka awal.", tags=["deep research"])
R("llm", "https://github.com/assafelovic/gpt-researcher", "GPT Researcher", "Agen riset otonom yang menghasilkan laporan bersumber.",
  "Pemindaian cepat literatur & kebijakan.", tags=["deep research"])
R("llm", "https://github.com/SakanaAI/AI-Scientist", "AI Scientist (Sakana)", "Eksperimen otomatis ujung-ke-ujung oleh LLM.",
  "Inspirasi otomasi siklus eksperimen.", tags=["otomasi"])

R("writing", "https://github.com/jgm/pandoc", "Pandoc", "Konverter dokumen universal.",
  "Markdown naskah → DOCX/PDF untuk jurnal.", tags=["konversi"], featured=True)
R("writing", "https://github.com/typst/typst", "Typst", "Sistem typesetting modern pengganti LaTeX.",
  "Poster dan naskah dengan kompilasi cepat.", tags=["typesetting"], featured=True)
R("writing", "https://github.com/executablebooks/jupyter-book", "Jupyter Book", "Buku/laporan dari notebook.",
  "Disertasi eksekutabel dengan hasil yang bisa direproduksi.", tags=["buku"])
R("writing", "https://github.com/mwouts/jupytext", "Jupytext", "Notebook sebagai skrip teks (versi-kontrol ramah).",
  "Notebook analisis yang bersih di git.", tags=["notebook"])
R("writing", "https://github.com/marimo-team/marimo", "marimo", "Notebook Python reaktif & reproducible.",
  "Analisis interaktif yang bisa dijalankan sebagai aplikasi.", tags=["notebook"])
R("writing", "https://github.com/garrettj403/SciencePlots", "SciencePlots", "Gaya Matplotlib untuk publikasi ilmiah.",
  "Gambar naskah yang konsisten.", tags=["visualisasi"])
R("writing", "https://github.com/mwaskom/seaborn", "seaborn", "Visualisasi statistik.",
  "Grafik distribusi & regresi untuk naskah.", tags=["visualisasi"])
R("writing", "https://github.com/plotly/plotly.py", "Plotly", "Grafik interaktif.",
  "Gambar interaktif untuk dashboard & lampiran.", tags=["visualisasi"])
R("writing", "https://github.com/ManimCommunity/manim", "Manim", "Animasi matematika/penjelasan.",
  "Video penjelasan mekanisme permintaan laten untuk diseminasi.", tags=["animasi"])
R("writing", "https://github.com/streamlit/streamlit", "Streamlit", "Aplikasi data cepat dari Python.",
  "Prototipe alat siting untuk PLN.", tags=["aplikasi"])
R("writing", "https://github.com/gradio-app/gradio", "Gradio", "Antarmuka demo model ML.",
  "Demo model prediksi untuk pemangku kepentingan.", tags=["aplikasi"])

R("belajar", "https://github.com/EbookFoundation/free-programming-books", "Free Programming Books", "Daftar buku pemrograman gratis.", "Dasar pemrograman.", tags=["buku"])
R("belajar", "https://github.com/practical-tutorials/project-based-learning", "Project-Based Learning", "Tutorial berbasis proyek.", "Belajar dengan membangun.", tags=["tutorial"])
R("belajar", "https://github.com/prakhar1989/awesome-courses", "Awesome Courses", "Kursus universitas terbuka.", "Kurikulum CS/statistik.", tags=["kursus"])
R("belajar", "https://github.com/Developer-Y/cs-video-courses", "CS Video Courses", "Kuliah video ilmu komputer.", "Kuliah gratis.", tags=["kursus"])
R("belajar", "https://github.com/mml-book/mml-book.github.io", "Mathematics for Machine Learning", "Buku matematika untuk ML.", "Fondasi aljabar linear, probabilitas, optimasi.", tags=["buku"], featured=True)
R("belajar", "https://github.com/fastai/fastbook", "fastbook (fast.ai)", "Buku deep learning praktis.", "Deep learning terapan.", tags=["buku"])
R("belajar", "https://github.com/karpathy/nn-zero-to-hero", "Neural Networks: Zero to Hero", "Kuliah membangun jaringan saraf dari nol.", "Intuisi backprop & model bahasa.", tags=["kursus"], featured=True)
R("belajar", "https://github.com/rasbt/LLMs-from-scratch", "LLMs from Scratch", "Membangun LLM dari nol (buku + kode).", "Memahami LLM yang dipakai untuk ABSA & RAG.", tags=["buku"])
R("belajar", "https://github.com/lukasmasuch/best-of-ml-python", "Best of ML Python", "Peringkat pustaka ML Python.", "Pintu gali pustaka.", tags=["katalog"])
R("belajar", "https://github.com/eugeneyan/applied-ml", "Applied ML", "Makalah & blog ML terapan di industri.", "Praktik ML di produksi.", tags=["kurasi"])
R("belajar", "https://github.com/jwasham/coding-interview-university", "Coding Interview University", "Kurikulum CS mandiri.", "Struktur data & algoritma.", tags=["kurikulum"])


# --------------------------------------------------------------------------- validasi & tulis
def build():
    cat_ids = {c["id"]: c for c in CATS}
    seen_id, seen_url = {}, {}
    for it in ITEMS:
        assert it["cat"] in cat_ids, "kategori tak dikenal: %s (%s)" % (it["cat"], it["url"])
        subs = cat_ids[it["cat"]].get("subs", [])
        assert not it["sub"] or it["sub"] in subs, "sub tak dikenal: %s (%s)" % (it["sub"], it["url"])
        assert it["id"] not in seen_id, "DOBEL id: %s <-> %s" % (it["url"], seen_id[it["id"]])
        assert it["url"] not in seen_url, "DOBEL url: %s" % it["url"]
        for t in it["themes"]:
            assert t in THEMES, "tema tak dikenal: %s (%s)" % (t, it["url"])
        for t in it["tabs"]:
            assert t in TAB_LABELS, "tab tak dikenal: %s (%s)" % (t, it["url"])
        for l in it["links"]:
            assert l[1] not in seen_url, "DOBEL url di links: %s" % l[1]
            seen_url[l[1]] = it["url"]
        seen_id[it["id"]] = it["url"]
        seen_url[it["url"]] = it["url"]

    by_cat = {}
    by_kind = {}
    for it in ITEMS:
        by_cat[it["cat"]] = by_cat.get(it["cat"], 0) + 1
        by_kind[it["kind"]] = by_kind.get(it["kind"], 0) + 1
    payload = dict(
        meta=dict(generated=datetime.date.today().isoformat(), total=len(ITEMS), by_kind=by_kind,
                  featured=sum(1 for i in ITEMS if i["featured"]), source="resources/catalog.py"),
        groups=GROUPS,
        cats=[dict(c, subs=c.get("subs", []), n=by_cat.get(c["id"], 0)) for c in CATS],
        themes=THEMES, tab_labels=TAB_LABELS, items=ITEMS,
    )
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print("%d entri · %d kategori · %s → %s (%.0f KB)" % (
        len(ITEMS), len(CATS), by_kind, os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024))
    for c in CATS:
        print("  %-10s %3d  %s" % (c["id"], by_cat.get(c["id"], 0), c["label"]))


if __name__ == "__main__":
    build()
