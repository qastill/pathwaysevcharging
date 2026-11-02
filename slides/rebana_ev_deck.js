// Builds slides/Rebana_EV_Charging_ur-scape.pptx (English deck for the 2nd Powering Rebana Workshop).
// Numbers come from analysis/rebana_insights.html (computed from analysis/rebana_data.json and ttm/ttm.json).
// Usage: NODE_PATH=<dir with pptxgenjs> node slides/rebana_ev_deck.js <dir with screenshot jpgs> <out.pptx>
const pptxgen = require("pptxgenjs");
const path = require("path");
const IMG = process.argv[2] || "img";
const OUT = process.argv[3] || "Rebana_EV_Charging_ur-scape.pptx";

const THEME = { name: "Rebana EV", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "13263A", lt1: "FFFFFF", dk2: "0E1B26", lt2: "EEF1F4", accent1: "C97D0E", accent2: "0F9A96",
            accent3: "7B5EA7", accent4: "C0392B", accent5: "1E8E5A", accent6: "55606E", hlink: "0F7E7B", folHlink: "7B5EA7" } };
const H = THEME.colors;
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";                       // 13.33 x 7.5 in
pres.author = "Qashtalani Haramaini";
pres.company = "Monash University Indonesia";
pres.title = "EV charging in Rebana: access, equity and grid readiness";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const FOOT = "Qashtalani Haramaini · Monash University Indonesia · 2nd Powering Rebana Workshop, Cirebon, 5–6 Nov 2026";

pres.defineSlideMaster({ title: "TITLE_DARK", background: { color: H.dk2 },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.7, y: 1.9, w: 11.9, h: 2.0, fontSize: 40, bold: true, color: "FFFFFF", fontFace: "Cambria", valign: "bottom", align: "left" }, text: "" } },
            { placeholder: { options: { name: "body", type: "body", x: 0.7, y: 4.1, w: 11.9, h: 1.6, fontSize: 18, color: "C9D3DC", fontFace: "Calibri", valign: "top", align: "left" }, text: "" } }] });
pres.defineSlideMaster({ title: "CONTENT", background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.95, fontSize: 30, bold: true, color: H.dk1, fontFace: "Cambria", valign: "middle", align: "left" }, text: "" } },
            { text: { text: FOOT, options: { x: 0.6, y: 7.02, w: 10.5, h: 0.3, fontSize: 10, color: "6B7683", fontFace: "Calibri" } } }],
  slideNumber: { x: 12.2, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: "6B7683", align: "right" } });

const chartText = { catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt", legendFontFace: "+mn-lt",
  catAxisLabelColor: "333F4B", valAxisLabelColor: "6B7683", dataLabelColor: "13263A", catAxisLabelFontSize: 12, valAxisLabelFontSize: 10, dataLabelFontSize: 11,
  valGridLine: { color: "E3E6EA", size: 0.75 }, catGridLine: { style: "none" }, titleColor: "13263A", titleFontSize: 13 };
const T = (s, o) => Object.assign({ isTextBox: true, fontFace: "Calibri", color: H.dk1, fontSize: 14, margin: 0, valign: "top" }, o, { text: undefined });
function text(slide, s, o) { slide.addText(s, T(s, o)); }
function card(slide, x, y, w, h, name, fill = "F2F4F6") { slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.08, objectName: name }); }
function stat(slide, x, y, w, big, small, col) {
  card(slide, x, y, w, 1.55, "stat " + big);
  text(slide, big, { x: x + 0.22, y: y + 0.16, w: w - 0.44, h: 0.7, fontSize: 34, bold: true, color: col, fontFace: "Cambria" });
  text(slide, small, { x: x + 0.22, y: y + 0.86, w: w - 0.44, h: 0.6, fontSize: 13, color: "45505C" });
}
function section(t) { pres.addSection({ title: t }); return t; }

// 1 ---------------------------------------------------------------- title
let sec = section("Opening");
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: sec });
s.addText("EV charging in Rebana: who can charge, who cannot, and is the grid ready?", { placeholder: "title" });
s.addText([{ text: "Qashtalani Haramaini · PhD candidate, Monash University Indonesia (RACE for 2030)", options: { breakLine: true } },
           { text: "2nd Powering Rebana Workshop · Cirebon, 5–6 November 2026", options: { breakLine: true } },
           { text: "All layers are also available in ur-scape, the workshop's shared visualisation platform" }], { placeholder: "body" });
s.addNotes("Purpose: show what the existing data says about EV charging in Rebana, and share the same layers in ur-scape so the workshop group can explore them together. Every number comes from the repo pathwaysevcharging and can be inspected cell by cell.");

// 2 ---------------------------------------------------------------- key message
sec = section("Findings");
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
s.addText("Rebana charges the cars passing through, not the cars of people who live there", { placeholder: "title" });
stat(s, 0.6, 1.6, 2.9, "73 %", "of Rebana's charging energy is sold at 19 toll-road rest areas", H.accent1);
stat(s, 3.67, 1.6, 2.9, "29 %", "of residents live within a 10-minute drive of a charger (Jabodetabek 76 %)", H.accent3);
stat(s, 6.74, 1.6, 2.9, "1.04 M", "residents (11 %) are more than 30 minutes from any charger", H.accent4);
stat(s, 9.81, 1.6, 2.9, "−15 MVA", "headroom at Sunyaragi substation, which supplies Kota Cirebon", H.accent4);
card(s, 0.6, 3.5, 12.1, 2.75, "summary card", "EEF6F6");
s.addText([
  { text: "Access is uneven and follows density, not need. ", options: { bold: true } }, { text: "The sparsest fifth of villages has 5 % of residents within 10 minutes; the densest fifth has 70 %.", options: { breakLine: true } },
  { text: "Grid capacity exists, but in the wrong places. ", options: { bold: true } }, { text: "Haurgeulis, Cikedung and Arjawinangun Baru substations have 56–69 % headroom and almost no chargers.", options: { breakLine: true } },
  { text: "Because Rebana is still being built, siting can be decided before demand forms. ", options: { bold: true } }, { text: "The village travel-time method becomes an ex-ante planning tool, not an audit." }],
  { x: 0.95, y: 3.75, w: 11.4, h: 2.3, fontSize: 17, color: H.dk1, isTextBox: true, paraSpaceAfter: 12, valign: "top", margin: 0 });
s.addNotes("One sentence to remember: Rebana's chargers serve through-traffic on the Cipali–Palikanci toll road. Residents, especially outside the cities, are barely served, while the substations with spare capacity sit where there are no chargers.");

// 3 ---------------------------------------------------------------- context table
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
s.addText("Seven regencies, 9.2 million people, and a metropolitan area still under construction", { placeholder: "title" });
const hdr = ["Area", "Population (M)", "Industrial zones (KPI)", "Investment 2025 (Rp T)", "Chargers per 100k"].map(t => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: H.dk1 } } }));
const rows = [["Kab. Cirebon", "2.45", "1", "4.01", "2.49"], ["Kab. Indramayu", "1.95", "6", "3.35", "1.06"], ["Kab. Subang", "1.66", "3", "18.2", "1.20"],
  ["Kab. Majalengka", "1.36", "3", "3.36", "1.74"], ["Kab. Kuningan", "1.24", "0", "–", "1.16"], ["Kab. Sumedang", "1.17", "0", "5.63", "1.30"], ["Kota Cirebon", "0.36", "0", "–", "1.96"]];
s.addTable([hdr, ...rows.map((r, i) => r.map((c, j) => ({ text: c, options: { align: j ? "right" : "left", fill: { color: i % 2 ? "FFFFFF" : "F4F6F8" } } })))],
  { x: 0.6, y: 1.55, w: 7.6, colW: [2.0, 1.3, 1.5, 1.5, 1.3], fontSize: 13, fontFace: "Calibri", color: H.dk1, border: { type: "solid", pt: 0.5, color: "DDE2E7" }, rowH: 0.42 });
card(s, 8.6, 1.55, 4.1, 3.5, "context card", "F7F1E6");
s.addText([{ text: "Rp 36.7 T", options: { bold: true, fontSize: 28, color: H.accent1, fontFace: "Cambria", breakLine: true } },
  { text: "investment in 2025 (BKPM via BP Rebana)", options: { fontSize: 13, color: "45505C", breakLine: true } },
  { text: " ", options: { fontSize: 8, breakLine: true } },
  { text: "13 industrial zones", options: { bold: true, fontSize: 20, color: H.dk1, breakLine: true } },
  { text: "largest: Cipali Subang Barat 10,408 ha, Losarang 6,170 ha", options: { fontSize: 13, color: "45505C", breakLine: true } },
  { text: " ", options: { fontSize: 8, breakLine: true } },
  { text: "1.78 M jobs targeted by 2030", options: { bold: true, fontSize: 20, color: H.dk1, breakLine: true } },
  { text: "plus Kertajati airport and Patimban port", options: { fontSize: 13, color: "45505C" } }],
  { x: 8.9, y: 1.75, w: 3.5, h: 3.2, isTextBox: true, margin: 0, valign: "top" });
s.addText("Sources: Kontur 2023, BPS 2024, BKPM/BP Rebana; chargers: PLN Charge.IN", { x: 0.6, y: 5.15, w: 7.6, h: 0.3, fontSize: 10, color: "6B7683", isTextBox: true, margin: 0 });
s.addNotes("Indramayu has six industrial zones and the most substation headroom, yet the fewest chargers per resident. Subang received half of 2025 investment.");

// 4 ---------------------------------------------------------------- charging today (bar chart)
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
s.addText("Charging today follows the toll corridor, not the towns", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "MWh, March 2026", labels: ["Toll rest areas (19)", "PLN offices (22)", "F&B / cafés (4)", "Public / government (3)", "Hotels (6)", "Malls / retail (4)", "Housing (1)", "Tourism (2)"],
  values: [255, 67, 6.9, 5.9, 5.0, 3.2, 1.4, 1.1] }], Object.assign({}, chartText, { x: 0.6, y: 1.5, w: 7.6, h: 5.2, barDir: "bar", catAxisOrientation: "maxMin",
  chartColors: [H.accent1], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.#", showLegend: false, showTitle: true, title: "Energy sold by location type, MWh (March 2026)", valAxisHidden: true, barGapWidthPct: 45 }));
stat(s, 8.6, 1.6, 4.1, "13,691", "charging sessions in March 2026, 13.6 % of West Java", H.dk1);
stat(s, 8.6, 3.35, 4.1, "60 %", "of sessions at chargers of 100 kW or more", H.accent1);
stat(s, 8.6, 5.1, 4.1, "< 100", "EVs registered by Rebana residents", H.accent4);
s.addNotes("Five sites (KM 166 A, CSE UP3 Cirebon, KM 164 B, KM 229 B, KM 101 B) sell 42 % of Rebana's energy. Daily peak is 13:00–17:00, a travel pattern, not a commuting pattern. Majalengka and Subang look busy only because the Cipali rest areas fall inside their borders.");

// 5 ---------------------------------------------------------------- access chart
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
s.addText("Fewer than three in ten residents can reach a charger in 10 minutes", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Share within 10 min", labels: ["Kota Cirebon", "Jabodetabek", "West Java", "Kab. Cirebon", "Kab. Kuningan", "Kab. Sumedang", "Rebana", "Kab. Subang", "Kab. Indramayu", "Kab. Majalengka"],
  values: [78, 76, 46, 39, 30, 30, 28.6, 19, 19, 19] }], Object.assign({}, chartText, { x: 0.6, y: 1.5, w: 7.8, h: 5.2, barDir: "bar", catAxisOrientation: "maxMin",
  chartColors: ["0F9A96", "7B5EA7", "7B5EA7", "0F9A96", "0F9A96", "0F9A96", "C97D0E", "0F9A96", "0F9A96", "0F9A96"], invertedColors: undefined,
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"%"', showLegend: false, showTitle: true, title: "Residents within a 10-minute drive of a public charger (%)", valAxisHidden: true, valAxisMaxVal: 90, barGapWidthPct: 40 }));
card(s, 8.8, 1.6, 3.9, 5.0, "method card", "F2F4F6");
s.addText([{ text: "How it is measured", options: { bold: true, fontSize: 16, breakLine: true } },
  { text: "Car travel time on the OSM road network (r5r village-to-village matrix, 60-minute cap, by Alyas Widita) from each of 1,981 Rebana villages to the nearest village with a public charger (1,556 sites, PLN Charge.IN June 2026), weighted by Kontur 2023 population.", options: { fontSize: 13, color: "45505C", breakLine: true } },
  { text: " ", options: { fontSize: 8, breakLine: true } },
  { text: "Within 30 minutes: 88.8 %", options: { bold: true, fontSize: 15, breakLine: true } },
  { text: "Kuningan and Sumedang each have about 250,000 residents beyond 30 minutes.", options: { fontSize: 13, color: "45505C" } }],
  { x: 9.05, y: 1.85, w: 3.4, h: 4.6, isTextBox: true, margin: 0, valign: "top" });
s.addNotes("Kota Cirebon is well served at 78 %. The three north-coast regencies, Subang, Indramayu and Majalengka, sit at 19 %, where most industrial zones are planned.");

// 6 ---------------------------------------------------------------- equity and ladder
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
s.addText("The gap is rural versus urban, and the service ladder stops at the first rung", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Within 10 min", labels: ["Q1 sparsest", "Q2", "Q3", "Q4", "Q5 densest"], values: [5.4, 10.7, 19.7, 37.6, 69.5] }],
  Object.assign({}, chartText, { x: 0.6, y: 1.5, w: 6.0, h: 4.6, barDir: "col", chartColors: [H.accent2], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"%"',
  showLegend: false, showTitle: true, title: "Within 10 minutes, by village density fifth", valAxisHidden: true, valAxisMaxVal: 80, barGapWidthPct: 50 }));
s.addChart(pres.charts.DOUGHNUT, [{ name: "Service ladder", labels: ["No charger within 10 min", "Reachable, capacity short", "Reachable and sufficient"], values: [71.4, 27.1, 1.5] }],
  Object.assign({}, chartText, { x: 6.9, y: 1.5, w: 5.8, h: 4.6, chartColors: [H.accent4, H.accent1, H.accent5], holeSize: 58, showPercent: false, showValue: true, dataLabelFormatCode: '0.#"%"',
  dataLabelColor: "FFFFFF", showLegend: true, legendPos: "b", legendFontSize: 12, showTitle: true, title: "Service ladder: share of Rebana residents" }));
s.addText("Concentration index of 15-minute access against density is 0.31; against spending per person only 0.08. Inequality here is rural–urban, not rich–poor, and can still be prevented. Sufficiency = E2SFCA charger kW within 10 minutes ≥ 0.03 kW per household.",
  { x: 0.6, y: 6.2, w: 12.1, h: 0.7, fontSize: 13, color: "45505C", isTextBox: true, margin: 0 });
s.addNotes("Quintile values from analysis/rebana_data.json (eq.rebana.quint), each fifth about 1.84 M residents. Rebana does not yet have a capacity problem, it has an existence problem.");

// 7 ---------------------------------------------------------------- grid
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
s.addText("Grid headroom exists where chargers do not", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Headroom MVA", labels: ["Kab. Indramayu", "Kab. Majalengka", "Kab. Cirebon", "Kab. Sumedang", "Kab. Kuningan", "Kab. Subang", "Kota Cirebon"], values: [120.6, 79.4, 77.5, 58.4, 20.4, 11.2, -15.1] }],
  Object.assign({}, chartText, { x: 0.6, y: 1.5, w: 6.6, h: 5.2, barDir: "bar", catAxisOrientation: "maxMin", chartColors: ["0F9A96", "0F9A96", "0F9A96", "0F9A96", "0F9A96", "0F9A96", "C0392B"], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0",
  showLegend: false, showTitle: true, title: "Substation headroom by area, MVA (capacity minus reported peak)", valAxisHidden: true, valAxisMinVal: -40, catAxisLabelPos: "low", barGapWidthPct: 40 }));
card(s, 7.6, 1.6, 5.1, 2.35, "risk 1", "FBEDEB");
s.addText([{ text: "Risk 1 · saturated towns", options: { bold: true, fontSize: 16, color: H.accent4, breakLine: true } },
  { text: "Sunyaragi (Kota Cirebon) is at 86 % of peak, Subang at 89.5 %, Indramayu and Jatibarang above 80 %. Fast chargers there add midday peak to full substations.", options: { fontSize: 14, color: "333F4B" } }],
  { x: 7.85, y: 1.8, w: 4.6, h: 2.0, isTextBox: true, margin: 0 });
card(s, 7.6, 4.2, 5.1, 2.35, "risk 2", "E8F4F3");
s.addText([{ text: "Risk 2 · idle capacity", options: { bold: true, fontSize: 16, color: H.accent2, breakLine: true } },
  { text: "Haurgeulis (69 %), Cikedung (56 %) and Arjawinangun Baru (56 %) serve sub-districts with no charger. Pair new rural sites with these, and daytime solar tariffs in towns.", options: { fontSize: 14, color: "333F4B" } }],
  { x: 7.85, y: 4.4, w: 4.6, h: 2.0, isTextBox: true, margin: 0 });
s.addNotes("Headroom = capacity minus reported peak load, PLN UID Jabar. N-1 and PLN reinforcement plans are not included.");

// 8 ---------------------------------------------------------------- siting
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
s.addText("Two siting models point to the same three places", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Added residents", labels: ["Gegesik (Cirebon)", "Terisi (Indramayu)", "Ciasem (Subang)", "Jatinunggal (Sumedang)", "Pusakajaya (Subang)", "Tanjungsiang (Subang)", "Dukupuntang (Cirebon)"], values: [432, 256, 220, 208, 206, 174, 168] }],
  Object.assign({}, chartText, { x: 0.6, y: 1.5, w: 6.9, h: 5.2, barDir: "bar", catAxisOrientation: "maxMin", chartColors: [H.accent5], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"k"',
  showLegend: false, showTitle: true, title: "Coverage model: residents added within 10 km per new site (thousands)", valAxisHidden: true, barGapWidthPct: 40 }));
card(s, 7.9, 1.6, 4.8, 2.6, "model card", "F2F4F6");
s.addText([{ text: "Model A · siting priority score", options: { bold: true, fontSize: 15, breakLine: true } },
  { text: "0.5 × need (travel time, distance) + 0.25 × demand (log population) + 0.25 × readiness (substation headroom). Top: Pusakanagara 67.0, Cibingbin 65.9, Krangkeng 65.9, Losari 65.2, Gegesik 63.2.", options: { fontSize: 13, color: "45505C" } }],
  { x: 8.15, y: 1.8, w: 4.3, h: 2.3, isTextBox: true, margin: 0 });
card(s, 7.9, 4.45, 4.8, 2.25, "converge card", "E9F5EE");
s.addText([{ text: "Both models meet at Gegesik, Terisi and Pusakanagara–Pusakajaya", options: { bold: true, fontSize: 15, color: H.accent5, breakLine: true } },
  { text: "One 4-gun station in Gegesik adds 432,000 residents to the 10 km radius, more than all new chargers in 2026 combined. Twelve sites lift coverage from 67 % to about 90 %.", options: { fontSize: 13, color: "333F4B" } }],
  { x: 8.15, y: 4.65, w: 4.3, h: 2.0, isTextBox: true, margin: 0 });
s.addNotes("Weights in model A are illustrative; use the ranking as a discussion order, not a decision. Model B is a greedy maximal-coverage pick at kecamatan level starting from 66.9 % coverage.");

// 9 ---------------------------------------------------------------- ur-scape intro
sec = section("ur-scape");
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
s.addText("The same evidence in ur-scape, the workshop's shared platform", { placeholder: "title" });
s.addImage({ path: path.join(IMG, "01_hdi.jpg"), x: 0.6, y: 1.45, w: 8.0, h: 8.0 * 1301 / 2000, altText: "ur-scape showing the West Java site with Rebana layers and an inspection line", objectName: "ur-scape screenshot" });
card(s, 8.95, 1.45, 3.75, 5.2, "package card", "F2F4F6");
s.addText([{ text: "28 layers, one site", options: { bold: true, fontSize: 18, breakLine: true } },
  { text: "Site \"West Java\", 0.5 arc-minute cells (about 0.9 km), no QGIS needed.", options: { fontSize: 13, color: "45505C", breakLine: true } },
  { text: " ", options: { fontSize: 6, breakLine: true } },
  { text: "EV Charging", options: { bold: true, fontSize: 14, color: H.accent3, breakLine: true } }, { text: "stations, energy, utilisation, travel time, access class, service ladder", options: { fontSize: 12, color: "45505C", breakLine: true } },
  { text: "Society and Economy", options: { bold: true, fontSize: 14, color: H.accent1, breakLine: true } }, { text: "density, Rebana HDI, poverty, expenditure, distances", options: { fontSize: 12, color: "45505C", breakLine: true } },
  { text: "Power Grid", options: { bold: true, fontSize: 14, color: H.accent2, breakLine: true } }, { text: "substations, peak loading, power plants, transmission", options: { fontSize: 12, color: "45505C", breakLine: true } },
  { text: "Insights", options: { bold: true, fontSize: 14, color: H.accent4, breakLine: true } }, { text: "siting priority, access gap, coverage picks, KPI kecamatan, transformer overload", options: { fontSize: 12, color: "45505C" } }],
  { x: 9.2, y: 1.7, w: 3.3, h: 4.8, isTextBox: true, margin: 0, valign: "top" });
s.addNotes("Install: unzip the package and run install.py with the path to ur-scape's Data folder, or copy Sites/West Java and append layers_add.csv and citations_add.csv. Download link on the last slide.");

// 10 --------------------------------------------------------------- inspection line
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
s.addText("Reading one line across Rebana with the ur-scape Inspector", { placeholder: "title" });
s.addImage({ path: path.join(IMG, "04_substation_capacity.jpg"), x: 0.6, y: 1.45, w: 6.6, h: 6.6 * 1301 / 2000, altText: "ur-scape inspection line with substation capacity points", objectName: "inspector screenshot" });
const ih = ["Layer along the 313 km line", "Min", "Median", "Mean", "Max"].map(t => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: H.dk1 } } }));
const ir = [["Population density (people/km²)", "124", "700", "1,628", "13,733"], ["Charger siting priority (0–100)", "16.1", "42.1", "39.7", "56.1"]];
s.addTable([ih, ...ir.map(r => r.map((c, j) => ({ text: c, options: { align: j ? "right" : "left" } })))], { x: 7.5, y: 1.5, w: 5.2, colW: [2.2, 0.7, 0.8, 0.75, 0.75], fontSize: 12, fontFace: "Calibri", color: H.dk1, border: { type: "solid", pt: 0.5, color: "DDE2E7" }, rowH: 0.45 });
s.addText([{ text: "What the line shows", options: { bold: true, fontSize: 15, breakLine: true } },
  { text: "Density along the line is skewed: median 700 but mean 1,628 people per km². A few town cells hold most residents.", options: { bullet: true, breakLine: true } },
  { text: "Siting priority ranges from 16 to 56 (median 42). The profile graph under the map shows where along the line it rises.", options: { bullet: true, breakLine: true } },
  { text: "The line crosses industrial-zone (KPI) sub-districts at 200 sample points.", options: { bullet: true, breakLine: true } },
  { text: "42–53 % of the line has no data because Rebana-only layers stop at the Rebana border.", options: { bullet: true } }],
  { x: 7.5, y: 3.15, w: 5.2, h: 3.6, fontSize: 13, color: "333F4B", isTextBox: true, margin: 0, paraSpaceAfter: 6, valign: "top" });
s.addNotes("Screenshots taken in ur-scape v0.9.96 with the West Java site. The inspector summary is for the selected line only; sums and means are not meaningful for percentage layers, as ur-scape itself notes.");

// 11 --------------------------------------------------------------- themes
sec = section("Implications");
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec });
s.addText("What this means for the three workshop themes", { placeholder: "title" });
const themes = [["Sustainable mobility & connectivity", H.accent3, "Separate transit charging (toll, working) from resident charging (missing). Measure success as the share of residents within 10 minutes: from 29 % to at least 50 % needs about 12 sites."],
  ["Energy", H.accent2, "Use substation headroom as a siting criterion. Haurgeulis, Cikedung, Arjawinangun Baru and Kadipaten can absorb 10–20 MW of chargers without reinforcement; towns need daytime time-of-use."],
  ["Skills", H.accent1, "1.78 M jobs by 2030 and 10,000 ha of industrial land in west Subang will move demand to the north coast, where access is 19 %. Plan chargers, transformers and technician training by the KPI map."]];
themes.forEach((t, i) => { const x = 0.6 + i * 4.1; card(s, x, 1.6, 3.85, 4.1, "theme " + t[0], "F4F6F8");
  s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: 1.9, w: 0.55, h: 0.55, fill: { color: t[1] }, line: { color: t[1] }, objectName: "theme dot " + (i + 1) });
  text(s, String(i + 1), { x: x + 0.3, y: 1.9, w: 0.55, h: 0.55, fontSize: 18, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  text(s, t[0], { x: x + 0.3, y: 2.6, w: 3.3, h: 0.8, fontSize: 17, bold: true, fontFace: "Cambria" });
  text(s, t[2], { x: x + 0.3, y: 3.45, w: 3.3, h: 2.2, fontSize: 14, color: "45505C" }); });
card(s, 0.6, 5.95, 12.1, 0.85, "equity card", "F7F1E6");
text(s, "Equity: spending-based concentration is close to zero, so a class gap has not formed yet. Kuningan and Sumedang, with no industrial zones, will be served last if siting follows the market.", { x: 0.85, y: 6.08, w: 11.6, h: 0.65, fontSize: 13, color: "333F4B", valign: "middle" });
s.addNotes("These map directly to ur-scape layers: Travel Time, Population Beyond 30 min, Coverage Model Picks (mobility); Substation Peak Loading, Rebana Substation Headroom (energy); Rebana KPI Kecamatan, Transformer Overload Share (skills).");

// 12 --------------------------------------------------------------- next steps / downloads
s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: sec });
s.addText("Next steps and open data", { placeholder: "title" });
s.addText([{ text: "Data that would sharpen the ex-ante analysis: monthly EV registrations by sub-district (Samsat), charger commissioning dates, and the 20 kV network plan for the industrial zones.", options: { breakLine: true } },
  { text: " ", options: { fontSize: 8, breakLine: true } },
  { text: "Report, slides and ur-scape package: jabar-ev.vercel.app/analysis/rebana_insights.html", options: { bold: true, color: "F2C46D", breakLine: true } },
  { text: "Code and data: github.com/qastill/pathwaysevcharging" }], { placeholder: "body" });
s.addNotes("Invite the group to add their own layers to the same ur-scape site so the workshop has one shared evidence base.");

pres.writeFile({ fileName: OUT }).then(f => console.log("wrote", f));
