import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import { useStore } from '../store';

export function TopBar({ title, right, back = true, line }: { title?: React.ReactNode; right?: React.ReactNode; back?: boolean; line?: boolean }) {
  const nav = useNavigate();
  return (
    <div className={'topbar' + (line ? ' line' : '')}>
      {back && <button className="iconbtn ghost" onClick={() => (window.history.length > 1 ? nav(-1) : nav('/'))} aria-label="back"><ChevronLeft size={22} /></button>}
      <h2 className="ell">{title}</h2>
      {right}
    </div>
  );
}
export function Toast() {
  const toast = useStore(s => s.toast);
  return toast ? <div className="toast">{toast}</div> : null;
}
export function Modal({ open, onClose, children }: { open: boolean; onClose: () => void; children: React.ReactNode }) {
  useEffect(() => { if (!open) return; const h = (e: KeyboardEvent) => e.key === 'Escape' && onClose(); window.addEventListener('keydown', h); return () => window.removeEventListener('keydown', h); }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="modal-bg" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}><div className="handle" />{children}</div>
    </div>
  );
}
export function Stars({ value, onChange, size = 30 }: { value: number; onChange?: (v: number) => void; size?: number }) {
  return (
    <div className="stars">{[1, 2, 3, 4, 5].map(i => <button key={i} type="button" style={{ fontSize: size }} className={i <= value ? 'on' : ''} onClick={() => onChange && onChange(i)}>★</button>)}</div>
  );
}
export function Empty({ icon, title, sub, action }: { icon: string; title: string; sub?: string; action?: React.ReactNode }) {
  return <div className="empty"><div className="ic">{icon}</div><div className="b" style={{ color: 'var(--ink)' }}>{title}</div>{sub && <div className="small">{sub}</div>}{action}</div>;
}
export function Skeleton({ h = 80, n = 3 }: { h?: number; n?: number }) {
  return <>{Array.from({ length: n }).map((_, i) => <div key={i} className="skeleton" style={{ height: h }} />)}</>;
}
