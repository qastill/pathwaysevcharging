// Menurunkan bauran energi & faktor emisi dari data kapasitas pembangkit.
// Jalankan: node analysis/carbon.mjs  -> analysis/carbon.json
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');

// Asumsi teknis — SEMUANYA parameter, bukan hasil pengukuran.
// EF  = faktor emisi pembakaran, tCO2 per MWh listrik yang dibangkitkan.
// CF  = capacity factor tahunan (fraksi jam setahun setara beban penuh).
// derate = pengali kapasitas terpasang -> kapasitas efektif AC (MWp surya -> MW AC).
const TECH = {
  PLTU:         { ef: 1.00, cf: 0.70, derate: 1.00, label: 'Batu bara (uap)',        renew: false },
  PLTGU:        { ef: 0.40, cf: 0.50, derate: 1.00, label: 'Gas siklus kombinasi',   renew: false },
  PLTG:         { ef: 0.58, cf: 0.15, derate: 1.00, label: 'Gas siklus terbuka',     renew: false },
  PLTMG:        { ef: 0.55, cf: 0.40, derate: 1.00, label: 'Mesin gas',              renew: false },
  PLTD:         { ef: 0.75, cf: 0.20, derate: 1.00, label: 'Diesel',                 renew: false },
  PLTA:         { ef: 0.00, cf: 0.35, derate: 1.00, label: 'Air (besar)',            renew: true  },
  PLTM:         { ef: 0.00, cf: 0.45, derate: 1.00, label: 'Air (mini)',             renew: true  },
  PLTMH:        { ef: 0.00, cf: 0.45, derate: 1.00, label: 'Air (mikro)',            renew: true  },
  PLTP:         { ef: 0.05, cf: 0.85, derate: 1.00, label: 'Panas bumi',             renew: true  },
  PLTS:         { ef: 0.00, cf: 0.16, derate: 0.83, label: 'Surya',                  renew: true  },
  PLTB:         { ef: 0.00, cf: 0.25, derate: 1.00, label: 'Bayu',                   renew: true  },
  PLTSA:        { ef: 0.40, cf: 0.70, derate: 1.00, label: 'Sampah',                 renew: false },
  PLTBG:        { ef: 0.00, cf: 0.70, derate: 1.00, label: 'Biogas',                 renew: true  },
  'PLT BIOMASS':{ ef: 0.00, cf: 0.70, derate: 1.00, label: 'Biomassa',               renew: true  },
};
const HOURS = 8760;

function loadWindowScript(file) {
  const ctx = { window: {} };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(file, 'utf8'), ctx);
  return ctx.window[Object.keys(ctx.window)[0]];
}

const num = v => { const n = parseFloat(v); return Number.isFinite(n) ? n : 0; };

function mixFor(features) {
  const by = {};
  for (const f of features) {
    const t = (f.properties.type || '').trim().toUpperCase();
    const spec = TECH[t];
    if (!spec) continue;
    const mw = num(f.properties.capacity_mw) * spec.derate;
    const gwh = mw * spec.cf * HOURS / 1000;
    by[t] ??= { type: t, label: spec.label, renew: spec.renew, units: 0, mw: 0, gwh: 0, tco2: 0 };
    by[t].units += 1;
    by[t].mw += mw;
    by[t].gwh += gwh;
    by[t].tco2 += gwh * 1000 * spec.ef;
  }
  const rows = Object.values(by).sort((a, b) => b.gwh - a.gwh);
  const gwh = rows.reduce((a, r) => a + r.gwh, 0);
  const tco2 = rows.reduce((a, r) => a + r.tco2, 0);
  const mw = rows.reduce((a, r) => a + r.mw, 0);
  return {
    rows: rows.map(r => ({
      ...r, mw: Math.round(r.mw), gwh: Math.round(r.gwh),
      tco2: Math.round(r.tco2),
      share_mw: +(100 * r.mw / mw).toFixed(1),
      share_gwh: +(100 * r.gwh / gwh).toFixed(1),
    })),
    total_mw: Math.round(mw),
    total_gwh: Math.round(gwh),
    total_tco2: Math.round(tco2),
    ef_kg_per_kwh: +(tco2 / (gwh * 1000)).toFixed(4),   // tCO2/MWh == kgCO2/kWh
    renew_share_gwh: +(100 * rows.filter(r => r.renew).reduce((a, r) => a + r.gwh, 0) / gwh).toFixed(1),
    renew_share_mw: +(100 * rows.filter(r => r.renew).reduce((a, r) => a + r.mw, 0) / mw).toFixed(1),
  };
}

const dir = path.join(root, 'data/grid-id');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.js')).sort();
const all = [], perSystem = {};
for (const file of files) {
  const D = loadWindowScript(path.join(dir, file));
  const g = D.generators?.features ?? [];
  all.push(...g);
  const sys = g[0]?.properties.system ?? file;
  perSystem[sys] = mixFor(g);
}
const jamali = loadWindowScript(path.join(dir, 'data_jamali.js')).generators.features;
const jabar = jamali.filter(f => /jawa barat|banten|dki/i.test(f.properties.province || ''));

const out = {
  generated_at: new Date().toISOString().slice(0, 10),
  assumptions: { hours_per_year: HOURS, tech: TECH },
  national: mixFor(all),
  jamali: mixFor(jamali),
  jamali_west: mixFor(jabar),           // Jabar + Banten + DKI: wilayah pasok Jawa bagian barat
  by_system: perSystem,
};
fs.writeFileSync(path.join(root, 'analysis/carbon.json'), JSON.stringify(out, null, 2));

const p = (t, m) => {
  console.log(`\n=== ${t} — ${m.total_mw.toLocaleString()} MW → est. ${m.total_gwh.toLocaleString()} GWh/thn`);
  console.log(`    Faktor emisi: ${m.ef_kg_per_kwh} kgCO2/kWh | EBT: ${m.renew_share_gwh}% energi (${m.renew_share_mw}% kapasitas)`);
  for (const r of m.rows.slice(0, 8))
    console.log(`      ${r.type.padEnd(12)} ${String(r.units).padStart(3)} unit ${String(r.mw).padStart(7)} MW  ${String(r.gwh).padStart(7)} GWh  ${String(r.share_gwh).padStart(5)}% energi`);
};
p('NASIONAL', out.national);
p('JAMALI', out.jamali);
p('JAWA BARAT+BANTEN+DKI', out.jamali_west);
