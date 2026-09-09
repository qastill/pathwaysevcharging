# Peta Ekuitas SPKLU Indonesia — padanan *EV Equity Roadmap* (UC Berkeley) untuk Indonesia

Tab **🗺️ Peta Ekuitas** (grup *Peta & Jaringan*, `index.html#tab=ekuitas`) dibangun dari folder ini.
Rujukannya adalah [EV Equity Roadmap](https://evmap.climateplans.org/) — peta keputusan CLEE UC Berkeley yang
mewarnai piksel 100 m di California dengan dua lapisan terpisah: **prioritas** (siapa yang paling butuh charger
publik) dan **kelayakan** (di mana jaringan dan lahan sanggup menampungnya). Intisari alat aslinya dan tabel
transfer lapisan → data Indonesia ada di Perpustakaan: `papers/bacaan_evmap_equity_roadmap.md` (id `bacaan-evmap`).

| Berkas | Isi |
|---|---|
| `fetch.py` | **butuh jaringan, sekali**: unduh Kontur Population (H3 res 8) + geoBoundaries ADM1/ADM2 ke `cache/`, padatkan ke `input/` |
| `input/hex_r6.csv` | 47.793 heksagon H3 res 6 (≈36 km²): `h3, pop, kab` — di-commit, supaya `prepare.py` berjalan offline |
| `input/kabupaten.csv` | 515 kabupaten/kota → provinsi (nama BPS) + shapeID geoBoundaries |
| `prepare.py` | indikator per heksagon + agregat kabupaten/provinsi/nasional → `equity.js` (2,6 MB) + `summary.json` |
| `equity.js` | payload `window.EQUITY` — **dimuat malas** saat tab dibuka, tidak disisipkan ke `index.html` |
| `vendor/h3-js.umd.js` | h3-js 4.1.0 (Apache-2.0) untuk menggambar batas heksagon di browser |
| `page.html` · `render.js` | markup tab (`#p-ekuitas`) dan renderer (`window.initEquity`) |
| `inject.py` | penyisip idempoten ke `index.html` (`<!-- EQ:BEGIN/END -->`, `/* EQ:BEGIN/END */`) |

## Urutan jalan

```bash
pip install numpy openpyxl h3 shapely
python3 equitymap/fetch.py      # hanya bila input/ ingin dibangun ulang (unduh ±75 MB)
python3 equitymap/prepare.py    # ±30 detik → equity.js, summary.json
python3 equitymap/inject.py     # pasang/perbarui tab (aman diulang)
```

## Sumber data

| Lapisan | Sumber | Catatan |
|---|---|---|
| Penduduk per heksagon | [Kontur Population — Indonesia](https://data.humdata.org/dataset/kontur-population-indonesia), rilis 2023-11-01, CC BY 4.0 | 874.919 heksagon res 8 → 47.793 heksagon res 6; total 277,5 juta jiwa |
| Batas kabupaten/provinsi | [geoBoundaries](https://www.geoboundaries.org/) gbOpen IDN ADM1/ADM2 (simplified), CC BY 4.0 | 34 provinsi, 515 kabupaten/kota; heksagon pesisir tanpa hit dilekatkan ke kabupaten terdekat (7.017) |
| SPKLU | `SPKLU_Indonesia_Lengkap_2026-06-08.xlsx` (master PLN) | 3.212 situs, 5.009 charger; koordinat semua di dalam kotak Indonesia |
| Jaringan | `data/grid-id/*.js` (RUPTL 2025–2034 + OSM) | 933 gardu induk (138.877 MVA), 4.052 ruas transmisi |
| Sosial-ekonomi | konstanta `POP`/`ECON` provinsi (BPS ~2023, indikatif) — disalin dari tab 🇮🇩 Indonesia | hanya tingkat provinsi |

**Situs operasional** = PLN berstatus `available`/`inuse` (2.059) + seluruh situs mitra non-PLN (1.013). Situs mitra
semuanya berstatus `offline mode` karena tidak terpantau sistem PLN, bukan karena mati — jadi ikut dihitung; sakelar
*PLN saja* di tab membuangnya. PLN `unavailable`/`maintenance` (140) dikecualikan.

## Indikator per heksagon (kolom `r6`)

| Kolom | Isi |
|---|---|
| `pop` | jiwa (Kontur 2023) |
| `d_spklu` · `d_pln` · `d_any` | km garis lurus ke situs operasional terdekat · PLN aktif saja · situs mana pun |
| `n10` · `c10` · `dc10` (+`p` = PLN saja) | situs, charger, dan situs DC ≥50 kW dalam 10 km |
| `pop10` | penduduk dalam dua cincin heksagon (`grid_disk` k=2 ≈ 10–13 km) |
| `d_gi` · `mva25` · `d_tx` | km ke gardu induk terdekat · MVA GI dalam 25 km · km ke ruas transmisi terdekat |

Hanya heksagon ≥100 jiwa yang dikirim ke peta (31.405 heksagon = 99,9 % penduduk); statistik kabupaten/provinsi
memakai semua heksagon.

## Skor & zona (dihitung di browser, rumus sama dengan `prepare.py`)

Skor = rata-rata tertimbang **peringkat persentil** tiap indikator di dalam lingkup yang dipilih (Indonesia atau satu
provinsi), arah dibalik untuk jarak; jarak dipotong 50 km.

| Prioritas keadilan (bobot bawaan) | Kelayakan pasokan (bobot bawaan) |
|---|---|
| jarak ke SPKLU terdekat 30 · jiwa per charger dalam ~10 km 25 · penduduk heksagon 25 · beban sosial-ekonomi provinsi (z kemiskinan − z IPM)/2 20 | jarak ke GI −30 · MVA dalam 25 km 20 · jarak ke transmisi −15 · penduduk ~10 km 20 · charger sudah ada dalam 10 km 15 |

Zona membagi pada skor 50: **1** prioritas & layak (bangun sekarang) · **2** prioritas, jaringan lemah (investasi
jaringan dulu) · **3** layak, prioritas rendah (biarkan pasar) · **4** rendah keduanya. Dua lensa preset — *Keadilan*
dan *Komersial* — meniru tombol yang sama di tab Location Intelligence. Tinjauan nasional menggabungkan heksagon ke
res 5 (rata-rata tertimbang penduduk); memilih provinsi menampilkan res 6.

## Angka bawaan (lingkup nasional, semua operator, bobot bawaan — dari `summary.json`)

| Ukuran | Nilai |
|---|---|
| Penduduk ≤10 km dari SPKLU operasional | **63,7 %** (PLN saja 62,6 %) |
| Penduduk >25 km (gurun pengisian) | **12,0 %** ≈ 33 juta jiwa |
| Jarak rata-rata tertimbang penduduk | 13,7 km |
| Gini charger per kapita antar-kabupaten / antar-provinsi | 0,595 / 0,34 |
| Zona 1 · 2 · 3 · 4 (jiwa) | 53,2 jt · 26,8 jt · 190,6 jt · 6,7 jt |
| Provinsi terlayani terbaik / terburuk (≤10 km) | DKI Jakarta 100 % · Bali 92 % · Banten 85 % / Kepulauan Riau 7 %* · Sulawesi Barat 21 % · Papua 22 % |

\* Kepulauan Riau adalah **gurun palsu**: SPKLU di wilayah PLN Batam tidak ada di master PLN (hanya 4 situs mitra
di Batam). Batas lain yang dicantumkan di tab: sosial-ekonomi tingkat provinsi, jarak garis lurus (bukan waktu
tempuh), kelayakan memakai proksi GI/transmisi (bukan headroom trafo distribusi), populasi Kontur adalah estimasi model.

## Apa yang belum ditiru dari EV Equity Roadmap (langkah berikutnya)

1. Indikator sosial-ekonomi tingkat kabupaten (BPS: kemiskinan, IPM, pengeluaran per kapita) menggantikan provinsi.
2. Lapisan *community resources* dari POI OpenStreetMap (kantor pemda, pasar, terminal, stasiun, puskesmas).
3. Waktu tempuh jalan (OSRM/Valhalla, ada di Repositori Riset) menggantikan garis lurus.
4. Headroom trafo distribusi untuk provinsi selain Jawa Barat (padanan peta hosting-capacity utilitas California).
5. Resolusi 7–8 per kota dari sumber Kontur yang sama (padanan piksel 100 m).
