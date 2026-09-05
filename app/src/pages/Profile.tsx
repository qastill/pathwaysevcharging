import { useNavigate } from 'react-router-dom';
import { Car, Heart, Calculator, BarChart3, Info, ChevronRight, RotateCcw, Download, Globe } from 'lucide-react';
import { TopBar, Modal } from '../components/ui';
import { useStore } from '../store';
import { useData, useAllHosts, useInstallPrompt } from '../hooks';
import { StationCard, HostCard } from '../components/Cards';
import { vehicleById } from '../vehicles';
import { rp, num, titleCase } from '../lib/format';
import { useState } from 'react';

export default function Profile() {
  const nav = useNavigate();
  const d = useData();
  const hosts = useAllHosts(d?.hosts);
  const { t, lang, set, userName, vehicleId, plate, bookings, favorites, resetDemo, showToast, location } = useStore(s => ({ t: s.t, lang: s.lang, set: s.set, userName: s.userName, vehicleId: s.vehicleId, plate: s.plate, bookings: s.bookings, favorites: s.favorites, resetDemo: s.resetDemo, showToast: s.showToast, location: s.location }));
  const veh = vehicleById(vehicleId);
  const install = useInstallPrompt();
  const [reset, setReset] = useState(false); const [about, setAbout] = useState(false);
  const done = bookings.filter(b => b.status === 'completed' && b.session);
  const kwh = done.reduce((a, b) => a + (b.session?.kwh || 0), 0), cost = done.reduce((a, b) => a + (b.session?.cost || 0), 0), co2 = done.reduce((a, b) => a + (b.session?.co2Saved || 0), 0);
  const favS = d ? d.stations.filter(s => favorites.includes(s.id)) : [], favH = hosts.filter(h => favorites.includes(h.id));
  return (
    <div className="page">
      <TopBar title={t('profile')} back={false} right={<button className="btn sm ghost" onClick={() => set({ lang: lang === 'id' ? 'en' : 'id' })}><Globe size={14} /> {lang === 'id' ? 'EN' : 'ID'}</button>} />
      <div className="content">
        <div className="card row">
          <div className="avatar" style={{ width: 52, height: 52, fontSize: 20, background: 'var(--mint)', color: 'var(--g2)' }}>{(userName || 'N')[0].toUpperCase()}</div>
          <div className="grow"><input className="input" style={{ height: 40, border: 0, padding: 0, fontWeight: 700, fontSize: 17, background: 'transparent' }} value={userName} placeholder={t('your_name')} onChange={e => set({ userName: e.target.value })} /><div className="xs mut">{done.length} {t('sessions')} · {num(kwh, 1)} kWh</div></div>
        </div>
        <div className="card click" onClick={() => nav('/vehicle')}>
          <div className="row"><span style={{ fontSize: 30 }}>🚗</span><div className="grow"><div className="xs mut b" style={{ textTransform: 'uppercase', letterSpacing: '.04em' }}>{t('my_vehicle')}</div><div className="b">{veh.brand} {veh.model}{plate ? ` · ${plate}` : ''}</div><div className="xs mut">{veh.battery} kWh · {veh.plug} · DC {veh.dc || '–'} kW · ≈ {veh.range} km</div></div><ChevronRight size={18} color="var(--mut2)" /></div>
        </div>
        <div className="grid3">
          <div className="stat g"><div className="n">{num(kwh, 0)}</div><div className="l">kWh</div></div>
          <div className="stat"><div className="n">{rp(cost, { compact: true })}</div><div className="l">{t('total')}</div></div>
          <div className="stat"><div className="n">{num(co2, 1)}</div><div className="l">kg CO₂ ↓</div></div>
        </div>
        <div className="card" style={{ padding: 0 }}>
          <div className="list-item" onClick={() => nav('/trip')}><div className="ic"><Calculator size={18} /></div><div className="grow sb">{t('trip')}</div><ChevronRight size={18} color="var(--mut2)" /></div>
          <div className="list-item" onClick={() => nav('/insights')}><div className="ic"><BarChart3 size={18} /></div><div className="grow sb">{t('insights')}</div><ChevronRight size={18} color="var(--mut2)" /></div>
          <div className="list-item" onClick={() => nav('/host')}><div className="ic"><Car size={18} /></div><div className="grow sb">{t('host_title')}</div><ChevronRight size={18} color="var(--mut2)" /></div>
          {install && <div className="list-item" onClick={async () => { install.prompt(); const r = await install.userChoice; if (r.outcome === 'accepted') showToast(t('installed')); }}><div className="ic"><Download size={18} /></div><div className="grow sb">{t('install')}</div><ChevronRight size={18} color="var(--mut2)" /></div>}
          <div className="list-item" onClick={() => setAbout(true)}><div className="ic"><Info size={18} /></div><div className="grow sb">{t('about')}</div><ChevronRight size={18} color="var(--mut2)" /></div>
          <div className="list-item" onClick={() => setReset(true)}><div className="ic" style={{ background: 'var(--red2)', color: 'var(--red)' }}><RotateCcw size={18} /></div><div className="grow sb">{t('reset_demo')}</div></div>
        </div>
        <h3><Heart size={16} style={{ verticalAlign: -2 }} /> {t('favorites')}</h3>
        {favS.length + favH.length === 0 ? <div className="small mut">{t('no_fav')}</div> : <>{favS.map(s => <StationCard key={s.id} s={s} meta={d!.meta} loc={location} nowH={new Date().getHours()} />)}{favH.map(h => <HostCard key={h.id} h={h} loc={location} />)}</>}
      </div>
      <Modal open={reset} onClose={() => setReset(false)}><h2 style={{ marginBottom: 14 }}>{t('reset_q')}</h2><div className="row"><button className="btn ghost grow" onClick={() => setReset(false)}>{t('keep')}</button><button className="btn danger grow" onClick={() => { resetDemo(); setReset(false); showToast('✓'); }}>{t('reset_demo')}</button></div></Modal>
      <Modal open={about} onClose={() => setAbout(false)}>
        <h2>⚡ {t('app')} <span className="pill g">v1.0</span></h2>
        <p className="small" style={{ margin: '10px 0' }}>{t('tagline')} {lang === 'en' ? 'A peer-to-peer and public EV-charging finder for Indonesia, built on real PLN West Java data.' : 'Aplikasi pencari charger EV publik dan peer-to-peer untuk Indonesia, dibangun di atas data nyata PLN UID Jawa Barat.'}</p>
        <div className="small mut" style={{ lineHeight: 1.55 }}>
          {t('data_note')}<br /><br />{d && <>{num(d.meta.counts.stations)} SPKLU · {d.meta.counts.provinces} {lang === 'en' ? 'provinces' : 'provinsi'} · {num(d.meta.counts.dc)} DC · {num(d.meta.counts.hosts)} {lang === 'en' ? 'sample hosts' : 'host contoh'}<br />{d.meta.builtFrom}</>}<br /><br />Peta © OpenFreeMap · OpenStreetMap contributors.
        </div>
      </Modal>
    </div>
  );
}
