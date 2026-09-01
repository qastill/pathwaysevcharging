# Analisis EV × Jaringan Distribusi (Jawa Barat)

Pipeline yang menghubungkan sisi permintaan EV (pelanggan KBLBB + SPKLU) dengan
kondisi jaringan distribusi (gardu + Gardu Induk), lalu mengekspor hasilnya
sebagai payload untuk tab **⚡ EV × Jaringan** di `index.html`.

## Urutan jalan

```bash
pip install openpyxl

# --- jalur 1: EV x gardu distribusi ---
python3 analysis/prepare.py    # xlsx -> analysis/gardu.csv, analysis/spklu.csv
python3 analysis/join.py       # spatial join -> analysis/joined.pkl
python3 analysis/insight.py    # laporan A-H  (konsol)
python3 analysis/insight2.py   # laporan I-L  (konsol)
python3 analysis/insight3.py   # laporan M-O  -> analysis/out3.json
python3 analysis/export.py     # -> analysis/grid.json

# --- jalur 2: karbon, harga, lapisan jaringan hulu ---
node analysis/carbon.mjs       # bauran energi & faktor emisi -> analysis/carbon.json
python3 analysis/price.py      # harga & karbon per transaksi -> analysis/price.json
node analysis/maplayers.mjs    # pembangkit/transmisi/GI -> analysis/maplayers.json
node analysis/export2.mjs      # gabung ketiganya -> analysis/grid2.json

# --- pasang ke dashboard ---
python3 analysis/inject.py     # sisipkan/perbarui tab di index.html
```

`price.py` membutuhkan `analysis/trx.csv` (ekspor kolom harga dari
`Detail Transaksi SPKLU 202603.xlsx`, sheet `Detail Transaksi`) dan
`analysis/carbon.json`, jadi jalankan `carbon.mjs` lebih dulu.

`inject.py` **idempoten**: bila tab sudah ada, blok lama dicopot lebih dulu lalu
dipasang ulang, sehingga aman dijalankan berkali-kali tanpa `git checkout`.
Batas blok ditandai `<!-- GX:BEGIN/END -->` (markup) dan `/* GX:BEGIN/END */` (skrip).

## Berkas keluaran

| Berkas | Isi |
|---|---|
| `gardu.csv` | 53.797 gardu, 32 kolom terpilih dari `Gardu_Beban_Lokasi_JABAR.xlsx` |
| `spklu.csv` | 636 unit SPKLU dari `Master SPKLU Maret 2026.xlsx` |
| `trx.csv` | 100.782 transaksi SPKLU Maret 2026 dengan rincian komponen harga |
| `grid.json` | payload EV x gardu (~250 KB), disisipkan sebagai `D.grid` |
| `grid2.json` | payload karbon + harga + lapisan peta (~370 KB), sebagai `D.grid2` |
| `carbon.json` | bauran energi & faktor emisi turunan, per sistem |
| `price.json` | struktur harga, PPJ per pemda, pola jam, biaya per 100 km |
| `maplayers.json` | pembangkit, gardu induk, dan ruas transmisi dalam kotak peta |
| `page.html` | markup tab |
| `render.js` / `render2.js` | renderer tab (chart, peta, tabel, narasi) |

Berkas antara berukuran besar (`gardu.csv`, `*.pkl`) tidak di-commit; semuanya
bisa dibuat ulang dari xlsx sumber di root repositori.

## Asumsi utama

- %beban gardu = arus rata-rata 3 fasa ÷ arus nominal (kVA×1000 ÷ √3×400 V), diambil maksimum siang/malam.
- Headroom aman memakai batas pembebanan 80%.
- Beban EV = jumlah charger × 7,7 kVA × faktor keserempakan (CF 1,0 / 0,6 / 0,35; 0,6 sebagai kasus dasar).
- Radius join: pelanggan EV ≤ 1 km, situs SPKLU ≤ 2 km ke gardu terdekat.
- Gardu dibuang bila koordinat di luar Jawa Barat, kapasitas di luar 5–3.000 kVA, atau %beban >200%.

## Asumsi karbon & harga

Faktor emisi **tidak** diukur, melainkan diturunkan: kapasitas terpasang tiap
jenis pembangkit dikalikan capacity factor tipikal untuk memperkirakan energi
tahunan, lalu dikalikan faktor emisi pembakaran per jenis. Seluruh parameter ada
di `analysis/carbon.mjs` (konstanta `TECH`) dan ditampilkan apa adanya pada tabel
"Asumsi karbon & harga" di dashboard.

Hasilnya: **0,77 kgCO₂/kWh** untuk sistem Jamali — jatuh di rentang yang lazim
dikutip untuk Jawa-Bali, yang menandakan asumsinya wajar. Untuk pelaporan resmi
tetap gunakan faktor emisi jaringan terbitan pemerintah, bukan angka ini.

Parameter harga (`analysis/price.py`): konsumsi EV 0,17 kWh/km, mobil bensin
11 km/liter dan 190 gCO₂/km, harga bensin Rp 12.500/liter, tarif listrik rumah
R-1 nonsubsidi Rp 1.699,53/kWh. Tarif SPKLU **tidak** diasumsikan — dihitung dari
101.020 transaksi nyata. Perbarui parameter ini ketika harga berubah.

Keterbatasan selengkapnya ada di panel "Metodologi & keterbatasan" dan
"Asumsi karbon & harga" pada tab dashboard.
