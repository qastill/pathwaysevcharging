import pandas as pd, re

SRC = "Detail Transaksi SPKLU 202603.xlsx"
OUT = "Detail Transaksi SPKLU Jawa Barat - Maret 2026 (Tagging).xlsx"

def classify(n):
    s=(n or "").upper()
    R=lambda p: re.search(p,s) is not None
    if R(r"REST AREA|RA KM|KM \d+ ?[AB]\b|RUAS|TRAVOY| TOL |TOL$|CIPULARANG|CIPALI|PALIKANCI|JAGORAWI|KANCI|PEJAGAN|PADALARANG - CILEUNYI|JAKARTA - CIKAMPEK|CIKAMPEK - PADALARANG|ALVACHARGE|AMANAH RAHARJO"): return "Rest Area Tol"
    if R(r"MALL|SUMMARECON|LIPPO|PLAZA|Q SQUARE|LIFESTYLE|TRANS STUDIO|PASAR SEGAR|PVJ|PARIS VAN JAVA|CIHAMPELAS|FESTIVAL CITYLINK|\bTSM\b|\bBIP\b|CITYLINK|TRANSMART|TECHNOMART|GALUH MAS|SUPERMARKET|HYPERMART|CARREFOUR|SUPERINDO|GIANT|HERO|LOTTE|RAMAYANA|MATAHARI"): return "Mall / Retail / Supermarket"
    if R(r"HOTEL|ASTON|\bINN\b|RESORT|DORMITORY|GUEST|HOSTEL|HORISON|HARRIS"): return "Hotel / Hospitality"
    if R(r"BYD|ARISTA|CHERY|GEELY|WULING|HYUNDAI|TOYOTA|DEALER|SHOWROOM|MARKETING GALLERY|SALES CENTER|AVANTE|\bAUTO\b|MITSUBISHI|NETA|DFSK|\bMG \b"): return "Dealer / Showroom Mobil"
    if R(r"COFFEE|CAFE|CAFÉ|CAR WASH|RESTO|RESTAURANT|\bKOPI\b|EATERY|FOOD PARK|\bFOOD\b|TERAS|DRUMS|AVENUE|POPI|\bRM \b|WAROENG|WARUNG|CIBIUK|SAMOLO"): return "F&B / Kafe / Leisure Retail"
    if R(r"\bRS |RSUD|RUMAH SAKIT|MEDIKA|HOSPITAL|KLINIK|SILOAM|HERMINA|SENTOSA|ADVENT|AYSHA"): return "Rumah Sakit / Kesehatan"
    if R(r"BALAI KOTA|SEKDA|PEMDA|PEMKOT|PEMKAB|DPRD|DISHUB|DINAS|SAMSAT|KECAMATAN|GEDUNG SATE|POLRES|POLSEK|POLDA|POSPOL|KODIM|KEJAKSAAN|PENGADILAN|BANDARA|AIRPORT|STASIUN|STATION|TERMINAL|KAMPUS|UNIVERSITAS|\bITB\b|UNPAD|SEKOLAH|ALUN-ALUN|ALUN ALUN|MASJID|MESJID|ISTANA"): return "Publik / Pemerintah / Transportasi"
    if R(r"PLN UP3|PLN ULP|PLN UID|PLN UIP|PLN UPT|CSE PLN|\bUP3\b|\bULP\b|\bUPT\b|UPDL|KANWIL|DAYA\+ PLN|DAYA\+ CENTER|DAYA\+ ULP|ICON ?HUB|ICON ?PLUS|\bPOSKO\b|\bUID\b|PLN CGE|MOBILE UID|GARDU INDUK|BISNIS CENTER|PLN 3 |SENTRA KIIC|ASTAKAIA"): return "Kantor / Unit Layanan PLN"
    if R(r"SPBU|PERTAMINA|SHELL| BP |\bVIVO\b"): return "SPBU / Fuel Station"
    if R(r"GEOWISATA|WISATA|PUNCAK|PANTAI|BEACH|CURUG|FLOATING|\bDAM\b|JATILUHUR|GLAMPING|VILLA|SAFARI|GOLF|CAMPSITE|CAMP\b|FOREST|RENGGANIS|OCEAN VIEW|PARADISO|FARM"): return "Wisata / Leisure"
    if R(r"KOTA BARU PARAHYANGAN|\bKBP\b|GRAND DEPOK CITY|GARDENS|BALE PARE|TOWNSHIP|RESIDENCE|\bPERUM\b|CLUSTER|CITRALAND|CITRAGRAN|CITRA |VERONA|HILLS|GRAND TARUMA|MAHATA|FAMILY PARK|PARAHYANGAN|APARTEMEN|APARTMENT|HARVEST CITY|MILLENNIUM CITY|GREENLAND|SAKURA|PANCAR GARDEN|CIANJUR ASRI|GATEWAY|\bKP \b|KAMPUNG"): return "Perumahan / Township"
    if R(r"BTN|BANK|BSPACE|OFFICE|GEDUNG|TOWER|GRHA|GRAHA|KANTOR|TENTH AVENUE|WALKING"): return "Perkantoran / Gedung Komersial"
    return "Lainnya / Campuran"

def tagging(trx):
    if trx > 50: return "Hijau (Utilisasi Tinggi >50 trx)"
    if trx >= 11: return "Kuning (Utilisasi Sedang 11-50 trx)"
    return "Merah (Utilisasi Rendah <10 trx)"

df = pd.read_excel(SRC, sheet_name="Detail Transaksi")
df = df[df['Provinsi'].astype(str).str.upper()=="JAWA BARAT"].copy()

# --- tagging per SPKLU (dihitung dari jumlah transaksi sebulan) ---
trx_count = df.groupby('IdSpklu')['Id Transaksi'].transform('count')
df['Tagging SPKLU'] = trx_count.apply(tagging)
df['Jenis Titik Lokasi'] = df['Nama SPKLU'].apply(classify)

# --- koordinat titik per SPKLU (ArcGIS) ---
coord = pd.read_excel("SPKLU_Indonesia_Lengkap_2026-06-08.xlsx", sheet_name="Master SPKLU Indonesia")
coord['ID SPKLU']=pd.to_numeric(coord['ID SPKLU'],errors='coerce')
coord=coord.dropna(subset=['ID SPKLU']).drop_duplicates('ID SPKLU').set_index(coord['ID SPKLU'].dropna().astype(int).values)
df['_id']=pd.to_numeric(df['IdSpklu'],errors='coerce')
df['Latitude']=df['_id'].map(coord['Latitude'])
df['Longitude']=df['_id'].map(coord['Longitude'])

# --- turunan waktu & durasi ---
df['Tanggal']=pd.to_datetime(df['Tanggal'])
df['Tgl'] = df['Tanggal'].dt.date
df['Jam'] = df['Tanggal'].dt.hour
def dur_min(x):
    try:
        h,m,s=str(x).split(':'); return round(int(h)*60+int(m)+int(s)/60,1)
    except: return None
df['Durasi (menit)']=df['durasi'].apply(dur_min)

for c in ['kwh','rpkwh','rpppj','rpmat','rpadmin','rppakai','%PPJ']:
    df[c]=pd.to_numeric(df[c],errors='coerce')

# --- susun kolom akhir ---
cols=[('No','No'),('Id Transaksi','Id Transaksi'),('Tanggal','Waktu Transaksi'),('Tgl','Tanggal'),
      ('Jam','Jam'),('Periode','Periode'),('IdSpklu','ID SPKLU'),('Nama SPKLU','Nama SPKLU'),
      ('Tagging SPKLU','Tagging SPKLU'),('Jenis Titik Lokasi','Jenis Titik Lokasi'),
      ('UP3','UP3'),('ULP','ULP'),('Pemda/Pemkot','Kota/Kabupaten'),('Provinsi','Provinsi'),
      ('Latitude','Latitude'),('Longitude','Longitude'),
      ('EV Charger','EV Charger'),('Id Charger','Id Charger'),('Daya Charger','Daya Charger'),
      ('Connector','Connector'),('Id Connector','Id Connector'),
      ('kwh','Energi (kWh)'),('durasi','Durasi'),('Durasi (menit)','Durasi (menit)'),
      ('rpkwh','Rp per kWh'),('rpppj','Rp PPJ'),('rpmat','Rp Material'),('rpadmin','Rp Admin'),
      ('rppakai','Total Bayar (Rp)'),('payment','Metode Bayar'),('%PPJ','% PPJ')]
df=df.sort_values('Tanggal').reset_index(drop=True)
df['No']=range(1,len(df)+1)
out=df[[c for c,_ in cols]].copy()
out.columns=[n for _,n in cols]

# --- tulis dgn xlsxwriter (efisien utk 100k+ baris) ---
with pd.ExcelWriter(OUT, engine='xlsxwriter', datetime_format='yyyy-mm-dd hh:mm:ss') as xw:
    out.to_excel(xw, sheet_name='Detail Transaksi', index=False, startrow=0)
    wb=xw.book; ws=xw.sheets['Detail Transaksi']
    hdr=wb.add_format({'bold':True,'bg_color':'#1F4E79','font_color':'white','border':1,
                       'align':'center','valign':'vcenter','text_wrap':True})
    f_num=wb.add_format({'num_format':'#,##0.00'}); f_int=wb.add_format({'num_format':'#,##0'})
    f_lat=wb.add_format({'num_format':'0.000000'}); f_dt=wb.add_format({'num_format':'yyyy-mm-dd hh:mm:ss'})
    f_date=wb.add_format({'num_format':'yyyy-mm-dd'})
    for i,name in enumerate(out.columns): ws.write(0,i,name,hdr)
    W={'No':7,'Id Transaksi':12,'Waktu Transaksi':19,'Tanggal':12,'Jam':6,'Periode':9,'ID SPKLU':9,
       'Nama SPKLU':44,'Tagging SPKLU':28,'Jenis Titik Lokasi':28,'UP3':16,'ULP':18,'Kota/Kabupaten':18,
       'Provinsi':12,'Latitude':12,'Longitude':12,'EV Charger':22,'Id Charger':18,'Daya Charger':12,
       'Connector':22,'Id Connector':11,'Energi (kWh)':12,'Durasi':10,'Durasi (menit)':13,'Rp per kWh':11,
       'Rp PPJ':10,'Rp Material':11,'Rp Admin':10,'Total Bayar (Rp)':14,'Metode Bayar':14,'% PPJ':8}
    fmt={'Energi (kWh)':f_num,'Durasi (menit)':f_num,'Latitude':f_lat,'Longitude':f_lat,
         'Waktu Transaksi':f_dt,'Tanggal':f_date,'Rp per kWh':f_int,'Rp PPJ':f_int,'Rp Material':f_int,
         'Rp Admin':f_int,'Total Bayar (Rp)':f_int,'ID SPKLU':f_int,'Jam':f_int,'% PPJ':f_num}
    for i,name in enumerate(out.columns):
        ws.set_column(i,i,W.get(name,14),fmt.get(name))
    ws.freeze_panes(1,0)
    ws.autofilter(0,0,len(out),len(out.columns)-1)

print("File:", OUT)
print("Baris transaksi:", f"{len(out):,}")
print("SPKLU unik:", out['ID SPKLU'].nunique(), "| berkoordinat:", out['Latitude'].notna().sum(), "baris")
print("Rentang waktu:", out['Waktu Transaksi'].min(), "→", out['Waktu Transaksi'].max())
print("Kolom:", list(out.columns))
print("\nContoh 3 baris:")
print(out.head(3).to_string(index=False))
