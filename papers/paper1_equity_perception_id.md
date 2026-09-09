# NASKAH 1 — DRAF (VERSI INDONESIA)

**Judul kerja:** *Siapa yang tertinggal? Keadilan spasial dan persepsi publik atas infrastruktur pengisian kendaraan listrik umum di sebuah megaregion negara berkembang — bukti dari Jawa Barat, Indonesia*

**Jurnal sasaran (utama):** *Energy Research & Social Science* (Elsevier, Q1)
**Alternatif:** *Energy Policy* (Q1) · *Journal of Transport Geography* (Q1)

> Catatan draf: seluruh angka di bawah diambil dari dataset proyek (Master SPKLU dan rincian transaksi PLN UID Jawa Barat, Maret 2026; korpus ulasan publik ABSA; indikator sosial-ekonomi BPS). Verifikasi setiap angka terhadap tabel sumber sebelum submit. Sitasi bertanda `[VERIFY]` adalah tempat kosong yang harus diisi rujukan nyata. Versi ini adalah terjemahan Indonesia dari `papers/paper1_equity_perception.md`; bila keduanya berbeda, versi Inggris yang mengikat.

---

## Ringkasan eksekutif — abstrak terstruktur (≈250 kata)

**Konteks.** Indonesia sedang memperluas pengisian kendaraan listrik umum (SPKLU) dengan cepat di bawah target mobilitas listrik 2030, tetapi apakah pembangunan itu *adil* — dan apakah pengguna *merasakannya* andal dan mudah diakses — belum pernah diukur pada skala sub-nasional.

**Tujuan.** Kami mengevaluasi keadilan distributif dan persepsi publik atas jaringan SPKLU di Jawa Barat, provinsi berpenduduk terbanyak di Indonesia, dan menguji apakah keadilan dan kualitas layanan yang dirasakan saling terkait.

**Data & metode.** Kami memadukan (i) registri resmi Master SPKLU (636 unit pengisian di 348 situs pada 26 kota/kabupaten), (ii) 101.020 transaksi pengisian nyata (≈2,26 GWh, Maret 2026), (iii) korpus 894 lokasi yang diulas pengguna (584 di antaranya diskor kuantitatif pada Service Quality Index, SQI), dan (iv) indikator populasi, IPM, dan tingkat pendapatan BPS. Kami menghitung koefisien Gini dan kurva Lorenz untuk distribusi unit dan konsumsi, menormalkannya terhadap populasi dan pendapatan, menyusun Equity Priority Index (EPI = kurang terlayani × pendapatan rendah), dan mengontraskan penyediaan perkotaan (kota) dengan perdesaan (kabupaten). Kami lalu memodelkan pendorong kualitas layanan yang dirasakan dari sentimen per aspek ulasan.

**Hasil.** Penyediaan tidak merata pada tingkat sedang hingga tinggi: Gini unit-terhadap-populasi ≈0,19, sedangkan Gini konsumsi-terhadap-populasi mencapai ≈0,45 — permintaan (dan akses efektif) terkonsentrasi jauh lebih tajam daripada perangkat kerasnya sendiri. Kota mendominasi cakupan maupun intensitas; beberapa kabupaten berpendapatan rendah sekaligus kurang terlayani dan berkebutuhan tinggi (EPI tinggi). Persepsi publik terutama digerakkan oleh **keandalan dan ketersediaan**, bukan fasilitas — dan lokasi ber-SQI terendah mengelompok di pinggiran yang sama yang kurang terlayani, yang menunjukkan bahwa keadilan dan kualitas yang dialami saling menguatkan.

**Implikasi.** Roll-out yang mengutamakan cakupan dapat menutupi celah *keandalan* dan *distributif*. Kami menerjemahkan temuan ini menjadi kerangka prioritisasi berbobot keadilan yang dapat dipindahkan untuk penggelaran pengisian EV yang adil di ekonomi berkembang.

**Kata kunci:** pengisian EV; keadilan energi; keadilan spasial; persepsi publik; Gini/Lorenz; Indonesia; transisi yang adil

---

## 1. Pendahuluan
- Transisi EV global dan peran pengisian cepat *publik* di negara-negara dengan akses pengisian pribadi yang rendah (apartemen, hunian kampung) — keadilan pengisian lebih menentukan di tempat home charging langka. `[VERIFY]`
- Celah 1: sebagian besar kajian keadilan pengisian berlatar konteks berpendapatan tinggi (AS/Uni Eropa/Tiongkok); Asia Tenggara dan megaregion negara berkembang kurang dikaji. `[VERIFY]`
- Celah 2: kajian keadilan jarang menghubungkan ukuran *distributif* dengan kualitas layanan yang *dirasakan/dialami* pengguna nyata.
- Latar: Jawa Barat (≈50 juta jiwa, provinsi terbesar di Indonesia), dorongan elektrifikasi PLN dalam RACE for 2030.
- **Kontribusi:** (1) penilaian terpadu pertama atas keadilan distributif + persepsi SPKLU pada skala provinsi dengan data operasional nyata; (2) Equity Priority Index yang menggabungkan kekurangan layanan dan kebutuhan sosial-ekonomi; (3) bukti bahwa celah distributif dan celah pengalaman berhimpit.
- **Pertanyaan riset:**
  - **RQ1 (Keadilan distributif):** Seberapa tidak merata sebaran unit dan konsumsi pengisian di Jawa Barat, dan apakah normalisasi terhadap populasi/pendapatan mengubah gambarannya?
  - **RQ2 (Kota–desa):** Seberapa besar disparitas kota (perkotaan) vs kabupaten (perdesaan) dalam cakupan dan intensitas penggunaan?
  - **RQ3 (Persepsi):** Aspek layanan mana yang paling menentukan kualitas pengisian yang dirasakan (SQI)?
  - **RQ4 (Keterkaitan):** Apakah wilayah yang kurang terlayani dan berpendapatan rendah juga mengalami kualitas yang dirasakan lebih rendah — yakni, apakah ketidakadilan bertumpuk?

## 2. Pustaka & kerangka
- **Triad keadilan energi** (distributif, prosedural, rekognisi) sebagai lensa pengorganisasi. `[VERIFY: Sovacool & Dworkin; Jenkins et al.]`
- Pustaka dan metode keadilan/aksesibilitas pengisian (Gini/Lorenz, 2SFCA, indeks bertipe EPI). `[VERIFY: Hsu & Fingerman; Khan et al.; Carlton & Sultana]`
- Persepsi / kualitas layanan pengisian (keandalan, uptime, ketersediaan). `[VERIFY]`
- Posisi naskah: distributif + pengalaman, negara berkembang, data operasional.

## 3. Wilayah kajian, data & metode
### 3.1 Wilayah kajian
Jawa Barat: 26 kota/kabupaten; inti perkotaan (mis. Bekasi, Bogor, Depok, Bandung) vs kabupaten perdesaan; heterogenitas demografi dan pendapatan (tipologi Klassen 2023).
### 3.2 Data
| Sumber | Isi | Cakupan |
|---|---|---|
| Master SPKLU (PLN) | 636 unit · 348 situs · koordinat · operator (PLN/mitra) | 26 kota/kab |
| Rincian transaksi | 101.020 sesi · 2,26 GWh · kWh, durasi, tarif, AC/DC | Maret 2026 (330 stasiun aktif) |
| Korpus ulasan ABSA | sentimen tingkat aspek; SQI | 894 lokasi (584 diskor) |
| BPS / Klassen | populasi (SP2022), IPM, kemiskinan, tingkat pendapatan | per kota/kab |

### 3.3 Metode
- **Keadilan distributif:** kurva Lorenz & Gini untuk (a) unit vs populasi, (b) konsumsi (kWh) vs populasi; tafsirkan selisih keduanya.
- **Normalisasi:** unit per 100 ribu jiwa, kWh per kapita, EV per 100 ribu jiwa.
- **Equity Priority Index:** EPI = standar(kekurangan layanan) × standar(pendapatan rendah), untuk menandai wilayah berkebutuhan tinggi yang kurang terlayani.
- **Kota–desa:** kontras kota vs kabupaten pada cakupan dan kWh/unit (proksi utilisasi/tekanan).
- **Model persepsi:** variabel terikat = SQI; prediktor = sentimen aspek (keandalan, ketersediaan, fasilitas, lokasi, harga, …); feature importance / regresi pada 584 lokasi terskor.
- **Keterkaitan (RQ4):** korelasi spasial antara EPI / kekurangan layanan dan rerata SQI.
- Ketahanan: sensitivitas Gini terhadap stasiun aktif-vs-semua; catat bahwa Gini adalah *proksi* keadilan sampai kontrol sosio-spasial yang lebih lengkap tersedia.

## 4. Hasil
- **R1 — Distribusi (RQ1):** Gini unit-vs-populasi ≈ **0,19**; Gini konsumsi-vs-populasi ≈ **0,45**. Kurva Lorenz menunjukkan perangkat keras terkonsentrasi sedang, tetapi *penggunaan* jauh lebih terkonsentrasi → celah akses efektif. *(Gbr. 1 Lorenz; Tabel 1 per kota.)*
- **R2 — Kota–desa (RQ2):** kota memegang sebagian besar unit dan kWh/unit yang jauh lebih tinggi; kabupaten menunjukkan cakupan tipis dan, bila ada, tekanan utilisasi tinggi. *(Gbr. 2.)*
- **R3 — Prioritas keadilan (RQ1/RQ2):** identifikasi kabupaten berpendapatan rendah yang kurang terlayani dan ber-EPI tinggi (sebutkan namanya dari tabel EPI). *(Gbr. 3 peta EPI.)*
- **R4 — Pendorong persepsi (RQ3):** **keandalan** dan **ketersediaan** mendominasi SQI; fasilitas/harga sekunder. *(Gbr. 4 tingkat kepentingan pendorong; rerata SQI ≈ [isi mean_jabar].)*
- **R5 — Penumpukan (RQ4):** wilayah kurang terlayani / ber-EPI tinggi juga menunjukkan rerata SQI lebih rendah → kerugian distributif dan kerugian pengalaman berhimpit. *(Gbr. 5 sebaran EPI vs SQI.)*

## 5. Pembahasan
- Ukuran berbasis cakupan menyanjung jaringan; lensa *keandalan-dan-distribusi* memperlihatkan celah yang sebenarnya (kaitkan dengan temuan nasional bahwa ~sepertiga stasiun berstatus "offline" — lihat Naskah 2).
- Pembacaan keadilan energi: kekurangan distributif + celah rekognisi (komunitas pinggiran berpendapatan lebih rendah) + prosedural (logika penggelaran mengunggulkan kota padat permintaan).
- Kebijakan: penempatan berbobot keadilan, mandat uptime/SLA, dukungan tertarget untuk kabupaten ber-EPI tinggi; pembangunan baru dipasangkan dengan jaminan keandalan.
- Keberlakuan umum ke megaregion berkembang lain (akses home charging rendah → keadilan pengisian publik menjadi penentu).

## 6. Keterbatasan
- Jendela transaksi satu bulan; Gini sebagai proksi keadilan; persepsi dari korpus ulasan (seleksi-diri); validitas konstruk SQI; belum ada pemodelan akses tingkat individu (ke depan: aksesibilitas isokron/2SFCA).

## 7. Kesimpulan
Ketidakadilan distributif dan ketidakadilan yang dialami pada jaringan SPKLU Jawa Barat nyata dan saling menguatkan; kerangka penggelaran yang berbobot keadilan dan sadar keandalan diperlukan bagi transisi EV yang *adil* di ekonomi berkembang.

---

### Rencana gambar/tabel
1. Kurva Lorenz (unit & kWh vs populasi) + Gini. 2. Cakupan kota–desa & kWh/unit. 3. Peta choropleth EPI. 4. Tingkat kepentingan pendorong SQI. 5. Sebaran EPI vs SQI. T1: tabel terpadu per kota. T2: ringkasan aspek persepsi.

### Data & etika
Pernyataan ketersediaan data; izin penggunaan data PLN; etika pengumpulan korpus ulasan & kepatuhan ketentuan layanan; de-identifikasi.

### Pustaka yang disarankan sebagai pembanding (VERIFY sitasi persisnya)
Kerangka keadilan energi; aksesibilitas/keadilan pengisian EV (AS/Uni Eropa/Tiongkok); 2SFCA & Gini dalam keadilan infrastruktur; kajian keandalan/uptime pengisian; kajian kebijakan EV Indonesia.
