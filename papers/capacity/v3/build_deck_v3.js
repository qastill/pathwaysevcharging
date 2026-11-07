// Deck v3 "Capacity maps as an equity instrument" — 24 slide, dibangun dari strengthen.json + capacity.json.
// Jalankan dari akar repositori:  NODE_PATH=<folder node_modules berisi pptxgenjs> node papers/capacity/v3/build_deck_v3.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const ROOT = path.resolve(__dirname, "../../..");
const FIG = path.join(ROOT, "papers/capacity/v3/figs") + "/";
const OUT = process.argv[2] || path.join(ROOT, "slides/Capacity_Maps_Equity_CIRED2027_v3.pptx");
const THEME_JS = process.env.APPLY_THEME;
const S = JSON.parse(fs.readFileSync(path.join(ROOT, "papers/capacity/v3/strengthen.json")));
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "papers/capacity/capacity.json")));
const B = S.base, R = B.rules, F1 = B.f1, RD = B.random, TW = B.two, V = S.variants;

const INK = "1B2A3A", TEAL = "0F7C6E", CORAL = "D1495B", AMBER = "E0A526", MUTED = "5E6B79",
      LIGHT = "F3F5F7", WHITE = "FFFFFF", SOFT = "C9D6E3", TEAL_LT = "E3F1EE", CORAL_LT = "FBE7EA", AMBER_LT = "FBF1DA";
const THEME = { name: "Capacity Maps Equity", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: INK, lt1: WHITE, dk2: "24404F", lt2: LIGHT, accent1: TEAL, accent2: CORAL, accent3: AMBER,
            accent4: "3D6E8F", accent5: MUTED, accent6: "9DB4C0", hlink: TEAL, folHlink: MUTED } };
const nb = (s) => String(s).replace(/ %/g, " %");
const f1 = (x) => x.toFixed(1), f2 = (x) => x.toFixed(2), f0 = (x) => Math.round(x).toLocaleString("en-US");
const terc = (k) => (k === "base" ? B.baseline.terc : R[k].terc);

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Calibri", bodyFontFace: "Calibri" };
pres.title = "Capacity maps as an equity instrument";
pres.author = "Qashtalani Haramaini, Alyas Widita, Liz Taylor";
let n = 0, cur = null;
const sec = (name) => { if (name !== cur) { pres.addSection({ title: name }); cur = name; } return name; };
const SRC = "Source: PLN UID Jawa Barat internal data (transformer surveys 2020–24, GI register, March 2026 charging log, registered EV customers); BPS 2024. Reproduced by papers/capacity/prepare.py and v3/strengthen.py.";
const T = (s, text, o) => s.addText(typeof text === "string" ? nb(text) : text, Object.assign({ fontFace: "Calibri", margin: 0, isTextBox: true, valign: "top", color: INK }, o));

function base(section, title, { lead, notes } = {}) {
  const s = pres.addSlide({ sectionTitle: sec(section) });
  n += 1;
  s.background = { color: WHITE };
  T(s, title, { x: 0.6, y: 0.38, w: 12.1, h: 1.0, fontSize: 27, bold: true });
  if (lead) T(s, lead, { x: 0.6, y: 1.36, w: 12.1, h: 0.45, fontSize: 15, color: MUTED });
  T(s, SRC, { x: 0.6, y: 7.0, w: 11.3, h: 0.3, fontSize: 8.5, color: MUTED });
  T(s, String(n), { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: MUTED, align: "right" });
  if (notes) s.addNotes(notes);
  return s;
}
const card = (s, x, y, w, h, fill = LIGHT) =>
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.08 });
function stat(s, x, y, w, h, big, label, color = TEAL, fill = LIGHT, bigSize = 32) {
  card(s, x, y, w, h, fill);
  T(s, big, { x: x + 0.22, y: y + 0.15, w: w - 0.44, h: 0.7, fontSize: bigSize, bold: true, color, valign: "middle" });
  T(s, label, { x: x + 0.22, y: y + 0.88, w: w - 0.44, h: h - 1.0, fontSize: 13 });
}
const circleNum = (s, x, y, d, txt, fill = TEAL, size = 16) => {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
  T(s, txt, { x, y, w: d, h: d, fontSize: size, bold: true, color: WHITE, align: "center", valign: "middle" });
};
const img = (s, file, x, y, w, h) => s.addImage({ path: FIG + file, x, y, w, h, sizing: { type: "contain", w, h } });
const arrow = (s, x, y, w, color = MUTED) =>
  s.addShape(pres.shapes.RIGHT_ARROW, { x, y, w, h: 0.32, fill: { color }, line: { color } });

// ===================================================================== 1. Judul
{
  n += 1;
  const s = pres.addSlide({ sectionTitle: sec("Introduction") });
  s.background = { color: INK };
  T(s, "Capacity maps as an equity instrument", { x: 0.8, y: 1.5, w: 11.7, h: 1.1, fontSize: 44, bold: true, color: WHITE });
  T(s, "Publishing charging demand and network headroom as open data in a vertically integrated DSO",
    { x: 0.8, y: 2.75, w: 11.2, h: 0.9, fontSize: 22, color: SOFT });
  T(s, [{ text: "Qashtalani Haramaini", options: { bold: true, breakLine: true } },
        { text: "Alyas Widita · Liz Taylor", options: { breakLine: true } },
        { text: "Monash University · PT PLN (Persero) UID Jawa Barat", options: { color: SOFT } }],
    { x: 0.8, y: 4.4, w: 11, h: 1.2, fontSize: 16, color: WHITE });
  T(s, "CIRED 2027 · West Java, Indonesia · draft for discussion", { x: 0.8, y: 6.45, w: 9, h: 0.4, fontSize: 12, color: AMBER });
  s.addNotes("Talk in one line: what a DSO chooses to publish on its capacity map decides where public chargers go and who gets served. West Java is a rare case because one company holds both the grid data and the charging data.");
}

// ===================================================================== 2. Ringkasan eksekutif
{
  const s = base("Introduction", "Six findings, each tested against chance, resolution and site size", {
    notes: "Executive summary. Each card is one finding; the rest of the deck is the evidence. The equity finding (card 3) is new in this version: it uses the 27 BPS regency polygons and per-capita expenditure instead of the mixed regency labels in the earlier pipeline." });
  const cards = [
    [TEAL, `AUC ${f2(F1.auc.kva)} vs ${f2(F1.auc.rel)}`, "Installed grid capacity predicts where chargers are; spare capacity does not (coin toss = 0.50)."],
    [CORAL, `${f1(B.hl.evp)} % vs ${f1(B.hl.chgp)} %`, "Share of EV owners vs share of chargers in high-demand, low-headroom cells."],
    [TEAL, `+${f1(R.dwh.terc[0] - B.baseline.terc[0])} vs +${f1(R.headroom.terc[0] - B.baseline.terc[0])} pts`, "Coverage gain in the poorest third of regencies: demand within headroom vs headroom-only."],
    [INK, `+14 to +32 %`, "More owners reached than headroom-only, at every cell size from 3 to 10 km."],
    [CORAL, `ρ = ${TW.rho >= 0 ? "+" : "−"}${f2(Math.abs(TW.rho))}`, "Transformer and substation headroom are unrelated, so one level says nothing about the other."],
    [AMBER, `${f1(D.audit.pii)} %`, "of load records carry field-staff names; 44 % lack a substation link. Not publication-ready."],
  ];
  cards.forEach((c, i) => {
    const x = 0.6 + (i % 3) * 4.1, y = 1.6 + Math.floor(i / 3) * 2.65;
    card(s, x, y, 3.85, 2.4, LIGHT);
    T(s, c[1], { x: x + 0.25, y: y + 0.2, w: 3.4, h: 0.8, fontSize: 28, bold: true, color: c[0], valign: "middle" });
    T(s, c[2], { x: x + 0.25, y: y + 1.1, w: 3.4, h: 1.2, fontSize: 14 });
  });
}

// ===================================================================== 3. Argumen: peta = alokasi
{
  const s = base("Introduction", "A capacity map ranks locations, so it also decides who gets served", {
    lead: "Every published layer becomes a ranking that capital follows",
    notes: "This is the causal chain we test. If the map shows only headroom, developers go where the grid is strong, which is where the last wave of investment went, which is where demand is already served." });
  const steps = [["What the DSO publishes", "headroom only, or headroom + demand", INK],
                 ["Where developers apply", "the top-ranked cells get the applications", "3D6E8F"],
                 ["Where chargers are built", "connection approved where headroom exists", TEAL],
                 ["Who is served", "owners near the new sites, and nobody else", CORAL]];
  steps.forEach((st, i) => {
    const x = 0.6 + i * 3.15;
    card(s, x, 2.3, 2.75, 2.3, LIGHT);
    circleNum(s, x + 0.25, 2.5, 0.55, String(i + 1), st[2]);
    T(s, st[0], { x: x + 0.25, y: 3.2, w: 2.3, h: 0.7, fontSize: 17, bold: true });
    T(s, st[1], { x: x + 0.25, y: 3.85, w: 2.3, h: 0.7, fontSize: 13, color: MUTED });
    if (i < 3) arrow(s, x + 2.8, 3.3, 0.3);
  });
  card(s, 0.6, 5.0, 12.1, 1.55, CORAL_LT);
  T(s, [{ text: "The equity problem. ", options: { bold: true, color: CORAL } },
        { text: "In a fast-growing, low-EV network, a headroom-only map ranks the urban cores first, because that is where the grid is strong and where chargers already are. It densifies instead of filling gaps: a distributive outcome produced by a procedural choice about what to disclose." }],
    { x: 0.9, y: 5.2, w: 11.5, h: 1.2, fontSize: 16 });
}

// ===================================================================== 4. Setting
{
  const s = base("Introduction", "PLN holds both surfaces that Europe keeps apart", {
    notes: "In Europe the DSO is generally not allowed to own chargers, partly because of this information advantage. In West Java PLN is both, so it holds both layers. That lets us test the claim, and it is why publication matters." });
  // EU
  card(s, 0.6, 1.6, 5.9, 4.9, LIGHT);
  T(s, "EU: unbundled", { x: 0.9, y: 1.8, w: 5.3, h: 0.5, fontSize: 18, bold: true, color: MUTED });
  [["DSO", "network headroom", INK, 0.9], ["CPO", "charging demand", "3D6E8F", 3.7]].forEach(([t, d, c, x]) => {
    card(s, x, 2.6, 2.5, 1.5, WHITE);
    T(s, t, { x: x + 0.2, y: 2.75, w: 2.1, h: 0.5, fontSize: 22, bold: true, color: c });
    T(s, d, { x: x + 0.2, y: 3.3, w: 2.1, h: 0.6, fontSize: 13 });
  });
  T(s, "Two organisations, two datasets. The DSO may not own charge points, so neither side sees both surfaces.",
    { x: 0.9, y: 4.5, w: 5.3, h: 1.6, fontSize: 15 });
  // Jawa Barat
  card(s, 6.8, 1.6, 5.9, 4.9, TEAL_LT);
  T(s, "West Java: vertically integrated", { x: 7.1, y: 1.8, w: 5.3, h: 0.5, fontSize: 18, bold: true, color: TEAL });
  card(s, 7.1, 2.6, 5.3, 1.5, WHITE);
  T(s, "PT PLN (Persero)", { x: 7.3, y: 2.75, w: 4.9, h: 0.5, fontSize: 22, bold: true, color: TEAL });
  T(s, "DSO for 18.1 million customers and the dominant public CPO", { x: 7.3, y: 3.3, w: 4.9, h: 0.6, fontSize: 13 });
  T(s, "One organisation holds transformer load, substation data, the charging log and the EV customer register. That makes the test possible, and it creates an information asymmetry with third-party CPOs.",
    { x: 7.1, y: 4.5, w: 5.3, h: 1.8, fontSize: 15 });
}

// ===================================================================== 5. Data
{
  const s = base("Introduction", "Four internal registers, fused on a 5 km grid", {
    notes: "All four are internal PLN data; raw records are not public. The charging session count (101,020) was checked against the March 2026 CSV. Owners are a latent-demand proxy that does not depend on where chargers were built." });
  const cw = 2.85, gap = 0.2;
  stat(s, 0.6, 1.7, cw, 2.3, f0(D.meta.total), `transformer load records, ${f0(D.meta.usable)} usable after plausibility checks (2020–24)`, INK);
  stat(s, 0.6 + (cw + gap), 1.7, cw, 2.3, `${D.meta.gi_trafo} GI`, `primary-substation transformers, ${f0(D.meta.gi_mva)} MVA`, INK);
  stat(s, 0.6 + 2 * (cw + gap), 1.7, cw, 2.3, "101,020", `charging sessions in March 2026 at ${D.meta.sites_reg} public sites`, TEAL);
  stat(s, 0.6 + 3 * (cw + gap), 1.7, cw, 2.3, f0(D.meta.ev), "geocoded registered EV customers (home-charging tariff)", AMBER);
  card(s, 0.6, 4.35, 12.1, 2.2, LIGHT);
  T(s, [{ text: "Fusion grid. ", options: { bold: true } },
        { text: `0.045° cells (≈5 km): ${f0(D.meta.cells)} cells, ${D.meta.cells_ev} with registered owners, ${D.meta.cells_chg} with a public charger. Owners and cells are assigned to the 27 BPS regencies by point-in-polygon and joined to 2024 per-capita expenditure.`, options: { breakLine: true } },
        { text: "Robustness grid. ", options: { bold: true } },
        { text: "The whole pipeline is re-run at 0.03°, 0.06° and 0.09° to test whether findings depend on the cell size." }],
    { x: 0.9, y: 4.55, w: 11.5, h: 1.9, fontSize: 15, paraSpaceAfter: 8 });
}

// ===================================================================== 6. Metode
{
  const s = base("Introduction", "From spot readings to a ranking a developer could act on", {
    notes: "Headroom at the 80 percent planning limit, compounded to March 2026 at 3 percent per year (DSO sales growth), sensitivities at 5.9 and 9.7. The three rules are what a DSO implicitly chooses when it decides which layers to publish." });
  const steps = [
    ["Headroom", "H = max(0, S·(0.8 − λ))\nper transformer and per GI"],
    ["Growth to 2026", "λ·(1+g)^(2026.2 − t)\ng = 3.0 %/yr (5.9, 9.7)"],
    ["5 km cells", "sum transformer H,\nmean GI H, owners, chargers"],
    ["Three rules", "headroom-only · demand-only ·\ndemand within headroom"],
    ["Stress tests", "5,000 random portfolios,\nN, kVA and cell-size sweeps"],
  ];
  steps.forEach((st, i) => {
    const x = 0.6 + i * 2.48;
    card(s, x, 1.8, 2.2, 3.0, i === 3 ? TEAL_LT : LIGHT);
    circleNum(s, x + 0.2, 2.0, 0.55, String(i + 1), i === 4 ? AMBER : TEAL);
    T(s, st[0], { x: x + 0.2, y: 2.7, w: 1.85, h: 0.5, fontSize: 16, bold: true });
    T(s, st[1], { x: x + 0.2, y: 3.25, w: 1.9, h: 1.5, fontSize: 12 });
    if (i < 4) arrow(s, x + 2.22, 3.15, 0.24);
  });
  const outs = [["Owners reached", "registered owners in the selected cells"],
                ["Stranded", "sites in below-median-demand cells"],
                ["Infeasible", `sites with < ${D.meta.feasible} kVA headroom (one 4 × 60 kW site)`],
                ["Equity", "coverage by income third, concentration index, regency Gini"]];
  outs.forEach((o, i) => {
    const x = 0.6 + i * 3.06;
    T(s, [{ text: o[0], options: { bold: true, color: TEAL, breakLine: true } }, { text: o[1], options: { fontSize: 13 } }],
      { x, y: 5.15, w: 2.85, h: 1.3, fontSize: 15 });
  });
  T(s, "Outcomes measured for each rule:", { x: 0.6, y: 4.85, w: 6, h: 0.3, fontSize: 12, color: MUTED });
}

// ===================================================================== 7. Dua permukaan
{
  const s = base("Findings", "Headroom and demand are two different maps", {
    lead: "Spare capacity concentrates in the industrial corridors; owners concentrate in the Bogor–Depok–Bekasi belt and Bandung",
    notes: `Panel a is what a headroom-only map would show. Panel b is what a demand layer adds. Panel c overlays them: ${f1(B.gap.h_nochg)} percent of growth-adjusted headroom sits in cells with no charger, and ${f1(B.gap.ev_nochg)} percent of owners live in such cells. These two shares fall with coarser cells (bigger cells are more likely to contain a charger), so quote them as 5 km figures.` });
  img(s, "fig1_two_surfaces.png", 0.5, 1.95, 12.3, 4.95);
}

// ===================================================================== 8. Temuan 1
{
  const s = base("Findings", `Grid density predicts a charger (AUC ${f2(F1.auc.kva)}); spare capacity does not (${f2(F1.auc.rel)})`, {
    notes: `AUC is the probability that a randomly chosen cell with a charger scores higher than a randomly chosen cell without one. 0.5 is a coin toss. Median installed capacity is ${f0(F1.med_kva.chg)} kVA in charger cells vs ${f0(F1.med_kva.nochg)} without, but the spare share is the same (${f1(100 * F1.med_rel.chg)} vs ${f1(100 * F1.med_rel.nochg)} percent). Among served cells, energy correlates with absolute headroom rho = ${f2(F1.abs)} [${F1.abs_ci.join(", ")}] and not with relative headroom rho = ${f2(F1.rel)} [${F1.rel_ci.join(", ")}].` });
  img(s, "fig2_density_not_capacity.png", 0.5, 1.6, 12.3, 3.9);
  card(s, 0.6, 5.65, 12.1, 1.15, TEAL_LT);
  T(s, [{ text: "Robust: ", options: { bold: true, color: TEAL } },
        { text: `AUC of relative headroom is ${V.map((v) => f2(v.f1.auc.rel)).join(" / ")} at 3 / 5 / 7 / 10 km cells; installed kVA stays at ${V.map((v) => f2(v.f1.auc.kva)).join(" / ")}. Correlation with relative headroom: ρ = ${f2(F1.rel)}, 95 % CI ${F1.rel_ci[0]} to +${F1.rel_ci[1]}.` }],
    { x: 0.9, y: 5.8, w: 11.5, h: 0.9, fontSize: 14 });
}

// ===================================================================== 9. Temuan 2: kuadran
{
  const s = base("Findings", `${f1(B.hl.evp)} % of owners live where demand is high and headroom low, with ${f1(B.hl.chgp)} % of chargers`, {
    notes: "Quadrants split at the median cell (2.5 owners, 2.8 MVA). The high-demand / high-headroom quadrant is broadly well served. The gap is top-left. At every cell size the owners' share in this quadrant exceeds the chargers' share (19.0 vs 7.3, 11.6 vs 5.6, 9.7 vs 3.9, 5.2 vs 3.6 percent)." });
  img(s, "fig3_quadrant.png", 0.5, 1.5, 6.3, 5.35);
  stat(s, 7.2, 1.7, 5.5, 1.6, `${B.hl.unserved} cells · ${B.hl.unserved_ev} owners`, "high demand, low headroom, and no charger at all", CORAL, CORAL_LT, 28);
  T(s, [{ text: "What each map would do with them", options: { bold: true, breakLine: true } },
        { text: "Headroom-only map: ranks them last.", options: { bullet: true, breakLine: true } },
        { text: "Demand-only map: ranks them first, without warning that connection is costly.", options: { bullet: true, breakLine: true } },
        { text: "Two-surface map: shows both, so the developer can price the connection.", options: { bullet: true } }],
    { x: 7.2, y: 3.6, w: 5.5, h: 2.6, fontSize: 15, paraSpaceAfter: 6 });
  T(s, `Holds at every cell size: owners' share exceeds chargers' share by 1.4× to 2.6×.`, { x: 7.2, y: 6.2, w: 5.5, h: 0.6, fontSize: 13, color: MUTED });
}

// ===================================================================== 10. Peta penempatan
{
  const s = base("Findings", "The same 50 sites land in different places depending on what is published", {
    lead: `50 new sites chosen from the ${B.pool} unserved cells that have registered owners (${f0(B.pool_ev)} owners)`,
    notes: "Headroom-only picks large, strong-grid cells, many with only one or two owners: hollow circles are stranded sites. Demand-only goes straight to the owner clusters, including three cells where the grid cannot host a 4 x 60 kW site (the X marks). Demand within headroom keeps the demand focus and drops the infeasible cells." });
  img(s, "fig4_site_maps.png", 0.5, 2.0, 12.3, 4.8);
}

// ===================================================================== 11. Hasil vs acak
{
  const s = base("Findings", "Every rule beats chance; only demand within headroom has no stranded and no infeasible sites", {
    notes: `Random placement of 50 sites in the same pool reaches ${f0(RD.owners_mean)} owners on average (95th percentile ${RD.owners_p95}), strands ${f1(RD.stranded_mean)} sites and places ${f1(RD.infeas_mean)} below feasibility. All three rules are at the 100th percentile of the random distribution for owners reached. The demand-within-headroom rule has zero infeasible sites by construction; the finding is the cost of that constraint: ${R.demand.owners - R.dwh.owners} owners (${f1(100 * (1 - R.dwh.owners / R.demand.owners))} percent).` });
  img(s, "fig5_rule_outcomes.png", 0.5, 1.55, 12.3, 3.75);
  const cols = [["Headroom-only", CORAL, CORAL_LT, `${R.headroom.owners} owners · ${R.headroom.stranded} stranded`, "Reaches 12 % fewer owners than demand within headroom and puts 30 % of sites where demand is below median."],
                ["Demand-only", AMBER, AMBER_LT, `${R.demand.owners} owners · ${R.demand.infeas} infeasible`, "Reaches the most owners, but 3 sites cannot be connected without reinforcement."],
                ["Demand within headroom", TEAL, TEAL_LT, `${R.dwh.owners} owners · 0 · 0`, `Gives up ${R.demand.owners - R.dwh.owners} owners (2.5 %) to make every site connectable.`]];
  cols.forEach((c, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 5.45, 3.85, 1.4, c[2]);
    T(s, c[3], { x: x + 0.2, y: 5.55, w: 3.5, h: 0.4, fontSize: 15, bold: true, color: c[1] });
    T(s, c[4], { x: x + 0.2, y: 5.95, w: 3.5, h: 0.85, fontSize: 12 });
  });
}

// ===================================================================== 12. Ekuitas pendapatan
{
  const s = base("Findings", `Headroom-only lifts the poorest third of regencies by ${f1(R.headroom.terc[0] - B.baseline.terc[0])} points; demand within headroom by ${f1(R.dwh.terc[0] - B.baseline.terc[0])}`, {
    notes: "Regencies are ranked by 2024 per-capita expenditure (BPS) and split into thirds of nine. Coverage is the share of registered owners living in a cell with a public charger. The poorest third has only 272 owners, 181 of them in Kabupaten Bandung Barat, so read the percentages with their counts. A headroom-only map adds almost nothing for the poorest third because strong-grid cells are concentrated in richer regencies." });
  img(s, "fig6_income_equity.png", 0.5, 1.5, 12.3, 3.95);
  stat(s, 0.6, 5.55, 3.95, 1.3, `+${Math.round((R.headroom.terc[0] - B.baseline.terc[0]) / 100 * 272)} owners`, "poorest third, headroom-only", CORAL, CORAL_LT, 24);
  stat(s, 4.7, 5.55, 3.95, 1.3, `+${Math.round((R.dwh.terc[0] - B.baseline.terc[0]) / 100 * 272)} owners`, "poorest third, demand within headroom", TEAL, TEAL_LT, 24);
  stat(s, 8.8, 5.55, 3.9, 1.3, `CI ${R.dwh.ci.toFixed(3)}`, `income concentration index (headroom-only ${R.headroom.ci.toFixed(3)})`, INK, LIGHT, 24);
}

// ===================================================================== 13. Tabel ekuitas
{
  const s = base("Findings", "Evenness alone is the wrong target: random placement is the most even and reaches the fewest owners", {
    notes: "Between-regency Gini of coverage is lowest for random placement because random sites spread across regencies regardless of where owners are. That is why the paper reports reach, the poorest-third coverage and the income concentration index together, not Gini alone. The earlier draft's Gini (0.69 to 0.60, and 0.49 to 0.36 in v2) was computed over 47 mixed regency labels; these values use the 27 BPS regencies." });
  const hdr = ["Scenario (50 new sites)", "Owners reached", "Coverage, all", "Coverage, poorest third", "Concentration index", "Regency Gini"];
  const rows = [
    ["Today", "—", `${f1(B.baseline.cov)} %`, `${f1(B.baseline.terc[0])} %`, B.baseline.ci.toFixed(3), B.baseline.gini.toFixed(3)],
    ["Random (mean of draws)", f0(RD.owners_mean), "—", "—", RD.ci_mean.toFixed(3), RD.gini_mean.toFixed(3)],
    ["Headroom-only", R.headroom.owners, `${f1(R.headroom.cov)} %`, `${f1(R.headroom.terc[0])} %`, R.headroom.ci.toFixed(3), R.headroom.gini.toFixed(3)],
    ["Demand-only", R.demand.owners, `${f1(R.demand.cov)} %`, `${f1(R.demand.terc[0])} %`, R.demand.ci.toFixed(3), R.demand.gini.toFixed(3)],
    ["Demand within headroom", R.dwh.owners, `${f1(R.dwh.cov)} %`, `${f1(R.dwh.terc[0])} %`, R.dwh.ci.toFixed(3), R.dwh.gini.toFixed(3)],
  ];
  const cell = (t, o = {}) => ({ text: nb(String(t)), options: Object.assign({ fontFace: "Calibri", fontSize: 15, color: INK, align: "center", valign: "middle" }, o) });
  const data = [hdr.map((h, i) => cell(h, { bold: true, color: WHITE, fill: { color: INK }, align: i ? "center" : "left", fontSize: 13 }))];
  rows.forEach((r, ri) => data.push(r.map((v, i) => cell(v, { align: i ? "center" : "left", fill: { color: ri === 4 ? TEAL_LT : ri === 1 ? LIGHT : WHITE },
    bold: (ri === 4 && (i === 3 || i === 4)) || (ri === 1 && i === 5), color: (ri === 1 && i === 5) ? CORAL : INK }))));
  s.addTable(data, { x: 0.6, y: 1.65, w: 12.1, colW: [3.3, 1.6, 1.7, 2.1, 1.7, 1.7], rowH: 0.55,
    border: { type: "solid", pt: 0.75, color: "D5DAE0" }, margin: 0.06 });
  T(s, [{ text: "How to read it. ", options: { bold: true } },
        { text: "Concentration index > 0 means coverage leans toward richer regencies. Demand within headroom has the lowest index and the highest coverage in the poorest third. Random placement has the lowest Gini but reaches less than half the owners, so a Gini target alone would reward spreading sites thinly." }],
    { x: 0.6, y: 5.15, w: 12.1, h: 1.5, fontSize: 15 });
}

// ===================================================================== 14. Kebetulan?
{
  const s = base("Findings", "Could any rule do this by luck? No: all three sit beyond every random draw", {
    notes: `5,000 random 50-site portfolios from the same ${B.pool} cells. Mean ${f0(RD.owners_mean)} owners, 95th percentile ${RD.owners_p95}. The lowest rule (headroom-only, ${R.headroom.owners}) is already far outside the distribution. So the comparison that matters is between rules, which is what the published layer decides.` });
  img(s, "fig7_random_baseline.png", 0.6, 1.55, 8.2, 3.6);
  stat(s, 9.1, 1.7, 3.6, 1.55, f0(RD.owners_mean), "owners reached by a random 50-site portfolio (mean)", MUTED);
  stat(s, 9.1, 3.45, 3.6, 1.55, String(RD.owners_p95), "95th percentile of 5,000 random draws", MUTED);
  card(s, 0.6, 5.45, 12.1, 1.35, LIGHT);
  T(s, [{ text: "Implication: ", options: { bold: true } },
        { text: `any informed rule doubles reach over chance. The policy question is not whether to use data but which layers to publish: the gap between the best and worst informed rule is ${R.demand.owners - R.headroom.owners} owners for the same budget.` }],
    { x: 0.9, y: 5.6, w: 11.5, h: 1.1, fontSize: 15 });
}

// ===================================================================== 15. Ketahanan (grafik)
{
  const s = base("Robustness", "The ordering survives portfolio size, site size and cell size", {
    notes: "a: demand-based rules lead at every portfolio size until the pool is exhausted. b: as sites get larger the demand-only rule places more infeasible sites (2, 3, 6, 12) while demand within headroom gives up more owners (807 to 734) but always stays above headroom-only (694). c: the whole pipeline re-run at four cell sizes, with N set to 38 percent of the pool so the comparison stays fair." });
  img(s, "fig8_robustness.png", 0.5, 1.6, 12.3, 3.75);
  const pts = [["Portfolio size", "Demand-based rules lead headroom-only until every cell in the pool is built."],
               ["Site size", "Bigger sites make demand-only more infeasible (2 → 12 sites); the constraint costs more owners but never falls below headroom-only."],
               ["Cell size", "Demand within headroom reaches 14–32 % more owners than headroom-only at 3, 5, 7 and 10 km."]];
  pts.forEach((p, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 5.5, 3.85, 1.35, LIGHT);
    T(s, [{ text: p[0], options: { bold: true, color: TEAL, breakLine: true } }, { text: p[1], options: { fontSize: 12.5 } }],
      { x: x + 0.2, y: 5.6, w: 3.5, h: 1.2, fontSize: 14 });
  });
}

// ===================================================================== 16. Ketahanan (tabel)
{
  const s = base("Robustness", "What holds at every resolution, and what does not", {
    notes: "Two results are resolution-sensitive and should not be headline numbers: the count of stranded sites (19, 15, 0, 4) and the share of headroom or owners in cells without chargers (falls from 53 to 21 percent and 43 to 5 percent as cells grow). The direction of the main findings holds at every cell size." });
  const hdr = ["Cell size", "Unserved pool", "AUC relative headroom", "ρ relative headroom", "Demand-in-headroom vs headroom-only", "Demand-only infeasible", "Headroom-only stranded"];
  const data = [hdr.map((h, i) => ({ text: h, options: { bold: true, color: WHITE, fill: { color: INK }, fontSize: 12, align: "center", valign: "middle", fontFace: "Calibri" } }))];
  V.forEach((v) => {
    const g = 100 * (v.rules_prop.dwh.owners / v.rules_prop.headroom.owners - 1);
    const row = [`${v.cell.toFixed(3)}° (≈${Math.round(v.cell * 111)} km)`, `${v.pool} cells · N = ${v.n_prop}`, f2(v.f1.auc.rel),
                 (v.f1.rel >= 0 ? "+" : "−") + f2(Math.abs(v.f1.rel)), `+${g.toFixed(0)} %`, String(v.rules_prop.demand.infeas), String(v.rules_prop.headroom.stranded)];
    data.push(row.map((t, i) => ({ text: nb(t), options: { fontSize: 14, align: "center", valign: "middle", fontFace: "Calibri", color: INK,
      fill: { color: v.cell === 0.045 ? TEAL_LT : WHITE }, bold: i === 4 } })));
  });
  data.push([{ text: "Verdict", options: { bold: true, fontSize: 13, fontFace: "Calibri", color: WHITE, fill: { color: TEAL }, valign: "middle" } },
             ...["—", "robust", "robust", "robust", "mostly (3 of 4)", "sensitive"].map((t) => ({ text: t, options: { bold: true, fontSize: 13, fontFace: "Calibri", align: "center", valign: "middle",
               color: t === "sensitive" ? CORAL : TEAL, fill: { color: LIGHT } } }))]);
  s.addTable(data, { x: 0.6, y: 1.6, w: 12.1, colW: [1.7, 1.9, 1.6, 1.5, 2.1, 1.6, 1.7], rowH: [0.75, 0.55, 0.55, 0.55, 0.55, 0.5],
    border: { type: "solid", pt: 0.75, color: "D5DAE0" }, margin: 0.05 });
  T(s, "N is held at 38 % of the unserved pool (50 of 132 at 5 km) so that the rules are compared on the same footing at each resolution.",
    { x: 0.6, y: 5.3, w: 12.1, h: 0.5, fontSize: 13, color: MUTED });
  card(s, 0.6, 5.85, 12.1, 0.95, CORAL_LT);
  T(s, [{ text: "Dropped as headline: ", options: { bold: true, color: CORAL } },
        { text: "\"15 stranded sites\" and \"42 % of headroom in uncharged cells\" are 5 km figures; they change with the grid and are reported as such." }],
    { x: 0.9, y: 5.98, w: 11.5, h: 0.75, fontSize: 14 });
}

// ===================================================================== 17. Dua tingkat
{
  const s = base("Findings", "Transformer and substation headroom are unrelated, so both levels must be published", {
    notes: `Among ${TW.n} served cells linked to a GI, Spearman rho between transformer headroom and GI headroom is ${f2(TW.rho)} (95 percent CI ${TW.rho_ci[0]} to ${TW.rho_ci[1]}). Median splits give ${TW.tight_tr_ample_gi} + ${TW.ample_tr_tight_gi} discordant cells (${f1(TW.discord)} percent), close to the 50 percent expected under independence. The earlier draft's 51 percent was not reproducible; the underlying claim is stronger stated as independence.` });
  img(s, "fig9_two_levels.png", 0.6, 1.5, 6.4, 5.3);
  stat(s, 7.4, 1.7, 5.3, 1.6, `ρ = ${TW.rho >= 0 ? "+" : "−"}${f2(Math.abs(TW.rho))}`, `95 % CI ${TW.rho_ci[0]} to +${TW.rho_ci[1]}, n = ${TW.n} served cells`, CORAL, CORAL_LT);
  T(s, [{ text: "Why it matters for the map", options: { bold: true, breakLine: true } },
        { text: "Low-voltage only: tells a developer to avoid cells where a new dedicated transformer on a lightly loaded feeder is cheap.", options: { bullet: true, breakLine: true } },
        { text: "Substation only: hides that the last few hundred metres of network are saturated.", options: { bullet: true, breakLine: true } },
        { text: `${f1(TW.discord)} % of served cells are tight at one level and ample at the other.`, options: { bullet: true } }],
    { x: 7.4, y: 3.6, w: 5.3, h: 3.2, fontSize: 15, paraSpaceAfter: 6 });
}

// ===================================================================== 18. Kesiapan data
{
  const s = base("Findings", "The load register is not publication-ready, and ageing cuts substation headroom by up to half", {
    notes: `Shares are of all ${f0(D.meta.total)} records. At 3.0 percent per year, ${f0(D.scen[1].over)} transformers (17 percent of usable records) pass the 80 percent limit; at 9.7 percent per year GI headroom falls by about half. Field-staff names appear in ${f1(D.audit.pii)} percent of records and must be stripped before anything is published.` });
  img(s, "fig10_readiness.png", 0.5, 1.6, 12.3, 4.2);
  T(s, `At 3.0 %/yr, ${f0(D.scen[1].over)} transformers (17 % of usable records) pass the 80 % limit. Headroom falls from ${f0(D.scen[0].trafo)} to ${f0(D.scen[1].trafo)} MVA (transformers) and ${f0(D.scen[0].gi)} to ${f0(D.scen[1].gi)} MVA (GI).`,
    { x: 0.6, y: 6.0, w: 12.1, h: 0.7, fontSize: 14 });
}

// ===================================================================== 19. Ledger klaim
{
  const s = base("Implications", "Claims ledger: what the evidence supports after testing", {
    notes: "This slide is the honest summary for reviewers. Green: survives every test. Amber: true at 5 km, direction holds, magnitude depends on grid. Red: revised from the earlier draft." });
  const rows = [
    ["Roll-out follows grid density, not spare capacity", "AUC 0.86 vs 0.46; ρ rel CI spans 0; all cell sizes", "Robust", TEAL],
    ["High-demand / low-headroom cells are under-served", "owners' share 1.4–2.6× chargers' share at all cell sizes", "Robust", TEAL],
    ["Headroom-only reaches fewer owners", "demand within headroom reaches 14–32 % more at every cell size; beyond all random draws", "Robust", TEAL],
    ["Headroom-only fails the poorest regencies", "+5.1 vs +18.0 points in the poorest third; lowest CI for demand within headroom", "New, supported", TEAL],
    ["Headroom-only strands 30 % of sites", "19 / 15 / 0 / 4 stranded at 3 / 5 / 7 / 10 km", "Resolution-sensitive", AMBER],
    ["Demand-only places infeasible sites", "2 → 12 as site size grows; 10 / 3 / 2 / 0 by cell size", "Mostly robust", AMBER],
    ["Demand within headroom lowers regency Gini most", "random has the lowest Gini; old Gini used 47 mixed labels", "Revised", CORAL],
    ["51 % of cells discordant between levels", "re-derived: 44.6 %, ρ = −0.02 (independence)", "Restated", AMBER],
  ];
  const data = [["Claim", "Evidence", "Status"].map((h) => ({ text: h, options: { bold: true, color: WHITE, fill: { color: INK }, fontSize: 13, fontFace: "Calibri", valign: "middle" } }))];
  rows.forEach((r) => data.push([
    { text: r[0], options: { fontSize: 13, fontFace: "Calibri", color: INK, valign: "middle", bold: true } },
    { text: nb(r[1]), options: { fontSize: 12, fontFace: "Calibri", color: INK, valign: "middle" } },
    { text: r[2], options: { fontSize: 13, fontFace: "Calibri", bold: true, color: WHITE, fill: { color: r[3] }, align: "center", valign: "middle" } }]));
  s.addTable(data, { x: 0.6, y: 1.55, w: 12.1, colW: [4.4, 5.6, 2.1], rowH: 0.56, border: { type: "solid", pt: 0.75, color: "D5DAE0" }, margin: 0.06 });
}

// ===================================================================== 20. Standar minimum
{
  const s = base("Implications", "Five requirements make a capacity map publishable", {
    notes: "Each requirement is tied to a finding: two levels (independence of levels), growth correction (ageing), a demand layer (income equity result), aggregation (staff names and customer labels), and a quality score (register readiness)." });
  const items = [
    ["Two network levels", "Transformer and primary substation at least; feeder where available.", "levels are unrelated: ρ ≈ 0"],
    ["Growth correction", "A stated rate and survey date for every value.", "GI headroom −20 % at 3 %/yr"],
    ["A demand layer", "Registered EV customers or predicted energy next to headroom.", "+18 vs +5 pts for the poorest third"],
    ["Spatial aggregation", "5 km cells (or 2 km hexagons) to protect people and assets.", `${f1(D.audit.pii)} % of records name staff`],
    ["Versioning + quality score", "So a map that misdirects capital can be corrected.", "44 % of records lack a GI link"],
  ];
  items.forEach((it, i) => {
    const y = 1.6 + i * 1.03;
    card(s, 0.6, y, 12.1, 0.88, i % 2 ? WHITE : LIGHT);
    circleNum(s, 0.8, y + 0.15, 0.58, String(i + 1));
    T(s, it[0], { x: 1.6, y: y + 0.08, w: 3.2, h: 0.72, fontSize: 17, bold: true, valign: "middle" });
    T(s, it[1], { x: 4.9, y: y + 0.08, w: 4.6, h: 0.72, fontSize: 14, valign: "middle" });
    T(s, it[2], { x: 9.6, y: y + 0.08, w: 2.95, h: 0.72, fontSize: 13, color: TEAL, bold: true, valign: "middle" });
  });
  T(s, "Evidence →", { x: 9.6, y: 1.25, w: 2.9, h: 0.3, fontSize: 11, color: MUTED });
}

// ===================================================================== 21. Pengganti unbundling
{
  const s = base("Implications", "Publishing the two-surface map is a functional substitute for unbundling", {
    notes: "Europe separates the DSO from charging because the DSO would hold this information. Indonesia chose integration. Publication removes the asymmetry without changing ownership, and it steers private capital toward the gaps." });
  const boxes = [["Information asymmetry", "PLN can site its own chargers using headroom and demand data that third-party CPOs do not have.", CORAL, CORAL_LT],
                 ["Publish both surfaces", "Headroom and demand, at two network levels, open to every applicant. Ownership does not change.", TEAL, TEAL_LT],
                 ["Capital steered to gaps", "Public and private investment points at unserved high-demand cells, including in poorer regencies.", INK, LIGHT]];
  boxes.forEach((b, i) => {
    const x = 0.6 + i * 4.2;
    card(s, x, 1.8, 3.7, 3.4, b[3]);
    circleNum(s, x + 0.25, 2.05, 0.6, String(i + 1), b[2]);
    T(s, b[0], { x: x + 0.25, y: 2.85, w: 3.2, h: 0.6, fontSize: 19, bold: true });
    T(s, b[1], { x: x + 0.25, y: 3.5, w: 3.2, h: 1.6, fontSize: 14 });
    if (i < 2) arrow(s, x + 3.75, 3.35, 0.4);
  });
  card(s, 0.6, 5.5, 12.1, 1.25, LIGHT);
  T(s, "EU DSOs are generally barred from owning charge points because of this advantage. Where the DSO is also the CPO, disclosure has to do the work that separation does in Europe.",
    { x: 0.9, y: 5.65, w: 11.5, h: 1.0, fontSize: 15, color: MUTED });
}

// ===================================================================== 22. Roadmap (usulan)
{
  const s = base("Implications", "A phased path to publication (proposed, for discussion with PLN UID Jawa Barat)", {
    notes: "This is a proposal derived from the findings, not an agreed plan. The order matters: cleaning first, because publishing an unclean register would misdirect capital and expose staff names." });
  const ph = [["Phase 0", "Clean", [`Strip staff names (${f1(D.audit.pii)} %)`, "Link records to GI (44 % missing)", "Reconcile coordinates (43 % > 1 km)"], AMBER],
              ["Phase 1", "Publish two surfaces", ["5 km cells, transformer + GI", "Growth-corrected, dated", "Owner counts as demand layer"], TEAL],
              ["Phase 2", "Deepen", ["Add feeder level (2,574 feeders)", "Quarterly versions", "Published quality score"], "3D6E8F"],
              ["Phase 3", "Close the loop", ["Link map to connection requests", "Track where sites go", "Monitor poorest-third coverage"], INK]];
  ph.forEach((p, i) => {
    const x = 0.6 + i * 3.08;
    s.addShape(pres.shapes.CHEVRON, { x, y: 1.75, w: 2.95, h: 0.8, fill: { color: p[3] }, line: { color: p[3] } });
    T(s, `${p[0]} · ${p[1]}`, { x: x + 0.5, y: 1.75, w: 2.15, h: 0.8, fontSize: 14, bold: true, color: WHITE, valign: "middle" });
    card(s, x, 2.8, 2.85, 2.5, LIGHT);
    T(s, p[2].map((t, j) => ({ text: nb(t), options: { bullet: true, breakLine: j < p[2].length - 1 } })),
      { x: x + 0.15, y: 3.0, w: 2.6, h: 2.2, fontSize: 14, paraSpaceAfter: 10 });
  });
  T(s, "Success measure: coverage in the poorest third of regencies rises at least as fast as in the richest third.",
    { x: 0.6, y: 5.6, w: 12.1, h: 0.6, fontSize: 16, bold: true, color: TEAL });
}

// ===================================================================== 23. Keterbatasan
{
  const s = base("Implications", "What this evidence does and does not show", {
    notes: "Be explicit about the proxy nature of the data. The equity result rests on 272 owners in the poorest third; it is a direction, not a precise estimate." });
  const lim = [
    "Headroom comes from two spot readings per transformer: a planning proxy, not a hosting-capacity calculation.",
    "Registered EV owners proxy latent demand and under-represent households without a home charger.",
    "The poorest third of regencies holds only 272 owners (181 in Kab. Bandung Barat): the equity result is a direction, not a precise estimate.",
    "Growth is province-wide; unit-level rates would sharpen the correction.",
    "Rules assume equal sites; the feeder level (2,574 feeders) is not yet included.",
    "Regency expenditure is an area measure; it does not describe the owners themselves.",
  ];
  T(s, lim.map((t, i) => ({ text: nb(t), options: { bullet: true, breakLine: i < lim.length - 1 } })),
    { x: 0.6, y: 1.7, w: 12.1, h: 5.0, fontSize: 17, paraSpaceAfter: 12 });
}

// ===================================================================== 24. Penutup
{
  n += 1;
  const s = pres.addSlide({ sectionTitle: sec("Close") });
  s.background = { color: INK };
  T(s, "The capacity map is a planning decision disguised as a data product.", { x: 0.8, y: 1.3, w: 11.7, h: 1.4, fontSize: 32, bold: true, color: WHITE });
  const pts = [
    `Headroom alone ranks the strong grid first: ${R.headroom.owners} owners reached, +${f1(R.headroom.terc[0] - B.baseline.terc[0])} points for the poorest third.`,
    `Headroom with demand reaches ${R.dwh.owners}, connects every site, and adds +${f1(R.dwh.terc[0] - B.baseline.terc[0])} points for the poorest third.`,
    "Both network levels, growth-corrected and quality-scored, can be built from data every DSO already holds.",
  ];
  T(s, pts.map((t, i) => ({ text: nb(t), options: { bullet: true, breakLine: i < pts.length - 1 } })),
    { x: 0.8, y: 3.0, w: 11.5, h: 2.8, fontSize: 19, color: SOFT, paraSpaceAfter: 14 });
  T(s, "Qashtalani Haramaini · Alyas Widita · Liz Taylor", { x: 0.8, y: 6.4, w: 11.5, h: 0.4, fontSize: 14, color: AMBER });
  s.addNotes("Close on the policy point: publication substitutes for unbundling. Then the claims ledger can be shown again during questions.");
}

pres.writeFile({ fileName: OUT }).then(async (f) => {
  if (THEME_JS) { await require(THEME_JS).applyTheme(OUT, THEME); }
  console.log("written", f, "slides", n);
});
