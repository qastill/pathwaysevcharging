import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'id.ngecas.app',
  appName: 'Ngecas',
  webDir: 'dist',
  backgroundColor: '#F5F7F4',
  ios: { contentInset: 'always' },
  android: { allowMixedContent: false },
  plugins: {
    StatusBar: { style: 'LIGHT', backgroundColor: '#0E7A4A' },
  },
};

export default config;
