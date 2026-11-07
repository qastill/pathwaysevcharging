# v4: deck ilustratif, infografis, beranimasi

Berkas: `slides/Capacity_Maps_Equity_CIRED2027_v4.pptx`, berisi 32 slide dengan speaker notes. Angkanya sama dengan v3
(`papers/capacity/capacity.json` + `papers/capacity/v3/strengthen.json`); hanya penyajiannya yang berubah.

## Yang baru dibanding v3

- **Ilustrasi:** ikon di setiap konsep (Font Awesome lewat react-icons), peta hero data asli di slide judul dan
  penutup, peta berlabel kota, dan peta celah dengan callout per klaster (Bogor–Depok, Sukabumi, Bandung,
  Karawang–Subang, Cirebon). Juga diagram UE vs Jawa Barat, rantai kausal peta → investasi → siapa terlayani,
  dan hierarki GI → penyulang → trafo → charger.
- **Infografis:**
  - funnel data (53.797 catatan → 50 situs)
  - gauge donat AUC ("86 dari 100")
  - waffle "dari 100 pemilik", untuk seluruh pemilik dan untuk sepertiga kabupaten termiskin
  - piktogram 50 situs per aturan (terjangkau / terlantar / tak layak)
  - batang kesenjangan kaya–miskin
  - perbandingan tiga metrik "kemerataan vs jangkauan"
  - scorecard ketahanan per ukuran sel
  - ledger klaim berlampu lalu lintas
  - timeline roadmap
- **Animasi:** setiap slide punya transisi fade, dan elemennya muncul berurutan secara otomatis (fade, atau wipe dari
  bawah/kiri untuk batang). Ada empat slide pembatas bagian (01–04).

## Cara membangun ulang

```bash
python3 papers/capacity/v4/build_deck_figs_v4.py      # peta & infografis gambar -> papers/capacity/v4/figs
# butuh: pptxgenjs react react-dom react-icons sharp
NODE_PATH=<node_modules> APPLY_THEME=<skill pptx>/scripts/apply_theme.js \
  node papers/capacity/v4/build_deck_v4.js /tmp/v4_raw.pptx
python3 papers/capacity/v4/add_animations.py /tmp/v4_raw.pptx slides/Capacity_Maps_Equity_CIRED2027_v4.pptx
```

`add_animations.py` membaca `objectName` berpola `a<langkah><efek>-…` (efek f = fade, u = wipe dari bawah,
r = wipe dari kiri) dan menulis `<p:transition>` dan `<p:timing>` ke tiap slide. Elemen berlangkah sama muncul
bersamaan; langkah berikutnya mulai setelah langkah sebelumnya selesai ("After Previous").

Pratinjau LibreOffice tidak menampilkan animasi. Animasi terlihat saat Slide Show di PowerPoint.
