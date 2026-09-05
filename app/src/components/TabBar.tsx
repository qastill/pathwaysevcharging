import { NavLink, useLocation } from 'react-router-dom';
import { Map, CalendarCheck, Zap, Home, User } from 'lucide-react';
import { useStore } from '../store';

export default function TabBar() {
  const { t, bookings } = useStore(s => ({ t: s.t, bookings: s.bookings }));
  const active = bookings.find(b => b.status === 'active');
  const loc = useLocation();
  const on = (p: string) => (loc.pathname === p || (p !== '/' && loc.pathname.startsWith(p)) ? 'on' : '');
  return (
    <nav className="tabbar">
      <NavLink to="/" className={on('/') || on('/s') || on('/h')}><Map size={22} />{t('tab_map')}</NavLink>
      <NavLink to="/bookings" className={on('/bookings')}><CalendarCheck size={22} />{t('tab_bookings')}</NavLink>
      <NavLink to={active ? '/session/' + active.id : '/charge'} className={'fab' + (active ? ' live' : '') + ' ' + (on('/session') || on('/charge'))}><span className="ic"><Zap size={24} fill="#fff" /></span>{t('tab_charge')}</NavLink>
      <NavLink to="/host" className={on('/host')}><Home size={22} />{t('tab_host')}</NavLink>
      <NavLink to="/profile" className={on('/profile') || on('/vehicle') || on('/trip') || on('/insights')}><User size={22} />{t('tab_profile')}</NavLink>
    </nav>
  );
}
