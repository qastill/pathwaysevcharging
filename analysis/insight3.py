import pickle,collections,math,json,statistics as st
d=pickle.load(open("analysis/joined.pkl","rb")); G,EV,SP=d["G"],d["EV"],d["SP"]
def pct(a,b): return 100.0*a/b if b else 0.0
mev=[e for e in EV if e["gi_idx"] is not None]; msp=[s for s in SP if s["gi_idx"] is not None]
# dedupe SPKLU into locations
loc=collections.defaultdict(list)
for s in msp: loc[(round(s["lat"],5),round(s["lon"],5))].append(s)
LOC=[]
for k,v in loc.items():
    LOC.append(dict(lat=k[0],lon=k[1],kw=sum(x["kw"] for x in v),n=len(v),
        lok=v[0]["lok"],up3=v[0]["up3"],gi_idx=v[0]["gi_idx"],dist=v[0]["dist"],milik=v[0]["milik"]))
print("SPKLU lokasi unik:",len(LOC),"| total kW terpasang:",f"{sum(l['kw'] for l in LOC):,.0f}")

print(); print("="*70); print("M. BEBAN SPKLU TERHADAP PENYULANG (feeder) — agregat per penyulang")
pf=collections.defaultdict(lambda: dict(kw=0,n=0,ev=0,gs=[]))
for l in LOC:
    g=G[l["gi_idx"]]
    if g["peny"]: k=(g["up3"],g["peny"],g["gi"]); pf[k]["kw"]+=l["kw"]; pf[k]["n"]+=1
for e in mev:
    g=G[e["gi_idx"]]
    if g["peny"]: pf[(g["up3"],g["peny"],g["gi"])]["ev"]+=1
for g in G:
    if g["peny"] and (g["up3"],g["peny"],g["gi"]) in pf: pf[(g["up3"],g["peny"],g["gi"])]["gs"].append(g)
rows=[]
for k,v in pf.items():
    if not v["gs"]: continue
    kva=sum(x["kva"] for x in v["gs"]); load=sum(x["kva"]*x["pb"]/100 for x in v["gs"])
    evkw=v["ev"]*7.7*0.6; spkw=v["kw"]/0.9
    rows.append(dict(up3=k[0],peny=k[1],gi=k[2],ntr=len(v["gs"]),kva=kva,pb=pct(load,kva),
        nsp=v["n"],spkva=spkw,nev=v["ev"],evkva=evkw,
        evshare=pct(spkw+evkw,kva),post=pct(load+spkw+evkw,kva)))
rows.sort(key=lambda r:-r["evshare"])
print(f"  {'PENYULANG':17s} {'UP3':13s} {'nTr':>3s} {'kVA':>7s} {'%now':>5s} {'nSP':>3s} {'kVA_SP':>7s} {'nEV':>4s} {'EVshare%':>8s} {'%post':>6s}")
for r in rows[:20]:
    print(f"  {r['peny'][:17]:17s} {r['up3'].replace('UP3 ','')[:13]:13s} {r['ntr']:3d} {r['kva']:7.0f} {r['pb']:5.1f} {r['nsp']:3d} {r['spkva']:7.0f} {r['nev']:4d} {r['evshare']:8.1f} {r['post']:6.1f}")
print(f"  Penyulang dgn beban EV+SPKLU >20% kapasitas trafo terpasang: {sum(1 for r in rows if r['evshare']>20)} dari {len(rows)}")

print(); print("="*70); print("N. KECAMATAN: EV DI ATAS GARDU TERTEKAN (>=80%)")
kec=collections.defaultdict(lambda: dict(n=0,risk=0,ov=0))
for e in mev:
    g=G[e["gi_idx"]]; k=(e["kab"].split(" - ")[-1],e["kec"].split(" - ")[-1])
    kec[k]["n"]+=1
    if g["pb"]>=80: kec[k]["risk"]+=1
    if g["pb"]>=100: kec[k]["ov"]+=1
kr=[(v["risk"],pct(v["risk"],v["n"]),v["n"],v["ov"],k) for k,v in kec.items() if v["n"]>=8]
kr.sort(key=lambda x:(-x[1],-x[0]))
print(f"  {'KECAMATAN':22s} {'KAB/KOTA':20s} {'nEV':>4s} {'nRisk':>5s} {'%risk':>6s} {'nOverload':>9s}")
for n,p,tot,ov,k in kr[:18]:
    print(f"  {k[1][:22]:22s} {k[0][:20]:20s} {tot:4d} {n:5d} {p:6.1f} {ov:9d}")

print(); print("="*70); print("O. INDEKS KESIAPAN JARINGAN UNTUK EV (per UP3)")
u_g=collections.defaultdict(list); u_ev=collections.Counter(); u_sp=collections.Counter(); u_spkw=collections.Counter()
for g in G: u_g[g["up3"]].append(g)
for e in mev: u_ev[G[e["gi_idx"]]["up3"]]+=1
for l in LOC: u_sp[G[l["gi_idx"]]["up3"]]+=1; u_spkw[G[l["gi_idx"]]["up3"]]+=l["kw"]
out=[]
for u,gs in u_g.items():
    if not u.strip(): continue
    n=len(gs)
    head=sum(max(0,x["kva"]*(0.8-x["pb"]/100)) for x in gs)/1000
    ok=sum(1 for x in gs if x["kva"]*(0.8-x["pb"]/100)>=5*7.7*0.6)
    out.append(dict(up3=u.replace("UP3 ",""),n=n,
        headMVA=round(head,1), headPerGardu=round(head*1000/n,1),
        pctReady=round(pct(ok,n),1),
        pctOver=round(pct(sum(1 for x in gs if x["pb"]>=100),n),1),
        pctHot=round(pct(sum(1 for x in gs if x["pb"]>=80),n),1),
        medPb=round(st.median(x["pb"] for x in gs),1),
        unb=round(pct(sum(1 for x in gs if x["stunb"].startswith("Prioritas")),n),1),
        nEV=u_ev[u], evPer1k=round(1000*u_ev[u]/n,1), nSPKLU=u_sp[u], spkluKW=round(u_spkw[u])))
# score: readiness 0-100
mx=max(o["headPerGardu"] for o in out)
for o in out:
    o["score"]=round(0.40*(o["pctReady"]) + 0.25*(100-min(o["pctHot"]*3,100)) + 0.20*(100*o["headPerGardu"]/mx) + 0.15*(100-min(o["unb"],100)),1)
out.sort(key=lambda o:-o["score"])
print(f"  {'UP3':14s} {'skor':>5s} {'%siap5EV':>8s} {'%>=80':>6s} {'%OL':>5s} {'kVA head/gardu':>14s} {'unb%':>5s} {'EV/1k':>6s} {'SPKLU':>5s}")
for o in out:
    print(f"  {o['up3'][:14]:14s} {o['score']:5.1f} {o['pctReady']:8.1f} {o['pctHot']:6.1f} {o['pctOver']:5.1f} {o['headPerGardu']:14.1f} {o['unb']:5.1f} {o['evPer1k']:6.1f} {o['nSPKLU']:5d}")
json.dump(dict(up3=out,feeder=rows[:40],kec=[dict(kec=k[1],kab=k[0],n=tot,risk=n,pct=round(p,1),ov=ov) for n,p,tot,ov,k in kr[:25]],
    nloc=len(LOC),spkw=sum(l["kw"] for l in LOC)),open("analysis/out3.json","w"))
