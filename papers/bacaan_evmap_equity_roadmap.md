# Intisari bacaan — EV Equity Roadmap (UC Berkeley CLEE): peta prioritas × kelayakan untuk penempatan charger yang adil, dan apa yang bisa dipakai untuk Indonesia

Qashtalani Haramaini · intisari bacaan untuk Bagian 2 (RQ2) dan Bagian 4 (RQ4) · September 2026

> Dokumen ini bukan naskah. Ia merangkum satu alat rujukan — https://evmap.climateplans.org/ — cukup rinci
> untuk dipakai sebagai cetak biru, lalu memetakan lapisan demi lapisan ke data yang ada di repositori ini.
> Hasil penerapannya ada di tab **🗺️ Peta Ekuitas** (grup *Peta & Jaringan*). Butir bertanda `[VERIFY]` diambil
> dari ringkasan pihak ketiga dan ingatan, belum dicek langsung ke halaman aslinya (situs diblokir dari lingkungan bangun).

## Ringkasan eksekutif

EV Equity Roadmap adalah platform peta terbuka dan gratis dari Center for Law, Energy & the Environment (CLEE),
UC Berkeley School of Law, dibangun bersama Energy and Resources Group (ERG) dan Renewable and Appropriate Energy
Laboratory (RAEL) di bawah Prof. Daniel Kammen, dirancang oleh mahasiswa pascasarjana Ari Ball-Burack, Meagan
Leberth, Brad Rhymer, dan Ankita Shanbhag; San Francisco Environment Department menjadi mitra pengguna awal.
Alat ini mewarnai piksel 100 × 100 m di seluruh kota dan county California dengan dua lapisan yang sengaja
dipisahkan: **prioritas** (di mana charger publik paling dibutuhkan menurut kriteria keadilan) dan **kelayakan**
(di mana jaringan listrik, lahan, dan skema pendanaan sanggup menampungnya), ditambah lapisan **sumber daya
komunitas** (perpustakaan, sekolah, stasiun transit, perumahan terjangkau) sebagai kandidat hub. Pengguna
memilih yurisdiksi, menyalakan atau mematikan kriteria, dan mendapat peta zona yang bisa dibawa ke forum warga,
proposal hibah, dan negosiasi dengan pengembang. Tiga hal yang bisa dipakai langsung untuk Indonesia: (1) pemisahan
prioritas dari kelayakan sebagai dua sumbu, bukan satu skor; (2) transparansi kriteria dan bobot sebagai keluaran,
bukan parameter tersembunyi; (3) definisi "akses" sebagai jarak ke charger yang ada, dinormalkan di dalam yurisdiksi.
Yang tidak bisa dipindahkan mentah: CalEnviroScreen (beban polusi per traktus sensus), data hosting-capacity
utilitas, dan kategori "penyewa/hunian multi-keluarga" — ketiganya tidak punya padanan data publik di Indonesia dan
diganti proksi di tab Peta Ekuitas.

## 1. Apa alat ini, siapa yang membuat, untuk siapa

| Hal | Isi |
|---|---|
| Nama | EV Equity Roadmap (sebelumnya disebut *EV Equity Mapping Tool* `[VERIFY]`) |
| Alamat | https://evmap.climateplans.org/ (peta: /map/) |
| Pembuat | CLEE UC Berkeley Law × ERG/RAEL (Prof. Dan Kammen); pengembang Ari Ball-Burack, Meagan Leberth, Brad Rhymer, Ankita Shanbhag |
| Mitra | San Francisco Environment Department (SFE) — pengguna dan penyandang dana awal `[VERIFY]` |
| Cakupan | Seluruh kota dan county California; diniatkan diperluas nasional |
| Rilis | Dapat diakses publik akhir 2024 |
| Lisensi/akses | Gratis, akses terbuka, berbasis browser |
| Pengguna sasaran | Pemerintah daerah, organisasi komunitas, utilitas, pengembang charger, penyusun proposal hibah |

Alat ini lahir dari **EV Equity Initiative** CLEE — program kebijakan yang menerbitkan *Equitable EV Action Plan
Framework* (Desember 2024), laporan *Facilitating Equity-Oriented EV Infrastructure Investments: Strategies for
Project Design* (November 2024), dan policy brief *EV Charging Access for Multifamily Housing Residents* (Agustus
2024). Peta adalah lengan teknis dari kerangka kebijakan itu, bukan produk berdiri sendiri.

## 2. Cara kerjanya — tiga lapisan pada piksel 100 m

### 2.1 Lapisan prioritas (piksel biru)

Menjawab: *siapa yang paling membutuhkan charger publik?* Kriteria yang dipakai (dapat dinyalakan/dimatikan):

- **Beban lingkungan & sosial** — persentil CalEnviroScreen 4.0 (indeks gabungan polusi udara, air, limbah, dan
  kerentanan penduduk per traktus sensus); ini yang membuat alat ini "memperluas CalEnviroScreen".
- **Pendapatan rendah / komunitas rentan** — traktus berpendapatan rendah, kelayakan Justice40 `[VERIFY]`.
- **Penyewa dan hunian multi-keluarga** — rumah tangga yang tidak bisa memasang charger di rumah, sehingga
  bergantung pada charger publik; ini argumen keadilan paling khas dari alat ini.
- **Akses charger yang ada** — jarak ke charger Level 2 / DC fast terdekat; makin jauh, makin prioritas.
- **Adopsi EV & akses transit** — disebut di deskripsi resmi sebagai "existing EV and charging access" dan
  "transportation and employment access" `[VERIFY rincian variabelnya]`.

### 2.2 Lapisan kelayakan (piksel oranye)

Menjawab: *di mana charger bisa benar-benar dibangun sekarang?*

- **Kapasitas jaringan** — data *load/hosting capacity* (Integration Capacity Analysis) yang dipublikasikan
  utilitas: PG&E, SCE, SDG&E, LADWP, SMUD. Lapisan ini hanya ada di wilayah utilitas yang membuka datanya —
  pembatas yang diakui alat ini secara eksplisit.
- **Kelayakan pendanaan federal** — piksel yang memenuhi syarat program NEVI/CFI atau Justice40 `[VERIFY]`.
- **Ruang komersial dan publik** — tata guna lahan/persil yang memungkinkan charger publik (komersial, parkir,
  fasilitas publik) `[VERIFY]`.

### 2.3 Lapisan sumber daya komunitas (kandidat hub)

Titik-titik yang bisa menjadi lokasi hub: perumahan terjangkau/berpendapatan rendah, perpustakaan, sekolah, stasiun
transit, dan fasilitas publik lain. Piksel prioritas-dan-layak yang memuat titik semacam ini adalah "situs kandidat".

### 2.4 Alur pakai

1. Pilih yurisdiksi (kota/county). 2. Nyalakan kriteria prioritas dan kelayakan yang relevan. 3. Baca tumpang
tindih biru × oranye sebagai zona prioritas yang layak. 4. Tambahkan lapisan komunitas untuk menemukan situs.
5. Bawa peta ke forum warga, proposal hibah, atau negosiasi. Tidak ada "skor tunggal" yang memeringkat seluruh
negara bagian — normalisasi terjadi di dalam yurisdiksi, karena keputusan alokasi memang dibuat di sana.

## 3. Mengapa desainnya penting (pembacaan prinsip pertama)

- **Dua sumbu, bukan satu skor.** Menjumlahkan kebutuhan dan kemudahan ke satu angka membuat kebutuhan kalah oleh
  kemudahan (daerah yang mudah selalu menang). Dengan memisahkan keduanya, daerah *prioritas tinggi tetapi tidak
  layak* tetap terlihat — dan itulah daerah yang butuh investasi jaringan lebih dulu, bukan dilupakan.
- **Kriteria sebagai sakelar yang terlihat.** Fungsi tujuan model penempatan adalah keputusan perencanaan; alat ini
  memaksa pengguna memilihnya secara sadar. Ini persis argumen naskah CUPUM Bab 1 (*One model, two cities*) di
  repositori ini.
- **Yurisdiksi sebagai unit normalisasi.** Persentil dihitung di dalam kota/county, sehingga kota kecil tidak
  "tenggelam" oleh Los Angeles. Untuk Indonesia, padanannya adalah provinsi atau kabupaten/kota.
- **Piksel, bukan poligon administratif.** Resolusi 100 m memungkinkan melihat celah di dalam satu kelurahan;
  agregasi ke kabupaten dilakukan belakangan, bukan di awal.

## 4. Apa yang bisa dipakai untuk Indonesia — lapisan demi lapisan

| Lapisan EV Equity Roadmap | Padanan data Indonesia | Ada di repositori? | Diterapkan di tab Peta Ekuitas |
|---|---|---|---|
| CalEnviroScreen (beban polusi + kerentanan per traktus) | Tidak ada padanan resmi. Proksi: kemiskinan, IPM (BPS) per kabupaten; kualitas udara per kota (KLHK/ISPU) | Provinsi: ya (BPS ~2023 indikatif); kabupaten: belum | Beban sosial-ekonomi provinsi = (z kemiskinan − z IPM)/2 |
| Pendapatan rendah / penyewa / hunian multi-keluarga | Rumah tanpa garasi, rumah petak, rusun (Susenas/Sensus — belum publik per grid); proksi: kepadatan penduduk | Kepadatan: ya (Kontur 2023 per heksagon) | Penduduk per heksagon sebagai proksi kepadatan/tanpa-garasi |
| Akses charger yang ada (jarak ke L2/DCFC) | Jarak ke SPKLU operasional; jiwa per charger; situs DC ≥50 kW dalam 10 km | Ya — master SPKLU nasional 3.212 situs | Diterapkan penuh (garis lurus) |
| Hosting/load capacity utilitas (ICA) | PLN tidak menerbitkan; repositori punya pembebanan trafo Jawa Barat (Capacity Maps) dan GI/transmisi nasional | Jawa Barat: trafo; nasional: 933 GI + 4.052 ruas transmisi | Jarak GI, MVA dalam 25 km, jarak transmisi (proksi) |
| Kelayakan pendanaan (NEVI/Justice40) | Lintasan wajib cakupan SPKLU 2025–2030 (Kepmen ESDM 24.K/2025), RUPTL PLN, skema KPBU | Kepmen: dirujuk di naskah DNDP | Belum |
| Ruang komersial & publik; sumber daya komunitas | POI OpenStreetMap: kantor pemda, pasar, terminal, stasiun, puskesmas, kampus, masjid besar | Belum (klasifikasi venue dari nama situs ada di tab Indonesia) | Belum — langkah berikutnya |
| Pilih yurisdiksi, nyalakan kriteria | 34 provinsi, 515 kabupaten/kota (geoBoundaries) | Ya | Ya + bobot geser + ekspor CSV |
| Piksel 100 × 100 m | H3 res 6 (≈36 km²) nasional; Kontur menyediakan res 8 (≈0,7 km²) bila dibutuhkan per kota | Ya | Res 6 nasional, agregat res 5 untuk tinjauan |

**Yang bisa dipakai sekarang (sudah diterapkan):** pemisahan prioritas × kelayakan; normalisasi di dalam yurisdiksi;
akses sebagai jarak ke charger yang ada; bobot yang bisa digeser dan diterbitkan; empat zona keputusan
(bangun sekarang / jaringan dulu / biarkan pasar / tunda).

**Yang bisa dipakai setelah data ditambah:** indikator sosial-ekonomi tingkat kabupaten (BPS: kemiskinan, IPM,
pengeluaran per kapita); POI publik dari OSM sebagai lapisan komunitas; waktu tempuh jalan (OSRM/Valhalla di
Repositori Riset) menggantikan garis lurus; headroom trafo distribusi untuk provinsi selain Jawa Barat.

**Yang tidak sebaiknya ditiru:** definisi keadilan California berpusat pada polusi lokal dan penyewa; di Indonesia
masalah utamanya adalah *ketiadaan* charger di luar Jawa dan konsentrasi pada koridor tol, bukan ketimpangan di
dalam kota yang sudah terlayani. Karena itu bobot bawaan di tab Peta Ekuitas menaruh jarak dan defisit charger
di atas indikator sosial-ekonomi — dan mencatatnya sebagai keputusan, bukan kebenaran.

## 5. Batas dan kritik yang perlu dibawa saat menyitir

- Alat ini **tidak memprediksi permintaan** (kWh); ia memeringkat kebutuhan dan kemudahan. Menggabungkannya dengan
  model permintaan laten (poster BAM 2026, CUPUM Bab 2) adalah kontribusi yang belum dilakukan pembuatnya.
- Kelayakan hanya sebaik data utilitas yang dibuka; di California pun tidak semua utilitas membukanya. Di Indonesia,
  ketiadaan peta hosting-capacity publik adalah pembatas struktural — argumen naskah CIRED 2027 di repositori ini.
- Piksel 100 m memberi kesan presisi; presisinya dibatasi resolusi data masukan (traktus sensus ≈ ribuan jiwa).
- Belum ada evaluasi dampak yang dipublikasikan: apakah kota yang memakainya benar-benar menempatkan charger di
  zona prioritas `[VERIFY — cek publikasi CLEE 2025–2026]`.

## 6. Cara menyitir & tautan

- EV Equity Roadmap — https://evmap.climateplans.org/ (diakses September 2026)
- CLEE, *EV Equity Initiative — Mapping* — https://www.law.berkeley.edu/research/clee/ev-equity/mapping/
- CLEE, *EV Equity Resources* — https://clee.berkeley.edu/initiative/ev-equity-initiative/ev-equity-resources/
- Legal Planet, *Mapping City Priorities for an Equitable EV Infrastructure Rollout* (23 Jun 2023) —
  https://legal-planet.org/2023/06/23/mapping-city-priorities-for-an-equitable-ev-infrastructure-rollout/
- Legal Planet, *A Framework for Equity and Local Leadership in the EV Transition* (12 Des 2024) —
  https://legal-planet.org/2024/12/12/a-framework-for-equity-and-local-leadership-in-the-ev-transition/
- CLEE, *Equitable EV Action Plan Framework* (Des 2024) —
  https://www.law.berkeley.edu/wp-content/uploads/archive/2024/12/Equitable-EV-Action-Plan-Framework_CLEE.pdf
- CLEE, *Facilitating Equity-Oriented EV Infrastructure Investments: Strategies for Project Design* (Nov 2024) —
  https://legal-planet.org/2024/11/07/new-report-equity-oriented-ev-infrastructure-development/
- CLEE, *EV Charging Access for Multifamily Housing Residents* (Agu 2024) —
  https://www.law.berkeley.edu/wp-content/uploads/2024/08/EV-Charging-Access-for-Multifamily-Housing-Residents-CLEE-Report.pdf
- SF Environment, *EV Equity Roadmap* — https://www.sfenvironment.org/ev-equity-roadmap

Format sitasi yang disarankan: Ball-Burack, A., Leberth, M., Rhymer, B., Shanbhag, A., Kammen, D. M., & CLEE
(2024). *EV Equity Roadmap* [peta interaktif]. UC Berkeley Center for Law, Energy & the Environment.
https://evmap.climateplans.org/ `[VERIFY urutan penulis di halaman resmi]`.

## 7. Hubungan dengan naskah di repositori ini

| Naskah | Yang diambil dari EV Equity Roadmap |
|---|---|
| Paper 1 — Spatial equity & perception | Definisi akses sebagai jarak ke charger yang ada; normalisasi di dalam yurisdiksi untuk indeks konsentrasi |
| CUPUM Bab 1 — One model, two cities | Bukti bahwa alat perencanaan publik pun memperlakukan bobot sebagai sakelar yang terlihat |
| CIRED 2027 — Capacity maps as an equity instrument | Preseden bahwa lapisan kelayakan bergantung pada utilitas yang membuka hosting-capacity |
| Paper 2 — Coverage to capability (siting nasional) | Empat zona keputusan sebagai kerangka rekomendasi nasional |
| RQ4 — Inequity & inequality (sintesis) | Pemisahan prioritas (keadilan) dari kelayakan (efisiensi) sebagai dua tuas kebijakan yang berbeda |
