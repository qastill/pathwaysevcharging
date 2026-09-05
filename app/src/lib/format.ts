export const rp = (n: number, opts: { compact?: boolean } = {}) => {
  if (opts.compact) {
    if (Math.abs(n) >= 1e9) return 'Rp ' + (n / 1e9).toFixed(1).replace('.', ',') + ' M';
    if (Math.abs(n) >= 1e6) return 'Rp ' + (n / 1e6).toFixed(1).replace('.', ',') + ' jt';
    if (Math.abs(n) >= 1e3) return 'Rp ' + Math.round(n / 1e3) + ' rb';
  }
  return 'Rp ' + Math.round(n).toLocaleString('id-ID');
};
export const num = (n: number, d = 0) => n.toLocaleString('id-ID', { maximumFractionDigits: d, minimumFractionDigits: d });
export const km = (m: number) => (m < 1000 ? Math.round(m) + ' m' : (m / 1000).toFixed(m < 10000 ? 1 : 0).replace('.', ',') + ' km');
export const mins = (m: number) => {
  m = Math.round(m); if (m < 60) return m + ' mnt';
  const h = Math.floor(m / 60), r = m % 60; return r ? `${h} j ${r} mnt` : `${h} jam`;
};
export const pad = (n: number) => String(n).padStart(2, '0');
export const hhmm = (d: Date) => pad(d.getHours()) + ':' + pad(d.getMinutes());
export const isoDate = (d: Date) => d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
export const dateLabel = (iso: string, lang: string) => {
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString(lang === 'en' ? 'en-GB' : 'id-ID', { weekday: 'short', day: 'numeric', month: 'short' });
};
export const longDate = (ts: number, lang: string) => new Date(ts).toLocaleString(lang === 'en' ? 'en-GB' : 'id-ID', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
export const uid = () => Math.random().toString(36).slice(2, 8).toUpperCase() + Date.now().toString(36).slice(-3).toUpperCase();
export const code = () => 'NG' + Math.floor(1000 + Math.random() * 9000) + String.fromCharCode(65 + Math.floor(Math.random() * 26));
export const titleCase = (s: string) => s.toLowerCase().replace(/(^|\s|\(|-|\/)([a-z])/g, (m, p, c) => p + c.toUpperCase()).replace(/\bPln\b/g, 'PLN').replace(/\bSpklu\b/g, 'SPKLU').replace(/\bKm\b/g, 'KM').replace(/\bUp3\b/g, 'UP3').replace(/\bUlp\b/g, 'ULP').replace(/\bUid\b/g, 'UID').replace(/\bByd\b/g, 'BYD').replace(/\bMg\b/g, 'MG').replace(/\bKw\b/gi, 'kW').replace(/\bBsd\b/g, 'BSD').replace(/\bPik\b/g, 'PIK').replace(/\bDc\b/g, 'DC').replace(/\bAc\b/g, 'AC').replace(/\bRs\b/g, 'RS').replace(/\bRsud\b/g, 'RSUD').replace(/\bSpbu\b/g, 'SPBU').replace(/\bDki\b/g, 'DKI');
export const hash = (s: string) => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0) / 4294967295; };
