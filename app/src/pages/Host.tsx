import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Home, TrendingUp, Check, X, Pencil, Trash2 } from 'lucide-react';
import { TopBar, Modal } from '../components/ui';
import { useStore, type HostRequest } from '../store';
import { useData } from '../hooks';
import { rp, num, isoDate, dateLabel, hash, uid } from '../lib/format';

const GUESTS = ['Andi P.', 'Sari M.', 'Bayu K.', 'Dewi R.', 'Rizky A.', 'Maya S.', 'Fajar H.', 'Putri N.'];
const CARS = ['BYD Atto 3', 'Wuling BinguoEV', 'Hyundai Ioniq 5', 'Chery Omoda E5', 'BYD Dolphin', 'Geely EX5', 'MG4 EV'];

export default function Host() {
  const nav = useNavigate();
  const d = useData();
  const { t, lang, listings, upsertListing, removeListing, requests, set, bookings, showToast } = useStore(s => ({ t: s.t, lang: s.lang, listings: s.listings, upsertListing: s.upsertListing, removeListing: s.removeListing, requests: s.requests, set: s.set, bookings: s.bookings, showToast: s.showToast }));
  const [hours, setHours] = useState(4); const [price, setPrice] = useState(2500); const [kw, setKw] = useState(7);
  const [del, setDel] = useState<string | null>(null);
  const home = d?.meta.assume.tarif_rumah || 1699.53;
  const margin = hours * kw * 0.85 * (price - home) * 30; // 85 % of nominal power actually delivered
  const gross = hours * kw * 0.85 * price * 30;

  // seed a few incoming requests for each active listing (deterministic per listing)
  useEffect(() => {
    const need = listings.filter(l => l.active && !requests.some(r => r.listingId === l.id));
    if (!need.length) return;
    const add: HostRequest[] = [];
    for (const l of need) for (let i = 0; i < 2; i++) {
      const h = hash(l.id + i); const dt = new Date(); dt.setDate(dt.getDate() + 1 + Math.floor(h * 4));
      const kwh = Math.round(12 + h * 30);
      add.push({ id: uid(), listingId: l.id, guest: GUESTS[Math.floor(h * GUESTS.length)], vehicle: CARS[Math.floor(hash(l.id + 'c' + i) * CARS.length)], date: isoDate(dt), start: (Math.floor(hash(l.id + 'h' + i) * 14) + 8).toString().padStart(2, '0') + ':00', kwh, amount: Math.round(kwh * l.priceKwh), status: 'pending' });
    }
    set({ requests: [...requests, ...add] });
  }, [listings]); // eslint-disable-line

  const earnings = useMemo(() => {
    const accepted = requests.filter(r => r.status === 'accepted').reduce((a, r) => a + r.amount * 0.95, 0);
    const own = bookings.filter(b => b.kind === 'host' && b.status === 'completed' && listings.some(l => l.id === b.targetId)).reduce((a, b) => a + (b.session?.cost || 0) * 0.95, 0);
    return accepted + own;
  }, [requests, bookings, listings]);
  const pending = requests.filter(r => r.status === 'pending');

  if (listings.length === 0) return (
    <div className="page">
      <TopBar title={t('tab_host')} back={false} />
      <div className="content">
        <div className="hero host" style={{ borderRadius: 24, padding: 22 }}>
          <div className="venue">🏠⚡</div>
          <h1>{t('host_title')}</h1>
          <p className="small" style={{ opacity: .92, marginTop: 8, lineHeight: 1.5 }}>{t('host_pitch')}</p>
        </div>
        <div className="card">
          <div className="row" style={{ marginBottom: 10 }}><TrendingUp size={18} color="var(--g)" /><h3>{t('earn_calc')}</h3></div>
          <div className="field"><label className="lbl">{t('l_power')}</label><div className="seg">{[7, 11, 22].map(k => <button key={k} className={kw === k ? 'on' : ''} onClick={() => setKw(k)}>{k} kW</button>)}</div></div>
          <div className="field" style={{ marginTop: 12 }}><label className="lbl">{hours} {t('hours_day')}</label><input type="range" className="range" min={1} max={12} value={hours} onChange={e => setHours(+e.target.value)} /></div>
          <div className="field" style={{ marginTop: 12 }}><label className="lbl">{t('your_price')}: {rp(price)}/kWh</label><input type="range" className="range" min={1800} max={3500} step={50} value={price} onChange={e => setPrice(+e.target.value)} /></div>
          <div className="grid2" style={{ marginTop: 14 }}>
            <div className="stat"><div className="n">{rp(gross, { compact: true })}</div><div className="l">{lang === 'en' ? 'gross / month' : 'kotor / bulan'}</div></div>
            <div className="stat g"><div className="n">{rp(margin, { compact: true })}</div><div className="l">{t('margin_month')}</div></div>
          </div>
          <div className="xs mut" style={{ marginTop: 8 }}>{t('electricity_cost')}: {rp(home)}/kWh · {t('price_hint')}</div>
        </div>
        <button className="btn lg full amber" onClick={() => nav('/host/new')}><Plus size={18} /> {t('list_charger')}</button>
      </div>
    </div>
  );

  return (
    <div className="page">
      <TopBar title={t('tab_host')} back={false} right={<button className="btn sm amber" onClick={() => nav('/host/new')}><Plus size={14} /> {t('add_listing')}</button>} />
      <div className="content">
        <div className="card" style={{ background: 'linear-gradient(135deg,#9A5B00,#D98A05)', color: '#fff', borderColor: 'transparent' }}>
          <div className="small" style={{ opacity: .85 }}>{t('earnings')} · {t('this_month')}</div>
          <div style={{ fontSize: 34, fontWeight: 800, letterSpacing: '-.03em' }}>{rp(earnings)}</div>
          <div className="row" style={{ marginTop: 8, gap: 16 }}><span className="small"><b>{requests.filter(r => r.status === 'accepted').length + bookings.filter(b => b.kind === 'host' && b.status === 'completed').length}</b> {t('sessions')}</span><span className="small"><b>{listings.filter(l => l.active).length}</b> {t('active_listing').toLowerCase()}</span><span className="small"><b>{num(requests.filter(r => r.status === 'accepted').reduce((a, r) => a + r.kwh, 0))}</b> kWh</span></div>
        </div>

        {pending.length > 0 && (
          <div>
            <h3 style={{ marginBottom: 8 }}>{t('requests')} <span className="pill red">{pending.length}</span></h3>
            <div className="col">{pending.map(r => { const l = listings.find(x => x.id === r.listingId); return (
              <div key={r.id} className="card">
                <div className="row"><div className="avatar">{r.guest[0]}</div><div className="grow"><div className="b">{r.guest} · {r.vehicle}</div><div className="xs mut">{l?.name} · {dateLabel(r.date, lang)} {r.start} · ≈ {r.kwh} kWh</div></div><div className="b" style={{ color: 'var(--g)' }}>{rp(r.amount, { compact: true })}</div></div>
                <div className="row" style={{ marginTop: 10 }}><button className="btn sm ghost grow" onClick={() => set({ requests: requests.map(x => (x.id === r.id ? { ...x, status: 'declined' } : x)) })}><X size={14} /> {t('decline')}</button><button className="btn sm grow" onClick={() => { set({ requests: requests.map(x => (x.id === r.id ? { ...x, status: 'accepted' } : x)) }); showToast('✓ ' + t('accept')); }}><Check size={14} /> {t('accept')}</button></div>
              </div>); })}</div>
          </div>
        )}

        <h3>{t('my_listings')}</h3>
        {listings.map(l => (
          <div key={l.id} className="card">
            <div className="row sp"><div className="row"><div className="station-card" style={{ padding: 0, border: 0 }}><div className="ico host"><Home size={22} color="#9A5B00" /></div></div><div><div className="b">{l.name}</div><div className="xs mut">{l.area}, {l.city} · {l.kw} kW · {rp(l.priceKwh)}/kWh</div></div></div><button className={'toggle' + (l.active ? ' on' : '')} onClick={() => upsertListing({ ...l, active: !l.active })} /></div>
            <div className="row wrap" style={{ marginTop: 8 }}><span className={'pill ' + (l.active ? 'lime' : '')}>{l.active ? t('active_listing') : t('paused')}</span><span className="pill">{l.from}–{l.to}</span><span className="pill">{t(l.days)}</span></div>
            <div className="row" style={{ marginTop: 10 }}><button className="btn sm ghost" onClick={() => nav('/h/' + l.id)}>{t('view')}</button><button className="btn sm ghost" onClick={() => nav('/host/edit/' + l.id)}><Pencil size={14} /> {t('edit')}</button><button className="btn sm ghost" style={{ color: 'var(--red)' }} onClick={() => setDel(l.id)}><Trash2 size={14} /></button></div>
          </div>
        ))}
        <div className="xs mut">{t('price_hint')}</div>
      </div>
      <Modal open={!!del} onClose={() => setDel(null)}><h2 style={{ marginBottom: 14 }}>{t('delete')}?</h2><div className="row"><button className="btn ghost grow" onClick={() => setDel(null)}>{t('keep')}</button><button className="btn danger grow" onClick={() => { removeListing(del!); setDel(null); }}>{t('delete')}</button></div></Modal>
    </div>
  );
}
