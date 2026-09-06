# PROPOSAL — DRAFT

**Working title:** *DiPCOM-ID — Digital and data-driven planning and management of parking and modular charging for shared light-electric mobility in Indonesia: a twinning proposal*

**Instrument:** Collaborative research & innovation project · 36 months
**Coordinating author:** Qashtalani Haramaini — Monash University Indonesia / PT PLN (Persero) UID Jawa Barat
**Twinned with:** DiPCOM (*Digital and data-driven planning and management for parking and modular charging of shared micromobility*), Drive Sweden — Chalmers University of Technology, Standab, Göteborgs Stad, Stockholms stad, WSP, EIT Urban Mobility. Results presented at Drive Sweden Forum, 15 September 2026. `[VERIFY: project number, call, budget, end date, and publication list]`

> Draft note: this is a **proposal**, not a results paper. No partner named below has been
> approached or has committed; every consortium role is a *proposed* role to be secured.
> Figures describing assets already held by the coordinating team are real and traceable to
> `papers/capacity/capacity.json` and `papers/p2p/p2p.json`. Everything about funding calls,
> budgets, and regulatory clauses carries `[VERIFY]` and must be checked before submission.

---

## Ringkasan eksekutif (Bahasa Indonesia)

**Masalah.** Perencanaan parkir dan pengisian daya untuk kendaraan listrik ringan berbagi
(*shared light-electric mobility*) di Indonesia dikerjakan hampir tanpa data. Kota tidak tahu di
mana armada beristirahat, operator tidak tahu di mana kapasitas jaringan tersedia, dan PLN tidak
melihat beban itu sampai ia muncul di trafo. Proyek DiPCOM di Swedia menunjukkan bahwa persoalan
ini dapat diselesaikan dengan analisis data besar, optimasi, dan alat digital — tetapi metodenya
dibangun untuk satu rezim perilaku: skuter sewa bebas-parkir.

**Yang berbeda di Indonesia.** Di sini ada **dua rezim yang berlawanan sifatnya**, dan keduanya
harus ditangani sekaligus:

* **Rezim A — sewa bebas-parkir** (skuter & sepeda listrik). Secara hukum dikurung oleh Permenhub
  45/2020 pada lajur khusus dan kawasan tertentu, sehingga di Indonesia ia hidup sebagai
  *mikromobilitas enklave*: kampus, superblok, kawasan TOD, kawasan wisata. Energinya kecil,
  sebaran tempat berhentinya sangat acak, dan **letak modul menentukan di mana kendaraan berakhir**.
* **Rezim B — armada motor listrik** (ojol, kurir, sewa langganan). Segmen berbagi terbesar dan
  paling nyata. Kendaraan bermalam di rumah pengemudi, bukan di trotoar. Energinya besar, tetapi
  **letak istirahatnya sudah ditentukan oleh tempat tinggal pengemudi yang tidak dikendalikan
  perencana** — dan tidak tercatat di register mana pun.

**Inti ilmiahnya.** Tujuan optimasi yang sama menghasilkan logika penempatan yang berlawanan:
Rezim A adalah persoalan *facility location dengan permintaan terinduksi*; Rezim B adalah persoalan
*penutupan wilayah atas medan permintaan laten*. Kontribusi proposal ini bukan memindahkan DiPCOM,
melainkan **menggeneralisasikannya menjadi formulasi dua-rezim** dan menguji apakah satu instrumen
perencanaan dapat melayani keduanya.

**Modal yang sudah ada.** Tim koordinator sudah memegang lapisan jaringan yang biasanya paling sulit
diperoleh: 41.129 catatan pembebanan trafo distribusi Jawa Barat yang layak pakai (dari 53.797),
182 trafo Gardu Induk / 9.790 MVA, 100.782 sesi pengisian bermeter, 3.694 sambungan home charging
tergeokode ke 695 kelurahan, ditambah metode headroom, fungsi transfer energi→puncak, pemisahan
permintaan laten, dan arsitektur tarif di bawah larangan jual-beli listrik — semuanya sudah
diterbitkan atau berstatus draft di perpustakaan riset ini. **Yang hilang hanya lapisan permintaan
mikromobilitasnya.**

**Yang diminta.** Proyek 36 bulan, delapan paket kerja, dua pilot kota, satu per rezim. Keluaran
utamanya adalah peta kapasitas terbuka, dua model penempatan, satu kerangka tarif yang sah tanpa
izin penjualan tenaga listrik, dan rekomendasi kebijakan untuk Kemenhub, Kemen ESDM, pemerintah
kota, dan PLN.

**Timbal balik ke Swedia.** Ini bukan permintaan bantuan. Formulasi rezim armada dan arsitektur
tarif tanpa jual-beli energi adalah dua hal yang **tidak dimiliki DiPCOM** dan akan dibutuhkan kota
Eropa begitu moped listrik terkelola menggantikan skuter bebas-parkir.

---

## 1. The challenge

Shared light-electric mobility is the cheapest decarbonisation lever available to Indonesian cities
and the one with the least planning evidence behind it. Two-wheelers dominate Indonesian mobility;
their electrification is a national programme; and the vehicles that matter most are *shared* —
ride-hailing and delivery fleets whose riders do not own them, and rental fleets whose users do not
keep them. Yet almost nothing is known, at planning resolution, about **where those vehicles rest
and what happens to the grid when they charge.**

Three actors each hold one third of the picture and none can see the other two:

| Actor | What they can see | What they cannot see |
|---|---|---|
| City government | kerb space, land use, permits | where fleets actually rest; how much energy they draw |
| Fleet / rental operator | trips, battery state, rebalancing cost | where the grid has capacity; where the city will allow furniture |
| Electricity utility | transformer loading, connections, headroom | that a fleet is about to appear on a feeder |

DiPCOM addressed exactly this fracture for Swedish cities, using big-data analysis, optimisation and
digital tools to plan parking and modular charging for shared micromobility, with a consortium
spanning a university, a charging-as-a-service company, two cities, an engineering consultancy and a
European innovation community. This proposal asks what it takes to do the same where the vehicle
mix, the behaviour, the law and the grid are all different — and argues that answering that question
produces a *more general* method, not a localised copy.

---

## 2. What DiPCOM established, and what does not transfer

| DiPCOM element | Transfers to Indonesia? | Why |
|---|---|---|
| Big-data trip traces as the demand layer | **Method yes, data no** | No Indonesian operator publishes trip data; acquisition is a work package, not an assumption |
| Modular charging as parking furniture | **Yes, for Regime A** | Directly applicable in enclave settings (campuses, superblocks, TOD, tourism zones) |
| Modular charging as the charging answer | **No, for Regime B** | Fleet e-motorcycles charge by battery swap or at the rider's home, not at kerbside racks |
| Optimisation of module siting | **Reformulated** | Two regimes need two formulations — §3 |
| City as the deploying authority | **Partly** | Kerb space is municipal, but the electron is national and licensed — §5 |
| Charging-as-a-service business model | **Blocked in one form** | Selling kWh requires a licence; the fee must be re-based — §5.2 |
| Sidewalk clutter as the motivating problem | **Weak** | Free-floating scooters are legally confined here, so clutter is an enclave problem, not a city-wide one |

The honest summary: **DiPCOM's method transfers, DiPCOM's problem does not.** The Swedish
motivating problem is disorderly free-floating supply on public kerbs. The Indonesian motivating
problem is an invisible fleet charging load landing on residential low-voltage networks, plus a
small enclave micromobility sector that looks like Sweden's but is a fraction of the energy.

---

## 3. The scientific core: one objective, two opposite siting logics

Both regimes can be written as the same programme — minimise the sum of user access cost,
infrastructure cost and network cost, subject to a service-level constraint. The difference is what
the decision variable does to demand.

### 3.1 Regime A — free-floating rental (induced demand)

The planner places modules; users then choose where to end trips, and that choice **responds to
where the modules are**. Rest locations are endogenous. This is facility location with induced
demand: siting shapes the very distribution it is optimised against, so the problem is a fixed point,
not a one-shot allocation. It is also the regime where the *parking* objective (order, accessibility,
pedestrian space) can bind harder than the *charging* objective.

### 3.2 Regime B — fleet e-motorcycle (latent, exogenous demand)

The vehicle sleeps where the rider sleeps. Rest locations are exogenous to the planner and, worse,
**unobserved**: there is no register of ride-hailing riders' home addresses, and there should not be.
This is a covering problem over a demand field that must first be *estimated* rather than measured —
the same identification problem the coordinating team has already formalised for public car charging
(latent demand separated from the supply filter that records it).

### 3.3 Why the contrast is the contribution

| | Regime A — free-floating | Regime B — fleet 2W |
|---|---|---|
| Who chooses the rest location | thousands of users, uncoordinated | rider's home; operator's pool |
| Rest location w.r.t. the planner | **endogenous** (siting shapes it) | **exogenous and latent** (siting cannot move it) |
| Problem class | facility location with induced demand | covering under an estimated demand field |
| Energy per vehicle per day | ≈ 0.3–0.8 kWh `[VERIFY]` | ≈ 3–6 kWh `[VERIFY]` |
| Charging mode | modular rack, in place | battery swap, or home charging |
| Grid node touched | kerbside LV, daytime | residential LV, overnight |
| Legal box of the transaction | operator charges its own asset | swap = licensed service; home = §5.2 problem |
| Failure mode if mis-sited | clutter, low utilisation | rider detour, transformer overload |

A single planning instrument that serves both must therefore carry two solvers behind one interface.
Whether that is achievable — and whether the two solutions *conflict* where the regimes overlap
spatially — is the project's central research question.

---

## 4. Research questions

**RQ1 — Demand.** Where do shared light-electric vehicles actually rest, by regime, at planning
resolution, and how much of that distribution can be recovered when the recording instrument is
itself a function of existing supply?

**RQ2 — Siting.** Does one optimisation formulation serve both regimes, or does induced versus
latent demand force two solvers? Where the regimes overlap spatially, do their optimal sitings
conflict, and how should a planner arbitrate?

**RQ3 — Network.** What does each regime do to distribution-transformer loading at the hours that
matter, and how much of the deployment can be absorbed by existing headroom before reinforcement is
triggered?

**RQ4 — Institution.** Which fee and permit architectures make modular charging and shared parking
lawful and financially viable under Indonesian electricity licensing and kerbside regulation — and
who captures the surplus each architecture creates?

**RQ5 — Equity.** Does data-driven siting of micromobility infrastructure narrow or widen access
gaps, measured on the population rather than on the users the system already records?

---

## 5. The institutional layer Sweden did not need

This is where an Indonesian twin must build something DiPCOM never had to, and it is a genuine
research contribution rather than compliance work.

### 5.1 The same hardware sits in three legal boxes

A "modular charging station" is not one regulated object. What it is depends on **who owns the
vehicle and who owns the electron**:

| Configuration | Who buys the electricity | Regulatory box | Binding constraint |
|---|---|---|---|
| Operator charges its own rental fleet at its own module | the operator, as an end customer | ordinary connection | kerb permit, not electricity law |
| Module open to the public, priced per kWh | third parties | public charging (SPKLU/SPBKLU) regime | licence, tariff formula `[VERIFY: Permen ESDM 1/2023]` |
| Battery swap for fleet riders | swap operator, reselling as a service | SPBKLU regime | licence; battery standardisation |
| Rider charges at home | the rider's household | residential tariff | no sale may occur if a third party pays |

### 5.2 The no-resale constraint, already solved for cars

Supplying electricity to the public in Indonesia is a licensed activity, and unlicensed sale of
surplus power is prohibited. `[VERIFY: UU 30/2009 Art. 49(3) as amended by UU 6/2023]` The
coordinating team has already derived and quantified a fee architecture that works under that
constraint for private car charging — the transaction is re-based from energy (Rp/kWh) onto **time
and space** (a bay rental plus a flat service fee), so no kilowatt-hours change hands. The result
generalises directly to shared micromobility, and one of its properties matters more here than it
did for cars: because host revenue accrues per hour rather than per kWh, the private incentive is
**occupancy rather than throughput**, which points deployment at the load-curve trough instead of
its peak.

WP4 tests whether the same architecture survives three transpositions: a rental operator's own
module (where no third-party sale occurs at all), a shared kerbside module, and a rider charging a
fleet-owned battery at a household meter.

### 5.3 Kerb space

Regime A modules occupy road space (*ruang milik jalan*) and touch municipal parking retribution
regimes that differ by city. `[VERIFY: the relevant Perda for each pilot city]` A national method
that ignores this will not deploy. WP4 therefore produces a model permit and retribution clause
alongside the technical guidance.

### 5.4 Why Regime A is enclave micromobility here

E-scooters, e-bikes, hoverboards, unicycles and otopeds are regulated as *kendaraan tertentu*, with
a 25 km/h limit, helmet and minimum-age requirements, and — decisively for siting — operation
confined to **dedicated lanes and designated areas**. `[VERIFY: Permenhub 45/2020, and any amending
instrument]` The consequence is structural rather than incidental: Indonesian free-floating
micromobility is not a city-wide network but a set of enclaves. Optimisation over an enclave with a
hard boundary is a different problem from optimisation over an open city, and the proposal treats it
as such rather than importing an open-city formulation and discovering the boundary later.

---

## 6. What the consortium already holds

The proposal's competitive advantage is that the hardest and least shareable layer — the electricity
network — is already assembled, cleaned and published as a reproducible pipeline by the coordinating
team.

| Asset | Scale | Where it comes from |
|---|---|---|
| Distribution-transformer load register, West Java | **41,129 usable** of 53,797 surveyed records | `papers/capacity/prepare.py` |
| Grid-substation transformers | 182 units / 9,790 MVA | same |
| Public charging sessions, metered | **100,782 sessions**, 329 stations, March 2026 | `papers/p2p/prepare.py` |
| Home-charging connections, geocoded | **3,694 applications** (2,181 completed) across 231 districts / 695 villages | same |
| Two-tier headroom method at the 80 % planning limit | 1,295 cells of ≈5 km | Manuscript 4 (CIRED 2027) |
| Energy → peak-load transfer function | *P* = 0.133·*E*<sup>0.695</sup>, 15-min reconstruction | Manuscript 5 (CIRED 2027, DNDP) |
| Latent-demand / capture separation | BYM2 hierarchical model, 14 service areas | Manuscript 9 (BAM 2026 poster) |
| Fee architecture under the no-resale constraint | feasible band, break-even dwell, four-sided model | Manuscript 13 |
| Equity machinery | Gini / Lorenz / concentration indices against population | Manuscripts 1 and 12 |

**What is missing is exactly one layer: shared micromobility demand.** No Indonesian operator
publishes trip or battery telemetry, and no public register records where fleet two-wheelers rest.
Acquiring that layer is WP1 and is the project's principal risk (§10).

---

## 7. Work packages

**WP0 — Coordination, data governance and ethics** *(months 1–36)*
Consortium management; a data-sharing agreement per operator; a privacy protocol under the personal
data protection law `[VERIFY: UU 27/2022 and its implementing regulation]`. Rider home locations are
never held at individual resolution: telemetry is aggregated to a spatial unit before it leaves the
operator's environment, and the aggregation rule is a project deliverable, not an afterthought.

**WP1 — Data foundation** *(1–12)*
Negotiate and ingest operator telemetry for both regimes; build the rest-location and energy layers;
join to the existing grid layer; publish the schema and, where agreements permit, an open aggregated
extract. **Deliverables:** D1.1 data-sharing framework; D1.2 demand layer v1; D1.3 open schema.

**WP2 — Two-regime demand modelling** *(7–24)*
Regime A: rest-location choice conditional on module placement — the induced-demand fixed point.
Regime B: latent rest-density estimation with capture correction, extending the team's existing
hierarchical formulation from stations to fleets. **Deliverables:** D2.1 Regime A choice model;
D2.2 Regime B latent-demand model with credible intervals; D2.3 validation protocol.

**WP3 — Grid-aware siting optimisation** *(13–30)*
Two solvers behind one objective; headroom as a hard constraint priced in kWh/month rather than
as a binary; explicit treatment of the overlap zones where the two regimes' optima disagree.
**Deliverables:** D3.1 Regime A solver; D3.2 Regime B solver; D3.3 arbitration rules for overlap;
D3.4 benchmark against as-built deployments.

**WP4 — Legal, tariff and permit architecture** *(7–30)*
The three-box problem (§5.1); transposition of the time-and-space fee architecture to shared
micromobility; a model kerb permit and retribution clause. **Deliverables:** D4.1 legal mapping;
D4.2 fee architectures with quantified four-sided outcomes; D4.3 model permit text.

**WP5 — Digital tools** *(19–34)*
A planner-facing capacity-and-siting map (extending the team's published dashboard) and an
operator-facing scheduling view. Open payloads so numbers can be audited rather than believed.
**Deliverables:** D5.1 planner tool; D5.2 operator tool; D5.3 open payload spec.

**WP6 — City pilots** *(19–36)*
Two pilots, one per regime, in two cities with contrasting network conditions — one dense city core
and one peri-urban regency. Instrument, deploy, measure against the counterfactual siting.
**Deliverables:** D6.1 pilot protocol; D6.2 pilot results; D6.3 transfer guide.

**WP7 — Equity and impact assessment** *(25–36)*
Access measured on the population, not on recorded users; concentration indices with uncertainty
carried through; explicit test of whether optimisation concentrates or disperses provision. The
prior for this is not optimistic: in the team's car-charging work, private charging assets were found
to be *more* spatially concentrated than the public network they were supposed to supplement.
**Deliverables:** D7.1 equity protocol; D7.2 assessment; D7.3 targeting recommendations.

**WP8 — Dissemination, policy transfer and twinning** *(1–36)*
Joint publications and a two-way exchange with the DiPCOM team; policy briefs for the transport and
energy ministries, the pilot cities, and the utility. **Deliverables:** D8.1 policy briefs;
D8.2 joint papers; D8.3 twinning workshops.

---

## 8. Proposed consortium

**No organisation listed here has been approached. These are proposed roles to be secured.**

| Proposed role | Candidate type | Why needed |
|---|---|---|
| Coordinator, demand & equity modelling | Monash University Indonesia | Holds the existing grid + charging data assets and the published methods |
| Method partner, twinning | Chalmers University of Technology | DiPCOM's method holder; the reciprocity in §11 runs through here |
| Network data & pilot host | PT PLN (Persero) UID Jawa Barat | Transformer, feeder and charging data; the reinforcement decisions the project informs |
| Pilot city A (dense core) | a West Java city government | Kerb space, permits, parking retribution |
| Pilot city B (peri-urban) | a West Java regency government | Contrasting network and land-use conditions |
| Fleet operator | a shared e-motorcycle / delivery fleet | Regime B telemetry and a real deployment decision |
| Rental operator | an enclave micromobility operator | Regime A telemetry within a bounded area |
| Charging-as-a-service | a modular charging supplier | Hardware, and the business-model reality check |
| Engineering consultancy | a national infrastructure consultancy | Deployment engineering and transfer to practice |
| Local urban planning | an Indonesian university partner | Land-use, kerb and TOD expertise |

**Candidate funding routes** — all `[VERIFY]` for current call status, eligibility and deadlines:
national research and matching-fund schemes; the coordinating author's doctoral programme;
Australia–Indonesia bilateral research partnerships; European urban-mobility innovation partnerships
of the kind that co-funded DiPCOM.

---

## 9. Timeline and indicative budget

| Year | Focus | Gate |
|---|---|---|
| 1 (m1–12) | Data agreements, demand layer v1, legal mapping | **G1:** at least one operator agreement per regime signed, or Plan B triggered (§10) |
| 2 (m13–24) | Both demand models, both solvers, tool alpha | **G2:** solvers beat as-built siting on the retrospective benchmark |
| 3 (m25–36) | Pilots, equity assessment, policy transfer | **G3:** pilot results published with open payloads |

Indicative budget shape only — **not costed**, and to be built bottom-up with partners before
submission: the majority to personnel across the university partners, a substantial minority to pilot
hardware and installation, and the remainder to data acquisition, travel for the twinning exchange,
and open dissemination. `[VERIFY: all figures, cost categories and funder eligibility rules]`

---

## 10. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| **No operator shares telemetry** — the project's single point of failure | **High** | Sign at least one agreement per regime before submission, not after award; Plan B in the next row |
| Plan B if telemetry is refused | — | Substitute a demand layer built from land use, POI density, population and the team's existing charging records, and reframe WP2 as estimation under heavier uncertainty — weaker, but the project survives |
| Regime A market too small to study | Medium | Enclave sampling (campus, superblock, TOD, tourism zone) makes a small sector tractable rather than fatal |
| Regulatory change mid-project | Medium | WP4 tracks instruments continuously; the fee architecture is designed against the *structure* of the licensing rule, not a specific clause |
| Privacy harm from rider location data | **High** | Aggregate before export; never hold individual home locations; ethics approval and a published aggregation rule as a WP0 deliverable |
| Pilot city changes administration | Medium | Two cities, and a transfer guide written so a third city can adopt without the team |
| Optimisation concentrates provision in already-served areas | Medium | WP7 is a gate, not a report: equity outcomes are assessed against population and can veto a siting rule |

---

## 11. What Indonesia gives back

A twinning proposal that only receives is a weak proposal. Two things in this project do not exist in
DiPCOM and will be needed in Europe:

1. **The fleet regime formulation.** European shared micromobility is drifting from free-floating
   scooters toward operator-managed e-mopeds and delivery fleets. When it does, the induced-demand
   formulation stops being the right one and the latent, exogenous rest-location problem — Regime B —
   becomes the live question. Indonesia has that regime at scale today.
2. **Charging economics under a resale prohibition.** The time-and-space fee architecture was forced
   on Indonesia by electricity licensing, but its property — revenue per hour rather than per kWh,
   hence occupancy rather than throughput, hence trough rather than peak — is something European
   network operators want and currently buy with tariff incentives. A market that reaches it
   structurally is worth studying.

Third, and less glamorous: a method that survives Indonesian data conditions — sparse, unregistered,
partly unobservable — will survive most places. Robustness earned here transfers upward more easily
than robustness earned in Gothenburg transfers down.

---

## 12. Expected outcomes

**For cities.** A siting instrument that answers "where do we put these, and how many" with a number
and an uncertainty, plus a model permit and retribution clause so the answer is deployable.

**For operators.** Placement and charging schedules that cut rebalancing cost and avoid connections
that cannot be served, before capital is committed.

**For the utility.** Advance sight of a load it currently discovers after the fact, expressed in the
planning unit that matters — kW at a named transformer, at the hour that binds.

**For the ministries.** Evidence for whether the enclave confinement of light electric vehicles is
the right long-run settlement, and a tested fee architecture that does not require every host to
become a licensed electricity seller.

**For the field.** A two-regime generalisation of data-driven micromobility infrastructure planning,
and an equity assessment honest enough to report the uncomfortable result if the optimisation
concentrates provision.

---

## 13. Open questions to resolve before submission

1. Which two pilot cities, and is there a signed expression of interest from each?
2. Which operators, and what exactly will they share — trip traces, battery state, or only aggregates?
3. Is the DiPCOM team interested in a twinning arrangement at all, and on what terms?
4. Which funding call, and does it permit a non-EU coordinator with European partners?
5. Does the project stand up if Regime A is dropped entirely and it becomes a fleet-only proposal —
   and if so, is the two-regime framing worth the added scope?
6. Confirm every regulatory reference in §5 against the primary texts, including any instrument
   issued after the drafting date.

---

## Data availability

Grid, charging and home-connection layers described in §6 are used under a data agreement with the
utility, aggregated and pseudonymised. Their analysis pipelines are published in this repository
(`papers/capacity/prepare.py`, `papers/p2p/prepare.py`). No shared micromobility data is held by the
team at the time of writing; acquiring it is WP1.
