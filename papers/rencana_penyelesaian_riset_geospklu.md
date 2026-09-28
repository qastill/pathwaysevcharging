# Rencana penyelesaian riset: dari GeoSPKLU ke bukti pemerataan akses

Tanggal penyusunan: 28 September 2026. Status: rencana kerja dan audit awal; bukan hasil analisis baru atau persetujuan pembimbing.

**Tujuan:** menggunakan GeoSPKLU untuk menjawab siapa yang memperoleh akses SPKLU, siapa yang tertinggal, dan apakah perluasan serta kualitas layanan memperbaiki distribusi tersebut.

Dashboard yang dirujuk: [GeoSPKLU](https://jabar-ev.vercel.app/). Repo: [qastill/pathwaysevcharging](https://github.com/qastill/pathwaysevcharging). Audit dokumen/kode mengacu pada commit [e2f9ff0](https://github.com/qastill/pathwaysevcharging/tree/e2f9ff08f6cbf1f95e533e6a0280521242665bcb); kesamaan commit produksi dengan repo belum diverifikasi.

## 1. Mulai di sini

Tiga keluaran pertama:

- [ ] Satu register data yang menjelaskan lokasi, charger, port, transaksi, cakupan wilayah, periode, dan aturan penyaringan.
- [ ] Satu protokol RQ1: populasi sasaran, unit spasial, ukuran akses, bobot, peringkat sosial ekonomi, dan standar keadilan.
- [ ] Satu tabel percobaan wilayah kecil yang menghubungkan penduduk, kesejahteraan, urban–rural, dan akses; kemudian perluas ke nasional.

Jalur utama penyelesaian adalah RQ1 distribusi nasional, RQ2 pengalaman pengguna, dan RQ3 integrasi. RQ4 kebutuhan dan skenario menjadi pengembangan bertahap. Penomoran ini mengikuti percakapan penyusunan rencana; cocokkan dengan penomoran manuskrip sebelum pengajuan. Analisis kausal atau permintaan laten tidak otomatis menjadi syarat penyelesaian; sepakati ruang lingkupnya dengan pembimbing.

## 2. Apa yang sudah ada dan apa yang harus diperbaiki

Temuan di bawah berasal dari pembacaan dashboard, dokumentasi, dan kode. Pipeline belum dijalankan ulang dalam audit ini.

| Bagian | Bukti dalam repo/dashboard | Tindakan untuk riset |
|---|---|---|
| Distribusi nasional | [Peta Ekuitas](../equitymap/README.md), [prepare.py](../equitymap/prepare.py), [summary.json](../equitymap/summary.json) | Gunakan sebagai baseline; dokumentasikan status operasi dan kelengkapan operator |
| Gini dan concentration index | [keadilan.py](../equitymap/keadilan.py), [keadilan.json](../equitymap/keadilan.json), [catatan ekuitas](catatan_ekuitas_kesetaraan.md) | Tetapkan outcome setiap indeks, bobot penduduk, dan arti variabel pengurutan |
| Jangkauan nasional | Jarak garis lurus 10 km di modul equitymap | Jangan menuliskan hasil ini sebagai waktu berkendara 10 menit; routing jalan merupakan tahap lanjutan |
| Sosial ekonomi | Indikator provinsi; [sosek.py](../equitymap/sosek.py) mendukung tabel kabupaten opsional | Verifikasi tahun/sumber dan cakupan tabel; jangan menganggap data kabupaten lengkap hanya karena pembacanya tersedia |
| Urban–rural | keadilan.py memisahkan nama wilayah berawalan “Kota” dari “Kabupaten” | Sebut sebagai kategori administratif; gunakan klasifikasi desa urban–rural untuk klaim urban–rural |
| Riwayat jaringan | [dinamika.py](../equitymap/dinamika.py) memakai tanggal unit Jabar dan proksi tahun dari ID untuk nasional | Audit tanggal Jabar; pisahkan seri tanggal observasi dan seri rekonstruksi nasional |
| Persepsi | Dashboard menampilkan 584 lokasi terskor ABSA; [naskah equity–perception](paper1_equity_perception_id.md) | Audit label, pemetaan lokasi, cakupan ulasan, dan evaluasi model sebelum klaim terawasi |
| Penempatan dan kapasitas | [dokumentasi capacity](README.md#paperscapacity--cired-2027), [prepare.py](capacity/prepare.py) | Rekonsiliasi angka manuskrip dengan hitung ulang, lalu bandingkan skenario dengan anggaran setara |

### Koreksi terhadap asumsi awal

1. **10 km berbeda dari 10 menit.** Baseline nasional yang diperiksa memakai jarak garis lurus. Label harus mengikuti metode yang benar-benar dijalankan.
2. **Riwayat Jabar bukan seluruhnya belum tersedia.** Repo sudah memakai tanggal operasi dari master Jabar. Periksa apakah tanggal itu tanggal unit atau lokasi, kelengkapan, dan perubahan kapasitas. Riwayat nasional berbasis ID tetap merupakan estimasi.
3. **IPM bukan pendapatan rumah tangga.** CI berperingkat IPM berarti konsentrasi menurut IPM. PDRB per kapita menunjukkan ekonomi wilayah, bukan pendapatan setiap penduduk.
4. **Kota/kabupaten bukan klasifikasi urban–rural.** Kabupaten dapat berisi desa perkotaan.
5. **Angka Gini capacity belum tuntas direproduksi.** papers/README.md mencatat manuskrip 0,692 → 0,600 versus hitung ulang 0,493 → 0,360. Jangan memilih angka yang lebih mendukung argumen; kunci populasi, grid, bobot, dan rumus lalu jelaskan selisih.
6. **Jumlah unit observasi belum seragam.** Halaman overview yang diperiksa menampilkan 348 sites, serta keterangan wilayah yang berbeda antara kartu dan narasi. Rekonsiliasi jumlah lokasi, unit, kota/kabupaten, periode, dan filter sebelum angka dipakai di naskah.

Angka 0,595 untuk Gini charger/kapita dan 0,274 untuk Gini akses di payload saat audit adalah dua outcome berbeda. Nilainya tidak dapat dipertukarkan atau ditafsirkan sebagai perbaikan sebelum–sesudah.

## 3. Fungsi indeks dalam setiap pertanyaan penelitian

| Pertanyaan | Outcome utama | Kegunaan indeks | Batas kesimpulan |
|---|---|---|---|
| RQ1: apakah akses timpang? | Akses penduduk ke layanan charging | Gini: besar ketimpangan; CI: konsentrasi menurut kesejahteraan | Ketimpangan terukur belum otomatis ketidakadilan |
| RQ1: apakah jaringan berkembang lebih merata? | Outcome identik pada dua tanggal | Perubahan Gini/CI, rata-rata akses, dan coverage | Sebelum–sesudah deskriptif bukan efek kausal kebijakan |
| RQ2: bagaimana pengalaman pengguna? | Label aksesibilitas dan keandalan dari ulasan | Fokus pada distribusi aspek dan pengalaman; Gini/CI bukan ukuran wajib | Pengulas bukan sampel acak seluruh masyarakat |
| RQ3: apakah jangkauan sesuai layanan yang dapat digunakan? | Akses spasial versus akses yang disesuaikan operasi | Hitung ulang indeks dengan outcome yang sebanding | Tidak ada transaksi tidak membuktikan stasiun rusak |
| RQ4: bagaimana kebutuhan dan pilihan lokasi mengubah hasil? | Akses setelah skenario penempatan | Bandingkan Gini/CI dan manfaat kelompok kurang terlayani | Skenario adalah hasil model, bukan dampak yang sudah terjadi |

Standar keadilan yang diusulkan: akses minimum bagi seluruh populasi, serta perhatian pada kelompok berakses rendah dan kurang sejahtera. Pemilik EV sekarang, penduduk umum, dan rumah tangga tanpa home charging adalah populasi sasaran berbeda; laporkan sebagai analisis terpisah.

## 4. Protokol pengukuran

### Unit dan outcome

Pertahankan semua unit berpenduduk, termasuk yang aksesnya nol. Pilih grid/desa sesuai resolusi sumber; laporkan agregat kabupaten dan keterbatasan variasi di dalam wilayah. Rata-rata wilayah tidak menggambarkan kondisi setiap rumah tangga.

Gunakan dua jalur yang diberi nama jelas:

- **Baseline yang tersedia:** charger per kapita dan jangkauan garis lurus 10 km.
- **Analisis akses lanjutan:** port publik yang dapat dijangkau melalui jalan dalam 10 menit, dengan sensitivitas 15/20 menit; kemudian kapasitas dan kompetisi pengguna melalui 2SFCA/E2SFCA bila data mendukung.

Dalam ukuran akses sederhana, a_i = jumlah port yang dapat dijangkau dari wilayah i. Port yang sama boleh masuk jangkauan beberapa wilayah; jumlah seluruh a_i bukan jumlah port fisik nasional. Untuk kompetisi, gunakan permintaan pada catchment stasiun, bukan sekadar membagi akses dengan penduduk grid asal.

### Rumus dan kontrak input

Untuk bobot w_i = P_i / sum(P_i), rata-rata mu = sum(w_i a_i):

- Gini = sum_i sum_j [w_i w_j |a_i-a_j|] / (2 mu).
- CI = 2 sum_i [w_i a_i R_i] / mu - 1.
- R_i adalah peringkat tengah kumulatif penduduk setelah unit diurutkan menurut kesejahteraan rendah → tinggi. Nilai pengurutan yang sama memakai peringkat tengah kelompok yang sama.

Fungsi lorenz(pop, val) dan concentration(pop, val, rank_key) dalam keadilan.py menerima **jumlah outcome**, bukan langsung nilai akses per orang. Bila a_i adalah akses penduduk pada unit i, gunakan val_i = P_i × a_i. Bila outcome adalah charger per kapita, val_i memang jumlah charger wilayah. Audit panggilan lorenz(pop_h, c10_h): ia mengukur distribusi c10_h/pop_h, berbeda dari distribusi pengalaman akses c10_h berbobot penduduk.

Aturan pelaporan:

- CI positif berarti akses lebih besar pada peringkat tinggi; beri nama peringkatnya (pengeluaran, IPM, PDRB, atau kepadatan).
- CI nol tidak memastikan pemerataan; lihat kurva dan kelompok.
- Semua akses nol membuat Gini/CI tidak terdefinisi; tampilkan NA dengan alasan, bukan nilai pemerataan.
- Gini untuk indikator individual biner terlayani/tidak sama dengan proporsi tidak terlayani. Gini antarwilayah atas proporsi coverage adalah ukuran agregat berbeda.
- Untuk outcome terbatas/biner, jelaskan ketergantungan batas CI pada rata-rata sebelum membandingkan waktu atau kelompok; pilih koreksi berdasarkan estimand, bukan otomatis.
- Laporkan rata-rata akses dan coverage agar pemerataan pada tingkat layanan rendah tidak disalahartikan sebagai keberhasilan.
- Gunakan Theil untuk dekomposisi antar/dalam kelompok yang aditif; jangan menganggap Gini dapat dipecah sederhana dengan cara yang sama.
- Pisahkan ketidakpastian sampling, estimasi populasi, kelengkapan master, dan asumsi routing. Jika memakai bootstrap, tentukan desain yang sesuai ketergantungan spasial.

### Contoh hipotetis untuk evaluasi penempatan

Empat wilayah berpenduduk sama diurutkan dari pendapatan rendah ke tinggi. Untuk ilustrasi ini, setiap tambahan port hanya melayani wilayah sasaran.

| Skenario | Akses A/B/C/D | Rata-rata | Gini | CI |
|---|---|---:|---:|---:|
| Awal | 1 / 3 / 5 / 7 | 4 | 0,3125 | +0,3125 |
| Tambah 4 port di A | 5 / 3 / 5 / 7 | 5 | 0,1500 | +0,1000 |
| Tambah 4 port di D | 1 / 3 / 5 / 11 | 5 | 0,4000 | +0,4000 |

Jumlah tambahan sama, konsekuensi distribusi berbeda. Dalam jaringan sebenarnya, hitung ulang seluruh catchment dan kompetisi; contoh ini bukan hasil GeoSPKLU.

## 5. Data yang diperlukan

| Dataset | Kolom minimum | Untuk apa | Tindakan |
|---|---|---|---|
| Master lokasi | station_id, koordinat, operator, akses publik, status, snapshot_date | Jaringan saat ini | Deduplikasi dan dokumentasikan status tidak terpantau |
| Charger/port | charger_id, station_id, connector, simultaneous_ports, rated_kw | Kapasitas layanan | Bedakan konektor, unit, dan port simultan |
| Penduduk | area_id, population, tahun, geometri, sumber | Bobot dan populasi sasaran | Audit Kontur serta pengaitan batas wilayah |
| Kesejahteraan | area_id, pengeluaran/pendapatan/IPM, tahun, definisi | Peringkat CI | Catat missing, resolusi, dan proxy; gunakan bobot peringkat yang konsisten |
| Urban–rural | kode desa, klasifikasi, tahun | Strata proposal | Jangan mengganti dengan kota/kabupaten tanpa label proxy |
| Routing | titik asal, station_id, travel_minutes, mode, versi jaringan | Akses jalan | Validasi rute pulau, penyeberangan, tol, dan pintu masuk |
| Riwayat | ID, open_date, close_date, perubahan kapasitas, sumber tanggal | Perubahan jaringan | Pisahkan tanggal observasi dari imputasi ID |
| Operasi | ID port, waktu observasi, uptime/downtime, missingness | Akses usable | Validasi dengan log operasi; transaksi hanya bukti pendukung |
| Ulasan | ID anonim, station_id, tanggal, teks, label, split | RQ2/RQ3 | Audit cakupan, anotasi, dan kebocoran data latih/uji |
| Kebutuhan alternatif | EV terdaftar, akses home charging, perjalanan | Sensitivitas/skenario | Bedakan pemilik EV umum dari pelanggan home charging |

Tabel analisis akhir yang diusulkan:

area_id | period | population | population_source | welfare_value | welfare_type | welfare_year | urban_rural | access_value | access_unit | coverage_share | operator_scope | missing_reason

Missing bukan nol. Setiap hasil menyimpan versi data, periode, filter operator, ukuran supply, outcome, bobot, ranking, threshold, dan commit skrip. Jangan memasukkan identitas pelanggan, lokasi rumah individual, atau ulasan yang dapat mengidentifikasi seseorang ke keluaran publik; gunakan agregat yang sesuai.

## 6. Paket kerja dan kriteria selesai

Jadwal berikut adalah urutan relatif untuk draf analisis utama, bukan janji seluruh disertasi selesai dalam delapan minggu. Waktu akuisisi data dan revisi pembimbing dapat mengubah durasi.

| Paket | Waktu indikatif | Kegiatan | Kriteria selesai |
|---|---|---|---|
| W1 Audit data | Minggu 1 | Register, deduplikasi, periode, jumlah unit, operator | Satu versi data acuan dan tabel selisih dengan dashboard/naskah |
| W2 Kunci metode | Minggu 2 | Outcome, bobot, ranking, standar keadilan, unit, sensitivitas | Protokol dua halaman; keputusan yang membutuhkan pembimbing ditandai |
| W3 Baseline RQ1 | Minggu 3–4 | Reproduksi baseline dan keluaran kelompok | Peta, Lorenz, CI curve, tabel urban–rural yang valid, draf metode/hasil |
| W4 Akses jalan | Setelah input routing siap | Pilot lalu perluasan; bandingkan garis lurus dan routing | Selisih coverage/peringkat terjelaskan; label waktu hanya untuk hasil routing |
| W5 Persepsi | Mulai anotasi sejak minggu 2; analisis minggu 4–6 | Panduan label, pemeriksaan antarpenilai, model, evaluasi | Data uji terpisah, metrik per kelas, analisis kesalahan, cakupan ulasan |
| W6 Integrasi | Minggu 6–8, setelah W3/W5 | Samakan periode dan unit, bandingkan akses dan pengalaman | Hasil sesuai/tidak sesuai dilaporkan tanpa menetapkan arah sebelumnya |
| W7 Pengembangan | Sesudah hasil utama | Riwayat terverifikasi, kebutuhan alternatif, skenario | Asumsi dan batas bukti jelas; analisis kausal hanya jika desain memadai |

Pekerjaan pertama pada modul indeks:

- [ ] Audit makna val dan pop pada semua pemanggilan Gini/CI.
- [ ] Tangani total supply nol dan peringkat yang sama.
- [ ] Periksa konstruksi kuintil: pemilihan seluruh provinsi melalui batas kumulatif tidak menjamin tiap kelompok berisi tepat 20% penduduk. Nyatakan kelompok aproksimasi atau gunakan alokasi fraksional yang terdokumentasi.
- [ ] Rekonsiliasi Gini capacity dan himpunan titik/grid.
- [ ] Pisahkan label IPM/PDRB/pengeluaran dan kota/kabupaten versus urban–rural.
- [ ] Bandingkan semua operator versus PLN; status mitra tidak terpantau diperlakukan sebagai asumsi yang diuji.
- [ ] Uji sensitivitas kekosongan data regional yang sudah disebut dalam equitymap/README.md, termasuk Batam.

Kriteria uji untuk implementasi berikutnya: akses seragam memberi Gini/CI nol; permutasi baris tidak mengubah hasil; ties peringkat tidak tergantung urutan baris; seluruh akses nol memberi NA; contoh numerik di atas terproduksi; perubahan satuan tidak mengubah indeks; supply fisik tidak terhitung ganda saat agregasi.

## 7. Menyatukan hasil menjadi naskah

Paket minimum pembahasan:

1. Siapa yang memiliki akses rendah, menurut wilayah dan kelompok.
2. Apakah ketimpangan mengikuti gradien kesejahteraan, dengan ukuran yang disebut secara tepat.
3. Apakah kesimpulan berubah ketika ukuran supply, akses, atau kebutuhan diganti.
4. Apakah persepsi dan keandalan mendukung atau berbeda dari pola akses spasial.
5. Intervensi yang sesuai: penambahan jangkauan, perbaikan operasi, atau keduanya.

Jangan menjadikan kWh terjual sebagai ukuran akses, transaksi sepi sebagai bukti downtime, korelasi sebagai kausalitas, atau estimasi tahun dari ID sebagai tanggal pembukaan teramati. Hasil Jabar mendukung pengujian mekanisme dan batas interpretasi, tetapi tidak otomatis membuktikan pola nasional.

## 8. Keputusan untuk pertemuan pembimbing berikutnya

- Apakah RQ1 nasional + RQ2 persepsi + RQ3 integrasi cukup menjadi jalur utama penyelesaian?
- Outcome primer: reachable ports, akses yang memperhitungkan kompetisi, atau baseline supply/kapita sambil routing disiapkan?
- Standar minimum akses dan prioritas kelompok mana yang dipakai?
- Resolusi sosial ekonomi dan urban–rural apa yang dapat dipertanggungjawabkan?
- Bagian longitudinal/kausal mana yang diteruskan jika data nasional tidak tersedia?
- Angka naskah mana yang ditahan sampai selisih reproduksi diselesaikan?

## 9. Rujukan metode dan sumber audit

- [World Bank — Concentration Index](https://www.worldbank.org/content/dam/Worldbank/document/HDN/Health/HealthEquityCh8.pdf): ranking, interpretasi, dan sifat indeks.
- [World Bank — Concentration Curves](https://www.worldbank.org/content/dam/Worldbank/document/HDN/Health/HealthEquityCh7.pdf): konstruksi kurva.
- [Income and racial disparity in household publicly available EV infrastructure accessibility](https://www.nature.com/articles/s41467-024-49481-w): konteks pengukuran akses EV charging.
- [README proyek](../README.md), [equitymap](../equitymap/README.md), [naskah dan reproduksi capacity](README.md), serta skrip/payload yang ditautkan pada bagian 2.

Dokumen ini menambahkan rencana dan kontrak analisis. Perhitungan produksi, payload, dan tampilan dashboard perlu diperbarui melalui pekerjaan implementasi terpisah setelah keputusan metode dikunci.
