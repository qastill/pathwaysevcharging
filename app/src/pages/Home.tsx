import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Search, SlidersHorizontal, LocateFixed, List, X, Home as HomeIcon, ChevronRight } from 'lucide-react';
import MapView, { type MapHandle } from '../components/MapView';
import { StationCard, HostCard } from '../components/Cards';
import { Modal, Skeleton } from '../components/ui';
import { useData, useAllHosts, locate, useNow } from '../hooks';
import { useStore } from '../store';
import type { Station, Host, PlugType, LatLng } from '../types';
import { distM, DEFAULT_CENTER, CITIES } from '../lib/geo';
import { VENUE_LABEL } from '../data';
import { vehicleById } from '../vehicles';
import { compatible } from '../lib/model';
import { titleCase, rp } from '../lib/format';

interface Filters { type: 'all' | 'AC' | 'DC'; plug: 'all' | PlugType; op: 'all' | 'PLN' | 'Mitra' | 'host'; minKw: number; availOnly: boolean; maxPrice: number; hosts: boolean; venue: string; compat: boolean }
const F0: Filters = { type: 'all', plug: 'all', op: 'all', minKw: 0, availOnly: false, maxPrice: 0, hosts: true, venue: 'all', compat: false };
type Sort = 'nearest' | 'fastest' | 'cheapest' | 'popular';

export default function Home() {
  const d = useData();
  const nav = useNavigate();
  const [sp] = useSearchParams();
  const { t, lang, location, locationSource, vehicleId } = useStore(s => ({ t: s.t, lang: s.lang, location: s.location, locationSource: s.locationSource, vehicleId: s.vehicleId }));
  const hosts = useAllHosts(d?.hosts);
  const now = useNow();
  const mapRef = useRef<MapHandle>(null);
  const [q, setQ] = useState(sp.get('q') || '');
  const [f, setF] = useState<Filters>(() => ({ ...F0, op: (sp.get('op') as any) || 'all', venue: sp.get('venue') || 'all' }));
  const [draft, setDraft] = useState<Filters>(f);
  const [showF, setShowF] = useState(false);
  const [sheet, setSheet] = useState<0 | 1 | 2>(1);
  const [sel, setSel] = useState<{ kind: 'station' | 'host'; id: string } | null>(null);
  const [sort, setSort] = useState<Sort>('nearest');
  const [center, setCenter] = useState<LatLng>(location || DEFAULT_CENTER);
  const [locating, setLocating] = useState(false);
  const veh = vehicleById(vehicleId);

  useEffect(() => { if (!location) locate(true).then(l => { setCenter(l); mapRef.current?.flyTo(l, 12); }); }, []); // eslint-disable-line

  const activeCount = (f.type !== 'all' ? 1 : 0) + (f.plug !== 'all' ? 1 : 0) + (f.op !== 'all' ? 1 : 0) + (f.minKw ? 1 : 0) + (f.availOnly ? 1 : 0) + (f.maxPrice ? 1 : 0) + (!f.hosts ? 1 : 0) + (f.venue !== 'all' ? 1 : 0) + (f.compat ? 1 : 0);

  const filtered = useMemo(() => {
    if (!d) return { stations: [] as Station[], hosts: [] as Host[] };
    const qq = q.trim().toLowerCase();
    const match = (s: string) => s.toLowerCase().includes(qq);
    let st = d.stations.filter(s => {
      if (f.op === 'host') return false;
      if (f.op !== 'all' && s.operator !== f.op) return false;
      if (f.type !== 'all' && s.type !== f.type) return false;
      if (f.plug !== 'all' && !s.plugs.some(p => p.type === f.plug)) return false;
      if (f.minKw && s.kw < f.minKw) return false;
      if (f.availOnly && s.status !== 'available') return false;
      if (f.maxPrice && s.priceKwh > f.maxPrice) return false;
      if (f.venue !== 'all' && s.venue !== f.venue) return false;
      if (f.compat && !s.plugs.some(p => compatible(veh, p.type))) return false;
      if (qq && !(match(s.name) || match(s.address) || match(s.city || '') || match(s.province))) return false;
      return true;
    });
    let hs = f.hosts && f.type !== 'DC' && (f.op === 'all' || f.op === 'host') && f.venue === 'all' && (f.plug === 'all' || f.plug === 'Type 2') ? hosts.filter(h => (!f.minKw || h.kw >= f.minKw) && (!f.maxPrice || h.priceKwh <= f.maxPrice) && (!qq || match(h.name) || match(h.area) || match(h.city))) : [];
    return { stations: st, hosts: hs };
  }, [d, hosts, q, f, veh]);

  const origin = location || center;
  const list = useMemo(() => {
    const items: { kind: 'station' | 'host'; s?: Station; h?: Host; d: number; key: string }[] = [
      ...filtered.stations.map(s => ({ kind: 'station' as const, s, d: distM(origin, s), key: 's' + s.id })),
      ...filtered.hosts.map(h => ({ kind: 'host' as const, h, d: distM(origin, h), key: 'h' + h.id })),
    ];
    const by: Record<Sort, (a: typeof items[0], b: typeof items[0]) => number> = {
      nearest: (a, b) => a.d - b.d,
      fastest: (a, b) => (b.s?.kw || b.h?.kw || 0) - (a.s?.kw || a.h?.kw || 0) || a.d - b.d,
      cheapest: (a, b) => (a.s?.priceKwh || a.h?.priceKwh || 0) - (b.s?.priceKwh || b.h?.priceKwh || 0) || a.d - b.d,
      popular: (a, b) => (b.s?.stats?.trx || b.h?.sessions || 0) - (a.s?.stats?.trx || a.h?.sessions || 0) || a.d - b.d,
    };
    return { top: items.sort(by[sort]).slice(0, 80), near: items.filter(i => i.d < 10000).length };
  }, [filtered, origin, sort]);

  const cityHit = useMemo(() => { const qq = q.trim().toLowerCase(); return qq.length >= 3 ? CITIES.find(c => c.name.toLowerCase().startsWith(qq)) : undefined; }, [q]);
  const selObj = sel ? (sel.kind === 'station' ? d?.stations.find(s => s.id === sel.id) : hosts.find(h => h.id === sel.id)) : undefined;
  const nearby = location ? list.near : 0;

  const onLocate = async () => { setLocating(true); const l = await locate(); setLocating(false); setCenter(l); mapRef.current?.flyTo(l, 13); };
  const select = (kind: 'station' | 'host', id: string) => { setSel({ kind, id }); const o = kind === 'station' ? d?.stations.find(s => s.id === id) : hosts.find(h => h.id === id); if (o) mapRef.current?.flyTo(o, Math.max(mapRef.current.getZoom(), 13)); };
  const sheetH = sheet === 0 ? 'calc(112px + var(--sab))' : sheet === 1 ? '46%' : '86%';
  const nowH = now.getHours();

  return (
    <div className="home">
      <MapView ref={mapRef} stations={filtered.stations} hosts={filtered.hosts} selectedId={sel?.id} onSelect={select} userLoc={location} center={center} zoom={location ? 12 : 8} onMove={c => setCenter(c)} padding={{ bottom: 200 }} />

      <div className="home-top">
        <div className="search">
          <span className="logo"><Search size={18} /></span>
          <input value={q} onChange={e => { setQ(e.target.value); setSheet(1); }} placeholder={t('search_ph')} />
          {q ? <button className="iconbtn ghost" onClick={() => setQ('')}><X size={18} /></button> : <span className="logo">⚡ {t('app')}</span>}
          <button className={'iconbtn' + (activeCount ? ' on' : '')} onClick={() => { setDraft(f); setShowF(true); }} aria-label="filters"><SlidersHorizontal size={18} />{activeCount ? <span style={{ position: 'absolute', marginTop: -26, marginLeft: 26, background: 'var(--lime)', color: 'var(--ink)', borderRadius: 8, fontSize: 10, fontWeight: 800, padding: '0 5px' }}>{activeCount}</span> : null}</button>
        </div>
        <div className="chips">
          {[['all', t('all')], ['DC', 'DC ⚡'], ['AC', 'AC']].map(([k, l]) => <button key={k} className={'chip g' + (f.type === k ? ' on' : '')} onClick={() => setF({ ...f, type: k as any })}>{l}</button>)}
          <button className={'chip g' + (f.op === 'host' ? ' on' : '')} onClick={() => setF({ ...f, op: f.op === 'host' ? 'all' : 'host', hosts: true })}><HomeIcon size={14} />{t('host')}</button>
          <button className={'chip g' + (f.venue === 'rest_area' ? ' on' : '')} onClick={() => setF({ ...f, venue: f.venue === 'rest_area' ? 'all' : 'rest_area' })}>🛣️ Rest area</button>
          <button className={'chip g' + (f.availOnly ? ' on' : '')} onClick={() => setF({ ...f, availOnly: !f.availOnly })}>✅ {t('available')}</button>
          <button className={'chip g' + (f.compat ? ' on' : '')} onClick={() => setF({ ...f, compat: !f.compat })}>🚗 {veh.brand} {veh.model}</button>
        </div>
        {cityHit && <button className="chip" style={{ alignSelf: 'flex-start' }} onClick={() => { mapRef.current?.flyTo(cityHit, 12); setCenter(cityHit); }}>📍 {cityHit.name} <ChevronRight size={14} /></button>}
      </div>

      <div className="mapbtns" style={{ bottom: `calc(${sheetH} + 14px)`, transition: 'bottom .25s' }}>
        <button className={'mapbtn' + (locationSource === 'gps' ? ' on' : '')} onClick={onLocate} aria-label={t('locate')}><LocateFixed size={20} className={locating ? 'bolt' : ''} /></button>
        <button className="mapbtn" onClick={() => setSheet(sheet === 2 ? 1 : 2)} aria-label={t('list')}><List size={20} /></button>
      </div>

      {selObj && (
        <div className="selected-card" style={{ bottom: `calc(${sheetH} + 12px)`, transition: 'bottom .25s' }}>
          {sel!.kind === 'station' ? <StationCard s={selObj as Station} meta={d!.meta} loc={location} nowH={nowH} selected onClick={() => nav('/s/' + selObj.id)} /> : <HostCard h={selObj as Host} loc={location} selected onClick={() => nav('/h/' + selObj.id)} />}
        </div>
      )}

      <div className="sheet" style={{ height: sheetH }}>
        <button className="handle" onClick={() => setSheet(sheet === 0 ? 1 : sheet === 1 ? 2 : 0)} aria-label="toggle" />
        <div className="head">
          <div onClick={() => setSheet(sheet === 0 ? 1 : sheet)} style={{ cursor: 'pointer' }}>
            <div className="b">{location && sort === 'nearest' ? t('near_you') : t('all_stations')}</div>
            <div className="xs mut">{d ? <>{filtered.stations.length + filtered.hosts.length} {t('results')}{location && nearby ? ` · ${nearby} ${t('stations_near')} 10 km` : ''}</> : t('loading')}</div>
          </div>
          <select className="input" style={{ width: 'auto', height: 36, fontSize: 13, fontWeight: 600, paddingRight: 34 }} value={sort} onChange={e => setSort(e.target.value as Sort)}>
            <option value="nearest">{t('nearest')}</option><option value="fastest">{t('fastest')}</option><option value="cheapest">{t('cheapest')}</option><option value="popular">{t('popular')}</option>
          </select>
        </div>
        <div className="body">
          {!d ? <Skeleton h={84} n={5} /> : list.top.length === 0 ? <div className="empty"><div className="ic">🔍</div><div>{lang === 'en' ? 'Nothing matches. Try widening the filters.' : 'Tidak ada yang cocok. Coba longgarkan filter.'}</div></div> :
            list.top.map(i => i.kind === 'station' ? <StationCard key={i.key} s={i.s!} meta={d.meta} loc={location} nowH={nowH} selected={sel?.id === i.s!.id} onClick={() => nav('/s/' + i.s!.id)} /> : <HostCard key={i.key} h={i.h!} loc={location} selected={sel?.id === i.h!.id} onClick={() => nav('/h/' + i.h!.id)} />)}
          {d && list.top.length > 0 && <div className="legend" style={{ padding: '6px 4px' }}><span><i style={{ background: '#0E7A4A' }} />DC PLN</span><span><i style={{ background: '#0E9F8A' }} />AC PLN</span><span><i style={{ background: '#2563EB' }} />{t('mitra')}</span><span><i style={{ background: '#F59E0B' }} />{t('host')}</span></div>}
        </div>
      </div>

      <Modal open={showF} onClose={() => setShowF(false)}>
        <div className="row sp" style={{ marginBottom: 12 }}><h2>{t('filters')}</h2><button className="btn sm ghost" onClick={() => setDraft(F0)}>{t('reset')}</button></div>
        <div className="col" style={{ gap: 16 }}>
          <div className="field"><label className="lbl">{t('f_type')}</label><div className="seg">{(['all', 'DC', 'AC'] as const).map(k => <button key={k} className={draft.type === k ? 'on' : ''} onClick={() => setDraft({ ...draft, type: k })}>{k === 'all' ? t('all') : k}</button>)}</div></div>
          <div className="field"><label className="lbl">{t('f_plug')}</label><div className="seg">{(['all', 'CCS2', 'Type 2', 'CHAdeMO'] as const).map(k => <button key={k} className={draft.plug === k ? 'on' : ''} onClick={() => setDraft({ ...draft, plug: k })}>{k === 'all' ? t('all') : k}</button>)}</div></div>
          <div className="field"><label className="lbl">{t('f_operator')}</label><div className="seg">{(['all', 'PLN', 'Mitra', 'host'] as const).map(k => <button key={k} className={draft.op === k ? 'on' : ''} onClick={() => setDraft({ ...draft, op: k })}>{k === 'all' ? t('all') : k === 'PLN' ? 'PLN' : k === 'Mitra' ? t('mitra') : t('host')}</button>)}</div></div>
          <div className="field"><label className="lbl">{t('f_minkw')}: {draft.minKw ? draft.minKw + ' kW' : t('all')}</label><input type="range" className="range" min={0} max={200} step={10} value={draft.minKw} onChange={e => setDraft({ ...draft, minKw: +e.target.value })} /></div>
          <div className="field"><label className="lbl">{t('f_maxprice')}: {draft.maxPrice ? rp(draft.maxPrice) : t('all')}</label><input type="range" className="range" min={0} max={4000} step={100} value={draft.maxPrice} onChange={e => setDraft({ ...draft, maxPrice: +e.target.value })} /></div>
          <div className="field"><label className="lbl">{t('f_venue')}</label><select className="input" value={draft.venue} onChange={e => setDraft({ ...draft, venue: e.target.value })}><option value="all">{t('all')}</option>{Object.entries(VENUE_LABEL).filter(([k]) => k !== 'home').map(([k, v]) => <option key={k} value={k}>{v.icon} {lang === 'en' ? v.en : v.id}</option>)}</select></div>
          <div className="row sp"><span className="sb">{t('f_available')}</span><button className={'toggle' + (draft.availOnly ? ' on' : '')} onClick={() => setDraft({ ...draft, availOnly: !draft.availOnly })} /></div>
          <div className="row sp"><span className="sb">{t('f_hosts')}</span><button className={'toggle' + (draft.hosts ? ' on' : '')} onClick={() => setDraft({ ...draft, hosts: !draft.hosts })} /></div>
          <div className="row sp"><span className="sb">{lang === 'en' ? 'Only compatible with' : 'Hanya yang cocok dengan'} {veh.brand} {veh.model}</span><button className={'toggle' + (draft.compat ? ' on' : '')} onClick={() => setDraft({ ...draft, compat: !draft.compat })} /></div>
          <button className="btn lg full" onClick={() => { setF(draft); setShowF(false); }}>{t('apply')}</button>
        </div>
      </Modal>
    </div>
  );
}
