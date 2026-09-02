# Naskah & perpustakaan

Dua tab dashboard dibangun dari folder ini:

| Tab | Sumber | Payload |
|---|---|---|
| 🔌 **Capacity Maps** | `papers/capacity/` | `capacity.json` → `D.cap` |
| 📚 **Perpustakaan** | `papers/library/` | `library.json` → `D.lib` |
| 🌏 ASEAN Paper | `papers/asean/` | — (statis, lihat `papers/asean/inject.py`) |

## Urutan jalan

```bash
pip install openpyxl

python3 papers/capacity/prepare.py   # data mentah PLN -> papers/capacity/capacity.json
python3 papers/library/build.py      # naskah md/docx -> papers/library/library.json
python3 papers/inject_papers.py      # sisipkan/perbarui kedua tab di index.html
```

`inject_papers.py` **idempoten**: blok lama dicopot lebih dulu, jadi aman dijalankan
berkali-kali tanpa `git checkout index.html`. Batas blok ditandai
`<!-- CAP:BEGIN/END -->`, `<!-- LIB:BEGIN/END -->` (markup) dan
`/* CAP:BEGIN/END */`, `/* LIB:BEGIN/END */` (skrip).

## papers/capacity — CIRED 2027

`prepare.py` mereproduksi seluruh metode makalah dari berkas mentah di akar repositori
(`Gardu_Beban_Lokasi_JABAR.xlsx`, `Data pelanggan EV.txt`, `Rekap_SPKLU_Jabar_ArcGIS.csv`):

- headroom trafo & Gardu Induk pada batas pembebanan 80 %: `H = max(0, S·(0,8 − λ))`;
- koreksi pertumbuhan beban ke Maret 2026: `λ(2026) = λ(t)·(1+g)^(2026,2−t)`,
  dengan `g` = 0 / 3,0 / 5,9 / 9,7 %/tahun;
- agregasi ke sel 0,045° (≈5 km) dan klasifikasi permintaan × headroom;
- tiga aturan penempatan 50 situs baru (headroom-only, demand-only, demand-within-headroom);
- audit kesiapan publikasi atas 53.797 catatan survei.

Peta dan grafik di tab dihitung **dari payload ini**, bukan dari gambar naskah, jadi
angkanya bisa berbeda tipis dari yang tercetak. Tabel 2 di halaman menampilkan kedua
versi berdampingan, dan panel "Gambar asli naskah" merinci selisih yang diketahui.

Reproduksi terhadap angka naskah:

| Angka | Naskah | Hitung ulang |
|---|---|---|
| Catatan trafo / layak pakai | 53.797 / 41.129 | 53.797 / 41.129 |
| Trafo Gardu Induk / MVA | 182 / 9.790 | 182 / 9.790 |
| Umur survei median / tertua | 2,3 / 6,2 tahun | 2,3 / 6,2 tahun |
| Pelanggan EV tergeokode | 3.687 | 3.687 |
| ρ energi ~ headroom absolut / relatif | +0,42 / −0,06 | +0,42 / −0,06 |
| Headroom trafo, apa adanya → 3 %/th | 2.624 → 2.392 MVA | 2.624 → 2.392 MVA |
| Pemilik terjangkau (headroom / demand / DwH) | 694 / 807 / 789 | 694 / 809 / 789 |
| Situs terlantar | 15 / 0 / 0 | 15 / 0 / 0 |
| Cakupan baseline | 75,5 % | 75,4 % |

| Headroom GI, apa adanya → 3 % → 9,7 %/th | 2.377 → 1.912 MVA → −52 % | 2.377 → 1.912 MVA → −52 % |

Headroom GI baru cocok setelah beban GI dituakan dari **April 2022** (tanggal register
GI/penyulang di Tabel 1 naskah) — umur 3,9 tahun ke Maret 2026 adalah satu-satunya nilai
yang mereproduksi 1.912 MVA pada 3 %/th *dan* −52 % pada 9,7 %/th sekaligus; konstanta
`GI_YEAR` di `prepare.py`.

Yang **belum** cocok, dan tidak bisa diselesaikan tanpa skrip asli penulis:

- **Gini antar-kabupaten** (naskah 0,692 → 0,600; hitung ulang 0,493 → 0,360). Lima
  definisi dicoba — Gini pangsa cakupan per kabupaten, sama dengan 27 kabupaten, Gini
  pemilik tercakup, Gini pemilik tak tercakup, dan versi tertimbang pemilik — tidak ada
  yang mereproduksi keempat angka naskah. Urutan antar-aturan tetap sama.
- **Jumlah sel** (naskah 1.292 sel / 235 sel EV / 129 belum terlayani / 901 pemilik;
  hitung ulang 1.295 / 238 / 132 / 908). Empat jangkar grid dicoba (`floor`, `round`,
  sudut bbox, titik minimum); jumlah sel EV selalu 238, jadi selisihnya ada pada himpunan
  titik pelanggan yang dipakai naskah, bukan pada grid.

## papers/library — perpustakaan naskah

`build.py` mengubah `papers/*.md` dan berkas `.docx` menjadi HTML siap baca, memberi
indeks stabil `data-b` pada tiap blok, lalu menulis katalog + isi ke `library.json`.
Metadata tiap naskah ada pada konstanta `PAPERS` di dalam `build.py`; rencana submisi per
kuartal pada `PLAN`; daftar kategori pada `CATEGORIES`. **Perbarui di sana**, bukan di
`library.json`.

Delapan naskah, empat kategori:

| Kategori | Naskah |
|---|---|
| Akses & keadilan infrastruktur pengisian | Paper 1 (equity & perception) · Paper 2 (coverage to capability) |
| Jaringan distribusi & perencanaan | CIRED 2027 Capacity maps · CIRED 2027 Energy forecast → network load |
| Emisi & dekarbonisasi | Tailpipe to smokestack · Captive generation & CBAM |
| Model bisnis, pasar & kebijakan | ASEAN comparative · Balance sheet problem (battery swapping) |

Tiap naskah membawa **brief riset** yang tampil di kartu dan di kepala pembaca: `goal`
(tujuan), `finding` (temuan kunci), `method`, `data`, dan `abstract`. Abstrak **tidak
ditulis tangan** — `abstract_of()` mengambil paragraf setelah heading *Abstract* /
*Summary of Research* dari naskahnya sendiri, dan build gagal bila tidak ketemu.

Kolom `venue` adalah rencana publikasi; `venue_src` mencatat asalnya. Dua naskah
(*Tailpipe to smokestack*, *Captive generation & CBAM*) tidak menyebut sasaran di
naskahnya, jadi sasarannya **usulan** — ditandai lencana merah pada kartu dan tabel
"Rencana publikasi", dan tinggal diganti di `build.py`.

Fitur tinjauan pembimbing di tab: sorot kalimat → **Komentari** (komentar tertambat ke
blok) atau **Tandai** (penanda kuning); komentar tampil di rel kanan, bisa ditandai
selesai atau dihapus; tombol **⬇ Unduh** menghasilkan `.json` (untuk dimuat balik) dan
`.md` (untuk dibaca manusia); tombol **⬆ Muat** menggabungkan berkas komentar dari
peninjau lain.

### Unggah naskah & penyimpanan bersama

Tombol **📤 Unggah naskah baru** menerima `.docx` / `.md` / `.txt`. Berkas diparse **di
peramban** (docx lewat mammoth.js, markdown lewat padanan JS dari `build.py`), diberi
indeks blok `data-b` yang sama dengan naskah bawaan, lalu disimpan.

Tab bekerja dalam dua mode, dipilih otomatis lewat `GET /api/papers`:

| Mode | Kapan | Naskah unggahan | Komentar |
|---|---|---|---|
| **Lokal** | env Vercel belum diatur | `localStorage` peramban pengunggah | `localStorage` peramban peninjau |
| **Bersama** | env Vercel sudah diatur | tabel `papers` + bucket `papers` di Supabase | tabel `paper_comments` — terlihat semua peninjau |

Mengaktifkan mode bersama:

1. Jalankan `papers/library/schema.sql` pada proyek Supabase yang dipilih (SQL Editor).
   Skema membuat `papers`, `paper_comments`, bucket publik `papers`, dan kebijakan RLS:
   anon boleh **baca** semua serta **tulis komentar**; **unggah naskah hanya lewat kunci
   layanan** di `api/papers.js`.
2. Atur env var di Vercel (Project → Settings → Environment Variables), lalu redeploy:

   | Var | Isi |
   |---|---|
   | `SUPABASE_URL` | `https://<ref>.supabase.co` |
   | `SUPABASE_ANON_KEY` | kunci publik (anon / `sb_publishable_…`) — dikirim ke klien |
   | `SUPABASE_SERVICE_KEY` | kunci `service_role` — hanya dipakai server-side untuk unggah |
   | `PAPERS_UPLOAD_KEY` | kata sandi yang diketik pengunggah di form |

`api/papers.js` mengikuti pola `api/chat.js`: kunci hanya hidup di env server, tidak
pernah masuk repositori atau ke peramban (kecuali kunci anon, yang memang publik dan
dibatasi RLS). Unggahan dibatasi 20 MB per berkas; `id` naskah harus slug
(`^[a-z0-9][a-z0-9-]{1,60}$`) dan unggahan dengan `id` sama akan menimpa.

Naskah bawaan (empat di `build.py`) tetap statis dan selalu tampil; naskah unggahan
digabung setelahnya.
