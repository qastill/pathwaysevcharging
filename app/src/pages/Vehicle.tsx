import { useNavigate } from 'react-router-dom';
import { TopBar } from '../components/ui';
import { useStore } from '../store';
import { VEHICLES } from '../vehicles';

export default function Vehicle() {
  const nav = useNavigate();
  const { t, vehicleId, plate, set, showToast } = useStore(s => ({ t: s.t, vehicleId: s.vehicleId, plate: s.plate, set: s.set, showToast: s.showToast }));
  return (
    <div className="page">
      <TopBar title={t('choose_vehicle')} line />
      <div className="content">
        <div className="field"><label className="lbl">{t('plate')} ({t('optional')})</label><input className="input" value={plate} onChange={e => set({ plate: e.target.value.toUpperCase() })} placeholder="D 1234 EV" /></div>
        <div className="grid2">
          {VEHICLES.map(v => (
            <button key={v.id} className="card click" style={{ textAlign: 'left', borderColor: v.id === vehicleId ? 'var(--g)' : undefined, background: v.id === vehicleId ? 'var(--mint)' : undefined }} onClick={() => { set({ vehicleId: v.id }); showToast(`${v.brand} ${v.model} ✓`); nav(-1); }}>
              <div className="xs mut b">{v.brand}</div><div className="b">{v.model}</div>
              <div className="xs mut" style={{ marginTop: 6 }}>{v.battery} kWh · {v.plug}<br />AC {v.ac} kW{v.dc ? ` · DC ${v.dc} kW` : ' · AC only'}<br />≈ {v.range} km</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
