import { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Zap, Square } from 'lucide-react';
import { TopBar } from '../components/ui';
import { useData } from '../hooks';
import { useStore } from '../store';
import { rp, mins, num } from '../lib/format';
import { vehicleById } from '../vehicles';
import { co2Saved } from '../lib/model';

// Accelerated simulation: 1 real second = 1 charging minute. Replace `tick` with an OCPP/operator feed for production.
export default function Session() {
  const { id } = useParams();
  const nav = useNavigate();
  const d = useData();
  const { t, bookings, updateBooking } = useStore(s => ({ t: s.t, bookings: s.bookings, updateBooking: s.updateBooking }));
  const b = bookings.find(x => x.id === id);
  const veh = vehicleById(b?.vehicleId || '');
  const [sim, setSim] = useState<{ soc: number; kwh: number; min: number; kw: number }>(() => ({ soc: b?.startSoc || 20, kwh: 0, min: 0, kw: 0 }));
  const raf = useRef<number>();
  useEffect(() => { if (b && b.status === 'upcoming') updateBooking(b.id, { status: 'active', session: { startedAt: Date.now(), kwh: 0, cost: 0, minutes: 0, endSoc: b.startSoc, km: 0, co2Saved: 0 } }); if (b && b.status === 'active' && !b.session) updateBooking(b.id, { session: { startedAt: Date.now(), kwh: 0, cost: 0, minutes: 0, endSoc: b.startSoc, km: 0, co2Saved: 0 } }); }, []); // eslint-disable-line
  useEffect(() => {
    if (!b || b.status !== 'active') return;
    const dc = b.plug !== 'Type 2'; const maxKw = b.kw || (dc ? Math.min(veh.dc, 50) : Math.min(veh.ac, 7));
    let last = performance.now();
    const step = (now: number) => {
      const dtMin = (now - last) / 1000; last = now; // 1 s real = 1 min sim
      setSim(s => {
        if (s.soc >= b.targetSoc) return s;
        const kw = dc && s.soc >= 80 ? maxKw * Math.max(0.25, 1 - (s.soc - 80) / 25) : dc && s.soc < 10 ? maxKw * 0.7 : maxKw;
        const dk = (kw * 0.93 * dtMin) / 60; const soc = Math.min(b.targetSoc, s.soc + (dk / veh.battery) * 100);
        return { soc, kwh: s.kwh + dk, min: s.min + dtMin, kw };
      });
      raf.current = requestAnimationFrame(step);
    };
    raf.current = requestAnimationFrame(step);
    return () => { if (raf.current) cancelAnimationFrame(raf.current); };
  }, [b?.id, b?.status]); // eslint-disable-line
  const finish = () => {
    if (!b || !d) return;
    const cost = Math.round(sim.kwh * b.priceKwh * (b.kind === 'host' ? 1.05 : 1));
    const c = co2Saved(sim.kwh, d.meta);
    updateBooking(b.id, { status: 'completed', session: { startedAt: b.session?.startedAt || Date.now(), endedAt: Date.now(), kwh: Math.round(sim.kwh * 100) / 100, cost, minutes: Math.round(sim.min), endSoc: Math.round(sim.soc), km: Math.round(c.km), co2Saved: Math.round(c.kg * 10) / 10 } });
    nav('/done/' + b.id, { replace: true });
  };
  useEffect(() => { if (b && b.status === 'active' && sim.soc >= b.targetSoc && sim.min > 0) finish(); }, [sim.soc]); // eslint-disable-line
  if (!b) return <div className="content"><TopBar title={t('charging')} /><div className="empty"><div className="ic">🔌</div>{t('no_active')}</div></div>;
  if (b.status === 'completed') { nav('/done/' + b.id, { replace: true }); return null; }
  const pct = Math.round(sim.soc); const r = 96, C = 2 * Math.PI * r;
  const remainingKwh = Math.max(0, ((b.targetSoc - sim.soc) / 100) * veh.battery);
  const eta = sim.kw > 0 ? (remainingKwh / (sim.kw * 0.93)) * 60 : 0;
  const cost = sim.kwh * b.priceKwh * (b.kind === 'host' ? 1.05 : 1);
  return (
    <div className="page">
      <div className="hero" style={{ paddingBottom: 26 }}>
        <div className="row sp" style={{ marginBottom: 14 }}><span className="b" style={{ fontSize: 18 }}>{t('charging')}</span><span className="pill">{b.code}</span></div>
        <div className="ring">
          <svg width="220" height="220"><circle cx="110" cy="110" r={r} stroke="rgba(255,255,255,.18)" strokeWidth="14" fill="none" /><circle cx="110" cy="110" r={r} stroke="#B8F55A" strokeWidth="14" fill="none" strokeLinecap="round" strokeDasharray={C} strokeDashoffset={C * (1 - sim.soc / 100)} style={{ transition: 'stroke-dashoffset .3s' }} /></svg>
          <div className="c" style={{ color: '#fff' }}><div className="pct">{pct}<span style={{ fontSize: 24 }}>%</span></div><div className="small" style={{ opacity: .85 }}><Zap size={14} className="bolt" fill="#B8F55A" color="#B8F55A" style={{ verticalAlign: -2 }} /> {sim.kw > 0 ? num(sim.kw, 0) + ' kW' : t('preparing')}</div></div>
        </div>
        <div className="small" style={{ opacity: .9, textAlign: 'center', marginTop: 14 }}>{b.targetName}<br />{veh.brand} {veh.model} → {b.targetSoc}%{eta > 0 && <> · {t('ev_ready_at')} ≈ {mins(eta)}</>}</div>
      </div>
      <div className="content">
        <div className="grid3" style={{ width: '100%' }}>
          <div className="stat"><div className="n">{num(sim.kwh, 1)}</div><div className="l">kWh</div></div>
          <div className="stat"><div className="n">{mins(sim.min)}</div><div className="l">{t('elapsed')}</div></div>
          <div className="stat g"><div className="n">{rp(cost, { compact: true })}</div><div className="l">{t('est_cost')}</div></div>
        </div>
        <div className="card" style={{ width: '100%' }}>
          <div className="kv"><span className="k">{t('power')}</span><span className="v">{b.plug} · {b.kw} kW max</span></div>
          <div className="kv"><span className="k">{t('range_added')}</span><span className="v">≈ {Math.round(sim.kwh / veh.kwhKm)} km</span></div>
          <div className="kv"><span className="k">{t('payment')}</span><span className="v">{b.payment}</span></div>
        </div>
        <div className="xs mut" style={{ textAlign: 'center' }}>{t('demo_fast')}</div>
        <button className="btn lg danger full" onClick={finish}><Square size={16} fill="currentColor" /> {t('stop')}</button>
      </div>
    </div>
  );
}
