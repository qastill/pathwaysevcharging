export interface Vehicle { id: string; brand: string; model: string; battery: number; plug: 'CCS2' | 'Type 2'; ac: number; dc: number; range: number; kwhKm: number }

// Indonesian-market EVs. battery = usable kWh, ac/dc = max charge power (kW), range = WLTP/NEDC-ish km.
export const VEHICLES: Vehicle[] = [
  { id: 'byd-atto3', brand: 'BYD', model: 'Atto 3', battery: 60.5, plug: 'CCS2', ac: 7, dc: 88, range: 480, kwhKm: 0.16 },
  { id: 'byd-dolphin', brand: 'BYD', model: 'Dolphin', battery: 44.9, plug: 'CCS2', ac: 7, dc: 60, range: 410, kwhKm: 0.14 },
  { id: 'byd-seal', brand: 'BYD', model: 'Seal', battery: 82.5, plug: 'CCS2', ac: 7, dc: 150, range: 650, kwhKm: 0.15 },
  { id: 'byd-m6', brand: 'BYD', model: 'M6', battery: 71.8, plug: 'CCS2', ac: 7, dc: 115, range: 530, kwhKm: 0.17 },
  { id: 'byd-sealion7', brand: 'BYD', model: 'Sealion 7', battery: 82.5, plug: 'CCS2', ac: 11, dc: 150, range: 567, kwhKm: 0.17 },
  { id: 'denza-d9', brand: 'Denza', model: 'D9', battery: 103, plug: 'CCS2', ac: 11, dc: 166, range: 600, kwhKm: 0.2 },
  { id: 'wuling-airev', brand: 'Wuling', model: 'Air ev Long Range', battery: 26.7, plug: 'Type 2', ac: 6.6, dc: 0, range: 300, kwhKm: 0.11 },
  { id: 'wuling-binguo', brand: 'Wuling', model: 'BinguoEV', battery: 37.9, plug: 'CCS2', ac: 6.6, dc: 50, range: 410, kwhKm: 0.12 },
  { id: 'wuling-cloud', brand: 'Wuling', model: 'Cloud EV', battery: 50.6, plug: 'CCS2', ac: 6.6, dc: 50, range: 460, kwhKm: 0.13 },
  { id: 'jaecoo-j6', brand: 'JAECOO', model: 'J6', battery: 69.8, plug: 'CCS2', ac: 6.6, dc: 70, range: 426, kwhKm: 0.18 },
  { id: 'geely-ex5', brand: 'Geely', model: 'EX5', battery: 60.2, plug: 'CCS2', ac: 11, dc: 100, range: 495, kwhKm: 0.15 },
  { id: 'aion-y', brand: 'AION', model: 'Y Plus', battery: 63.2, plug: 'CCS2', ac: 7, dc: 80, range: 490, kwhKm: 0.15 },
  { id: 'chery-omoda', brand: 'Chery', model: 'Omoda E5', battery: 61, plug: 'CCS2', ac: 9.9, dc: 80, range: 430, kwhKm: 0.16 },
  { id: 'chery-j6', brand: 'Chery', model: 'J6', battery: 69.8, plug: 'CCS2', ac: 6.6, dc: 80, range: 426, kwhKm: 0.18 },
  { id: 'hyundai-ioniq5', brand: 'Hyundai', model: 'Ioniq 5', battery: 72.6, plug: 'CCS2', ac: 11, dc: 220, range: 481, kwhKm: 0.17 },
  { id: 'hyundai-kona', brand: 'Hyundai', model: 'Kona Electric', battery: 65.4, plug: 'CCS2', ac: 11, dc: 100, range: 490, kwhKm: 0.15 },
  { id: 'mg-4', brand: 'MG', model: 'MG4 EV', battery: 64, plug: 'CCS2', ac: 7, dc: 140, range: 450, kwhKm: 0.16 },
  { id: 'gwm-ora', brand: 'GWM', model: 'Ora 03', battery: 63, plug: 'CCS2', ac: 11, dc: 80, range: 420, kwhKm: 0.16 },
  { id: 'toyota-bz4x', brand: 'Toyota', model: 'bZ4X', battery: 71.4, plug: 'CCS2', ac: 6.6, dc: 150, range: 500, kwhKm: 0.16 },
  { id: 'neta-v', brand: 'Neta', model: 'V-II', battery: 40.7, plug: 'CCS2', ac: 6.6, dc: 40, range: 401, kwhKm: 0.12 },
  { id: 'vinfast-vfe34', brand: 'VinFast', model: 'VF e34', battery: 42, plug: 'CCS2', ac: 7.4, dc: 55, range: 318, kwhKm: 0.15 },
  { id: 'bmw-ix1', brand: 'BMW', model: 'iX1', battery: 64.7, plug: 'CCS2', ac: 11, dc: 130, range: 440, kwhKm: 0.17 },
  { id: 'mini-cooperse', brand: 'Mini', model: 'Cooper SE', battery: 49.2, plug: 'CCS2', ac: 11, dc: 95, range: 400, kwhKm: 0.14 },
  { id: 'dfsk-gelora', brand: 'DFSK', model: 'Gelora E', battery: 42, plug: 'CCS2', ac: 6.6, dc: 40, range: 300, kwhKm: 0.17 },
  { id: 'byd-atto1', brand: 'BYD', model: 'Atto 1', battery: 38.9, plug: 'CCS2', ac: 6.6, dc: 65, range: 380, kwhKm: 0.12 },
];

export const DEFAULT_VEHICLE = 'byd-atto3';
export const vehicleById = (id: string) => VEHICLES.find(v => v.id === id) || VEHICLES[0];
