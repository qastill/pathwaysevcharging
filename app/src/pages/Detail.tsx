import { useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Heart, Navigation, Share2, Copy, Zap, Clock, Star, MapPin, Info } from 'lucide-react';
import { useData, useNow } from '../hooks';
import { useStore } from '../store';
import { VENUE_LABEL, AMENITY } from '../data';
import Hours from '../components/Hours';
import { ReviewList } from '../components/Reviews';
import MapView from '../components/MapView';
import { rp, km, mins, titleCase, num } from '../lib/format';
import { distM, mapsUrl } from '../lib/geo';
import { hoursFor, busyAt, statusOf, estimateCharge, compatible, priceParts } from '../lib/model';
import { vehicleById } from '../vehicles';

export default function Detail() {
  const { id } = useParams();
  const nav = useNavigate();
  const d = useData();
  const now = useNow();
  const { t, lang, location, favorites, toggleFav, vehicleId, showToast } = useStore(s => ({ t: s.t, lang: s.lang, location: s.location, favorites: s.favorites, toggleFav: s.toggleFav, vehicleId: s.vehicleId, showToast: s.showToast }));
  const s = d?.stations.find(x => x.id === id);
  const veh = vehicleById(vehicleId);
  const [showAll, setShowAll] = useState(false);
  const est = useMemo(() => { if (!s) return null; const p = s.plugs.find(p => compatible(veh, p.type)) || s.plugs[0]; const ok = compatible(veh, p.type); const e = estimateCharge(veh, p.kw, p.type, 20, 80); return { p, ok, ...e, cost: e.kwh * s.priceKwh }; }, [s, veh]);
  if (!d || !s) return <div className="content"><div className="skeleton" style={{ height: 240 }} /><div className="skeleton" style={{ height: 120 }} /></div>;

  const hours = hoursFor(s, d.meta); const nowH = now.getHours(); const b = busyAt(hours, nowH);
  const st = statusOf(s); const v = VENUE_LABEL[s.venue]; const fav = favorites.includes(s.id);
  const parts = priceParts(s.priceKwh, d.meta, s.priceEstimated);
  const share = async () => { const url = window.location.href; try { if (navigator.share) await navigator.share({ title: titleCase(s.name), text: `${titleCase(s.name)} — ${s.address}`, url }); else { await navigator.clipboard.writeText(url); showToast(t('copied')); } } catch { /* cancelled */ } };
  const copy = async () => { try { await navigator.clipboard.writeText(s.address); showToast(t('copied')); } catch { /* ignore */ } };

  return (
    <div className="page">
      <div className={'hero' + (s.operator !== 'PLN' ? ' mitra' : '')}>
        <div className="row sp">
          <button className="iconbtn" onClick={() => nav(-1)}><ChevronLeft size={22} /></button>
          <div className="row"><button className="iconbtn" onClick={share}><Share2 size={18} /></button><button className="iconbtn" onClick={() => toggleFav(s.id)}><Heart size={18} fill={fav ? '#fff' : 'none'} /></button></div>
        </div>
        <div className="venue">{v.icon}</div>
        <h1>{titleCase(s.name)}</h1>
        <div className="row wrap" style={{ marginTop: 10 }}>
          <span className="pill"><Zap size={11} /> {s.type} {Math.round(s.kw)} kW</span>
          <span className="pill">{s.operator === 'PLN' ? 'PLN' : t('mitra')}</span>
          <span className="pill">{lang === 'en' ? v.en : v.id}</span>
          <span className="pill"><Star size={11} fill="#fff" /> {s.score.toFixed(1)}</span>
        </div>
        <div className="row wrap small" style={{ marginTop: 12, opacity: .92 }}>
          <span className={'pill ' + (st === 'available' ? 'lime' : st === 'inuse' ? 'amber' : st === 'offline' ? '' : 'red')} style={{ color: st === 'available' ? '#3E6A0C' : undefined }}>{t(st)}</span>
          <span><Clock size={13} style={{ verticalAlign: -2 }} /> {s.open === '24h' ? t('open_24h') : s.open}</span>
          {location && <span><Navigation size={13} style={{ verticalAlign: -2 }} /> {km(distM(location, s))}</span>}
        </div>
      </div>

      <div className="content">
        <div className="grid3">
          <div className="stat g"><div className="n">{rp(s.priceKwh)}</div><div className="l">{t('per_kwh')} {s.priceEstimated ? '(' + t('est') + ')' : ''}</div></div>
          <div className="stat"><div className="n">{s.connectors || s.plugs.reduce((a, p) => a + p.n, 0)}</div><div className="l">{t('connectors')}</div></div>
          <div className="stat"><div className="n" style={{ color: b.level === 'busy' ? 'var(--red)' : b.level === 'moderate' ? 'var(--amber)' : 'var(--g)' }}>{t(b.level)}</div><div className="l">{t('now')}</div></div>
        </div>

        {est && (
          <div className="card" style={{ background: 'linear-gradient(135deg,#F1FBF4,#E3F5EA)', borderColor: 'transparent' }}>
            <div className="row sp"><div className="b">{t('your_cost')}</div><button className="btn sm ghost" onClick={() => nav('/vehicle')}>{veh.brand} {veh.model} · {t('change')}</button></div>
            {est.ok ? (
              <div className="row" style={{ marginTop: 8, gap: 18 }}>
                <div><div className="xs mut">20% → 80%</div><div className="b" style={{ fontSize: 18 }}>{rp(est.cost)}</div></div>
                <div><div className="xs mut">{t('est_energy')}</div><div className="b" style={{ fontSize: 18 }}>{num(est.kwh, 1)} kWh</div></div>
                <div><div className="xs mut">{t('est_time')} @ {est.kw} kW</div><div className="b" style={{ fontSize: 18 }}>{mins(est.minutes)}</div></div>
              </div>
            ) : <div className="small" style={{ color: 'var(--red)', marginTop: 6 }}>{t('incompatible_ac')}</div>}
          </div>
        )}

        <div className="card">
          <h3 style={{ marginBottom: 4 }}>{t('connectors')}</h3>
          {s.plugs.map((p, i) => (
            <div className="plugrow" key={i}>
              <div className={'plugico' + (p.type !== 'Type 2' ? ' dc' : '')}>{p.type === 'Type 2' ? 'T2' : p.type === 'CCS2' ? 'CCS' : 'CHA'}</div>
              <div className="grow"><div className="b">{p.type} · {Math.round(p.kw)} kW {p.type === 'Type 2' ? 'AC' : 'DC'}</div><div className="xs mut">{p.n} {t('units')}{p.trx ? ` · ${num(p.trx)} ${t('sessions_month')}` : ''}{!compatible(veh, p.type) ? ` · ${t('not_compatible')}` : ''}</div></div>
              <span className={'pill ' + (compatible(veh, p.type) ? 'g' : 'red')}>{compatible(veh, p.type) ? '✓' : '✕'}</span>
            </div>
          ))}
          {s.brands && s.brands.length > 0 && <div className="xs mut" style={{ marginTop: 8 }}>{t('brands')}: {s.brands.join(', ')}{s.since ? ` · ${t('operating_since')} ${s.since}` : ''}</div>}
        </div>

        <div className="card">
          <Hours hours={hours} nowH={nowH} />
          <div className="xs mut" style={{ marginTop: 8 }}>{s.usage && s.usage.n >= 25 ? `${t('based_on')} ${num(s.usage.n)} ${t('sessions_month')}` : t('no_usage')}</div>
          {s.usage && (
            <div className="grid3" style={{ marginTop: 10 }}>
              <div className="stat"><div className="n">{num(s.usage.avgKwh, 1)}</div><div className="l">{t('median_kwh')}</div></div>
              <div className="stat"><div className="n">{mins(s.usage.avgMin)}</div><div className="l">{t('median_min')}</div></div>
              <div className="stat"><div className="n">{s.stats ? t(s.stats.tag === 'high' ? 'high_util' : s.stats.tag === 'mid' ? 'mid_util' : 'low_util') : '–'}</div><div className="l">{t('utilisation')}</div></div>
            </div>
          )}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 8 }}>{t('breakdown')} ({t('per_kwh').replace('/', '')})</h3>
          {s.priceEstimated ? <div className="small mut"><Info size={13} style={{ verticalAlign: -2 }} /> {t('price_est_note')}</div> : (
            <>
              <div className="kv"><span className="k">{t('energy')} (PLN)</span><span className="v">{rp(parts.energy)}</span></div>
              <div className="kv"><span className="k">{t('ppj')} {Math.round(parts.ppjRate * 100)}% · {s.city}</span><span className="v">{rp(parts.ppj)}</span></div>
              <div className="kv"><span className="k">{t('admin')}</span><span className="v">Rp 0</span></div>
              <div className="divider" /><div className="kv"><span className="k b">{t('total')}</span><span className="v b">{rp(s.priceKwh)}</span></div>
            </>
          )}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 8 }}>{t('amenities')}</h3>
          <div className="row wrap">{s.amenities.map(a => <span key={a} className="pill">{AMENITY[a]?.icon} {lang === 'en' ? AMENITY[a]?.en : AMENITY[a]?.id}</span>)}</div>
        </div>

        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ height: 180, position: 'relative' }}><MapView stations={[s]} hosts={[]} onSelect={() => {}} userLoc={null} center={s} zoom={14} interactive={false} /></div>
          <div style={{ padding: 14 }}>
            <div className="row sp"><div className="grow"><div className="xs mut b" style={{ textTransform: 'uppercase', letterSpacing: '.04em' }}>{t('address')}</div><div className="small">{s.address || '–'}</div><div className="xs mut">{s.city ? s.city + ', ' : ''}{s.province}{s.up3 ? ` · UP3 ${s.up3}` : ''}</div></div><button className="iconbtn" onClick={copy}><Copy size={16} /></button></div>
            <a className="btn sec full" style={{ marginTop: 10 }} href={mapsUrl(s)} target="_blank" rel="noreferrer"><MapPin size={16} /> {t('directions')} (Google Maps)</a>
          </div>
        </div>

        <ReviewList targetId={s.id} baseScore={s.score} baseCount={s.reviews} />
        <div className="xs mut" style={{ textAlign: 'center' }}>ID SPKLU {s.id} · {t('data_snapshot')}</div>
      </div>

      <div className="sticky-cta">
        <button className="btn lg ghost grow" onClick={() => nav(`/book/station/${s.id}`)}>{t('book')}</button>
        <button className="btn lg grow" disabled={st === 'unavailable' || st === 'maintenance'} onClick={() => nav(`/book/station/${s.id}?now=1`)}><Zap size={18} fill="#fff" /> {t('charge_now')}</button>
      </div>
    </div>
  );
}
