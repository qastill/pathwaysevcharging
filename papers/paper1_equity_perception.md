# PAPER 1 — DRAFT

**Working title:** *Who is left behind? Spatial equity and public perception of public EV charging infrastructure in a developing-country megaregion — evidence from West Java, Indonesia*

**Target journal (primary):** *Energy Research & Social Science* (Elsevier, Q1)
**Alternatives:** *Energy Policy* (Q1) · *Journal of Transport Geography* (Q1)

> Draft note: numbers below are drawn from the project datasets (PLN UID West Java Master SPKLU & transaction detail, March 2026; ABSA public-review corpus; BPS socio-economic indicators). Verify every figure against the source tables before submission. Citations marked `[VERIFY]` are placeholders for real references you must insert.

---

## Structured abstract (≈250 words)

**Context.** Indonesia is scaling public EV charging (SPKLU) rapidly under its 2030 electric-mobility targets, but whether this build-out is *equitable* — and whether users *perceive* it as reliable and accessible — remains unmeasured at sub-national scale.

**Objective.** We evaluate the distributive equity and public perception of the public SPKLU network in West Java, Indonesia's most populous province, and test whether equity and perceived service quality are linked.

**Data & methods.** We integrate (i) the official Master SPKLU registry (636 charging units across 348 sites in 26 cities/regencies), (ii) 101,020 real charging transactions (≈2.26 GWh, March 2026), (iii) a corpus of 894 user-reviewed locations (584 quantitatively scored on a Service Quality Index, SQI), and (iv) BPS population, HDI and income-tier indicators. We compute Gini coefficients and Lorenz curves for unit and consumption distribution, normalise them by population and income, construct an Equity Priority Index (EPI = underserved × low-income), and contrast urban (cities) versus rural (regencies) provision. We then model the drivers of perceived service quality from review aspect-sentiment.

**Results.** Provision is moderately-to-highly unequal: the unit-vs-population Gini is ≈0.19 while the consumption-vs-population Gini reaches ≈0.45, indicating demand (and effective access) concentrates far more than the hardware itself. Cities dominate both coverage and intensity; several low-income regencies are simultaneously under-served and high-need (high EPI). Public perception is driven primarily by **reliability and availability**, not by amenities — and the lowest-SQI locations cluster in the same under-served peripheries, suggesting equity and experienced quality reinforce one another.

**Implications.** A coverage-first roll-out can mask a *reliability* and *distributive* gap. We translate the findings into a transferable, equity-weighted prioritisation framework for just EV-charging deployment in emerging economies.

**Keywords:** EV charging; energy justice; spatial equity; public perception; Gini/Lorenz; Indonesia; just transition

---

## 1. Introduction
- The global EV transition and the role of *public* fast charging in countries with low private-charging access (apartments, kampung housing) — charging equity matters more where home charging is rare. `[VERIFY]`
- Gap 1: most charging-equity work is on high-income contexts (US/EU/China); Southeast Asia and developing megaregions are under-studied. `[VERIFY]`
- Gap 2: equity studies rarely link *distributive* metrics to *perceived/experienced* service quality from real users.
- Setting: West Java (≈50M people, Indonesia's largest province), PLN's RACE-for-2030 electrification push.
- **Contribution:** (1) first integrated distributive-equity + perception assessment of SPKLU at provincial scale on real operational data; (2) an Equity Priority Index combining under-service and socio-economic need; (3) evidence that distributive and experiential gaps coincide.
- **Research questions:**
  - **RQ1 (Distributive equity):** How unequally are charging units and consumption distributed across West Java, and does normalising by population/income change the picture?
  - **RQ2 (Urban–rural):** How large is the urban (city) vs rural (regency) disparity in coverage and usage intensity?
  - **RQ3 (Perception):** Which service aspects most determine perceived charging quality (SQI)?
  - **RQ4 (Linkage):** Do under-served, low-income areas also experience lower perceived quality — i.e., does inequity compound?

## 2. Literature & framing
- **Energy-justice triad** (distributive, procedural, recognition) as the organising lens. `[VERIFY: Sovacool & Dworkin; Jenkins et al.]`
- Charging-equity / accessibility literature and methods (Gini/Lorenz, 2SFCA, EPI-type indices). `[VERIFY: Hsu & Fingerman; Khan et al.; Carlton & Sultana]`
- Perception / service-quality of charging (reliability, uptime, availability). `[VERIFY]`
- Position the paper: distributive + experiential, developing-country, operational data.

## 3. Study area, data & methods
### 3.1 Study area
West Java: 26 cities/regencies; urban cores (e.g., Bekasi, Bogor, Depok, Bandung) vs rural regencies; demographic & income heterogeneity (Klassen typology 2023).
### 3.2 Data
| Source | Content | Scope |
|---|---|---|
| Master SPKLU (PLN) | 636 units · 348 sites · coordinates · operator (PLN/partner) | 26 kota/kab |
| Transaction detail | 101,020 sessions · 2.26 GWh · kWh, duration, tariff, AC/DC | March 2026 (330 active stations) |
| ABSA review corpus | aspect-level sentiment; SQI | 894 locations (584 scored) |
| BPS / Klassen | population (SP2022), HDI, poverty, income tier | per kota/kab |

### 3.3 Methods
- **Distributive equity:** Lorenz curves & Gini for (a) units vs population, (b) consumption (kWh) vs population; interpret the gap between them.
- **Normalisation:** units-per-100k, kWh-per-capita, EV-per-100k.
- **Equity Priority Index:** EPI = standardised(under-service) × standardised(low-income), to flag high-need under-served areas.
- **Urban–rural:** city vs regency contrasts on coverage and kWh/unit (utilisation/pressure proxy).
- **Perception model:** dependent var = SQI; predictors = aspect sentiments (reliability, availability, facilities, location, price…); feature-importance / regression on 584 scored locations.
- **Linkage (RQ4):** spatial correlation between EPI / under-service and mean SQI.
- Robustness: sensitivity of Gini to active-vs-all stations; note Gini is an equity *proxy* pending fuller socio-spatial controls.

## 4. Results
- **R1 — Distribution (RQ1):** unit-vs-pop Gini ≈ **0.19**; consumption-vs-pop Gini ≈ **0.45**. Lorenz curves show hardware is moderately concentrated but *use* is far more concentrated → effective access gap. *(Fig. 1 Lorenz; Table 1 per-kota.)*
- **R2 — Urban–rural (RQ2):** cities hold the bulk of units and far higher kWh/unit; regencies show coverage thin-ness and, where present, high utilisation pressure. *(Fig. 2.)*
- **R3 — Equity Priority (RQ1/RQ2):** identify the high-EPI under-served, low-income regencies (name them from the EPI table). *(Fig. 3 EPI map.)*
- **R4 — Perception drivers (RQ3):** **reliability** and **availability** dominate SQI; facilities/price secondary. *(Fig. 4 driver importance; mean SQI ≈ [insert mean_jabar].)*
- **R5 — Compounding (RQ4):** under-served / high-EPI areas also show lower mean SQI → distributive and experiential disadvantage coincide. *(Fig. 5 EPI vs SQI scatter.)*

## 5. Discussion
- Coverage-first metrics flatter the network; a *reliability-and-distribution* lens reveals the real gap (link to the national finding that ~a third of stations sit "offline" — see Paper 2).
- Energy-justice reading: distributive shortfall + recognition gap (peripheral, lower-income communities) + procedural (deployment logic favours demand-dense cities).
- Policy: equity-weighted siting, uptime/SLA mandates, targeted support for high-EPI regencies; pairing new builds with reliability guarantees.
- Generalisability to other emerging megaregions (low home-charging access → public-charging equity is decisive).

## 6. Limitations
- Single-month transaction window; Gini as equity proxy; perception from a review corpus (self-selection); SQI construct validity; no individual-level access modelling (future: isochrone/2SFCA accessibility).

## 7. Conclusion
Distributive and experienced inequities in West Java's SPKLU network are real and mutually reinforcing; an equity-weighted, reliability-aware deployment framework is needed for a *just* EV transition in developing economies.

---

### Figures/Tables plan
1. Lorenz curves (units & kWh vs population) + Gini. 2. Urban–rural coverage & kWh/unit. 3. EPI choropleth. 4. SQI driver importance. 5. EPI vs SQI scatter. T1: per-kota integrated table. T2: perception aspect summary.

### Data & ethics
Data-availability statement; PLN data-use permission; review-corpus collection ethics & ToS compliance; de-identification.

### Suggested literature to position against (VERIFY exact citations)
Energy-justice frameworks; EV charging accessibility/equity (US/EU/China); 2SFCA & Gini in infrastructure equity; charging reliability/uptime studies; Indonesia EV-policy papers.
