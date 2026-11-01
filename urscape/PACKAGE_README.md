# ur-scape site "West Java" — EV charging, access equity, Rebana, power grid

23 lapisan grid (0,5 menit busur ≈ 0,9 km) untuk [ur-scape](https://ur-scape.com) v0.9.9x, dibangun dari
https://github.com/qastill/pathwaysevcharging (`urscape/build.py`). Tidak perlu QGIS.

## Pasang

```bash
python3 install.py "/path/ke/ur-scape/Data"      # folder Data yang berisi layers.csv
```

atau manual: salin `Sites/West Java/` ke `Data/Sites/`, lalu tempel isi `layers_add.csv` (tanpa baris header) ke
akhir `Data/layers.csv` dan isi `citations_add.csv` ke akhir `Data/citations.csv` (keduanya UTF-16). Buka ur-scape → Site Browser → **West Java**.

## Lapisan

| Grup | Lapisan | Sumber |
|---|---|---|
| EV Charging | Stations · Chargers · Energy · Sessions · Utilisation | PLN Charge.IN Jun 2026; transaksi PLN Jabar Mar 2026 |
| EV Charging | Travel Time to Nearest Charger · Chargers within 10/30 min · Charger Access Class · Charging Capacity per Household (E2SFCA) · Charging Service Ladder | `ttm/ttm.json` — TTM r5r (Alyas Widita), GADM 4.1, Kontur 2023 |
| Society and Economy | Population Density (Jabar–Jakarta–Banten) · Rebana HDI, Poverty, Expenditure, Distance to Substation/Charger, Substation Headroom, Chargers per Kecamatan | Kontur 2023; BPS 2024; `analysis/rebana_data.json` |
| Power Grid | Substation Capacity · Substation Peak Loading · Power Plant Capacity · Transmission Lines (70/150/500 kV) | RUPTL 2025-2034 × OSM (`data/grid-id/data_jamali.js`); beban GI PLN UID Jabar |

Nilai dirasterisasi dari titik tengah sel (poligon desa/kecamatan) atau dijumlahkan per sel (titik). Sitasi tiap lapisan
terbaca lewat ikon ⓘ di panel Data Layers.
