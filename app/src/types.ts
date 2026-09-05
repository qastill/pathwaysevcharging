export type PlugType = 'CCS2' | 'CHAdeMO' | 'Type 2';
export type Venue = 'rest_area' | 'mall' | 'hotel' | 'dealer' | 'fnb' | 'hospital' | 'public' | 'pln' | 'fuel' | 'leisure' | 'residential' | 'office' | 'other';

export interface Plug { type: PlugType; kw: number; n: number; trx: number }

export interface Station {
  id: string; name: string; address: string; lat: number; lng: number;
  kw: number; status: string; chargers: number; connectors: number;
  operator: 'PLN' | 'Mitra'; city?: string; province: string; up3?: string;
  brands?: string[]; since?: number; venue: Venue; venueLabel?: string; type: 'AC' | 'DC';
  stats?: { trx: number; kwh: number; rp: number; tag: 'high' | 'mid' | 'low' };
  plugs: Plug[];
  usage?: { n: number; hours: number[]; dow: number[]; avgMin: number; avgKwh: number; p90Min: number };
  priceKwh: number; priceEstimated?: boolean; speed: 'ultra' | 'fast' | 'medium' | 'slow';
  score: number; reviews: number; amenities: string[]; open: string;
}

export interface Host {
  id: string; name: string; host: string; lat: number; lng: number; area: string; city: string; province: string;
  kw: number; plug: PlugType; priceKwh: number; days: 'daily' | 'weekdays' | 'weekends'; from: string; to: string;
  score: number; reviews: number; sessions: number; vehicle: string; amenities: string[]; note: string; since: number; simulated?: boolean;
  mine?: boolean; active?: boolean; address?: string;
}

export interface Meta {
  builtFrom: string;
  tariff: { energyRp: number; ppjDefault: number; avgAllIn: number; ppjByCity: Record<string, number> };
  hoursByVenue: Record<string, number[]>; hoursAll: number[];
  session: { medianMin: number; medianKwh: number; meanKwh: number };
  assume: { kwh_km: number; ice_kmpl: number; bbm: number; ice_g: number; tarif_rumah: number };
  carbon: { ef_jamali: number; ef_west: number; ev_g_km: number; reduction: number };
  cost: { spklu100: number; home100: number; ice100: number };
  monthly: { year: number; month: string; trx: number; kwh: number; rp: number }[];
  counts: { stations: number; pln: number; mitra: number; dc: number; provinces: number; hosts: number };
  ev_brands: Record<string, number>;
}

export type TargetKind = 'station' | 'host';
export type BookingStatus = 'upcoming' | 'active' | 'completed' | 'cancelled';

export interface Booking {
  id: string; code: string; kind: TargetKind; targetId: string; targetName: string; targetSub: string;
  plug: PlugType; kw: number; date: string; start: string; end: string; startNow?: boolean;
  startSoc: number; targetSoc: number; estKwh: number; estCost: number; priceKwh: number; payment: string;
  status: BookingStatus; created: number; vehicleId: string;
  session?: { startedAt: number; endedAt?: number; kwh: number; cost: number; minutes: number; endSoc: number; km: number; co2Saved: number };
  reviewed?: boolean;
}

export interface Review { id: string; targetId: string; rating: number; text: string; date: number; author: string; tags: string[] }

export interface Listing extends Host { mine: true; active: boolean; address: string; createdAt: number }

export interface LatLng { lat: number; lng: number }
