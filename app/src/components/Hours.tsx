import { useStore } from '../store';
import { busyAt } from '../lib/model';

export default function Hours({ hours, nowH, compact }: { hours: number[]; nowH: number; compact?: boolean }) {
  const t = useStore(s => s.t);
  const max = Math.max(1, ...hours);
  const b = busyAt(hours, nowH);
  return (
    <div>
      {!compact && (
        <div className="row sp" style={{ marginBottom: 8 }}>
          <span className="small mut">{t('popular_hours')}</span>
          <span className={'pill ' + (b.level === 'busy' ? 'red' : b.level === 'moderate' ? 'amber' : 'g')}>{t(b.level)} {t('now')}</span>
        </div>
      )}
      <div className="hours" style={compact ? { height: 40 } : undefined}>
        {hours.map((v, h) => <div key={h} className={h === nowH ? 'now' : v / max > 0.72 ? 'hi' : ''} style={{ height: Math.max(3, (v / max) * 100) + '%' }} title={`${h}:00 — ${v}`} />)}
      </div>
      <div className="hours-x"><span>00</span><span>06</span><span>12</span><span>18</span><span>23</span></div>
    </div>
  );
}
