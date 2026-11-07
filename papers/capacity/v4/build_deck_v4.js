// Deck v4 "Capacity maps as an equity instrument": ilustratif, infografis, beranimasi.
// Elemen beranimasi diberi objectName "a<langkah><efek>-<nama>"; efek f = fade, u = wipe dari bawah, r = wipe dari kiri.
// papers/capacity/v4/add_animations.py lalu menulis transisi slide dan urutan animasi ke XML.
// Jalankan dari akar repositori:
//   NODE_PATH=<node_modules: pptxgenjs react react-dom react-icons sharp> node papers/capacity/v4/build_deck_v4.js out.pptx
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const RDS = require("react-dom/server");
const sharp = require("sharp");
const Fa = require("react-icons/fa");

const ROOT = path.resolve(__dirname, "../../..");
const F3 = path.join(ROOT, "papers/capacity/v3/figs") + "/";
const F4 = path.join(ROOT, "papers/capacity/v4/figs") + "/";
const OUT = process.argv[2] || path.join(ROOT, "slides/Capacity_Maps_Equity_CIRED2027_v4.pptx");
const S = JSON.parse(fs.readFileSync(path.join(ROOT, "papers/capacity/v3/strengthen.json")));
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "papers/capacity/capacity.json")));
const B = S.base, R = B.rules, F1 = B.f1, RD = B.random, TW = B.two, V = S.variants;

const INK = "1B2A3A", TEAL = "0F7C6E", CORAL = "D1495B", AMBER = "E0A526", MUTED = "5E6B79", BLUE = "3D6E8F",
      LIGHT = "F3F5F7", WHITE = "FFFFFF", SOFT = "C9D6E3", TEAL_LT = "E3F1EE", CORAL_LT = "FBE7EA", AMBER_LT = "FBF1DA",
      GREY = "B8BEC6", LINE = "D5DAE0", NIGHT = "13202D";
const THEME = { name: "Capacity Maps Equity", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: INK, lt1: WHITE, dk2: "24404F", lt2: LIGHT, accent1: TEAL, accent2: CORAL, accent3: AMBER,
            accent4: BLUE, accent5: MUTED, accent6: "9DB4C0", hlink: TEAL, folHlink: MUTED } };
const nb = (s) => String(s).replace(/ %/g, " %");
const f1 = (x) => x.toFixed(1), f2 = (x) => x.toFixed(2), f0 = (x) => Math.round(x).toLocaleString("en-US");
const sg = (x) => (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(2);
const gP = (k) => R[k].terc[0] - B.baseline.terc[0];

// ------------------------------------------------------------------ ikon
const ICON_CACHE = {};
async function icon(name, color = WHITE, size = 256) {
  const key = `${name}_${color}`;
  if (ICON_CACHE[key]) return ICON_CACHE[key];
  const Comp = Fa[name];
  if (!Comp) throw new Error("ikon tidak ada: " + name);
  const svg = RDS.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: String(size) }));
  const png = await sharp(Buffer.from(svg)).resize(size, size).png().toBuffer();
  return (ICON_CACHE[key] = "image/png;base64," + png.toString("base64"));
}

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Calibri", bodyFontFace: "Calibri" };
pres.title = "Capacity maps as an equity instrument";
pres.author = "Qashtalani Haramaini, Alyas Widita, Liz Taylor";
let n = 0, cur = null, uid = 0;
const sec = (name) => { if (name !== cur) { pres.addSection({ title: name }); cur = name; } return name; };
const A = (step, eff = "f", tag = "x") => `a${step}${eff}-${tag}-${++uid}`;
const SRC = "Source: PLN UID Jawa Barat internal data (transformer surveys 2020–24, GI register, March 2026 charging log, registered EV customers); BPS 2024. Reproduced by papers/capacity/prepare.py and v3/strengthen.py.";

const T = (s, text, o) => s.addText(typeof text === "string" ? nb(text) : text,
  Object.assign({ fontFace: "Calibri", margin: 0, isTextBox: true, valign: "top", color: INK }, o));
const box = (s, x, y, w, h, fill = LIGHT, o = {}) =>
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, Object.assign({ x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.1 }, o));
async function iconDot(s, x, y, d, name, fill = TEAL, step = null, iconColor = WHITE) {
  const o = step != null ? { objectName: A(step, "f", "dot") } : {};
  s.addShape(pres.shapes.OVAL, Object.assign({ x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } }, o));
  const k = d * 0.52;
  s.addImage(Object.assign({ data: await icon(name, iconColor), x: x + (d - k) / 2, y: y + (d - k) / 2, w: k, h: k },
    step != null ? { objectName: A(step, "f", "ico") } : {}));
}
async function iconBare(s, x, y, d, name, color, step = null) {
  s.addImage(Object.assign({ data: await icon(name, color), x, y, w: d, h: d }, step != null ? { objectName: A(step, "f", "ico") } : {}));
}
const arrowR = (s, x, y, w, color = GREY, step = null) =>
  s.addShape(pres.shapes.RIGHT_ARROW, Object.assign({ x, y, w, h: 0.34, fill: { color }, line: { color } }, step != null ? { objectName: A(step, "r", "arr") } : {}));

function base(section, title, { lead, notes, dark = false } = {}) {
  const s = pres.addSlide({ sectionTitle: sec(section) });
  n += 1;
  s.background = { color: dark ? INK : WHITE };
  T(s, title, { x: 0.6, y: 0.36, w: 12.1, h: 1.0, fontSize: 27, bold: true, color: dark ? WHITE : INK });
  if (lead) T(s, lead, { x: 0.6, y: 1.34, w: 12.1, h: 0.45, fontSize: 15, color: dark ? SOFT : MUTED });
  T(s, SRC, { x: 0.6, y: 7.02, w: 11.3, h: 0.28, fontSize: 8, color: dark ? "8FA3B5" : MUTED });
  T(s, String(n), { x: 12.2, y: 7.02, w: 0.5, h: 0.28, fontSize: 10, color: dark ? "8FA3B5" : MUTED, align: "right" });
  if (notes) s.addNotes(notes);
  return s;
}

async function divider(section, num, title, question, iconName, color, notes) {
  const s = pres.addSlide({ sectionTitle: sec(section) });
  n += 1;
  s.background = { color: INK };
  s.addShape(pres.shapes.OVAL, { x: 8.6, y: 1.2, w: 4.6, h: 4.6, fill: { color, transparency: 82 }, line: { color, transparency: 60, width: 1.5 }, objectName: A(1, "f", "halo") });
  s.addShape(pres.shapes.OVAL, { x: 9.55, y: 2.15, w: 2.7, h: 2.7, fill: { color }, line: { color }, objectName: A(1, "f", "core") });
  s.addImage({ data: await icon(iconName, WHITE), x: 10.25, y: 2.85, w: 1.3, h: 1.3, objectName: A(1, "f", "ico") });
  T(s, num, { x: 0.8, y: 1.3, w: 3, h: 1.2, fontSize: 72, bold: true, color });
  T(s, title, { x: 0.8, y: 2.65, w: 7.5, h: 1.2, fontSize: 40, bold: true, color: WHITE });
  T(s, question, { x: 0.8, y: 4.0, w: 7.3, h: 1.5, fontSize: 20, color: SOFT, italic: true, objectName: A(2, "f", "q") });
  T(s, String(n), { x: 12.2, y: 7.02, w: 0.5, h: 0.28, fontSize: 10, color: "8FA3B5", align: "right" });
  if (notes) s.addNotes(notes);
  return s;
}

// gambar dengan rasio asli (dibaca dari header PNG), dipusatkan dalam kotak x,y,w,h
function pic(s, file, x, y, w, h, objectName) {
  const b = fs.readFileSync(file);
  const iw = b.readUInt32BE(16), ih = b.readUInt32BE(20);
  const k = Math.min(w / iw, h / ih), ww = iw * k, hh = ih * k;
  s.addImage(Object.assign({ path: file, x: x + (w - ww) / 2, y: y + (h - hh) / 2, w: ww, h: hh }, objectName ? { objectName } : {}));
}

// batang horizontal dari shape (beranimasi wipe dari kiri)
function hbars(s, x, y, w, rows, { max, rowH = 0.62, labelW = 2.6, fmt = (v) => String(v), step0 = 1, valueSize = 16, labelSize = 14, track = true }) {
  rows.forEach((r, i) => {
    const yy = y + i * rowH;
    T(s, r.label, { x, y: yy, w: labelW - 0.15, h: rowH * 0.8, fontSize: labelSize, valign: "middle", bold: !!r.bold, align: "right" });
    const bw = (w - labelW - 1.1) * Math.max(r.value, 0) / max;
    if (track) s.addShape(pres.shapes.RECTANGLE, { x: x + labelW, y: yy + rowH * 0.15, w: w - labelW - 1.1, h: rowH * 0.5, fill: { color: LIGHT }, line: { color: LIGHT } });
    s.addShape(pres.shapes.RECTANGLE, { x: x + labelW, y: yy + rowH * 0.15, w: Math.max(bw, 0.02), h: rowH * 0.5, fill: { color: r.color }, line: { color: r.color }, objectName: A(step0 + i, "r", "bar") });
    T(s, fmt(r.value), { x: x + labelW + bw + 0.1, y: yy, w: 1.0, h: rowH * 0.8, fontSize: valueSize, bold: true, color: r.color === GREY ? MUTED : r.color, valign: "middle", objectName: A(step0 + i, "f", "val") });
  });
}

// batang vertikal (wipe dari bawah)
function vbars(s, x, y, w, h, cols, { max, fmt = (v) => String(v), step0 = 1, labelSize = 13, valueSize = 18, baseline = null }) {
  const cw = w / cols.length;
  cols.forEach((c, i) => {
    const bh = (h - 0.9) * c.value / max;
    const bx = x + i * cw + cw * 0.18, bw = cw * 0.64;
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: y + (h - 0.9) - bh + 0.4, w: bw, h: Math.max(bh, 0.02), fill: { color: c.color }, line: { color: c.color }, objectName: A(step0 + i, "u", "col") });
    T(s, fmt(c.value), { x: bx - 0.2, y: y + (h - 0.9) - bh, w: bw + 0.4, h: 0.38, fontSize: valueSize, bold: true, align: "center", color: c.color === GREY ? MUTED : c.color, objectName: A(step0 + i, "f", "val") });
    T(s, c.label, { x: x + i * cw, y: y + h - 0.45, w: cw, h: 0.5, fontSize: labelSize, align: "center", color: INK });
  });
  s.addShape(pres.shapes.LINE, { x, y: y + h - 0.5, w, h: 0, line: { color: MUTED, width: 1 } });
  if (baseline) {
    const by = y + (h - 0.9) - (h - 0.9) * baseline.value / max + 0.4;
    s.addShape(pres.shapes.LINE, { x, y: by, w, h: 0, line: { color: MUTED, width: 1.25, dashType: "dash" }, objectName: A(step0 + cols.length, "f", "base") });
    T(s, baseline.label, { x: x + w - 3.2, y: by - 0.36, w: 3.2, h: 0.32, fontSize: 12, color: MUTED, align: "right", objectName: A(step0 + cols.length, "f", "basel") });
  }
}

// gauge donat (grafik asli PowerPoint)
function gauge(s, x, y, d, value, color, big, label, step) {
  s.addChart(pres.charts.DOUGHNUT, [{ name: "AUC", labels: ["value", "rest"], values: [value, 1 - value] }],
    { x, y, w: d, h: d, holeSize: 72, chartColors: [color, "E4E8EC"], showLegend: false, showValue: false, showPercent: false,
      showLabel: false, showTitle: false, dataBorder: { pt: 0, color: "FFFFFF" }, firstSliceAng: 0, objectName: A(step, "f", "gauge") });
  T(s, [{ text: big, options: { fontSize: 30, bold: true, color, breakLine: true } }, { text: "of 100", options: { fontSize: 11, color: MUTED } }],
    { x: x + d * 0.25, y: y + d * 0.32, w: d * 0.5, h: d * 0.36, align: "center", valign: "middle", objectName: A(step, "f", "gv") });
  T(s, label, { x: x - 0.3, y: y + d + 0.05, w: d + 0.6, h: 0.8, fontSize: 13, align: "center", objectName: A(step, "f", "gl") });
}

(async () => {
// ===================================================================== 1. Judul (hero)
{
  n += 1;
  const s = pres.addSlide({ sectionTitle: sec("Introduction") });
  s.background = { color: INK };
  pic(s, F4 + "hero_map.png", 6.3, 0.7, 7.0, 4.75, A(1, "f", "hero"));
  T(s, "CIRED 2027 · WEST JAVA, INDONESIA", { x: 0.8, y: 1.0, w: 6, h: 0.4, fontSize: 13, bold: true, color: AMBER, charSpacing: 2 });
  T(s, "Capacity maps as an equity instrument", { x: 0.8, y: 1.5, w: 6.4, h: 1.9, fontSize: 42, bold: true, color: WHITE });
  T(s, "Publishing charging demand and network headroom as open data in a vertically integrated DSO",
    { x: 0.8, y: 3.45, w: 6.0, h: 1.1, fontSize: 19, color: SOFT, objectName: A(2, "f", "sub") });
  const legend = [["FaBolt", TEAL, "network headroom"], ["FaCarSide", AMBER, "EV owners"], ["FaChargingStation", WHITE, "public chargers"]];
  for (let i = 0; i < legend.length; i++) {
    const x = 7.0 + i * 2.05;
    s.addShape(pres.shapes.OVAL, { x, y: 5.65, w: 0.42, h: 0.42, fill: { color: legend[i][1] === WHITE ? "5E6B79" : legend[i][1] }, line: { color: legend[i][1] === WHITE ? "5E6B79" : legend[i][1] }, objectName: A(3, "f", "lg") });
    s.addImage({ data: await icon(legend[i][0], WHITE), x: x + 0.09, y: 5.74, w: 0.24, h: 0.24, objectName: A(3, "f", "lgi") });
    T(s, legend[i][2], { x: x + 0.5, y: 5.66, w: 1.5, h: 0.42, fontSize: 12, color: SOFT, valign: "middle", objectName: A(3, "f", "lgt") });
  }
  T(s, [{ text: "Qashtalani Haramaini", options: { bold: true, breakLine: true } },
        { text: "Alyas Widita · Liz Taylor", options: { breakLine: true } },
        { text: "Monash University · PT PLN (Persero) UID Jawa Barat", options: { color: SOFT } }],
    { x: 0.8, y: 5.0, w: 6, h: 1.3, fontSize: 15, color: WHITE, objectName: A(2, "f", "auth") });
  s.addNotes("One line: what a distribution operator chooses to publish on its capacity map decides where public chargers go and who gets served. The background map is the real data: amber cells are where registered EV owners live, green-blue cells are where the grid has spare capacity, white dots are public chargers.");
}

// ===================================================================== 2. Agenda
{
  const s = base("Introduction", "The talk in four questions", { notes: "Four parts. Each part opens with a dark divider slide." });
  const parts = [["01", "Why does a map matter?", "A capacity map ranks places, and capital follows the ranking.", "FaMapMarkedAlt", BLUE],
                 ["02", "What did we find?", "Chargers follow the strong grid, and the poorest regencies are left out.", "FaSearchLocation", TEAL],
                 ["03", "Is it robust?", "Tested against chance, site size and four map resolutions.", "FaShieldAlt", AMBER],
                 ["04", "What should a DSO publish?", "Five requirements and a phased path to open data.", "FaBullhorn", CORAL]];
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i], x = 0.6 + i * 3.08;
    box(s, x, 1.7, 2.85, 4.9, LIGHT, { objectName: A(i + 1, "u", "card") });
    await iconDot(s, x + 0.95, 2.05, 0.95, p[3], p[4], i + 1);
    T(s, p[0], { x: x + 0.2, y: 3.2, w: 2.45, h: 0.6, fontSize: 30, bold: true, color: p[4], align: "center", objectName: A(i + 1, "f", "num") });
    T(s, p[1], { x: x + 0.2, y: 3.85, w: 2.45, h: 0.95, fontSize: 18, bold: true, align: "center", objectName: A(i + 1, "f", "t") });
    T(s, p[2], { x: x + 0.25, y: 4.85, w: 2.35, h: 1.5, fontSize: 13.5, align: "center", color: MUTED, objectName: A(i + 1, "f", "d") });
  }
}

// ===================================================================== 3. Ringkasan infografis
{
  const s = base("Introduction", "Six findings at a glance", { notes: "The whole talk on one slide. Each tile is backed by a later slide and a robustness test." });
  const tiles = [
    ["FaIndustry", TEAL, `${f2(F1.auc.kva)} vs ${f2(F1.auc.rel)}`, "Grid size predicts where chargers are (AUC). Spare capacity is a coin toss."],
    ["FaMapPin", CORAL, `${f1(B.hl.evp)} % : ${f1(B.hl.chgp)} %`, "Owners vs chargers in cells with high demand and low headroom."],
    ["FaBalanceScale", TEAL, `+${f1(gP("dwh"))} vs +${f1(gP("headroom"))}`, "Points of coverage for the poorest third of regencies: demand within headroom vs headroom-only."],
    ["FaUsers", INK, "+14–32 %", "More owners reached than headroom-only, at every map resolution."],
    ["FaLayerGroup", BLUE, `ρ = ${sg(TW.rho)}`, "Transformer and substation headroom are unrelated: publish both."],
    ["FaUserShield", AMBER, `${f1(D.audit.pii)} %`, "of load records name field staff. Clean before publishing."],
  ];
  for (let i = 0; i < tiles.length; i++) {
    const t = tiles[i], x = 0.6 + (i % 3) * 4.1, y = 1.55 + Math.floor(i / 3) * 2.7;
    const st = i + 1;
    box(s, x, y, 3.85, 2.45, LIGHT, { objectName: A(st, "f", "tile") });
    await iconDot(s, x + 0.25, y + 0.25, 0.75, t[0], t[1], st);
    T(s, t[2], { x: x + 1.15, y: y + 0.22, w: 2.6, h: 0.8, fontSize: 26, bold: true, color: t[1], valign: "middle", objectName: A(st, "f", "big") });
    T(s, t[3], { x: x + 0.25, y: y + 1.15, w: 3.4, h: 1.2, fontSize: 13.5, objectName: A(st, "f", "lbl") });
  }
}

// ===================================================================== D1
await divider("Why the map matters", "01", "Why the map matters", "If a DSO publishes only where the grid has room, where does the next charger go, and who does it serve?", "FaMapMarkedAlt", BLUE,
  "Part one sets up the argument and the data.");

// ===================================================================== 4. Rantai kausal
{
  const s = base("Why the map matters", "A capacity map is a ranking, and capital follows the ranking", {
    notes: "This is the causal chain the paper tests. Every arrow is a choice someone makes using what the DSO published." });
  const steps = [["FaDatabase", "DSO publishes", "headroom only, or headroom + demand", INK],
                 ["FaSearchLocation", "Developer searches", "picks the top-ranked cells", BLUE],
                 ["FaPlug", "Grid connects", "where headroom allows", TEAL],
                 ["FaUsers", "Owners served", "those near the new sites", CORAL]];
  for (let i = 0; i < steps.length; i++) {
    const st = steps[i], x = 0.75 + i * 3.15;
    await iconDot(s, x + 0.6, 1.75, 1.3, st[0], st[3], i + 1);
    T(s, st[1], { x: x - 0.1, y: 3.2, w: 2.7, h: 0.5, fontSize: 19, bold: true, align: "center", objectName: A(i + 1, "f", "t") });
    T(s, st[2], { x: x - 0.1, y: 3.7, w: 2.7, h: 0.6, fontSize: 14, color: MUTED, align: "center", objectName: A(i + 1, "f", "d") });
    if (i < 3) arrowR(s, x + 2.3, 2.25, 0.75, GREY, i + 1);
  }
  // dua skenario
  box(s, 0.6, 4.6, 5.9, 2.15, CORAL_LT, { objectName: A(5, "f", "sc1") });
  await iconBare(s, 0.85, 4.85, 0.55, "FaBolt", CORAL, 5);
  T(s, [{ text: "Headroom-only map", options: { bold: true, color: CORAL, breakLine: true } },
        { text: "Ranks the strong grid first: urban cores and industrial corridors, where chargers already are. It densifies." }],
    { x: 1.55, y: 4.8, w: 4.75, h: 1.8, fontSize: 15, objectName: A(5, "f", "sc1t") });
  box(s, 6.8, 4.6, 5.9, 2.15, TEAL_LT, { objectName: A(6, "f", "sc2") });
  await iconBare(s, 7.05, 4.85, 0.55, "FaLayerGroup", TEAL, 6);
  T(s, [{ text: "Two-surface map", options: { bold: true, color: TEAL, breakLine: true } },
        { text: "Shows where owners wait and whether the grid can host them. It fills gaps, and prices the connection." }],
    { x: 7.75, y: 4.8, w: 4.75, h: 1.8, fontSize: 15, objectName: A(6, "f", "sc2t") });
}

// ===================================================================== 5. UE vs Jawa Barat (ilustrasi)
{
  const s = base("Why the map matters", "PLN sees both surfaces that Europe keeps apart", {
    notes: "In the EU the DSO generally may not own charge points, partly because it would know where headroom is. In West Java PLN is both. That makes this study possible, and it creates an information asymmetry with private charge-point operators." });
  // UE
  box(s, 0.6, 1.6, 5.9, 5.15, LIGHT, { objectName: A(1, "f", "eu") });
  await iconBare(s, 0.9, 1.85, 0.5, "FaGlobeEurope", MUTED, 1);
  T(s, "European Union: unbundled", { x: 1.55, y: 1.85, w: 4.7, h: 0.5, fontSize: 18, bold: true, color: MUTED, valign: "middle", objectName: A(1, "f", "eut") });
  await iconDot(s, 1.05, 2.8, 1.1, "FaBolt", INK, 2);
  T(s, "DSO\nknows headroom", { x: 0.65, y: 4.0, w: 1.9, h: 0.8, fontSize: 13, align: "center", objectName: A(2, "f", "l") });
  s.addShape(pres.shapes.RECTANGLE, { x: 3.4, y: 2.6, w: 0.12, h: 2.2, fill: { color: CORAL }, line: { color: CORAL }, objectName: A(3, "f", "wall") });
  await iconBare(s, 3.2, 4.95, 0.5, "FaLock", CORAL, 3);
  await iconDot(s, 4.55, 2.8, 1.1, "FaChargingStation", BLUE, 2);
  T(s, "CPO\nknows demand", { x: 4.15, y: 4.0, w: 1.9, h: 0.8, fontSize: 13, align: "center", objectName: A(2, "f", "l") });
  T(s, "A wall between the two datasets: no single actor sees both.", { x: 0.9, y: 5.6, w: 5.3, h: 0.9, fontSize: 14, color: MUTED, objectName: A(3, "f", "eud") });
  // Jabar
  box(s, 6.8, 1.6, 5.9, 5.15, TEAL_LT, { objectName: A(4, "f", "jb") });
  await iconBare(s, 7.1, 1.85, 0.5, "FaFlag", TEAL, 4);
  T(s, "West Java: vertically integrated", { x: 7.75, y: 1.85, w: 4.7, h: 0.5, fontSize: 18, bold: true, color: TEAL, valign: "middle", objectName: A(4, "f", "jbt") });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.3, y: 2.6, w: 4.9, h: 2.4, fill: { color: WHITE }, line: { color: TEAL, width: 1.5 }, rectRadius: 0.12, objectName: A(5, "f", "pln") });
  T(s, "PT PLN (Persero)", { x: 7.5, y: 2.7, w: 4.5, h: 0.45, fontSize: 16, bold: true, color: TEAL, align: "center", objectName: A(5, "f", "plnt") });
  await iconDot(s, 7.9, 3.3, 0.9, "FaBolt", INK, 5);
  await iconDot(s, 9.3, 3.3, 0.9, "FaChargingStation", BLUE, 5);
  await iconDot(s, 10.7, 3.3, 0.9, "FaCarSide", AMBER, 5);
  T(s, "grid · chargers · EV customers", { x: 7.5, y: 4.3, w: 4.5, h: 0.4, fontSize: 13, align: "center", color: MUTED, objectName: A(5, "f", "plnd") });
  await iconBare(s, 7.3, 5.4, 0.5, "FaEye", TEAL, 6);
  T(s, "One company sees both surfaces. Private CPOs do not: that asymmetry is what publication removes.", { x: 7.95, y: 5.3, w: 4.5, h: 1.3, fontSize: 14, objectName: A(6, "f", "jbd") });
}

// ===================================================================== 6. Corong data
{
  const s = base("Why the map matters", "From 53,797 field records to 50 candidate sites", {
    notes: "The funnel shows how raw registers become a decision. Each step loses information for a reason: implausible records, aggregation to 5 km cells, and the restriction to cells that have owners but no charger." });
  const rows = [[`${f0(D.meta.total)}`, "transformer load records (2020–24)", "FaDatabase", INK],
                [`${f0(D.meta.usable)}`, "usable after plausibility checks", "FaFilter", BLUE],
                [`${f0(D.meta.cells)}`, "5 km cells with grid, chargers or owners", "FaThLarge", TEAL],
                [`${D.meta.cells_ev}`, "cells with registered EV owners", "FaCarSide", AMBER],
                [`${B.pool}`, `of them with no public charger (${f0(B.pool_ev)} owners)`, "FaMapPin", CORAL],
                ["50", "new sites placed by each rule", "FaChargingStation", TEAL]];
  for (let i = 0; i < rows.length; i++) {
    const r = rows[i], w = 7.4 - i * 0.95, x = 0.6 + (7.4 - w) / 2, y = 1.55 + i * 0.88;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.74, fill: { color: r[3] }, line: { color: r[3] }, rectRadius: 0.08, objectName: A(i + 1, "u", "fun") });
    T(s, r[0], { x, y, w, h: 0.74, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle", objectName: A(i + 1, "f", "fn") });
    await iconBare(s, 8.4, y + 0.14, 0.46, r[2], r[3], i + 1);
    T(s, r[1], { x: 9.0, y, w: 3.8, h: 0.74, fontSize: 14, valign: "middle", objectName: A(i + 1, "f", "fl") });
  }
}

// ===================================================================== 7. Metode (alur ikon)
{
  const s = base("Why the map matters", "Method: from spot readings to a ranking, then stress tests", {
    notes: "Headroom at the 80 percent planning limit; growth to March 2026 at 3 percent per year with sensitivities; aggregation to 5 km; three siting rules; then random portfolios and sweeps. Regencies come from BPS polygons, not the register's regency field." });
  const steps = [["FaBolt", "Headroom", "H = max(0, S·(0.8 − λ))", TEAL],
                 ["FaClock", "Age to 2026", "λ·(1+g)^(2026.2 − t)\ng = 3.0 %/yr", TEAL],
                 ["FaThLarge", "5 km cells", "+ 27 BPS regencies\n+ per-capita expenditure", TEAL],
                 ["FaSitemap", "Three rules", "headroom · demand ·\ndemand within headroom", CORAL],
                 ["FaDice", "Stress tests", "5,000 random draws,\nsite size, 4 resolutions", AMBER]];
  for (let i = 0; i < steps.length; i++) {
    const st = steps[i], x = 0.6 + i * 2.5;
    box(s, x, 1.8, 2.2, 3.2, LIGHT, { objectName: A(i + 1, "u", "c") });
    await iconDot(s, x + 0.65, 2.05, 0.9, st[0], st[3], i + 1);
    T(s, st[1], { x: x + 0.1, y: 3.1, w: 2.0, h: 0.5, fontSize: 17, bold: true, align: "center", objectName: A(i + 1, "f", "t") });
    T(s, st[2], { x: x + 0.1, y: 3.6, w: 2.0, h: 1.3, fontSize: 12.5, align: "center", color: MUTED, objectName: A(i + 1, "f", "d") });
    if (i < 4) arrowR(s, x + 2.2, 3.2, 0.28, GREY, i + 1);
  }
  const outs = [["FaUsers", "Owners reached", TEAL], ["FaHourglassHalf", "Stranded sites", CORAL], ["FaTimesCircle", "Infeasible sites", INK], ["FaBalanceScale", "Who gains (income)", AMBER]];
  T(s, "Each rule is scored on:", { x: 0.6, y: 5.3, w: 4, h: 0.35, fontSize: 13, color: MUTED, objectName: A(6, "f", "sc") });
  for (let i = 0; i < outs.length; i++) {
    const x = 0.6 + i * 3.08;
    await iconDot(s, x, 5.8, 0.6, outs[i][0], outs[i][2], 6);
    T(s, outs[i][1], { x: x + 0.75, y: 5.8, w: 2.2, h: 0.6, fontSize: 15, bold: true, valign: "middle", objectName: A(6, "f", "o") });
  }
}

// ===================================================================== D2
await divider("What we found", "02", "What we found", "Did chargers go where the grid has spare room, or where it is simply big? And who was left out?", "FaSearchLocation", TEAL,
  "Part two: the findings.");

// ===================================================================== 8. Dua permukaan
{
  const s = base("What we found", "Headroom and demand are two different maps", {
    notes: `Left: spare capacity, concentrated in the Bekasi–Karawang corridor and central Bandung. Middle: owners, concentrated in Bogor–Depok–Bekasi and Bandung. Right: overlay. ${f1(B.gap.h_nochg)} percent of headroom sits in cells without a charger and ${f1(B.gap.ev_nochg)} percent of owners live in such cells (5 km figures).` });
  const heads = [["FaBolt", TEAL, "Network headroom", "what a DSO map shows today"], ["FaCarSide", AMBER, "EV owners", "the demand layer that is missing"], ["FaChargingStation", CORAL, "Where they meet", "chargers, and the gaps"]];
  for (let i = 0; i < 3; i++) {
    const x = 0.6 + i * 4.1;
    await iconDot(s, x, 1.45, 0.55, heads[i][0], heads[i][1], i + 1);
    T(s, [{ text: heads[i][2], options: { bold: true, breakLine: true } }, { text: heads[i][3], options: { color: MUTED, fontSize: 12 } }],
      { x: x + 0.65, y: 1.4, w: 3.3, h: 0.7, fontSize: 16, objectName: A(i + 1, "f", "h") });
  }
  pic(s, F4 + "map_surfaces_labeled.png", 0.5, 2.2, 12.3, 3.8, A(1, "f", "map"));
  box(s, 0.6, 6.1, 12.1, 0.75, CORAL_LT, { objectName: A(4, "f", "cb") });
  T(s, [{ text: `${f1(B.gap.h_nochg)} %`, options: { bold: true, color: CORAL } }, { text: " of spare capacity sits in cells with no charger, and " },
        { text: `${f1(B.gap.ev_nochg)} %`, options: { bold: true, color: CORAL } }, { text: " of owners live in such cells (5 km grid)." }],
    { x: 0.9, y: 6.18, w: 11.6, h: 0.6, fontSize: 16, valign: "middle", objectName: A(4, "f", "cbt") });
}

// ===================================================================== 9. Temuan 1: gauge AUC
{
  const s = base("What we found", "Chargers follow the size of the grid, not its spare room", {
    lead: "Pick one cell with a charger and one without. How often does each variable point to the right one?",
    notes: `AUC: the probability that a randomly chosen charger cell scores higher than a randomly chosen cell without one. 0.50 is a coin toss. Installed kVA gets it right ${Math.round(100 * F1.auc.kva)} times in 100; relative headroom ${Math.round(100 * F1.auc.rel)} times, slightly worse than chance. Same story at every map resolution.` });
  gauge(s, 0.9, 2.1, 2.6, F1.auc.kva, INK, `${Math.round(100 * F1.auc.kva)}`, "Installed grid capacity (kVA)", 1);
  gauge(s, 4.3, 2.1, 2.6, F1.auc.ev, AMBER, `${Math.round(100 * F1.auc.ev)}`, "Registered EV owners", 2);
  gauge(s, 7.7, 2.1, 2.6, F1.auc.rel, CORAL, `${Math.round(100 * F1.auc.rel)}`, "Spare capacity (% free)", 3);
  box(s, 10.75, 2.0, 2.0, 3.5, LIGHT, { objectName: A(4, "f", "coin") });
  await iconBare(s, 11.35, 2.25, 0.8, "FaCoins", MUTED, 4);
  T(s, "coin toss = 50/100", { x: 10.85, y: 3.2, w: 1.8, h: 0.8, fontSize: 14, bold: true, align: "center", color: MUTED, objectName: A(4, "f", "coint") });
  T(s, "spare capacity does no better", { x: 10.85, y: 4.0, w: 1.8, h: 1.2, fontSize: 12.5, align: "center", color: MUTED, objectName: A(4, "f", "coind") });
  box(s, 0.6, 5.85, 12.1, 0.95, TEAL_LT, { objectName: A(5, "f", "b") });
  T(s, [{ text: `${Math.round(F1.med_kva.chg / F1.med_kva.nochg)}× more installed kVA`, options: { bold: true, color: TEAL } },
        { text: ` in charger cells (median ${f0(F1.med_kva.chg)} vs ${f0(F1.med_kva.nochg)} kVA), but the same free share (${f1(100 * F1.med_rel.chg)} % vs ${f1(100 * F1.med_rel.nochg)} %). ρ with spare share = ${sg(F1.rel)}, 95 % CI ${sg(F1.rel_ci[0])} to ${sg(F1.rel_ci[1])}.` }],
    { x: 0.9, y: 5.95, w: 11.6, h: 0.8, fontSize: 15, valign: "middle", objectName: A(5, "f", "bt") });
}

// ===================================================================== 10. Waffle: 1 dari 4 pemilik
{
  const s = base("What we found", "One in four EV owners has no public charger in their 5 km cell", {
    notes: `Of ${f0(D.meta.ev)} registered owners, ${f1(B.baseline.cov)} percent live in a cell with a public charger. The rest, ${f1(100 - B.baseline.cov)} percent, do not. This is the pool the next 50 sites could serve.` });
  pic(s, F4 + "waffle_all_today.png", 0.9, 1.6, 5.0, 5.0, A(1, "f", "waffle"));
  T(s, "each square = 1 % of registered EV owners", { x: 0.9, y: 6.55, w: 5, h: 0.35, fontSize: 11, color: MUTED, align: "center" });
  await iconDot(s, 6.6, 1.9, 0.75, "FaCheckCircle", TEAL, 2);
  T(s, [{ text: `${f1(B.baseline.cov)} %`, options: { bold: true, fontSize: 40, color: TEAL, breakLine: true } },
        { text: "live in a 5 km cell that already has a public charger", options: { fontSize: 15 } }],
    { x: 7.55, y: 1.75, w: 5.1, h: 1.6, objectName: A(2, "f", "a") });
  await iconDot(s, 6.6, 3.75, 0.75, "FaTimesCircle", CORAL, 3);
  T(s, [{ text: `${f1(100 - B.baseline.cov)} %`, options: { bold: true, fontSize: 40, color: CORAL, breakLine: true } },
        { text: `do not: ${f0(B.pool_ev)} owners in ${B.pool} cells, the pool for new sites`, options: { fontSize: 15 } }],
    { x: 7.55, y: 3.6, w: 5.1, h: 1.6, objectName: A(3, "f", "b") });
  box(s, 6.6, 5.45, 6.1, 1.3, LIGHT, { objectName: A(4, "f", "c") });
  T(s, "Which of these owners a new site reaches depends on what the DSO publishes.", { x: 6.85, y: 5.55, w: 5.6, h: 1.1, fontSize: 16, bold: true, valign: "middle", objectName: A(4, "f", "ct") });
}

// ===================================================================== 11. Peta celah dengan callout
{
  const s = base("What we found", `${B.hl.unserved} cells have many owners, little headroom and no charger`, {
    notes: `The red cells are the high-demand / low-headroom quadrant without a charger: ${B.hl.unserved} cells, ${B.hl.unserved_ev} owners. Across that quadrant, owners' share is ${f1(B.hl.evp)} percent and chargers' share ${f1(B.hl.chgp)} percent. A headroom-only map ranks these cells last; a demand-only map ranks them first without signalling the connection cost.` });
  pic(s, F4 + "map_gap_callouts.png", 0.4, 1.35, 8.4, 5.55, A(1, "f", "map"));
  T(s, "owners' share vs chargers' share in high-demand, low-headroom cells", { x: 9.0, y: 1.5, w: 3.8, h: 0.7, fontSize: 13, color: MUTED, objectName: A(2, "f", "l") });
  hbars(s, 9.0, 2.25, 3.9, [{ label: "Owners", value: B.hl.evp, color: CORAL }, { label: "Chargers", value: B.hl.chgp, color: GREY }],
    { max: 14, labelW: 1.0, fmt: (v) => `${f1(v)} %`, step0: 2, valueSize: 18 });
  box(s, 9.0, 3.85, 3.8, 2.9, LIGHT, { objectName: A(4, "f", "w") });
  T(s, [{ text: "What each map does with them", options: { bold: true, breakLine: true } },
        { text: "Headroom-only: ranks them last.", options: { bullet: true, breakLine: true } },
        { text: "Demand-only: ranks them first, silent on connection cost.", options: { bullet: true, breakLine: true } },
        { text: "Two surfaces: shows both, so the cost can be priced.", options: { bullet: true } }],
    { x: 9.2, y: 4.0, w: 3.45, h: 2.7, fontSize: 13.5, paraSpaceAfter: 6, objectName: A(4, "f", "wt") });
}

// ===================================================================== 12. Tiga peta yang bisa dipublikasikan
{
  const s = base("What we found", "Three maps a DSO could publish, three ways to pick 50 sites", {
    notes: `Each rule picks 50 of the ${B.pool} unserved cells that have owners. The rule is what the published layer implicitly tells developers.` });
  const rules = [["FaBolt", CORAL, CORAL_LT, "Headroom-only", "Publish spare capacity.", "Rank cells by headroom (kVA)."],
                 ["FaCarSide", AMBER, AMBER_LT, "Demand-only", "Publish where owners are.", "Rank cells by registered owners."],
                 ["FaLayerGroup", TEAL, TEAL_LT, "Demand within headroom", "Publish both surfaces.", `Rank by owners among cells with ≥ ${D.meta.feasible} kVA (one 4 × 60 kW site).`]];
  for (let i = 0; i < 3; i++) {
    const r = rules[i], x = 0.6 + i * 4.1;
    box(s, x, 1.6, 3.85, 5.15, r[2], { objectName: A(i + 1, "u", "c") });
    await iconDot(s, x + 1.4, 1.9, 1.05, r[0], r[1], i + 1);
    T(s, r[3], { x: x + 0.2, y: 3.1, w: 3.45, h: 0.55, fontSize: 21, bold: true, align: "center", color: r[1], objectName: A(i + 1, "f", "t") });
    T(s, r[4], { x: x + 0.2, y: 3.7, w: 3.45, h: 0.45, fontSize: 15, bold: true, align: "center", objectName: A(i + 1, "f", "p") });
    T(s, r[5], { x: x + 0.3, y: 4.2, w: 3.25, h: 0.9, fontSize: 13.5, align: "center", color: MUTED, objectName: A(i + 1, "f", "d") });
    pic(s, F4 + `sites_${["headroom", "demand", "dwh"][i]}.png`, x + 0.2, 5.05, 3.45, 1.6, A(i + 1, "f", "m"));
  }
}

// ===================================================================== 13. Piktogram 50 situs
{
  const s = base("What we found", "Fifty sites each: what happens to every one of them", {
    lead: "Each dot is one new site. Filled = reaches owners; hollow = stranded in a low-demand cell; ✕ = grid cannot host it",
    notes: `Headroom-only: ${R.headroom.stranded} of 50 sites stranded. Demand-only: ${R.demand.infeas} sites below the ${D.meta.feasible} kVA threshold. Demand within headroom: every site reaches demand and can be connected. Owners reached: ${R.headroom.owners}, ${R.demand.owners}, ${R.dwh.owners}.` });
  const rows = [["headroom", CORAL, "Headroom-only", `${R.headroom.owners} owners`, `${R.headroom.stranded} stranded`],
                ["demand", AMBER, "Demand-only", `${R.demand.owners} owners`, `${R.demand.infeas} infeasible`],
                ["dwh", TEAL, "Demand within headroom", `${R.dwh.owners} owners`, "0 stranded · 0 infeasible"]];
  rows.forEach((r, i) => {
    const y = 2.0 + i * 1.6;
    T(s, r[2], { x: 0.6, y, w: 3.0, h: 0.5, fontSize: 18, bold: true, color: r[1], objectName: A(i + 1, "f", "n") });
    T(s, [{ text: r[3], options: { bold: true, breakLine: true } }, { text: r[4], options: { color: MUTED } }], { x: 0.6, y: y + 0.5, w: 3.0, h: 0.8, fontSize: 15, objectName: A(i + 1, "f", "v") });
    pic(s, F4 + `picto_${r[0]}.png`, 3.7, y - 0.05, 9.0, 1.4, A(i + 1, "r", "p"));
  });
}

// ===================================================================== 14. Pemilik terjangkau (batang) vs acak
{
  const s = base("What we found", "Every rule beats chance, but the published layer still moves 115 owners", {
    notes: `Random placement of 50 sites in the same pool reaches ${f0(RD.owners_mean)} owners on average. All rules are far above. Between the best and the worst informed rule: ${R.demand.owners - R.headroom.owners} owners for the same budget.` });
  vbars(s, 0.8, 1.6, 7.6, 5.1, [{ label: "Random", value: Math.round(RD.owners_mean), color: GREY },
    { label: "Headroom-only", value: R.headroom.owners, color: CORAL }, { label: "Demand-only", value: R.demand.owners, color: AMBER },
    { label: "Demand within\nheadroom", value: R.dwh.owners, color: TEAL }], { max: 900, step0: 1 });
  await iconDot(s, 9.0, 1.8, 0.7, "FaDice", MUTED, 5);
  T(s, [{ text: `${RD.owners_p95}`, options: { bold: true, fontSize: 28, breakLine: true } }, { text: "best 5 % of 5,000 random portfolios", options: { fontSize: 13, color: MUTED } }],
    { x: 9.85, y: 1.7, w: 3.0, h: 1.1, objectName: A(5, "f", "r") });
  await iconDot(s, 9.0, 3.25, 0.7, "FaArrowsAltH", INK, 6);
  T(s, [{ text: `${R.demand.owners - R.headroom.owners} owners`, options: { bold: true, fontSize: 28, breakLine: true } }, { text: "gap between best and worst informed rule", options: { fontSize: 13, color: MUTED } }],
    { x: 9.85, y: 3.15, w: 3.0, h: 1.1, objectName: A(6, "f", "g") });
  await iconDot(s, 9.0, 4.7, 0.7, "FaShieldAlt", TEAL, 7);
  T(s, [{ text: `−${R.demand.owners - R.dwh.owners} owners`, options: { bold: true, fontSize: 28, color: TEAL, breakLine: true } }, { text: "the price of making every site connectable", options: { fontSize: 13, color: MUTED } }],
    { x: 9.85, y: 4.6, w: 3.0, h: 1.1, objectName: A(7, "f", "c") });
}

// ===================================================================== 15. Ekuitas: waffle termiskin
{
  const s = base("What we found", "In the poorest third of regencies, the map decides who gets a charger", {
    lead: "Of every 100 EV owners in the nine regencies with the lowest per-capita expenditure, how many live in a cell with a charger?",
    notes: `Regencies ranked by 2024 per-capita expenditure (BPS), nine per third. Today ${f1(B.baseline.terc[0])} percent; headroom-only ${f1(R.headroom.terc[0])}; demand-only ${f1(R.demand.terc[0])}; demand within headroom ${f1(R.dwh.terc[0])}. Only 272 owners live in this third, 181 in Kabupaten Bandung Barat, so treat magnitudes with care; the direction is clear.` });
  const ws = [["base", "Today", INK, B.baseline.terc[0], ""], ["headroom", "Headroom-only", CORAL, R.headroom.terc[0], `+${f1(gP("headroom"))}`],
              ["demand", "Demand-only", AMBER, R.demand.terc[0], `+${f1(gP("demand"))}`], ["dwh", "Demand within headroom", TEAL, R.dwh.terc[0], `+${f1(gP("dwh"))}`]];
  ws.forEach((w, i) => {
    const x = 0.6 + i * 3.1;
    pic(s, F4 + `waffle_poor_${w[0]}.png`, x + 0.2, 2.15, 2.6, 2.6, A(i + 1, "f", "w"));
    T(s, String(Math.round(w[3])), { x, y: 4.85, w: 3.0, h: 0.75, fontSize: 40, bold: true, align: "center", color: w[2], objectName: A(i + 1, "f", "n") });
    T(s, w[1], { x, y: 5.6, w: 3.0, h: 0.45, fontSize: 15, bold: true, align: "center", objectName: A(i + 1, "f", "l") });
    if (w[4]) T(s, `${w[4]} points`, { x, y: 6.05, w: 3.0, h: 0.4, fontSize: 14, align: "center", color: w[2], objectName: A(i + 1, "f", "g") });
  });
}

// ===================================================================== 16. Ekuitas: kesenjangan kaya-miskin
{
  const s = base("What we found", "Headroom-only widens the rich–poor gap fivefold; demand within headroom keeps it narrowest", {
    notes: "Gap = coverage in the richest third minus coverage in the poorest third, in percentage points. Concentration index above zero means coverage leans toward richer regencies." });
  const gaps = [["Today", B.baseline.terc[2] - B.baseline.terc[0], GREY, B.baseline.ci],
                ["Headroom-only", R.headroom.terc[2] - R.headroom.terc[0], CORAL, R.headroom.ci],
                ["Demand-only", R.demand.terc[2] - R.demand.terc[0], AMBER, R.demand.ci],
                ["Demand within headroom", R.dwh.terc[2] - R.dwh.terc[0], TEAL, R.dwh.ci]];
  T(s, "Coverage gap, richest third minus poorest third (percentage points)", { x: 0.6, y: 1.5, w: 8, h: 0.4, fontSize: 14, color: MUTED });
  hbars(s, 0.6, 2.05, 8.4, gaps.map((g) => ({ label: g[0], value: g[1], color: g[2] })), { max: 24, labelW: 3.0, fmt: (v) => `${f1(v)} pts`, step0: 1, rowH: 0.95, valueSize: 20, labelSize: 15 });
  box(s, 9.3, 1.55, 3.4, 4.2, LIGHT, { objectName: A(5, "f", "ci") });
  await iconBare(s, 9.55, 1.75, 0.55, "FaBalanceScale", INK, 5);
  T(s, "Income concentration index of coverage", { x: 10.2, y: 1.7, w: 2.4, h: 0.7, fontSize: 13, bold: true, objectName: A(5, "f", "cit") });
  gaps.forEach((g, i) => {
    T(s, [{ text: g[0], options: { breakLine: true, fontSize: 12, color: MUTED } }, { text: g[3].toFixed(3), options: { bold: true, fontSize: 20, color: g[2] === GREY ? MUTED : g[2] } }],
      { x: 9.55, y: 2.55 + i * 0.78, w: 3.0, h: 0.75, objectName: A(5, "f", "civ") });
  });
  box(s, 0.6, 6.0, 12.1, 0.8, TEAL_LT, { objectName: A(6, "f", "k") });
  T(s, "Lower is fairer for both measures. Demand within headroom is lowest on the concentration index and narrowest of the three rules on the gap.",
    { x: 0.9, y: 6.08, w: 11.6, h: 0.65, fontSize: 15, valign: "middle", objectName: A(6, "f", "kt") });
}

// ===================================================================== 17. Jebakan "kemerataan"
{
  const s = base("What we found", "Spreading sites evenly is not the same as serving people", {
    lead: "Random placement scores best on the between-regency Gini, and reaches the fewest owners",
    notes: `Between-regency Gini of coverage: random ${RD.gini_mean.toFixed(3)}, headroom-only ${R.headroom.gini.toFixed(3)}, demand within headroom ${R.dwh.gini.toFixed(3)}, demand-only ${R.demand.gini.toFixed(3)}. A Gini target alone rewards scattering sites. That is why the paper reports reach and poorest-third coverage alongside it.` });
  const sc = [["Random", RD.owners_mean, RD.gini_mean, null, GREY], ["Headroom-only", R.headroom.owners, R.headroom.gini, R.headroom.terc[0], CORAL],
              ["Demand-only", R.demand.owners, R.demand.gini, R.demand.terc[0], AMBER], ["Demand within headroom", R.dwh.owners, R.dwh.gini, R.dwh.terc[0], TEAL]];
  const mets = [["Owners reached", 1, 900, (v) => f0(v), "more is better"], ["Regency Gini", 2, 0.25, (v) => v.toFixed(3), "lower = more even"], ["Poorest third covered", 3, 100, (v) => v == null ? "—" : `${f1(v)} %`, "more is better"]];
  const cx0 = 2.75, cwid = 2.05, ry0 = 2.35, rh = 0.95;
  sc.forEach((r, i) => T(s, r[0], { x: 0.6, y: ry0 + i * rh, w: 2.05, h: 0.6, fontSize: 13.5, bold: true, color: r[4] === GREY ? MUTED : r[4], valign: "middle", align: "right" }));
  mets.forEach((m, j) => {
    const x = cx0 + j * (cwid + 0.1);
    T(s, [{ text: m[0], options: { bold: true, breakLine: true } }, { text: m[4], options: { fontSize: 11, color: MUTED } }], { x, y: 1.75, w: cwid, h: 0.6, fontSize: 13.5, align: "center" });
    sc.forEach((r, i) => {
      const v = r[m[1]], y = ry0 + i * rh;
      s.addShape(pres.shapes.RECTANGLE, { x: x + 0.05, y: y + 0.12, w: cwid - 0.75, h: 0.36, fill: { color: LIGHT }, line: { color: LIGHT } });
      if (v != null) s.addShape(pres.shapes.RECTANGLE, { x: x + 0.05, y: y + 0.12, w: Math.max((cwid - 0.75) * v / m[2], 0.03), h: 0.36, fill: { color: r[4] }, line: { color: r[4] }, objectName: A(j + 1, "r", "b") });
      T(s, m[3](v), { x: x + cwid - 0.68, y, w: 0.75, h: 0.6, fontSize: 12.5, bold: true, valign: "middle", objectName: A(j + 1, "f", "v") });
    });
  });
  box(s, 0.6, 6.2, 8.2, 0.6, AMBER_LT, { objectName: A(4, "f", "k") });
  T(s, "Random wins on evenness and loses on reach and on the poorest third.", { x: 0.85, y: 6.22, w: 7.8, h: 0.55, fontSize: 14, bold: true, valign: "middle", objectName: A(4, "f", "kt") });
  box(s, 9.3, 1.75, 3.4, 5.05, LIGHT, { objectName: A(5, "f", "m") });
  await iconBare(s, 9.55, 2.0, 0.55, "FaLightbulb", AMBER, 5);
  T(s, [{ text: "Insight", options: { bold: true, breakLine: true, fontSize: 16 } },
        { text: "State equity targets as coverage of under-served groups, such as the poorest regencies, not as evenness across administrative units.", options: { fontSize: 14 } }],
    { x: 9.55, y: 2.7, w: 2.95, h: 3.9, objectName: A(5, "f", "mt") });
}

// ===================================================================== D3
await divider("Is it robust?", "03", "Is it robust?", "Could the result be luck, or an artefact of the 5 km grid or the site size we chose?", "FaShieldAlt", AMBER,
  "Part three: robustness. We tried to break each finding.");

// ===================================================================== 18. Baseline acak
{
  const s = base("Is it robust?", "Not luck: all three rules sit beyond every one of 5,000 random portfolios", {
    notes: `Random 50-site portfolios from the same ${B.pool} cells: mean ${f0(RD.owners_mean)} owners, 95th percentile ${RD.owners_p95}, maximum below every rule.` });
  pic(s, F3 + "fig7_random_baseline.png", 0.5, 1.5, 8.4, 3.8, A(1, "f", "h"));
  const st = [["FaDice", MUTED, `${f0(RD.owners_mean)}`, "owners, average random portfolio"], ["FaTrophy", TEAL, `${R.headroom.owners}+`, "owners, the weakest informed rule"], ["FaHourglassHalf", CORAL, f1(RD.stranded_mean), "stranded sites, random average"]];
  for (let i = 0; i < 3; i++) {
    const y = 1.6 + i * 1.3;
    await iconDot(s, 9.3, y, 0.7, st[i][0], st[i][1], i + 2);
    T(s, [{ text: st[i][2], options: { bold: true, fontSize: 26, breakLine: true, color: st[i][1] } }, { text: st[i][3], options: { fontSize: 12.5, color: MUTED } }],
      { x: 10.15, y: y - 0.1, w: 2.6, h: 1.1, objectName: A(i + 2, "f", "t") });
  }
  box(s, 0.6, 5.6, 12.1, 1.15, LIGHT, { objectName: A(5, "f", "b") });
  T(s, "Using data at all doubles reach. The policy choice is which layers to publish, and that choice still moves hundreds of owners and the poorest regencies.",
    { x: 0.9, y: 5.7, w: 11.5, h: 0.95, fontSize: 15.5, valign: "middle", objectName: A(5, "f", "bt") });
}

// ===================================================================== 19. Ukuran situs (garis asli)
{
  const s = base("Is it robust?", "Bigger sites make demand-only riskier; demand within headroom always stays ahead of headroom-only", {
    notes: `Feasibility thresholds 120, 240, 480, 960 kVA. Demand-only infeasible sites: ${B.feas.map((r) => r.demand.infeas).join(", ")}. Demand within headroom owners: ${B.feas.map((r) => r.dwh.owners).join(", ")}. Headroom-only stays at ${R.headroom.owners}.` });
  const labels = B.feas.map((r) => `${r.kva} kVA`);
  s.addChart(pres.charts.LINE, [
    { name: "Demand-only", labels, values: B.feas.map((r) => r.demand.owners) },
    { name: "Demand within headroom", labels, values: B.feas.map((r) => r.dwh.owners) },
    { name: "Headroom-only", labels, values: B.feas.map((r) => r.headroom.owners) }],
    { x: 0.5, y: 1.55, w: 7.8, h: 4.6, chartColors: [AMBER, TEAL, CORAL], lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 9,
      valAxisMinVal: 650, valAxisMaxVal: 850, valAxisMajorUnit: 50, valGridLine: { color: "E4E8EC", size: 0.75 }, catGridLine: { style: "none" },
      showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", catAxisLabelFontSize: 12, valAxisLabelFontSize: 11,
      catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", catAxisLabelColor: MUTED, valAxisLabelColor: MUTED,
      showTitle: true, title: "EV owners reached by 50 sites, by site size", titleFontSize: 13, titleColor: INK, titleFontFace: "+mn-lt",
      objectName: A(1, "f", "ch") });
  T(s, "Demand-only sites the grid cannot host", { x: 8.7, y: 1.6, w: 4, h: 0.4, fontSize: 14, bold: true, objectName: A(2, "f", "t") });
  for (let i = 0; i < B.feas.length; i++) {
    const r = B.feas[i], y = 2.15 + i * 0.95;
    T(s, `${r.kva} kVA`, { x: 8.7, y, w: 1.2, h: 0.6, fontSize: 13, valign: "middle", color: MUTED, objectName: A(i + 2, "f", "k") });
    for (let j = 0; j < r.demand.infeas; j++) {
      s.addImage({ data: await icon("FaTimes", INK), x: 9.9 + (j % 12) * 0.24, y: y + 0.18, w: 0.22, h: 0.22, objectName: A(i + 2, "f", "x") });
    }
    T(s, String(r.demand.infeas), { x: 9.9 + Math.min(r.demand.infeas, 12) * 0.24 + 0.08, y, w: 0.6, h: 0.6, fontSize: 16, bold: true, color: AMBER, valign: "middle", objectName: A(i + 2, "f", "n") });
  }
  box(s, 8.7, 6.0, 4.0, 0.8, TEAL_LT, { objectName: A(6, "f", "b") });
  T(s, "Demand within headroom: 0 at every size", { x: 8.9, y: 6.05, w: 3.7, h: 0.7, fontSize: 14, bold: true, color: TEAL, valign: "middle", objectName: A(6, "f", "bt") });
}

// ===================================================================== 20. Scorecard resolusi
{
  const s = base("Is it robust?", "Scorecard: what holds at 3, 5, 7 and 10 km", {
    notes: "Each column is the whole pipeline re-run at a different cell size, with the number of new sites held at 38 percent of the unserved pool. Two results are resolution-sensitive and are not used as headlines." });
  const cols = V.map((v) => `${Math.round(v.cell * 111)} km`);
  const rowsDef = [
    ["Spare capacity fails to predict chargers (AUC < 0.5)", V.map((v) => v.f1.auc.rel <= 0.5 ? "ok" : "no"), V.map((v) => f2(v.f1.auc.rel))],
    ["Owners outnumber chargers in high-demand, low-headroom cells", V.map((v) => v.hl.evp > v.hl.chgp ? "ok" : "no"), V.map((v) => `${(v.hl.evp / v.hl.chgp).toFixed(1)}×`)],
    ["Demand within headroom reaches more owners than headroom-only", V.map((v) => v.rules_prop.dwh.owners > v.rules_prop.headroom.owners ? "ok" : "no"), V.map((v) => `+${Math.round(100 * (v.rules_prop.dwh.owners / v.rules_prop.headroom.owners - 1))} %`)],
    ["Demand-only places infeasible sites", V.map((v) => v.rules_prop.demand.infeas > 0 ? "ok" : "warn"), V.map((v) => String(v.rules_prop.demand.infeas))],
    ["Headroom-only strands sites", V.map((v) => v.rules_prop.headroom.stranded > 0 ? "ok" : "warn"), V.map((v) => String(v.rules_prop.headroom.stranded))],
  ];
  const x0 = 0.6, lw = 5.4, cw = 1.65, y0 = 1.55;
  cols.forEach((c, j) => T(s, c, { x: x0 + lw + j * cw, y: y0, w: cw, h: 0.45, fontSize: 15, bold: true, align: "center", color: V[j].cell === 0.045 ? TEAL : INK }));
  T(s, "cell size →", { x: x0, y: y0, w: lw - 0.2, h: 0.45, fontSize: 12, color: MUTED, align: "right" });
  for (let i = 0; i < rowsDef.length; i++) {
    const r = rowsDef[i], y = y0 + 0.55 + i * 0.8;
    box(s, x0, y, 12.1, 0.7, i % 2 ? WHITE : LIGHT, { objectName: A(i + 1, "f", "row") });
    T(s, r[0], { x: x0 + 0.2, y, w: lw - 0.3, h: 0.7, fontSize: 14, valign: "middle", bold: true, objectName: A(i + 1, "f", "rl") });
    for (let j = 0; j < r[1].length; j++) {
      const st = r[1][j], ic = st === "ok" ? ["FaCheckCircle", TEAL] : st === "warn" ? ["FaExclamationTriangle", AMBER] : ["FaTimesCircle", CORAL];
      s.addImage({ data: await icon(ic[0], ic[1]), x: x0 + lw + j * cw + 0.25, y: y + 0.16, w: 0.38, h: 0.38, objectName: A(i + 1, "f", "ic") });
      T(s, r[2][j], { x: x0 + lw + j * cw + 0.7, y, w: 0.95, h: 0.7, fontSize: 14, valign: "middle", objectName: A(i + 1, "f", "v") });
    }
  }
  box(s, 0.6, 6.35, 12.1, 0.5, AMBER_LT, { objectName: A(6, "f", "n") });
  T(s, "⚠ Stranded-site counts and \"share of headroom in uncharged cells\" depend on the grid: reported as 5 km figures, not headlines.",
    { x: 0.85, y: 6.38, w: 11.7, h: 0.45, fontSize: 13, valign: "middle", objectName: A(6, "f", "nt") });
}

// ===================================================================== 21. Dua tingkat (ilustrasi hierarki)
{
  const s = base("Is it robust?", "Transformer and substation headroom are independent, so publish both levels", {
    notes: `Among ${TW.n} served cells linked to a primary substation: Spearman rho ${sg(TW.rho)} (95 percent CI ${sg(TW.rho_ci[0])} to ${sg(TW.rho_ci[1])}). ${TW.tight_tr_ample_gi} cells are tight at the transformer but ample at the substation, ${TW.ample_tr_tight_gi} the reverse. The earlier 51 percent discordance could not be reproduced; independence is the stronger, verified statement.` });
  const lv = [["FaIndustry", "Primary substation (GI)", "150/20 kV", INK], ["FaProjectDiagram", "Feeder", "20 kV (next step: 2,574 feeders)", BLUE], ["FaBolt", "Distribution transformer", "20 kV / LV", TEAL], ["FaChargingStation", "Charger", "4 × 60 kW site", AMBER]];
  for (let i = 0; i < lv.length; i++) {
    const y = 1.6 + i * 1.28;
    await iconDot(s, 0.8, y, 0.85, lv[i][0], lv[i][3], i + 1);
    T(s, [{ text: lv[i][1], options: { bold: true, breakLine: true } }, { text: lv[i][2], options: { color: MUTED, fontSize: 12 } }], { x: 1.8, y: y + 0.02, w: 3.2, h: 0.85, fontSize: 15, objectName: A(i + 1, "f", "l") });
    if (i < 3) s.addShape(pres.shapes.LINE, { x: 1.225, y: y + 0.88, w: 0, h: 0.38, line: { color: GREY, width: 2 }, objectName: A(i + 1, "f", "ln") });
  }
  pic(s, F3 + "fig9_two_levels.png", 5.2, 1.45, 4.6, 3.75, A(5, "f", "sc"));
  box(s, 10.0, 1.55, 2.7, 3.6, CORAL_LT, { objectName: A(6, "f", "rho") });
  T(s, `ρ = ${sg(TW.rho)}`, { x: 10.1, y: 1.75, w: 2.5, h: 0.8, fontSize: 30, bold: true, color: CORAL, align: "center", objectName: A(6, "f", "rv") });
  T(s, `95 % CI ${sg(TW.rho_ci[0])} to ${sg(TW.rho_ci[1])}\n${TW.n} served cells`, { x: 10.15, y: 2.6, w: 2.4, h: 0.8, fontSize: 12.5, align: "center", objectName: A(6, "f", "rc") });
  T(s, "one level tells you nothing about the other", { x: 10.15, y: 3.5, w: 2.4, h: 1.4, fontSize: 14, bold: true, align: "center", objectName: A(6, "f", "rm") });
  box(s, 5.2, 5.4, 7.5, 1.4, LIGHT, { objectName: A(7, "f", "w") });
  T(s, [{ text: `${TW.tight_tr_ample_gi} cells: `, options: { bold: true, color: CORAL } }, { text: "transformer full, substation free → a low-voltage map wrongly says \"avoid\".", options: { breakLine: true } },
        { text: `${TW.ample_tr_tight_gi} cells: `, options: { bold: true, color: CORAL } }, { text: "transformer free, substation full → a low-voltage map hides the real constraint." }],
    { x: 5.45, y: 5.5, w: 7.1, h: 1.2, fontSize: 14, valign: "middle", objectName: A(7, "f", "wt") });
}

// ===================================================================== 22. Kesiapan data (infografis batang ikon)
{
  const s = base("Is it robust?", "The register is not ready to publish, and ageing erodes headroom fast", {
    notes: `Shares of all ${f0(D.meta.total)} records. Growth correction at 3 percent per year pushes ${f0(D.scen[1].over)} transformers past the 80 percent limit. Field-staff names must be removed before any disclosure.` });
  T(s, `Share of ${f0(D.meta.total)} transformer records failing each check`, { x: 0.6, y: 1.45, w: 7.4, h: 0.4, fontSize: 14, color: MUTED });
  const checks = [["FaUserShield", "Field-staff names recorded", D.audit.pii], ["FaUnlink", "No link to a substation", D.audit.gi],
                  ["FaMapMarkerAlt", "Coordinates > 1 km off", D.audit.koord], ["FaTachometerAlt", "No load reading", D.audit.beban],
                  ["FaQuestionCircle", "No rated capacity", D.audit.kva]];
  for (let i = 0; i < checks.length; i++) {
    const y = 1.95 + i * 0.85;
    await iconDot(s, 0.6, y + 0.05, 0.55, checks[i][0], CORAL, i + 1);
    T(s, checks[i][1], { x: 1.3, y, w: 2.9, h: 0.65, fontSize: 14, valign: "middle", objectName: A(i + 1, "f", "l") });
    s.addShape(pres.shapes.RECTANGLE, { x: 4.2, y: y + 0.15, w: 3.0, h: 0.38, fill: { color: LIGHT }, line: { color: LIGHT } });
    s.addShape(pres.shapes.RECTANGLE, { x: 4.2, y: y + 0.15, w: 3.0 * checks[i][2] / 100, h: 0.38, fill: { color: CORAL }, line: { color: CORAL }, objectName: A(i + 1, "r", "b") });
    T(s, `${f1(checks[i][2])} %`, { x: 7.25, y, w: 0.9, h: 0.65, fontSize: 15, bold: true, color: CORAL, valign: "middle", objectName: A(i + 1, "f", "v") });
  }
  T(s, "Headroom at 80 % limit (MVA)", { x: 8.6, y: 1.45, w: 4.2, h: 0.4, fontSize: 14, color: MUTED });
  s.addChart(pres.charts.BAR, [
    { name: "Transformers", labels: ["as measured", "+3.0 %/yr", "+5.9 %/yr", "+9.7 %/yr"], values: D.scen.map((x) => Math.round(x.trafo)) },
    { name: "Substations (GI)", labels: ["as measured", "+3.0 %/yr", "+5.9 %/yr", "+9.7 %/yr"], values: D.scen.map((x) => Math.round(x.gi)) }],
    { x: 8.5, y: 1.85, w: 4.3, h: 4.1, barDir: "col", barGapWidthPct: 60, chartColors: [INK, GREY], showValue: true, dataLabelPosition: "outEnd",
      dataLabelFontSize: 9, dataLabelFontFace: "+mn-lt", dataLabelColor: INK, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      catAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", catAxisLabelColor: MUTED, showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: "+mn-lt",
      objectName: A(6, "f", "ch") });
  box(s, 0.6, 6.25, 12.1, 0.55, AMBER_LT, { objectName: A(7, "f", "n") });
  T(s, `At 3 %/yr growth, ${f0(D.scen[1].over)} transformers (17 % of usable records) pass the 80 % limit; GI headroom falls ${Math.round(100 * (1 - D.scen[1].gi / D.scen[0].gi))} %.`,
    { x: 0.85, y: 6.28, w: 11.7, h: 0.5, fontSize: 14, valign: "middle", objectName: A(7, "f", "nt") });
}

// ===================================================================== D4
await divider("What a DSO should publish", "04", "What a DSO should publish", "What would a capacity map need to show to steer capital toward the gaps, and how do we get there safely?", "FaBullhorn", CORAL,
  "Part four: implications.");

// ===================================================================== 23. Ledger klaim (lampu lalu lintas)
{
  const s = base("What a DSO should publish", "Claims ledger: what survived testing", {
    notes: "Green survives every test. Amber: true at 5 km and in direction, magnitude depends on the grid. Red: dropped from the earlier draft." });
  const rows = [["Roll-out follows grid size, not spare capacity", "AUC 0.86 vs 0.46; all resolutions", "ok"],
                ["High-demand, low-headroom cells are under-served", "owners 1.4–2.6× chargers' share", "ok"],
                ["Headroom-only reaches fewest owners", "+14 to +32 % for demand within headroom", "ok"],
                ["Headroom-only does least for the poorest regencies", "+5.1 vs +18.0 points (272 owners)", "ok"],
                ["Transformer and GI levels are independent", `ρ = ${sg(TW.rho)} (was "51 % discordant")`, "ok"],
                ["Demand-only places infeasible sites", "2 → 12 with site size; 0 at 10 km", "warn"],
                ["Headroom-only strands 30 % of sites", "19 / 15 / 0 / 4 by resolution", "warn"],
                ["Demand within headroom minimises regency Gini", "random and headroom-only are lower", "no"]];
  for (let i = 0; i < rows.length; i++) {
    const r = rows[i], y = 1.5 + i * 0.66;
    const ic = r[2] === "ok" ? ["FaCheckCircle", TEAL, "Holds"] : r[2] === "warn" ? ["FaExclamationTriangle", AMBER, "Depends on grid"] : ["FaTimesCircle", CORAL, "Dropped"];
    box(s, 0.6, y, 12.1, 0.58, i % 2 ? WHITE : LIGHT, { objectName: A(i + 1, "r", "r") });
    s.addImage({ data: await icon(ic[0], ic[1]), x: 0.75, y: y + 0.1, w: 0.38, h: 0.38, objectName: A(i + 1, "f", "i") });
    T(s, r[0], { x: 1.3, y, w: 5.6, h: 0.58, fontSize: 14, bold: true, valign: "middle", objectName: A(i + 1, "f", "c") });
    T(s, nb(r[1]), { x: 7.0, y, w: 3.9, h: 0.58, fontSize: 12.5, valign: "middle", color: MUTED, objectName: A(i + 1, "f", "e") });
    T(s, ic[2], { x: 10.95, y, w: 1.65, h: 0.58, fontSize: 13, bold: true, valign: "middle", color: ic[1], objectName: A(i + 1, "f", "s") });
  }
}

// ===================================================================== 24. Standar minimum (kartu ikon)
{
  const s = base("What a DSO should publish", "Five requirements for a publishable capacity map", {
    notes: "Each requirement is tied to one of the findings: independence of levels, ageing, the income result, staff names, and register quality." });
  const items = [["FaLayerGroup", "Two network levels", "Transformer + substation; feeder where available.", "levels independent: ρ ≈ 0", TEAL],
                 ["FaClock", "Growth-corrected", "A stated rate and survey date on every value.", "GI headroom −20 % at 3 %/yr", BLUE],
                 ["FaCarSide", "A demand layer", "Registered EV owners or predicted energy.", "+18 vs +5 pts for the poorest", AMBER],
                 ["FaThLarge", "Aggregated", "5 km cells or 2 km hexagons, never assets or people.", `${f1(D.audit.pii)} % of records name staff`, INK],
                 ["FaSyncAlt", "Versioned + scored", "Quarterly versions with a data-quality score.", "44 % lack a GI link", CORAL]];
  for (let i = 0; i < items.length; i++) {
    const it = items[i], x = 0.6 + i * 2.48;
    box(s, x, 1.6, 2.3, 5.15, LIGHT, { objectName: A(i + 1, "u", "c") });
    await iconDot(s, x + 0.65, 1.85, 1.0, it[0], it[4], i + 1);
    T(s, String(i + 1), { x: x + 0.15, y: 1.7, w: 0.5, h: 0.5, fontSize: 18, bold: true, color: it[4], objectName: A(i + 1, "f", "n") });
    T(s, it[1], { x: x + 0.15, y: 3.0, w: 2.0, h: 0.7, fontSize: 17, bold: true, align: "center", objectName: A(i + 1, "f", "t") });
    T(s, it[2], { x: x + 0.15, y: 3.75, w: 2.0, h: 1.4, fontSize: 13, align: "center", objectName: A(i + 1, "f", "d") });
    s.addShape(pres.shapes.LINE, { x: x + 0.3, y: 5.3, w: 1.7, h: 0, line: { color: GREY, width: 1 } });
    T(s, nb(it[3]), { x: x + 0.15, y: 5.4, w: 2.0, h: 1.2, fontSize: 12.5, bold: true, color: it[4], align: "center", objectName: A(i + 1, "f", "e") });
  }
}

// ===================================================================== 25. Pengganti unbundling
{
  const s = base("What a DSO should publish", "Publication does what unbundling does, without changing ownership", {
    notes: "Europe separates the DSO from charging partly because the DSO would hold this information. Indonesia chose integration. Publishing both surfaces removes the asymmetry and steers private capital to the gaps." });
  const st = [["FaLock", "Information asymmetry", "PLN can site chargers using data private CPOs cannot see.", CORAL],
              ["FaUnlock", "Open both surfaces", "Headroom + demand, two levels, open to every applicant.", TEAL],
              ["FaHandHoldingUsd", "Capital follows gaps", "Public and private money aims at unserved owners.", INK],
              ["FaBalanceScale", "Fairer coverage", "Poorest regencies gain most under the two-surface rule.", AMBER]];
  for (let i = 0; i < st.length; i++) {
    const x = 0.6 + i * 3.15;
    await iconDot(s, x + 0.75, 1.8, 1.3, st[i][0], st[i][3], i + 1);
    T(s, st[i][1], { x: x - 0.1, y: 3.25, w: 3.0, h: 0.55, fontSize: 18, bold: true, align: "center", objectName: A(i + 1, "f", "t") });
    T(s, st[i][2], { x: x + 0.05, y: 3.85, w: 2.7, h: 1.2, fontSize: 13.5, align: "center", color: MUTED, objectName: A(i + 1, "f", "d") });
    if (i < 3) arrowR(s, x + 2.4, 2.3, 0.7, GREY, i + 1);
  }
  box(s, 0.6, 5.4, 12.1, 1.35, LIGHT, { objectName: A(5, "f", "b") });
  await iconBare(s, 0.85, 5.65, 0.6, "FaGlobeEurope", MUTED, 5);
  T(s, "EU DSOs are generally barred from owning charge points because of this advantage. Where the DSO is also the CPO, disclosure has to do the work that separation does in Europe.",
    { x: 1.65, y: 5.5, w: 10.8, h: 1.15, fontSize: 15, valign: "middle", objectName: A(5, "f", "bt") });
}

// ===================================================================== 26. Roadmap (timeline)
{
  const s = base("What a DSO should publish", "A phased path to an open two-surface map (proposed)", {
    notes: "A proposal derived from the findings, for discussion with PLN UID Jawa Barat; not an agreed plan. Cleaning comes first, because publishing the raw register would misdirect capital and expose staff names." });
  s.addShape(pres.shapes.LINE, { x: 0.9, y: 2.55, w: 11.6, h: 0, line: { color: GREY, width: 3 }, objectName: A(1, "r", "tl") });
  const ph = [["FaBroom", "Phase 0", "Clean", [`Strip staff names (${f1(D.audit.pii)} %)`, "Link records to GI (44 % missing)", "Fix coordinates (43 % > 1 km)"], AMBER],
              ["FaMap", "Phase 1", "Publish two surfaces", ["5 km cells, transformer + GI", "Growth-corrected and dated", "Owner counts as demand layer"], TEAL],
              ["FaLayerGroup", "Phase 2", "Deepen", ["Add the feeder level", "Quarterly versions", "Published quality score"], BLUE],
              ["FaSyncAlt", "Phase 3", "Close the loop", ["Link to connection requests", "Track where sites go", "Monitor poorest-third coverage"], INK]];
  for (let i = 0; i < ph.length; i++) {
    const x = 0.75 + i * 3.1;
    await iconDot(s, x + 0.85, 2.0, 1.1, ph[i][0], ph[i][4], i + 2);
    T(s, [{ text: ph[i][1], options: { color: ph[i][4], breakLine: true, fontSize: 13 } }, { text: ph[i][2], options: { bold: true, fontSize: 18 } }],
      { x, y: 3.25, w: 2.8, h: 0.9, align: "center", objectName: A(i + 2, "f", "t") });
    box(s, x, 4.2, 2.8, 2.0, LIGHT, { objectName: A(i + 2, "f", "c") });
    T(s, ph[i][3].map((t, j) => ({ text: nb(t), options: { bullet: true, breakLine: j < 2 } })), { x: x + 0.15, y: 4.35, w: 2.55, h: 1.8, fontSize: 13, paraSpaceAfter: 6, objectName: A(i + 2, "f", "l") });
  }
  T(s, "Success measure: coverage in the poorest third of regencies rises at least as fast as in the richest third.", { x: 0.6, y: 6.35, w: 12.1, h: 0.45, fontSize: 15, bold: true, color: TEAL, objectName: A(6, "f", "m") });
}

// ===================================================================== 27. Keterbatasan
{
  const s = base("What a DSO should publish", "What this evidence does not show", { notes: "Be explicit about proxies and sample size. The equity result is a direction, not a precise estimate." });
  const lim = [["FaTachometerAlt", "Two spot readings per transformer", "a planning proxy, not a hosting-capacity calculation"],
               ["FaCarSide", "Registered owners as demand", "misses households without a home charger"],
               ["FaUsers", "272 owners in the poorest third", "181 in one regency: direction, not precision"],
               ["FaChartLine", "One growth rate for the province", "unit-level rates would sharpen the ageing correction"],
               ["FaProjectDiagram", "No feeder level yet", "2,574 feeders are the next layer"],
               ["FaCity", "Regency expenditure is an area measure", "it does not describe the owners themselves"]];
  for (let i = 0; i < lim.length; i++) {
    const x = 0.6 + (i % 2) * 6.15, y = 1.6 + Math.floor(i / 2) * 1.75;
    box(s, x, y, 5.95, 1.55, LIGHT, { objectName: A(i + 1, "f", "c") });
    await iconDot(s, x + 0.25, y + 0.38, 0.8, lim[i][0], MUTED, i + 1);
    T(s, [{ text: lim[i][1], options: { bold: true, breakLine: true } }, { text: lim[i][2], options: { color: MUTED, fontSize: 13.5 } }],
      { x: x + 1.25, y: y + 0.2, w: 4.55, h: 1.2, fontSize: 16, valign: "middle", objectName: A(i + 1, "f", "t") });
  }
}

// ===================================================================== 28. Penutup (hero)
{
  n += 1;
  const s = pres.addSlide({ sectionTitle: sec("What a DSO should publish") });
  s.background = { color: INK };
  pic(s, F4 + "hero_map.png", 7.4, 1.1, 5.7, 3.9, A(1, "f", "hero"));
  T(s, "The capacity map is a planning decision disguised as a data product.", { x: 0.8, y: 0.9, w: 6.6, h: 1.9, fontSize: 32, bold: true, color: WHITE });
  const pts = [["FaBolt", CORAL, `Headroom alone: ${R.headroom.owners} owners, +${f1(gP("headroom"))} pts for the poorest third.`],
               ["FaLayerGroup", TEAL, `Headroom + demand: ${R.dwh.owners} owners, every site connectable, +${f1(gP("dwh"))} pts for the poorest third.`],
               ["FaUnlock", AMBER, "Two levels, growth-corrected, quality-scored: from data every DSO already holds."]];
  for (let i = 0; i < pts.length; i++) {
    const y = 3.1 + i * 1.05;
    await iconDot(s, 0.8, y, 0.65, pts[i][0], pts[i][1], i + 2);
    T(s, pts[i][2], { x: 1.65, y: y - 0.05, w: 5.6, h: 0.85, fontSize: 16, color: SOFT, valign: "middle", objectName: A(i + 2, "f", "t") });
  }
  T(s, "Qashtalani Haramaini · Alyas Widita · Liz Taylor  |  qashtalani.haramaini@monash.edu", { x: 0.8, y: 6.5, w: 11.5, h: 0.4, fontSize: 13, color: AMBER });
  T(s, String(n), { x: 12.2, y: 7.02, w: 0.5, h: 0.28, fontSize: 10, color: "8FA3B5", align: "right" });
  s.addNotes("Close on the policy point: in a vertically integrated utility, publishing both surfaces is the functional substitute for unbundling. Then take questions; the claims ledger slide is the best backup.");
}

await pres.writeFile({ fileName: OUT });
if (process.env.APPLY_THEME) await require(process.env.APPLY_THEME).applyTheme(OUT, THEME);
console.log("written", OUT, "slides", n);
})().catch((e) => { console.error(e); process.exit(1); });
