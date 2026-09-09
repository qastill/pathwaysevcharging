# pathwaysevcharging

## 📱 Ngecas — web app & mobile app

Aplikasi konsumen (cari, pesan, ngecas + sewa charger rumah P2P) yang dibangun dari data repositori ini
ada di [`app/`](app/README.md) — satu basis kode untuk PWA dan Android/iOS (Capacitor).

## 🧭 Dashboard (`index.html`) — navigasi dua tingkat

Tab dashboard dikelompokkan menjadi empat grup (baris atas), tiap grup memuat tab-tabnya (baris bawah).
Tautan langsung ke tab: `index.html#tab=<id>` (mis. `#tab=resources`).

| Grup | Tab |
|---|---|
| 📊 Analisis SPKLU | Overview · Indonesia · Demand & Sales · Growth & Policy · Sector Analysis · Jakarta Raya · Pelanggan EV · Global Benchmark · Socio-Economic · Spatial Equity · **Ekuitas vs Kesetaraan** · Perception |
| 🗺️ Peta & Jaringan | Map · Location Intelligence · **Peta Ekuitas** · **Parkir × Charger** · GeoSPKLU · EV × Jaringan |
| 📚 Naskah & Perpustakaan | Perpustakaan · ASEAN Paper · Capacity Maps · P2P Charging · Summary — semua naskah/jurnal terdaftar di Perpustakaan ([`papers/`](papers/README.md)) |
| 🌍 Open Source & Data Dunia | World EV Insight · Open Charge Map · EV Models · **Repositori Riset** · **Kombinasi** |

## 🗺️ Peta Ekuitas — padanan EV Equity Roadmap (UC Berkeley) untuk Indonesia

[EV Equity Roadmap](https://evmap.climateplans.org/) mewarnai piksel 100 m di California dengan dua lapisan
terpisah — **prioritas** (siapa yang paling butuh charger publik) dan **kelayakan** (di mana jaringan sanggup).
Tab **Peta Ekuitas** membangun logika yang sama untuk seluruh Indonesia pada heksagon H3 res 6 (≈36 km²):
populasi Kontur 2023 per heksagon, 3.212 SPKLU master nasional, 933 gardu induk + 4.052 ruas transmisi, dan
indikator BPS provinsi. Skor dihitung di browser dari indikator mentah — bobot bisa digeser, lingkup provinsi/
kabupaten (515) dipilih, hasil diekspor CSV. Rinciannya di [`equitymap/`](equitymap/README.md); intisari alat
aslinya dan tabel transfer lapisan → data Indonesia ada di Perpustakaan (`papers/bacaan_evmap_equity_roadmap.md`).

| Ukuran (nasional, bobot bawaan) | Nilai |
|---|---|
| Penduduk ≤10 km dari SPKLU operasional | **63,7 %** (PLN saja 62,6 %) |
| Penduduk >25 km — gurun pengisian | **12,0 %** ≈ 33 juta jiwa |
| Gini charger per kapita antar-kabupaten | 0,595 |
| Zona *prioritas tinggi & layak* / *prioritas tinggi, jaringan lemah* | 53,2 jt / 26,8 jt jiwa |

```bash
pip install numpy openpyxl h3 shapely
python3 equitymap/prepare.py && python3 equitymap/inject.py    # equitymap/fetch.py hanya bila input ingin dibangun ulang
```

## ⚖️ Ekuitas vs Kesetaraan — mengapa angkanya begitu

Tab **Ekuitas vs Kesetaraan** (grup *Analisis SPKLU*) membongkar dua angka Peta Ekuitas dari prinsip pertama dan
memisahkan *kesetaraan* (porsi charger sebanding penduduk) dari *ekuitas* (porsi mengikuti kebutuhan). Dihitung
`equitymap/keadilan.py`; narasinya di Perpustakaan (`papers/catatan_ekuitas_kesetaraan.md`).

| Temuan | Angka |
|---|---|
| Akses vs kepemilikan | Gini akses ≤10 km **0,274** vs Gini charger/kapita **0,595** — 63,7 % tercakup dan Gini 0,6 bisa hidup bersama |
| Dari mana ketimpangan | **63 %** antar-provinsi (Theil); kota **5,0×** kabupaten per kapita; 100 kabupaten (15,6 jt jiwa) tanpa charger; 20:20 = 33,7× |
| Ekuitas vertikal | CI ~IPM **0,365** (pro-kaya), ~PDRB 0,212, ~kepadatan 0,47; kuintil termiskin 0,83 charger/100 rb, 21 % penduduknya >25 km |
| Defisit kesetaraan | **+2.097 charger (+44 %)** di 402 kabupaten agar semua ≥ rata-rata 1,73/100 rb |
| Uji 300 situs baru | aturan ekuitas mengorbankan 0,09 poin cakupan nasional, menambah **3,8 poin** bagi kuintil termiskin |

## 🅿️ Parkir × Charger — padanan ParkServe/ParkScore (Trust for Public Land) untuk SPKLU

[ParkServe](https://www.tpl.org/park-data-downloads) mengukur % penduduk dalam 10 menit jalan kaki dari taman,
menandai *park priority areas*, dan memeringkat 100 kota dengan ParkScore. Tab **Parkir × Charger** memindahkan
ketiganya ke lahan parkir ber-charger: akses 10 menit ke SPKLU dari 874.919 heksagon Kontur res 8, heksagon
prioritas per kabupaten, ChargeScore 100 kota — ditambah perilaku parkir nyata (durasi, okupansi bay, perputaran,
profil jam) dari 157.760 sesi per kategori lahan parkir. Rinciannya di [`parkir/`](parkir/README.md); intisari
alat aslinya di Perpustakaan (`papers/bacaan_tpl_parkserve.md`).

| Ukuran | Nilai |
|---|---|
| Penduduk ≤0,8 km (10 menit jalan kaki) / ≤5 km (berkendara) dari SPKLU | **8,7 %** / **44,7 %** |
| Durasi parkir median di charger — mal vs rest area | 45,8 vs 36,6 menit (ditentukan daya charger, bukan alasan parkir) |
| Okupansi bay tertinggi / terendah (Jawa Barat) | dealer 57 % / destinasi 15 % |

```bash
pip install numpy openpyxl h3 scipy
python3 parkir/prepare.py && python3 parkir/inject.py    # parkir/access.py hanya bila akses ingin dihitung ulang
```

## 🧰 Repositori Riset — database sumber terbuka

Satu database untuk semua repositori GitHub, dataset, portal, dan standar yang dipakai/relevan untuk riset
(178 entri, 15 kategori, satu entri per sumber). Sumber kebenaran: [`resources/catalog.py`](resources/README.md);
tab *Global EV Data* dan *Open-Source Stack* yang lama dilebur ke sini supaya tidak ada daftar tautan ganda.

```bash
python3 resources/catalog.py && python3 resources/inject.py
```

## 🔗 Kombinasi — hasil menyambungkan data repo ke sumber terbuka

Katalog menjawab *apa yang ada*; tab **Kombinasi** menjawab *apa yang keluar bila disambungkan*.
Enam temuan, seluruh angkanya dihitung ulang dari 99.544 transaksi SPKLU, 3.687 rumah pemilik EV,
dan GeoJSON jaringan Jawa–Bali — memakai pvlib, H3, dan spesifikasi Open EV Data. Rinciannya di
[`resources/combine/`](resources/combine/README.md).

| Kombinasi | Temuan |
|---|---|
| Tangga daya | charger terpasang 124 kW, armada mampu 89 kW, **yang mengalir 35 kW** — daya bukan pengikatnya |
| Kebetulan surya | pengisian memuncak 13.00–16.00, **52%** energi bisa langsung dari PV tanpa baterai |
| Gurun pengisian | gurun terbesar ternyata pin default geocoder; setelah dibersihkan hanya **1,9%** pemilik di luar jangkauan |
| Kunci standar | CCS2 **91,4%** energi; CHAdeMO 791 kWh sebulan di 18 charger |
| Kelekatan jaringan | situs dekat gardu induk menjual **4,6×** lebih banyak energi |
| Sintesis karbon | PV di situs meniadakan **811 tCO₂/bulan**, puluhan kali lebih besar dari menggeser jam |

```bash
pip install pandas numpy pvlib h3
python3 resources/combine/prepare.py && python3 resources/combine/inject.py
```
