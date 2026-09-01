"""Analisis harga & karbon dari transaksi SPKLU nyata (Maret 2026)."""
import csv, json, collections, statistics as st, datetime, math

def f(x):
    try:
        v=float(x); return v if v==v else 0.0
    except: return 0.0

rows=[]
for r in csv.DictReader(open("analysis/trx.csv")):
    kwh=f(r["kwh"])
    if kwh<=0: continue
    rows.append(dict(
        t=r["Tanggal"], up3=r["UP3"].strip(), pemda=r["Pemda/Pemkot"].strip(),
        spklu=r["Nama SPKLU"].strip(), daya=r["Daya Charger"].strip(),
        kwh=kwh, energi=f(r["rpkwh"]), ppj=f(r["rpppj"]), mat=f(r["rpmat"]),
        adm=f(r["rpadmin"]), total=f(r["rppakai"]), pay=r["payment"].strip(),
        dur=r["durasi"].strip()))
print("transaksi valid:",len(rows))

tot_kwh=sum(r["kwh"] for r in rows); tot_rp=sum(r["total"] for r in rows)
tot_en=sum(r["energi"] for r in rows); tot_ppj=sum(r["ppj"] for r in rows)
tot_adm=sum(r["adm"] for r in rows); tot_mat=sum(r["mat"] for r in rows)
print(f"\n=== A. STRUKTUR HARGA (Maret 2026, Jawa Barat)")
print(f"  Energi terjual      : {tot_kwh:>14,.0f} kWh")
print(f"  Nilai transaksi     : Rp {tot_rp:>12,.0f}")
print(f"  Tarif all-in        : Rp {tot_rp/tot_kwh:>12,.0f} /kWh")
print(f"  Komponen energi     : Rp {tot_en/tot_kwh:>12,.0f} /kWh  ({100*tot_en/tot_rp:.1f}% dari tagihan)")
print(f"  Komponen PPJ        : Rp {tot_ppj/tot_kwh:>12,.0f} /kWh  ({100*tot_ppj/tot_rp:.1f}%)")
print(f"  Admin + materai     : Rp {(tot_adm+tot_mat)/tot_kwh:>12,.0f} /kWh  ({100*(tot_adm+tot_mat)/tot_rp:.1f}%)")

# --- PPJ per pemda: pajak daerah membuat harga kWh berbeda antarkota ---
print("\n=== B. PPJ PER PEMDA — pajak daerah yang membuat harga tidak seragam")
pe=collections.defaultdict(lambda: dict(kwh=0.0,en=0.0,ppj=0.0,tot=0.0,n=0))
for r in rows:
    d=pe[r["pemda"]]; d["kwh"]+=r["kwh"]; d["en"]+=r["energi"]; d["ppj"]+=r["ppj"]; d["tot"]+=r["total"]; d["n"]+=1
P=[]
for k,d in pe.items():
    if d["n"]<200: continue
    P.append(dict(pemda=k, n=d["n"], kwh=d["kwh"], rate=100*d["ppj"]/d["en"] if d["en"] else 0,
                  allin=d["tot"]/d["kwh"], energi=d["en"]/d["kwh"]))
P.sort(key=lambda x:-x["rate"])
print(f"  {'PEMDA':26s} {'trx':>6s} {'PPJ%':>6s} {'Rp/kWh energi':>14s} {'Rp/kWh all-in':>14s}")
for x in P: print(f"  {x['pemda'][:26]:26s} {x['n']:6,} {x['rate']:6.2f} {x['energi']:14,.0f} {x['allin']:14,.0f}")
sp=max(P,key=lambda x:x["allin"])["allin"]-min(P,key=lambda x:x["allin"])["allin"]
print(f"  >>> Selisih harga all-in termahal vs termurah: Rp {sp:,.0f}/kWh ({100*sp/min(P,key=lambda x:x['allin'])['allin']:.1f}%)")

# --- per kelas daya charger ---
print("\n=== C. HARGA PER KELAS DAYA CHARGER")
dc=collections.defaultdict(lambda: dict(kwh=0.0,tot=0.0,n=0,dur=[]))
def kw(s):
    try: return float(str(s).lower().replace('kw','').strip())
    except: return None
for r in rows:
    k=kw(r["daya"])
    if k is None: continue
    b='AC ≤22 kW' if k<=22 else '25–49 kW' if k<50 else '50–99 kW' if k<100 else '100–149 kW' if k<150 else '≥150 kW'
    d=dc[b]; d["kwh"]+=r["kwh"]; d["tot"]+=r["total"]; d["n"]+=1
order=['AC ≤22 kW','25–49 kW','50–99 kW','100–149 kW','≥150 kW']
print(f"  {'KELAS':12s} {'trx':>7s} {'kWh':>12s} {'kWh/sesi':>9s} {'Rp/kWh':>8s}")
for b in order:
    if b not in dc: continue
    d=dc[b]; print(f"  {b:12s} {d['n']:7,} {d['kwh']:12,.0f} {d['kwh']/d['n']:9.1f} {d['tot']/d['kwh']:8,.0f}")

# --- pola jam: kapan orang mengisi & berapa nilainya ---
print("\n=== D. POLA JAM (volume & nilai)")
hr=collections.defaultdict(lambda: dict(kwh=0.0,tot=0.0,n=0))
for r in rows:
    try: h=datetime.datetime.fromisoformat(r["t"].split('.')[0]).hour
    except: continue
    d=hr[h]; d["kwh"]+=r["kwh"]; d["tot"]+=r["total"]; d["n"]+=1
peak=sorted(hr.items(), key=lambda x:-x[1]["kwh"])[:5]
print("  Jam puncak kWh:", ", ".join(f"{h:02d}:00 ({d['kwh']/1000:.0f} MWh)" for h,d in peak))
night=sum(d["kwh"] for h,d in hr.items() if h>=22 or h<5)
print(f"  Porsi kWh 22:00–05:00 (jendela tarif malam): {100*night/tot_kwh:.1f}%")

# --- karbon & biaya per km ---
C=json.load(open("analysis/carbon.json"))
EF=C["jamali"]["ef_kg_per_kwh"]; EFW=C["jamali_west"]["ef_kg_per_kwh"]
KWH_KM=0.17          # asumsi konsumsi EV, kWh/km
ICE_KMPL=11.0        # asumsi konsumsi mobil bensin sekelas, km/liter
BBM=12500.0          # asumsi harga bensin, Rp/liter
ICE_GCO2_KM=190.0    # asumsi emisi tank-to-wheel mobil bensin, gCO2/km
TARIF_RUMAH=1699.53  # asumsi tarif rumah tangga nonsubsidi R-1 >=3.500 VA, Rp/kWh

allin=tot_rp/tot_kwh
print("\n=== E. KARBON & BIAYA PER 100 KM")
print(f"  Faktor emisi Jamali (turunan)      : {EF} kgCO2/kWh")
print(f"  Faktor emisi Jawa bagian barat     : {EFW} kgCO2/kWh")
print(f"  Emisi EV per km (Jamali)           : {EF*KWH_KM*1000:.0f} gCO2/km")
print(f"  Emisi mobil bensin (asumsi)        : {ICE_GCO2_KM:.0f} gCO2/km")
red=100*(1-EF*KWH_KM*1000/ICE_GCO2_KM)
print(f"  >>> Penurunan emisi EV vs bensin   : {red:.1f}%")
ev_sp=allin*KWH_KM*100; ev_hm=TARIF_RUMAH*KWH_KM*100; ice=BBM/ICE_KMPL*100
print(f"  Biaya 100 km — SPKLU               : Rp {ev_sp:,.0f}")
print(f"  Biaya 100 km — isi rumah           : Rp {ev_hm:,.0f}  (hemat {100*(1-ev_hm/ev_sp):.0f}% vs SPKLU)")
print(f"  Biaya 100 km — bensin (asumsi)     : Rp {ice:,.0f}")
be=allin*KWH_KM*ICE_KMPL
print(f"  >>> Harga bensin impas vs SPKLU    : Rp {be:,.0f}/liter (di bawah ini, bensin lebih murah)")
be2=TARIF_RUMAH*KWH_KM*ICE_KMPL
print(f"  >>> Harga bensin impas vs isi rumah: Rp {be2:,.0f}/liter")

# emisi total & pendapatan
print("\n=== F. JEJAK KARBON PENJUALAN SPKLU MARET 2026")
tco2=tot_kwh*EF/1000
print(f"  Emisi tak langsung (scope-2) dari {tot_kwh:,.0f} kWh: {tco2:,.0f} tCO2")
km=tot_kwh/KWH_KM
print(f"  Setara jarak tempuh                 : {km:,.0f} km")
print(f"  Emisi bila jarak itu ditempuh bensin : {km*ICE_GCO2_KM/1e6:,.0f} tCO2")
print(f"  >>> Emisi yang dihindari (bulan itu) : {km*ICE_GCO2_KM/1e6-tco2:,.0f} tCO2")

out=dict(
  price=dict(kwh=tot_kwh, rp=tot_rp, allin=allin, energi=tot_en/tot_kwh,
             ppj=tot_ppj/tot_kwh, adm=(tot_adm+tot_mat)/tot_kwh,
             share_energi=100*tot_en/tot_rp, share_ppj=100*tot_ppj/tot_rp,
             share_adm=100*(tot_adm+tot_mat)/tot_rp, n=len(rows)),
  pemda=P,
  tiers=[dict(tier=b, n=dc[b]["n"], kwh=dc[b]["kwh"], per=dc[b]["kwh"]/dc[b]["n"], rp=dc[b]["tot"]/dc[b]["kwh"]) for b in order if b in dc],
  hours=[dict(h=h, kwh=hr[h]["kwh"], n=hr[h]["n"], rp=hr[h]["tot"]/hr[h]["kwh"] if hr[h]["kwh"] else 0) for h in sorted(hr)],
  night_share=100*night/tot_kwh,
  assume=dict(kwh_km=KWH_KM, ice_kmpl=ICE_KMPL, bbm=BBM, ice_g=ICE_GCO2_KM, tarif_rumah=TARIF_RUMAH),
  carbon=dict(ef_jamali=EF, ef_west=EFW, ev_g_km=EF*KWH_KM*1000, reduction=red,
              tco2=tco2, km=km, avoided=km*ICE_GCO2_KM/1e6-tco2),
  cost=dict(spklu100=ev_sp, home100=ev_hm, ice100=ice, be_spklu=be, be_home=be2),
)
json.dump(out, open("analysis/price.json","w"), separators=(",",":"))
print("\nanalysis/price.json ditulis")
