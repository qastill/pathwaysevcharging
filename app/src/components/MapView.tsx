import { useEffect, useRef, useState, useImperativeHandle, forwardRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { Station, Host, LatLng } from '../types';

export interface MapHandle { flyTo: (p: LatLng, zoom?: number) => void; fitBounds: (b: [number, number, number, number]) => void; getCenter: () => LatLng; getZoom: () => number }
interface Props { stations: Station[]; hosts: Host[]; selectedId?: string | null; onSelect: (kind: 'station' | 'host', id: string) => void; userLoc: LatLng | null; center: LatLng; zoom: number; onMove?: (c: LatLng, z: number) => void; interactive?: boolean; padding?: { bottom?: number; left?: number } }

const STYLE = 'https://tiles.openfreemap.org/styles/liberty';
const RASTER: any = { version: 8, sources: { osm: { type: 'raster', tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'], tileSize: 256, attribution: '© OpenStreetMap' } }, layers: [{ id: 'osm', type: 'raster', source: 'osm' }] };
const COLORS: Record<string, string> = { dc: '#0E7A4A', ac: '#0E9F8A', mitra: '#2563EB', host: '#F59E0B' };

const MapView = forwardRef<MapHandle, Props>(function MapView({ stations, hosts, selectedId, onSelect, userLoc, center, zoom, onMove, interactive = true, padding }, ref) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [ready, setReady] = useState(false);
  const cb = useRef({ onSelect, onMove }); cb.current = { onSelect, onMove };

  useImperativeHandle(ref, () => ({
    flyTo: (p, z) => map.current?.flyTo({ center: [p.lng, p.lat], zoom: z ?? Math.max(map.current.getZoom(), 13), essential: true, padding: padding as any }),
    fitBounds: b => map.current?.fitBounds(b as any, { padding: 60, maxZoom: 13 }),
    getCenter: () => { const c = map.current?.getCenter(); return c ? { lat: c.lat, lng: c.lng } : center; },
    getZoom: () => map.current?.getZoom() ?? zoom,
  }));

  useEffect(() => {
    if (!el.current || map.current) return;
    const m = new maplibregl.Map({ container: el.current, style: STYLE, center: [center.lng, center.lat], zoom, attributionControl: false, interactive, maxZoom: 18, minZoom: 3 });
    m.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right');
    if (interactive) m.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    let fellBack = false;
    m.on('error', (e: any) => {
      // vector style unreachable (offline / blocked) -> fall back to raster OSM tiles
      if (!fellBack && e?.error && /style|Failed to fetch|NetworkError|404|403/i.test(String(e.error.message || e.error))) { fellBack = true; m.setStyle(RASTER); }
    });
    m.on('load', () => setReady(true));
    m.on('style.load', () => setReady(r => !r ? r : r)); // no-op, layers re-added by effect below via styledata
    m.on('moveend', () => { const c = m.getCenter(); cb.current.onMove && cb.current.onMove({ lat: c.lat, lng: c.lng }, m.getZoom()); });
    map.current = m;
    return () => { m.remove(); map.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // (re)build layers whenever style or data changes
  useEffect(() => {
    const m = map.current; if (!m || !ready) return;
    const build = () => {
      if (!m.isStyleLoaded()) return;
      const fc = {
        type: 'FeatureCollection',
        features: [
          ...stations.map(s => ({ type: 'Feature', geometry: { type: 'Point', coordinates: [s.lng, s.lat] }, properties: { id: s.id, kind: 'station', cat: s.operator !== 'PLN' ? 'mitra' : s.type === 'DC' ? 'dc' : 'ac', kw: s.kw, sel: s.id === selectedId ? 1 : 0 } })),
          ...hosts.map(h => ({ type: 'Feature', geometry: { type: 'Point', coordinates: [h.lng, h.lat] }, properties: { id: h.id, kind: 'host', cat: 'host', kw: h.kw, sel: h.id === selectedId ? 1 : 0 } })),
        ],
      } as any;
      const src = m.getSource('pts') as maplibregl.GeoJSONSource | undefined;
      if (src) { src.setData(fc); }
      else {
        m.addSource('pts', { type: 'geojson', data: fc, cluster: true, clusterRadius: 46, clusterMaxZoom: 13 });
        m.addLayer({ id: 'clusters', type: 'circle', source: 'pts', filter: ['has', 'point_count'], paint: { 'circle-color': '#0E7A4A', 'circle-opacity': 0.92, 'circle-radius': ['step', ['get', 'point_count'], 16, 10, 20, 50, 25, 200, 30], 'circle-stroke-width': 3, 'circle-stroke-color': 'rgba(184,245,90,.9)' } });
        m.addLayer({ id: 'cluster-count', type: 'symbol', source: 'pts', filter: ['has', 'point_count'], layout: { 'text-field': ['get', 'point_count_abbreviated'], 'text-size': 12, 'text-font': ['Noto Sans Bold'] }, paint: { 'text-color': '#ffffff' } });
        m.addLayer({ id: 'pt-halo', type: 'circle', source: 'pts', filter: ['all', ['!', ['has', 'point_count']], ['==', ['get', 'sel'], 1]], paint: { 'circle-radius': 18, 'circle-color': ['match', ['get', 'cat'], 'dc', COLORS.dc, 'ac', COLORS.ac, 'mitra', COLORS.mitra, COLORS.host], 'circle-opacity': 0.25 } });
        m.addLayer({ id: 'pt', type: 'circle', source: 'pts', filter: ['!', ['has', 'point_count']], paint: { 'circle-radius': ['case', ['==', ['get', 'sel'], 1], 11, ['>=', ['get', 'kw'], 50], 8, 6.5], 'circle-color': ['match', ['get', 'cat'], 'dc', COLORS.dc, 'ac', COLORS.ac, 'mitra', COLORS.mitra, COLORS.host], 'circle-stroke-width': 2, 'circle-stroke-color': '#ffffff' } });
        m.on('click', 'clusters', e => {
          const f = m.queryRenderedFeatures(e.point, { layers: ['clusters'] })[0]; if (!f) return;
          (m.getSource('pts') as any).getClusterExpansionZoom(f.properties!.cluster_id).then((z: number) => m.easeTo({ center: (f.geometry as any).coordinates, zoom: z + 0.5 }));
        });
        m.on('click', 'pt', e => { const f = e.features?.[0]; if (f) cb.current.onSelect(f.properties!.kind, f.properties!.id); });
        for (const l of ['clusters', 'pt']) { m.on('mouseenter', l, () => (m.getCanvas().style.cursor = 'pointer')); m.on('mouseleave', l, () => (m.getCanvas().style.cursor = '')); }
      }
      // user location
      const ufc = { type: 'FeatureCollection', features: userLoc ? [{ type: 'Feature', geometry: { type: 'Point', coordinates: [userLoc.lng, userLoc.lat] }, properties: {} }] : [] } as any;
      const us = m.getSource('me') as maplibregl.GeoJSONSource | undefined;
      if (us) us.setData(ufc);
      else {
        m.addSource('me', { type: 'geojson', data: ufc });
        m.addLayer({ id: 'me-halo', type: 'circle', source: 'me', paint: { 'circle-radius': 16, 'circle-color': '#2563EB', 'circle-opacity': 0.18 } });
        m.addLayer({ id: 'me', type: 'circle', source: 'me', paint: { 'circle-radius': 7, 'circle-color': '#2563EB', 'circle-stroke-width': 3, 'circle-stroke-color': '#fff' } });
      }
    };
    build();
    m.on('styledata', build);
    return () => { m.off('styledata', build); };
  }, [ready, stations, hosts, selectedId, userLoc]);

  useEffect(() => { const m = map.current; if (m) m.resize(); });

  return <div ref={el} className="mapwrap" />;
});
export default MapView;
