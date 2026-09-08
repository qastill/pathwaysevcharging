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
| 🌍 Open Source & Data Dunia | World EV Insight · Open Charge Map · EV Models · **Repositori Riset** |

## 🧰 Repositori Riset — database sumber terbuka

Satu database untuk semua repositori GitHub, dataset, portal, dan standar yang dipakai/relevan untuk riset
(174 entri, 15 kategori, satu entri per sumber). Sumber kebenaran: [`resources/catalog.py`](resources/README.md);
tab *Global EV Data* dan *Open-Source Stack* yang lama dilebur ke sini supaya tidak ada daftar tautan ganda.

```bash
python3 resources/catalog.py && python3 resources/inject.py
```
