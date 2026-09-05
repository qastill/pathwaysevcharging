import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store';

export default function Onboarding() {
  const nav = useNavigate();
  const { t, lang, set } = useStore(s => ({ t: s.t, lang: s.lang, set: s.set }));
  const [i, setI] = useState(0);
  const slides = [['🗺️', 'ob1_t', 'ob1_d'], ['📊', 'ob2_t', 'ob2_d'], ['🔌', 'ob3_t', 'ob3_d']] as const;
  const finish = () => { set({ onboarded: true }); nav('/', { replace: true }); };
  return (
    <div className="ob">
      <div className="row sp"><span className="b" style={{ fontSize: 18 }}>⚡ {t('app')}</span><div className="row"><button className="btn sm" style={{ background: 'rgba(255,255,255,.18)' }} onClick={() => set({ lang: lang === 'id' ? 'en' : 'id' })}>{lang === 'id' ? 'EN' : 'ID'}</button><button className="btn sm" style={{ background: 'transparent', color: 'rgba(255,255,255,.8)' }} onClick={finish}>{t('skip')}</button></div></div>
      <div className="art">{slides[i][0]}</div>
      <h1>{t(slides[i][1])}</h1>
      <p>{t(slides[i][2])}</p>
      <div className="dots">{slides.map((_, k) => <i key={k} className={k === i ? 'on' : ''} />)}</div>
      <button className="btn lg lime full" onClick={() => (i < 2 ? setI(i + 1) : finish())}>{i < 2 ? t('next') : t('get_started')}</button>
    </div>
  );
}
