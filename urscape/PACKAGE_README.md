# ur-scape sites "West Java" and "Rebana": EV charging, access equity, power grid

Two sites with the same 28 grid layers: **West Java** (0.5 arc-minute cells, about 0.9 km, Jabar-Jakarta-Banten) and
**Rebana** (300 m cells, Subang-Indramayu-Majalengka-Sumedang-Kuningan-Cirebon) for [ur-scape](https://ur-scape.com) v0.9.9x, built from
https://github.com/qastill/pathwaysevcharging (`urscape/build.py`). QGIS is not required.

Report: https://jabar-ev.vercel.app/analysis/rebana_insights.html · User guide: https://jabar-ev.vercel.app/analysis/urscape_guide.html

## Install

```bash
python3 install.py "/path/to/ur-scape/Data"      # the Data folder that contains layers.csv
```

Or by hand: copy `Sites/West Java/` and `Sites/Rebana/` into `Data/Sites/`, then append the contents of `layers_add.csv` (without the header row) to the end of
`Data/layers.csv`, and the contents of `citations_add.csv` to the end of `Data/citations.csv` (both files are UTF-16).
Open ur-scape, go to the Site Browser and choose **Rebana** or **West Java**.

## Layers

| Group | Layers | Source |
|---|---|---|
| EV Charging | Stations · Chargers · Energy · Sessions · Utilisation | PLN Charge.IN Jun 2026; PLN West Java transactions Mar 2026 |
| EV Charging | Travel Time to Nearest Charger · Chargers within 10/30 min · Charger Access Class · Charging Capacity per Household (E2SFCA) · Charging Service Ladder | `ttm/ttm.json`: r5r travel-time matrix (Alyas Widita), GADM 4.1, Kontur 2023 |
| Society and Economy | Population Density (West Java, Jakarta, Banten) · Rebana HDI, Poverty, Expenditure, Distance to Substation/Charger, Substation Headroom, Chargers per Kecamatan | Kontur 2023; BPS 2024; `analysis/rebana_data.json` |
| Insights | Charger Siting Priority (0–100) · Rebana KPI Kecamatan · Population Beyond 30 min (access gap) · Coverage Model Picks · Transformer Overload Share (Indramayu) | derived from the layers above; the formula is in each layer's Citation tag |
| Power Grid | Substation Capacity · Substation Peak Loading · Power Plant Capacity · Transmission Lines (70/150/500 kV) | RUPTL 2025-2034 × OSM (`data/grid-id/data_jamali.js`); PLN UID Jabar substation loads |

Values are rasterised at cell centres (village or sub-district polygons) or summed per cell (points). Each layer's citation
can be read through the ⓘ icon in the Data Layers panel.
