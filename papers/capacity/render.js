
/* ============ PAPER: CAPACITY MAPS AS AN EQUITY INSTRUMENT (CIRED 2027) ============ */
(function(){
 const C=(typeof D!=='undefined'&&D.cap)||null; if(!C) return;
 const $=id=>document.getElementById(id);
 const nf=(v,d=0)=>Number(v).toLocaleString('id-ID',{minimumFractionDigits:d,maximumFractionDigits:d});
 const CELL=C.meta.cell_deg;
 // cells: [lat,lon,h,hraw,kva,n,gi,ev,chg,kwh,q,kab]
 const CL=C.cells.map(a=>({lat:a[0],lon:a[1],h:a[2],hraw:a[3],kva:a[4],n:a[5],gi:a[6],
                           ev:a[7],chg:a[8],kwh:a[9],q:a[10],kab:a[11]}));
 const EVC=CL.filter(c=>c.ev>0), SERVED=CL.filter(c=>c.chg>0);
 const R=C.rules, byKey=k=>R.find(r=>r.key===k);

 /* ---------- angka kunci ---------- */
 $('capFacts').innerHTML=[
  [nf(C.meta.usable),'trafo distribusi layak pakai dari '+nf(C.meta.total)+' catatan survei'],
  [nf(C.meta.ev),'pelanggan EV terdaftar tergeokode'],
  [nf(C.meta.sites_reg||C.meta.sites),'situs SPKLU (636 unit charger) Maret 2026'],
  [C.rho.abs.toFixed(2)+' / '+C.rho.rel.toFixed(2),'ρ energi terhadap headroom absolut / relatif'],
  [C.gap.h_nochg_pct+' %','headroom provinsi di sel tanpa charger'],
  ['+'+Math.round(100*(byKey('dwh').owners/byKey('headroom').owners-1))+' %','pemilik terjangkau: demand-within-headroom vs headroom-only'],
 ].map(f=>`<div class="f"><div class="n">${f[0]}</div><div class="l">${f[1]}</div></div>`).join('');

 const tbl=(id,head,rows)=>{const el=$(id); if(!el)return;
  el.innerHTML='<table><thead><tr>'+head.map(h=>`<th>${h}</th>`).join('')+'</tr></thead><tbody>'+
   rows.map(r=>'<tr>'+r.map(c=>`<td>${c}</td>`).join('')+'</tr>').join('')+'</tbody></table>';};

 tbl('capT1',['Dataset','Records','Period','Key fields'],[
  ['Distribution-transformer load register',`53,797 (${nf(C.meta.usable)} usable)`,'2020–2024','kVA, day/night loading, feeder, GI, MVA and loading of GI, coordinates'],
  ['Public charging sessions','101,020 sessions / 636 chargers / 331 sites','Mar 2026','kWh, duration, revenue, site type'],
  ['Registered EV customers',nf(C.meta.ev)+' geocoded','to Jun 2026','coordinates, connected power'],
  ['Feeder peak-load register (full paper)','2,574 feeders','Apr 2022','GI, feeder, kHA, day/night loading'],
 ]);

 /* ---------- Tabel 2: naskah vs hitung ulang ---------- */
 const P={headroom:[694,15,0,16,'94.4%',0.653],demand:[807,0,2,15,'97.4%',0.611],dwh:[789,0,0,17,'97%',0.600]};
 const rows=[];
 R.forEach(r=>{const p=P[r.key];
  rows.push([`<b>${r.label}</b> <span style="color:var(--mut)">— naskah</span>`,p[0],p[1],p[2],p[3],p[4],p[5].toFixed(3)]);
  rows.push([`<span style="color:var(--mut)">${r.label} — hitung ulang</span>`,r.owners,r.stranded,r.infeas,r.regen,r.cov+'%',r.gini.toFixed(3)]);});
 rows.push(['<b>Baseline (hari ini)</b> — naskah','—','—','—','—','75.5%','0.692']);
 rows.push(['<span style="color:var(--mut)">Baseline — hitung ulang</span>','—','—','—','—',C.baseline.cov+'%',C.baseline.gini.toFixed(3)]);
 tbl('capT2',['Siting rule (50 sites)','Owners','Stranded','Infeas.','Regen.','Cover.','Gini'],rows);

 tbl('capT3',['Angka','Naskah','Hitung ulang','Catatan'],[
  ['Sel 5 km terisi','1.292',nf(C.meta.cells),'titik jangkar grid & saringan bounding box sedikit berbeda'],
  ['Sel dengan pemilik EV','235',nf(C.meta.cells_ev),'idem'],
  ['Sel dengan SPKLU','174',nf(C.meta.cells_chg),'sama'],
  ['Pemilik di sel belum terlayani','901',nf(C.pool.ev),'idem'],
  ['Kuadran permintaan tinggi / headroom rendah','12,8 % pemilik · 7,2 % charger',
   C.quad.HL.evp+' % pemilik · '+C.quad.HL.chgp+' % charger','median dihitung ulang atas 238 sel'],
  ['Gini cakupan antar-kabupaten','0,692 → 0,600',C.baseline.gini.toFixed(3)+' → '+byKey('dwh').gini.toFixed(3),
   'definisi Gini di naskah tidak dirinci; urutan antar-aturan tetap sama'],
  ['Headroom GI, g = 3 %/th','1.912 MVA',nf(C.scen[1].gi)+' MVA','umur survei GI tidak tersedia; dipakai umur median trafo ('+C.meta.med_age+' th)'],
 ]);

 /* ---------- warna ---------- */
 const RAMP=['#0d3b2e','#1b6b4f','#3fa06b','#8fca86','#d9e8a8','#fbe3a0','#f3a25c','#d6443c'];
 const QCOL={HH:'#2e9e5b',HL:'#d6443c',LH:'#3a6ea5',LL:'#9aa7bd'};
 const QLAB={HH:'Permintaan ↑ / headroom ↑',HL:'Permintaan ↑ / headroom ↓',
             LH:'Permintaan ↓ / headroom ↑',LL:'Permintaan ↓ / headroom ↓'};
 const LAYERS={
  h:{lab:'Headroom trafo 2026 (kVA)',get:c=>c.h,rev:true,fmt:v=>nf(v)+' kVA'},
  hrel:{lab:'Headroom relatif (% kapasitas)',get:c=>c.kva?100*c.h/c.kva:0,rev:true,fmt:v=>v.toFixed(1)+' %'},
  gi:{lab:'Headroom Gardu Induk (MVA)',get:c=>c.gi,rev:true,fmt:v=>v.toFixed(1)+' MVA'},
  ev:{lab:'Pemilik EV terdaftar',get:c=>c.ev,rev:false,fmt:v=>nf(v)+' pemilik'},
  kwh:{lab:'Energi SPKLU Maret 2026 (kWh)',get:c=>c.kwh,rev:false,fmt:v=>nf(v)+' kWh'},
  q:{lab:'Kuadran permintaan × headroom',get:c=>c.q,cat:true},
 };
 function breaks(vals){ // kuantil, buang nol supaya skala tidak tertelan sel kosong
  const v=vals.filter(x=>x>0).sort((a,b)=>a-b); if(!v.length) return [0];
  return Array.from({length:7},(_,i)=>v[Math.floor((i+1)/8*v.length)]);
 }
 function colorOf(val,bk,rev){
  let i=0; while(i<bk.length&&val>bk[i]) i++;
  return RAMP[rev?RAMP.length-1-i:i];
 }

 /* ---------- Fig. 1: peta utama ---------- */
 let map,cellLyr,spkluLyr,gapLyr,evLyr,inited=false;
 const show={spklu:true,gap:true,ev:false};

 function drawCells(){
  const key=$('capLayer').value,L=LAYERS[key];
  cellLyr.clearLayers();
  const bk=L.cat?null:breaks(CL.map(L.get));
  CL.forEach(c=>{
   const v=L.get(c);
   if(L.cat&&!v) return;
   const col=L.cat?QCOL[v]:colorOf(v,bk,L.rev);
   const b=[[c.lat-CELL/2,c.lon-CELL/2],[c.lat+CELL/2,c.lon+CELL/2]];
   L2.rectangle(b,{color:col,weight:.4,opacity:.55,fillColor:col,fillOpacity:L.cat?.55:.62})
    .bindPopup(`<b>Sel ${c.lat.toFixed(3)}, ${c.lon.toFixed(3)}</b><br>${c.kab||'—'}<br>`+
      `<hr style="margin:5px 0">Headroom trafo 2026: <b>${nf(c.h)} kVA</b> (tanpa koreksi ${nf(c.hraw)})<br>`+
      `Kapasitas terpasang: ${nf(c.kva)} kVA · ${c.n} trafo<br>`+
      `Headroom relatif: <b>${c.kva?(100*c.h/c.kva).toFixed(1):'—'} %</b><br>`+
      `Headroom GI rata-rata: ${c.gi.toFixed(1)} MVA<br>`+
      `Pemilik EV: <b>${c.ev}</b> · SPKLU: <b>${c.chg}</b> · ${nf(c.kwh)} kWh<br>`+
      (c.q?`Kuadran: <b style="color:${QCOL[c.q]}">${QLAB[c.q]}</b>`:''))
    .addTo(cellLyr);
  });
  // legenda
  let lg='';
  if(L.cat){ lg=Object.keys(QLAB).map(k=>`<span><i style="background:${QCOL[k]}"></i>${QLAB[k]}</span>`).join(''); }
  else{
   const r=L.rev?RAMP.slice().reverse():RAMP;
   lg=`<span>${L.lab}: sedikit <span class="ramp">${r.map(c=>`<span style="background:${c}"></span>`).join('')}</span> banyak</span>`;
   if(L.rev) lg=`<span>${L.lab}: <b>sedikit sisa</b> <span class="ramp">${RAMP.map(c=>`<span style="background:${c}"></span>`).join('')}</span> <b>banyak sisa</b></span>`;
  }
  lg+=`<span><i style="background:#111;border-radius:50%"></i>SPKLU (ukuran = energi)</span>`+
      `<span><i style="background:#d6443c;border:2px solid #7d1f1a"></i>sel rawan tanpa charger</span>`;
  $('capLegend').innerHTML=lg;
 }

 const L2=window.L;
 function initCapMap(){
  if(inited){ map.invalidateSize(); return; }
  inited=true;
  map=L2.map('capMap',{scrollWheelZoom:false}).setView([-6.75,107.4],8);
  L2.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
   {attribution:'© OpenStreetMap © CARTO',maxZoom:16}).addTo(map);
  cellLyr=L2.layerGroup().addTo(map);
  gapLyr=L2.layerGroup(); spkluLyr=L2.layerGroup(); evLyr=L2.layerGroup();

  // sel rawan: permintaan tinggi / headroom rendah, belum ada charger
  CL.filter(c=>c.q==='HL'&&c.chg===0).forEach(c=>{
   L2.rectangle([[c.lat-CELL/2,c.lon-CELL/2],[c.lat+CELL/2,c.lon+CELL/2]],
    {color:'#7d1f1a',weight:2,fill:true,fillColor:'#d6443c',fillOpacity:.25,dashArray:'4 3'})
    .bindPopup(`<b>Sel rawan</b><br>${c.kab||''}<br>${c.ev} pemilik EV · headroom ${nf(c.h)} kVA · belum ada SPKLU`)
    .addTo(gapLyr);
  });
  const mx=Math.max(...C.sites.map(s=>s.kwh))||1;
  C.sites.forEach(s=>{
   L2.circleMarker([s.lat,s.lon],{radius:3+7*Math.sqrt(s.kwh/mx),color:'#0a1733',weight:1,
     fillColor:'#d4af37',fillOpacity:.9})
    .bindPopup(`<b>${s.nm}</b><br>${s.jl} · ${s.kab}<br>${nf(s.kwh)} kWh · ${nf(s.trx)} transaksi (Mar 2026)`)
    .addTo(spkluLyr);
  });
  C.ev.forEach(p=>L2.circleMarker(p,{radius:1.6,color:'#3a6ea5',weight:0,fillOpacity:.5}).addTo(evLyr));

  if(show.spklu) spkluLyr.addTo(map);
  if(show.gap) gapLyr.addTo(map);
  drawCells();
  $('capLayer').onchange=drawCells;
  document.querySelectorAll('#p-capacity [data-caplyr]').forEach(b=>b.onclick=()=>{
   const k=b.dataset.caplyr; show[k]=!show[k]; b.classList.toggle('active',show[k]);
   const lyr={spklu:spkluLyr,gap:gapLyr,ev:evLyr}[k];
   show[k]?lyr.addTo(map):map.removeLayer(lyr);
  });
  initRuleMap();
 }

 /* ---------- Fig. 2: kuadran ---------- */
 let quadCh,ruleCh,discCh,auditCh,scenCh;
 function initQuad(){
  if(quadCh) return;
  const ds=Object.keys(QCOL).map(q=>({label:QLAB[q],
    data:EVC.filter(c=>c.q===q).map(c=>({x:Math.max(c.h,1),y:c.ev,r:c.chg?4+Math.sqrt(c.kwh)/40:3,c:c})),
    backgroundColor:QCOL[q]+'cc',borderColor:QCOL[q],pointRadius:ctx=>ctx.raw.r,
    pointStyle:ctx=>ctx.raw.c.chg?'rectRot':'circle'}));
  quadCh=new Chart($('capQuad'),{type:'scatter',data:{datasets:ds},options:{responsive:true,
   plugins:{legend:{labels:{boxWidth:9,font:{size:10}}},tooltip:{callbacks:{label:i=>{
     const c=i.raw.c; return `${c.kab||''} — ${c.ev} pemilik · ${nf(c.h)} kVA · ${c.chg} SPKLU`;}}}},
   scales:{x:{type:'logarithmic',title:{display:true,text:'Headroom trafo 2026 (kVA, log)',font:{size:10}},
              ticks:{font:{size:9}}},
           y:{type:'logarithmic',title:{display:true,text:'Pemilik EV terdaftar (log)',font:{size:10}},
              ticks:{font:{size:9}}}}},
   plugins:[{id:'med',afterDraw(ch){const{ctx,chartArea:a,scales:s}=ch;ctx.save();
     ctx.setLineDash([5,4]);ctx.strokeStyle='#9aa7bd';ctx.lineWidth=1;
     const x=s.x.getPixelForValue(C.med.h),y=s.y.getPixelForValue(C.med.ev);
     ctx.beginPath();ctx.moveTo(x,a.top);ctx.lineTo(x,a.bottom);ctx.moveTo(a.left,y);ctx.lineTo(a.right,y);
     ctx.stroke();ctx.restore();}}]});

  const Q=['HH','HL','LH','LL'];
  new Chart($('capQuadBar'),{type:'bar',data:{labels:Q.map(q=>QLAB[q]),datasets:[
    {label:'% pemilik EV',data:Q.map(q=>C.quad[q].evp),backgroundColor:'#3a6ea5'},
    {label:'% charger',data:Q.map(q=>C.quad[q].chgp),backgroundColor:'#d4af37'}]},
   options:{indexAxis:'y',responsive:true,plugins:{legend:{labels:{boxWidth:9,font:{size:10}}}},
    scales:{x:{ticks:{font:{size:9},callback:v=>v+' %'}},y:{ticks:{font:{size:9.5}}}}}});

  $('capQuadBox').innerHTML=Q.map(q=>{const v=C.quad[q];
   return `<div class="qb${q==='HL'?' gapq':''}"><b style="color:${QCOL[q]}">${QLAB[q]}</b>
    <div class="s">${v.cells} sel · <b>${v.evp} %</b> pemilik EV · <b>${v.chgp} %</b> charger</div></div>`;}).join('')
   +`<div class="qb gapq" style="grid-column:1/-1"><b>Celah utama</b><div class="s">${C.gap.cells} sel
     permintaan-tinggi/headroom-rendah sama sekali belum punya SPKLU — ${C.gap.ev} pemilik EV.
     ${C.gap.h_nochg_pct} % headroom provinsi dan ${C.gap.ev_nochg_pct} % pemilik EV berada di sel tanpa charger.</div></div>`;
 }

 /* ---------- Fig. 3: aturan penempatan ---------- */
 let rmap,rsel,rlayer,rbase,rspklu,rinit=false,active='dwh';
 function initRuleMap(){
  if(rinit){rmap.invalidateSize();return;} rinit=true;
  rmap=L2.map('capRuleMap',{scrollWheelZoom:false}).setView([-6.75,107.4],8);
  L2.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
   {attribution:'© OpenStreetMap © CARTO',maxZoom:16}).addTo(rmap);
  rbase=L2.layerGroup().addTo(rmap); rlayer=L2.layerGroup().addTo(rmap);
  rspklu=L2.layerGroup().addTo(rmap);
  CL.filter(c=>c.ev>0&&c.chg===0).forEach(c=>
   L2.circleMarker([c.lat,c.lon],{radius:2.5,color:'#9aa7bd',weight:0,fillOpacity:.7})
    .bindPopup(`kandidat · ${c.ev} pemilik · ${nf(c.h)} kVA`).addTo(rbase));
  C.sites.forEach(s=>L2.circleMarker([s.lat,s.lon],{radius:2,color:'#2e9e5b',weight:0,fillOpacity:.55}).addTo(rspklu));
  drawRule();
 }
 function drawRule(){
  if(!rinit) return;
  const r=byKey(active); rlayer.clearLayers();
  const mx=Math.max(...r.sel.map(s=>s[2]))||1;
  r.sel.forEach(s=>L2.circleMarker([s[0],s[1]],
   {radius:4+9*Math.sqrt(s[2]/mx),color:'#7d1f1a',weight:1.2,fillColor:'#d6443c',fillOpacity:.75})
   .bindPopup(`<b>Situs terpilih — ${r.label}</b><br>${s[2]} pemilik EV<br>headroom ${nf(s[3])} kVA`
     +(s[3]<C.meta.feasible?'<br><b style="color:#d6443c">di bawah ambang kelayakan 240 kVA</b>':''))
   .addTo(rlayer));
  const st=`<div class="kpis" style="margin:0">
   ${[['Pemilik EV terjangkau',nf(r.owners),'dari '+nf(C.pool.ev)+' di sel belum terlayani'],
      ['Situs terlantar',r.stranded,'di sel permintaan di bawah median kandidat'],
      ['Situs tak layak',r.infeas,'headroom < '+nf(C.meta.feasible)+' kVA'],
      ['Kabupaten tersentuh',r.regen,'sebaran geografis'],
      ['Cakupan pemilik',r.cov+' %','baseline '+C.baseline.cov+' %'],
      ['Gini antar-kabupaten',r.gini.toFixed(3),'baseline '+C.baseline.gini.toFixed(3)]]
    .map(k=>`<div class="kpi"><div class="l">${k[0]}</div><div class="v">${k[1]}</div><div class="s">${k[2]}</div></div>`).join('')}
   </div><div class="cap" style="margin-top:10px">Sensitivitas <i>demand-within-headroom</i> terhadap asumsi pertumbuhan:
   ${C.sens.map(s=>`${s.g} %/th → <b>${s.owners}</b> pemilik`).join(' · ')}.</div>`;
  $('capRuleStat').innerHTML=st;
 }
 function initRuleChart(){
  if(ruleCh) return;
  $('capRuleBtns').innerHTML=R.map(r=>
   `<button class="mode-btn${r.key===active?' active':''}" data-caprule="${r.key}">${r.label}</button>`).join('');
  document.querySelectorAll('#capRuleBtns [data-caprule]').forEach(b=>b.onclick=()=>{
   active=b.dataset.caprule;
   document.querySelectorAll('#capRuleBtns [data-caprule]').forEach(x=>x.classList.toggle('active',x===b));
   drawRule();});
  ruleCh=new Chart($('capRuleChart'),{data:{labels:R.map(r=>r.label),datasets:[
   {type:'bar',label:'Pemilik EV terjangkau',data:R.map(r=>r.owners),backgroundColor:'#3a6ea5',yAxisID:'y'},
   {type:'bar',label:'Situs terlantar / tak layak',data:R.map(r=>r.stranded+r.infeas),backgroundColor:'#d6443c',yAxisID:'y'},
   {type:'line',label:'Gini cakupan antar-kabupaten',data:R.map(r=>r.gini),borderColor:'#d4af37',
    backgroundColor:'#d4af37',yAxisID:'y1',tension:.25,pointRadius:5}]},
   options:{responsive:true,plugins:{legend:{labels:{boxWidth:9,font:{size:10}}},
    tooltip:{callbacks:{afterBody:i=>{const r=R[i[0].dataIndex];
      return `terlantar ${r.stranded} · tak layak ${r.infeas} · ${r.regen} kabupaten · cakupan ${r.cov} %`;}}}},
    scales:{y:{title:{display:true,text:'pemilik / situs',font:{size:10}},ticks:{font:{size:9}}},
            y1:{position:'right',min:0,max:.8,grid:{drawOnChartArea:false},
                title:{display:true,text:'Gini',font:{size:10}},ticks:{font:{size:9}}},
            x:{ticks:{font:{size:9.5}}}}}});
 }

 /* ---------- 5.4 ketidaksesuaian dua tingkat ---------- */
 function initDisc(){
  if(discCh) return;
  const med=a=>{const v=a.slice().sort((x,y)=>x-y);return v[Math.floor(v.length/2)];};
  const mh=med(SERVED.map(c=>c.kva?c.h/c.kva:0)), mg=med(SERVED.map(c=>c.gi));
  let tl=0,lt=0,tt=0,ll=0;
  SERVED.forEach(c=>{const t=(c.kva?c.h/c.kva:0)>=mh,g=c.gi>=mg;
   if(t&&g)tt++;else if(!t&&!g)ll++;else if(!t&&g)lt++;else tl++;});
  discCh=new Chart($('capDisc'),{type:'bar',data:{
   labels:['Trafo longgar · GI longgar','Trafo sempit · GI longgar','Trafo longgar · GI sempit','Trafo sempit · GI sempit'],
   datasets:[{data:[tt,lt,tl,ll],backgroundColor:['#2e9e5b','#e0a52b','#e8742c','#d6443c']}]},
   options:{indexAxis:'y',responsive:true,plugins:{legend:{display:false}},
    scales:{x:{title:{display:true,text:'jumlah sel terlayani',font:{size:10}},ticks:{font:{size:9}}},
            y:{ticks:{font:{size:9.5}}}}}});
  const disc=lt+tl;
  $('capDiscNote').innerHTML=`Dari ${SERVED.length} sel yang sudah punya SPKLU, <b>${disc}
   (${(100*disc/SERVED.length).toFixed(0)} %)</b> memberi sinyal berlawanan antara tingkat trafo dan tingkat
   Gardu Induk — ${lt} sel sempit di trafo tetapi longgar di GI, ${tl} sebaliknya. Peta satu tingkat akan
   menyesatkan pada separuh lokasi. (Naskah: 42 dan 46 sel, 51 %.)`;
 }

 /* ---------- 5.5 audit & skenario ---------- */
 function initAudit(){
  if(auditCh) return;
  const A=C.audit, lab=[['gi','tidak tertaut Gardu Induk'],['koord','koordinat survei > 1 km dari register aset'],
   ['beban','tanpa pembacaan beban'],['kva','tanpa kapasitas terpasang'],['geo','koordinat tidak valid'],
   ['pii','memuat nama petugas (harus dihapus)']].filter(l=>A[l[0]]!==undefined);
  auditCh=new Chart($('capAudit'),{type:'bar',data:{labels:lab.map(l=>l[1]),
   datasets:[{data:lab.map(l=>A[l[0]]),backgroundColor:lab.map(l=>l[0]==='pii'?'#67748c':'#d6443c')}]},
   options:{indexAxis:'y',responsive:true,plugins:{legend:{display:false},
    tooltip:{callbacks:{label:i=>i.raw+' % ('+nf(C.audit_n[lab[i.dataIndex][0]])+' catatan)'}}},
    scales:{x:{max:100,ticks:{font:{size:9},callback:v=>v+' %'}},y:{ticks:{font:{size:9.5}}}}}});

  scenCh=new Chart($('capScen'),{data:{labels:C.scen.map(s=>s.g?s.g+' %/th':'apa adanya'),
   datasets:[{type:'bar',label:'Headroom trafo (MVA)',data:C.scen.map(s=>s.trafo),backgroundColor:'#3a6ea5'},
    {type:'bar',label:'Headroom Gardu Induk (MVA)',data:C.scen.map(s=>s.gi),backgroundColor:'#d4af37'},
    {type:'line',label:'Trafo melewati batas 80 %',data:C.scen.map(s=>s.over),borderColor:'#d6443c',
     backgroundColor:'#d6443c',yAxisID:'y1',tension:.25,pointRadius:4}]},
   options:{responsive:true,plugins:{legend:{labels:{boxWidth:9,font:{size:10}}}},
    scales:{y:{title:{display:true,text:'MVA',font:{size:10}},ticks:{font:{size:9}}},
     y1:{position:'right',grid:{drawOnChartArea:false},title:{display:true,text:'jumlah trafo',font:{size:10}},
         ticks:{font:{size:9}}},x:{ticks:{font:{size:9.5}}}}}});
 }

 /* ---------- referensi ---------- */
 const REFS=[
  '[1] Directive (EU) 2019/944 on common rules for the internal market for electricity, Art. 32; Regulation (EU) 2024/1747 amending Regulation (EU) 2019/943 (transparency of available hosting capacity).',
  '[2] E.DSO, "Technology Report on Grid Hosting Capacity Maps," E.DSO Technology & Knowledge Sharing Committee, Brussels (accessed Sep. 2026).',
  '[3] ICCT, "Mapping the charge: why grid data is key to electrifying road freight," International Council on Clean Transportation, Nov. 2025.',
  '[4] O. Lennerhag, S. Ackeby, M. H. J. Bollen, G. Foskolos and T. Gafurov, "Using measurements to increase the accuracy of hosting capacity calculations," CIRED – Open Access Proc. J., vol. 2017, no. 1, pp. 2041–2044, 2017.',
  '[5] C.-W. Hsu and K. Fingerman, "Public electric vehicle charger access disparities across race and income in California," Transport Policy, vol. 100, pp. 59–67, 2021.',
  '[6] B. K. Sovacool and M. H. Dworkin, "Energy justice: Conceptual insights and practical applications," Applied Energy, vol. 142, pp. 435–444, 2015.',
  '[7] Regulation (EU) 2023/1804 on the deployment of alternative fuels infrastructure (AFIR); Peraturan Presiden No. 55/2019 (Indonesia).',
  '[8] S. M. Ismael, S. H. E. Abdel Aleem, A. Y. Abdelaziz and A. F. Zobaa, "State-of-the-art of hosting capacity in modern power systems with distributed generation," Renewable Energy, vol. 130, pp. 1002–1020, 2019.',
  '[9] G. Carlton and S. Sultana, "Electric vehicle charging station accessibility and land use clustering: A case study of the Chicago region," J. Urban Mobility, vol. 2, 100019, 2022.',
  '[10] A. K. Karmaker, K. Prakash, M. N. I. Siddique, M. A. Hossain and H. Pota, "Electric vehicle hosting capacity analysis: Challenges and solutions," Renewable and Sustainable Energy Reviews, vol. 189, 113916, 2024.',
  '[11] M. Muratori, "Impact of uncoordinated plug-in electric vehicle charging on residential power demand," Nature Energy, vol. 3, pp. 193–201, 2018.',
  '[12] W. Dai, C. Wang, H. H. Goh, J. Zhao and J. Jian, "Hosting capacity evaluation method for power distribution networks integrated with electric vehicles," J. Modern Power Systems and Clean Energy, vol. 11, no. 5, pp. 1564–1575, 2023.',
  '[13] PT PLN (Persero) UID Jawa Barat, 2025 performance release: 63,503 GWh sales (+3.0 %), 35,686 MVA connected (+5.9 %), Feb. 2026.',
  '[14] Ember, "Transparent grids for all: hosting capacity maps," Jul. 2024.',
 ];
 $('capRefs').innerHTML=REFS.map(r=>`<div>${r}</div>`).join('');

 const lnk=$('capToLib');
 if(lnk) lnk.onclick=e=>{e.preventDefault();
  const t=document.querySelector('.tab[data-p="library"]'); if(t){t.click();
   setTimeout(()=>{const b=document.querySelector('[data-libopen="cired2027"]'); if(b) b.click();},120);}};

 window.initCapacity=function(){ initCapMap(); initQuad(); initRuleChart(); initDisc(); initAudit(); };
})();
