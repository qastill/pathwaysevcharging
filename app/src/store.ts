import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Booking, Review, Listing, LatLng } from './types';
import type { Lang } from './i18n';
import { DEFAULT_VEHICLE } from './vehicles';
import { t as tr, type Key } from './i18n';

export interface HostRequest { id: string; listingId: string; guest: string; vehicle: string; date: string; start: string; kwh: number; amount: number; status: 'pending' | 'accepted' | 'declined' }

interface State {
  lang: Lang; onboarded: boolean; userName: string; vehicleId: string; plate: string;
  favorites: string[]; bookings: Booking[]; reviews: Review[]; listings: Listing[]; requests: HostRequest[];
  location: LatLng | null; locationSource: 'gps' | 'default' | null;
  toast: string | null;
  set: (p: Partial<State>) => void;
  t: (k: Key) => string;
  toggleFav: (id: string) => void;
  addBooking: (b: Booking) => void; updateBooking: (id: string, p: Partial<Booking>) => void;
  addReview: (r: Review) => void; upsertListing: (l: Listing) => void; removeListing: (id: string) => void;
  showToast: (m: string) => void; resetDemo: () => void;
}

export const useStore = create<State>()(
  persist(
    (set, get) => ({
      lang: 'id', onboarded: false, userName: '', vehicleId: DEFAULT_VEHICLE, plate: '',
      favorites: [], bookings: [], reviews: [], listings: [], requests: [], location: null, locationSource: null, toast: null,
      set: p => set(p),
      t: k => tr(k, get().lang),
      toggleFav: id => set(s => ({ favorites: s.favorites.includes(id) ? s.favorites.filter(x => x !== id) : [...s.favorites, id] })),
      addBooking: b => set(s => ({ bookings: [b, ...s.bookings] })),
      updateBooking: (id, p) => set(s => ({ bookings: s.bookings.map(b => (b.id === id ? { ...b, ...p } : b)) })),
      addReview: r => set(s => ({ reviews: [r, ...s.reviews] })),
      upsertListing: l => set(s => ({ listings: s.listings.some(x => x.id === l.id) ? s.listings.map(x => (x.id === l.id ? l : x)) : [l, ...s.listings] })),
      removeListing: id => set(s => ({ listings: s.listings.filter(x => x.id !== id), requests: s.requests.filter(r => r.listingId !== id) })),
      showToast: m => { set({ toast: m }); setTimeout(() => set(s => (s.toast === m ? { toast: null } : {})), 2600); },
      resetDemo: () => set({ bookings: [], reviews: [], listings: [], requests: [], favorites: [] }),
    }),
    { name: 'ngecas-v1', partialize: s => ({ lang: s.lang, onboarded: s.onboarded, userName: s.userName, vehicleId: s.vehicleId, plate: s.plate, favorites: s.favorites, bookings: s.bookings, reviews: s.reviews, listings: s.listings, requests: s.requests, location: s.location, locationSource: s.locationSource }) },
  ),
);
export const useT = () => useStore(s => s.t);
