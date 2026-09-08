# Repositori Riset — database sumber terbuka

Tab **🧰 Repositori Riset** (grup *Open Source & Data Dunia*) dibangun dari folder ini.
Isinya: setiap repositori GitHub, dataset, portal, dan standar yang dipakai atau relevan
untuk riset SPKLU — **satu entri per sumber, tidak ada dobel** — diklasifikasikan dan
diberi tema riset yang sama dengan Perpustakaan.

| Berkas | Isi |
|---|---|
| `catalog.py` | **sumber kebenaran**: taksonomi (`GROUPS`, `CATS`, `THEMES`) + semua entri (`R(...)`) + validasi |
| `resources.json` | payload terhitung (jangan disunting manual) → `D.res` di `index.html` |
| `page.html` | markup tab (`#p-resources`) |
| `render.js` | renderer (`window.initResources`): filter grup → kategori → sub, pencarian, tema, jenis, urut, statistik GitHub, ekspor Markdown |
| `inject.py` | penyisip idempoten ke `index.html` (tab, hook, markup, payload, skrip) |

## Urutan jalan

```bash
python3 resources/catalog.py   # validasi + tulis resources.json
python3 resources/inject.py    # sisipkan/perbarui tab di index.html (aman diulang)
```

`inject.py` mencopot blok lama lebih dulu (`<!-- RES:BEGIN/END -->`, `/* RES:BEGIN/END */`,
`Object.assign(D,{res:...})`) sehingga aman dijalankan berkali-kali. Pola dan penanda blok
sama dengan `papers/inject_papers.py`.

## Taksonomi

Tiga grup, lima belas kategori. Empat kategori pertama mempertahankan pengelompokan
awal **Lapisan 1–4**; Lapisan 4 dipecah lagi dengan sub-kategori karena menampung
katalog CSMS/OCPP/firmware yang sebelumnya ada di tab *Open-Source Stack*.

| Grup | Kategori |
|---|---|
| 🔌 EV charging — lapisan domain | L1 Lokasi & inventori charger · L2 Sesi charging, demand & mobilitas · L3 Spesifikasi kendaraan · L4 Siting, simulasi & operasi (sub: siting & optimasi · simulasi & profil beban · CSMS & back-office · pustaka OCPP · server & simulator OCPP · firmware, hardware & manajemen energi · roaming/ISO 15118/metering · standar & protokol · katalog & pintu gali) |
| 🧮 Metode & alat analisis | Facility location, siting & equity · GIS core & geo-AI · Sistem tenaga & pemodelan energi · Surya, cuaca & emisi · Data Indonesia · Statistik, kausal, Bayesian & ML · Data engineering & experiment tracking |
| 📖 Riset, penulisan & belajar | Lit review & manajemen referensi · LLM untuk riset · Menulis, publikasi & visualisasi · Belajar (mahasiswa) |

Keputusan penempatan yang perlu diketahui:

* Daftar "EV charging & mobility" dilebur ke lapisan domain: `acnportal` → L2, `simbev` dan
  `everest-core` → L4, `ocm-system` → L1; `movingpandas` dan `scikit-mobility` → L2 karena
  data mobilitas adalah bahan estimasi permintaan.
* Proyek dengan beberapa repo turunan dicatat **sekali**, repo lainnya masuk `links`
  (mis. CitrineOS → `citrineos-core` + umbrella + `citrineos-ocpi`; OpenEVSE → org + firmware ESP32;
  Global EV Data Initiative → org + tiga repo WebGIS).
* Sumber non-GitHub yang dulu ada di tab *Global EV Data* (IEA GEVO, EAFO, AFDC, portal OCM)
  menjadi entri berjenis `portal` di L1; dataset SPKLU Mendeley dan ACN-Data berjenis `dataset`.
* Repo Varanasi GIS-MCDM, aksesibilitas Norwegia, Hamburg, dan Chargym **tidak** dimasukkan
  karena URL-nya belum diverifikasi; halaman topik GitHub yang memuatnya dicatat sebagai
  entri `topic` ("pintu gali") dengan catatan itu.

## Skema entri

```python
R(cat, url, name, desc, role,
  sub=None,        # sub-kategori (hanya kategori yang punya `subs`)
  kind=None,       # repo | org | topic | dataset | portal | standard — diturunkan dari URL bila kosong
  themes=(),       # tema riset: akses | jaringan | emisi | bisnis (= kategori Perpustakaan)
  tabs=(),         # tab dashboard yang BENAR-BENAR memakai sumber ini (lihat TAB_LABELS)
  tags=(),         # kata kunci pendek untuk pencarian
  featured=False,  # inti riset → kartu bertepi emas, filter "⭐ Inti saja"
  links=())        # [(label, url), ...] repo turunan / unduhan terkait
```

`role` adalah satu kalimat **peran sumber itu dalam riset SPKLU** (bukan deskripsi ulang) —
inilah yang membedakan database ini dari daftar tautan biasa.

`catalog.py` menolak: kategori/sub/tema/tab yang tak dikenal, id atau URL dobel
(termasuk URL yang sudah dipakai di `links` entri lain).

## Di tab

* **Grup → kategori → sub**: chip dengan jumlah entri; deskripsi kategori tampil di kotak kuning.
* **Pencarian** menyaring nama, `owner/repo`, deskripsi, peran, tag, dan sub-kategori.
* **Tema riset** memakai kunci & warna Perpustakaan, jadi "semua sumber untuk naskah bertema
  *jaringan*" adalah satu klik.
* **Chip biru ↗** melompat ke tab dashboard yang memakai sumber itu (`window.gotoTab`).
* **★ Muat statistik GitHub** mengambil bintang/fork/bahasa/push terakhir untuk entri yang
  sedang tampil (≤ 50 per klik, tanpa kunci → 60 permintaan/jam), disimpan 7 hari di
  `localStorage`. Urutan "★ bintang" tersedia setelah dimuat.
* **⬇ Salin Markdown** menyalin daftar yang sedang tampil, dikelompokkan per kategori.
* Deep link: `index.html#tab=resources&cat=siting` (id kategori: `L1`…`L4`, `siting`, `gis`,
  `power`, `solar`, `indonesia`, `stats`, `dataeng`, `litrev`, `llm`, `writing`, `belajar`).
