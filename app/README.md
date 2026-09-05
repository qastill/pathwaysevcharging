# ⚡ Ngecas — cari, pesan, ngecas

Aplikasi pencari & pemesanan charger mobil listrik untuk Indonesia — SPKLU publik (PLN dan swasta)
**plus** charger rumah peer-to-peer (host menyewakan wallbox-nya). Satu basis kode untuk
**web app (PWA)** dan **aplikasi mobile Android/iOS** (Capacitor).

Dibangun di atas data nyata repositori ini:

| Sumber | Dipakai untuk |
|---|---|
| `SPKLU_Indonesia_Lengkap_2026-06-08.xlsx` | 3.212 SPKLU di 34 provinsi: koordinat, daya, status, jumlah charger/konektor, PLN vs non-PLN |
| `Master SPKLU Maret 2026.xlsx` | 636 unit Jawa Barat: merek, AC/DC, konektor, alamat, tahun operasi |
| `Detail Transaksi SPKLU Jawa Barat - Maret 2026.csv` | 101.020 transaksi: jam ramai per stasiun, median durasi & kWh, konektor riil, harga efektif per kWh |
| `Rekap_SPKLU_Jabar_ArcGIS.csv` | utilisasi (hijau/kuning/merah), transaksi & energi per stasiun |
| `Data SPKLU.xlsx` | jenis plug (CCS2/CHAdeMO/Type 2) unit PLN yang disurvei |
| `analysis/price.json` | struktur tarif (energi + PPJ per pemda), asumsi biaya & karbon |
| `Data pelanggan EV.txt` | **hanya sebaran spasial** pemasangan home charging → listing host contoh (lokasi digeser 250–600 m, identitas disamarkan, tanpa nama/HP/VIN) |

## Fitur

- **Peta & pencarian** — MapLibre + clustering, filter AC/DC, konektor, penyedia, daya, harga, lokasi, kompatibilitas mobil; urut terdekat/tercepat/termurah/terpopuler; lokasi GPS.
- **Detail stasiun** — harga/kWh dengan rincian energi + PPJ, konektor & kompatibilitas mobil, **jam ramai dari transaksi nyata**, sesi median, utilisasi, fasilitas, rute Google Maps, ulasan.
- **Estimasi untuk mobil Anda** — kurva pengisian (AC/DC, taper >80 %) dari katalog 25 EV pasar Indonesia.
- **Pemesanan slot** — tanggal, jam (dengan tingkat ramai & ketersediaan), SoC awal/target, rincian biaya, metode bayar.
- **Sesi ngecas langsung** — ring progres, kW, kWh, biaya, ETA (demo dipercepat), lalu layar *Charging complete* + struk + ulasan.
- **Host (P2P)** — kalkulator pendapatan, daftar wallbox (pin peta, daya, harga, jam, fasilitas), permintaan masuk, dashboard pendapatan.
- **Kalkulator & rute** — biaya bulanan SPKLU vs rumah vs bensin, CO₂, charger sepanjang koridor antar-kota.
- **Data & wawasan** — tren nasional, jam puncak, stasiun tersibuk, sebaran provinsi.
- **PWA** — installable, offline-ready (data & tile cache). **ID/EN**.

## Menjalankan

```bash
cd app
npm install
npm run data     # opsional: bangun ulang public/data/*.json dari xlsx/csv di root repo (butuh pandas, openpyxl)
npm run dev      # http://localhost:5173
npm run build    # -> dist/
```

## Mobile (Capacitor)

```bash
npm run build && npx cap sync
npx cap open android   # Android Studio -> Run / Build APK
npx cap open ios       # Xcode (macOS)
```

Folder `android/` dan `ios/` sudah dibuat (`npx cap add`). `appId`: `id.ngecas.app`. Ganti ikon/splash
lewat `npx @capacitor/assets generate` bila perlu.

## Backend (opsional)

Secara bawaan semua pesanan, ulasan, dan listing disimpan di perangkat (`localStorage`) — tidak perlu server.
Untuk mode bersama, jalankan `supabase/schema.sql` di proyek Supabase lalu isi `.env`:

```
VITE_SUPABASE_URL=https://<ref>.supabase.co
VITE_SUPABASE_ANON_KEY=...
```

## Deploy web

Dua cara:

1. **Ikut proyek Vercel dashboard yang sudah ada** — `vercel.json` + `build.sh` di akar repo menyalin
   situs statis ke `public/` dan membangun aplikasi ke `public/ngecas/` (base `/ngecas/`), sehingga
   tersedia di `https://<domain-dashboard>/ngecas/` tanpa proyek baru.
2. **Proyek Vercel terpisah** — *Root Directory* = `app`, framework Vite (auto). Routing memakai hash (`/#/...`) sehingga
tidak butuh rewrite khusus dan berjalan sama di `file://` (Capacitor).

## Struktur

```
app/
├── scripts/build_data.py   pipeline xlsx/csv -> public/data/{stations,hosts,meta}.json
├── public/data/            payload (3.212 stasiun, 380 host contoh, meta tarif & pola jam)
├── src/
│   ├── pages/              Home, Detail, HostDetail, Book, Session, Done, Bookings, Host, HostForm, Profile, Vehicle, Trip, Insights, Onboarding
│   ├── components/         MapView (MapLibre), Cards, Hours, Reviews, TabBar, ui
│   ├── lib/model.ts        jam ramai, ketersediaan slot, kurva pengisian, harga, CO₂
│   ├── vehicles.ts         katalog EV Indonesia
│   ├── i18n.ts · store.ts  teks ID/EN · state (zustand + persist)
├── supabase/schema.sql
├── capacitor.config.ts · android/ · ios/
```

Peta © [OpenFreeMap](https://openfreemap.org) · © OpenStreetMap contributors.
