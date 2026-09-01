# Analisis EV × Jaringan Distribusi (Jawa Barat)

Pipeline yang menghubungkan sisi permintaan EV (pelanggan KBLBB + SPKLU) dengan
kondisi jaringan distribusi (gardu + Gardu Induk), lalu mengekspor hasilnya
sebagai payload untuk tab **⚡ EV × Jaringan** di `index.html`.

## Urutan jalan

```bash
pip install openpyxl
python3 analysis/prepare.py    # xlsx -> analysis/gardu.csv, analysis/spklu.csv
python3 analysis/join.py       # spatial join -> analysis/joined.pkl
python3 analysis/insight.py    # laporan A-H  (konsol)
python3 analysis/insight2.py   # laporan I-L  (konsol)
python3 analysis/insight3.py   # laporan M-O  -> analysis/out3.json
python3 analysis/export.py     # -> analysis/grid.json (payload dashboard)
python3 analysis/inject.py     # sisipkan tab ke index.html
```

`inject.py` bersifat idempotent-aman: ia menolak berjalan bila tab sudah ada di
`index.html`, jadi jalankan `git checkout index.html` lebih dulu saat mengulang.

## Berkas keluaran

| Berkas | Isi |
|---|---|
| `gardu.csv` | 53.797 gardu, 32 kolom terpilih dari `Gardu_Beban_Lokasi_JABAR.xlsx` |
| `spklu.csv` | 636 unit SPKLU dari `Master SPKLU Maret 2026.xlsx` |
| `grid.json` | payload dashboard (~250 KB) yang disisipkan sebagai `D.grid` |
| `page.html` | markup tab |
| `render.js` | renderer tab (chart, peta, tabel, narasi) |

Berkas antara berukuran besar (`gardu.csv`, `*.pkl`) tidak di-commit; semuanya
bisa dibuat ulang dari xlsx sumber di root repositori.

## Asumsi utama

- %beban gardu = arus rata-rata 3 fasa ÷ arus nominal (kVA×1000 ÷ √3×400 V), diambil maksimum siang/malam.
- Headroom aman memakai batas pembebanan 80%.
- Beban EV = jumlah charger × 7,7 kVA × faktor keserempakan (CF 1,0 / 0,6 / 0,35; 0,6 sebagai kasus dasar).
- Radius join: pelanggan EV ≤ 1 km, situs SPKLU ≤ 2 km ke gardu terdekat.
- Gardu dibuang bila koordinat di luar Jawa Barat, kapasitas di luar 5–3.000 kVA, atau %beban >200%.

Keterbatasan selengkapnya ada di panel "Metodologi & keterbatasan" pada tab dashboard.
