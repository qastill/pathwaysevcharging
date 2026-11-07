// Naskah v3 "Capacity maps as an equity instrument" (docx), angka dibaca dari capacity.json + strengthen.json.
// Jalankan dari akar repositori:  node papers/capacity/v3/build_paper_v3.js [keluaran.docx]
const fs = require("fs");
const path = require("path");
const d = require(process.env.DOCX_MODULE || "docx");
const { Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, AlignmentType,
        HeadingLevel, Footer, Header, PageNumber, BorderStyle, ShadingType } = d;
const ROOT = path.resolve(__dirname, "../../..");
const FIG = path.join(ROOT, "papers/capacity/v3/figs") + "/";
const OUT = process.argv[2] || path.join(ROOT, "papers/capacity/Capacity_Maps_Equity_CIRED2027_v3.docx");
const S = JSON.parse(fs.readFileSync(path.join(ROOT, "papers/capacity/v3/strengthen.json")));
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "papers/capacity/capacity.json")));
const B = S.base, R = B.rules, F1 = B.f1, RD = B.random, TW = B.two, V = S.variants;
const f0 = (x) => Math.round(x).toLocaleString("en-US"), f1 = (x) => x.toFixed(1), f2 = (x) => x.toFixed(2), f3 = (x) => x.toFixed(3);
const sg = (x, k = 2) => (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(k);
const gainP = (k) => R[k].terc[0] - B.baseline.terc[0];
const gainR = (k) => R[k].terc[2] - B.baseline.terc[2];
const vg = (v) => 100 * (v.rules_prop.dwh.owners / v.rules_prop.headroom.owners - 1);

const FONT = "Times New Roman", INK = "1B2A3A", GRID = "BFC6CF", HEAD = "E8EDF2", HL = "E3F1EE";
const TEXT_W = 9638;
const runs = (t, o = {}) => [new TextRun({ text: t, font: FONT, size: o.size || 22, bold: o.bold, italics: o.italics, color: o.color })];
const body = (t) => new Paragraph({ children: runs(t), alignment: AlignmentType.JUSTIFIED, spacing: { after: 140, line: 300 } });
const rich = (parts) => new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 140, line: 300 },
  children: parts.flatMap((p) => typeof p === "string" ? runs(p) : runs(p.t, p)) });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })] });
const center = (t, o = {}) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: o.after ?? 60 }, children: runs(t, o) });
const note = (t) => new Paragraph({ children: runs(t, { size: 18, italics: true, color: "5E6B79" }), spacing: { before: 60, after: 200 }, alignment: AlignmentType.JUSTIFIED });
const caption = (t) => new Paragraph({ children: runs(t, { size: 19, color: "333F4C" }), spacing: { before: 60, after: 240 }, alignment: AlignmentType.JUSTIFIED });
const tcaption = (t) => new Paragraph({ children: runs(t, { size: 19, bold: true }), spacing: { before: 200, after: 100 }, keepNext: true });
const bullet = (t) => new Paragraph({ children: runs(t), bullet: { level: 0 }, spacing: { after: 80, line: 290 }, alignment: AlignmentType.LEFT });

function pngSize(p) { const b = fs.readFileSync(p); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; }
function fig(file, widthPx, cap) {
  const s = pngSize(FIG + file);
  return [new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 160, after: 60 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(FIG + file), transformation: { width: widthPx, height: Math.round(widthPx * s.h / s.w) },
      altText: { title: cap.slice(0, 60), description: cap, name: file } })] }), caption(cap)];
}
const border = { style: BorderStyle.SINGLE, size: 4, color: GRID };
const borders = { top: border, bottom: border, left: border, right: border };
function table(headers, rows, widths, { hiRow = -1, size = 18 } = {}) {
  const cell = (t, i, head, hi) => new TableCell({ width: { size: widths[i], type: WidthType.DXA }, borders,
    shading: head ? { fill: HEAD, type: ShadingType.CLEAR, color: "auto" } : hi ? { fill: HL, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 80, right: 80 },
    children: [new Paragraph({ alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER, children: runs(String(t), { size, bold: head }) })] });
  return new Table({ width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: widths, rows: [
    new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true, false)) }),
    ...rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((v, i) => cell(v, i, false, ri === hiRow)) }))] });
}

const C = [];
const add = (...xs) => xs.forEach((x) => (Array.isArray(x) ? C.push(...x) : C.push(x)));

// ------------------------------------------------------------------ judul
add(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 240 }, children: runs("Capacity maps as an equity instrument: publishing charging demand and network headroom as open data in a vertically integrated DSO", { size: 32, bold: true, color: INK }) }),
  center("Qashtalani Haramaini¹ ², Alyas Widita¹, Liz Taylor³", { bold: true, after: 40 }),
  center("¹ Monash University Indonesia, Indonesia   ² PT PLN (Persero) UID Jawa Barat, Indonesia   ³ Monash University, MADA, Australia", { size: 18, after: 40 }),
  center("qashtalani.haramaini@monash.edu · alyas.widita@monash.edu · liz.taylor@monash.edu", { size: 18, after: 320 }));

// ------------------------------------------------------------------ abstrak
add(new Paragraph({ children: runs("Abstract", { bold: true }), spacing: { after: 80 } }),
  new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 160, line: 290 }, indent: { left: 360, right: 360 }, children: runs(
    `Distribution system operators (DSOs) increasingly publish hosting-capacity maps to steer connection applicants toward spare grid capacity. We argue that in a fast-growing network with low electric-vehicle (EV) penetration such a map is an allocation instrument: what the DSO publishes shapes where public charging is built and who is served. West Java, Indonesia, offers a rare test because PT PLN (Persero) is both the DSO and the dominant public charge-point operator, and so holds both surfaces that European regulation keeps apart. Fusing ${f0(D.meta.total)} distribution-transformer load records, 101,020 charging sessions and ${f0(D.meta.ev)} geocoded registered EV customers on a 5 km grid, and joining them to the 27 regencies and their per-capita expenditure, we find that: (i) installed grid capacity separates cells with a charger from cells without (AUC ${f2(F1.auc.kva)}) while spare capacity does not (AUC ${f2(F1.auc.rel)}); (ii) cells with high demand but low headroom hold ${f1(B.hl.evp)} % of owners and ${f1(B.hl.chgp)} % of chargers; (iii) for the same 50 new sites, a headroom-only rule reaches ${R.headroom.owners} owners and strands ${R.headroom.stranded} sites, a demand-only rule reaches ${R.demand.owners} but places ${R.demand.infeas} below the feasibility threshold, and a demand-within-headroom rule reaches ${R.dwh.owners} with neither; (iv) headroom-only raises coverage in the poorest third of regencies by ${f1(gainP("headroom"))} percentage points against ${f1(gainP("dwh"))} for demand-within-headroom; and (v) transformer and substation headroom are statistically unrelated (ρ = ${sg(TW.rho)}). The ordering of rules survives 5,000 random portfolios, four site sizes and four cell sizes. We propose a minimum standard for publishable two-surface capacity maps and argue that, where the DSO is also the CPO, publication is a functional substitute for unbundling.`, { size: 20 }) }),
  new Paragraph({ spacing: { after: 300 }, indent: { left: 360, right: 360 }, children: runs("Keywords: capacity maps; hosting capacity; EV charging; distributive justice; open data; vertically integrated utility; Indonesia", { size: 19, italics: true }) }));

// ------------------------------------------------------------------ 1
add(h1("1. Introduction"),
  body("Grid connection has become the binding constraint on public charging deployment in many jurisdictions [1,3]. European regulation now requires system operators to publish available hosting capacity [1], and DSO associations treat capacity maps as a building block of a customer-oriented grid [2]. The maps are framed as transparency: they inform developers and shorten connection lead times."),
  body("This paper starts from a different premise. A capacity map is a ranking of locations, and a ranking that drives investment is also a distribution of benefits. If the only published layer is network headroom, capital flows to where the grid is strong. In fast-growing, low-penetration networks that is where the last generation of investment went, typically urban cores and industrial corridors, which is also where charging demand is already served. A headroom-only map therefore tends to densify rather than fill gaps. This is an energy-justice problem in the sense of Sovacool and Dworkin [6]: a distributive outcome produced by a procedural choice about what to disclose."),
  body("Testing the claim requires two surfaces that are rarely held by one organisation: network headroom, a DSO asset, and charging demand, a CPO asset. West Java offers both. PT PLN (Persero) is the vertically integrated utility; its distribution unit UID Jawa Barat operates the 20 kV and low-voltage network for 18.1 million customers, and PLN operates most of the province’s public charging stations (SPKLU) [13]. To our knowledge this is the first study to overlay transformer load, charging sessions and registered EV customers at province scale."),
  body("The contributions are: (1) a test of whether the roll-out follows spare capacity or grid density; (2) a demand × headroom classification that isolates the locational gap; (3) a counterfactual comparison of three siting rules a DSO could implement through what it publishes, benchmarked against random placement; (4) an assessment of who gains, using the 27 regencies and their per-capita expenditure; (5) evidence that transformer and substation headroom carry independent information; (6) robustness across portfolio size, site size and spatial resolution; and (7) a data-readiness audit that translates into a minimum disclosure standard."));

// ------------------------------------------------------------------ 2
add(h1("2. Background and research gap"),
  h2("2.1 Hosting-capacity maps in Europe"),
  body("Hosting capacity is the amount of load or generation that can be connected without violating operational limits [8]. Its calculation is sensitive to method: Lennerhag et al. showed at CIRED 2017 that five methods yield widely different values, and that measurement-based approaches raise usable capacity without added risk [4]. Under the 2024 electricity market reform, EU system operators must publish available capacity and the criteria used [1]. E.DSO concludes that the priority is clearer definitions, stronger links to connection processes and a balanced approach to transparency [2]. ICCT finds public grid-capacity maps for charging in only part of the EU [3]. None of these documents treats the map as a distributive instrument."),
  h2("2.2 Charging-access equity"),
  body("A separate literature documents that public charger access is unequally distributed across income and ethnicity [5] and clusters with commercial land use [9]. These studies treat the grid as exogenous. Work on EV hosting capacity [10,11] treats demand as exogenous. The two literatures meet in optimisation models that co-locate chargers with grid capacity [12], which assume a single planner holding both datasets, precisely the situation in a vertically integrated utility."),
  h2("2.3 Indonesia"),
  body("Presidential Regulation 55/2019 launched Indonesia’s battery-EV programme [7]. PLN reports 3.0 % electricity sales growth and 5.9 % connected-capacity growth in West Java in 2025 [13]. EV penetration remains well below 1 % of the vehicle stock, so the charging network is being built ahead of demand, the regime in which the published layer matters most."));

// ------------------------------------------------------------------ 3
add(h1("3. Case and data"),
  body("Five datasets were assembled (Table 1). The transformer register is a field-survey database: two spot readings (day and night) of phase currents per distribution transformer, with rated kVA, feeder, primary substation (GI) and coordinates from two sources. The charging log contains every session at PLN’s public chargers in March 2026. The EV customer register lists households that applied for the home-charging tariff, geocoded at the service point; it is used as a latent-demand proxy that does not depend on where public chargers were built. Regency boundaries and 2024 socio-economic indicators come from Statistics Indonesia (BPS) [18]."),
  tcaption("Table 1 – Datasets used. The four PLN registers are internal; raw records are not public."),
  table(["Dataset", "Records", "Period", "Key fields"], [
    ["Distribution-transformer load register", `${f0(D.meta.total)} (${f0(D.meta.usable)} usable)`, "2020–2024", "kVA, day/night loading, feeder, GI, coordinates, survey date"],
    ["GI transformer register", `${D.meta.gi_trafo} units, ${f0(D.meta.gi_mva)} MVA`, "2022", "MVA, loading, GI code"],
    ["Public charging sessions", `101,020 sessions; ${D.meta.sites_reg} sites in the register`, "Mar 2026", "kWh, duration, revenue, site"],
    ["Registered EV customers", `${f0(D.meta.ev)} geocoded`, "to Jun 2026", "Coordinates, connected power"],
    ["Regency boundaries and indicators (BPS)", "27 regencies and cities", "2024", "Polygons, per-capita expenditure, HDI, poverty"],
  ], [2900, 2500, 1300, 2938]));

// ------------------------------------------------------------------ 4
add(h1("4. Method"),
  h2("4.1 Two-level headroom and growth correction"),
  body(`For each transformer i with rated capacity Si and measured loading λi (share of nominal current, larger of day and night readings), headroom at the 80 % planning limit is Hi = max(0, Si·(0.8 − λi)). Records with invalid coordinates, S outside 5–3,000 kVA or λ outside 0–200 % were dropped, leaving ${f0(D.meta.usable)}. Primary-substation headroom is computed identically from GI transformer MVA and loading (${D.meta.gi_trafo} transformers, ${f0(D.meta.gi_mva)} MVA). Surveys are dated (median age ${D.meta.med_age} years, oldest ${D.meta.max_age}), so loading is compounded to March 2026 as λ(2026) = λ(t)·(1 + g)^(2026.2 − t), with g = 3.0 %/yr (the DSO’s 2025 sales growth [13]) and sensitivities at 5.9 and 9.7 %/yr.`),
  h2("4.2 Grid, classification and siting rules"),
  body(`All layers are aggregated to a 0.045° (≈5 km) grid of ${f0(D.meta.cells)} non-empty cells; ${D.meta.cells_ev} contain registered owners and ${D.meta.cells_chg} a public charger. Cells with owners are classified at the medians of owners (2.5) and headroom (2.8 MVA). Three rules then place 50 sites in the ${B.pool} unserved cells with owners (${f0(B.pool_ev)} owners). Headroom-only ranks by H. Demand-only ranks by owners. Demand-within-headroom ranks by owners among cells with H ≥ ${D.meta.feasible} kVA (one 4 × 60 kW site), then the remainder. For each rule we record owners reached, stranded sites (in cells below the pool median of ${B.med_pool} owners) and infeasible sites (H < ${D.meta.feasible} kVA). Demand-within-headroom has no infeasible site by construction whenever enough feasible cells exist; what is tested is the cost of that constraint in owners reached.`),
  h2("4.3 Equity metrics"),
  body("Each owner and each cell centre is assigned by point-in-polygon to one of the 27 BPS regencies (nearest polygon for points on the coast or a boundary). The regency field carried in the DSO registers was not used: it mixes regency names with service-unit names and contains duplicate spellings. Coverage is the share of registered owners living in a cell with a public charger. We report coverage overall and by thirds of regencies ranked by 2024 per-capita expenditure (nine regencies each), the owner-level concentration index of coverage with respect to regency expenditure [15], and the between-regency Gini of coverage shares. A positive concentration index means coverage leans toward owners in richer regencies."),
  h2("4.4 Statistical tests and robustness"),
  body(`Rank correlations are reported with 95 % bootstrap intervals (${f0(2000)} resamples) [17]. To test what predicts the presence of a charger, we compute the area under the ROC curve (AUC) for each cell attribute across all ${f0(F1.n_pos + F1.n_neg)} cells with transformers [16]; 0.5 is a coin toss. Rule outcomes are compared with ${f0(RD.n)} random 50-site portfolios drawn from the same pool. Sweeps vary the number of sites (5 to ${B.pool}) and the feasibility threshold (120 to 960 kVA). Finally, the entire pipeline is re-run at 0.03°, 0.06° and 0.09° cells, with the number of sites held at 38 % of the unserved pool so that rules are compared on equal footing.`));

// ------------------------------------------------------------------ 5
add(h1("5. Results"),
  h2("5.1 Two different surfaces"),
  body(`Fig. 1 shows the two surfaces side by side. Headroom concentrates in the Bekasi–Karawang industrial corridor and central Bandung; registered owners concentrate in the Bogor–Depok–Bekasi belt and Bandung. At 5 km resolution, ${f1(B.gap.h_nochg)} % of growth-adjusted headroom lies in cells with no public charger and ${f1(B.gap.ev_nochg)} % of owners live in such cells. Both shares fall as cells grow (to ${f1(V[3].gap.h_nochg)} % and ${f1(V[3].gap.ev_nochg)} % at 0.09°), because larger cells are more likely to contain a charger; they are therefore reported as 5 km figures.`),
  ...fig("fig1_two_surfaces.png", 640, "Fig. 1 – The two surfaces. (a) 2026-adjusted transformer headroom per 5 km cell. (b) Registered EV owners per cell. (c) Public chargers, cells with owners but no charger (pink), and high-demand/low-headroom cells with no charger (hatched)."),
  h2("5.2 The roll-out follows grid density, not spare capacity"),
  body(`Across all cells with transformers, installed capacity separates cells with a charger from cells without almost as well as any variable we have (AUC ${f2(F1.auc.kva)}; number of transformers ${f2(F1.auc.ntr)}; absolute headroom ${f2(F1.auc.abs)}). Relative headroom, the share of capacity still free, does not (AUC ${f2(F1.auc.rel)}). Median installed capacity is ${f0(F1.med_kva.chg)} kVA in charger cells and ${f0(F1.med_kva.nochg)} kVA elsewhere, ${Math.round(F1.med_kva.chg / F1.med_kva.nochg)} times higher, while the median free share is ${f1(100 * F1.med_rel.chg)} % and ${f1(100 * F1.med_rel.nochg)} % (Fig. 2). Among served cells, charging energy correlates with absolute headroom (ρ = ${sg(F1.abs)}, 95 % CI ${sg(F1.abs_ci[0])} to ${sg(F1.abs_ci[1])}) and installed kVA (ρ = ${sg(F1.kva)}), but not with relative headroom (ρ = ${sg(F1.rel)}, 95 % CI ${sg(F1.rel_ci[0])} to ${sg(F1.rel_ci[1])}). The result holds at every cell size: AUC of relative headroom is ${V.map((v) => f2(v.f1.auc.rel)).join(", ")} at 0.03°, 0.045°, 0.06° and 0.09°. Chargers were placed where the grid is dense, without regard to whether it is loaded.`),
  ...fig("fig2_density_not_capacity.png", 640, `Fig. 2 – (a) AUC of each cell attribute for separating the ${F1.n_pos} cells with a charger from the ${f0(F1.n_neg)} without. (b) Median installed kVA. (c) Median free share of installed capacity.`),
  h2("5.3 The equity gap is locational"),
  body(`Fig. 3 classifies the ${D.meta.cells_ev} cells with owners. The high-demand/high-headroom quadrant (89 cells) holds ${f1(D.quad.HH.evp)} % of owners and ${f1(D.quad.HH.chgp)} % of chargers. The gap is the high-demand/low-headroom quadrant (30 cells): ${f1(B.hl.evp)} % of owners and ${f1(B.hl.chgp)} % of chargers, with ${B.hl.unserved} cells and ${B.hl.unserved_ev} owners having no charger at all. At every resolution the owners’ share of this quadrant exceeds the chargers’ share, by a factor of ${V.map((v) => (v.hl.evp / v.hl.chgp).toFixed(1)).join(", ")} from finest to coarsest. A headroom-only map ranks these cells last; a demand-only map ranks them first without signalling the connection cost.`),
  ...fig("fig3_quadrant.png", 430, "Fig. 3 – Demand × headroom quadrants of the cells with registered owners (medians dashed; teal = has a public charger, sized by energy; grey = none)."),
  h2("5.4 The published layer changes the portfolio"),
  body(`Fig. 4 maps where each rule places its 50 sites and Fig. 5 summarises the outcomes. Headroom-only selects large strong-grid cells: it reaches ${R.headroom.owners} owners and places ${R.headroom.stranded} sites in below-median-demand cells. Demand-only goes to the owner clusters and reaches ${R.demand.owners} owners, but ${R.demand.infeas} of its sites fall below ${D.meta.feasible} kVA. Demand-within-headroom reaches ${R.dwh.owners} owners with no stranded and no infeasible site: ${f1(100 * (R.dwh.owners / R.headroom.owners - 1))} % more than headroom-only, at a cost of ${R.demand.owners - R.dwh.owners} owners (${f1(100 * (1 - R.dwh.owners / R.demand.owners))} %) relative to demand-only. All three rules lie beyond every one of ${f0(RD.n)} random portfolios, which reach ${f0(RD.owners_mean)} owners on average (95th percentile ${RD.owners_p95}), strand ${f1(RD.stranded_mean)} sites and place ${f1(RD.infeas_mean)} below the threshold (Fig. 7). The question a DSO faces is therefore not whether to use data but which layers to publish.`),
  ...fig("fig4_site_maps.png", 640, "Fig. 4 – Where each rule places 50 new sites. Filled markers sized by owners in the cell; hollow = stranded (below-median demand); X = infeasible (< 240 kVA headroom); grey dots = existing chargers."),
  ...fig("fig5_rule_outcomes.png", 600, "Fig. 5 – Owners reached, stranded sites and infeasible sites under each rule; dashed line = mean of 5,000 random 50-site portfolios."),
  h2("5.5 Who gains: income equity"),
  body(`Coverage today is ${f1(B.baseline.terc[0])} % in the poorest third of regencies, against ${f1(B.baseline.terc[2])} % in the richest third (concentration index ${f3(B.baseline.ci)}). The rules diverge sharply in who benefits (Fig. 6, Table 2). Headroom-only raises coverage in the poorest third by ${f1(gainP("headroom"))} points and in the richest by ${f1(gainR("headroom"))}, widening the gap from ${f1(B.baseline.terc[2] - B.baseline.terc[0])} to ${f1(R.headroom.terc[2] - R.headroom.terc[0])} points. Demand-within-headroom raises the poorest third by ${f1(gainP("dwh"))} points, more than demand-only (${f1(gainP("demand"))}), and yields the lowest concentration index (${f3(R.dwh.ci)}, against ${f3(R.headroom.ci)} for headroom-only). The poorest third contains only 272 owners, 181 of them in Kabupaten Bandung Barat, so the magnitudes are imprecise; the direction is what the evidence supports. Headroom-only adds about ${Math.round(gainP("headroom") / 100 * 272)} newly covered owners in the poorest third; demand-within-headroom about ${Math.round(gainP("dwh") / 100 * 272)}.`),
  body(`The between-regency Gini of coverage behaves differently. It is lowest for random placement (${f3(RD.gini_mean)}), because random sites spread across regencies regardless of where owners live, and among the rules it is lowest for headroom-only (${f3(R.headroom.gini)}). Evenness across regencies alone is therefore the wrong target: it rewards spreading sites thinly. The earlier version of this analysis reported Gini values computed over the regency field of the DSO registers, which mixes regency and service-unit names; those values are superseded.`),
  ...fig("fig6_income_equity.png", 640, "Fig. 6 – (a) Share of registered owners living in a cell with a public charger, by thirds of regencies ranked by 2024 per-capita expenditure. (b) Gain in percentage points in the poorest and richest thirds."),
  tcaption("Table 2 – Outcomes of 50 new sites in the unserved pool. Coverage from owner points; concentration index (CI) of coverage with respect to regency per-capita expenditure; Gini of coverage across regencies with owners."),
  table(["Scenario", "Owners reached", "Stranded", "Infeasible", "Coverage", "Poorest third", "CI", "Gini"], [
    ["Today", "—", "—", "—", `${f1(B.baseline.cov)} %`, `${f1(B.baseline.terc[0])} %`, f3(B.baseline.ci), f3(B.baseline.gini)],
    ["Random (mean)", f0(RD.owners_mean), f1(RD.stranded_mean), f1(RD.infeas_mean), "—", "—", f3(RD.ci_mean), f3(RD.gini_mean)],
    ["Headroom-only", R.headroom.owners, R.headroom.stranded, R.headroom.infeas, `${f1(R.headroom.cov)} %`, `${f1(R.headroom.terc[0])} %`, f3(R.headroom.ci), f3(R.headroom.gini)],
    ["Demand-only", R.demand.owners, R.demand.stranded, R.demand.infeas, `${f1(R.demand.cov)} %`, `${f1(R.demand.terc[0])} %`, f3(R.demand.ci), f3(R.demand.gini)],
    ["Demand within headroom", R.dwh.owners, R.dwh.stranded, R.dwh.infeas, `${f1(R.dwh.cov)} %`, `${f1(R.dwh.terc[0])} %`, f3(R.dwh.ci), f3(R.dwh.gini)],
  ], [2438, 1050, 950, 950, 1050, 1150, 1000, 1050], { hiRow: 4 }),
  note(`Growth sensitivity for demand within headroom: ${D.sens.map((x) => x.owners).join(" / ")} owners at ${D.sens.map((x) => x.g).join(" / ")} %/yr.`),
  h2("5.6 Robustness"),
  body(`Fig. 8 tests the ordering. (a) Demand-based rules reach more owners than headroom-only at every portfolio size until the pool is exhausted. (b) As the site size, and therefore the feasibility threshold, grows from 120 to 960 kVA, demand-only places ${B.feas.map((r) => r.demand.infeas).join(", ")} infeasible sites, while demand-within-headroom gives up more owners (${B.feas.map((r) => r.dwh.owners).join(", ")}) but never falls to the headroom-only level (${R.headroom.owners}). (c) Re-running the whole pipeline at four cell sizes, demand-within-headroom reaches ${V.map((v) => "+" + vg(v).toFixed(0) + " %").join(", ")} more owners than headroom-only. Table 3 separates what is robust from what is not. The count of stranded sites is resolution-sensitive (${V.map((v) => v.rules_prop.headroom.stranded).join(", ")}) and is not used as a headline result.`),
  ...fig("fig7_random_baseline.png", 520, `Fig. 7 – Owners reached by ${f0(RD.n)} random 50-site portfolios drawn from the same ${B.pool} cells, with the three rules marked.`),
  ...fig("fig8_robustness.png", 640, "Fig. 8 – Robustness. (a) Owners reached by number of sites. (b) Owners reached by feasibility threshold, with demand-only infeasible sites labelled. (c) Gain over headroom-only at four cell sizes (N = 38 % of the unserved pool)."),
  tcaption("Table 3 – Results across spatial resolution. N is held at 38 % of the unserved pool."),
  table(["Cell size", "Pool / N", "AUC rel. headroom", "ρ rel. headroom", "Demand-in-headroom vs headroom-only", "Demand-only infeasible", "Headroom-only stranded"],
    V.map((v) => [`${v.cell.toFixed(3)}° (≈${Math.round(v.cell * 111)} km)`, `${v.pool} / ${v.n_prop}`, f2(v.f1.auc.rel), sg(v.f1.rel), `+${vg(v).toFixed(0)} %`, v.rules_prop.demand.infeas, v.rules_prop.headroom.stranded]),
    [1600, 1150, 1250, 1150, 1800, 1300, 1388], { hiRow: 1 }),
  h2("5.7 Transformer and substation headroom are independent"),
  body(`Among the ${TW.n} served cells linked to a primary substation, transformer headroom and the headroom of the supplying GI are unrelated (Spearman ρ = ${sg(TW.rho)}, 95 % CI ${sg(TW.rho_ci[0])} to ${sg(TW.rho_ci[1])}; Fig. 9). Split at the medians, ${TW.tight_tr_ample_gi} cells have tight transformer but ample substation headroom and ${TW.ample_tr_tight_gi} the reverse: ${f1(TW.discord)} % of served cells, close to the 50 % expected if the two levels were independent. An earlier figure of 51 % could not be reproduced; the stronger statement is that one level carries no information about the other. A low-voltage-only map would steer developers away from cells where a new dedicated transformer on a lightly loaded feeder is cheap; a substation-only map would hide that the last few hundred metres of network are saturated. Both levels must be published.`),
  ...fig("fig9_two_levels.png", 400, "Fig. 9 – Transformer headroom in the cell against headroom of the supplying primary substation, served cells (medians dashed; marker size = charging energy)."),
  h2("5.8 Ageing and data readiness"),
  body(`Growth correction at 3.0 %/yr moves ${f0(D.scen[1].over)} transformers (${f1(100 * D.scen[1].over / D.meta.usable)} % of usable records) past the 80 % limit and reduces province-wide headroom from ${f0(D.scen[0].trafo)} to ${f0(D.scen[1].trafo)} MVA at transformer level and from ${f0(D.scen[0].gi)} to ${f0(D.scen[1].gi)} MVA at GI level; at 9.7 %/yr the reductions are ${Math.round(100 * (1 - D.scen[3].trafo / D.scen[0].trafo))} % and ${Math.round(100 * (1 - D.scen[3].gi / D.scen[0].gi))} % (Fig. 10, right). The register is not publication-ready (Fig. 10, left): ${f1(D.audit.gi)} % of records are not linked to a GI, ${f1(D.audit.koord)} % have survey coordinates more than 1 km from the asset register, ${f1(D.audit.geo)} % have missing or invalid coordinates, ${f1(D.audit.beban)} % lack a load reading and ${f1(D.audit.kva)} % lack rated capacity. ${f1(D.audit.pii)} % of records carry field-staff names, which must be removed before any disclosure.`),
  ...fig("fig10_readiness.png", 640, `Fig. 10 – Left: share of the ${f0(D.meta.total)} transformer records failing each readiness check. Right: province-wide headroom at the 80 % limit under four load-growth assumptions.`));

// ------------------------------------------------------------------ 6
add(h1("6. Discussion"),
  h2("6.1 What the evidence supports"),
  body("Table 4 records each claim with the test it faced. The central claims, that the roll-out follows grid density and that a headroom-only map reaches fewer owners and fewer of the poorest regencies, survive every test. Two figures from earlier drafts were demoted or revised: the count of stranded sites depends on resolution, and the claim that the demand-within-headroom rule minimises the regency Gini does not hold once regencies are assigned correctly."),
  tcaption("Table 4 – Claims ledger."),
  table(["Claim", "Evidence", "Status"], [
    ["Roll-out follows grid density, not spare capacity", `AUC ${f2(F1.auc.kva)} vs ${f2(F1.auc.rel)}; ρ (relative) CI spans zero; all cell sizes`, "Robust"],
    ["High-demand/low-headroom cells are under-served", "owners’ share 1.4–2.6× chargers’ share at all cell sizes", "Robust"],
    ["Headroom-only reaches fewer owners", `demand within headroom reaches +${V.map((v) => vg(v).toFixed(0)).join("/+")} % more; beyond all random draws`, "Robust"],
    ["Headroom-only does least for the poorest regencies", `+${f1(gainP("headroom"))} vs +${f1(gainP("dwh"))} points; lowest CI for demand within headroom`, "Supported (small n)"],
    ["Headroom-only strands 30 % of sites", `${V.map((v) => v.rules_prop.headroom.stranded).join(" / ")} stranded by cell size`, "Resolution-sensitive"],
    ["Demand-only places infeasible sites", `${B.feas.map((r) => r.demand.infeas).join(" → ")} as site size grows`, "Mostly robust"],
    ["Demand within headroom minimises regency Gini", "random and headroom-only are lower", "Not supported"],
    ["Transformer and GI levels disagree", `ρ = ${sg(TW.rho)}; ${f1(TW.discord)} % discordant`, "Restated as independence"],
  ], [3300, 4338, 2000], { size: 17 }),
  h2("6.2 A minimum standard for publishable capacity maps"),
  body("The results translate into five requirements, each tied to a finding."),
  bullet("Two network levels at least, transformer and primary substation, with the feeder level where available, because the levels are independent (Section 5.7)."),
  bullet("Growth correction with a stated rate and survey date, because a static snapshot overstates substation headroom by a fifth within a few years (Section 5.8)."),
  bullet("A demand layer next to headroom, because without it the map steers investment away from the poorest regencies (Section 5.5)."),
  bullet("Spatial aggregation (5 km cells here; 2 km hexagons in the companion siting tool) to protect customers, staff and critical infrastructure, consistent with E.DSO’s call for balanced transparency [2]."),
  bullet("Versioning and a published data-quality score, because nearly half of the register lacks a substation link (Section 5.8)."),
  h2("6.3 Publication as a substitute for unbundling"),
  body("EU DSOs are generally barred from owning charging points, partly because of the information advantage documented here. Indonesia has the opposite structure: the incumbent can site its own chargers on knowledge of headroom and demand that third-party CPOs lack. Publishing the two-surface map removes that asymmetry without changing ownership. It is a functional substitute for unbundling, and it steers public and private capital toward gap-filling rather than densification. A phased path follows from the findings: clean the register first (staff names, GI links, coordinates), then publish both surfaces at 5 km with growth correction, then add the feeder level and quarterly versions, and finally link the map to connection requests and monitor coverage in the poorest regencies."),
  h2("6.4 Reach, feasibility and evenness"),
  body("The three rules expose a three-way trade-off. Demand-only maximises reach but ignores feasibility. Headroom-only guarantees feasibility but sacrifices reach and the poorest regencies. Demand-within-headroom gives up 2.5 % of reach to make every site connectable, and it does the most for the poorest third. A between-regency Gini, by contrast, is minimised by random placement, which reaches less than half as many owners. Equity targets for charging networks should therefore be stated as coverage of under-served groups, not as evenness across administrative units."),
  h2("6.5 Limitations"),
  body("Headroom is derived from two spot readings per transformer: a planning proxy, not a hosting-capacity calculation in the sense of [4,8]. Registered EV customers proxy latent demand and under-represent households without a home charger. The equity result rests on 272 owners in the poorest third and on regency-level expenditure, an area measure that does not describe the owners themselves. The growth rate is province-wide. The counterfactual assumes equal sites, and the feeder level (2,574 feeders) is not yet included."));

// ------------------------------------------------------------------ 7
add(h1("7. Conclusions"),
  body(`In a vertically integrated DSO building charging ahead of demand, the capacity map is a planning decision disguised as a data product. The West Java evidence shows that the existing roll-out followed grid density rather than spare capacity, and that what the DSO publishes changes both how many owners new sites reach and who they are. For the same 50 sites, a headroom-only map reaches ${R.headroom.owners} owners and adds ${f1(gainP("headroom"))} points of coverage in the poorest third of regencies; publishing demand within headroom reaches ${R.dwh.owners}, connects every site and adds ${f1(gainP("dwh"))} points. These results survive random benchmarks and changes in portfolio size, site size and resolution. Publishing both surfaces, at two network levels, growth-corrected and quality-scored, is achievable with data every DSO already holds.`),
  new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.JUSTIFIED, children: runs("Data availability. ", { bold: true, size: 20 }).concat(runs("Aggregated outputs and the reproducible pipeline are in the project repository (papers/capacity/prepare.py, papers/capacity/v3/strengthen.py). The raw PLN register data are internal and are not published.", { size: 20 })) }));

const refs = [
  "[1] Directive (EU) 2019/944 on common rules for the internal market for electricity, Art. 32; Regulation (EU) 2024/1747 amending Regulation (EU) 2019/943.",
  "[2] E.DSO, “Technology Report on Grid Hosting Capacity Maps,” E.DSO Technology & Knowledge Sharing Committee, Brussels. [Access date to be confirmed.]",
  "[3] ICCT, “Mapping the charge: why grid data is key to electrifying road freight,” International Council on Clean Transportation, Nov. 2025. [Confirm title before submission.]",
  "[4] O. Lennerhag, S. Ackeby, M. H. J. Bollen, G. Foskolos and T. Gafurov, “Using measurements to increase the accuracy of hosting capacity calculations,” CIRED – Open Access Proc. J., vol. 2017, no. 1, pp. 2041–2044, 2017.",
  "[5] C.-W. Hsu and K. Fingerman, “Public electric vehicle charger access disparities across race and income in California,” Transport Policy, vol. 100, pp. 59–67, 2021.",
  "[6] B. K. Sovacool and M. H. Dworkin, “Energy justice: Conceptual insights and practical applications,” Applied Energy, vol. 142, pp. 435–444, 2015.",
  "[7] Peraturan Presiden No. 55/2019 (Indonesia); Regulation (EU) 2023/1804 (AFIR).",
  "[8] S. M. Ismael, S. H. E. Abdel Aleem, A. Y. Abdelaziz and A. F. Zobaa, “State-of-the-art of hosting capacity in modern power systems with distributed generation,” Renewable Energy, vol. 130, pp. 1002–1020, 2019.",
  "[9] G. Carlton and S. Sultana, “Electric vehicle charging station accessibility and land use clustering: A case study of the Chicago region,” J. Urban Mobility, vol. 2, 100019, 2022.",
  "[10] A. K. Karmaker, K. Prakash, M. N. I. Siddique, M. A. Hossain and H. Pota, “Electric vehicle hosting capacity analysis: Challenges and solutions,” Renewable and Sustainable Energy Reviews, vol. 189, 113916, 2024.",
  "[11] M. Muratori, “Impact of uncoordinated plug-in electric vehicle charging on residential power demand,” Nature Energy, vol. 3, pp. 193–201, 2018.",
  "[12] W. Dai, C. Wang, H. H. Goh, J. Zhao and J. Jian, “Hosting capacity evaluation method for power distribution networks integrated with electric vehicles,” J. Modern Power Systems and Clean Energy, vol. 11, no. 5, pp. 1564–1575, 2023.",
  "[13] PT PLN (Persero) UID Jawa Barat, 2025 performance release: 63,503 GWh sales (+3.0 %), 35,686 MVA connected (+5.9 %), Feb. 2026.",
  "[14] Ember, “Transparent grids for all: hosting capacity maps,” Jul. 2024. [Confirm before submission.]",
  "[15] O. O’Donnell, E. van Doorslaer, A. Wagstaff and M. Lindelow, Analyzing Health Equity Using Household Survey Data. Washington, DC: World Bank, 2008, ch. 8.",
  "[16] T. Fawcett, “An introduction to ROC analysis,” Pattern Recognition Letters, vol. 27, no. 8, pp. 861–874, 2006.",
  "[17] B. Efron and R. J. Tibshirani, An Introduction to the Bootstrap. New York: Chapman & Hall, 1993.",
  "[18] Badan Pusat Statistik (BPS), regency boundaries and 2024 indicators (per-capita expenditure, HDI, poverty) for Jawa Barat.",
];
add(h1("References"), ...refs.map((t) => new Paragraph({ children: runs(t, { size: 19 }), spacing: { after: 80 }, indent: { left: 400, hanging: 400 } })));

const doc = new Document({
  creator: "Qashtalani Haramaini, Alyas Widita, Liz Taylor", title: "Capacity maps as an equity instrument",
  styles: { default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 26, bold: true, color: INK }, paragraph: { spacing: { before: 300, after: 120 }, keepNext: true, keepLines: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 22, bold: true, color: INK }, paragraph: { spacing: { before: 200, after: 80 }, keepNext: true, keepLines: true, outlineLevel: 1 } }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: runs("Capacity maps as an equity instrument · draft for CIRED 2027", { size: 16, italics: true, color: "6B7785" }) })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 })] })] }) },
    children: C }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length); });
