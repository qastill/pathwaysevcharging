import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, X } from 'lucide-react';
import { TopBar, Empty, Modal } from '../components/ui';
import { useStore } from '../store';
import type { Booking } from '../types';
import { rp, num, dateLabel, mins } from '../lib/format';

export default function Bookings() {
  const nav = useNavigate();
  const { t, lang, bookings, updateBooking } = useStore(s => ({ t: s.t, lang: s.lang, bookings: s.bookings, updateBooking: s.updateBooking }));
  const [tab, setTab] = useState<'upcoming' | 'completed' | 'cancelled'>('upcoming');
  const [cancel, setCancel] = useState<Booking | null>(null);
  const list = bookings.filter(b => (tab === 'upcoming' ? b.status === 'upcoming' || b.status === 'active' : b.status === tab));
  return (
    <div className="page">
      <TopBar title={t('tab_bookings')} back={false} />
      <div className="content">
        <div className="seg">{(['upcoming', 'completed', 'cancelled'] as const).map(k => <button key={k} className={tab === k ? 'on' : ''} onClick={() => setTab(k)}>{t(k)}</button>)}</div>
        {list.length === 0 ? <Empty icon="🗓️" title={t('no_bookings')} action={<button className="btn sec" onClick={() => nav('/')}>{t('find_charger')}</button>} /> : list.map(b => (
          <div key={b.id} className="card">
            <div className="row sp"><span className="xs mut">{dateLabel(b.date, lang)} · {b.start}{b.end ? '–' + b.end : ''}</span><span className={'pill ' + (b.status === 'active' ? 'lime' : b.status === 'upcoming' ? 'g' : b.status === 'completed' ? '' : 'red')}>{t(b.status)}</span></div>
            <div className="row" style={{ margin: '8px 0' }}><span style={{ fontSize: 26 }}>{b.kind === 'host' ? '🏠' : '⚡'}</span><div className="grow"><div className="b">{b.targetName}</div><div className="xs mut">{b.targetSub} · {b.plug} {b.kw} kW</div></div></div>
            <div className="grid3">
              <div className="stat" style={{ padding: 8 }}><div className="n" style={{ fontSize: 16 }}>{num(b.session?.kwh ?? b.estKwh, 1)}</div><div className="l">kWh</div></div>
              <div className="stat" style={{ padding: 8 }}><div className="n" style={{ fontSize: 16 }}>{b.session ? mins(b.session.minutes) : `${b.startSoc}→${b.targetSoc}%`}</div><div className="l">{b.session ? t('duration') : t('battery')}</div></div>
              <div className="stat" style={{ padding: 8 }}><div className="n" style={{ fontSize: 16 }}>{rp(b.session?.cost ?? b.estCost, { compact: true })}</div><div className="l">{t('code')} {b.code}</div></div>
            </div>
            <div className="row" style={{ marginTop: 10 }}>
              {b.status === 'upcoming' && <><button className="btn sm ghost" onClick={() => setCancel(b)}>{t('cancel')}</button><button className="btn sm grow" onClick={() => nav('/session/' + b.id)}><Zap size={14} fill="#fff" /> {t('start')}</button></>}
              {b.status === 'active' && <button className="btn sm lime grow" onClick={() => nav('/session/' + b.id)}><Zap size={14} /> {t('continue')}</button>}
              {b.status === 'completed' && <button className="btn sm sec grow" onClick={() => nav('/done/' + b.id)}>{t('view')}</button>}
              <button className="btn sm ghost" onClick={() => nav((b.kind === 'host' ? '/h/' : '/s/') + b.targetId)}>{t('details')}</button>
            </div>
          </div>
        ))}
      </div>
      <Modal open={!!cancel} onClose={() => setCancel(null)}>
        <h2 style={{ marginBottom: 6 }}>{t('cancel_q')}</h2><div className="small mut" style={{ marginBottom: 16 }}>{cancel?.targetName} · {cancel && dateLabel(cancel.date, lang)} {cancel?.start}</div>
        <div className="row"><button className="btn ghost grow" onClick={() => setCancel(null)}>{t('keep')}</button><button className="btn danger grow" onClick={() => { updateBooking(cancel!.id, { status: 'cancelled' }); setCancel(null); }}><X size={16} /> {t('yes_cancel')}</button></div>
      </Modal>
    </div>
  );
}
