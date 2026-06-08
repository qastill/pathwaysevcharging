# PAPER 2 — DRAFT

**Working title:** *From coverage to capability: data-driven siting and a utilisation–availability diagnosis of a rapidly scaling national EV-charging network — a transaction-level study of Indonesia*

**Target journal (primary):** *Sustainable Cities and Society* (Elsevier, Q1)
**Alternatives:** *Applied Energy* (Q1) · *eTransportation* (Q1) · *Computers, Environment and Urban Systems* (Q1, if the GIS/MCDA method is the headline)

> Draft note: figures are from the project datasets (national Master SPKLU registry & monthly consumption series 2024–2026; West Java transaction detail, March 2026; Jakarta Raya + West Java transaction detail, 1–8 June 2026). Province assignment for national points is **estimated from coordinates** — state this explicitly. Verify all numbers; `[VERIFY]` marks placeholder citations.

---

## Structured abstract (≈250 words)

**Context.** EV-charging research overwhelmingly measures *coverage* — how many chargers, and where. Far less is known about whether a fast-growing national network is *capable*: actually available, well-utilised, and sited where demand is.

**Objective.** Using one of the largest operational EV-charging datasets reported for a developing country, we (i) characterise the explosive growth and spatial structure of Indonesia's public SPKLU network, (ii) diagnose an under-examined **availability gap**, (iii) quantify *which kinds of locations actually sell energy*, and (iv) propose and validate a transferable, transaction-grounded **site-selection and commercial-viability** framework.

**Data & methods.** We combine the national Master SPKLU registry (≈3,200 sites; location, capacity, operator, operational status), the national monthly consumption series (Jan 2024–Jun 2026), and transaction-level detail for West Java (101,020 sessions, Mar 2026) and Jakarta Raya (56,740 sessions over 8 days, Jun 2026). Methods: growth and concentration analysis; an operational-status diagnosis; a venue-type ("sector") utilisation classifier; and a multi-criteria (MCDA) weighted-overlay siting model extended with catchment, competitor/cannibalisation and a simple payback model, validated against observed per-venue utilisation.

**Results.** National energy sold rose ≈**5×** in one year (≈9.1→48.6 GWh, 2024→2025) with a 2026 run-rate near 10 GWh/month; demand is heavily Java-centric (~67% of sites). Crucially, ~**32% of stations report an "offline" operational state** — a reliability gap invisible to coverage maps. Utilisation is highly venue-dependent: **toll-road rest areas sell ~3.5× the energy per site of a utility-office charger and ~13× a hotel charger**; midday-peaking, DC-dominated demand in Jakarta indicates a commercial/fleet usage rhythm. Our siting model reproduces these patterns and ranks candidate sites by payback.

**Implications.** "More chargers" is the wrong objective; *capable* chargers — available, high-throughput, demand-matched — is the right one. We offer an open, reproducible siting toolkit for emerging-economy charging networks.

**Keywords:** EV charging; site selection; MCDA; utilisation; availability/reliability; smart cities; Indonesia

---

## 1. Introduction
- Charging networks in emerging economies are scaling faster than they are being *evaluated*; coverage metrics dominate, capability metrics (availability, utilisation, demand-match) are neglected. `[VERIFY]`
- Three blind spots: (a) **availability/uptime** rarely measured at network scale; (b) **utilisation by location type** rarely quantified on real energy data; (c) **site-selection methods** rarely *validated* against observed demand.
- **Contributions:** (1) a national growth + spatial + **availability** diagnosis on operational data; (2) a venue-type utilisation taxonomy (where charging actually "sells"); (3) a transaction-validated MCDA + commercial-viability siting framework with catchment & cannibalisation; (4) an open, reproducible dashboard implementation.
- **Research questions:**
  - **RQ1 (Growth & structure):** How fast, and how spatially concentrated, is the network's demand?
  - **RQ2 (Availability):** What share of stations are non-operational, and where?
  - **RQ3 (Utilisation by venue):** Which location types deliver the most energy per site, and why?
  - **RQ4 (Siting):** Can an MCDA + catchment + payback model reproduce observed utilisation and rank new sites credibly?

## 2. Related work
- EV charging demand & utilisation modelling. `[VERIFY]`
- Charging-station **site selection** (MCDA/AHP/GIS, optimisation). `[VERIFY: reviews of EVCS siting]`
- Reliability/uptime of public charging (mostly high-income contexts). `[VERIFY]`
- Gap statement: combine all three on a national, developing-country, transaction-level dataset.

## 3. Data & methods
### 3.1 Data
| Source | Content | Scope |
|---|---|---|
| National Master SPKLU | ~3,200 sites: coords, capacity, **status**, charger/connector count, PLN/non-PLN | Indonesia (province **estimated from coordinates**) |
| National consumption series | monthly sessions, kWh, revenue | Jan 2024 – Jun 2026 |
| West Java transactions | 101,020 sessions, 2.26 GWh, AC/DC, duration | Mar 2026 |
| Jakarta Raya transactions | 56,740 sessions, 1.29 GWh, hourly/UP3/kota/power | 1–8 Jun 2026 |

### 3.2 Methods
- **Growth & concentration (RQ1):** monthly series; year-on-year multiples; island/province share (note coordinate-based province estimation + Jakarta bounding-box correction).
- **Availability diagnosis (RQ2):** classify operational status (available / in-use / offline / unavailable / maintenance); map and quantify the offline share by region; discuss measurement caveats (snapshot vs sustained downtime).
- **Venue utilisation (RQ3):** keyword classifier assigns each station to a venue sector (toll rest area, mall, hotel, dealer, PLN office, F&B, hospital, public/transport, residential, etc.); compare **kWh per site**, sessions/site, kWh/session, mean power, dwell; interpret via dwell-time × charger-power × captive-demand mechanism. (West Java has per-site energy; national has site counts.)
- **Siting model (RQ4):** min–max-normalised MCDA weighted overlay (demand, growth, supply-gap, equity) at area level; point-level candidate scoring by distance-to-nearest-SPKLU + host demand; **catchment** (radius/iso-proxy), **competitor/cannibalisation** scan (PLN vs private), and a **commercial-viability** score + simple **payback** anchored to observed sessions/unit/month. Validate by checking the model ranks high-utilisation venue types (toll/dealer) above low ones (hotel).

## 4. Results
- **R1 — Hockey-stick growth (RQ1):** ≈9.1 GWh (2024) → ≈48.6 GWh (2025), ~**5.3×**; 2026 run-rate ~10 GWh/month (~120 GWh/yr trajectory); ~2.4M registered users. Java ≈67% of sites; private sector ≈32% of the network. *(Fig. 1 growth; Fig. 2 island/province shares.)*
- **R2 — Availability gap (RQ2):** ~**32%** of stations in "offline" state (≈1,000 of ~3,200); available ≈49%, in-use ≈16%. Map the offline share by region. **Headline: coverage maps overstate effective capacity.** *(Fig. 3 condition map; Table 1 status by region.)*
- **R3 — Where charging sells (RQ3):** ranked kWh/site (West Java, Mar 2026): toll rest area ≈**18,700**, auto dealer ≈17,300, mall ≈10,100, …, PLN office ≈**5,400**, hotel ≈**1,400**. → toll ≈3.5× a utility office, ≈13× a hotel. Mechanism: captive transit demand + high DC power + short dwell = high turnover; amenity AC sites idle. Jakarta June: **DC-dominant, midday-peaking** (fleet/ride-hail rhythm), demand concentrated in South/East Jakarta. *(Fig. 4 venue ranking; Fig. 5 power-vs-intensity; Fig. 6 Jakarta hourly.)*
- **R4 — Siting validation (RQ4):** the MCDA + catchment + payback model ranks transit/dealer venues highest and saturated/amenity sites lowest, consistent with observed utilisation; example candidate rankings + payback ranges. *(Fig. 7 candidate map; Table 2 viability/payback.)*

## 5. Discussion
- Reframe the policy objective from **coverage → capability** (available + utilised + demand-matched).
- Availability as the cheapest capacity: fixing offline stations may add more effective charging than new builds.
- Demand-matched siting: bias toward transit corridors / high-throughput DC; treat hotels/offices as amenity, not revenue.
- Grid as the missing layer (distance to substation/feeder, spare transformer capacity) — the operator's informational advantage; flag as future integration.
- Transferability to other emerging-economy networks.

## 6. Limitations
- Province assignment **estimated from coordinates** (nearest-centroid + Jakarta bbox) — aggregate-robust, not site-exact.
- National per-station transactions unavailable (status counters reset to ~0) → utilisation depth shown for West Java + Jakarta only; national consumption is a country total (not region-split).
- "Offline" is a snapshot status (may over/understate sustained downtime).
- Venue classifier is heuristic (a small share mis-bucketed); payback model is indicative, not a financial quotation.

## 7. Conclusion
A rapidly scaling network can be wide yet not deep: Indonesia's SPKLU footprint is impressive, but ~a third sits offline and utilisation is sharply venue-dependent. A capability-first, demand-matched, reliability-aware deployment strategy — embodied in our open siting toolkit — better serves the EV transition than coverage alone.

---

### Figures/Tables plan
1. National monthly growth. 2. Island/province shares. 3. **National condition map** (status-coloured). 4. kWh/site by venue. 5. Power-vs-intensity quadrant. 6. Jakarta hourly rhythm. 7. Candidate-siting map + payback. T1: status by region. T2: candidate viability/payback. T3: venue utilisation summary.

### Reproducibility & data
Open dashboard implementation; aggregation scripts; data-availability statement; province-estimation method disclosed; PLN data-use permission.

### Suggested literature to position against (VERIFY exact citations)
EVCS site-selection reviews (MCDA/AHP/GIS/optimisation); charging utilisation & demand studies; public-charging reliability/uptime; smart-city infrastructure analytics; Indonesia/SE-Asia EV transition.
