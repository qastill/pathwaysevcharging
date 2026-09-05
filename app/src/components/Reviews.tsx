import { useState } from 'react';
import { useStore } from '../store';
import { Modal, Stars } from './ui';
import { uid, longDate } from '../lib/format';

const TAGS = ['tag_works', 'tag_fast', 'tag_easy', 'tag_queue', 'tag_broken', 'tag_friendly'] as const;

export function ReviewForm({ targetId, open, onClose, onDone }: { targetId: string; open: boolean; onClose: () => void; onDone?: () => void }) {
  const { t, addReview, userName, showToast } = useStore(s => ({ t: s.t, addReview: s.addReview, userName: s.userName, showToast: s.showToast }));
  const [rating, setRating] = useState(5); const [text, setText] = useState(''); const [tags, setTags] = useState<string[]>([]);
  const submit = () => { addReview({ id: uid(), targetId, rating, text: text.trim(), date: Date.now(), author: userName || 'Pengguna Ngecas', tags }); showToast(t('thanks')); onClose(); onDone && onDone(); setText(''); setTags([]); };
  return (
    <Modal open={open} onClose={onClose}>
      <h2 style={{ marginBottom: 12 }}>{t('write_review')}</h2>
      <div className="col" style={{ gap: 14 }}>
        <div className="field"><label className="lbl">{t('rating')}</label><Stars value={rating} onChange={setRating} size={36} /></div>
        <div className="chips" style={{ flexWrap: 'wrap' }}>{TAGS.map(k => <button key={k} className={'chip' + (tags.includes(k) ? ' on' : '')} onClick={() => setTags(tags.includes(k) ? tags.filter(x => x !== k) : [...tags, k])}>{t(k)}</button>)}</div>
        <textarea className="input" placeholder={t('review_ph')} value={text} onChange={e => setText(e.target.value)} />
        <button className="btn lg full" onClick={submit}>{t('submit')}</button>
      </div>
    </Modal>
  );
}

export function ReviewList({ targetId, baseScore, baseCount }: { targetId: string; baseScore: number; baseCount: number }) {
  const { t, reviews, lang } = useStore(s => ({ t: s.t, reviews: s.reviews, lang: s.lang }));
  const [open, setOpen] = useState(false);
  const mine = reviews.filter(r => r.targetId === targetId);
  const score = mine.length ? (baseScore * baseCount + mine.reduce((a, r) => a + r.rating, 0)) / (baseCount + mine.length) : baseScore;
  return (
    <div className="card">
      <div className="row sp" style={{ marginBottom: 8 }}>
        <div><h3>{t('reviews')}</h3><div className="small mut">★ {score.toFixed(1)} · {baseCount + mine.length} {t('reviews').toLowerCase()}</div></div>
        <button className="btn sm sec" onClick={() => setOpen(true)}>{t('write_review')}</button>
      </div>
      {mine.length === 0 ? <div className="small mut">{t('no_reviews')}</div> : mine.map(r => (
        <div key={r.id} style={{ padding: '10px 0', borderTop: '1px solid var(--line2)' }}>
          <div className="row sp"><span className="sb small">{r.author}</span><span className="xs mut">{longDate(r.date, lang)}</span></div>
          <div style={{ color: 'var(--amber)', fontSize: 13 }}>{'★'.repeat(r.rating)}<span style={{ color: 'var(--line)' }}>{'★'.repeat(5 - r.rating)}</span></div>
          {r.tags.length > 0 && <div className="row wrap" style={{ gap: 4, margin: '4px 0' }}>{r.tags.map(k => <span key={k} className="pill">{t(k as any)}</span>)}</div>}
          {r.text && <div className="small" style={{ marginTop: 4 }}>{r.text}</div>}
        </div>
      ))}
      <ReviewForm targetId={targetId} open={open} onClose={() => setOpen(false)} />
    </div>
  );
}
