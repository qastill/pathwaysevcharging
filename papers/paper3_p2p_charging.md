# PAPER 3 — DRAFT

**Working title:** *Charging without selling electricity: a parking-and-service fee architecture for peer-to-peer EV charging under a single-buyer electricity regime — evidence from West Java, Indonesia*

**Target journal (primary):** *Energy Policy* (Elsevier, Q1)
**Alternatives:** *Energy Research & Social Science* (Q1) · *Utilities Policy* (Q2) · *Transport Policy* (Q1)

> Draft note: every figure in this manuscript is produced by `papers/p2p/prepare.py` from the raw
> project datasets (PLN UID West Java transaction detail and home-charging application register,
> March–June 2026). Re-run that script and the numbers here can be reproduced line by line.
> Citations and legal-clause references marked `[VERIFY]` are placeholders that must be checked
> against the primary texts before submission.

---

## Structured abstract (≈300 words)

**Context.** Peer-to-peer (P2P) charging — a household renting out its private wallbox to another
driver — is the cheapest way to add EV charging capacity, because the asset is already built. In
most markets the transaction is straightforward: the host sells kilowatt-hours. In Indonesia it is
not. Supplying electricity to the public is a licensed activity; an individual customer reselling
kWh has no licence to do it. The literature on P2P charging assumes away exactly the constraint
that binds in the largest EV market of Southeast Asia.

**Objective.** We ask whether a P2P charging market can be built *without* the sale of energy, and
what such a market does to prices, host income, platform economics, utility revenue, network peak
load, and spatial equity.

**Data & methods.** We use 100,782 metered public-charging sessions (2.26 GWh, Rp 5.89 bn, March
2026) across 329 public stations in West Java, and the register of 3,694 PLN home-charging
connection applications (2,181 completed) to June 2026, geocoded to 695 villages. We derive a
fee architecture in which the driver pays a **parking rate** (Rp/hour) plus a flat **service fee**
(Rp/session) and no kWh changes hands; the energy remains a residential sale from the utility to
the host. We solve the architecture analytically for its feasible price band, break-even dwell
time and surplus split, then quantify a four-sided financial model (host, driver, platform,
utility), the load-shift effect, and Gini/Lorenz equity outcomes.

**Results.** (i) The entire business lives inside a band of **Rp 8,328–16,981 per hour** at 7 kW,
whose two edges are set by tariffs the host does not control. (ii) A time-based fee is *floored*
in Rp/kWh terms and therefore only beats public charging above a **break-even dwell of 1.44 hours
(9.3 kWh)** — the architecture is structurally an overnight product and structurally unsuited to
top-ups. (iii) Because host revenue accrues per hour rather than per kWh, the host's incentive is
to maximise **occupancy, not throughput** — the legal constraint accidentally aligns private
incentive with system benefit. (iv) 2,181 already-installed home chargers hold **2.96 GWh/month of
idle overnight capacity, 1.31× the entire public network's output**, equivalent to 431 public fast-
charging sites and about Rp 518 bn of avoided capital. (v) 64.8 % of recorded public sessions
(56.8 % of energy) are technically substitutable. (vi) The utility gains: at 20 % substitution,
avoided capital and O&M of Rp 8.08 bn/year exceed revenue dilution of Rp 3.66 bn/year. (vii) But
hosts are **more spatially concentrated than the public network they would supplement** (Gini 0.599
vs 0.264 against population; ρ = 0.73 with existing demand). P2P is an efficiency instrument, not
an equity instrument.

**Implications.** We derive a five-step regulatory ladder that makes the architecture lawful and
then makes it fair, centred on a dedicated host-meter tariff class and a mandatory disclosure of
effective Rp/kWh at booking.

**Keywords:** peer-to-peer charging; EV charging; electricity market regulation; two-part tariff;
platform design; energy justice; Indonesia

---

## 1. Introduction

The cheapest charge point is the one already installed. By June 2026 the utility's West Java
distribution region had processed 3,694 applications for dedicated home-charging connections and
completed 2,181 of them, spread across 231 sub-districts and 695 villages. Each is a 7,700 VA
single-phase service feeding a ~7 kW wallbox that, as Section 5.2 shows, sits unused about 87 % of
the nights it could be working. In the same province the public network — 329 stations that
recorded a transaction in March 2026 — sold 2.26 GWh at an all-in Rp 2,608/kWh.

The arithmetic invites an obvious question. If idle household chargers could be rented to drivers
who have none, the province would add charging capacity at nearly zero marginal capital cost,
using assets that have already been paid for and connections that have already been engineered.
This is the peer-to-peer (P2P) proposition, and internationally it is not exotic: platforms in the
UK, the Netherlands and the United States operate host-listed home chargers as a straightforward
marketplace. `[VERIFY: Co Charger; Joosup; EVmatch; Plugshare Home]`

What makes Indonesia different is that the obvious form of the transaction is closed. Supplying
electricity to the public is a licensed activity under Law 30/2009 on Electricity; selling surplus
electricity for public use without government approval carries criminal liability (Art. 49(3):
up to two years and Rp 2 bn, narrowed by the Job Creation Law to cases producing harm).
`[VERIFY: exact clause numbering after UU 6/2023]` Public charging stations (SPKLU) are classified
under business code KBLI 35114 — *sale of electric power* — a high-risk activity requiring a
business identification number and an electricity supply business licence, with the price to the
vehicle owner set from the special-service tariff class at a multiplier of at most 1.5.
`[VERIFY: Permen ESDM 1/2023, Arts. 10, 15 and the tariff annex]` A household with a residential
connection holds none of this. It cannot lawfully resell the kilowatt-hours it buys.

Almost the entire P2P charging literature is written for jurisdictions where that constraint does
not exist, and therefore treats the design problem as one of matching, pricing and trust.
`[VERIFY: P2P charging platform literature]` The Indonesian case forces a prior question: **can the
market be built at all if the thing being traded cannot be the energy?**

This paper answers yes, and shows that the answer is not merely a workaround. Re-basing the
transaction from energy to *time and space* — a parking rate plus a service fee, with the kWh
remaining a residential sale from the utility to the host — changes the economics in ways that are
mostly, and surprisingly, favourable to the electricity system. We set out the architecture,
solve it, quantify it against a full month of metered demand and a complete host register, and
derive the policy sequence that would make it lawful and then make it fair.

**Contributions.**

1. A formal fee architecture for P2P charging under a licensing regime that forbids energy resale,
   with closed-form expressions for its feasible price band and break-even dwell time.
2. The proposition — derived, then quantified — that **the fee base determines the load shape**:
   per-kWh pricing rewards throughput and therefore peak-hour turnover; per-hour pricing rewards
   occupancy and therefore overnight charging.
3. A four-sided financial model (host, driver, platform, utility) estimated on real transactions
   rather than survey intentions, including the revenue dilution the utility must absorb.
4. The first measurement, to our knowledge, of the *idle* overnight capacity already installed in a
   developing-country home-charging fleet, benchmarked against the public network it could relieve.
5. An equity result that cuts against the usual advocacy: P2P supply is more spatially concentrated
   than the public network, and will widen access gaps unless deliberately steered.

---

## 2. The constraint, taken seriously

### 2.1 What is actually forbidden

Three legal facts define the design space. `[VERIFY: all three against primary texts]`

| Fact | Instrument | Consequence for P2P |
|---|---|---|
| Supplying electricity to the public is a licensed activity; unlicensed sale of surplus power is prohibited and criminally sanctioned | UU 30/2009 Art. 49(3), as amended by UU 6/2023 | A household cannot price its wallbox in Rp/kWh |
| Public charging (SPKLU) is business code KBLI 35114 *sale of electric power*, high risk, requiring NIB + electricity supply licence | Permen ESDM 1/2023 Arts. 10 & 15; PP 5/2021 Art. 15(1) | Becoming a licensed operator is not proportionate for a single 7 kW socket |
| The SPKLU price to the vehicle owner derives from the special-service tariff class with multiplier N ≤ 1.5 | Permen ESDM 1/2023 tariff provisions | The public price is administratively set, not competed — so it is a stable ceiling to price against |

The prohibition is on **selling energy**, not on being paid. A hotel that charges for parking and
offers a socket, a mall that bundles charging into a validated parking ticket, and an office that
recovers costs through a facilities fee are all doing something the law contemplates. The
architecture below simply makes that structure explicit, priced, and bookable.

### 2.2 Two architectures

**Model A — the Airbnb transposition (per-kWh).** The host lists a price \(p_h\) in Rp/kWh; the
platform takes a commission \(\theta\); the host's electricity cost is the residential tariff.
This is the international norm and the economically cleanest form. In Indonesia today it is the
one thing that cannot be done.

**Model B — parking and service (per-hour + per-session).** The driver books a *bay* for a period.
The driver pays a parking rate \(r\) (Rp/hour) to the host and a flat service fee \(F\) (Rp/session)
to the platform. **No kilowatt-hours are bought or sold at any point.** The energy flowing through
the host's meter remains a residential sale from the utility to the host, at the host's own tariff,
exactly as it would be if the host's own car were plugged in.

The rest of the paper treats Model B as the deployable design and Model A as the benchmark and the
post-reform target state.

### 2.3 Solving Model B

Let \(P\) be the connection's usable AC power (kW), \(\eta\) the AC charging efficiency, \(t\) the
booked dwell (hours), \(p_s\) the all-in public price (Rp/kWh) and \(p_0\) the host's own tariff.

Two energy quantities must be kept apart, and conflating them is the most common error in
back-of-envelope P2P models:

- **Metered energy** \(E_m = P\,t\) — what the host's meter records and what the host pays for.
- **Battery energy** \(E_b = P\,t\,\eta\) — what the driver receives and values.

The driver's cost per useful kWh is therefore

$$c(t)\;=\;\frac{F + r\,t}{P\,t\,\eta}\;=\;\underbrace{\frac{F}{P\,\eta\,t}}_{\text{decays with dwell}}\;+\;\underbrace{\frac{r}{P\,\eta}}_{\text{hard floor}}$$

Three properties follow immediately.

**(P1) A price floor the driver can never get below.** As \(t \to \infty\), \(c \to r/(P\eta)\).
The parking rate divided by delivered power is a hard floor in Rp/kWh. For the architecture ever
to beat public charging, \(r < P\,\eta\,p_s\).

**(P2) A break-even dwell.** Setting \(c(t^\*) = p_s\),

$$t^\* \;=\; \frac{F}{P\,\eta\,p_s - r}$$

Below \(t^\*\) the P2P session is *more* expensive than the public network. The architecture is
structurally hostile to short top-ups and structurally suited to long dwell.

**(P3) A feasible band with two exogenous edges.** The host must not subsidise the guest's energy,
so \(r > P\,p_0\); the driver must be better off, so \(r < P\,\eta\,p_s\). Hence

$$P\,p_0 \;<\; r \;<\; P\,\eta\,p_s$$

Both edges are set by administratively determined tariffs. **The entire commercial design space of
P2P charging in Indonesia is a band whose width neither the host, the driver nor the platform can
influence.**

### 2.4 The fee base determines the load shape

This is the paper's central proposition, and it is a consequence of the algebra rather than of the
data.

Under **Model A** the host's revenue is \(R_A = (1-\theta)\,p_h\,P\,\eta\,t\): proportional to
power. A rational host upgrades the connection, installs a faster wallbox, and prefers many short
high-power sessions — precisely the behaviour that stacks new load onto the low-voltage network and,
because demand for charging is highest in the evening, onto the system peak.

Under **Model B** the host's revenue is \(R_B = r\,t\): **independent of power**. The host is
indifferent to how fast the guest charges and cares only that the bay is occupied. The rational
host therefore seeks long, uninterrupted bookings — overnight — and has no incentive whatsoever to
increase connected power.

The regulatory constraint, in other words, does not merely permit a second-best market. It removes
the private incentive to add peak-coincident household capacity, and replaces it with an incentive
to fill the trough. Section 5.6 quantifies the effect.

---

## 3. Data

| Dataset | Records | Period | Fields used |
|---|---|---|---|
| Public charging transaction detail, West Java | 100,782 valid sessions (of 101,020 records; 238 with zero metered energy) | March 2026 | timestamp, hour, station id and coordinates, site type, city/regency, charger power, kWh, duration, tariff components, total paid |
| Home-charging connection applications | 3,694 (2,181 completed; 3,689 geocoded) | Nov 2025 – Jun 2026 | coordinates, connected power, approval status, vehicle make, regency/district/village, application month |
| Public station recap | 331 stations | March 2026 | utilisation tagging, sessions, energy, revenue |
| Tariff decomposition | derived from the same transactions | March 2026 | energy component, municipal public-lighting levy by city, all-in price |
| Vehicle catalogue | 25 Indonesian-market EVs | 2026 | maximum onboard AC power by make |
| Population | 27 cities/regencies | BPS mid-2023 projection `[VERIFY]` | equity normalisation |

Household-level records are aggregated and pseudonymised; no individual applicant is identifiable.
Coordinates are used only to compute distances to public stations and counts per administrative
unit.

### 3.1 Operationalising "substitutable"

A recorded public session is counted as **P2P-substitutable** when all three hold:

1. **Not corridor charging.** Sessions at toll-road rest areas are excluded. There the reason for
   stopping is DC speed on an intercity trip; a 7 kW socket at someone's house is not a substitute.
2. **A host exists in the neighbourhood.** The station lies within 3 km of at least one completed
   home-charging installation. This is a proxy for matchability, not a claim about any individual
   driver's origin, and it is deliberately generous: results at 1, 2, 5 and 10 km are reported.
3. **The energy fits one night.** Session energy ≤ 45.6 kWh, the amount a 7 kW AC connection
   delivers to a battery across a seven-hour window at \(\eta = 0.93\).

This is an **upper bound on geographic matchability**, not a demand forecast. It says how much of
the recorded demand *could* physically have been served by a neighbourhood wallbox, and nothing
about willingness on either side.

---

## 4. Method

All quantities are produced by `papers/p2p/prepare.py`, in seven blocks: (A) market baseline;
(B) host supply and idle capacity; (C) substitutable demand; (D) fee architecture, feasible band
and power-risk sensitivity; (E) four-sided financials; (F) network load shift; (G) equity.

**Parameters and their provenance.** \(p_s = 2{,}608.39\) Rp/kWh and its decomposition are computed
from the transactions themselves, not assumed. \(p_0 = 1{,}699.53\) Rp/kWh is the residential
tariff for ≥3,500 VA `[VERIFY]`; the night rate \(p_0^{n} = 1{,}189.67\) applies the utility's 30 %
home-charging discount for 22:00–05:00 `[VERIFY: promotional period 1 Jul 2025 – 30 Jun 2026]`.
\(P = 7.0\) kW reflects the 7,700 VA single-phase connection that 3,553 of 3,694 applicants took.
\(\eta = 0.93\) follows the project's charging model. Capital benchmarks — Rp 1.2 bn per public DC
site, Rp 96 m/year site O&M, Rp 18 m per installed home wallbox, 10-year life — are indicative and
flagged `[VERIFY]`; the utility results in Section 5.5 are reported as sensitivities against them.

**Equity.** Gini coefficients and Lorenz curves are computed against population for three
quantities per city/regency: public stations, public energy consumed, and home-charging hosts.
Spearman rank correlations relate host counts to existing demand and existing supply.

---

## 5. Results

### 5.1 The gap the whole model has to live in

March 2026 public charging in West Java cost an all-in **Rp 2,608.39/kWh**: an energy component of
Rp 2,466.75 plus a municipal public-lighting levy averaging Rp 141.62, which varies from 5 % to
10 % by municipality and makes the same kilowatt-hour cost Rp 2,590 in one regency and Rp 2,713 in
another. Mean session size was 22.42 kWh over 53.9 minutes (medians 19.82 kWh, 40.9 minutes).

Against a residential tariff of Rp 1,699.53, the gross surplus available to any P2P arrangement is
**Rp 908.86/kWh**; against the discounted night rate of Rp 1,189.67 it is **Rp 1,418.72/kWh**. That
surplus is the only thing there is to divide among four parties.

Translated into the parking rate of Section 2.3, at \(P = 7\) kW and \(\eta = 0.93\):

| Window | Host's own tariff | Floor \(P p_0\) | Ceiling \(P\eta p_s\) | Band width |
|---|---|---|---|---|
| Night 22:00–05:00 (discount applies) | Rp 1,189.67/kWh | Rp 8,328/h | Rp 16,981/h | **Rp 8,653/h** |
| Evening 18:00–22:00 (full tariff) | Rp 1,699.53/kWh | Rp 11,897/h | Rp 16,981/h | **Rp 5,084/h** |
| Daytime 09:00–15:00 (full tariff) | Rp 1,699.53/kWh | Rp 11,897/h | Rp 16,981/h | **Rp 5,084/h** |

*Table 1 — The feasible parking-rate band. Both edges are administratively set.*

Two things follow. First, the night discount does not merely make charging cheaper; it **widens the
commercial band by 70 %**, from Rp 5,084 to Rp 8,653 per hour. Second — and this is a fragility the
business plan must confront — that discount is a **promotion with an expiry date**
(1 July 2025 – 30 June 2026) `[VERIFY]`, not a structural tariff. A P2P market built on it is built
on an administrative decision that can lapse.

### 5.2 The capacity is already installed, and it is idle

A household driving 1,200 km/month at 0.17 kWh/km needs 204 kWh into the battery, or 219 kWh
metered — **31.3 charger-hours per month**, equivalent to 3.9 full nights out of thirty. Against a
shareable window of eight hours per night, **86.9 % of the household charger's night capacity is
unused**.

| Fleet | Idle capacity | Ratio to entire public network | Public-site equivalents | Capital equivalent |
|---|---|---|---|---|
| 2,181 completed installations | **2.96 GWh/month** | **1.31×** | 431 sites | ≈ Rp 518 bn `[VERIFY]` |
| 3,694 applications | 5.02 GWh/month | 2.22× | 731 sites | ≈ Rp 877 bn `[VERIFY]` |

*Table 2 — Idle overnight capacity of the installed home-charging fleet, at 1,358 kWh per host per
month, benchmarked against the public network's 2.26 GWh/month across 329 stations.*

The comparison is deliberately blunt. **The overnight capacity sitting idle in West Java's already-
installed home chargers exceeds the total monthly output of every public charging station in the
province by 31 %.** No new capital is required to access it — only a lawful transaction.

The fleet continues to grow: applications ran at 457, 460, 551, 776 and 771 per month from January
to May 2026. The installed base is not a stock to be harvested once.

### 5.3 How much demand could actually move

| Filter | Sessions remaining | Share |
|---|---|---|
| All March 2026 sessions | 100,782 | 100 % |
| Not corridor (toll rest-area) charging | 72,414 | 71.9 % |
| Station within 3 km of a completed host | 70,423 | 69.9 % |
| Energy fits one AC night window | **65,338** | **64.8 %** |

*Table 3 — Substitutability funnel.*

The surviving segment is 65,338 sessions and **1,284,196 kWh — 56.8 % of the province's public
charging energy**. The share is remarkably insensitive to the distance threshold: 52.3 % of energy
at 1 km, 56.8 % at 3 km, 57.6 % at 10 km. Almost all of the geographic matching that is available
is available *within one kilometre*, because home chargers and public stations are drawn to the
same places (Section 5.7).

The binding filter is not distance but trip purpose: corridor charging alone removes 28 % of
sessions, and it is precisely the demand a home wallbox cannot serve.

### 5.4 A concrete design, and what each side gets

Setting \(r =\) **Rp 13,500/hour** (inside the night band, above the daytime floor) and \(F =\)
**Rp 5,000/session**:

- price floor \(r/(P\eta) =\) **Rp 2,073.73/kWh**, 20.5 % below the public network;
- break-even dwell \(t^\* =\) **1.44 hours**, i.e. **9.35 kWh** — below that, the driver should use
  a public charger.

| Dwell | Battery kWh | Metered kWh | Driver pays | Effective Rp/kWh | vs public | Host net (night) | Host net (day) |
|---|---|---|---|---|---|---|---|
| 2 h | 13.0 | 14.0 | Rp 32,000 | 2,458 | −5.8 % | Rp 10,345 | Rp 3,207 |
| 4 h | 26.0 | 28.0 | Rp 59,000 | 2,266 | −13.1 % | Rp 20,689 | Rp 6,413 |
| 6 h | 39.1 | 42.0 | Rp 86,000 | 2,202 | −15.6 % | Rp 31,034 | Rp 9,620 |
| **8 h** | **52.1** | **56.0** | **Rp 113,000** | **2,170** | **−16.8 %** | **Rp 41,378** | **Rp 12,826** |
| 10 h | 65.1 | 70.0 | Rp 140,000 | 2,151 | −17.6 % | Rp 51,723 | Rp 16,033 |

*Table 4 — Session economics at r = Rp 13,500/h, F = Rp 5,000. Host net is the parking fee less the
host's own electricity bill for the metered energy.*

The host's night margin (Rp 41,378 on an eight-hour booking) is **3.2× the daytime margin**
(Rp 12,826) for an identical service at an identical price to the driver. The entire difference is
the 30 % night discount. This is the sharpest operational finding in the paper: **in Indonesia, P2P
charging is not a business that happens to work best at night; outside the night window it barely
works at all.**

**A like-for-like comparison with the Airbnb form.** Hold the driver's price constant at
Rp 113,000 for a 52.1 kWh overnight session and ask who receives it:

| Architecture | Host receives | Platform receives |
|---|---|---|
| Model B — parking Rp 13,500/h + flat Rp 5,000 | **Rp 41,378** | Rp 5,000 |
| Model A — per-kWh at 15 % commission | Rp 29,428 | **Rp 16,950** |

*Table 5 — Same driver price, different split.*

At the same price to the driver, the lawful architecture moves **Rp 11,950 per session from the
platform to the host** — because a flat service fee does not scale with session size while a
percentage commission does. The constraint is not merely tolerable for hosts; on this dimension it
is better for them. It is the platform that pays for the constraint, which has a direct implication
for how such a platform must be capitalised (Section 5.5).

### 5.5 The four sides

**Host.** At Rp 13,500/hour on night bookings:

| Bookings/week | Dwell | Sessions/month | Net income/month | Yield on an already-installed Rp 18 m wallbox | Payback if bought to rent |
|---|---|---|---|---|---|
| 2 | 8 h | 8.7 | Rp 358,613 | 23.9 %/yr | 50 months |
| 3 | 8 h | 13.0 | **Rp 537,920** | **35.9 %/yr** | 33 months |
| 5 | 8 h | 21.7 | Rp 896,533 | 59.8 %/yr | 20 months |
| 3 | 4 h | 13.0 | Rp 268,960 | 17.9 %/yr | 67 months |

*Table 6 — Host economics.*

The right column is the wrong question and the second-to-last is the right one. A household that
installed a wallbox for its own car has **already sunk the capital**; P2P income is yield on an
existing asset, not the return on a new investment. Three bookings a week — one night in
two-and-a-third — returns **36 % a year on a Rp 18 m asset that would otherwise sit idle 87 % of
nights**. That is the offer, and it does not require the host to believe anything about future EV
adoption.

**Driver.** For a driver without home charging, covering 1,200 km/month (204 kWh):

| Source | Cost/month | vs public charging |
|---|---|---|
| Public network at Rp 2,608/kWh | Rp 532,112 | — |
| **P2P at the design fee** | **Rp 442,627** | **−Rp 89,485 (−16.8 %)** |
| Own home charging, night rate | Rp 242,693 | −54.4 % |
| Petrol equivalent (11 km/l, Rp 12,500/l) | Rp 1,363,636 | +156 % |

*Table 7 — Driver economics.*

P2P is decisively cheaper than public charging and decisively more expensive than having your own
wallbox. It does not close the gap between those who can install a charger and those who cannot —
it **halves** it. That is the honest claim, and it is the claim on which the equity case rests or
falls (Section 5.7).

**Platform.** Applying penetration rates to the substitutable segment:

| Penetration of substitutable energy | Sessions/month | GMV/month | Platform fee revenue | Host pool | Active hosts needed |
|---|---|---|---|---|---|
| 5 % | 3,267 | Rp 149 m | Rp 16.3 m | Rp 51.0 m | ≈ 151 |
| 10 % | 6,534 | Rp 299 m | Rp 32.7 m | Rp 102.0 m | ≈ 302 |
| **20 %** | **13,068** | **Rp 598 m** | **Rp 65.3 m** | **Rp 204.1 m** | **≈ 603** |
| 35 % | 22,868 | Rp 1,046 m | Rp 114.3 m | Rp 357.1 m | ≈ 1,055 |
| 50 % | 32,669 | Rp 1,495 m | Rp 163.3 m | Rp 510.2 m | ≈ 1,508 |

*Table 8 — Platform scale, at five bookings/host/week.*

A flat Rp 5,000 fee yields **10.9 % of GMV** — thin, and thinner still in absolute terms than a
percentage commission would deliver. At 20 % penetration the platform earns Rp 65 m/month against
a national customer-acquisition and payments cost base; the model reaches interesting revenue only
above 35 % penetration and ~1,000 active hosts. **A P2P platform under this architecture is a
volume business, not a margin business** — which is exactly the structural consequence of Table 5.
Whether the fee should instead be a percentage of the *parking* charge (which is not energy, and so
raises no licensing issue) is the single most consequential open design question, and we flag it as
such rather than resolving it here.

**Utility.** The utility faces a genuine trade-off, and the P2P advocacy literature usually ignores
one half of it. Energy moving from a public station to a host's meter moves from an energy
component of Rp 2,466.75/kWh to a night residential rate of Rp 1,189.67/kWh on 7.5 % more metered
energy — a dilution of about **Rp 1,187/kWh sold**.

| Penetration | Energy moved/month | Revenue dilution/year | Public-site equivalents avoided | Avoided capital + O&M per year | **Net/year** |
|---|---|---|---|---|---|
| 5 % | 64,210 kWh | Rp 0.92 bn | 9.4 | Rp 2.02 bn | **+Rp 1.10 bn** |
| 10 % | 128,420 kWh | Rp 1.83 bn | 18.7 | Rp 4.04 bn | **+Rp 2.21 bn** |
| **20 %** | **256,839 kWh** | **Rp 3.66 bn** | **37.4** | **Rp 8.08 bn** | **+Rp 4.42 bn** |
| 35 % | 449,469 kWh | Rp 6.41 bn | 65.4 | Rp 14.14 bn | **+Rp 7.73 bn** |
| 50 % | 642,098 kWh | Rp 9.15 bn | 93.5 | Rp 20.19 bn | **+Rp 11.04 bn** |

*Table 9 — Utility position. Avoided capital annuitised over 10 years at Rp 1.2 bn/site plus
Rp 96 m/site/year O&M `[VERIFY]`.*

The net is positive throughout, but the result rests on an assumption that deserves to be stated
rather than buried: **avoided sites are valued at the network's average output, and the sites a
utility avoids building are marginal sites, which run below average.** If marginal sites deliver
half the average energy, the avoided-site count doubles and the case strengthens; if the avoided
capital is not in fact avoided — because coverage mandates require the sites regardless of
utilisation — the dilution stands alone and the utility is worse off. The policy question in
Section 7 is precisely how to make the avoidance real.

One further number decides whether the utility can be expected to fund this arrangement out of the
night tariff. At Rp 1,189.67/kWh against a Java–Bali cost of supply of roughly Rp 1,150/kWh
`[VERIFY]`, the discounted rate clears cost by about **Rp 40/kWh**. There is no margin there to
finance a market from. Section 7 proposes the alternative.

### 5.6 What it does to the network

Public charging in West Java is not off-peak. The hours 17:00–21:59 carry **25.8 % of monthly
energy** in 20.8 % of the time, averaging **3.76 MW** across the province against 1.95 MW in the
seven overnight hours.

| Penetration | Peak energy displaced | Peak MW removed | Share of the charging peak |
|---|---|---|---|
| 5 % | 16,577 kWh | 0.11 MW | 2.8 % |
| 10 % | 33,155 kWh | 0.21 MW | 5.7 % |
| **20 %** | **66,310 kWh** | **0.43 MW** | **11.4 %** |
| 35 % | 116,042 kWh | 0.75 MW | 19.9 % |
| 50 % | 165,774 kWh | 1.07 MW | 28.4 % |

*Table 10 — Evening-peak relief if substitutable peak-hour sessions move into the night window.*

The absolute magnitudes are small today — a province whose system peak is measured in gigawatts is
not rescued by one megawatt. They matter for two reasons. First, they scale with the EV fleet while
the network's capacity to absorb evening charging does not. Second, the *shape* of what P2P adds is
different in kind: a public site concentrates 120 kW at one low-voltage connection, while the same
energy served by hosts is spread over **17 separate 7 kW connections** on 17 different service
drops. Under Model B, as Section 2.4 established, the host has no revenue reason to increase that
power. The architecture disperses load by construction.

### 5.7 The uncomfortable equity result

The advocacy case for P2P is that it reaches places a capital-intensive public rollout will not.
Against the West Java data, it does not.

| Distribution vs population, 27 cities/regencies | Gini |
|---|---|
| Public charging **stations** | **0.264** |
| Public charging **energy consumed** | 0.537 |
| Home-charging **hosts** | **0.599** |

*Table 11 — Concentration against population.*

Home chargers are **more unequally distributed than the public network they are supposed to
supplement**, and more unequally distributed than public consumption itself. Rank correlations
confirm the mechanism: host counts correlate with existing public energy at ρ = 0.73 and with
existing station counts at ρ = 0.71. Hosts appear where charging demand already is — the four
largest host populations (Kab. Bogor 787, Kota Depok 663, Kota Bandung 462, Kota Bekasi 400)
are the same places that already dominate public consumption. Kab. Pangandaran has no hosts at all;
Kab. Ciamis has no public station.

The reason is structural rather than accidental. A home-charging connection requires home ownership
or a landlord's consent, a garage or private frontage, and about Rp 18 m of capital. Those
conditions are distributed like wealth, and wealth is distributed like the existing public network.

The conclusion follows and should not be softened: **peer-to-peer charging is an efficiency
instrument, not an equity instrument.** It lowers the cost of serving demand where hosts already
exist. Left to itself it deepens the core–periphery split that Paper 1 measured. If it is to serve
equity, the steering must be deliberate and fiscal — Section 7.

There is, however, a real distributional gain hiding inside the aggregate. The customer for P2P is
by definition a driver who *cannot* install a wallbox — an apartment resident, a renter, a household
in dense kampung housing — and who therefore pays the full public price today. Table 7 puts that
driver's saving at Rp 89,485/month. P2P transfers surplus from those with off-street parking to
those without, *within* the districts where both live. It is progressive within places and
regressive between them.

### 5.8 Who bears the power risk

Under a time-based fee, the effective price per kWh is inversely proportional to the power the car
actually accepts. This risk does not exist under per-kWh pricing, and it falls entirely on the
driver.

| Car's accepted AC power | Battery kWh in 8 h | Driver pays | Effective Rp/kWh | vs public network |
|---|---|---|---|---|
| 3.3 kW | 24.6 | Rp 113,000 | **4,602** | **+76 %** |
| 4.0 kW | 29.8 | Rp 113,000 | 3,797 | +46 % |
| 5.0 kW | 37.2 | Rp 113,000 | 3,038 | +16 % |
| 6.6 kW | 49.1 | Rp 113,000 | 2,301 | −12 % |
| 7.0 kW | 52.1 | Rp 113,000 | 2,170 | −17 % |

*Table 12 — Effective price by onboard charger power, at the design fee.*

For the actual host fleet the exposure is modest — makes weighted by their share of the register
give an effective AC power of **6.85 kW**, and the spread across the top ten makes is only
Rp 2,170–2,301/kWh — because the Indonesian market is dominated by 6.6–7 kW onboard chargers. But a
driver whose vehicle accepts 3.3 kW pays 76 % *more* than the public network for the same booking
and has no way to know it from the listing. Any competent implementation must therefore compute and
display the **expected effective Rp/kWh for the specific vehicle** at the moment of booking, not the
parking rate. We treat this as a consumer-protection requirement, not a product nicety (Section 7,
step 4).

---

## 6. The Airbnb scheme, transposed

The user-facing product is an Airbnb for parking bays that happen to have a socket. Every Airbnb
primitive maps, and the three that do not map are the ones that matter.

| Airbnb primitive | P2P charging equivalent | Notes |
|---|---|---|
| Listing | Bay: coordinates, power, connector, photo, access instructions | Power must be *verified*, since it determines the driver's real price |
| Calendar | Nightly windows, default 21:00–05:00 | Instant-book for repeat guests; the night window is the inventory |
| Price | **Parking rate Rp/hour** within the feasible band | Never Rp/kWh — see §2 |
| Service fee | Flat Rp/session to the platform | Alternative: percentage of the parking charge (not of energy) |
| Reviews | Two-sided: access, reliability, safety, accuracy of stated power | Reliability dominates perception in this market (Paper 1) |
| Trust & safety | Identity check, electrical safety certificate, RCD verification | Not optional: the guest plugs into the host's fixed installation |
| Insurance | Host-liability cover for the installation and vehicle | The clearest gap in the Indonesian market `[VERIFY]` |
| Cancellation | Free until T−2 h; host no-show penalty | A blocked bay is a stranded trip, not a hotel night |
| Payout | Weekly transfer to the host, platform-collected | Payment aggregation is licensed activity `[VERIFY: BI PJP licence]` |

**Where the analogy breaks.**

1. **The commodity is metered and belongs to a third party.** The host is not selling a room; the
   host is reselling nothing at all while paying a utility bill that varies with what the guest
   does. This is why the parking rate must be time-based and why a maximum-power cap on the bay is
   a necessary term of the listing.
2. **The host wants the inventory.** An Airbnb host who rents out the spare room does not sleep in
   it. A P2P host's own car needs the same eight-hour window and the same socket. Section 5.2 shows
   the conflict is milder than it seems — own use consumes 3.9 nights of 30 — but it caps
   utilisation per host and makes a second socket, or a two-car household, the natural power host.
3. **Supply cannot move.** A poorly located listing cannot be repositioned. The matching problem is
   therefore permanent and geographic, and Table 3 sets its ceiling: 56.8 % of current public energy
   is within reach, and no amount of product work raises that number.

**One design note back to the product.** A companion consumer application in this project lists
sample host prices of Rp 2,200–2,800/kWh. Under the architecture derived here, the ceiling on any
economically sensible effective price is **Rp 2,458/kWh** (the price at r = Rp 16,000/h) and the
public network sits at Rp 2,608. Listings above roughly Rp 2,450/kWh are not aggressive pricing;
they are offers no informed driver should accept. The listing UI should express price as a parking
rate and *derive* the effective Rp/kWh for the driver's own car.

---

## 7. Policy: a ladder, not a switch

Nothing in Section 5 requires the law to change before anything can happen. The ladder is ordered so
that each step is useful on its own.

**Step 1 — Confirm, in writing, that a time-based bay rental is not a sale of electricity.**
The single cheapest intervention available. A directorate-general circular stating that
compensation for the use of a parking bay and fixed charging equipment, priced per unit of time and
not per kilowatt-hour, does not constitute *penjualan tenaga listrik* under UU 30/2009 and does not
require an SPKLU licence, would unlock the entire architecture at zero fiscal cost. Bound it: a
power cap (≤ 7.7 kVA), a session cap, a registration duty, and no onward supply. `[VERIFY: the
appropriate instrument — circular, ministerial regulation, or amendment to Permen ESDM 1/2023]`

**Step 2 — Create a host-meter tariff class, and make the night discount structural.**
Two defects sit in the current tariff. The night discount is a **promotion with an expiry date**,
and at Rp 1,189.67/kWh it clears the cost of supply by roughly Rp 40/kWh, so the utility cannot
finance a market from it. Both are fixed by the same instrument: a registered *P2P host* tariff,
applied to the dedicated home-charging meter, priced between the residential and public-charging
rates and permanent rather than promotional. At Rp 1,600/kWh the band remains Rp 5,781/hour wide —
enough for a Rp 2,300/kWh driver price and a Rp 3,800/hour host margin — while cutting the utility's
revenue dilution from Rp 1,187 to Rp 746 per kWh, a **37 % reduction**, and clearing cost of supply
by Rp 450/kWh. That is the price at which the utility can be a sponsor rather than a reluctant
counterparty.

**Step 3 — Make the avoided capital real.** Table 9's benefit is contingent on sites not being
built. Coverage mandates expressed in *stations per area* will force them to be built anyway and
convert the whole exercise into pure revenue dilution. Rewrite the obligation in terms of **served
demand within an access standard**, and allow registered P2P bays to count toward it at a
discounted weight reflecting their lower power and private ownership. This is the step that turns
P2P from a cost to the utility into a saving.

**Step 4 — Mandate effective-price disclosure at booking.** A time-based fee hides its per-kWh cost,
and Table 12 shows the hidden cost can be 76 % *above* the public network for a slow-charging car.
Require every listing to display, before payment, the expected effective Rp/kWh for the vehicle
being booked, computed from the bay's verified power and the vehicle's onboard limit, alongside the
public-network price for comparison. Require the bay's power to be verified, not self-declared.

**Step 5 — Steer it, or it will concentrate.** Table 11 is the result that should govern how public
money is spent here. Host subsidies distributed on demand will be claimed in Bogor, Depok, Bandung
and Bekasi, where hosts already are. Any public support for P2P — installation subsidy, connection-
fee waiver, guaranteed minimum utilisation — should be **conditioned on location**, targeting
regencies with high registered-EV counts and low host density, and evaluated against the host Gini
rather than against host counts. A programme that raises the number of hosts while leaving the Gini
at 0.599 has bought efficiency and called it access.

**Sequencing.** Steps 1 and 4 are administrative and could be done this year. Step 2 requires a
tariff decision. Step 3 requires rewriting a coverage obligation. Step 5 requires a budget line.
Only Step 1 is strictly necessary for the market to exist; only Step 5 makes it fair.

---

## 8. Limitations

1. **One month of demand.** March 2026 transactions, a single province. Seasonality, holiday travel
   and the Ramadan/Idul Fitri corridor peak are not represented.
2. **Substitutability is an upper bound.** Section 3.1 measures geographic matchability, not
   willingness. No driver in the dataset has been asked whether they would park overnight at a
   stranger's house, and no host has been asked whether they would let them.
3. **Host register ≠ active hosts.** 2,181 completed installations are potential supply, not
   consenting supply. Participation rates in comparable platforms are low `[VERIFY]`, and the
   analysis is deliberately silent on what fraction would list.
4. **Capital benchmarks are indicative.** Rp 1.2 bn/site, Rp 96 m/year O&M and Rp 18 m/wallbox drive
   Table 9 and Table 6 and are flagged `[VERIFY]`. Utility results should be read as sensitivities.
5. **Avoided sites valued at average, not marginal, output** (Section 5.5) — the direction of the
   bias is stated but not corrected.
6. **The legal readings are secondary.** Every clause reference in Section 2.1 carries `[VERIFY]`
   and must be checked against the primary texts, and against any instrument issued after
   June 2026, before submission. This paper argues about a design under a constraint; it does not
   give legal advice.
7. **No behavioural model of pricing.** The design fee is chosen inside the feasible band, not
   estimated from revealed host or driver preferences. A discrete-choice experiment is the obvious
   next step.
8. **No congestion or queueing model.** Matching is treated as frictionless within 3 km.

---

## 9. Conclusion

Peer-to-peer charging in Indonesia cannot be built the way it is built elsewhere, because the thing
it would trade — the kilowatt-hour — is reserved to licensed suppliers. Re-basing the transaction
onto time and space makes the market lawful, and the algebra of that re-basing turns out to carry
most of the paper's findings. The business lives inside a band of Rp 8,328–16,981 per hour whose
edges are administratively set; it is priced with a floor and a break-even dwell that make it an
overnight product; and because revenue accrues per hour rather than per kilowatt-hour, the host's
incentive is occupancy rather than throughput — which is to say, the constraint that was supposed to
be the obstacle is what points the private incentive at the trough of the load curve instead of its
peak.

The capacity is already there. The 2,181 home chargers West Java has installed hold 2.96 GWh of idle
overnight capacity every month, a third more than every public station in the province produces, and
56.8 % of current public charging energy is close enough to a host to be served by one. The driver
without a garage saves 17 %; the host earns 36 % a year on an asset already bought; the utility is
ahead on the capital it does not spend, provided the mandates let it not spend it.

What the data does not support is the claim usually made for P2P. Home chargers are more
concentrated than the public network (Gini 0.599 against 0.264) and appear where demand already is
(ρ = 0.73). Peer-to-peer charging will make charging cheaper in the places that already have it. It
becomes an instrument of access only if it is aimed there deliberately — which is a budget decision,
not a platform feature.

---

## Figures & tables planned

**Fig. 1** — The feasible band: parking rate against effective Rp/kWh, with the residential floor,
the night-discounted floor and the public-price ceiling drawn as lines.
**Fig. 2** — Effective price against dwell time for r = Rp 11,000–17,000/h, with \(t^\*\) marked.
**Fig. 3** — Substitutability funnel and its sensitivity to the distance threshold.
**Fig. 4** — Hourly energy profile with the evening peak and the night window shaded; overlay of the
shifted profile at 20 % penetration.
**Fig. 5** — Lorenz curves against population for stations, public energy and hosts.
**Fig. 6** — Host count against public energy by city/regency, log–log, with the ρ = 0.73 fit.

**T1** — Feasible band by window · **T2** — Idle capacity · **T3** — Funnel · **T4** — Session
economics · **T5** — Model A vs B split · **T6–T9** — Four-sided financials · **T10** — Peak relief
· **T11** — Gini · **T12** — Power risk.

## References to assemble

P2P charging platforms and shared private infrastructure; two-part and time-based tariff design;
platform market design and take-rate structure; electricity licensing and unbundling in
single-buyer systems; managed charging and load-shifting evidence; energy-justice treatment of
private-asset sharing; Indonesian EV policy instruments (UU 30/2009 as amended by UU 6/2023;
PP 5/2021; Permen ESDM 1/2023; the prevailing electricity tariff adjustment decision).
`[VERIFY: all]`

## Data availability

Public charging transactions and the home-charging application register are used under a data
agreement with the utility, aggregated and pseudonymised. The full analysis pipeline is published
at `papers/p2p/prepare.py`; the derived payload at `papers/p2p/p2p.json` reproduces every figure
and table above.
