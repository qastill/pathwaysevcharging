# Catatan analisis — Ekuitas vs kesetaraan jaringan SPKLU Indonesia: mengapa Gini 0,595 dan cakupan 63,7 % bisa keluar bersamaan, dan apa kesimpulannya

Qashtalani Haramaini · catatan analisis untuk Bagian 2 (RQ2) dan Bagian 4 (RQ4) · September 2026

> Catatan ini menjelaskan angka-angka di tab **⚖️ Ekuitas vs Kesetaraan** dan **🗺️ Peta Ekuitas** dari prinsip
> pertama. Semua angka dihitung ulang oleh `equitymap/keadilan.py` dari payload Peta Ekuitas; tidak ada yang diketik
> tangan. Definisi: *kesetaraan* (equality, horizontal) = porsi charger sebanding penduduk; *ekuitas* (equity,
> vertikal) = porsi mengikuti kebutuhan.

## Ringkasan eksekutif

Jaringan SPKLU Indonesia (4.795 charger operasional di 3.072 situs, Juni 2026) mencakup 63,7 % penduduk dalam
radius 10 km, tetapi Gini charger per kapita antar-kabupaten mencapai 0,595 — dua angka yang tampak bertentangan
dan sebenarnya mengukur dua hal berbeda: *ada atau tidak* (akses, Gini 0,274) versus *berapa banyak*
(kepemilikan, Gini 0,595). Ketidaksetaraan itu terstruktur, bukan menyebar: 63 % berasal dari perbedaan
antar-provinsi (dekomposisi Theil), kota memegang 57 % charger untuk 21 % penduduk (5,0× per kapita kabupaten),
100 kabupaten berpenduduk 15,6 juta jiwa tidak punya satu charger pun, dan 20 % penduduk yang paling terlayani
memegang 63 % charger sementara 20 % terbawah 1,9 % (rasio 20:20 = 33,7). Secara vertikal jaringan pro-kaya
(indeks konsentrasi terhadap IPM 0,365) tetapi gradiennya adalah pembangunan manusia dan kepadatan, bukan PDRB
(CI 0,212): provinsi kaya sumber daya yang jarang penduduk sama kurang terlayaninya dengan provinsi miskin.
Kuintil provinsi termiskin (25 juta jiwa) mendapat 0,83 charger per 100 ribu jiwa, 2,8× lebih sedikit dari kuintil
terkaya, dan 21 % penduduknya lebih dari 25 km dari charger. Kesetaraan per kapita menuntut +2.097 charger (+44 %)
di 402 kabupaten. Uji penempatan 300 situs baru menunjukkan ekuitas nyaris gratis dalam rezim cakupan: memberi
bobot 2× pada provinsi termiskin mengorbankan 0,09 poin cakupan nasional dan menambah 3,8 poin cakupan bagi
kuintil termiskin. Kesimpulan untuk RQ4: ukuran keadilan harus bertingkat (provinsi → kota/kabupaten → heksagon)
dan dua-dimensi (akses dan kepemilikan); rekomendasi kebijakan yang dapat dipertahankan adalah aturan penempatan
berbobot ekuitas dengan keberhasilan diukur pada cakupan kuintil termiskin.

## 1. Dua angka, dua pertanyaan

| Angka | Mengukur | Cara hitung |
|---|---|---|
| 63,7 % penduduk ≤10 km | **Akses** — ada charger yang bisa dijangkau | jarak garis lurus pusat heksagon Kontur res 6 (31.405 heksagon ≥100 jiwa) ke situs operasional terdekat |
| Gini 0,595 | **Kepemilikan** — porsi charger relatif penduduk | kurva Lorenz 508 kabupaten/kota diurut charger/kapita; Gini = 1 − 2 × luas |

Keduanya bisa tinggi bersamaan karena satu situs melayani banyak orang sekaligus (cakupan jenuh cepat di daerah
padat), sedangkan jumlah charger tidak. Gini akses (penduduk tercakup per kapita) hanya 0,274 — jaringan sudah
cukup *ada* di mana-mana yang padat, tetapi *berapa banyak* sangat tidak merata.

## 2. Mengapa Gini-nya 0,595 — anatomi kurva Lorenz

1. **Ekor kiri menempel di lantai.** 100 kabupaten (15,6 juta jiwa, 5,6 %) tanpa charger; 402 dari 508 kabupaten di
   bawah rata-rata nasional 1,73 charger/100 ribu; median kabupaten hanya 0,62. Dua puluh persen penduduk yang
   paling sedikit terlayani memegang 1,9 % charger.
2. **Ekor kanan melonjak.** 10 kabupaten/kota teratas memegang 41,1 % charger untuk 10,4 % penduduk; DKI Jakarta
   27,7 % charger untuk 4,1 % penduduk; Jakarta Selatan 21,4 charger/100 ribu = 12× rata-rata nasional. Dua puluh
   persen penduduk teratas memegang 63,1 % (rasio 20:20 = 33,7; Palma 6,1).
3. **Bertingkat: situs → unit → kW.** Gini situs 0,555 < Gini charger 0,595 < Gini kW 0,712. Daerah yang sudah
   punya situs mendapat lebih banyak unit per situs dan daya lebih besar (DC). Ukuran "jumlah situs" meremehkan
   ketimpangan.
4. **Lebih timpang di dalam kabupaten.** Gini per heksagon (charger dalam 10 km terhadap penduduk) 0,72: di dalam
   satu kabupaten pun charger mengelompok di pusat kota dan koridor tol.
5. **Lapisan mana yang menyumbang.** Tanpa DKI Gini turun ke 0,512; kota saja 0,456; kabupaten saja 0,467; Jawa saja
   0,582; luar Jawa 0,550 — ketimpangan tetap tinggi di semua irisan. Theil T = 0,700 dengan **63,2 % antar-provinsi**
   dan 36,8 % dalam-provinsi; dikelompokkan kota vs kabupaten, 44,8 % adalah celah kota–kabupaten.

## 3. Dua garis patahan: kota vs kabupaten, Jawa vs luar Jawa

| Kelompok | Kab/kota | Penduduk | Charger | /100 rb | ≤10 km | >25 km | Jarak rata² | Tanpa charger |
|---|---|---|---|---|---|---|---|---|
| Kota | 93 | 57,8 jt | 2.739 | 4,74 | 96,8 % | 0,8 % | 2,6 km | 0 |
| Kabupaten | 415 | 219,8 jt | 2.056 | 0,94 | 54,9 % | 14,9 % | 16,1 km | 100 |
| Jawa | 116 | 153,9 jt | 3.528 | 2,29 | 75,8 % | 2,2 % | 6,9 km | 2 |
| Luar Jawa | 392 | 123,7 jt | 1.267 | 1,02 | 48,5 % | 24,2 % | 21,1 km | 98 |

Angka nasional 63,7 % adalah rata-rata dua dunia yang tidak dialami siapa pun: Jawa 75,8 % dan luar Jawa 48,5 %.
Masalah luar Jawa adalah *ketiadaan* (24 % penduduk, ≈30 juta jiwa, >25 km); masalah Jawa adalah *ketebalan*
(kota padat dengan sedikit charger per orang). Kepadatan Jawa membuat tiap situs mencakup lebih banyak orang;
per-kapita yang sama di luar Jawa tidak akan menghasilkan cakupan yang sama — argumen mengapa target nasional harus
dinyatakan per wilayah.

## 4. Ekuitas vertikal: apakah charger mengikuti kebutuhan?

| Ukuran | Nilai | Bacaan |
|---|---|---|
| CI charger ~ PDRB/kapita provinsi | 0,212 | pro-kaya lemah |
| CI charger ~ IPM | 0,365 | pro-kaya jelas |
| CI charger ~ kemiskinan (miskin → kaya) | 0,366 | pro-kaya jelas |
| CI akses ≤10 km ~ PDRB | −0,027 | netral |
| CI charger ~ kepadatan kabupaten | 0,470 | sangat pro-padat |

Gradien ketidakadilan bukan uang melainkan pembangunan manusia dan kepadatan: provinsi ber-PDRB tinggi karena
sumber daya alam (Riau, Kalimantan Timur/Utara, Papua Barat) jarang penduduk dan minim charger. Kuintil provinsi
menurut PDRB (tertimbang penduduk):

| Kuintil | Provinsi | Penduduk | PDRB/kap | Kemiskinan | Charger/100 rb | ≤10 km | >25 km |
|---|---|---|---|---|---|---|---|
| Q1 | Aceh, Bengkulu, DIY, NTB, NTT, Gorontalo, Sulbar, Maluku | 25,5 jt | 36 jt | 15,0 % | 0,83 | 47,5 % | 21,2 % |
| Q2 | Jawa Barat, Jawa Tengah | 85,0 jt | 49 jt | 8,8 % | 1,43 | 78,4 % | 1,7 % |
| Q3 | Sumbar, Lampung, Banten, Bali, Kalbar, Sulut, Malut, Papua | 46,9 jt | 56 jt | 9,8 % | 2,08 | 60,5 % | 19,8 % |
| Q4 | Sumut, Sumsel, Babel, Kalsel, Sultra | 31,6 jt | 66 jt | 8,5 % | 0,97 | 52,7 % | 20,1 % |
| Q5 | Riau, Kepri, Jambi, DKI, Jatim, Kalteng, Kaltim, Kaltara, Sulteng, Sulsel, Papua Barat | 88,6 jt | 126 jt | 8,6 % | 2,35 | 59,7 % | 12,3 % |

Q2 (Jawa Barat & Jawa Tengah) miskin menurut PDRB tetapi paling tercakup — kepadatan membeli cakupan, bukan
pendapatan. Ketidakadilan vertikal Indonesia hari ini adalah ketidakadilan **kedalaman** (berapa banyak) yang
berubah menjadi **ketiadaan** di Q1. Catatan: CI ini antar-provinsi (34 unit); ketidakadilan dalam-provinsi menurut
pendapatan (kota kaya vs kabupaten miskin) belum terukur nasional — itulah yang ditangkap Spatial Equity Jawa Barat
(EPI, CI per kabupaten IPM) dan membutuhkan data BPS tingkat kabupaten.

## 5. Defisit menuju kesetaraan

Membawa setiap kabupaten ke rata-rata nasional 1,73 charger/100 ribu tanpa mengambil dari yang sudah punya
memerlukan **+2.097 charger (+44 % jaringan)** di 402 kabupaten. Defisit terbesar bukan di Papua melainkan di
kabupaten padat Jawa (Malang +32, Jember +31, Sukabumi +31, Tasikmalaya +30) karena ukuran per kapita memihak
jumlah orang; Kota Batam (+27) adalah artefak master PLN yang tidak memuat wilayah PLN Batam. Surplus terbesar di
Jakarta dan Tangerang bukan mubazir (utilisasinya tinggi) melainkan tanda ukuran per kapita tidak menangkap
permintaan armada dan komuter. Defisit adalah ukuran kesetaraan, bukan target pembangunan.

## 6. Uji aturan penempatan: kesetaraan vs ekuitas pada 300 situs

Greedy maximum coverage, radius dua cincin heksagon res 6 (≈10–13 km), kandidat = pusat heksagon berpenduduk.

| Situs baru | Aturan kesetaraan (maks. penduduk baru) | Aturan ekuitas (bobot beban provinsi ≤2×) |
|---|---|---|
| 0 | 63,9 % | 63,9 % |
| +100 | 75,5 % | 75,5 % |
| +300 | 84,3 % | 84,2 % |
| Cakupan kuintil termiskin setelah +300 | 67,8 % | 71,6 % |

Seratus situs pertama sama pada kedua aturan (Kediri, Jember, Sampang, Purbalingga, Indramayu — kabupaten padat
Jawa yang belum tercakup). Bobot ekuitas menggeser urutan sejak situs ke-4 (Paniai, Lombok Timur) tetapi hanya
mengorbankan 0,09 poin cakupan nasional sambil menambah 3,8 poin bagi 25 juta penduduk termiskin. Kurva melandai
setelah ±150 situs karena sisa penduduk tak tercakup tersebar tipis. **Dalam rezim cakupan 10 km, kesetaraan dan
ekuitas tidak bertentangan sampai ±300 situs**; konfliknya baru muncul pada ukuran per kapita (§5) dan pada
situs-situs ekor (Papua pegunungan) yang mahal secara jaringan — wilayah "prioritas tinggi, jaringan lemah" di
Peta Ekuitas.

## 7. Kesimpulan untuk riset

1. Jaringan tidak setara dan ketidaksetaraannya terstruktur tiga tingkat: antar-provinsi (63 %), kota vs kabupaten
   (5,0× per kapita), pusat vs pinggiran di dalam kabupaten (Gini heksagon 0,72). Ukuran keadilan untuk RQ4 harus
   bertingkat, bukan satu Gini nasional.
2. Akses dan kepemilikan berbeda dan keduanya harus dilaporkan; kebijakan yang mengejar cakupan akan "selesai" jauh
   sebelum kesetaraan tercapai.
3. Ketidakadilan vertikal adalah ketidakadilan kedalaman yang menjadi ketiadaan di kuintil termiskin; gradiennya IPM
   dan kepadatan, bukan PDRB — sehingga instrumen kebijakan yang tepat adalah target per wilayah, bukan subsidi
   menurut pendapatan daerah.
4. Kesetaraan per kapita menuntut +2.097 charger di 402 kabupaten dan menaruh Jawa di depan Papua — ukuran keadilan
   horizontal, bukan rencana pembangunan.
5. Ekuitas nyaris gratis di rezim cakupan: gunakan aturan berbobot ekuitas untuk 300 situs berikutnya dan ukur
   keberhasilan dengan cakupan kuintil termiskin.
6. Belum terjawab: ketidakadilan dalam-provinsi menurut pendapatan (BPS kabupaten), waktu tempuh jalan, dan siapa
   yang bisa mengisi di rumah (garasi) — agenda RQ4 berikutnya.

## 8. Batas

Jarak garis lurus; charger = unit di situs operasional (PLN *available/inuse* + mitra non-PLN berstatus *offline
mode* karena tidak terpantau PLN); master PLN tanpa wilayah PLN Batam; populasi Kontur 2023 (estimasi model);
indikator sosial-ekonomi BPS ~2023 indikatif tingkat provinsi; kurva cakupan memakai radius heksagon (≈10–13 km),
bukan tepat 10 km, dan tidak memperhitungkan biaya jaringan tiap situs.
