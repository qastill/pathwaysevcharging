import { useNavigate } from 'react-router-dom';
import { Zap, Home, Star, Navigation } from 'lucide-react';
import type { Station, Host, Meta, LatLng } from '../types';
import { useStore } from '../store';
import { rp, km, titleCase } from '../lib/format';
import { distM } from '../lib/geo';
import { VENUE_LABEL } from '../data';
import { hoursFor, busyAt, statusOf } from '../lib/model';

export function StationCard({ s, meta, loc, selected, onClick, nowH }: { s: Station; meta: Meta; loc: LatLng | null; selected?: boolean; onClick?: () => void; nowH: number }) {
  const { t, lang } = useStore(st => ({ t: st.t, lang: st.lang }));
  const nav = useNavigate();
  const b = busyAt(hoursFor(s, meta), nowH);
  const st = statusOf(s);
  const v = VENUE_LABEL[s.venue];
  return (
    <div className={'station-card' + (selected ? ' sel' : '')} onClick={onClick || (() => nav('/s/' + s.id))}>
      <div className={'ico ' + (s.operator !== 'PLN' ? 'mitra' : s.type === 'DC' ? 'dc' : 'ac')}>{v.icon}</div>
      <div className="grow">
        <div className="name">{titleCase(s.name)}</div>
        <div className="xs mut ell" style={{ marginTop: 2 }}>{loc && <><Navigation size={11} style={{ verticalAlign: -1 }} /> {km(distM(loc, s))} · </>}{s.city || s.province}</div>
        <div className="meta">
          <span className={'pill ' + (s.type === 'DC' ? 'g' : 'teal')}><Zap size={11} />{s.type} {s.kw >= 1 ? Math.round(s.kw) : ''} kW</span>
          <span className={'pill ' + (st === 'available' ? 'lime' : st === 'inuse' ? 'amber' : st === 'offline' ? '' : 'red')}>{t(st)}</span>
          {s.stats && s.stats.tag === 'high' && <span className="pill">{t('popular')}</span>}
          {s.usage && <span className={'pill ' + (b.level === 'busy' ? 'red' : b.level === 'moderate' ? 'amber' : 'g')}>{t(b.level)}</span>}
        </div>
      </div>
      <div className="price">
        <span className="p">{rp(s.priceKwh)}<span className="xs mut" style={{ fontWeight: 600 }}>{t('per_kwh')}</span></span>
        <span className="xs mut"><Star size={11} fill="#F59E0B" color="#F59E0B" style={{ verticalAlign: -1 }} /> {s.score.toFixed(1)}{s.operator !== 'PLN' && <> · {lang === 'en' ? 'private' : 'mitra'}</>}</span>
      </div>
    </div>
  );
}

export function HostCard({ h, loc, selected, onClick }: { h: Host; loc: LatLng | null; selected?: boolean; onClick?: () => void }) {
  const t = useStore(st => st.t);
  const nav = useNavigate();
  return (
    <div className={'station-card' + (selected ? ' sel' : '')} onClick={onClick || (() => nav('/h/' + h.id))}>
      <div className="ico host"><Home size={22} color="#9A5B00" /></div>
      <div className="grow">
        <div className="name">{h.name} {h.mine && <span className="pill amber" style={{ marginLeft: 4 }}>{t('my_listings')}</span>}</div>
        <div className="xs mut ell" style={{ marginTop: 2 }}>{loc && <><Navigation size={11} style={{ verticalAlign: -1 }} /> {km(distM(loc, h))} · </>}{h.area}</div>
        <div className="meta">
          <span className="pill amber"><Zap size={11} />AC {h.kw} kW</span>
          <span className="pill">{h.from}–{h.to}</span>
          <span className="pill">{t(h.days)}</span>
        </div>
      </div>
      <div className="price">
        <span className="p">{rp(h.priceKwh)}<span className="xs mut" style={{ fontWeight: 600 }}>{t('per_kwh')}</span></span>
        <span className="xs mut"><Star size={11} fill="#F59E0B" color="#F59E0B" style={{ verticalAlign: -1 }} /> {h.score.toFixed(1)} ({h.reviews})</span>
      </div>
    </div>
  );
}
