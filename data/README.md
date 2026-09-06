# Data jaringan kelistrikan — Indonesia & dunia

Lapisan data jaringan yang dibawa dari repositori
[`qastill/electraskillacademy`](https://github.com/qastill/electraskillacademy)
(commit `e807ce5`) ke repositori ini, sebagai bahan pengembangan lanjutan —
antara lain menghubungkan sisi pembangkitan dengan analisis EV × jaringan
distribusi yang sudah ada di tab **⚡ EV × Jaringan**.

## Isi

```
data/
├── grid-id/          jaringan Indonesia, dipecah per sistem/pulau (8 berkas)
├── grid-world/       pembangkit & interkoneksi dunia (2 berkas)
├── inventory.mjs     skrip pembuat ringkasan
└── inventory.json    ringkasan terhitung (jangan disunting manual)
```

Semua berkas `.js` menempelkan satu variabel global saat dimuat di browser
(`<script src="data/grid-id/data_jamali.js">` → `window.JAMALI_DATA`), jadi bisa
dipakai langsung tanpa build step. Perbarui ringkasan dengan `node data/inventory.mjs`.

## `grid-id/` — jaringan Indonesia

| Berkas | Global | Sistem | Gardu Induk | Pembangkit | Ruas transmisi |
|---|---|---|---:|---:|---:|
| `data_jamali.js` | `JAMALI_DATA` | Jamali | 502 | 171 | 2.357 |
| `data_sumatra.js` | `SUMATRA_DATA` | Sumatera | 195 | 116 | 794 |
| `data_sulawesi.js` | `SULAWESI_DATA` | Sulawesi | 94 | 84 | 390 |
| `data_kalimantan.js` | `KALIMANTAN_DATA` | Khatulistiwa | 85 | 68 | 332 |
| `data_ntb.js` | `NTB_DATA` | NTB | 21 | 18 | 31 |
| `data_ntt.js` | `NTT_DATA` | NTT | 16 | 39 | 51 |
| `data_maluku.js` | `MALUKU_DATA` | Maluku | 12 | 12 | 61 |
| `data_papua.js` | `PAPUA_DATA` | Papua | 8 | 20 | 36 |
| **Total** | | | **933** | **528** | **4.052** |

Total kapasitas: **138.877 MVA** gardu induk, **87.361 MW** pembangkit,
**36.669 km** panjang transmisi.

Tiap berkas memuat tiga `FeatureCollection` GeoJSON:

**`substations`** (Point) — `id`, `name`, `voltage` (mis. `"150/20"`),
`trafo_count`, `capacity_mva`, `province`, `system`, `osm_id`, `osm_name`,
`match_score`, `match_source`, `review_flag`, `source_id`, `source_table`.

**`generators`** (Point) — `id`, `name`, `osm_name`, `type` (PLTU/PLTA/PLTS/…),
`capacity_mw`, `capacity_unit`, `province`, `system`, `status`, `operator`,
`method`, `osm_id`, `osm_source`, `review_flag`, `source_id`.

**`transmission`** (LineString) — `id`, `voltage_class`, `voltage_kv_max`,
`voltage_kv_all`, `length_km`, `osm_id`, `osm_voltage`, `source_id`, `color`, `weight`.
Kelas tegangan: 150 kV (3.245 ruas), 70 kV (351), 500 kV (312), 275 kV (144).

### Pembangkit Indonesia per jenis

| Jenis | Unit | Kapasitas |
|---|---:|---:|
| PLTU (batu bara) | 118 | 53.452 MW |
| PLTGU | 23 | 18.205 MW |
| PLTA | 80 | 6.856 MW |
| PLTG | 30 | 3.071 MW |
| PLTP (panas bumi) | 46 | 2.670 MW |
| PLTMG | 24 | 1.182 MW |
| PLTD | 58 | 1.140 MW |
| PLTS (surya) | 124 | 570 MWp |
| PLTB (bayu) | 11 | 153 MW |
| PLTSA / PLTM / PLTMH / PLTBG / biomassa | 14 | 63 MW |

## `grid-world/` — dunia

**`world-plants.js`** → `window.WORLD_PLANTS` — 34.936 pembangkit di 167 negara,
total 5.706.972 MW. Struktur padat:

```js
{
  fuels: ["Hydro","Solar","Gas", ...],      // 15 jenis
  countries: { AFG:"Afghanistan", ... },     // ISO3 → nama
  plants: [ [name, iso3, capacity_mw, lat, lon, fuelIndex], ... ]
}
```

`fuelIndex` adalah indeks ke dalam `fuels`. Lima besar kapasitas dunia: batu bara
1.965.541 MW, gas 1.493.052 MW, hidro 1.053.160 MW, nuklir 407.912 MW, angin
263.052 MW. Subset Indonesia di dataset ini: 178 pembangkit / 48.752 MW.

**`world-grid.js`** → `window.WORLD_GRID` — kerangka interkoneksi antarnegara.

```js
{
  nodes: { "IDN-JW": [lat, lon, "Indonesia"], ... },   // 280 simpul
  edges: [ [fromNode, toNode, capacity_a, capacity_b], ... ]  // 567 ruas
}
```

## Sumber & lisensi

| Lapisan | Sumber | Lisensi |
|---|---|---|
| Gardu induk & pembangkit Indonesia | RUPTL PLN 2025–2034 (nomor tabel ada di properti `source_table`) | dokumen publik PLN |
| Geometri/koordinat Indonesia | OpenStreetMap, dicocokkan lewat `osm_fuzzy` (skor di `match_score`) | ODbL |
| Pembangkit dunia | WRI Global Power Plant Database | CC-BY 4.0 |
| Interkoneksi dunia | kompilasi turunan pada repo sumber | ikut sumbernya |

Sertakan atribusi ini pada tampilan apa pun yang memakai data ini.

## Catatan sebelum dipakai untuk analisis

1. **`capacity_unit` bercampur.** 404 pembangkit memakai `MW`, 124 memakai `MWp`
   — seluruhnya PLTS. MWp adalah puncak DC dan tidak setara MW AC, jadi
   menjumlahkan keduanya begitu saja melebihkan kontribusi surya. Pisahkan, atau
   kalikan MWp dengan faktor konversi yang eksplisit.
2. **Pembangkit captive ikut terhitung.** PLTU Weda Bay (4.000 MW, Maluku Utara)
   adalah pembangkit kawasan industri nikel, bukan pemasok sistem PLN — dan
   sendirian mendominasi angka Maluku. Saring lewat `operator`/`status` bila yang
   dimaksud hanya sistem PLN.
3. **Koordinat hasil pencocokan fuzzy.** `match_score` < 1,0 berarti nama RUPTL
   dicocokkan ke objek OSM secara perkiraan; `review_flag` menandai baris yang
   masih perlu diperiksa. Perlakukan koordinat berskor rendah sebagai indikatif.
4. **Dua dataset Indonesia tidak identik.** `grid-id/` (RUPTL, 528 unit / 87,4 GW)
   dan subset IDN pada `world-plants.js` (178 unit / 48,8 GW) berbeda tahun dan
   cakupan. Pilih salah satu sebagai acuan; jangan digabung tanpa deduplikasi.
5. **Tanpa data pembebanan.** Berkas ini berisi kapasitas dan topologi, bukan
   beban terukur. Kondisi pembebanan aktual untuk Jawa Barat ada di
   `Gardu_Beban_Lokasi_JABAR.xlsx` dan `beban GI.xlsx` di root repositori.

## Kaitan dengan analisis EV yang sudah ada

Tab **⚡ EV × Jaringan** (lihat `analysis/README.md`) berhenti di sisi hilir:
gardu distribusi dan Gardu Induk pemasok di Jawa Barat. Data ini melanjutkan
rantainya ke hulu — transmisi 150/275/500 kV dan pembangkit yang memasok GI
tersebut — sehingga pertanyaan "apakah trafo di depan rumah pelanggan sanggup"
bisa diperluas menjadi "dari pembangkit apa listrik EV itu sebenarnya berasal,
dan seberapa bersih".

Kunci join alaminya adalah field `GARDU_INDUK` pada data gardu distribusi
terhadap `substations[].properties.name` di `grid-id/data_jamali.js` — tetapi
**join ini belum bersih dan perlu dikerjakan**. Pengujian: dari 1.358 nama GI
unik di data gardu distribusi Jawa Barat, hanya **202 yang cocok persis** setelah
normalisasi (huruf besar, buang non-alfanumerik) ke 502 GI Jamali — mencakup
15.962 gardu distribusi atau **37,9%**. Sisanya gagal karena varian penulisan yang
bisa diperbaiki: akhiran nomor trafo (`DAWUAN 1` vs `DAWUAN`), awalan (`GI FAJAR SW`),
dan singkatan lapangan (`SKMDI`, `KSBRU`). Perlu pencocokan fuzzy plus kamus alias
sebelum angka hasil join layak ditampilkan — pendekatan yang sama sudah dipakai
kolom `GI_KODE` di `Gardu_Beban_Lokasi_JABAR.xlsx` dan bisa dijadikan acuan.
