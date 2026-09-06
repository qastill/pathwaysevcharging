import type { Station, Host, Meta } from './types';

type Bundle = { stations: Station[]; hosts: Host[]; meta: Meta };
let cache: Bundle | null = null;
let pending: Promise<Bundle> | null = null;

export async function loadData() {
  if (cache) return cache;
  if (!pending) {
    pending = (async () => {
      const base = import.meta.env.BASE_URL || '/';
      const [s, h, m] = await Promise.all([
        fetch(base + 'data/stations.json').then(r => r.json()),
        fetch(base + 'data/hosts.json').then(r => r.json()),
        fetch(base + 'data/meta.json').then(r => r.json()),
      ]);
      cache = { stations: s, hosts: h, meta: m } as Bundle;
      return cache;
    })();
  }
  return pending;
}
export const getData = () => cache;

export const VENUE_LABEL: Record<string, { id: string; en: string; icon: string }> = {
  rest_area: { id: 'Rest area tol', en: 'Toll rest area', icon: '🛣️' },
  mall: { id: 'Mall / ritel', en: 'Mall / retail', icon: '🛍️' },
  hotel: { id: 'Hotel', en: 'Hotel', icon: '🏨' },
  dealer: { id: 'Dealer mobil', en: 'Car dealer', icon: '🚗' },
  fnb: { id: 'Kafe / resto', en: 'Café / restaurant', icon: '☕' },
  hospital: { id: 'Rumah sakit', en: 'Hospital', icon: '🏥' },
  public: { id: 'Fasilitas publik', en: 'Public facility', icon: '🏛️' },
  pln: { id: 'Kantor PLN', en: 'PLN office', icon: '⚡' },
  fuel: { id: 'SPBU', en: 'Fuel station', icon: '⛽' },
  leisure: { id: 'Wisata', en: 'Leisure', icon: '🌴' },
  residential: { id: 'Perumahan', en: 'Residential', icon: '🏘️' },
  office: { id: 'Perkantoran', en: 'Office', icon: '🏢' },
  other: { id: 'Lokasi umum', en: 'General site', icon: '📍' },
  home: { id: 'Charger rumah', en: 'Home charger', icon: '🏠' },
};

export const AMENITY: Record<string, { id: string; en: string; icon: string }> = {
  toilet: { id: 'Toilet', en: 'Restroom', icon: '🚻' }, musala: { id: 'Musala', en: 'Prayer room', icon: '🕌' }, food: { id: 'Makanan', en: 'Food', icon: '🍜' },
  parking: { id: 'Parkir luas', en: 'Parking', icon: '🅿️' }, wifi: { id: 'Wi-Fi', en: 'Wi-Fi', icon: '📶' }, covered: { id: 'Carport tertutup', en: 'Covered carport', icon: '🏠' },
  cctv: { id: 'CCTV', en: 'CCTV', icon: '📹' }, coffee: { id: 'Kopi', en: 'Coffee', icon: '☕' }, wide: { id: 'Akses mobil besar', en: 'Wide access', icon: '🚙' },
};
