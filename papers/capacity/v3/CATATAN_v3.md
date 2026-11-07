# v3: penguatan temuan "Capacity maps as an equity instrument"

Berkas:

- `papers/capacity/Capacity_Maps_Equity_CIRED2027_v3.docx`: naskah, 11 halaman, 10 figur, 4 tabel.
- `slides/Capacity_Maps_Equity_CIRED2027_v3.pptx`: 24 slide dengan speaker notes.
- `strengthen.py` → `strengthen.json`: semua uji tambahan.
- `build_figs_v3.py` → `figs/`, lalu `build_deck_v3.js` dan `build_paper_v3.js`.

Urutan jalan dari akar repositori:

```bash
pip install shapely matplotlib openpyxl
python3 papers/capacity/prepare.py                  # capacity.json (tidak diubah oleh v3)
python3 papers/capacity/v3/strengthen.py --variants # ± 1 menit, termasuk sel 0,03/0,06/0,09 derajat
python3 papers/capacity/v3/build_figs_v3.py
NODE_PATH=<node_modules berisi pptxgenjs> node papers/capacity/v3/build_deck_v3.js
DOCX_MODULE=<path modul docx> node papers/capacity/v3/build_paper_v3.js
```

## Koreksi penting: field kabupaten

Field `kab` di `capacity.json` berisi **47 label** untuk 26 kabupaten/kota yang memiliki pemilik EV. Label itu
mencampur nama kabupaten dengan nama UP3/ULP (GUNUNG PUTRI, PLERED, JATIBARANG…) dan ejaan ganda
(`BOGOR` vs `3201 - KAB. BOGOR`). Akibatnya, "Gini antar-kabupaten" di naskah lama (0,69 → 0,60) maupun v2
(0,493 → 0,360) **tidak dihitung atas kabupaten**. v3 menempatkan setiap titik pemilik dan pusat sel ke
27 poligon BPS (`data/kabkota_bps.geojson`) dan menggabungkannya dengan pengeluaran per kapita 2024
(`equitymap/input/jabar_sosek_kabkota.csv`). Kode CSV tersimpan sebagai angka, sehingga "32.1" berarti
Majalengka (32.10); kode dinormalkan menjadi dua desimal.

`prepare.py` dan tab dashboard Capacity Maps masih memakai field lama dan belum diubah.

## Hasil uji (sel 0,045°, kecuali disebut lain)

| Uji | Hasil |
|---|---|
| AUC: apa yang membedakan sel bercharger | kVA terpasang 0,86 · jumlah trafo 0,84 · headroom absolut 0,85 · pemilik EV 0,76 · **headroom relatif 0,46** |
| Median kVA terpasang, sel bercharger vs tanpa charger | 11.395 vs 675 kVA (17×); persentase ruang sisa 30,8 % vs 32,7 % |
| ρ energi ~ headroom relatif (bootstrap 2.000) | −0,06, 95 % CI −0,21 sampai +0,09 |
| Cakupan sepertiga kabupaten termiskin (hari ini 71,7 %) | headroom-only 76,8 % · demand-only 87,5 % · dwh 89,7 % |
| Indeks konsentrasi terhadap pengeluaran (hari ini 0,029) | headroom-only 0,026 · demand-only 0,015 · dwh 0,012 |
| Gini antar-kabupaten (hari ini 0,234) | acak 0,144 · headroom-only 0,171 · dwh 0,174 · demand-only 0,191 |
| 5.000 portofolio acak, 50 situs | rata-rata 345 pemilik (p95 = 484); 24,6 situs terlantar; 8,0 situs tak layak |
| Ambang kelayakan 120/240/480/960 kVA | demand-only tak layak 2/3/6/12; dwh 807/789/754/734 pemilik; headroom-only tetap 694 |
| Ukuran sel 0,03/0,045/0,06/0,09° (N = 38 % kolam) | dwh vs headroom-only +20/+14/+32/+29 %; demand-only tak layak 10/3/2/0; headroom-only terlantar 19/15/0/4 |
| Dua tingkat (157 sel terlayani bertaut GI) | ρ(trafo, GI) = −0,02, 95 % CI −0,18 sampai +0,16; 44,6 % sumbang (35 + 35) |

## Status klaim

- **Robust:** roll-out mengikuti kepadatan grid; sel permintaan tinggi/headroom rendah kurang terlayani di semua
  ukuran sel; headroom-only menjangkau paling sedikit pemilik.
- **Baru, didukung (n kecil):** headroom-only paling sedikit menolong sepertiga kabupaten termiskin. Sepertiga
  termiskin hanya berisi 272 pemilik, 181 di antaranya di Kab. Bandung Barat.
- **Sensitif resolusi:** jumlah situs terlantar ("15") dan bagian headroom/pemilik di sel tanpa charger ("42 %",
  "24,6 %"). Dilaporkan sebagai angka 5 km, bukan headline.
- **Tidak didukung:** "demand-within-headroom menurunkan Gini antar-kabupaten paling jauh".
- **Dirumuskan ulang:** "51 % sumbang" → 44,6 %, dan kedua tingkat tidak berkorelasi (ρ ≈ 0).

## Masih terbuka

- Referensi [2], [3], [14]: judul dan tanggal akses perlu dikonfirmasi.
- Tingkat penyulang (2.574 penyulang) belum masuk analisis.
