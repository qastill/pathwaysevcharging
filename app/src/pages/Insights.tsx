import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '../components/ui';
import { StationCard } from '../components/Cards';
import Hours from '../components/Hours';
import { useData } from '../hooks';
import { useStore } from '../store';
import { num, rp } from '../lib/format';

export default function Insights() {
  const d = useData(); const nav = useNavigate();
  const { t, lang, location } = useStore(s => ({ t: s.t, lang: s.lang, location: s.location }));
  const prov = useMemo(() => { if (!d) return []; const m: Record<string, number> = {}; d.stations.forEach(s => (m[s.province] = (m[s.province] || 0) + 1)); return Object.entries(m).sort((a, b) => b[1] - a[1]); }, [d]);
  if (!d) return <div className="content"><div className="skeleton" style={{ height: 300 }} /></div>;
  const m = d.meta; const all = m.monthly; const full = all.length > 1 && all[all.length - 1].kwh < 0.5 * all[all.length - 2].kwh ? all.slice(0, -1) : all; const months = full.slice(-15); const mx = Math.max(...months.map(x => x.kwh));
  const top = d.stations.filter(s => s.stats).slice(0, 8);
  return (
    <div className="page">
      <TopBar title={t('insights')} line />
      <div className="content">
        <div className="grid2">
          <div className="stat g"><div className="n">{num(m.counts.stations)}</div><div className="l">SPKLU · {m.counts.provinces} {lang === 'en' ? 'provinces' : 'provinsi'}</div></div>
          <div className="stat"><div className="n">{num(m.counts.dc)}</div><div className="l">DC fast charging</div></div>
          <div className="stat"><div className="n">{num(months[months.length - 1].trx)}</div><div className="l">{lang === 'en' ? 'sessions, ' : 'sesi, '}{months[months.length - 1].month} {months[months.length - 1].year} ({lang === 'en' ? 'national' : 'nasional'})</div></div>
          <div className="stat"><div className="n">{num(months[months.length - 1].kwh / 1e6, 1)} GWh</div><div className="l">{lang === 'en' ? 'sold, ' : 'terjual, '}{months[months.length - 1].month} {months[months.length - 1].year}</div></div>
        </div>
        <div className="card">
          <h3 style={{ marginBottom: 8 }}>{t('monthly_kwh')}</h3>
          <div className="bar">{months.map(x => <div key={x.year + x.month} style={{ height: (x.kwh / mx) * 100 + '%' }} title={`${x.month} ${x.year}: ${num(x.kwh)} kWh`} />)}</div>
          <div className="hours-x"><span>{months[0].month.slice(0, 3)} {months[0].year}</span><span>{months[months.length - 1].month.slice(0, 3)} {months[months.length - 1].year}</span></div>
          <div className="xs mut" style={{ marginTop: 6 }}>{lang === 'en' ? 'Energy sold grew' : 'Energi terjual tumbuh'} {num(months[months.length - 1].kwh / months[0].kwh, 1)}× {lang === 'en' ? `in ${months.length - 1} months` : `dalam ${months.length - 1} bulan`}.</div>
        </div>
        <div className="card"><h3 style={{ marginBottom: 8 }}>{t('peak')}</h3><Hours hours={m.hoursAll} nowH={new Date().getHours()} /><div className="xs mut" style={{ marginTop: 6 }}>{lang === 'en' ? 'Median session' : 'Sesi median'}: {m.session.medianKwh} kWh · {m.session.medianMin} {lang === 'en' ? 'min' : 'mnt'} · {lang === 'en' ? 'avg price' : 'harga rata-rata'} {rp(m.tariff.avgAllIn)}/kWh</div></div>
        <div className="card">
          <h3 style={{ marginBottom: 8 }}>{t('by_province')}</h3>
          {prov.slice(0, 12).map(([p, n]) => <div key={p} className="row" style={{ padding: '3px 0' }}><span className="small" style={{ width: 130 }}>{p}</span><div className="grow" style={{ height: 10, background: 'var(--line2)', borderRadius: 5 }}><div style={{ width: (n / prov[0][1]) * 100 + '%', height: '100%', background: 'var(--g)', borderRadius: 5 }} /></div><span className="small b" style={{ width: 40, textAlign: 'right' }}>{n}</span></div>)}
        </div>
        <h3>{t('top_jabar')}</h3>
        {top.map(s => <StationCard key={s.id} s={s} meta={m} loc={location} nowH={new Date().getHours()} onClick={() => nav('/s/' + s.id)} />)}
        <div className="xs mut">{t('data_note')}</div>
      </div>
    </div>
  );
}
