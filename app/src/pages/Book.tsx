import { useMemo, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { Zap, Info } from 'lucide-react';
import { TopBar } from '../components/ui';
import { useData, useAllHosts, useNow } from '../hooks';
import { useStore } from '../store';
import type { PlugType, Booking } from '../types';
import { rp, mins, num, isoDate, dateLabel, pad, uid, code, titleCase } from '../lib/format';
import { hoursFor, busyAt, slotOpen, hostOpen, estimateCharge, compatible, priceParts } from '../lib/model';
import { vehicleById } from '../vehicles';

const PAY = [['pln', 'PLN Mobile', '⚡'], ['qris', 'QRIS', '▦'], ['gopay', 'GoPay', '🟢'], ['ovo', 'OVO', '🟣'], ['card', 'Kartu kredit / debit', '💳']];

export default function Book() {
  const { kind, id } = useParams<{ kind: 'station' | 'host'; id: string }>();
  const [sp] = useSearchParams();
  const startNow = sp.get('now') === '1';
  const nav = useNavigate();
  const d = useData();
  const hosts = useAllHosts(d?.hosts);
  const now = useNow(10000);
  const { t, lang, vehicleId, addBooking, showToast } = useStore(s => ({ t: s.t, lang: s.lang, vehicleId: s.vehicleId, addBooking: s.addBooking, showToast: s.showToast }));
  const veh = vehicleById(vehicleId);
  const st = kind === 'station' ? d?.stations.find(x => x.id === id) : undefined;
  const hs = kind === 'host' ? hosts.find(x => x.id === id) : undefined;
  const plugs = useMemo(() => (st ? st.plugs : hs ? [{ type: 'Type 2' as PlugType, kw: hs.kw, n: 1, trx: 0 }] : []), [st, hs]);
  const [pi, setPi] = useState(() => Math.max(0, plugs.findIndex(p => compatible(veh, p.type))));
  const days = useMemo(() => Array.from({ length: 7 }, (_, i) => { const x = new Date(now); x.setDate(x.getDate() + i); return isoDate(x); }), [now]);
  const [date, setDate] = useState(days[0]);
  const [hour, setHour] = useState<number>(startNow ? now.getHours() : -1);
  const [soc, setSoc] = useState(25); const [target, setTarget] = useState(80);
  const [pay, setPay] = useState('pln');
  if (!d || (!st && !hs)) return <div className="content"><div className="skeleton" style={{ height: 300 }} /></div>;

  const plug = plugs[Math.min(pi, plugs.length - 1)] || plugs[0];
  const ok = compatible(veh, plug.type);
  const price = st ? st.priceKwh : hs!.priceKwh;
  const est = estimateCharge(veh, plug.kw, plug.type, soc, Math.max(soc + 1, target));
  const parts = st ? priceParts(price, d.meta, st.priceEstimated) : { energy: price, ppj: 0, ppjRate: 0 };
  const svc = hs ? Math.round(est.kwh * price * 0.05) : 0; // 5 % platform fee on P2P
  const cost = Math.round(est.kwh * price) + svc;
  const hours = st ? hoursFor(st, d.meta) : d.meta.hoursAll;
  const isToday = date === days[0];
  const nowH = now.getHours();
  const name = st ? titleCase(st.name) : hs!.name;
  const sub = st ? (st.city || st.province) : hs!.area;

  const slotState = (h: number): 'off' | 'ok' | 'past' => {
    if (isToday && h < nowH) return 'past';
    if (st) return slotOpen(st, date, h, hours) ? 'ok' : 'off';
    return hostOpen(hs!, date, h) ? 'ok' : 'off';
  };
  const confirm = () => {
    const hStart = startNow ? nowH : hour;
    const endMin = hStart * 60 + (startNow ? now.getMinutes() : 0) + est.minutes;
    const b: Booking = {
      id: uid(), code: code(), kind: kind!, targetId: id!, targetName: name, targetSub: sub, plug: plug.type, kw: est.kw || plug.kw, date, start: startNow ? pad(nowH) + ':' + pad(now.getMinutes()) : pad(hStart) + ':00',
      end: pad(Math.floor(endMin / 60) % 24) + ':' + pad(endMin % 60), startNow, startSoc: soc, targetSoc: target, estKwh: est.kwh, estCost: cost, priceKwh: price, payment: PAY.find(p => p[0] === pay)![1],
      status: startNow ? 'active' : 'upcoming', created: Date.now(), vehicleId,
    };
    addBooking(b);
    showToast(t('booked') + ' · ' + b.code);
    nav(startNow ? '/session/' + b.id : '/bookings', { replace: true });
  };

  return (
    <div className="page">
      <TopBar title={startNow ? t('charge_now') : t('booking')} line />
      <div className="content">
        <div className="card flat" style={{ background: 'var(--mint)', borderColor: 'transparent' }}>
          <div className="b">{name}</div><div className="small mut">{sub} · {plug.type} {Math.round(plug.kw)} kW</div>
        </div>

        <div className="card">
          <div className="row sp" style={{ marginBottom: 8 }}><h3>{t('vehicle')}</h3><button className="btn sm ghost" onClick={() => nav('/vehicle')}>{t('change')}</button></div>
          <div className="row"><span style={{ fontSize: 28 }}>🚗</span><div><div className="b">{veh.brand} {veh.model}</div><div className="xs mut">{veh.battery} kWh · {veh.plug} · AC {veh.ac} kW{veh.dc ? ` · DC ${veh.dc} kW` : ''}</div></div></div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 8 }}>{t('choose_plug')}</h3>
          <div className="col">
            {plugs.map((p, i) => { const c = compatible(veh, p.type); return (
              <button key={i} className="row" style={{ padding: 10, borderRadius: 12, border: '1.5px solid ' + (i === pi ? 'var(--g)' : 'var(--line)'), background: i === pi ? 'var(--mint)' : 'var(--card)', opacity: c ? 1 : .5, textAlign: 'left' }} onClick={() => c && setPi(i)}>
                <div className={'plugico' + (p.type !== 'Type 2' ? ' dc' : '')}>{p.type === 'Type 2' ? 'T2' : p.type === 'CCS2' ? 'CCS' : 'CHA'}</div>
                <div className="grow"><div className="b">{p.type} · {Math.round(p.kw)} kW</div><div className="xs mut">{c ? `${p.n} ${t('units')}` : t('not_compatible')}</div></div>
                {i === pi && c && <span className="pill g">✓</span>}
              </button>); })}
          </div>
        </div>

        {!startNow && (
          <div className="card">
            <h3 style={{ marginBottom: 8 }}>{t('choose_date')}</h3>
            <div className="chips">{days.map((x, i) => <button key={x} className={'datechip' + (date === x ? ' on' : '')} onClick={() => { setDate(x); setHour(-1); }}><small>{i === 0 ? t('today') : i === 1 ? t('tomorrow') : dateLabel(x, lang).split(' ')[0]}</small><span>{new Date(x + 'T00:00:00').getDate()}</span><small>{dateLabel(x, lang).split(' ').slice(-1)[0]}</small></button>)}</div>
            <h3 style={{ margin: '14px 0 8px' }}>{t('choose_time')}</h3>
            <div className="slots">
              {Array.from({ length: 24 }, (_, h) => { const s = slotState(h); const bz = busyAt(hours, h); return (
                <button key={h} className={'slot ' + bz.level + (s !== 'ok' ? ' off' : '') + (hour === h ? ' on' : '')} onClick={() => setHour(h)}>
                  {pad(h)}:00<span className="lv">{s === 'past' ? t('past') : s === 'off' ? (hs ? t('closed') : t('slot_full')) : t(bz.level)}</span>
                </button>); })}
            </div>
            {hs && <div className="xs mut" style={{ marginTop: 8 }}><Info size={12} style={{ verticalAlign: -2 }} /> {t('home_slot_note')}</div>}
          </div>
        )}

        <div className="card">
          <h3 style={{ marginBottom: 8 }}>{t('battery')}</h3>
          <div className="row sp small"><span>{t('battery_now')}: <b>{soc}%</b></span><span>{t('battery_target')}: <b>{target}%</b></span></div>
          <input type="range" className="range" min={5} max={95} value={soc} onChange={e => { const v = +e.target.value; setSoc(v); if (v >= target) setTarget(Math.min(100, v + 5)); }} style={{ margin: '10px 0' }} />
          <input type="range" className="range" min={10} max={100} value={target} onChange={e => setTarget(Math.max(soc + 1, +e.target.value))} />
          <div className="grid3" style={{ marginTop: 12 }}>
            <div className="stat"><div className="n">{num(est.kwh, 1)}</div><div className="l">kWh</div></div>
            <div className="stat"><div className="n">{ok ? mins(est.minutes) : '–'}</div><div className="l">@ {est.kw} kW</div></div>
            <div className="stat g"><div className="n">{rp(cost, { compact: true })}</div><div className="l">{t('est_cost')}</div></div>
          </div>
          {ok && est.minutes > 0 && <div className="xs mut" style={{ marginTop: 8 }}>{t('range_added')}: ≈ {Math.round(est.kwh / veh.kwhKm)} km</div>}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 6 }}>{t('breakdown')}</h3>
          <div className="kv"><span className="k">{t('energy')} {num(est.kwh, 1)} kWh × {rp(parts.energy)}</span><span className="v">{rp(est.kwh * parts.energy)}</span></div>
          {parts.ppj > 0 && <div className="kv"><span className="k">PPJ {Math.round(parts.ppjRate * 100)}%</span><span className="v">{rp(est.kwh * parts.ppj)}</span></div>}
          {svc > 0 && <div className="kv"><span className="k">{t('service_fee')} 5%</span><span className="v">{rp(svc)}</span></div>}
          <div className="divider" /><div className="kv"><span className="k b">{t('total')}</span><span className="v b" style={{ fontSize: 17 }}>{rp(cost)}</span></div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 8 }}>{t('payment')}</h3>
          <div className="col">{PAY.map(([k, l, ic]) => <button key={k} className="row" style={{ padding: '10px 12px', borderRadius: 12, border: '1.5px solid ' + (pay === k ? 'var(--g)' : 'var(--line)'), background: pay === k ? 'var(--mint)' : 'var(--card)', textAlign: 'left' }} onClick={() => setPay(k)}><span style={{ width: 24, textAlign: 'center' }}>{ic}</span><span className="grow sb">{l}</span>{pay === k && <span className="pill g">✓</span>}</button>)}</div>
        </div>
      </div>
      <div className="sticky-cta">
        <button className="btn lg full" disabled={!ok || (!startNow && hour < 0)} onClick={confirm}><Zap size={18} fill="#fff" /> {startNow ? t('start_now') : t('confirm')} · {rp(cost)}</button>
      </div>
    </div>
  );
}
