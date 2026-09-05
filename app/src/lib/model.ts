// Domain helpers: busy level, slot availability, charge estimates, pricing.
import type { Station, Host, Meta, PlugType } from '../types';
import type { Vehicle } from '../vehicles';
import { hash } from './format';

export type Busy = 'quiet' | 'moderate' | 'busy';

export function hoursFor(s: Station, meta: Meta): number[] {
  if (s.usage && s.usage.n >= 25) return s.usage.hours;
  return meta.hoursByVenue[s.venue] || meta.hoursAll;
}
export function busyAt(hours: number[], h: number): { level: Busy; ratio: number } {
  const max = Math.max(1, ...hours); const ratio = hours[h] / max;
  return { level: ratio > 0.72 ? 'busy' : ratio > 0.4 ? 'moderate' : 'quiet', ratio };
}
export function slotOpen(s: Station, date: string, h: number, hours: number[]) {
  if (s.open !== '24h' && (h < 8 || h >= 22)) return false;
  const { ratio } = busyAt(hours, h);
  // deterministic pseudo-availability: busier hours at small sites are more often taken
  const cap = Math.max(1, s.connectors);
  const p = hash(s.id + date + h);
  return !(ratio > 0.6 && p < (ratio - 0.55) * (2.2 / cap));
}
export function hostOpen(hst: Host, date: string, h: number) {
  const d = new Date(date + 'T00:00:00').getDay();
  if (hst.days === 'weekdays' && (d === 0 || d === 6)) return false;
  if (hst.days === 'weekends' && d !== 0 && d !== 6) return false;
  const f = parseInt(hst.from), t = parseInt(hst.to);
  if (hst.from === '00:00' && hst.to === '24:00') return true;
  if (f < t) return h >= f && h < t;
  return h >= f || h < t; // overnight window
}

// price components per kWh: energy + PPJ levy; admin 0 (PLN Mobile) — matches observed transactions
export function priceParts(priceKwh: number, meta: Meta, estimated?: boolean) {
  if (estimated) return { energy: priceKwh, ppj: 0, ppjRate: 0 };
  const energy = meta.tariff.energyRp; const ppj = Math.max(0, priceKwh - energy);
  return { energy, ppj, ppjRate: ppj / energy };
}

// realistic charge curve: AC = flat at min(car AC, plug); DC = min(car DC, plug) up to 80 %, then tapers
export function estimateCharge(v: Vehicle, plugKw: number, plugType: PlugType, startSoc: number, targetSoc: number) {
  const dc = plugType !== 'Type 2';
  const kw = dc ? Math.min(v.dc || 0, plugKw) : Math.min(v.ac, plugKw);
  const kwh = ((targetSoc - startSoc) / 100) * v.battery;
  if (kw <= 0 || kwh <= 0) return { kwh: Math.max(0, kwh), minutes: 0, kw: 0 };
  let minutes = 0;
  for (let soc = startSoc; soc < targetSoc; soc += 1) {
    const p = dc && soc >= 80 ? kw * Math.max(0.25, 1 - (soc - 80) / 25) : dc && soc < 10 ? kw * 0.7 : kw;
    minutes += ((v.battery / 100) / (p * 0.93)) * 60; // 93 % charging efficiency
  }
  return { kwh: Math.round(kwh * 10) / 10, minutes: Math.round(minutes), kw };
}
export function compatible(v: Vehicle, plug: PlugType) {
  if (plug === 'Type 2') return true;
  if (plug === 'CCS2') return v.plug === 'CCS2' && v.dc > 0;
  return false; // CHAdeMO: no current Indonesian-market model in the catalogue
}
export function co2Saved(kwh: number, meta: Meta) {
  const km = kwh / meta.assume.kwh_km;
  return { km, kg: (km * (meta.assume.ice_g - meta.carbon.ev_g_km)) / 1000 };
}
export const statusOf = (s: Station): 'available' | 'inuse' | 'unavailable' | 'maintenance' | 'offline' =>
  s.status === 'available' ? 'available' : s.status === 'inuse' ? 'inuse' : s.status === 'maintenance' ? 'maintenance' : s.status === 'unavailable' ? 'unavailable' : 'offline';
