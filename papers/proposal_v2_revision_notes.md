# Catatan revisi proposal konfirmasi — v2 (8 Oktober 2026)

Berkas: `papers/Confirmation_Proposal_Who_Is_Really_Served_v2.docx` (disunting langsung pada XML dokumen asli;
gaya, header/footer, gambar, dan tabel tidak berubah). Sumber masukan: email Dr Alyas Widita, 6 Oktober 2026,
cc Dr Elizabeth Taylor.

## Apa yang diminta supervisor

1. Menjangkarkan riset pada **perbandingan nasional antar-kota/metropolitan**, bukan antar-provinsi, karena koordinat
   eksak seluruh stasiun tersedia.
2. Membongkar lanskap **(in)equality / (in)equity** akses SPKLU antar kota/kawasan metropolitan.
3. Memakai **matriks waktu tempuh** (r5r, `west_java_ttm_car.csv`, folder QH) sebagai fondasi pengukuran.

## Apa yang diubah (arah metode dan jenis output — tanpa angka hasil)

| Bagian | Perubahan |
|---|---|
| Sampul | Baris "Revised draft, 8 October 2026, following supervisor feedback …" |
| Abstract | Kalimat bahwa rasio provinsi menyembunyikan skala kota; paragraf baru: jangkar multi-kota, waktu tempuh r5r dari desa ke stasiun berkoordinat eksak, equality vs equity dibandingkan antar-metropolitan; kontribusi dan kata kunci ditambah |
| 1.2 | Butir "administrative containment" diperluas: stasiun lintas batas provinsi, metropolitan yang melintasi batas (Jabodetabek) |
| 1.5 Scope | Dua skala → tiga skala: nasional (514 kab/kota), **desa dalam 10 kawasan metropolitan** (unit banding utama), Jabar + Jakarta + Banten daratan sebagai area pilot dan uji penggunaan |
| 2.3 | Paragraf baru: R5/r5r sebagai standar matriks waktu tempuh; pemisahan equality (Lorenz/Gini) dan equity (indeks konsentrasi) — bisa *unequal* tanpa *inequitable*, dan bisa berbeda antar kota |
| 2.4 | Klaim kebaruan ditambah: belum ada perbandingan equality/equity akses antar-metropolitan Indonesia berbasis waktu tempuh |
| 2.5 | Celah baru **G5 Scale**; "Four gaps" → "Five gaps" |
| 3.6 | Anak tangga 1: waktu tempuh r5r/R5 dari desa; ambang ≤15 menit (sensitivitas 10 dan 30) — menggantikan ≤10 (7 dan 15) agar konsisten dengan skrip supervisor |
| 4.5 RQ4 | Pertanyaan diperluas: "…and how do the equality and the equity of access differ between Indonesia's metropolitan areas?"; tujuan, metode (Gini/Lorenz, CI, kuintil, Theil dalam/antar kawasan), dan output (*league table* kawasan pada equality dan equity terpisah) |
| 4.6 Tabel sintesis | Baris baru "Do cities differ in equality and equity of access?" |
| 4.7 | Hipotesis **H5**: kota berbeda lebih besar pada equity daripada equality |
| 5.2 Data | Baris jaringan jalan diperbarui (ekstrak Geofabrik per kawasan); baris baru: matriks waktu tempuh r5r (Jabar–Jakarta–Banten *held*), populasi Kontur 2023, batas desa GADM L4 / BPS–HDX 2020 |
| 5.3 | Desa sebagai unit banding antar-metropolitan, dengan alasan (kode resmi, bisa digabung sensus/PODES, cukup kecil di perkotaan) |
| 5.4 | OSRM dari centroid → **r5r/R5 dari titik di dalam poligon desa**, matriks desa-ke-desa, maks 60 menit, stasiun ditugaskan ke desa lewat koordinat; E2SFCA memakai matriks yang sama |
| 5.7 | Paragraf baru: ukuran per kawasan metropolitan (pangsa ≤15/30 menit, Lorenz/Gini, CI terhadap pengeluaran/IPM, kuintil, Theil), dilaporkan sebagai peringkat berpasangan |
| 5.8 | Catchment 7/10/15 → 10/15/30 menit |
| **5.10 (baru)** | *Pilot workflow and the outputs it will produce*: deskripsi pipeline pilot (6.669 desa, 1.556 lokasi stasiun, populasi Kontur), lima jenis output yang akan dihasilkan untuk tiap kawasan, dan dua keputusan praktis (kode BPS 10 digit, *point-in-polygon*). Hasil pilot sengaja **tidak** dimuat; ia hidup di dashboard (tab ⏱️ Akses Waktu Tempuh) |
| 7.1 | Kontribusi empiris baru: perbandingan equality/equity antar-metropolitan |
| 7.2 | Paper B memuat perbandingan antar-metropolitan |
| Referensi | Conway, Byrd & van der Linden (2017); Pereira et al. (2021) r5r; van Wee & Geurs (2011) |

## Yang tidak diubah

Kerangka normatif (sufficientarianism + capability), tangga layanan lima anak tangga, Alkire–Foster, FGT, kurva
spesifikasi, etika, struktur bab. Masukan supervisor memperluas *bagaimana* akses diukur dan *di antara siapa*
dibandingkan; ia tidak mengubah *standar* yang dipakai untuk menilai.

## Hal yang perlu diputuskan bersama supervisor

- Delineasi sepuluh kawasan metropolitan (KSN perkotaan RTRWN) vs definisi lain (BPS *metropolitan statistical area*).
- Variabel peringkat untuk equity di tingkat desa: pengeluaran kab/kota (tersedia), Meta RWI, atau PODES.
- Apakah 15 menit (bukan 10) layak menjadi ambang utama anak tangga 1; skrip supervisor memakai 30 menit untuk peta.
- Satu waktu keberangkatan (Selasa 14.00) vs rata-rata beberapa jam.
