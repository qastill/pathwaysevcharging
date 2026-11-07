# Revisi angka: naskah & slide "Capacity maps as an equity instrument"

Sumber angka: `papers/capacity/capacity.json`. Berkas ini dibangun ulang dari data mentah oleh `papers/capacity/prepare.py`
dan **identik byte per byte** dengan versi yang di-commit, jadi JSON adalah acuan. Naskah lama
(`papers/capacity/CIRED2027_capacity_maps_equity.docx`) dan dua figur lamanya (`fig2_quadrant.png`, `fig3_rules.png`)
tertinggal dari pipeline; berkas lama dibiarkan utuh, versi baru ada di folder ini.

## Angka yang berubah

| Item | Naskah lama | Pipeline (capacity.json) |
|---|---|---|
| Sel grid 0,045° | 1.292 | **1.295** |
| Sel dengan pemilik EV | 235 | **238** |
| Kuadran tinggi-permintaan/tinggi-headroom | 84,9 % pemilik · 79,9 % charger | **84,2 % · 70,3 %** |
| Kuadran tinggi-permintaan/rendah-headroom | 12,8 % pemilik · 7,2 % charger | **11,6 % · 5,6 %** |
| Sel tinggi-permintaan/rendah-headroom tanpa charger | 37 sel · 270 pemilik | **20 sel · 230 pemilik** |
| Kolam sel tak terlayani | 129 sel · 901 pemilik | **132 sel · 908 pemilik** |
| Headroom-only: pemilik / Gini / kabupaten / cakupan | 694 / 0,653 / 16 / 94,4 % | **694 / 0,411 / 18 / 94,2 %** |
| Demand-only: pemilik / taklayak / Gini / kabupaten / cakupan | 807 / 2 / 0,611 / 15 / 97,4 % | **809 / 3 / 0,347 / 18 / 97,3 %** |
| Demand-in-headroom: Gini / kabupaten / cakupan | 0,600 / 17 / 97,0 % | **0,360 / 18 / 96,8 %** |
| Baseline: Gini / cakupan | 0,692 / 75,5 % | **0,493 / 75,4 %** |
| Transformator melewati 80 % (3,0 %/tahun) | 7.088 | **7.090** |
| Koordinat survei vs register > 1 km | 38 % | **43,2 %** |
| Koordinat hilang/tidak VALID | 20 % | **19,8 %** |
| Nama petugas lapangan tercatat (baru) | — | **79,6 %** |
| Selisih relatif dwh vs headroom-only | "+12 %" | **+13,7 %** (694 lebih 12 % rendah dari 789) |
| Sesi Maret 2026 | 101.020 | 101.020 (diverifikasi dari CSV) |
| Pengisian: "636 charger" | 636 | **329 ID situs di log** (331 terdaftar); 636 tidak dapat diverifikasi |

## Perubahan kesimpulan (bukan sekadar angka)

- Naskah lama mengklaim demand-within-headroom menurunkan Gini paling jauh. Pipeline menunjukkan **demand-only**
  Gini-nya lebih rendah (0,347 vs 0,360) dan menjangkau lebih banyak pemilik (809 vs 789). Keunggulan
  demand-within-headroom yang tersisa adalah **kelayakan**: nol situs di bawah 240 kVA, dibanding tiga pada demand-only.
  Naskah dan slide sekarang menyatakannya begitu.
- Semua aturan menjangkau 18 kabupaten, jadi jumlah kabupaten tidak membedakan aturan.
- Nilai "12 % more owners" pada kesimpulan lama dikoreksi menjadi 14 % lebih banyak dibanding headroom-only
  (atau headroom-only 12 % lebih sedikit, seperti di abstrak).

## Belum diverifikasi (ditandai di naskah)

- **51 % sel tidak sepakat** antara tingkat trafo dan GI (§5.4): tidak dihasilkan oleh `prepare.py`. Perlu dihitung ulang.
- Jumlah 2.574 feeder (Tabel 1): tidak dipakai di analisis ini.
- Referensi [2], [3], [7], [14]: judul, tanggal akses, dan keberadaan kutipan perlu dikonfirmasi sebelum kirim.

## Berkas

- `Capacity_Maps_Equity_CIRED2027_v2.docx` (folder `papers/capacity/`): naskah revisi, 8 halaman, empat figur dan dua tabel.
- `slides/Capacity_Maps_Equity_CIRED2027.pptx`: 15 slide, empat bagian.
- `papers/capacity/v2/fig1..4*.png` dan `build_figs.py`: figur dibangun dari `capacity.json`.
