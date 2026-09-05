import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '../components/ui';
import { StationCard } from '../components/Cards';
import { useData } from '../hooks';
import { useStore } from '../store';
import { CITIES, distToSegM, distM } from '../lib/geo';
import { rp, num } from '../lib/format';
import { vehicleById } from '../vehicles';

export default function Trip() {
  const d = useData();
  const nav = useNavigate();
  const { t, lang, vehicleId, location } = useStore(s => ({ t: s.t, lang: s.lang, vehicleId: s.vehicleId, location: s.location }));
  const veh = vehicleById(vehicleId);
  const [kmMonth, setKmMonth] = useState(1200);
  const [from, setFrom] = useState('Jakarta'); const [to, setTo] = useState('Bandung');
  const [dcOnly, setDcOnly] = useState(true);
  const a = CITIES.find(c => c.name === from)!, b = CITIES.find(c => c.name === to)!;
  const corridor = useMemo(() => {
    if (!d) return [];
    return d.stations.filter(s => (!dcOnly || s.type === 'DC') && s.status !== 'unavailable' && s.status !== 'maintenance').map(s => ({ s, ...distToSegM(s, a, b) })).filter(x => x.d < 12000).sort((x, y) => x.t - y.t).slice(0, 40);
  }, [d, a, b, dcOnly]);
  if (!d) return <div className="content"><div className="skeleton" style={{ height: 300 }} /></div>;
  const m = d.meta; const kwh = kmMonth * veh.kwhKm;
  const spklu = kwh * m.tariff.avgAllIn, home = kwh * m.assume.tarif_rumah, ice = (kmMonth / m.assume.ice_kmpl) * m.assume.bbm;
  const co2 = (kmMonth * (m.assume.ice_g - m.carbon.ev_g_km)) / 1000;
  const dist = distM(a, b) * 1.25; // road factor
  const stops = Math.max(0, Math.ceil(dist / 1000 / (veh.range * 0.7)) - 1);
  return (
    <div className="page">
      <TopBar title={t('trip')} line />
      <div className="content">
        <div className="card">
          <h3>{t('cost_calc')}</h3><div className="xs mut" style={{ marginBottom: 8 }}>{veh.brand} {veh.model} · {veh.kwhKm} kWh/km</div>
          <label className="lbl">{num(kmMonth)} {t('km_month')}</label><input type="range" className="range" min={200} max={5000} step={100} value={kmMonth} onChange={e => setKmMonth(+e.target.value)} />
          <div className="col" style={{ marginTop: 12 }}>
            {[[t('at_home'), home, 'var(--g)'], [t('at_spklu'), spklu, 'var(--teal)'], [t('petrol'), ice, 'var(--red)']].map(([l, v, c]) => (
              <div key={l as string}><div className="row sp small"><span className="sb">{l}</span><span className="b">{rp(v as number)} {t('per_month')}</span></div><div style={{ height: 8, background: 'var(--line2)', borderRadius: 4, marginTop: 4 }}><div style={{ width: ((v as number) / ice) * 100 + '%', height: '100%', background: c as string, borderRadius: 4 }} /></div></div>
            ))}
          </div>
          <div className="grid2" style={{ marginTop: 12 }}>
            <div className="stat g"><div className="n">{rp(ice - spklu, { compact: true })}</div><div className="l">{lang === 'en' ? 'saved vs petrol (stations)' : 'hemat vs bensin (SPKLU)'}</div></div>
            <div className="stat"><div className="n">{num(co2, 0)} kg</div><div className="l">CO₂ {lang === 'en' ? 'avoided / month' : 'dihindari / bulan'}</div></div>
          </div>
          <div className="xs mut" style={{ marginTop: 8 }}>{lang === 'en' ? 'Assumptions' : 'Asumsi'}: SPKLU {rp(m.tariff.avgAllIn)}/kWh (observed), R-1 {rp(m.assume.tarif_rumah)}/kWh, {lang === 'en' ? 'petrol' : 'bensin'} {rp(m.assume.bbm)}/L @ {m.assume.ice_kmpl} km/L, grid {m.carbon.ef_jamali} kgCO₂/kWh.</div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 8 }}>{t('route')}</h3>
          <div className="grid2">
            <div className="field"><label className="lbl">{t('from')}</label><select className="input" value={from} onChange={e => setFrom(e.target.value)}>{CITIES.map(c => <option key={c.name}>{c.name}</option>)}</select></div>
            <div className="field"><label className="lbl">{t('to_')}</label><select className="input" value={to} onChange={e => setTo(e.target.value)}>{CITIES.map(c => <option key={c.name}>{c.name}</option>)}</select></div>
          </div>
          <div className="row sp" style={{ marginTop: 10 }}><span className="small sb">DC {lang === 'en' ? 'only' : 'saja'}</span><button className={'toggle' + (dcOnly ? ' on' : '')} onClick={() => setDcOnly(!dcOnly)} /></div>
          <div className="grid3" style={{ marginTop: 10 }}>
            <div className="stat"><div className="n">≈ {num(dist / 1000)}</div><div className="l">km</div></div>
            <div className="stat"><div className="n">{stops}</div><div className="l">{t('stops_needed')}</div></div>
            <div className="stat g"><div className="n">{corridor.length}</div><div className="l">{lang === 'en' ? 'chargers en route' : 'charger di rute'}</div></div>
          </div>
        </div>
        <div className="small mut">{t('corridor')}</div>
        {corridor.map(x => <StationCard key={x.s.id} s={x.s} meta={m} loc={location} nowH={new Date().getHours()} onClick={() => nav('/s/' + x.s.id)} />)}
      </div>
    </div>
  );
}
