# pathwaysevcharging

## 📱 Ngecas — web app & mobile app

Aplikasi konsumen (cari, pesan, ngecas + sewa charger rumah P2P) yang dibangun dari data repositori ini
ada di [`app/`](app/README.md) — satu basis kode untuk PWA dan Android/iOS (Capacitor).

## 🧭 Dashboard (`index.html`) — navigasi dua tingkat

Tab dashboard dikelompokkan menjadi empat grup (baris atas), tiap grup memuat tab-tabnya (baris bawah).
Tautan langsung ke tab: `index.html#tab=<id>` (mis. `#tab=resources`).

| Grup | Tab |
|---|---|
| 📊 Analisis SPKLU | Overview · Indonesia · Demand & Sales · Growth & Policy · Sector Analysis · Jakarta Raya · Pelanggan EV · Global Benchmark · Socio-Economic · Spatial Equity · Perception |
| 🗺️ Peta & Jaringan | Map · Location Intelligence · GeoSPKLU · EV × Jaringan |
| 📚 Naskah & Perpustakaan | Perpustakaan · ASEAN Paper · Capacity Maps · P2P Charging · Summary — semua naskah/jurnal terdaftar di Perpustakaan ([`papers/`](papers/README.md)) |
| 🌍 Open Source & Data Dunia | World EV Insight · Open Charge Map · EV Models · **Repositori Riset** · **Kombinasi** |

## 🧰 Repositori Riset — database sumber terbuka

Satu database untuk semua repositori GitHub, dataset, portal, dan standar yang dipakai/relevan untuk riset
(174 entri, 15 kategori, satu entri per sumber). Sumber kebenaran: [`resources/catalog.py`](resources/README.md);
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
