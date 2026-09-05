import { useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { LocateFixed } from 'lucide-react';
import { TopBar } from '../components/ui';
import MapView, { type MapHandle } from '../components/MapView';
import { useStore } from '../store';
import { locate } from '../hooks';
import type { Listing, PlugType } from '../types';
import { AMENITY } from '../data';
import { DEFAULT_CENTER } from '../lib/geo';
import { rp, uid } from '../lib/format';
import { vehicleById } from '../vehicles';

export default function HostForm() {
  const { id } = useParams();
  const nav = useNavigate();
  const { t, lang, listings, upsertListing, userName, location, vehicleId, showToast } = useStore(s => ({ t: s.t, lang: s.lang, listings: s.listings, upsertListing: s.upsertListing, userName: s.userName, location: s.location, vehicleId: s.vehicleId, showToast: s.showToast }));
  const existing = listings.find(l => l.id === id);
  const veh = vehicleById(vehicleId);
  const mapRef = useRef<MapHandle>(null);
  const [f, setF] = useState(() => existing || ({ id: 'my-' + uid(), name: '', host: userName || 'Saya', lat: (location || DEFAULT_CENTER).lat, lng: (location || DEFAULT_CENTER).lng, area: '', city: '', province: 'Jawa Barat', address: '', kw: 7, plug: 'Type 2' as PlugType, priceKwh: 2500, days: 'daily' as const, from: '18:00', to: '06:00', score: 5, reviews: 0, sessions: 0, vehicle: veh.brand, amenities: [] as string[], note: '', since: new Date().getFullYear(), mine: true as const, active: true, createdAt: Date.now() } as Listing));
  const [pin, setPin] = useState({ lat: f.lat, lng: f.lng });
  const valid = f.name.trim().length >= 3 && f.area.trim() && f.city.trim() && f.priceKwh >= 1000;
  const hoursOpts = useMemo(() => Array.from({ length: 25 }, (_, i) => (i === 24 ? '24:00' : String(i).padStart(2, '0') + ':00')), []);
  const save = () => { upsertListing({ ...f, lat: pin.lat, lng: pin.lng, host: f.host || 'Saya' }); showToast(t('saved')); nav('/host', { replace: true }); };
  const gps = async () => { const l = await locate(); setPin(l); mapRef.current?.flyTo(l, 15); };
  return (
    <div className="page">
      <TopBar title={existing ? t('edit') : t('list_charger')} line />
      <div className="content">
        <div className="field"><label className="lbl">{t('l_name')}</label><input className="input" value={f.name} onChange={e => setF({ ...f, name: e.target.value })} placeholder={lang === 'en' ? 'e.g. Wallbox at Green Residence' : 'mis. Wallbox Rumah Griya Asri'} /></div>
        <div className="field"><label className="lbl">{t('l_address')}</label><input className="input" value={f.address} onChange={e => setF({ ...f, address: e.target.value })} placeholder="Jl. Mawar No. 12, cluster Anggrek" /></div>
        <div className="grid2">
          <div className="field"><label className="lbl">{t('l_area')}</label><input className="input" value={f.area} onChange={e => setF({ ...f, area: e.target.value })} placeholder="Sukajadi, Bandung" /></div>
          <div className="field"><label className="lbl">{t('l_city')}</label><input className="input" value={f.city} onChange={e => setF({ ...f, city: e.target.value })} placeholder="Kota Bandung" /></div>
        </div>
        <div className="field">
          <div className="row sp"><label className="lbl">{t('l_location')}</label><button className="btn sm ghost" onClick={gps}><LocateFixed size={14} /> {t('use_gps')}</button></div>
          <div className="minimap"><MapView ref={mapRef} stations={[]} hosts={[]} onSelect={() => {}} userLoc={null} center={pin} zoom={15} onMove={c => setPin(c)} /><div className="pin">📍</div></div>
          <div className="xs mut">{t('drag_pin')} · {pin.lat.toFixed(5)}, {pin.lng.toFixed(5)}</div>
        </div>
        <div className="field"><label className="lbl">{t('l_power')}</label><div className="seg">{[7, 11, 22].map(k => <button key={k} className={f.kw === k ? 'on' : ''} onClick={() => setF({ ...f, kw: k })}>{k} kW</button>)}</div></div>
        <div className="field"><label className="lbl">{t('l_plug')}</label><div className="seg">{(['Type 2', 'CCS2'] as PlugType[]).map(k => <button key={k} className={f.plug === k ? 'on' : ''} onClick={() => setF({ ...f, plug: k })}>{k}</button>)}</div></div>
        <div className="field"><label className="lbl">{t('l_price')}: {rp(f.priceKwh)}</label><input type="range" className="range" min={1500} max={4000} step={50} value={f.priceKwh} onChange={e => setF({ ...f, priceKwh: +e.target.value })} /><div className="xs mut">{t('price_hint')}</div></div>
        <div className="field"><label className="lbl">{t('l_days')}</label><div className="seg">{(['daily', 'weekdays', 'weekends'] as const).map(k => <button key={k} className={f.days === k ? 'on' : ''} onClick={() => setF({ ...f, days: k })}>{t(k)}</button>)}</div></div>
        <div className="field"><label className="lbl">{t('l_hours')}</label><div className="grid2"><select className="input" value={f.from} onChange={e => setF({ ...f, from: e.target.value })}>{hoursOpts.slice(0, 24).map(h => <option key={h}>{h}</option>)}</select><select className="input" value={f.to} onChange={e => setF({ ...f, to: e.target.value })}>{hoursOpts.map(h => <option key={h}>{h}</option>)}</select></div></div>
        <div className="field"><label className="lbl">{t('l_amenities')}</label><div className="row wrap">{['covered', 'cctv', 'wifi', 'toilet', 'coffee', 'musala', 'wide'].map(a => <button key={a} className={'chip' + (f.amenities.includes(a) ? ' on' : '')} onClick={() => setF({ ...f, amenities: f.amenities.includes(a) ? f.amenities.filter(x => x !== a) : [...f.amenities, a] })}>{AMENITY[a].icon} {lang === 'en' ? AMENITY[a].en : AMENITY[a].id}</button>)}</div></div>
        <div className="field"><label className="lbl">{t('l_note')} ({t('optional')})</label><textarea className="input" value={f.note} onChange={e => setF({ ...f, note: e.target.value })} /></div>
      </div>
      <div className="sticky-cta"><button className="btn lg full amber" disabled={!valid} onClick={save}>{t('save')}</button></div>
    </div>
  );
}
