# 🅿️ Parkir × Charger — padanan ParkServe / park priority areas / ParkScore (Trust for Public Land) untuk SPKLU

Tab **🅿️ Parkir × Charger** (grup *Peta & Jaringan*, `index.html#tab=parkir`) dibangun dari folder ini.
Rujukannya adalah [data ParkServe](https://www.tpl.org/park-data-downloads) milik Trust for Public Land:
% penduduk dalam 10 menit berjalan kaki dari taman, *park priority areas* (blok di luar jangkauan), dan indeks
ParkScore untuk 100 kota. Di sini objeknya bukan taman melainkan **lahan parkir ber-charger** — setiap SPKLU publik
berdiri di sebuah lahan parkir, dan ekonominya ditentukan oleh mengapa mobil diparkir di sana dan berapa lama.
Intisari alat aslinya ada di Perpustakaan: `papers/bacaan_tpl_parkserve.md` (id `bacaan-parkserve`).

| Berkas | Isi |
|---|---|
| `venue.py` | klasifikasi tempat dari nama situs (port `venueOf()` tab Indonesia) + pengelompokan ke 6 kategori lahan parkir + pemetaan tag lokasi resmi PLN |
| `access.py` | **butuh cache Kontur** (`equitymap/cache/`, dari `equitymap/fetch.py`): jarak 874.919 heksagon res 8 ke SPKLU → `input/access.json` (di-commit) |
| `input/access.json` | akses per kabupaten (≤0,8 km, ≤5 km, varian parkir umum & DC), pita jarak nasional, 25 heksagon prioritas per kabupaten (12.670) |
| `prepare.py` | offline: situs + kategori, perilaku parkir dari transaksi, ChargeScore → `parkir.js` (≈1 MB, dimuat malas) + `summary.json` |
| `page.html` · `render.js` | markup tab (`#p-parkir`) dan renderer (`window.initParkir`); heksagon digambar dengan `equitymap/vendor/h3-js.umd.js` |
| `inject.py` | penyisip idempoten ke `index.html` (`<!-- PK:BEGIN/END -->`, `/* PK:BEGIN/END */`) |

## Urutan jalan

```bash
pip install numpy openpyxl h3 scipy
python3 parkir/access.py     # hanya bila input/access.json ingin dibangun ulang (butuh equitymap/fetch.py dulu)
python3 parkir/prepare.py    # ±8 detik → parkir.js, summary.json
python3 parkir/inject.py     # pasang/perbarui tab (aman diulang; jalankan setelah equitymap/inject.py)
```

## Tiga blok

**A. Akses 10 menit (ParkServe → charger).** Jarak garis lurus dari pusat tiap heksagon Kontur res 8 (≈0,74 km²)
ke SPKLU operasional terdekat (PLN *available/inuse* + seluruh mitra non-PLN). Dua ambang: **0,8 km** = 10 menit
jalan kaki (≈0,5 mil, ambang TPL) dan **5 km** = 10 menit berkendara. Varian: hanya charger di lahan parkir umum
(transit · destinasi · kerja) dan hanya situs DC ≥50 kW. *Heksagon prioritas* = 25 heksagon berpenduduk ≥150 jiwa
terpadat per kabupaten di luar 0,8 km (padanan park priority areas).

**B. Perilaku parkir di charger.** 101.020 sesi Jawa Barat (Maret 2026, tag lokasi resmi PLN) dan 56.740 sesi
Jakarta Raya (1–8 Juni 2026, kategori dari nama situs). Per kategori: durasi parkir (median, p25, p75, histogram
6 pita), okupansi bay = jam-bay terisi ÷ (bay × 24 × hari), perputaran = sesi ÷ (bay × hari), kW efektif = kWh ÷
jam-bay, profil jam (tiap sesi disebar ke jam yang dilewatinya). Bay = jumlah charger situs di master PLN.

**C. ChargeScore (ParkScore → charger).** 100 kabupaten/kota terpadat; 8 ukuran dalam 4 kategori — akses (≤0,8 km,
≤5 km), kapasitas (charger/100 rb, kW/100 rb), ketersediaan (% situs PLN aktif, % situs DC), parkir (% charger di
parkir umum, % penduduk ≤0,8 km dari charger di parkir umum). Poin 1–5 per kuintil relatif; skor = poin ÷ 40 × 100.

## Kategori lahan parkir

| Kategori | Tempat (dari nama situs / tag PLN) | Charger operasional |
|---|---|---|
| Parkir transit | rest area tol, terminal/stasiun/bandara, SPBU | 420 |
| Parkir destinasi | mal/retail, hotel, F&B, wisata, rumah sakit | 955 |
| Parkir kerja & publik | perkantoran, kantor pemerintah/kampus, kantor PLN | 1.607 |
| Parkir hunian | perumahan, township, apartemen | 315 |
| Dealer / showroom | dealer otomotif | 404 |
| Lainnya | nama tidak terklasifikasi | 1.094 |

## Angka bawaan (dari `summary.json`)

| Ukuran | Nilai |
|---|---|
| Penduduk ≤0,8 km / ≤5 km dari SPKLU operasional | **8,7 %** / **44,7 %** |
| ≤0,8 km dari charger di parkir umum · ≤5 km dari situs DC | 5,7 % · 23,8 % |
| Kota terbaik ≤0,8 km | Jakarta Pusat 81,7 % · Jakarta Selatan 72,5 % · Jakarta Barat 62,7 % · Bandung 48,5 % |
| Jiwa terbanyak di luar 10 menit jalan kaki | Bogor 6,2 jt · Bekasi 4,3 jt · Tangerang 3,9 jt · Bandung 3,8 jt |
| Durasi parkir median (Jawa Barat) | transit 36,6 · dealer 39,8 · kerja 42,6 · hunian 44,5 · destinasi 45,8 menit |
| Durasi menurut daya charger | ≤7 kW 82 menit · 11–25 kW 78 · 30–60 kW 42 · 100–120 kW 37 · ≥150 kW 36 |
| Okupansi bay (Jawa Barat / Jakarta) | dealer 57 / 75 % · transit 23 / 56 % · hunian 36 / 30 % · kerja 18 / 35 % · destinasi 15 / 31 % |
| ChargeScore tertinggi (82,5) | Kota Jakarta Timur, Kota Bandung, Kota Jakarta Utara, Kota Bekasi, Kota Semarang, Kota Tangerang Selatan |

Temuan utama: durasi parkir di bay charger **tidak mengikuti alasan parkir** (mal ≈ rest area ≈ 40 menit) tetapi
mengikuti **daya charger** — bay charger dipakai seperti pompa bensin, sehingga peluang AC murah berjam-jam di parkir
destinasi/kerja belum terpakai (kW efektif destinasi 18 kW, okupansi 15 %).

## Batas

Garis lurus, bukan jaringan jalan · poligon lahan parkir (dan lahan parkir tanpa charger) belum ada — OSM diblokir
dari lingkungan bangun · master PLN tanpa wilayah PLN Batam · klasifikasi nama heuristik (698 situs "lainnya") ·
Jakarta hanya 8 hari · bay dari master (dealer cenderung terangkat) · tanpa kategori keadilan (data pendapatan hanya
tingkat provinsi).
