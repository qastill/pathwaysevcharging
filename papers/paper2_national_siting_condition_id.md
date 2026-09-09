# NASKAH 2 — DRAF (VERSI INDONESIA)

**Judul kerja:** *Dari cakupan ke kapabilitas: penempatan berbasis data dan diagnosis utilisasi–ketersediaan pada jaringan pengisian EV nasional yang tumbuh cepat — kajian tingkat transaksi di Indonesia*

**Jurnal sasaran (utama):** *Sustainable Cities and Society* (Elsevier, Q1)
**Alternatif:** *Applied Energy* (Q1) · *eTransportation* (Q1) · *Computers, Environment and Urban Systems* (Q1, bila metode GIS/MCDA yang dijadikan sorotan utama)

> Catatan draf: angka-angka berasal dari dataset proyek (registri Master SPKLU nasional & deret konsumsi bulanan 2024–2026; rincian transaksi Jawa Barat, Maret 2026; rincian transaksi Jakarta Raya + Jawa Barat, 1–8 Juni 2026). Penetapan provinsi untuk titik nasional **diestimasi dari koordinat** — nyatakan ini secara eksplisit. Verifikasi seluruh angka; `[VERIFY]` menandai sitasi yang masih kosong. Versi ini adalah terjemahan Indonesia dari `papers/paper2_national_siting_condition.md`; bila keduanya berbeda, versi Inggris yang mengikat.

---

## Ringkasan eksekutif — abstrak terstruktur (≈250 kata)

**Konteks.** Riset pengisian EV hampir seluruhnya mengukur *cakupan* — berapa banyak charger, dan di mana. Jauh lebih sedikit yang diketahui tentang apakah jaringan nasional yang tumbuh cepat itu *kapabel*: benar-benar tersedia, terutilisasi baik, dan ditempatkan di tempat permintaan berada.

**Tujuan.** Dengan salah satu dataset operasional pengisian EV terbesar yang pernah dilaporkan untuk negara berkembang, kami (i) menggambarkan pertumbuhan eksplosif dan struktur spasial jaringan SPKLU Indonesia, (ii) mendiagnosis **celah ketersediaan** yang jarang dikaji, (iii) mengukur *jenis lokasi mana yang benar-benar menjual energi*, dan (iv) mengusulkan serta memvalidasi kerangka **pemilihan situs dan kelayakan komersial** yang berpijak pada transaksi dan dapat dipindahkan.

**Data & metode.** Kami memadukan registri Master SPKLU nasional (≈3.200 situs; lokasi, kapasitas, operator, status operasional), deret konsumsi bulanan nasional (Jan 2024–Jun 2026), dan rincian tingkat transaksi untuk Jawa Barat (101.020 sesi, Mar 2026) dan Jakarta Raya (56.740 sesi dalam 8 hari, Jun 2026). Metode: analisis pertumbuhan dan konsentrasi; diagnosis status operasional; pengklasifikasi utilisasi menurut jenis tempat ("sektor"); dan model penempatan multi-kriteria (MCDA) weighted overlay yang diperluas dengan catchment, pesaing/kanibalisasi, dan model payback sederhana, divalidasi terhadap utilisasi per jenis tempat yang teramati.

**Hasil.** Energi terjual nasional naik ≈**5×** dalam setahun (≈9,1→48,6 GWh, 2024→2025) dengan laju 2026 mendekati 10 GWh/bulan; permintaan sangat berpusat di Jawa (~67 % situs). Yang menentukan, ~**32 % stasiun melaporkan status operasional "offline"** — celah keandalan yang tak terlihat pada peta cakupan. Utilisasi sangat bergantung jenis tempat: **rest area jalan tol menjual ~3,5× energi per situs dibanding charger di kantor utilitas dan ~13× charger hotel**; permintaan Jakarta yang memuncak siang hari dan didominasi DC menandai ritme penggunaan komersial/armada. Model penempatan kami mereproduksi pola ini dan memeringkat situs kandidat menurut payback.

**Implikasi.** "Lebih banyak charger" adalah tujuan yang keliru; charger yang *kapabel* — tersedia, ber-throughput tinggi, sesuai permintaan — adalah tujuan yang benar. Kami menyediakan perangkat penempatan yang terbuka dan dapat direproduksi untuk jaringan pengisian ekonomi berkembang.

**Kata kunci:** pengisian EV; pemilihan situs; MCDA; utilisasi; ketersediaan/keandalan; smart cities; Indonesia

---

## 1. Pendahuluan
- Jaringan pengisian di ekonomi berkembang tumbuh lebih cepat daripada *dievaluasi*; ukuran cakupan mendominasi, ukuran kapabilitas (ketersediaan, utilisasi, kesesuaian permintaan) terabaikan. `[VERIFY]`
- Tiga titik buta: (a) **ketersediaan/uptime** jarang diukur pada skala jaringan; (b) **utilisasi menurut jenis lokasi** jarang dikuantifikasi dengan data energi nyata; (c) **metode pemilihan situs** jarang *divalidasi* terhadap permintaan teramati.
- **Kontribusi:** (1) diagnosis pertumbuhan + spasial + **ketersediaan** nasional pada data operasional; (2) taksonomi utilisasi menurut jenis tempat (di mana pengisian benar-benar "laku"); (3) kerangka penempatan MCDA + kelayakan komersial yang divalidasi transaksi, dengan catchment & kanibalisasi; (4) implementasi dasbor yang terbuka dan dapat direproduksi.
- **Pertanyaan riset:**
  - **RQ1 (Pertumbuhan & struktur):** Seberapa cepat, dan seberapa terkonsentrasi secara spasial, permintaan jaringan?
  - **RQ2 (Ketersediaan):** Berapa pangsa stasiun yang tidak beroperasi, dan di mana?
  - **RQ3 (Utilisasi menurut tempat):** Jenis lokasi mana yang menghasilkan energi terbanyak per situs, dan mengapa?
  - **RQ4 (Penempatan):** Dapatkah model MCDA + catchment + payback mereproduksi utilisasi teramati dan memeringkat situs baru secara kredibel?

## 2. Kajian terkait
- Pemodelan permintaan & utilisasi pengisian EV. `[VERIFY]`
- **Pemilihan situs** stasiun pengisian (MCDA/AHP/GIS, optimasi). `[VERIFY: tinjauan siting EVCS]`
- Keandalan/uptime pengisian publik (umumnya konteks berpendapatan tinggi). `[VERIFY]`
- Pernyataan celah: gabungkan ketiganya pada dataset nasional, negara berkembang, tingkat transaksi.

## 3. Data & metode
### 3.1 Data
| Sumber | Isi | Cakupan |
|---|---|---|
| Master SPKLU nasional | ~3.200 situs: koordinat, kapasitas, **status**, jumlah charger/konektor, PLN/non-PLN | Indonesia (provinsi **diestimasi dari koordinat**) |
| Deret konsumsi nasional | sesi, kWh, pendapatan bulanan | Jan 2024 – Jun 2026 |
| Transaksi Jawa Barat | 101.020 sesi, 2,26 GWh, AC/DC, durasi | Mar 2026 |
| Transaksi Jakarta Raya | 56.740 sesi, 1,29 GWh, per jam/UP3/kota/daya | 1–8 Jun 2026 |

### 3.2 Metode
- **Pertumbuhan & konsentrasi (RQ1):** deret bulanan; kelipatan tahun-ke-tahun; pangsa pulau/provinsi (catat estimasi provinsi berbasis koordinat + koreksi kotak batas Jakarta).
- **Diagnosis ketersediaan (RQ2):** klasifikasikan status operasional (available / in-use / offline / unavailable / maintenance); petakan dan kuantifikasi pangsa offline per wilayah; bahas kehati-hatian pengukuran (snapshot vs downtime berkelanjutan).
- **Utilisasi menurut tempat (RQ3):** pengklasifikasi kata kunci menempatkan tiap stasiun ke satu sektor tempat (rest area tol, mall, hotel, dealer, kantor PLN, F&B, rumah sakit, publik/transportasi, hunian, dll.); bandingkan **kWh per situs**, sesi/situs, kWh/sesi, daya rerata, dwell; tafsirkan lewat mekanisme waktu tinggal × daya charger × permintaan tawanan. (Jawa Barat punya energi per situs; nasional hanya jumlah situs.)
- **Model penempatan (RQ4):** MCDA weighted overlay ternormalisasi min–maks (permintaan, pertumbuhan, celah pasokan, keadilan) pada tingkat wilayah; skor kandidat tingkat titik dari jarak ke SPKLU terdekat + permintaan tuan rumah; **catchment** (radius/proksi isokron), pemindaian **pesaing/kanibalisasi** (PLN vs swasta), dan skor **kelayakan komersial** + **payback** sederhana yang dijangkarkan pada sesi/unit/bulan teramati. Validasi dengan memeriksa apakah model memeringkat jenis tempat berutilisasi tinggi (tol/dealer) di atas yang rendah (hotel).

## 4. Hasil
- **R1 — Pertumbuhan tongkat hoki (RQ1):** ≈9,1 GWh (2024) → ≈48,6 GWh (2025), ~**5,3×**; laju 2026 ~10 GWh/bulan (lintasan ~120 GWh/tahun); ~2,4 juta pengguna terdaftar. Jawa ≈67 % situs; sektor swasta ≈32 % jaringan. *(Gbr. 1 pertumbuhan; Gbr. 2 pangsa pulau/provinsi.)*
- **R2 — Celah ketersediaan (RQ2):** ~**32 %** stasiun berstatus "offline" (≈1.000 dari ~3.200); available ≈49 %, in-use ≈16 %. Petakan pangsa offline per wilayah. **Sorotan: peta cakupan melebih-lebihkan kapasitas efektif.** *(Gbr. 3 peta kondisi; Tabel 1 status per wilayah.)*
- **R3 — Di mana pengisian laku (RQ3):** peringkat kWh/situs (Jawa Barat, Mar 2026): rest area tol ≈**18.700**, dealer otomotif ≈17.300, mall ≈10.100, …, kantor PLN ≈**5.400**, hotel ≈**1.400**. → tol ≈3,5× kantor utilitas, ≈13× hotel. Mekanisme: permintaan transit tawanan + daya DC tinggi + dwell singkat = perputaran tinggi; situs AC di fasilitas penunjang menganggur. Jakarta Juni: **dominan DC, memuncak siang hari** (ritme armada/ride-hail), permintaan terpusat di Jakarta Selatan/Timur. *(Gbr. 4 peringkat tempat; Gbr. 5 daya-vs-intensitas; Gbr. 6 profil jam Jakarta.)*
- **R4 — Validasi penempatan (RQ4):** model MCDA + catchment + payback memeringkat tempat transit/dealer tertinggi dan situs jenuh/fasilitas penunjang terendah, konsisten dengan utilisasi teramati; contoh peringkat kandidat + rentang payback. *(Gbr. 7 peta kandidat; Tabel 2 kelayakan/payback.)*

## 5. Pembahasan
- Bingkai ulang tujuan kebijakan dari **cakupan → kapabilitas** (tersedia + terutilisasi + sesuai permintaan).
- Ketersediaan sebagai kapasitas termurah: memperbaiki stasiun offline mungkin menambah pengisian efektif lebih banyak daripada membangun baru.
- Penempatan sesuai permintaan: condong ke koridor transit / DC ber-throughput tinggi; perlakukan hotel/kantor sebagai fasilitas penunjang, bukan sumber pendapatan.
- Jaringan listrik sebagai lapisan yang hilang (jarak ke gardu induk/penyulang, kapasitas trafo tersisa) — keunggulan informasi operator; tandai sebagai integrasi mendatang.
- Keterpindahan ke jaringan ekonomi berkembang lain.

## 6. Keterbatasan
- Penetapan provinsi **diestimasi dari koordinat** (centroid terdekat + kotak batas Jakarta) — kuat pada agregat, tidak presisi per situs.
- Transaksi nasional per stasiun tidak tersedia (penghitung status di-reset ke ~0) → kedalaman utilisasi hanya ditampilkan untuk Jawa Barat + Jakarta; konsumsi nasional adalah total negara (tidak terpecah per wilayah).
- "Offline" adalah status snapshot (bisa melebih- atau meremehkan downtime berkelanjutan).
- Pengklasifikasi tempat bersifat heuristik (sebagian kecil salah kelompok); model payback bersifat indikatif, bukan penawaran finansial.

## 7. Kesimpulan
Jaringan yang tumbuh cepat bisa luas tetapi tidak dalam: jejak SPKLU Indonesia mengesankan, tetapi ~sepertiganya offline dan utilisasi sangat bergantung jenis tempat. Strategi penggelaran yang mengutamakan kapabilitas, sesuai permintaan, dan sadar keandalan — yang diwujudkan dalam perangkat penempatan terbuka kami — melayani transisi EV lebih baik daripada cakupan semata.

---

### Rencana gambar/tabel
1. Pertumbuhan bulanan nasional. 2. Pangsa pulau/provinsi. 3. **Peta kondisi nasional** (diwarnai status). 4. kWh/situs menurut tempat. 5. Kuadran daya-vs-intensitas. 6. Ritme per jam Jakarta. 7. Peta penempatan kandidat + payback. T1: status per wilayah. T2: kelayakan/payback kandidat. T3: ringkasan utilisasi per tempat.

### Reproduksibilitas & data
Implementasi dasbor terbuka; skrip agregasi; pernyataan ketersediaan data; metode estimasi provinsi diungkap; izin penggunaan data PLN.

### Pustaka yang disarankan sebagai pembanding (VERIFY sitasi persisnya)
Tinjauan pemilihan situs EVCS (MCDA/AHP/GIS/optimasi); kajian utilisasi & permintaan pengisian; keandalan/uptime pengisian publik; analitik infrastruktur smart city; transisi EV Indonesia/Asia Tenggara.
