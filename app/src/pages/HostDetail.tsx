import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Heart, Navigation, Zap, Star, MapPin, Info, Clock } from 'lucide-react';
import { useData, useAllHosts } from '../hooks';
import { useStore } from '../store';
import { AMENITY } from '../data';
import { ReviewList } from '../components/Reviews';
import MapView from '../components/MapView';
import { rp, km, mins, num } from '../lib/format';
import { distM, mapsUrl } from '../lib/geo';
import { estimateCharge } from '../lib/model';
import { vehicleById } from '../vehicles';

export default function HostDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const d = useData();
  const hosts = useAllHosts(d?.hosts);
  const { t, lang, location, favorites, toggleFav, vehicleId } = useStore(s => ({ t: s.t, lang: s.lang, location: s.location, favorites: s.favorites, toggleFav: s.toggleFav, vehicleId: s.vehicleId }));
  const h = hosts.find(x => x.id === id);
  const veh = vehicleById(vehicleId);
  if (!d || !h) return <div className="content"><div className="skeleton" style={{ height: 240 }} /></div>;
  const est = estimateCharge(veh, h.kw, 'Type 2', 20, 80);
  const fav = favorites.includes(h.id);
  return (
    <div className="page">
      <div className="hero host">
        <div className="row sp"><button className="iconbtn" onClick={() => nav(-1)}><ChevronLeft size={22} /></button><button className="iconbtn" onClick={() => toggleFav(h.id)}><Heart size={18} fill={fav ? '#fff' : 'none'} /></button></div>
        <div className="venue">🏠</div>
        <h1>{h.name}</h1>
        <div className="small" style={{ opacity: .9, marginTop: 4 }}>{t('hosted_by')} {h.host} · {h.area}</div>
        <div className="row wrap" style={{ marginTop: 10 }}>
          <span className="pill"><Zap size={11} /> AC {h.kw} kW · Type 2</span>
          <span className="pill"><Star size={11} fill="#fff" /> {h.score.toFixed(1)} ({h.reviews})</span>
          <span className="pill"><Clock size={11} /> {h.from}–{h.to} · {t(h.days)}</span>
          {location && <span className="pill"><Navigation size={11} /> {km(distM(location, h))}</span>}
        </div>
      </div>
      <div className="content">
        <div className="grid3">
          <div className="stat" style={{ background: 'var(--amber2)', borderColor: 'transparent' }}><div className="n" style={{ color: '#9A5B00' }}>{rp(h.priceKwh)}</div><div className="l">{t('per_kwh')}</div></div>
          <div className="stat"><div className="n">{h.sessions}</div><div className="l">{t('sessions')}</div></div>
          <div className="stat"><div className="n">{h.since}</div><div className="l">{t('host_since')}</div></div>
        </div>
        <div className="card" style={{ background: 'linear-gradient(135deg,#FFF8EA,#FFF1D6)', borderColor: 'transparent' }}>
          <div className="row sp"><div className="b">{t('your_cost')}</div><button className="btn sm ghost" onClick={() => nav('/vehicle')}>{veh.brand} {veh.model}</button></div>
          <div className="row" style={{ marginTop: 8, gap: 18 }}>
            <div><div className="xs mut">20% → 80%</div><div className="b" style={{ fontSize: 18 }}>{rp(est.kwh * h.priceKwh)}</div></div>
            <div><div className="xs mut">{t('est_energy')}</div><div className="b" style={{ fontSize: 18 }}>{num(est.kwh, 1)} kWh</div></div>
            <div><div className="xs mut">{t('est_time')} @ {est.kw} kW</div><div className="b" style={{ fontSize: 18 }}>{mins(est.minutes)}</div></div>
          </div>
        </div>
        <div className="card">
          <div className="row" style={{ marginBottom: 10 }}><div className="avatar">{h.host[0]}</div><div><div className="b">{h.host}</div><div className="xs mut">{t('suitable_for')} {h.vehicle || 'EV'}</div></div></div>
          <div className="small">{h.note}</div>
          {h.amenities.length > 0 && <div className="row wrap" style={{ marginTop: 10 }}>{h.amenities.map(a => <span key={a} className="pill">{AMENITY[a]?.icon} {lang === 'en' ? AMENITY[a]?.en : AMENITY[a]?.id}</span>)}</div>}
        </div>
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ height: 180, position: 'relative' }}><MapView stations={[]} hosts={[h]} onSelect={() => {}} userLoc={null} center={h} zoom={14} interactive={false} /></div>
          <div style={{ padding: 14 }}>
            <div className="small">{h.address || h.area}, {h.city}</div>
            <a className="btn sec full" style={{ marginTop: 10, background: 'var(--amber2)', color: '#9A5B00' }} href={mapsUrl(h)} target="_blank" rel="noreferrer"><MapPin size={16} /> {t('directions')}</a>
          </div>
        </div>
        {h.simulated && <div className="card flat small mut" style={{ background: 'var(--line2)' }}><Info size={13} style={{ verticalAlign: -2 }} /> {t('simulated_note')}</div>}
        <ReviewList targetId={h.id} baseScore={h.score} baseCount={h.reviews} />
      </div>
      <div className="sticky-cta"><button className="btn lg full amber" onClick={() => nav(`/book/host/${h.id}`)}><Zap size={18} fill="#fff" /> {t('book')}</button></div>
    </div>
  );
}
