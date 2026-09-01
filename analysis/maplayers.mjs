// Menyiapkan lapisan peta jaringan (pembangkit, transmisi, gardu induk) untuk tab EV × Jaringan.
import fs from 'node:fs'; import path from 'node:path'; import vm from 'node:vm';
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const load = f => { const c={window:{}}; vm.createContext(c); vm.runInContext(fs.readFileSync(f,'utf8'),c); return c.window[Object.keys(c.window)[0]]; };
const num = v => { const n=parseFloat(v); return Number.isFinite(n)?n:0; };
const r4 = v => Math.round(v*1e4)/1e4;

const dir = path.join(root,'data/grid-id');
const files = fs.readdirSync(dir).filter(f=>f.endsWith('.js')).sort();

// kotak Jawa bagian barat + margin (peta tab fokus Jabar)
const BBOX = { s:-8.2, n:-5.2, w:104.8, e:109.8 };
const inBox = (lat,lon) => lat>BBOX.s && lat<BBOX.n && lon>BBOX.w && lon<BBOX.e;

const gens=[], subs=[], lines=[];
for (const f of files) {
  const D = load(path.join(dir,f));
  for (const x of D.generators?.features ?? []) {
    const [lon,lat] = x.geometry.coordinates;
    if (!inBox(lat,lon)) continue;
    gens.push([r4(lat), r4(lon), (x.properties.type||'').toUpperCase(),
               Math.round(num(x.properties.capacity_mw)), x.properties.name||'',
               x.properties.status||'']);
  }
  for (const x of D.substations?.features ?? []) {
    const [lon,lat] = x.geometry.coordinates;
    if (!inBox(lat,lon)) continue;
    subs.push([r4(lat), r4(lon), Math.round(num(x.properties.capacity_mva)),
               x.properties.name||'', x.properties.voltage||'']);
  }
  for (const x of D.transmission?.features ?? []) {
    const cs = x.geometry.coordinates;
    if (!cs?.length) continue;
    // Buang simpul yang terlalu rapat (toleransi ~275 m) supaya payload ringan,
    // tetapi titik awal dan akhir selalu dipertahankan agar ruas pendek tidak hilang.
    const valid = cs.filter(([lon,lat]) => Number.isFinite(lat) && Number.isFinite(lon));
    if (valid.length < 2) continue;
    const pts=[]; let last=null;
    valid.forEach(([lon,lat], i) => {
      const isEnd = i === 0 || i === valid.length - 1;
      if (!isEnd && last && Math.abs(lat-last[0])<0.0025 && Math.abs(lon-last[1])<0.0025) return;
      last=[lat,lon]; pts.push([r4(lat), r4(lon)]);
    });
    if (pts.length<2) continue;
    if (!pts.some(p=>inBox(p[0],p[1]))) continue;
    lines.push([num(x.properties.voltage_kv_max), pts]);
  }
}
const out = { gens, subs, lines };
const s = JSON.stringify(out);
fs.writeFileSync(path.join(root,'analysis/maplayers.json'), s);
console.log('pembangkit:',gens.length,'| gardu induk:',subs.length,'| ruas transmisi:',lines.length,
            '| simpul:',lines.reduce((a,l)=>a+l[1].length,0));
console.log('ukuran payload:',(s.length/1024).toFixed(0),'KB');
const vc={}; lines.forEach(l=>vc[l[0]]=(vc[l[0]]||0)+1); console.log('kV:',vc);
