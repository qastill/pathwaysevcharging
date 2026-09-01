import csv, math, json, collections
R=6371000.0
def flo(x):
    try:
        v=float(x)
        return v if v==v else None
    except: return None

# ---------- load gardu ----------
G=[]
with open("analysis/gardu.csv") as f:
    for r in csv.DictReader(f):
        lat,lon=flo(r["LATITUDE"]),flo(r["LONGITUDE"])
        if lat is None or lon is None: continue
        if r["STATUS_KOORDINAT"]!="VALID": continue
        kva=flo(r["KAPASITAS_KVA"]); pb=flo(r["PERSEN_BEBAN"])
        if kva is None or not (5<=kva<=3000): continue
        if pb is None or pb<0 or pb>200: continue
        G.append(dict(kode=r["KODE_GARDU"],nama=r["NAMA_GARDU"],up3=r["UP3"],gi=r["GARDU_INDUK"],
            peny=r["PENYULANG"],kva=kva,pb=pb,pbs=flo(r["PERSEN_BEBAN_SIANG"]),pbm=flo(r["PERSEN_BEBAN_MALAM"]),
            pfasa=flo(r["PERSEN_BEBAN_PUNCAK_FASA"]),kat=r["KATEGORI_BEBAN"],unb=flo(r["UNBALANCE_MAX_PCT"]),
            stunb=r["STATUS_UNBALANCE"],lat=lat,lon=lon,kota=r["KOTA_KAB"],gikode=r["GI_KODE"],
            gimva=flo(r["GI_DAYA_MVA"]),gips=flo(r["GI_PERSEN_SIANG"]),gipm=flo(r["GI_PERSEN_MALAM"]),
            gimatch=r["GI_METODE_MATCH"]))
print("gardu usable:",len(G))

# ---------- spatial index ----------
CELL=0.01
idx=collections.defaultdict(list)
for i,g in enumerate(G): idx[(int(g["lat"]/CELL),int(g["lon"]/CELL))].append(i)
def near(lat,lon,maxm=2000):
    rng=int(maxm/1000/1.11/CELL)+1
    cy,cx=int(lat/CELL),int(lon/CELL); best=None;bd=1e18
    coslat=math.cos(math.radians(lat))
    for dy in range(-rng,rng+1):
        for dx in range(-rng,rng+1):
            for i in idx.get((cy+dy,cx+dx),()):
                g=G[i]
                dl=(g["lat"]-lat)*111320.0; dn=(g["lon"]-lon)*111320.0*coslat
                d=dl*dl+dn*dn
                if d<bd: bd=d;best=i
    if best is None: return None,None
    d=math.sqrt(bd)
    return (best,d) if d<=maxm else (None,d)

# ---------- EV customers ----------
rows=list(csv.reader(open("Data pelanggan EV.txt",encoding="utf-8",errors="replace"),delimiter="\t"))
h=rows[0]; ci={k:i for i,k in enumerate(h)}
EV=[]
for r in rows[1:]:
    if len(r)<len(h): r=r+[""]*(len(h)-len(r))
    lat,lon=flo(r[ci["Lat"]]),flo(r[ci["Long"]])
    if lat is None or lon is None: continue
    if not(-8.0<lat<-5.0 and 105.0<lon<109.5): continue
    EV.append(dict(lat=lat,lon=lon,daya=flo(r[ci["tarif/Daya"]]) or 7700,
        status=r[ci["Status Approval"]].strip(),up3=r[ci["UP3"]].strip(),ulp=r[ci["ULP"]].strip(),
        kab=r[ci["Kabupaten"]].strip(),kec=r[ci["Kecamatan"]].strip(),merk=r[ci["Jenis Kendaraan"]].strip(),
        tgl=r[ci["Tgl Pengajuan"]].strip()))
print("EV geo:",len(EV),"selesai:",sum(1 for e in EV if e["status"]=="Selesai"))

# ---------- SPKLU ----------
SP=[]
for r in csv.DictReader(open("analysis/spklu.csv")):
    lat,lon=flo(r["LATITUDE"]),flo(r["LONGITUDE"])
    if lat is None or lon is None: continue
    if not(-8.0<lat<-5.0 and 105.0<lon<109.5): continue
    kw=r["KW"]; kwv=flo(str(kw).replace("kW","").strip()) or 0
    SP.append(dict(lat=lat,lon=lon,kw=kwv,up3=r["UP3"].strip(),lok=r["LOKASI"].strip(),
        kota=r["KOTA/KAB"].strip(),milik=r["MILIK"].strip(),jenis=r["JENIS Charging"].strip(),
        kon=flo(r["JML KONEKTOR"]) or 0))
print("SPKLU geo:",len(SP))

# ---------- join ----------
for e in EV:
    i,d=near(e["lat"],e["lon"],1000); e["gi_idx"]=i; e["dist"]=d
for s in SP:
    i,d=near(s["lat"],s["lon"],2000); s["gi_idx"]=i; s["dist"]=d
json.dump(dict(nG=len(G)),open("analysis/_tmp.json","w"))

matched_ev=[e for e in EV if e["gi_idx"] is not None]
matched_sp=[s for s in SP if s["gi_idx"] is not None]
print("EV matched<=1km:",len(matched_ev),"| SPKLU matched<=2km:",len(matched_sp))

import pickle
pickle.dump(dict(G=G,EV=EV,SP=SP),open("analysis/joined.pkl","wb"))
