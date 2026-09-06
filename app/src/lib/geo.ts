import type { LatLng } from '../types';
const R = 6371000;
export const distM = (a: LatLng, b: LatLng) => {
  const dLat = ((b.lat - a.lat) * Math.PI) / 180, dLng = ((b.lng - a.lng) * Math.PI) / 180;
  const s = Math.sin(dLat / 2) ** 2 + Math.cos((a.lat * Math.PI) / 180) * Math.cos((b.lat * Math.PI) / 180) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(s));
};
// distance from point p to segment ab, in metres (equirectangular approx — fine for ≤ 500 km corridors)
export const distToSegM = (p: LatLng, a: LatLng, b: LatLng) => {
  const kx = 111320 * Math.cos((p.lat * Math.PI) / 180), ky = 110574;
  const px = (p.lng - a.lng) * kx, py = (p.lat - a.lat) * ky, bx = (b.lng - a.lng) * kx, by = (b.lat - a.lat) * ky;
  const l2 = bx * bx + by * by; let t = l2 ? (px * bx + py * by) / l2 : 0; t = Math.max(0, Math.min(1, t));
  const dx = px - t * bx, dy = py - t * by; return { d: Math.sqrt(dx * dx + dy * dy), t };
};
export const mapsUrl = (p: LatLng) => `https://www.google.com/maps/dir/?api=1&destination=${p.lat},${p.lng}`;
export const DEFAULT_CENTER: LatLng = { lat: -6.6, lng: 107.05 };
export const CITIES: { name: string; lat: number; lng: number }[] = [
  { name: 'Jakarta', lat: -6.2088, lng: 106.8456 }, { name: 'Bandung', lat: -6.9175, lng: 107.6191 }, { name: 'Bekasi', lat: -6.2383, lng: 106.9756 },
  { name: 'Depok', lat: -6.4025, lng: 106.7942 }, { name: 'Bogor', lat: -6.5971, lng: 106.806 }, { name: 'Tangerang', lat: -6.1783, lng: 106.6319 },
  { name: 'Cirebon', lat: -6.7063, lng: 108.557 }, { name: 'Semarang', lat: -6.9932, lng: 110.4203 }, { name: 'Yogyakarta', lat: -7.7956, lng: 110.3695 },
  { name: 'Surabaya', lat: -7.2575, lng: 112.7521 }, { name: 'Malang', lat: -7.9666, lng: 112.6326 }, { name: 'Denpasar', lat: -8.6705, lng: 115.2126 },
  { name: 'Medan', lat: 3.5952, lng: 98.6722 }, { name: 'Palembang', lat: -2.9761, lng: 104.7754 }, { name: 'Makassar', lat: -5.1477, lng: 119.4327 },
  { name: 'Balikpapan', lat: -1.2379, lng: 116.8529 }, { name: 'Karawang', lat: -6.3227, lng: 107.3376 }, { name: 'Sukabumi', lat: -6.9277, lng: 106.93 },
  { name: 'Tasikmalaya', lat: -7.3506, lng: 108.2172 }, { name: 'Solo', lat: -7.5755, lng: 110.8243 }, { name: 'Batam', lat: 1.0456, lng: 104.0305 },
];
