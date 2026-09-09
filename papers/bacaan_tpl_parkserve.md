# Intisari bacaan — ParkServe, park priority areas & ParkScore (Trust for Public Land): ukuran akses 10 menit untuk taman, dan cara memindahkannya ke lahan parkir ber-charger

Qashtalani Haramaini · intisari bacaan untuk Bagian 1 (RQ1, penempatan) dan Bagian 2 (RQ2, akses) · September 2026

> Dokumen ini bukan naskah. Ia merangkum satu keluarga produk data — https://www.tpl.org/park-data-downloads — cukup
> rinci untuk dipakai sebagai cetak biru, lalu menjelaskan apa yang dipindahkan ke tab **🅿️ Parkir × Charger** dan
> mengapa. Butir bertanda `[VERIFY]` berasal dari ringkasan pihak ketiga dan ingatan; situs TPL diblokir dari
> lingkungan bangun sehingga belum dicek langsung.

## Ringkasan eksekutif

Trust for Public Land (TPL), organisasi nirlaba konservasi lahan di Amerika Serikat, menerbitkan tiga produk data
yang saling menyambung. **ParkServe®** adalah basis data taman untuk lebih dari 15.000 kota di AS yang menghitung
satu ukuran tajam: *persentase penduduk yang tinggal dalam 10 menit berjalan kaki (≈0,5 mil) dari sebuah taman*,
dihitung lewat jaringan jalan pejalan kaki dengan jalan tol/highway sebagai penghalang. **Park priority areas**
menandai blok sensus yang berada di luar jangkauan itu dan memeringkatnya menurut kebutuhan (kepadatan, pendapatan,
usia, ras/etnis). **ParkScore®** memeringkat 100 kota terbesar dengan lima kategori — akses, luas taman, investasi,
fasilitas, dan keadilan — dengan poin per bracket relatif antar-kota. Seluruh data dapat diunduh (poligon taman,
area layanan 10 menit, area prioritas, jalur, taman bermain, skema data) dalam format shapefile/GeoJSON/CSV.
Tiga hal yang dipindahkan ke charger: (1) ukuran akses satu-angka yang mudah dibaca warga — "berapa persen penduduk
dalam 10 menit dari charger"; (2) area prioritas sebagai *kantong penduduk di luar jangkauan*, bukan sekadar peta
kosong; (3) indeks kota yang relatif dan berkategori, dengan bobot yang terbuka. Yang tidak bisa dipindahkan mentah:
jaringan jalan pejalan kaki (diganti garis lurus), poligon taman (diganti SPKLU sebagai wakil lahan parkir), dan
pilahan demografi (belum ada data tingkat kabupaten).

## 1. Apa produk-produk ini, siapa yang membuat, untuk siapa

| Hal | Isi |
|---|---|
| Penerbit | Trust for Public Land (TPL), San Francisco; unit Planning & GIS (tplgis.org) |
| ParkServe | Basis data taman > 15.000 kota/kota kecil AS; diperbarui berkala; peta interaktif per kota |
| ParkScore | Indeks tahunan 100 kota terbesar AS (sejak 2012 `[VERIFY tahun]`), laporan PDF per kota |
| 10-Minute Walk | Kampanye kebijakan bersama National Recreation and Park Association & Urban Land Institute: setiap warga kota dalam 10 menit jalan kaki dari taman `[VERIFY mitra]` |
| Unduhan | https://www.tpl.org/park-data-downloads — park polygons, 10-minute walk service areas, park priority areas, places & urban areas, trails & playgrounds, skema data |
| Lisensi | Bebas dipakai untuk tujuan nonkomersial dengan atribusi `[VERIFY ketentuan persisnya]` |
| Pengguna | Dinas taman kota, perencana, organisasi warga, peneliti kesehatan masyarakat, wartawan |

## 2. Cara kerjanya

### 2.1 Area layanan 10 menit (ParkServe)

- Titik masuk taman (bukan centroid) menjadi asal; area layanan dibangun di atas jaringan jalan pejalan kaki
  nasional dengan batas 10 menit ≈ 0,5 mil; highway, freeway, dan interstate diperlakukan sebagai penghalang.
- Penduduk dihitung dari blok sensus yang jatuh di dalam area layanan; hasilnya *persentase penduduk dalam
  10 menit* per kota, dipilah menurut ras/etnis, usia, dan pendapatan.
- Keluaran: poligon area layanan per taman (dapat diunduh), angka per kota di peta ParkServe.

### 2.2 Park priority areas

- Blok sensus (block group) yang tidak berada dalam area layanan mana pun.
- Diberi peringkat kebutuhan (sangat tinggi → sedang) memakai kepadatan penduduk, kepadatan anak, pendapatan
  rendah, dan indikator kesehatan/panas `[VERIFY variabel persisnya]`.
- Fungsinya: memberi tahu kota *di mana* taman berikutnya paling banyak menambah penduduk terlayani.

### 2.3 ParkScore

| Kategori | Ukuran (contoh) | Bobot `[VERIFY]` |
|---|---|---|
| Akses | % penduduk dalam 10 menit jalan kaki | ~ seperlima |
| Luas | median ukuran taman; % luas kota yang menjadi taman | ~ seperlima |
| Investasi | belanja per kapita; dana nirlaba/relawan | ~ seperlima |
| Fasilitas | lapangan basket, taman anjing, taman bermain, jalur, toilet, pusat rekreasi per kapita | ~ seperlima |
| Keadilan | selisih akses & luas taman antar-lingkungan menurut ras dan pendapatan | ~ seperlima |

Setiap ukuran diberi poin menurut *bracket* relatif antar 100 kota, dijumlahkan, lalu dinormalkan ke skala 100.
Skor bersifat relatif: peringkat satu berarti *lebih baik dari 99 lainnya*, bukan *cukup baik*.

## 3. Mengapa desainnya penting (pembacaan prinsip pertama)

- **Satu angka yang bisa dipegang warga.** "% penduduk dalam 10 menit" mengalahkan hektare per kapita karena
  ia tentang *orang*, bukan aset — dan bisa dijanjikan wali kota.
- **Ambang waktu, bukan jarak.** 10 menit adalah batas psikologis perjalanan spontan; angka yang sama bisa dipakai
  untuk jalan kaki (0,8 km) atau berkendara (≈5 km) tanpa mengubah kerangkanya.
- **Area prioritas = penduduk, bukan lahan kosong.** Kantong terpadat di luar jangkauan adalah tempat tambahan
  satu fasilitas menambah penduduk terlayani paling banyak — logika *marginal coverage* yang sama dengan
  penempatan charger.
- **Indeks relatif, kategori terbuka.** Kota dapat melihat kategori mana yang menahan skornya; itu yang mengubah
  peringkat menjadi rencana kerja.

## 4. Apa yang dipindahkan ke lahan parkir ber-charger (tab 🅿️ Parkir × Charger)

| Produk TPL | Padanan di tab | Status |
|---|---|---|
| ParkServe: % penduduk dalam 10 menit jalan kaki ke taman | % penduduk ≤0,8 km (jalan kaki) dan ≤5 km (berkendara) dari SPKLU operasional, dihitung dari 874.919 heksagon Kontur res 8; varian "hanya charger di lahan parkir umum" dan "hanya DC" | ada — garis lurus, bukan jaringan jalan |
| Park priority areas | Heksagon di luar 0,8 km, 25 terpadat per kabupaten/kota (508 kabupaten), digambar di peta; jiwa di luar jangkauan per kabupaten | ada |
| ParkScore (100 kota, 5 kategori) | ChargeScore: 100 kabupaten/kota terpadat, 4 kategori (akses, kapasitas, ketersediaan, parkir), 8 ukuran, poin kuintil, skala 100 | ada — tanpa kategori keadilan |
| Poligon taman | Lahan parkir diwakili SPKLU yang berdiri di atasnya, diklasifikasi (transit · destinasi · kerja/publik · hunian · dealer) dari nama situs dan tag lokasi resmi PLN | proksi — poligon parkir OSM belum ada |
| Pilahan demografi | — | belum |
| (tidak ada di TPL) | Perilaku parkir nyata di charger: durasi, okupansi bay, perputaran, profil jam, dari 157.760 sesi | tambahan |

**Mengapa "parkir", bukan "taman".** Setiap SPKLU publik berdiri di sebuah lahan parkir; yang membedakan ekonominya
adalah *mengapa mobil diparkir di sana dan berapa lama*. Rest area menahan mobil 30–40 menit (parkir transit), mal
dan kantor menahan berjam-jam (parkir destinasi/kerja), perumahan semalaman (parkir hunian). Ukuran akses TPL
dipakai untuk menjawab *siapa yang bisa menjangkau charger*, sedangkan data transaksi menjawab *bagaimana charger
itu dipakai sebagai tempat parkir*.

## 5. Temuan awal (angka bawaan tab, September 2026)

| Ukuran | Nilai |
|---|---|
| Penduduk ≤0,8 km dari SPKLU operasional (10 menit jalan kaki) | 8,7 % |
| Penduduk ≤5 km (10 menit berkendara) | 44,7 % |
| Penduduk ≤0,8 km dari charger di lahan parkir umum | 5,7 % |
| Charger operasional di lahan parkir umum (transit · destinasi · kerja) | ≈62 % dari 4.795 |
| Durasi parkir median saat mengisi (Jawa Barat) | 37–46 menit di semua kategori lahan; ditentukan daya charger (≤7 kW: 82 menit; ≥150 kW: 36 menit) |
| Okupansi bay tertinggi / terendah (Jawa Barat) | dealer 57 % · hunian 36 % / destinasi 15 % |
| Kota ChargeScore tertinggi | Kota Jakarta Timur, Kota Bandung, Kota Jakarta Utara, Kota Bekasi, Kota Semarang, Kota Tangerang Selatan (82,5) |
| Kabupaten dengan jiwa terbanyak di luar 10 menit jalan kaki | Bogor 6,2 jt · Bekasi 4,3 jt · Tangerang 3,9 jt · Bandung 3,8 jt |

Pembacaan yang paling bernilai: durasi parkir di bay charger *tidak* mengikuti alasan parkirnya — di mal orang
mengisi 46 menit lalu memindahkan mobil, padahal mereka berbelanja berjam-jam. Bay charger diperlakukan seperti
pompa bensin. Itu berarti peluang AC berdaya rendah dan murah di parkir destinasi/kerja belum terpakai, dan
kebijakan tarif parkir (bukan tarif kWh) adalah tuas yang belum disentuh — sambungan langsung ke naskah P2P
(sewa bay per jam) di repositori ini.

## 6. Batas dan kritik yang perlu dibawa saat menyitir

- Ukuran akses TPL memakai jaringan jalan pejalan kaki; versi di tab memakai garis lurus, sehingga melebih-lebihkan
  akses di daerah bersungai/berjalan tol dan di kepulauan.
- Poligon lahan parkir Indonesia tidak tersedia offline; lahan parkir *tanpa* charger — justru kandidat situs —
  belum terpetakan. Langkah berikutnya: OpenStreetMap `amenity=parking` + kapasitas, dihubungkan ke heksagon
  prioritas.
- "Bay" dihitung dari jumlah charger di master PLN; bila master mencatat lebih sedikit dari fisik (lazim di dealer),
  okupansi dan perputaran terangkat.
- ChargeScore tanpa kategori keadilan karena data pendapatan hanya tingkat provinsi; ini kategori yang justru
  paling khas ParkScore.
- Master SPKLU PLN tidak memuat wilayah PLN Batam; Jakarta hanya 8 hari transaksi.

## 7. Cara menyitir & tautan

- Trust for Public Land. *ParkServe® Data Downloads.* https://www.tpl.org/park-data-downloads (diakses September 2026)
- Trust for Public Land. *The ParkServe® database — About.* https://www.tpl.org/parkserve/about
- Trust for Public Land. *ParkScore® Index 2026.* https://parkserve.tpl.org/ (laporan per kota, PDF)
- Trust for Public Land, Planning & GIS. *10-Minute Walk Tools and Projects Gallery.* https://web.tplgis.org/10minwalk-project-gallery/
- ArcGIS REST metadata *ParkServe® 10-minute walk Service Areas* — https://services9.arcgis.com/FF3qnCUixr5w9JQi/arcgis/rest/services/ServiceAreas_Clip/FeatureServer/0

Format sitasi yang disarankan: Trust for Public Land (2026). *ParkServe® database and ParkScore® Index* [dataset
and index]. https://www.tpl.org/parkserve `[VERIFY versi/tanggal rilis]`.

## 8. Hubungan dengan naskah di repositori ini

| Naskah | Yang diambil dari TPL |
|---|---|
| Paper 2 — Coverage to capability | Ukuran akses satu-angka per kota dan area prioritas sebagai kerangka "cakupan" yang jujur |
| Paper 3 — P2P charging tanpa menjual kWh | Bukti durasi parkir vs daya: bay charger dipakai seperti pompa bensin → ruang bagi tarif sewa bay per jam |
| CUPUM Bab 1 — One model, two cities | Indeks relatif berkategori dengan bobot terbuka sebagai contoh fungsi tujuan yang terlihat |
| RQ4 — Inequity & inequality | Kategori keadilan ParkScore sebagai templat yang belum bisa diisi (data pendapatan tingkat kabupaten) |
