import { useEffect, useState, useMemo } from 'react';
import { loadData } from './data';
import { useStore } from './store';
import type { Station, Host, Meta, LatLng } from './types';
import { DEFAULT_CENTER } from './lib/geo';

export function useData() {
  const [d, setD] = useState<{ stations: Station[]; hosts: Host[]; meta: Meta } | null>(null);
  useEffect(() => { let on = true; loadData().then(x => on && setD(x)); return () => { on = false; }; }, []);
  return d;
}

export function useAllHosts(hosts: Host[] | undefined) {
  const listings = useStore(s => s.listings);
  return useMemo(() => [...listings.filter(l => l.active), ...(hosts || [])], [hosts, listings]);
}

let locating = false;
export async function locate(silent = false): Promise<LatLng> {
  const st = useStore.getState();
  if (locating) return st.location || DEFAULT_CENTER;
  locating = true;
  try {
    const pos = await new Promise<GeolocationPosition>((res, rej) => {
      if (!navigator.geolocation) return rej(new Error('no geolocation'));
      navigator.geolocation.getCurrentPosition(res, rej, { enableHighAccuracy: true, timeout: 9000, maximumAge: 60000 });
    });
    const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
    st.set({ location: loc, locationSource: 'gps' });
    return loc;
  } catch {
    if (!st.location) st.set({ location: DEFAULT_CENTER, locationSource: 'default' });
    if (!silent) st.showToast(st.t('loc_denied'));
    return st.location || DEFAULT_CENTER;
  } finally { locating = false; }
}

export function useNow(intervalMs = 30000) {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => { const id = setInterval(() => setNow(new Date()), intervalMs); return () => clearInterval(id); }, [intervalMs]);
  return now;
}

export function useInstallPrompt() {
  const [evt, setEvt] = useState<any>(null);
  useEffect(() => {
    const h = (e: any) => { e.preventDefault(); setEvt(e); };
    window.addEventListener('beforeinstallprompt', h);
    return () => window.removeEventListener('beforeinstallprompt', h);
  }, []);
  return evt;
}
