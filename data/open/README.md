# data/open — data terbuka global, dipotong ke West Java (grid 0,0025° ≈ 278 m)

Semua `*.tif` di sini dibuat oleh `prep.py` dari unduhan mentah (tidak disimpan di repo, ~450 MB):

| Berkas | Sumber | Lisensi |
|---|---|---|
| `solar_*.tif`, `air_temp.tif`, `elevation.tif` | Global Solar Atlas 2.0 (Solargis / World Bank ESMAP) — point API `https://api.globalsolaratlas.info/data/lta?loc=lat,lon`, sampel tiap 0,025° (`solar_grid.jsonl`) | CC BY 4.0 |
| `lc_*.tif` | ESA WorldCover 2021 v200, tile S09E105 & S09E108 (`esa-worldcover.s3.eu-central-1.amazonaws.com`) | CC BY 4.0 |
| `built_*.tif`, `pop_*.tif` | GHSL R2023A GHS-BUILT-S E1975/E2000/E2020 & GHS-POP E2000/E2025/E2030, tile R10_C29 (3″) | CC BY 4.0 |
| `flood_rp100_*.tif` | JRC Global Flood Hazard Maps (CEMS-GloFAS), RP100, tile ID212_N0_E100 | CC BY 4.0 |
| `wind_100m.tif` | Global Wind Atlas 3.0 (DTU / World Bank), `IDN_wind-speed_100m.tif` | CC BY 4.0 |

```bash
python3 data/open/prep.py /folder/unduhan     # -> data/open/*.tif
python3 urscape/build.py && python3 urscape/build.py Rebana --keep   # lapisan ur-scape + web
python3 analysis/rebana_open_build.py          # -> analysis/rebana_open_data.json (laporan rebana_territory.html)
```
