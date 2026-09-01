import pickle,collections,math,json,statistics as st
d=pickle.load(open("analysis/joined.pkl","rb")); G,EV,SP=d["G"],d["EV"],d["SP"]
def pct(a,b): return 100.0*a/b if b else 0.0
mev=[e for e in EV if e["gi_idx"] is not None]; msp=[s for s in SP if s["gi_idx"] is not None]
def hav(a,b,c,d_):
    dl=(c-a)*111320.0; dn=(d_-b)*111320.0*math.cos(math.radians(a)); return math.hypot(dl,dn)

print("="*70); print("I. SPKLU: RASIO DAYA CHARGER TERHADAP GARDU PENYUPLAI")
close=[s for s in msp if s["dist"]<=300]
print(f"  SPKLU dengan gardu <=300 m: {len(close)}")
rat=[]
for s in close:
    g=G[s["gi_idx"]]
    if s["kw"]<=0: continue
    share=100.0*(s["kw"]/0.9)/g["kva"]         # kVA charger / kVA trafo
    post=g["pb"]+share
    rat.append((post,share,g,s))
rat.sort(key=lambda r:-r[0])
print(f"  Median porsi daya charger thd trafo: {st.median(r[1] for r in rat):.1f}% | rata2 {st.mean(r[1] for r in rat):.1f}%")
big=[r for r in rat if r[0]>=100]
print(f"  >>> SPKLU yang, bila ditarik penuh, membuat gardu terdekat >=100%: {len(big)} dari {len(rat)}")
print(f"  {'SPKLU':34s} {'kW':>4s} {'gardu kVA':>9s} {'%now':>5s} {'+%':>6s} {'%post':>6s}")
for post,share,g,s in rat[:15]:
    print(f"  {s['lok'][:34]:34s} {s['kw']:4.0f} {g['kva']:9.0f} {g['pb']:5.1f} {share:6.1f} {post:6.1f}")

print(); print("="*70); print("J. JARAK PELANGGAN EV KE SPKLU TERDEKAT (ketergantungan home charging)")
ds=[]
for e in mev:
    m=min(hav(e["lat"],e["lon"],s["lat"],s["lon"]) for s in SP)
    e["dsp"]=m; ds.append(m)
ds.sort()
print(f"  median {ds[len(ds)//2]/1000:.2f} km | p90 {ds[int(.9*len(ds))]/1000:.2f} km | max {ds[-1]/1000:.1f} km")
for th in (2000,5000,10000):
    print(f"  EV dengan SPKLU dalam {th/1000:.0f} km: {sum(1 for x in ds if x<=th)} ({pct(sum(1 for x in ds if x<=th),len(ds)):.1f}%)")

print(); print("="*70); print("K. MATRIKS KUADRAN KECAMATAN (adopsi EV vs tekanan jaringan)")
# assign gardu to kecamatan via nearest EV? better: aggregate by (kab,kec) of EV, grid stress from their gardu
kec=collections.defaultdict(list)
for e in mev: kec[(e["kab"].split(" - ")[-1],e["kec"].split(" - ")[-1])].append(e)
rows=[]
for k,evs in kec.items():
    gs=[G[e["gi_idx"]] for e in evs]
    stress=st.mean(g["pb"] for g in gs)
    hd=sum(max(0,g["kva"]*(0.8-g["pb"]/100)) for g in {id(g):g for g in gs}.values())/1000
    nsp=sum(1 for s in msp if any(hav(s["lat"],s["lon"],e["lat"],e["lon"])<5000 for e in evs[:40]))
    rows.append((len(evs),stress,hd,nsp,k))
rows.sort(key=lambda r:(-r[0],-r[1]))
print(f"  {'KECAMATAN':22s} {'KAB/KOTA':22s} {'nEV':>4s} {'%beban':>7s} {'headMVA':>8s} {'SPKLU<5km':>9s}")
for n,s_,hd,nsp,k in rows[:22]:
    print(f"  {k[1][:22]:22s} {k[0][:22]:22s} {n:4d} {s_:7.1f} {hd:8.2f} {nsp:9d}")
print("  --- KECAMATAN RISIKO: EV>=10 & %beban gardu >=70% ---")
risk=[r for r in rows if r[0]>=10 and r[1]>=70]
for n,s_,hd,nsp,k in risk: print(f"  {k[1][:22]:22s} {k[0][:22]:22s} {n:4d} {s_:7.1f} {hd:8.2f} {nsp:9d}")
print("  --- KECAMATAN 'EV DESERT' : EV>=15 tapi 0 SPKLU<5km ---")
des=[r for r in rows if r[0]>=15 and r[3]==0]
for n,s_,hd,nsp,k in des: print(f"  {k[1][:22]:22s} {k[0][:22]:22s} {n:4d} {s_:7.1f} {hd:8.2f}")

print(); print("="*70); print("L. HEADROOM vs SKENARIO PERTUMBUHAN EV (Jabar)")
head80=sum(max(0,g["kva"]*(0.8-g["pb"]/100)) for g in G)   # kVA
print(f"  Headroom aman total: {head80/1000:,.0f} MVA")
for cf in (1.0,0.6,0.35):
    cap=head80/(7.7*cf)
    print(f"  Kapasitas tambahan home charger 7.7 kVA @CF={cf}: {cap:,.0f} unit (teoritis, jika tersebar merata)")
print("  Realita: headroom TIDAK bisa dipindah — yang mengikat adalah gardu lokal.")
loc=[]
for g in G:
    h=g["kva"]*(0.8-g["pb"]/100)
    loc.append(max(0,h)/(7.7*0.6))
loc.sort()
print(f"  Gardu yang TIDAK bisa menerima 1 EV pun (@CF0.6): {sum(1 for x in loc if x<1)} ({pct(sum(1 for x in loc if x<1),len(G)):.1f}%)")
print(f"  Gardu bisa >=5 EV: {sum(1 for x in loc if x>=5)} ({pct(sum(1 for x in loc if x>=5),len(G)):.1f}%)")
print(f"  Gardu bisa >=20 EV: {sum(1 for x in loc if x>=20)} ({pct(sum(1 for x in loc if x>=20),len(G)):.1f}%)")
