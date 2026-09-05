import { useNavigate } from 'react-router-dom';
import { TopBar, Empty } from '../components/ui';
import { useStore } from '../store';
import { dateLabel } from '../lib/format';

export default function Charge() {
  const nav = useNavigate();
  const { t, lang, bookings } = useStore(s => ({ t: s.t, lang: s.lang, bookings: s.bookings }));
  const up = bookings.filter(b => b.status === 'upcoming').sort((a, b) => (a.date + a.start).localeCompare(b.date + b.start));
  return (
    <div className="page">
      <TopBar title={t('tab_charge')} back={false} />
      <div className="content">
        <Empty icon="🔌" title={t('no_active')} sub={t('no_active_d')} action={<button className="btn" onClick={() => nav('/')}>{t('find_charger')}</button>} />
        {up.length > 0 && <><h3>{t('upcoming')}</h3>{up.map(b => <div key={b.id} className="card click row" onClick={() => nav('/session/' + b.id)}><span style={{ fontSize: 24 }}>{b.kind === 'host' ? '🏠' : '⚡'}</span><div className="grow"><div className="b">{b.targetName}</div><div className="xs mut">{dateLabel(b.date, lang)} · {b.start} · {b.code}</div></div><button className="btn sm">{t('start')}</button></div>)}</>}
      </div>
    </div>
  );
}
