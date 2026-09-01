// Menggabungkan hasil karbon, harga, dan lapisan peta menjadi satu payload D.grid2.
import fs from 'node:fs'; import path from 'node:path';
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const rd = f => JSON.parse(fs.readFileSync(path.join(root, 'analysis', f), 'utf8'));

const C = rd('carbon.json'), P = rd('price.json'), M = rd('maplayers.json');

const slim = m => ({
  ef: m.ef_kg_per_kwh, mw: m.total_mw, gwh: m.total_gwh, tco2: m.total_tco2,
  renew_gwh: m.renew_share_gwh, renew_mw: m.renew_share_mw,
  rows: m.rows.map(r => ({ t: r.type, l: r.label, u: r.units, mw: r.mw, gwh: r.gwh,
                           smw: r.share_mw, sg: r.share_gwh, re: r.renew })),
});

const out = {
  carbon: {
    national: slim(C.national),
    jamali: slim(C.jamali),
    west: slim(C.jamali_west),
    tech: Object.fromEntries(Object.entries(C.assumptions.tech)
      .map(([k, v]) => [k, { ef: v.ef, cf: v.cf, derate: v.derate, l: v.label, re: v.renew }])),
    ev: P.carbon,
  },
  price: { ...P.price, pemda: P.pemda, tiers: P.tiers, hours: P.hours,
           night: P.night_share, cost: P.cost, assume: P.assume },
  map: M,
};
const s = JSON.stringify(out);
fs.writeFileSync(path.join(root, 'analysis/grid2.json'), s);
console.log('grid2.json:', (s.length / 1024).toFixed(0), 'KB');
