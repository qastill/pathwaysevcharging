import { HashRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import TabBar from './components/TabBar';
import { Toast } from './components/ui';
import { useStore } from './store';
import Home from './pages/Home';
import Detail from './pages/Detail';
import HostDetail from './pages/HostDetail';
import Book from './pages/Book';
import Session from './pages/Session';
import Done from './pages/Done';
import Bookings from './pages/Bookings';
import Charge from './pages/Charge';
import Host from './pages/Host';
import HostForm from './pages/HostForm';
import Profile from './pages/Profile';
import Vehicle from './pages/Vehicle';
import Trip from './pages/Trip';
import Insights from './pages/Insights';
import Onboarding from './pages/Onboarding';
import { loadData } from './data';

function Shell() {
  const onboarded = useStore(s => s.onboarded);
  const loc = useLocation();
  useEffect(() => { loadData(); }, []);
  useEffect(() => { document.querySelector('.page')?.scrollTo?.(0, 0); }, [loc.pathname]);
  if (!onboarded && loc.pathname !== '/onboarding') return <Navigate to="/onboarding" replace />;
  const bare = loc.pathname === '/onboarding';
  return (
    <div className="shell">
      <div className="grow" style={{ minHeight: 0, height: '100%', position: 'relative' }}>
        <Routes>
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/" element={<Home />} />
          <Route path="/s/:id" element={<Detail />} />
          <Route path="/h/:id" element={<HostDetail />} />
          <Route path="/book/:kind/:id" element={<Book />} />
          <Route path="/session/:id" element={<Session />} />
          <Route path="/done/:id" element={<Done />} />
          <Route path="/bookings" element={<Bookings />} />
          <Route path="/charge" element={<Charge />} />
          <Route path="/host" element={<Host />} />
          <Route path="/host/new" element={<HostForm />} />
          <Route path="/host/edit/:id" element={<HostForm />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/vehicle" element={<Vehicle />} />
          <Route path="/trip" element={<Trip />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      {!bare && <TabBar />}
      <Toast />
    </div>
  );
}
export default function App() { return <HashRouter><Shell /></HashRouter>; }
