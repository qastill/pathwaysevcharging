import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

const base = process.env.BASE || '/';

export default defineConfig({
  base,
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icons/icon.svg', 'icons/icon-192.png', 'icons/icon-512.png'],
      manifest: {
        name: 'Ngecas — Cari & pesan charger mobil listrik',
        short_name: 'Ngecas',
        description: 'Cari, pesan, dan ngecas mobil listrik di 3.200+ SPKLU dan charger rumah di seluruh Indonesia.',
        theme_color: '#0E7A4A',
        background_color: '#F5F7F4',
        display: 'standalone',
        orientation: 'portrait',
        start_url: base,
        scope: base,
        lang: 'id',
        icons: [
          { src: base + 'icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: base + 'icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: base + 'icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        maximumFileSizeToCacheInBytes: 6 * 1024 * 1024,
        globPatterns: ['**/*.{js,css,html,svg,png,json}'],
        runtimeCaching: [
          { urlPattern: /^https:\/\/tiles\.openfreemap\.org\//, handler: 'CacheFirst', options: { cacheName: 'map-tiles', expiration: { maxEntries: 600, maxAgeSeconds: 7 * 24 * 3600 } } },
          { urlPattern: /^https:\/\/fonts\.(googleapis|gstatic)\.com\//, handler: 'StaleWhileRevalidate', options: { cacheName: 'fonts' } },
        ],
      },
    }),
  ],
  build: { chunkSizeWarningLimit: 1500 },
  server: { port: 5173, host: true },
});
