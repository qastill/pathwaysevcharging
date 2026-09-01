import pickle,collections,math,json,statistics as st
d=pickle.load(open("analysis/joined.pkl","rb")); G,EV,SP=d["G"],d["EV"],d["SP"]
def pct(a,b): return 100.0*a/b if b else 0.0
PF=0.85  # kVA->kW proxy for reporting

print("="*70); print("A. BASELINE KONDISI JARINGAN DISTRIBUSI (gardu valid koordinat)")
cat=collections.Counter(g["kat"] for g in G)
for k,v in cat.most_common(): print(f"  {k:22s} {v:6d}  {pct(v,len(G)):5.1f}%")
tot_kva=sum(g["kva"] for g in G)
head=sum(max(0,g["kva"]*(1-g["pb"]/100)) for g in G)
print(f"  Total kapasitas terpasang : {tot_kva/1000:,.1f} MVA")
print(f"  Headroom teoritis (100%)  : {head/1000:,.1f} MVA ({pct(head,tot_kva):.1f}%)")
head80=sum(max(0,g["kva"]*(0.80-g["pb"]/100)) for g in G)
print(f"  Headroom aman (batas 80%) : {head80/1000:,.1f} MVA")
print(f"  Median %beban: {st.median(g['pb'] for g in G):.1f} | mean {st.mean(g['pb'] for g in G):.1f}")
unb=[g for g in G if g["stunb"] and g["stunb"].startswith("Prioritas")]
print(f"  Gardu unbalance Prioritas 1/2: {len(unb)} ({pct(len(unb),len(G)):.1f}%)")

print(); print("="*70); print("B. EV RUMAH (home charging) vs GARDU TERDEKAT")
mev=[e for e in EV if e["gi_idx"] is not None]
sel=[e for e in mev if e["status"]=="Selesai"]
c=collections.Counter(G[e["gi_idx"]]["kat"] for e in mev)
print(f"  {len(mev)} pelanggan EV ter-join (<=1 km). Kategori gardu penyuplai:")
for k,v in c.most_common(): print(f"    {k:22s} {v:5d}  {pct(v,len(mev)):5.1f}%")
risk=[e for e in mev if G[e["gi_idx"]]["pb"]>=80]
print(f"  >>> EV bertumpu pada gardu WASPADA/OVERLOAD (>=80%): {len(risk)} ({pct(len(risk),len(mev)):.1f}%)")
print(f"  Rata-rata %beban gardu penyuplai EV : {st.mean(G[e['gi_idx']]['pb'] for e in mev):.1f}%")
print(f"  Rata-rata %beban SELURUH gardu Jabar: {st.mean(g['pb'] for g in G):.1f}%")
# malam vs siang -> EV charging is a night load
pm=[G[e["gi_idx"]]["pbm"] for e in mev if G[e["gi_idx"]]["pbm"] is not None]
ps=[G[e["gi_idx"]]["pbs"] for e in mev if G[e["gi_idx"]]["pbs"] is not None]
print(f"  Gardu penyuplai EV: beban siang {st.mean(ps):.1f}% | beban MALAM {st.mean(pm):.1f}%  <-- jam charging rumah")
allm=[g["pbm"] for g in G if g["pbm"] is not None]
print(f"  Semua gardu Jabar : beban malam rata2 {st.mean(allm):.1f}%")

print(); print("="*70); print("C. DAMPAK BEBAN TAMBAHAN EV PER GARDU (clustering)")
per=collections.defaultdict(list)
for e in mev: per[e["gi_idx"]].append(e)
print(f"  Gardu terdampak: {len(per)} dari {len(G)} ({pct(len(per),len(G)):.2f}%)")
cnt=collections.Counter(len(v) for v in per.values())
print("  Distribusi jumlah EV per gardu:", dict(sorted(cnt.items())))
def post(gidx,evs,cf):
    g=G[gidx]; add=sum(e["daya"] for e in evs)/1000.0*cf   # kVA
    base=g["kva"]*g["pb"]/100.0
    return (base+add)/g["kva"]*100.0
for cf,lab in [(1.0,"CF=1.0 (worst case, semua nyala bersamaan)"),(0.6,"CF=0.6 (realistis malam)"),(0.35,"CF=0.35 (smart/terjadwal)")]:
    newov=0; newwas=0; already=0
    for gi,evs in per.items():
        g=G[gi]; p=post(gi,evs,cf)
        if g["pb"]>=100: already+=1
        elif p>=100: newov+=1
        elif g["pb"]<80<=p: newwas+=1
    print(f"  {lab}")
    print(f"     gardu SUDAH overload: {already} | JADI overload krn EV: {newov} | naik ke waspada: {newwas}")

print(); print("="*70); print("D. TOP GARDU PALING TERTEKAN OLEH EV (CF=0.6)")
sc=[]
for gi,evs in per.items():
    g=G[gi]; p=post(gi,evs,0.6)
    sc.append((p,g["pb"],len(evs),gi))
sc.sort(reverse=True)
print(f"  {'GARDU':10s} {'UP3':16s} {'kVA':>6s} {'%now':>6s} {'%post':>6s} {'nEV':>4s}  PENYULANG / GI")
for p,pb,n,gi in sc[:20]:
    g=G[gi]
    print(f"  {g['nama'][:10]:10s} {g['up3'].replace('UP3 ','')[:16]:16s} {g['kva']:6.0f} {pb:6.1f} {p:6.1f} {n:4d}  {g['peny'][:16]:16s} / {g['gi'][:12]}")

print(); print("="*70); print("E. SPKLU vs GARDU / GI")
msp=[s for s in SP if s["gi_idx"] is not None]
c=collections.Counter(G[s["gi_idx"]]["kat"] for s in msp)
for k,v in c.most_common(): print(f"    {k:22s} {v:5d}  {pct(v,len(msp)):5.1f}%")
print(f"  Rata-rata %beban gardu di sekitar SPKLU: {st.mean(G[s['gi_idx']]['pb'] for s in msp):.1f}%")
gis=[G[s["gi_idx"]] for s in msp if G[s["gi_idx"]]["gips"] is not None]
print(f"  Rata-rata %beban GI pemasok SPKLU: siang {st.mean(g['gips'] for g in gis):.1f}% | malam {st.mean(g['gipm'] for g in gis):.1f}%")
crit=[(s,G[s["gi_idx"]]) for s in msp if (G[s["gi_idx"]]["gips"] or 0)>=80 or (G[s["gi_idx"]]["gipm"] or 0)>=80]
print(f"  >>> SPKLU pada GI berbeban >=80%: {len(crit)} ({pct(len(crit),len(msp)):.1f}%)")

print(); print("="*70); print("F. GARDU INDUK: EV/SPKLU vs pembebanan GI")
gi_ev=collections.Counter(); gi_sp=collections.Counter(); gi_kw=collections.Counter(); gi_info={}
for e in mev:
    g=G[e["gi_idx"]]
    if g["gikode"]: gi_ev[g["gikode"]]+=1; gi_info[g["gikode"]]=g
for s in msp:
    g=G[s["gi_idx"]]
    if g["gikode"]: gi_sp[g["gikode"]]+=1; gi_kw[g["gikode"]]+=s["kw"]; gi_info.setdefault(g["gikode"],g)
rowsF=[]
for k,g in gi_info.items():
    if g["gips"] is None: continue
    rowsF.append((max(g["gips"],g["gipm"]),g["gips"],g["gipm"],g["gimva"],gi_ev[k],gi_sp[k],gi_kw[k],k,g["gi"],g["up3"]))
rowsF.sort(reverse=True)
hot=[r for r in rowsF if r[0]>=80 and (r[4]+r[5])>0]
print(f"  GI ter-join: {len(rowsF)} | GI beban>=80% yg sudah menanggung EV/SPKLU: {len(hot)}")
print(f"  {'GI':14s} {'MVA':>5s} {'%sng':>5s} {'%mlm':>5s} {'nEV':>4s} {'nSP':>4s} {'kW_SP':>7s}  UP3")
for r in hot[:18]:
    print(f"  {r[8][:14]:14s} {r[3] or 0:5.0f} {r[1]:5.1f} {r[2]:5.1f} {r[4]:4d} {r[5]:4d} {r[6]:7.0f}  {r[9].replace('UP3 ','')}")
print("  --- GI dengan HEADROOM besar (<50%) namun EV/SPKLU minim (peluang ekspansi) ---")
opp=[r for r in rowsF if r[0]<50 and (r[5]<=1)]
opp.sort(key=lambda r:(r[0],-(r[3] or 0)))
for r in opp[:15]:
    print(f"  {r[8][:14]:14s} {r[3] or 0:5.0f} {r[1]:5.1f} {r[2]:5.1f} {r[4]:4d} {r[5]:4d} {r[6]:7.0f}  {r[9].replace('UP3 ','')}")

print(); print("="*70); print("G. PENYULANG (feeder) DENGAN KONSENTRASI EV TERTINGGI")
pf=collections.Counter(); pfg={}
for e in mev:
    g=G[e["gi_idx"]]; k=(g["up3"],g["peny"])
    if g["peny"]: pf[k]+=1; pfg.setdefault(k,[]).append(g)
outG=[]
for k,n in pf.most_common(15):
    gs=pfg[k]; outG.append((k,n,st.mean(x["pb"] for x in gs),len(gs)))
print(f"  {'PENYULANG':20s} {'UP3':14s} {'nEV':>4s} {'%beban gardu':>13s}")
for (up3,p),n,mb,ng in outG:
    print(f"  {p[:20]:20s} {up3.replace('UP3 ','')[:14]:14s} {n:4d} {mb:12.1f}%")

print(); print("="*70); print("H. MATRIKS UP3: ADOPSI EV vs KESEHATAN JARINGAN")
u_g=collections.defaultdict(list); u_ev=collections.Counter(); u_sp=collections.Counter()
for g in G: u_g[g["up3"]].append(g)
for e in mev: u_ev[G[e["gi_idx"]]["up3"]]+=1
for s in msp: u_sp[G[s["gi_idx"]]["up3"]]+=1
print(f"  {'UP3':16s} {'nGardu':>6s} {'%OL':>5s} {'%>=80':>6s} {'medBeban':>8s} {'headMVA':>8s} {'nEV':>5s} {'EV/1k gardu':>11s} {'nSPKLU':>6s}")
H=[]
for u,gs in sorted(u_g.items()):
    if not u.strip(): continue
    ol=sum(1 for g in gs if g["pb"]>=100); w80=sum(1 for g in gs if g["pb"]>=80)
    hd=sum(max(0,g["kva"]*(0.8-g["pb"]/100)) for g in gs)/1000
    H.append(dict(up3=u,n=len(gs),ol=pct(ol,len(gs)),w80=pct(w80,len(gs)),med=st.median(g["pb"] for g in gs),
                  head=hd,ev=u_ev[u],evr=1000*u_ev[u]/len(gs),sp=u_sp[u]))
for r in sorted(H,key=lambda x:-x["evr"]):
    print(f"  {r['up3'].replace('UP3 ',''):16s} {r['n']:6d} {r['ol']:5.1f} {r['w80']:6.1f} {r['med']:8.1f} {r['head']:8.1f} {r['ev']:5d} {r['evr']:11.1f} {r['sp']:6d}")
json.dump(H,open("analysis/up3.json","w"))
pickle.dump(dict(per=per,rowsF=rowsF,sc=sc[:60]),open("analysis/res.pkl","wb"))
