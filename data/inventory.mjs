// Membaca seluruh dataset jaringan di data/ dan menulis ringkasan ke data/inventory.json.
// Jalankan: node data/inventory.mjs
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const here = path.dirname(new URL(import.meta.url).pathname);

function loadWindowScript(file) {
  const ctx = { window: {} };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(file, 'utf8'), ctx);
  const key = Object.keys(ctx.window)[0];
  return { key, data: ctx.window[key] };
}

const num = v => { const n = parseFloat(v); return Number.isFinite(n) ? n : 0; };
const bump = (o, k, v = 1) => { o[k] = (o[k] || 0) + v; };

// ---------- Indonesia ----------
const idDir = path.join(here, 'grid-id');
const regions = [];
const idFuel = {}, idFuelMw = {}, idProvinceGen = {}, idVoltage = {};
let idSub = 0, idSubMva = 0, idGen = 0, idGenMw = 0, idLine = 0, idLineKm = 0;

for (const file of fs.readdirSync(idDir).filter(f => f.endsWith('.js')).sort()) {
  const { key, data } = loadWindowScript(path.join(idDir, file));
  const subs = data.substations?.features ?? [];
  const gens = data.generators?.features ?? [];
  const lines = data.transmission?.features ?? [];

  const subMva = subs.reduce((a, f) => a + num(f.properties.capacity_mva), 0);
  const genMw = gens.reduce((a, f) => a + num(f.properties.capacity_mw), 0);
  const lineKm = lines.reduce((a, f) => a + num(f.properties.length_km), 0);

  for (const f of gens) {
    const t = (f.properties.type || 'TIDAK DIKETAHUI').trim().toUpperCase();
    bump(idFuel, t); bump(idFuelMw, t, num(f.properties.capacity_mw));
    bump(idProvinceGen, f.properties.province || 'n/a');
  }
  for (const f of lines) bump(idVoltage, f.properties.voltage_class || 'n/a');

  regions.push({
    file, global: key, system: subs[0]?.properties.system ?? gens[0]?.properties.system ?? null,
    substations: subs.length, substation_mva: Math.round(subMva),
    generators: gens.length, generator_mw: Math.round(genMw),
    transmission_lines: lines.length, transmission_km: Math.round(lineKm),
  });
  idSub += subs.length; idSubMva += subMva;
  idGen += gens.length; idGenMw += genMw;
  idLine += lines.length; idLineKm += lineKm;
}

// ---------- Dunia ----------
const { data: plants } = loadWindowScript(path.join(here, 'grid-world', 'world-plants.js'));
const { data: wgrid } = loadWindowScript(path.join(here, 'grid-world', 'world-grid.js'));

// plants.plants rows: [name, iso3, capacity_mw, lat, lon, fuelIndex]
const wFuel = {}, wFuelMw = {}, wCountryMw = {};
for (const [, iso, mw, , , fi] of plants.plants) {
  const fuel = plants.fuels[fi] ?? 'Unknown';
  bump(wFuel, fuel); bump(wFuelMw, fuel, num(mw)); bump(wCountryMw, iso, num(mw));
}
const idnPlants = plants.plants.filter(p => p[1] === 'IDN');

const sortDesc = o => Object.fromEntries(Object.entries(o).sort((a, b) => b[1] - a[1]));
const round = o => Object.fromEntries(Object.entries(o).map(([k, v]) => [k, Math.round(v)]));

const out = {
  generated_at: new Date().toISOString().slice(0, 10),
  indonesia: {
    totals: {
      substations: idSub, substation_mva: Math.round(idSubMva),
      generators: idGen, generator_mw: Math.round(idGenMw),
      transmission_lines: idLine, transmission_km: Math.round(idLineKm),
    },
    regions,
    generators_by_type: sortDesc(idFuel),
    generator_mw_by_type: round(sortDesc(idFuelMw)),
    generators_by_province: sortDesc(idProvinceGen),
    transmission_by_voltage_class: sortDesc(idVoltage),
  },
  world: {
    totals: {
      plants: plants.plants.length,
      countries: Object.keys(plants.countries).length,
      capacity_mw: Math.round(Object.values(wFuelMw).reduce((a, b) => a + b, 0)),
      interconnection_nodes: Object.keys(wgrid.nodes).length,
      interconnection_edges: wgrid.edges.length,
    },
    plants_by_fuel: sortDesc(wFuel),
    capacity_mw_by_fuel: round(sortDesc(wFuelMw)),
    top_countries_by_mw: Object.fromEntries(Object.entries(round(sortDesc(wCountryMw))).slice(0, 15)),
    indonesia_subset: {
      plants: idnPlants.length,
      capacity_mw: Math.round(idnPlants.reduce((a, p) => a + num(p[2]), 0)),
    },
  },
};

fs.writeFileSync(path.join(here, 'inventory.json'), JSON.stringify(out, null, 2));
console.log(JSON.stringify(out, null, 2));
