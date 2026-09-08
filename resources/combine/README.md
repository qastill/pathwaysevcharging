# Kombinasi — data repositori × sumber terbuka terkatalog

Tab **🔗 Kombinasi** (grup *Open Source & Data Dunia*) dibangun dari folder ini.

Katalog [`resources/`](../README.md) menjawab *apa yang ada*. Folder ini menjawab pertanyaan
berikutnya: **mana dari 174 sumber itu yang benar-benar bisa disambungkan ke data mentah
repositori ini, dan apa yang keluar bila disambungkan.** Seluruh angka pada tab dihitung ulang
dari berkas mentah — tidak ada yang diketik tangan.

| Berkas | Isi |
|---|---|
| `prepare.py` | pipeline enam kombinasi → `combine.json` |
| `combine.json` | payload terhitung (jangan disunting manual) → `D.kb` di `index.html` |
| `page.html` | markup tab (`#p-combine`) |
| `render.js` | renderer (`window.initCombine`) — kartu temuan, 8 grafik Chart.js, chip sumber |
| `inject.py` | penyisip idempoten ke `index.html` |

## Urutan jalan

```bash
pip install pandas numpy pvlib h3
python3 resources/combine/prepare.py   # hitung ulang -> combine.json
python3 resources/combine/inject.py    # pasang tab (aman diulang)
```

Tidak butuh jaringan: pvlib menghitung posisi matahari dan iradiasi langit-cerah secara
deterministik, H3 murni geometri, dan semua data lain ada di repositori.

## Enam kombinasi

| # | Kombinasi | Data repo | Sumber terkatalog | Temuan utama |
|---|---|---|---|---|
| K1 | Tangga daya | 99.544 sesi, 3.694 KBLBB | Open EV Data | terpasang 124 kW → armada 89 kW → **terkirim 35 kW** |
| K2 | Kebetulan surya | profil jam 2,26 GWh | pvlib, evcc | **52%** energi bisa langsung dari PV, tanpa baterai |
| K3 | Gurun pengisian | SPKLU + rumah pemilik EV | uber/h3, ChargeGap | hanya **1,4%** pemilik di luar jangkauan 5,6 km |
| K4 | Kunci standar | konektor pada transaksi | Open EV Data | CCS2 **91,4%**; CHAdeMO 791 kWh sebulan di 18 charger |
| K5 | Kelekatan jaringan | 328 situs SPKLU | `data/grid-id`, OSRM (lanjutan) | situs terdekat gardu induk menjual **4,6×** lebih banyak |
| K6 | Sintesis karbon | K2 + energi + `analysis/carbon.json` | Electricity Maps, pvlib | PV **811 tCO₂/bulan** vs geser jam 8–29 tCO₂ |

### Mengapa keenamnya, bukan yang lain

Jaringan keluar diblokir di lingkungan bangun ini, sehingga sumber yang **butuh unduhan atau
kunci API** (Open Charge Map, ST-EVCDP, UrbanEV, ACN-Data, Open-Meteo) tidak bisa dihitung ulang
secara reproduktif dan sengaja **tidak** dimasukkan. Yang tersisa adalah dua golongan yang jujur
bisa dijalankan siapa pun:

1. **Pustaka metode dari PyPI** yang deterministik — pvlib, H3, pandas/numpy.
2. **Data yang sudah ada di repositori** — transaksi, KBLBB, `data/grid-id`, `analysis/carbon.json`,
   dan spesifikasi kendaraan di `app/src/vehicles.ts` (skema Open EV Data).

## Aturan penulisan tiap kombinasi

Setiap entri di `combos` wajib membawa enam bidang, dan renderer menampilkan semuanya:

| Bidang | Isi |
|---|---|
| `question` | pertanyaan yang dijawab, satu kalimat |
| `sources` | `t="repo"` (data repositori) atau `t="cat"` (entri katalog; `id` = `owner/repo` atau URL) |
| `method` | cara hitungnya, cukup untuk direproduksi |
| `kpi` | empat angka; yang pertama disorot emas |
| `insight` | temuan, boleh memakai `**tebal**` |
| `action` | konsekuensi praktisnya untuk perencanaan SPKLU |
| `caveat` | batas keberlakuan — **wajib**, termasuk anggapan dan artefak data |

Aturan yang dipegang: **tidak ada angka tanpa metode, dan tidak ada temuan tanpa batas
keberlakuan.** Contohnya K3 melaporkan dua angka (3,3% mentah dan 1,4% setelah artefak batas
DKI dikoreksi), dan K6 menguji asumsinya pada rentang 8–30 persen supaya kesimpulannya tidak
bergantung pada satu tebakan.

## Yang perlu diketahui saat membaca angkanya

* **Daya rata-rata sesi** memakai durasi terhubung, termasuk waktu diam setelah pengisian
  selesai. Karena itu ia lebih rendah dari daya puncak; p95 dipakai sebagai batas bawah
  kemampuan nyata.
* **Langit-langit armada** memetakan merek pemohon KBLBB ke median daya DC modelnya, karena
  tipe per pemohon tidak tercatat. Dua belas merek ekor panjang memakai nilai anggapan dan
  ditandai `anggapan` di tabel armada.
* **Iradiasi langit-cerah** adalah batas atas; awan Maret memangkas tingkatnya, tetapi
  bentuk profil harian — yang menentukan pangsa kebetulan — jauh lebih stabil.
* **Faktor emisi** adalah rata-rata subsistem Jawa Barat (0,6969 kg/kWh), bukan marjinal.

## Tautan silang

Chip **katalog** pada tiap kartu memanggil `window.rsFind(q)` di
[`resources/render.js`](../render.js), yang melompat ke tab Repositori Riset dan menyaring
langsung ke entri sumbernya. Menambah kombinasi baru cukup menambah satu entri di `combos`
pada `prepare.py`, lalu menambahkan grafiknya di `chartFor()` (markup) dan `chartsAfter()`
(pembuatan Chart.js — **harus** di sana, karena kanvas belum ada di DOM saat `chartFor` jalan).
