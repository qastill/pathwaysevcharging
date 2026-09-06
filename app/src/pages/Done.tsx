import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Check, Download, Star } from 'lucide-react';
import { useStore } from '../store';
import { ReviewForm } from '../components/Reviews';
import { rp, mins, num, longDate } from '../lib/format';
import { vehicleById } from '../vehicles';

export default function Done() {
  const { id } = useParams();
  const nav = useNavigate();
  const { t, lang, bookings, updateBooking, showToast } = useStore(s => ({ t: s.t, lang: s.lang, bookings: s.bookings, updateBooking: s.updateBooking, showToast: s.showToast }));
  const b = bookings.find(x => x.id === id);
  const [rev, setRev] = useState(false);
  if (!b || !b.session) return <div className="content"><div className="empty"><div className="ic">🔌</div>{t('no_active')}</div></div>;
  const s = b.session; const veh = vehicleById(b.vehicleId);
  const receipt = () => {
    const lines = [`NGECAS — ${t('receipt')}`, `${t('transaction')}: ${b.code}`, `${b.targetName}`, `${b.targetSub}`, `${t('date')}: ${longDate(s.endedAt || Date.now(), lang)}`, `${t('vehicle')}: ${veh.brand} ${veh.model}`, `${t('battery')}: ${b.startSoc}% → ${s.endSoc}%`, `kWh: ${num(s.kwh, 2)} @ ${rp(b.priceKwh)}/kWh`, `${t('duration')}: ${mins(s.minutes)}`, `${t('total')}: ${rp(s.cost)}`, `${t('payment')}: ${b.payment}`];
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' }); const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `ngecas-${b.code}.txt`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 2000);
    showToast(t('receipt') + ' ✓');
  };
  return (
    <div className="page" style={{ position: 'relative' }}>
      <div className="confetti">{Array.from({ length: 26 }).map((_, i) => <i key={i} style={{ left: (i * 37) % 100 + '%', background: ['#B8F55A', '#0E7A4A', '#F59E0B', '#2563EB'][i % 4], animationDelay: (i % 7) * 0.15 + 's' }} />)}</div>
      <div className="content" style={{ paddingTop: 'calc(40px + var(--sat))', textAlign: 'center' }}>
        <div className="check"><Check size={44} strokeWidth={3} /></div>
        <h1>{t('complete')}</h1>
        <div className="mut">{t('ready_to_go')}</div>
        <div className="grid3">
          <div className="stat g"><div className="n">{s.endSoc}%</div><div className="l">{t('battery')}</div></div>
          <div className="stat"><div className="n">{num(s.kwh, 1)}</div><div className="l">kWh</div></div>
          <div className="stat"><div className="n">{rp(s.cost, { compact: true })}</div><div className="l">{t('total')}</div></div>
        </div>
        <div className="card" style={{ textAlign: 'left' }}>
          <h3 style={{ marginBottom: 6 }}>{t('summary')}</h3>
          <div className="row" style={{ padding: '8px 0' }}><span style={{ fontSize: 26 }}>{b.kind === 'host' ? '🏠' : '⚡'}</span><div><div className="b">{b.targetName}</div><div className="xs mut">{b.targetSub}</div></div></div>
          <div className="kv"><span className="k">{t('date')}</span><span className="v">{longDate(s.endedAt || s.startedAt, lang)}</span></div>
          <div className="kv"><span className="k">{t('duration')}</span><span className="v">{mins(s.minutes)}</span></div>
          <div className="kv"><span className="k">{t('battery')}</span><span className="v">{b.startSoc}% → {s.endSoc}%</span></div>
          <div className="kv"><span className="k">{t('energy')}</span><span className="v">{num(s.kwh, 2)} kWh × {rp(b.priceKwh)}</span></div>
          <div className="kv"><span className="k">{t('range_added')}</span><span className="v">≈ {s.km} km</span></div>
          <div className="kv"><span className="k">{t('co2')}</span><span className="v" style={{ color: 'var(--g)' }}>{num(s.co2Saved, 1)} kg</span></div>
          <div className="kv"><span className="k">{t('payment')}</span><span className="v">{b.payment}</span></div>
          <div className="kv"><span className="k">{t('transaction')}</span><span className="v">{b.code}</span></div>
        </div>
        <button className="btn ghost full" onClick={receipt}><Download size={16} /> {t('receipt')}</button>
        {!b.reviewed && <button className="btn sec full" onClick={() => setRev(true)}><Star size={16} /> {t('leave_review')}</button>}
        <button className="btn lg full" onClick={() => nav('/', { replace: true })}>{t('done')}</button>
      </div>
      <ReviewForm targetId={b.targetId} open={rev} onClose={() => setRev(false)} onDone={() => updateBooking(b.id, { reviewed: true })} />
    </div>
  );
}
