import pickle,collections,math,json,statistics as st
d=pickle.load(open("analysis/joined.pkl","rb")); G,EV,SP=d["G"],d["EV"],d["SP"]
o3=json.load(open("analysis/out3.json"))
def pct(a,b): return 100.0*a/b if b else 0.0
mev=[e for e in EV if e["gi_idx"] is not None]; msp=[s for s in SP if s["gi_idx"] is not None]
r5=lambda x: round(x,5)
loc=collections.defaultdict(list)
for s in msp: loc[(r5(s["lat"]),r5(s["lon"]))].append(s)
LOC=[dict(lat=k[0],lon=k[1],kw=sum(x["kw"] for x in v),lok=v[0]["lok"],up3=v[0]["up3"],gi_idx=v[0]["gi_idx"],dist=v[0]["dist"],milik=v[0]["milik"]) for k,v in loc.items()]
per=collections.defaultdict(list)
for e in mev: per[e["gi_idx"]].append(e)
def post(gi,evs,cf):
    g=G[gi]; return (g["kva"]*g["pb"]/100.0+sum(e["daya"] for e in evs)/1000.0*cf)/g["kva"]*100.0

O={}
O["meta"]=dict(nGardu=len(G),nGarduRaw=53797,nEV=len(EV),nEVjoin=len(mev),nSP=len(SP),nLoc=len(LOC),
  spkw=round(sum(l["kw"] for l in LOC)),
  totMVA=round(sum(g["kva"] for g in G)/1000,1),
  headMVA=round(sum(max(0,g["kva"]*(0.8-g["pb"]/100)) for g in G)/1000,1),
  medPb=round(st.median(g["pb"] for g in G),1))
O["catAll"]=dict(collections.Counter(g["kat"] for g in G))
O["catEV"]=dict(collections.Counter(G[e["gi_idx"]]["kat"] for e in mev))
O["catSP"]=dict(collections.Counter(G[l["gi_idx"]]["kat"] for l in LOC))
O["evRisk"]=sum(1 for e in mev if G[e["gi_idx"]]["pb"]>=80)
O["spRisk"]=sum(1 for l in LOC if G[l["gi_idx"]]["pb"]>=80)
O["diurnal"]=dict(
  evSiang=round(st.mean(G[e["gi_idx"]]["pbs"] for e in mev if G[e["gi_idx"]]["pbs"] is not None),1),
  evMalam=round(st.mean(G[e["gi_idx"]]["pbm"] for e in mev if G[e["gi_idx"]]["pbm"] is not None),1),
  allSiang=round(st.mean(g["pbs"] for g in G if g["pbs"] is not None),1),
  allMalam=round(st.mean(g["pbm"] for g in G if g["pbm"] is not None),1))
sc=[]
for cf in (1.0,0.6,0.35):
    a=b=c=0
    for gi,evs in per.items():
        g=G[gi]; p=post(gi,evs,cf)
        if g["pb"]>=100: a+=1
        elif p>=100: b+=1
        elif g["pb"]<80<=p: c+=1
    sc.append(dict(cf=cf,already=a,newOver=b,newHot=c))
O["scen"]=sc
O["cluster"]=sorted(collections.Counter(min(len(v),10) for v in per.values()).items())
hh=[]
for g in G:
    n=max(0,g["kva"]*(0.8-g["pb"]/100))/(7.7*0.6)
    hh.append(0 if n<1 else 1 if n<3 else 2 if n<5 else 3 if n<10 else 4 if n<20 else 5)
O["hostCap"]=dict(collections.Counter(hh))
# top hotspot gardu
tops=[]
for gi,evs in per.items():
    g=G[gi]; p=post(gi,evs,0.6)
    if p>=80: tops.append(dict(nm=g["nama"],up3=g["up3"].replace("UP3 ",""),kva=g["kva"],pb=round(g["pb"],1),
        post=round(p,1),nev=len(evs),peny=g["peny"],gi=g["gi"],lat=r5(g["lat"]),lon=r5(g["lon"])))
tops.sort(key=lambda x:-x["post"]); O["topGardu"]=tops[:40]; O["nTopGardu"]=len(tops)
# GI
gi_ev=collections.Counter(); gi_sp=collections.Counter(); gi_kw=collections.Counter(); gi_i={}
for e in mev:
    g=G[e["gi_idx"]]
    if g["gikode"]: gi_ev[g["gikode"]]+=1; gi_i[g["gikode"]]=g
for l in LOC:
    g=G[l["gi_idx"]]
    if g["gikode"]: gi_sp[g["gikode"]]+=1; gi_kw[g["gikode"]]+=l["kw"]; gi_i.setdefault(g["gikode"],g)
GI=[]
for k,g in gi_i.items():
    if g["gips"] is None: continue
    GI.append(dict(k=k,nm=g["gi"],up3=g["up3"].replace("UP3 ",""),mva=g["gimva"],
        ps=round(g["gips"],1),pm=round(g["gipm"],1),mx=round(max(g["gips"],g["gipm"]),1),
        nev=gi_ev[k],nsp=gi_sp[k],kw=round(gi_kw[k])))
GI.sort(key=lambda x:-x["mx"]); O["gi"]=GI
u_hot=collections.Counter(); u_ev2=collections.Counter()
for e in mev:
    g=G[e["gi_idx"]]; u=g["up3"].replace("UP3 ","")
    u_ev2[u]+=1
    if g["pb"]>=80: u_hot[u]+=1
for u in o3["up3"]:
    u["nEVhot"]=u_hot[u["up3"]]
    u["pctEVhot"]=round(pct(u_hot[u["up3"]],u_ev2[u["up3"]]),1) if u_ev2[u["up3"]] else 0.0
O["up3"]=o3["up3"]; O["feeder"]=o3["feeder"][:20]; O["kec"]=o3["kec"][:20]
# map layers (compact arrays)
O["mapEV"]=[[r5(e["lat"]),r5(e["lon"]),1 if G[e["gi_idx"]]["pb"]>=100 else (2 if G[e["gi_idx"]]["pb"]>=80 else 0)] for e in mev]
O["mapHot"]=[[r5(g["lat"]),r5(g["lon"]),round(g["pb"]),int(g["kva"])] for g in G if g["pb"]>=80]
O["mapSP"]=[[l["lat"],l["lon"],round(l["kw"])] for l in LOC]
# EV distance to SPKLU
def hav(a,b,c,e): return math.hypot((c-a)*111320.0,(e-b)*111320.0*math.cos(math.radians(a)))
ds=sorted(min(hav(e["lat"],e["lon"],s["lat"],s["lon"]) for s in SP) for e in mev)
O["evSpDist"]=dict(med=round(ds[len(ds)//2]/1000,2),p90=round(ds[int(.9*len(ds))]/1000,2),
  w2=sum(1 for x in ds if x<=2000),w5=sum(1 for x in ds if x<=5000))
json.dump(O,open("analysis/grid.json","w"),separators=(",",":"))
import os; print("bytes:",os.path.getsize("analysis/grid.json"))
