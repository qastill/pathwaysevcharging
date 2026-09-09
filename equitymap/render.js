
/* ============ PETA EKUITAS — prioritas × kelayakan per heksagon (window.EQUITY, dimuat malas) ============ */
(function(){
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>(n==null||isNaN(n))?'—':Math.round(+n).toLocaleString('id-ID');
const f1=n=>(n==null||isNaN(n))?'—':(+n).toLocaleString('id-ID',{maximumFractionDigits:1,minimumFractionDigits:1});
const jt=n=>n>=1e6?(n/1e6).toLocaleString('id-ID',{maximumFractionDigits:2})+' jt':n>=1e3?(n/1e3).toLocaleString('id-ID',{maximumFractionDigits:0})+' rb':fmt(n);
const NAVY='#16305f',GOLD='#d4af37',BLUE='#3a6ea5',GREEN='#2e9e5b',RED='#d6443c',ORANGE='#e8742c',MUT='#9aa6bd';
const ZC=[RED,ORANGE,BLUE,'#c3cad8'];
const ZL=['Prioritas tinggi & layak — bangun sekarang','Prioritas tinggi, jaringan lemah — investasi jaringan dulu','Layak, prioritas rendah — biarkan pasar','Prioritas & kelayakan rendah'];
const IND=[
 {k:'d_spklu',g:'P',s:+1,w:30,lab:'Jarak ke SPKLU terdekat',h:'km garis lurus ke situs operasional terdekat (dipotong 50 km). Jauh = prioritas tinggi.'},
 {k:'ppc',g:'P',s:+1,w:25,lab:'Jiwa per charger dalam ~10 km',h:'penduduk dua cincin heksagon ÷ charger operasional dalam 10 km; tanpa charger = maksimum.'},
 {k:'pop',g:'P',s:+1,w:25,lab:'Penduduk heksagon',h:'jiwa per heksagon ≈36 km² (Kontur 2023) — setara kepadatan karena luasnya hampir sama.'},
 {k:'burden',g:'P',s:+1,w:20,lab:'Beban sosial-ekonomi provinsi',h:'(z kemiskinan − z IPM)/2 tingkat provinsi, BPS ~2023 indikatif. Miskin & IPM rendah = tinggi.'},
 {k:'d_gi',g:'F',s:-1,w:30,lab:'Jarak ke gardu induk',h:'km ke gardu induk terdekat (data/grid-id, RUPTL/OSM). Dekat = layak.'},
 {k:'mva25',g:'F',s:+1,w:20,lab:'Kapasitas GI dalam 25 km',h:'jumlah MVA gardu induk dalam radius 25 km.'},
 {k:'d_tx',g:'F',s:-1,w:15,lab:'Jarak ke ruas transmisi',h:'km ke ruas transmisi 70–500 kV terdekat.'},
 {k:'pop10',g:'F',s:+1,w:20,lab:'Penduduk dalam ~10 km',h:'pasar yang bisa dijangkau satu situs.'},
 {k:'c10',g:'F',s:+1,w:15,lab:'Charger sudah ada dalam 10 km',h:'aglomerasi: operator sudah hidup di dekatnya.'}];
const PRESET={
 def:Object.fromEntries(IND.map(i=>[i.k,i.w])),
 eq:{d_spklu:35,ppc:30,pop:10,burden:25,d_gi:30,mva25:20,d_tx:15,pop10:20,c10:15},
 com:{d_spklu:10,ppc:15,pop:45,burden:0,d_gi:20,mva25:15,d_tx:10,pop10:35,c10:20}};

let E=null,ROWS=null,built=false,map=null,canvas=null,hexLayer=null,spkluLayer=null,giLayer=null,cellIndex=new Map(),cellRes=6;
const C={};
const S={prov:'all',kab:'all',mode:'zone',cov:'all',w:{...PRESET.def}};
let sortK='P',sortD=-1,tableRows=[];

function loadScript(src){return new Promise((res,rej)=>{const s=document.createElement('script');s.src=src;s.onload=res;s.onerror=()=>rej(new Error('gagal memuat '+src));document.head.appendChild(s);});}
function mk(id,cfg){if(C[id])C[id].destroy();const el=$(id);if(!el||typeof Chart==='undefined')return;C[id]=new Chart(el,cfg);}

/* ---------- data ---------- */
function parseRows(){
 const ci={};E.cols.forEach((c,i)=>ci[c]=i);
 ROWS=E.r6.map(a=>{const r={};E.cols.forEach((c,i)=>r[c]=a[i]);r.prov=E.kabs[r.kab].prov;r.burden=E.provs[r.prov].burden;return r;});
}
const val=(r,k)=>{
 if(k==='d_spklu')return Math.min(S.cov==='pln'?r.d_pln:r.d_spklu,E.meta.cap_km);
 if(k==='ppc'){const c=S.cov==='pln'?r.c10p:r.c10;return c>0?r.pop10/c:1e9;}
 if(k==='c10')return S.cov==='pln'?r.c10p:r.c10;
 if(k==='d_gi'||k==='d_tx')return Math.min(r[k],E.meta.cap_km);
 return r[k];};
const dist=r=>S.cov==='pln'?r.d_pln:r.d_spklu;
const chg=r=>S.cov==='pln'?r.c10p:r.c10;

function rank(v){const n=v.length;const idx=Array.from({length:n},(_,i)=>i).sort((a,b)=>v[a]-v[b]);const r=new Float64Array(n);
 let i=0;while(i<n){let j=i;while(j+1<n&&v[idx[j+1]]===v[idx[i]])j++;const avg=(i+j)/2;for(let k=i;k<=j;k++)r[idx[k]]=avg;i=j+1;}
 const d=Math.max(n-1,1);for(let k=0;k<n;k++)r[k]=100*r[k]/d;return r;}

function scopeRows(){return S.prov==='all'?ROWS:ROWS.filter(r=>r.prov===+S.prov);}
function score(rows){
 const n=rows.length,P=new Float64Array(n),F=new Float64Array(n);let wp=0,wf=0;
 IND.forEach(ind=>{const w=+S.w[ind.k]||0;if(!w)return;const v=new Float64Array(n);for(let i=0;i<n;i++)v[i]=ind.s*val(rows[i],ind.k);
  const rk=rank(v);if(ind.g==='P'){wp+=w;for(let i=0;i<n;i++)P[i]+=w*rk[i];}else{wf+=w;for(let i=0;i<n;i++)F[i]+=w*rk[i];}});
 for(let i=0;i<n;i++){const r=rows[i];r.P=wp?P[i]/wp:50;r.F=wf?F[i]/wf:50;r.Z=r.P>=50?(r.F>=50?0:1):(r.F>=50?2:3);}
 return rows;}

function aggKab(rows){
 const m=new Map();
 rows.forEach(r=>{let a=m.get(r.kab);if(!a){a={idx:r.kab,name:E.kabs[r.kab].name,prov:r.prov,provn:E.provs[r.prov].name,pop:0,dp:0,in10:0,b25:0,P:0,F:0,z0:0,z1:0,gi:0};m.set(r.kab,a);}
  const d=dist(r);a.pop+=r.pop;a.dp+=r.pop*Math.min(d,200);if(d<=10)a.in10+=r.pop;if(d>25)a.b25+=r.pop;a.P+=r.pop*r.P;a.F+=r.pop*r.F;if(r.Z===0)a.z0+=r.pop;if(r.Z===1)a.z1+=r.pop;});
 const ks={};E.kab_stats.forEach(k=>ks[k.idx]=k);
 return [...m.values()].map(a=>{const k=ks[a.idx]||{};a.d_mean=a.dp/a.pop;a.within10=100*a.in10/a.pop;a.beyond25=100*a.b25/a.pop;a.P/=a.pop;a.F/=a.pop;
  a.chargers=S.cov==='pln'?(k.chargers_pln||0):(k.chargers||0);a.per100k=a.pop?1e5*a.chargers/a.pop:0;a.gi=k.gi||0;a.sites=k.active||0;a.dc=k.dc||0;return a;});}

function lorenz(units){const u=units.filter(x=>x.pop>0).sort((a,b)=>a.chargers/a.pop-b.chargers/b.pop);
 const P=u.reduce((s,x)=>s+x.pop,0),V=u.reduce((s,x)=>s+x.chargers,0)||1;let cp=0,cv=0,area=0;const pts=[{x:0,y:0}];
 u.forEach(x=>{const p0=cp,v0=cv;cp+=x.pop/P;cv+=x.chargers/V;area+=(cp-p0)*(cv+v0)/2;pts.push({x:+cp.toFixed(3),y:+cv.toFixed(3)});});
 return {g:1-2*area,pts};}

/* ---------- warna ---------- */
const ramp=(t,a,b)=>{const h=x=>x.match(/\w\w/g).map(v=>parseInt(v,16));const A=h(a),B=h(b);return '#'+A.map((c,i)=>Math.round(c+(B[i]-c)*t).toString(16).padStart(2,'0')).join('');};
const popBins=[0,2000,10000,50000,200000,1e12];
function colorOf(r){
 if(S.mode==='zone')return ZC[r.Z];
 if(S.mode==='prio')return ramp(r.P/100,'#fdf1e9','#b3261e');
 if(S.mode==='feas')return ramp(r.F/100,'#eaf4ee','#155f3f');
 if(S.mode==='dist'){const d=dist(r);return d<=5?'#1b6b46':d<=10?'#7fc39a':d<=25?'#e0a52b':d<=50?ORANGE:RED;}
 const i=popBins.findIndex((b,j)=>r.pop<popBins[j+1]);return ['#eef1f6','#c9d4e8','#8ea6cc','#4f6ea3',NAVY][Math.max(0,i)];}
function legendHtml(){
 const it=(c,t)=>`<span><i style="background:${c}"></i>${t}</span>`;
 if(S.mode==='zone')return ZL.map((z,i)=>it(ZC[i],z)).join('');
 if(S.mode==='prio')return [0,25,50,75,100].map(v=>it(ramp(v/100,'#fdf1e9','#b3261e'),'P '+v)).join('')+'<span>skor prioritas keadilan 0–100 (peringkat persentil tertimbang di lingkup)</span>';
 if(S.mode==='feas')return [0,25,50,75,100].map(v=>it(ramp(v/100,'#eaf4ee','#155f3f'),'F '+v)).join('')+'<span>skor kelayakan pasokan 0–100</span>';
 if(S.mode==='dist')return it('#1b6b46','≤5 km')+it('#7fc39a','5–10')+it('#e0a52b','10–25')+it(ORANGE,'25–50')+it(RED,'>50 km')+'<span>jarak garis lurus ke SPKLU operasional terdekat</span>';
 return it('#eef1f6','<2 rb')+it('#c9d4e8','2–10 rb')+it('#8ea6cc','10–50 rb')+it('#4f6ea3','50–200 rb')+it(NAVY,'>200 rb jiwa')+'<span>per heksagon ≈36 km² (res 6) / ≈253 km² (res 5, tinjauan nasional)</span>';}

/* ---------- peta ---------- */
function initMap(){
 map=L.map('emMap',{preferCanvas:true}).setView([-2.3,118],5);
 L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{attribution:'© OSM © CARTO · Kontur Population · geoBoundaries · PLN',maxZoom:19}).addTo(map);
 canvas=L.canvas({padding:.4});
 // popup lewat pencarian sel H3 di titik klik — tidak bergantung pada hit-test kanvas per poligon
 map.on('click',e=>{const c=cellIndex.get(h3.latLngToCell(e.latlng.lat,e.latlng.lng,cellRes));
  if(c)L.popup({maxWidth:320}).setLatLng(e.latlng).setContent(popupOf(c)).openOn(map);});
}
function drawHex(rows,res5){
 if(hexLayer){hexLayer.remove();hexLayer=null;}
 hexLayer=L.layerGroup().addTo(map);
 let cells=rows;
 if(res5){const m=new Map();
  rows.forEach(r=>{const p=h3.cellToParent(r.h3,5);let a=m.get(p);if(!a){a={h3:p,pop:0,P:0,F:0,d:0,zp:[0,0,0,0],kab:{},n:0};m.set(p,a);}
   a.pop+=r.pop;a.P+=r.pop*r.P;a.F+=r.pop*r.F;a.d+=r.pop*Math.min(dist(r),200);a.zp[r.Z]+=r.pop;a.kab[r.kab]=(a.kab[r.kab]||0)+r.pop;a.n++;});
  cells=[...m.values()].map(a=>{a.P/=a.pop;a.F/=a.pop;a.d_spklu=a.d_pln=a.d/a.pop;a.Z=a.zp.indexOf(Math.max(...a.zp));a.kab=+Object.keys(a.kab).sort((x,y)=>a.kab[y]-a.kab[x])[0];a.prov=E.kabs[a.kab].prov;a.agg=true;return a;});}
 cellIndex=new Map();cellRes=res5?5:6;
 cells.forEach(c=>{cellIndex.set(c.h3,c);
  L.polygon(h3.cellToBoundary(c.h3),{renderer:canvas,stroke:false,fillColor:colorOf(c),fillOpacity:S.mode==='zone'?.72:.8,interactive:false}).addTo(hexLayer);});
 $('emLegend').innerHTML=legendHtml();
 const T={zone:'Zona',prio:'Prioritas keadilan',feas:'Kelayakan pasokan',dist:'Jarak ke SPKLU',pop:'Populasi'};
 $('emMapTitle').textContent=T[S.mode];
 $('emMapSub').textContent=`— ${cells.length.toLocaleString('id-ID')} heksagon ${res5?'res 5 (agregat dari res 6)':'res 6'} · ${scopeName()} · klik heksagon untuk rincian`;
}
function popupOf(c){
 const kab=E.kabs[c.kab],prov=E.provs[kab.prov];
 const z=`<span class="zone z${c.Z}" style="display:inline-block;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:700;color:#fff;background:${ZC[c.Z]}">${ZL[c.Z].split(' — ')[0]}</span>`;
 let s=`<div style="font-size:12px;line-height:1.55"><b>${esc(kab.name)}</b> · ${esc(prov.name)}<br>${z}<br>`;
 s+=`Penduduk ${fmt(c.pop)} jiwa${c.agg?' (agregat res 5)':''}<br>Prioritas <b>${f1(c.P)}</b> · Kelayakan <b>${f1(c.F)}</b><br>`;
 s+=`SPKLU operasional terdekat <b>${f1(dist(c))} km</b>`;
 if(!c.agg){s+=`<br>Charger dalam 10 km: <b>${chg(c)}</b> (DC ≥${E.meta.dc_kw} kW: ${S.cov==='pln'?c.dc10p:c.dc10}) · jiwa/charger: <b>${chg(c)?fmt(c.pop10/chg(c)):'∞'}</b>`;
  s+=`<br>Penduduk ~10 km: ${fmt(c.pop10)}<br>Gardu induk terdekat ${f1(c.d_gi)} km · ${fmt(c.mva25)} MVA dalam 25 km · transmisi ${f1(c.d_tx)} km`;
  s+=`<br>Provinsi: IPM ${prov.hdi} · kemiskinan ${prov.poverty}%`;}
 return s+'</div>';}
function drawOverlays(){
 if(spkluLayer){spkluLayer.remove();spkluLayer=null;}if(giLayer){giLayer.remove();giLayer=null;}
 const inScope=k=>S.prov==='all'||E.kabs[k].prov===+S.prov;
 if($('emLySpklu').checked){spkluLayer=L.layerGroup().addTo(map);
  E.spklu.forEach(s=>{if(!inScope(s[7]))return;if(S.cov==='pln'&&!s[5])return;const col=!s[4]?'#9aa6bd':s[5]?NAVY:GOLD;
   L.circleMarker([s[0],s[1]],{renderer:canvas,radius:3,fillColor:col,color:'#fff',weight:.6,fillOpacity:.95})
    .bindPopup(`<b>${esc(s[6])}</b><br>${s[2]} kW · ${s[3]} charger · ${s[5]?'PLN':'mitra non-PLN'} · ${s[4]?'operasional':'tidak aktif'}<br>${esc(E.kabs[s[7]].name)}`).addTo(spkluLayer);});}
 if($('emLyGi').checked){giLayer=L.layerGroup().addTo(map);
  E.gi.forEach(g=>{L.circleMarker([g[0],g[1]],{renderer:canvas,radius:4,fillColor:GREEN,color:'#fff',weight:.8,fillOpacity:.9})
   .bindPopup(`<b>GI ${esc(g[3])}</b><br>${g[4]} kV · ${fmt(g[2])} MVA`).addTo(giLayer);});}
}

/* ---------- ringkasan, grafik, tabel ---------- */
const scopeName=()=>S.kab!=='all'?E.kabs[+S.kab].name:S.prov==='all'?'Indonesia':E.provs[+S.prov].name;
function summarize(rows,kabs){
 const sel=S.kab!=='all'?rows.filter(r=>r.kab===+S.kab):rows;
 const pop=sel.reduce((s,r)=>s+r.pop,0);
 const bands=[0,0,0,0,0];sel.forEach(r=>{const d=dist(r);bands[d<=5?0:d<=10?1:d<=25?2:d<=50?3:4]+=r.pop;});
 const zp=[0,0,0,0];sel.forEach(r=>zp[r.Z]+=r.pop);
 const kk=S.kab!=='all'?kabs.filter(k=>k.idx===+S.kab):kabs;
 const chargers=kk.reduce((s,k)=>s+k.chargers,0);
 const lz=lorenz(kabs);
 const in10=100*(bands[0]+bands[1])/pop,b25=100*(bands[3]+bands[4])/pop;
 const dm=sel.reduce((s,r)=>s+r.pop*Math.min(dist(r),200),0)/pop;
 $('emStats').innerHTML=[[jt(pop),'penduduk '+scopeName()+' (Kontur 2023)'],[f1(in10)+'%','≤10 km dari SPKLU operasional'],[f1(b25)+'%','>25 km — gurun pengisian'],
  [fmt(chargers),'charger operasional'+(S.cov==='pln'?' (PLN)':'')],[chargers?jt(pop/chargers):'∞','jiwa per charger'],[f1(dm)+' km','jarak rata-rata tertimbang'],
  [jt(zp[0]),'jiwa di zona 1 — bangun sekarang'],[jt(zp[1]),'jiwa di zona 2 — jaringan dulu'],[lz.g.toFixed(3),'Gini charger/kapita antar-kab ('+(S.prov==='all'?'nasional':'provinsi')+')']]
  .map(x=>`<div class="s"><div class="n">${x[0]}</div><div class="t">${x[1]}</div></div>`).join('');
 const top=kabs.filter(k=>S.kab==='all'||k.idx===+S.kab).slice().sort((a,b)=>b.z0-a.z0).slice(0,3);
 const topP=kabs.slice().sort((a,b)=>b.P-a.P).slice(0,3);
 $('emInsight').innerHTML=`<b>Bacaan peta — ${esc(scopeName())}.</b> ${f1(in10)}% penduduk tinggal ≤10 km dari SPKLU operasional dan ${f1(b25)}% (${jt(bands[3]+bands[4])} jiwa) lebih dari 25 km.
  Dengan bobot saat ini, <b>${jt(zp[0])} jiwa</b> berada di <b>zona 1</b> (prioritas tinggi <i>dan</i> layak — kandidat pembangunan pertama), paling banyak di ${top.map(k=>'<b>'+esc(k.name)+'</b> ('+jt(k.z0)+')').join(', ')};
  <b>${jt(zp[1])} jiwa</b> di <b>zona 2</b> (prioritas tinggi tetapi jauh dari gardu induk/transmisi — charger di sini menuntut investasi jaringan lebih dulu).
  Prioritas keadilan tertinggi tertimbang penduduk: ${topP.map(k=>esc(k.name)+' ('+f1(k.P)+')').join(', ')}.
  Gini charger per kapita antar-kabupaten <b>${lz.g.toFixed(2)}</b> — ${lz.g>.5?'sangat timpang':lz.g>.35?'timpang':'relatif merata'}. Ubah lensa/bobot di atas: zona berubah, penduduknya tidak.`;
 // grafik
 mk('cEmBands',{type:'bar',data:{labels:['≤5 km','5–10','10–25','25–50','>50 km'],datasets:[{data:bands.map(b=>Math.round(b/1e6*100)/100),backgroundColor:['#1b6b46','#7fc39a','#e0a52b',ORANGE,RED],borderRadius:3}]},
  options:{maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:x=>x.raw+' juta jiwa'}}},scales:{y:{beginAtZero:true,title:{display:true,text:'juta jiwa',font:{size:10}},ticks:{font:{size:10}},grid:{color:'#eef1f6'}},x:{grid:{display:false},ticks:{font:{size:10}}}}}});
 mk('cEmLorenz',{type:'line',data:{datasets:[{label:'Lorenz',data:lz.pts,borderColor:NAVY,backgroundColor:'rgba(22,48,95,.12)',fill:true,pointRadius:0,borderWidth:2,tension:.1},
  {label:'kesetaraan',data:[{x:0,y:0},{x:1,y:1}],borderColor:MUT,borderDash:[5,4],pointRadius:0,borderWidth:1.5}]},
  options:{maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:x=>`${Math.round(x.raw.x*100)}% penduduk → ${Math.round(x.raw.y*100)}% charger`}}},
   scales:{x:{type:'linear',min:0,max:1,title:{display:true,text:'kumulatif penduduk (kab diurut charger/kapita)',font:{size:9}},ticks:{font:{size:9}}},y:{min:0,max:1,title:{display:true,text:'kumulatif charger',font:{size:9}},ticks:{font:{size:9}},grid:{color:'#eef1f6'}}}}});
 $('emLorenzSub').textContent=`antar-kabupaten · Gini ${lz.g.toFixed(3)}`;
 mk('cEmZone',{type:'doughnut',data:{labels:ZL.map(z=>z.split(' — ')[0]),datasets:[{data:zp.map(v=>Math.round(v/1e6*100)/100),backgroundColor:ZC,borderWidth:1}]},
  options:{maintainAspectRatio:false,cutout:'55%',plugins:{legend:{position:'right',labels:{boxWidth:10,font:{size:9.5}}},tooltip:{callbacks:{label:x=>x.label+': '+x.raw+' jt jiwa'}}}}});
 // peringkat
 let units,title;
 if(S.prov==='all'){const m=new Map();rows.forEach(r=>{let a=m.get(r.prov);if(!a){a={name:E.provs[r.prov].name,pop:0,in10:0,P:0};m.set(r.prov,a);}a.pop+=r.pop;if(dist(r)<=10)a.in10+=r.pop;a.P+=r.pop*r.P;});
  units=[...m.values()].map(a=>({name:a.name,v:100*a.in10/a.pop,P:a.P/a.pop}));title='provinsi';}
 else{units=kabs.map(k=>({name:k.name,v:k.within10,P:k.P}));title='kabupaten/kota — '+E.provs[+S.prov].name;}
 units.sort((a,b)=>b.v-a.v);$('emRankTitle').textContent=title;
 mk('cEmRank',{type:'bar',data:{labels:units.map(u=>u.name),datasets:[{label:'% penduduk ≤10 km',data:units.map(u=>+u.v.toFixed(1)),backgroundColor:units.map(u=>ramp(u.P/100,'#c9d4e8','#b3261e')),borderRadius:2}]},
  options:{indexAxis:'y',maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:x=>'prioritas tertimbang: '+f1(units[x.dataIndex].P)}}},
   scales:{x:{min:0,max:100,grid:{color:'#eef1f6'},ticks:{font:{size:10}},title:{display:true,text:'% penduduk ≤10 km dari SPKLU operasional · warna = skor prioritas (biru rendah → merah tinggi)',font:{size:10}}},y:{grid:{display:false},ticks:{font:{size:units.length>40?8:10},autoSkip:false}}}}});
}
function renderTable(){
 const q=($('emSearch').value||'').toLowerCase();
 let rows=tableRows.filter(k=>!q||k.name.toLowerCase().includes(q)||k.provn.toLowerCase().includes(q));
 rows.sort((a,b)=>{const x=a[sortK],y=b[sortK];return (typeof x==='string')?sortD*x.localeCompare(y):sortD*((x||0)-(y||0));});
 $('emCount').textContent=rows.length+' kabupaten/kota';
 const bar=(v,c)=>`<span class="bar"><i style="width:${Math.max(0,Math.min(100,v))}%;background:${c}"></i></span>${f1(v)}`;
 $('tblEm').querySelector('tbody').innerHTML=rows.map(k=>`<tr data-k="${k.idx}" style="cursor:pointer${S.kab!=='all'&&+S.kab===k.idx?';background:#fff7e3':''}">
  <td><b>${esc(k.name)}</b></td><td>${esc(k.provn)}</td><td class="n">${fmt(k.pop)}</td><td class="n">${fmt(k.chargers)}</td><td class="n">${f1(k.per100k)}</td>
  <td class="n">${f1(k.d_mean)}</td><td class="n">${f1(k.within10)}</td><td class="n" style="color:${k.beyond25>50?RED:'inherit'}">${f1(k.beyond25)}</td><td class="n">${k.gi}</td>
  <td>${bar(k.P,'#b3261e')}</td><td>${bar(k.F,'#155f3f')}</td><td class="n">${fmt(k.z0)}</td></tr>`).join('');
 $('tblEm').querySelectorAll('tbody tr').forEach(tr=>tr.onclick=()=>{S.kab=tr.dataset.k;$('emKab').value=S.kab;update(false);zoomKab();});
}
function zoomKab(){
 const rows=S.kab!=='all'?ROWS.filter(r=>r.kab===+S.kab):scopeRows();
 if(!rows.length)return;let s=1e9,n=-1e9,w=1e9,e=-1e9;
 rows.forEach(r=>{const [la,lo]=h3.cellToLatLng(r.h3);s=Math.min(s,la);n=Math.max(n,la);w=Math.min(w,lo);e=Math.max(e,lo);});
 map.fitBounds([[s-.05,w-.05],[n+.05,e+.05]]);
}
function csv(){
 const h=['kabupaten','provinsi','penduduk','charger','charger_per_100k','jarak_rata_km','pct_dalam_10km','pct_lebih_25km','gardu_induk','prioritas','kelayakan','jiwa_zona1','jiwa_zona2'];
 const lines=[h.join(',')].concat(tableRows.map(k=>[k.name,k.provn,Math.round(k.pop),k.chargers,k.per100k.toFixed(2),k.d_mean.toFixed(1),k.within10.toFixed(1),k.beyond25.toFixed(1),k.gi,k.P.toFixed(1),k.F.toFixed(1),Math.round(k.z0),Math.round(k.z1)].map(v=>/[",]/.test(v)?'"'+String(v).replace(/"/g,'""')+'"':v).join(',')));
 const w=Object.entries(S.w).map(([k,v])=>k+'='+v).join(' ');
 const blob=new Blob(['# Peta Ekuitas SPKLU — lingkup '+scopeName()+' · cakupan '+S.cov+' · bobot '+w+'\n'+lines.join('\n')],{type:'text/csv;charset=utf-8'});
 const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='peta_ekuitas_'+scopeName().replace(/\W+/g,'_')+'.csv';a.click();
}

/* ---------- kontrol ---------- */
function renderWeights(){
 const row=i=>`<div class="wrow"><div class="lab"><b>${i.lab}</b><span class="v" id="emwv_${i.k}">${S.w[i.k]}</span></div><input type="range" min="0" max="50" step="5" value="${S.w[i.k]}" data-k="${i.k}"><div class="h">${i.h}</div></div>`;
 $('emWP').innerHTML=IND.filter(i=>i.g==='P').map(row).join('');$('emWF').innerHTML=IND.filter(i=>i.g==='F').map(row).join('');
 document.querySelectorAll('#p-ekuitas .wrow input').forEach(inp=>inp.oninput=()=>{S.w[inp.dataset.k]=+inp.value;$('emwv_'+inp.dataset.k).textContent=inp.value;update(true);});
 const wp=IND.filter(i=>i.g==='P').reduce((s,i)=>s+(+S.w[i.k]),0),wf=IND.filter(i=>i.g==='F').reduce((s,i)=>s+(+S.w[i.k]),0);
 $('emWsum').textContent=`bobot prioritas Σ${wp} · kelayakan Σ${wf} (dinormalisasi)`;
}
function applyPreset(p){S.w={...p};renderWeights();update(true);}
function fillKab(){
 const sel=$('emKab');const cur=S.kab;
 const ks=E.kabs.map((k,i)=>({i,...k})).filter(k=>S.prov==='all'||k.prov===+S.prov).sort((a,b)=>a.name.localeCompare(b.name));
 sel.innerHTML='<option value="all">Semua</option>'+ks.map(k=>`<option value="${k.i}">${esc(k.name)}${S.prov==='all'?' · '+esc(E.provs[k.prov].name):''}</option>`).join('');
 sel.value=ks.some(k=>String(k.i)===cur)?cur:'all';S.kab=sel.value;
}
function update(recompute){
 const rows=score(scopeRows());
 const kabs=aggKab(rows);tableRows=kabs;
 summarize(rows,kabs);renderTable();
 drawHex(rows,S.prov==='all');drawOverlays();
}
function note(){
 const m=E.meta,n=E.nat;
 $('emNote').innerHTML=`<b>Apa yang dihitung.</b> Untuk tiap heksagon H3 resolusi 6 berpenduduk ≥${m.pop_min} jiwa (${fmt(n.hex_live)} heksagon, ${jt(n.pop_live)} jiwa = ${f1(100*n.pop_live/n.pop)}% penduduk), sembilan indikator mentah dihitung di
  <code>equitymap/prepare.py</code>: jarak garis lurus ke SPKLU operasional terdekat, charger &amp; situs DC ≥${m.dc_kw} kW dalam 10 km, penduduk dalam dua cincin heksagon (~10 km), jarak ke gardu induk, MVA dalam 25 km, jarak ke ruas transmisi,
  dan beban sosial-ekonomi provinsi. <b>Skor</b> = rata-rata tertimbang <i>peringkat persentil</i> tiap indikator di dalam lingkup yang dipilih (arah dibalik untuk jarak); <b>zona</b> membagi pada skor 50 — sehingga, seperti EV Equity Roadmap,
  peta ini menjawab <i>"di mana lebih dulu"</i> di dalam yurisdiksi, bukan berapa kWh yang akan terjual. Tinjauan nasional menggabungkan heksagon ke resolusi 5 (rata-rata tertimbang penduduk; zona = zona dengan penduduk terbanyak).<br>
  <b>Sumber.</b> ${m.sources.map(esc).join(' · ')}. Situs <b>operasional</b> = PLN berstatus <i>available/inuse</i> (${fmt(n.active_pln)}) + seluruh situs mitra non-PLN (${fmt(n.active-n.active_pln)}) yang berstatus <i>offline mode</i> karena tidak terpantau sistem PLN — bukan karena mati; sakelar <b>PLN saja</b> membuang situs mitra. PLN <i>unavailable/maintenance</i> dikecualikan.<br>
  <b>Batas yang harus dibaca bersama petanya.</b> <span class="warn">1</span> Indikator sosial-ekonomi masih tingkat <b>provinsi</b> (BPS ~2023 indikatif) — di dalam satu provinsi, "beban" tidak membedakan kota dan kabupaten; padanan CalEnviroScreen di tingkat kabupaten/kecamatan adalah pekerjaan berikutnya.
  <span class="warn">2</span> Jarak <b>garis lurus</b>, bukan waktu tempuh jalan — di kepulauan dan pegunungan ini meremehkan hambatan (OSRM/Valhalla di katalog adalah langkah lanjutnya).
  <span class="warn">3</span> Master SPKLU adalah registri PLN: SPKLU di wilayah <b>PLN Batam</b> (Kepulauan Riau) tidak ada di dalamnya, sehingga Batam tampak sebagai gurun palsu; situs mitra bermerek (mis. "khusus kendaraan Hyundai") dihitung operasional walau aksesnya terbatas.
  <span class="warn">4</span> Kelayakan memakai proksi <b>transmisi/GI</b>; headroom trafo distribusi (yang menentukan sambungan nyata) baru ada untuk Jawa Barat di tab Capacity Maps.
  <span class="warn">5</span> Populasi Kontur 2023 adalah estimasi model (GHSL, bangunan, HRSL) — total ${jt(n.pop)} jiwa versus proyeksi BPS ±279 juta; per heksagon galatnya lebih besar.
  <span class="warn">6</span> Heksagon &lt;${m.pop_min} jiwa tidak ditampilkan tetapi ikut dalam statistik kabupaten/provinsi.<br>
  <b>Reproduksi.</b> <code>python3 equitymap/fetch.py</code> (unduh Kontur &amp; geoBoundaries, sekali) → <code>python3 equitymap/prepare.py</code> → <code>python3 equitymap/inject.py</code>. Rincian di <code>equitymap/README.md</code>;
  intisari alat aslinya di <a href="#" data-emlib="bacaan-evmap">Perpustakaan → Intisari bacaan: EV Equity Roadmap</a>; pustaka yang dipakai (H3, Kontur, geoBoundaries, EV Equity Roadmap) ada di <a href="#" data-emres="siting">Repositori Riset</a>.`;
 document.querySelectorAll('#p-ekuitas [data-emlib]').forEach(a=>a.onclick=e=>{e.preventDefault();if(window.gotoTab)gotoTab('library');setTimeout(()=>{const b=document.querySelector('#p-library [data-libopen="bacaan-evmap"]');if(b)b.click();},400);});
 document.querySelectorAll('#p-ekuitas [data-emres]').forEach(a=>a.onclick=e=>{e.preventDefault();try{history.replaceState(null,'','#tab=resources&cat='+a.dataset.emres);}catch(x){}if(window.gotoTab)gotoTab('resources');});
}

function build(){
 parseRows();
 $('emLoading').style.display='none';$('emBody').style.display='block';
 const n=E.nat;
 $('emMeta').innerHTML=[[fmt(n.hex_live),'heksagon res 6 ≥'+E.meta.pop_min+' jiwa'],[jt(n.pop),'penduduk (Kontur 2023)'],[fmt(n.active),'SPKLU operasional / '+fmt(n.sites)],[fmt(n.chargers),'charger operasional'],[fmt(n.gi),'gardu induk · '+jt(n.mva)+' MVA'],[E.kabs.length,'kabupaten/kota'],[f1(n.within10)+'%','penduduk ≤10 km dari SPKLU']]
  .map(x=>`<div><div class="n">${x[0]}</div><div class="t">${x[1]}</div></div>`).join('');
 $('emProv').innerHTML='<option value="all">Seluruh Indonesia</option>'+E.provs.map((p,i)=>`<option value="${i}">${esc(p.name)}</option>`).join('');
 fillKab();renderWeights();initMap();note();
 $('emProv').onchange=()=>{S.prov=$('emProv').value;S.kab='all';fillKab();update(true);zoomKab();};
 $('emKab').onchange=()=>{S.kab=$('emKab').value;update(false);zoomKab();};
 $('emMode').querySelectorAll('button').forEach(b=>b.onclick=()=>{$('emMode').querySelectorAll('button').forEach(x=>x.classList.remove('active'));b.classList.add('active');S.mode=b.dataset.m;drawHex(score(scopeRows()),S.prov==='all');});
 $('emCov').querySelectorAll('button').forEach(b=>b.onclick=()=>{$('emCov').querySelectorAll('button').forEach(x=>x.classList.remove('active'));b.classList.add('active');S.cov=b.dataset.c;update(true);});
 $('emLySpklu').onchange=drawOverlays;$('emLyGi').onchange=drawOverlays;
 $('emPreEq').onclick=()=>applyPreset(PRESET.eq);$('emPreCom').onclick=()=>applyPreset(PRESET.com);$('emPreDef').onclick=()=>applyPreset(PRESET.def);
 $('tblEm').querySelectorAll('th').forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(!k)return;if(k===sortK)sortD*=-1;else{sortK=k;sortD=(k==='name'||k==='provn')?1:-1;}renderTable();});
 $('emSearch').oninput=renderTable;$('emCsv').onclick=csv;
 update(true);setTimeout(()=>map.invalidateSize(),150);
 built=true;
}

window.initEquity=async function(){
 if(built){if(map)map.invalidateSize();return;}
 if(window.emLoadingNow)return;window.emLoadingNow=true;
 try{
  if(typeof h3==='undefined')await loadScript('equitymap/vendor/h3-js.umd.js');
  if(!window.EQUITY)await loadScript('equitymap/equity.js');
  E=window.EQUITY;build();
 }catch(e){$('emLoading').innerHTML='<b>Gagal memuat peta ekuitas:</b> '+esc(e.message)+'. Pastikan <code>equitymap/equity.js</code> ada (jalankan <code>python3 equitymap/prepare.py</code>).';}
 finally{window.emLoadingNow=false;}
};
// tautan dalam (#tab=ekuitas) memicu klik tab sebelum skrip ini terurai — inisialisasi bila tab sudah aktif
if(document.querySelector('#p-ekuitas.active'))setTimeout(window.initEquity,60);
})();
