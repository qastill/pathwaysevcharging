
/* ============ EV × JARINGAN (grid readiness) ============ */
(function(){
 const X=D.grid; if(!X) return;
 const M=X.meta, CAT=["OVERLOAD (>=100%)","WASPADA (80-100%)","NORMAL (30-80%)","UNDERLOAD (<30%)"];
 const CATLAB=["Overload ≥100%","Waspada 80–100%","Normal 30–80%","Underload <30%"];
 const CATCOL=["#d6443c","#e8742c","#2e9e5b","#9fb2cd"];
 const p1=(a,b)=>b?(100*a/b):0, f1=v=>(Math.round(v*10)/10).toFixed(1).replace('.',',');
 const fmt=n=>n==null?'–':Math.round(n).toLocaleString('id-ID');
 const evHot=X.evRisk, evHotP=f1(p1(evHot,M.nEVjoin));
 const hotAll=(X.catAll[CAT[0]]||0)+(X.catAll[CAT[1]]||0);
 const noRoom=X.hostCap["0"]||0;

 $('gxInsight').innerHTML=`<b>Temuan utama — EV bertemu jaringan:</b> dari <b>${fmt(M.nEVjoin)}</b> pelanggan EV rumah yang berhasil dipetakan ke gardu terdekat (≤1 km), <b>${fmt(evHot)} (${evHotP}%)</b> bertumpu pada gardu yang <b>sudah ≥80%</b> terbebani. Secara agregat Jawa Barat masih longgar — median beban gardu <b>${M.medPb}%</b> dan headroom aman <b>${fmt(M.headMVA)} MVA</b> — <b>tetapi headroom tidak bisa dipindahkan</b>: <b>${fmt(noRoom)} gardu (${f1(p1(noRoom,M.nGardu))}%)</b> tidak sanggup menerima satu charger 7,7 kVA pun (pada keserempakan 0,6) tanpa melewati batas aman 80%. Masalah EV di Jabar bukan kekurangan kapasitas total, melainkan <b>ketidakcocokan lokasi antara kantong adopsi EV dan kantong kapasitas jaringan</b>.`;

 $('gxKpis').innerHTML=[
  ["Gardu dianalisis",fmt(M.nGardu),"koordinat valid, dari "+fmt(M.nGarduRaw)+" baris"],
  ["Gardu tertekan ≥80%",fmt(hotAll)+" ("+f1(p1(hotAll,M.nGardu))+"%)",fmt(X.catAll[CAT[0]])+" sudah overload"],
  ["EV di gardu tertekan",fmt(evHot)+" ("+evHotP+"%)","dari "+fmt(M.nEVjoin)+" pelanggan ter-join"],
  ["SPKLU di gardu tertekan",fmt(X.spRisk)+" ("+f1(p1(X.spRisk,M.nLoc))+"%)","dari "+fmt(M.nLoc)+" situs · "+fmt(M.spkw)+" kW"],
  ["Headroom aman",fmt(M.headMVA)+" MVA","batas 80% · total "+fmt(M.totMVA)+" MVA"],
  ["Gardu tanpa ruang EV",fmt(noRoom)+" ("+f1(p1(noRoom,M.nGardu))+"%)","tak muat 1 charger 7,7 kVA @CF 0,6"],
 ].map(x=>`<div class="kpi"><div class="l">${x[0]}</div><div class="v">${x[1]}</div><div class="s">${x[2]}</div></div>`).join('');

 // --- kategori gardu: Jabar vs EV vs SPKLU ---
 const sets=[["Semua gardu Jabar",X.catAll,M.nGardu],["Gardu penyuplai EV",X.catEV,M.nEVjoin],["Gardu sekitar SPKLU",X.catSP,M.nLoc]];
 if(C.cGxCat)C.cGxCat.destroy();
 C.cGxCat=new Chart($('cGxCat'),{type:'bar',data:{labels:sets.map(s=>s[0]),
   datasets:CAT.map((c,i)=>({label:CATLAB[i],data:sets.map(s=>+f1(p1(s[1][c]||0,s[2]))),backgroundColor:CATCOL[i],borderRadius:3}))},
  options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
   plugins:{legend:{position:'bottom',labels:{font:{size:10.5},boxWidth:12}},
    tooltip:{callbacks:{label:c=>c.dataset.label+': '+c.raw+'%'}}},
   scales:{x:{stacked:true,max:100,grid:{color:'#eef1f6'},ticks:{callback:v=>v+'%'}},y:{stacked:true,ticks:{font:{size:10.5}},grid:{display:false}}}}});
 $('cGxCat').parentElement.style.height='300px';
 const dEV=p1(X.catEV[CAT[0]]+X.catEV[CAT[1]],M.nEVjoin), dAll=p1(hotAll,M.nGardu);
 $('gxCatNote').innerHTML=`<b>Kabar baik yang menipu.</b> Pelanggan EV justru <b>sedikit lebih jarang</b> berada di gardu tertekan (<b>${f1(dEV)}%</b>) dibanding rata-rata gardu Jabar (<b>${f1(dAll)}%</b>) — masuk akal, karena adopsi EV terkonsentrasi di perumahan baru Bodebek yang jaringannya relatif muda. <b>Tetapi</b> ${f1(p1(X.catSP[CAT[0]]+X.catSP[CAT[1]],M.nLoc))}% situs SPKLU berada di gardu tertekan, dan yang penting bukan rata-rata melainkan <b>ekornya</b>: ${fmt(evHot)} rumah EV sudah berada di jaringan yang tidak punya cadangan.`;

 // --- diurnal ---
 const dd=X.diurnal;
 if(C.cGxDiurnal)C.cGxDiurnal.destroy();
 C.cGxDiurnal=new Chart($('cGxDiurnal'),{type:'bar',data:{labels:['Siang (pengukuran ~10–14)','Malam (pengukuran ~18–22)'],
   datasets:[{label:'Semua gardu Jabar',data:[dd.allSiang,dd.allMalam],backgroundColor:'#9fb2cd',borderRadius:5},
             {label:'Gardu penyuplai EV',data:[dd.evSiang,dd.evMalam],backgroundColor:GOLD,borderRadius:5}]},
  options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{font:{size:11},boxWidth:12}},
   tooltip:{callbacks:{label:c=>c.dataset.label+': '+c.raw+'%'}}},
   scales:{y:{beginAtZero:true,grid:{color:'#eef1f6'},ticks:{callback:v=>v+'%'}},x:{grid:{display:false},ticks:{font:{size:10.5}}}}}});
 $('cGxDiurnal').parentElement.style.height='300px';
 $('gxDiuNote').innerHTML=`<b>Ini inti persoalannya.</b> Gardu penyuplai EV naik dari <b>${dd.evSiang}%</b> (siang) ke <b>${dd.evMalam}%</b> (malam) — lonjakan <b>+${f1(dd.evMalam-dd.evSiang)} poin</b>. Pengisian mobil listrik di rumah hampir seluruhnya terjadi malam hari, yaitu <b>tepat di puncak beban rumah tangga</b>. Beban EV karena itu bukan beban tambahan yang netral: ia menumpuk di jam yang sudah paling sesak. Tanpa insentif tarif malam-dalam / <i>smart charging</i>, setiap EV baru menambah beban pada titik tersempit kurva harian.`;

 // --- skenario ---
 const S=X.scen, slab=S.map(s=>'CF '+s.cf.toFixed(2).replace('.',',')+(s.cf===1?' (serentak)':s.cf===0.6?' (realistis)':' (smart charging)'));
 if(C.cGxScen)C.cGxScen.destroy();
 C.cGxScen=new Chart($('cGxScen'),{type:'bar',data:{labels:slab,
   datasets:[{label:'Sudah overload sebelum EV',data:S.map(s=>s.already),backgroundColor:'#8a1f1a',borderRadius:4},
             {label:'Jadi overload karena EV',data:S.map(s=>s.newOver),backgroundColor:'#d6443c',borderRadius:4},
             {label:'Naik ke waspada karena EV',data:S.map(s=>s.newHot),backgroundColor:'#e8742c',borderRadius:4}]},
  options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{font:{size:10.5},boxWidth:12}}},
   scales:{x:{stacked:true,grid:{display:false},ticks:{font:{size:10}}},y:{stacked:true,beginAtZero:true,grid:{color:'#eef1f6'},title:{display:true,text:'jumlah gardu',font:{size:10}}}}}});
 $('cGxScen').parentElement.style.height='300px';
 const s6=S[1],s10=S[0],s35=S[2];
 $('gxScenNote').innerHTML=`Dengan populasi EV yang <b>sudah terpasang hari ini</b>, skenario realistis (faktor keserempakan 0,6) membuat <b>${s6.newOver} gardu jatuh ke overload</b> dan <b>${s6.newHot} gardu naik ke status waspada</b>. Pada kondisi terburuk (semua charger menyala bersamaan) angkanya menjadi <b>${s10.newOver}</b> dan <b>${s10.newHot}</b>. <i>Smart charging</i> yang menekan keserempakan ke 0,35 memangkasnya ke <b>${s35.newOver}</b> dan <b>${s35.newHot}</b> — artinya <b>${s10.newOver-s35.newOver} penggantian trafo bisa dihindari lewat pengaturan waktu isi, bukan belanja modal</b>. Ini rasio manfaat-biaya yang sangat jarang muncul di perencanaan distribusi.`;

 // --- host capacity ---
 const HC=X.hostCap, hlab=['0 EV','1–2 EV','3–4 EV','5–9 EV','10–19 EV','≥20 EV'];
 const hval=[0,1,2,3,4,5].map(i=>HC[i]||0);
 if(C.cGxHost)C.cGxHost.destroy();
 C.cGxHost=new Chart($('cGxHost'),{type:'bar',data:{labels:hlab,datasets:[{data:hval,
   backgroundColor:['#d6443c','#e8742c','#e0a52b','#7fae6b','#2e9e5b','#16305f'],borderRadius:5}]},
  options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},
   tooltip:{callbacks:{label:c=>fmt(c.raw)+' gardu ('+f1(p1(c.raw,M.nGardu))+'%)'}}},
   scales:{y:{beginAtZero:true,grid:{color:'#eef1f6'},title:{display:true,text:'jumlah gardu',font:{size:10}}},x:{grid:{display:false}}}}});
 $('cGxHost').parentElement.style.height='300px';
 const big=(HC[4]||0)+(HC[5]||0);
 $('gxHostNote').innerHTML=`Distribusi daya tampung sangat <b>timpang</b>. <b>${fmt(noRoom)} gardu (${f1(p1(noRoom,M.nGardu))}%)</b> tidak punya ruang untuk satu charger pun, sementara <b>${fmt(big)} gardu (${f1(p1(big,M.nGardu))}%)</b> sanggup menampung 10 EV atau lebih. Secara total headroom aman Jabar setara <b>~${fmt(M.headMVA*1000/(7.7*0.6))} charger rumah</b> — jauh di atas proyeksi kebutuhan — namun angka agregat itu <b>menyesatkan bagi perencanaan</b>: yang mengikat adalah trafo di depan rumah pelanggan, bukan neraca provinsi. Karena itu skrining kelayakan EV harus dilakukan <b>per gardu</b>, bukan per UP3.`;

 // --- peta ---
 let gxMapInit=false;
 window.initGx=function(){
  if(gxMapInit){if(window.gxMap)window.gxMap.invalidateSize();return;}
  gxMapInit=true;
  const map=L.map('gxMap',{scrollWheelZoom:false}).setView([-6.75,107.4],9);
  window.gxMap=map;
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{attribution:'© OpenStreetMap, © CARTO',maxZoom:18}).addTo(map);
  const lHot=L.layerGroup(), lEV=L.layerGroup(), lSP=L.layerGroup();
  X.mapHot.forEach(h=>L.circleMarker([h[0],h[1]],{radius:h[2]>=100?3.4:2.4,color:h[2]>=100?'#8a1f1a':'#d6443c',
    weight:0,fillOpacity:h[2]>=100?.75:.5}).bindPopup(`<b>Gardu ${h[3]} kVA</b><br>Beban puncak: <b>${h[2]}%</b><br>${h[2]>=100?'⛔ Overload':'⚠️ Waspada'}`).addTo(lHot));
  X.mapEV.forEach(e=>L.circleMarker([e[0],e[1]],{radius:e[2]?3.4:2.2,color:e[2]===1?'#8a1f1a':e[2]===2?'#e8742c':'#3a6ea5',
    weight:0,fillOpacity:e[2]?.85:.55}).bindPopup('Pelanggan EV rumah<br>'+(e[2]===1?'⛔ gardu terdekat <b>overload</b>':e[2]===2?'⚠️ gardu terdekat <b>waspada</b>':'✅ gardu terdekat normal')).addTo(lEV));
  X.mapSP.forEach(s=>L.circleMarker([s[0],s[1]],{radius:Math.min(9,3+Math.sqrt(s[2])/4),color:'#8a6b12',weight:1,
    fillColor:'#d4af37',fillOpacity:.8}).bindPopup('<b>Situs SPKLU</b><br>Kapasitas terpasang: <b>'+s[2]+' kW</b>').addTo(lSP));
  lHot.addTo(map); lEV.addTo(map); lSP.addTo(map);
  const layers={'Gardu ≥80%':lHot,'Pelanggan EV':lEV,'Situs SPKLU':lSP};
  $('gxToolbar').innerHTML=Object.keys(layers).map(k=>`<button class="mode-btn" data-l="${k}" style="border-color:var(--navy);color:var(--navy)">✓ ${k}</button>`).join('');
  $('gxToolbar').querySelectorAll('.mode-btn').forEach(b=>b.onclick=()=>{
    const g=layers[b.dataset.l], on=map.hasLayer(g);
    if(on){map.removeLayer(g);b.textContent='  '+b.dataset.l;b.style.color='var(--mut)';b.style.borderColor='var(--line)';}
    else{map.addLayer(g);b.textContent='✓ '+b.dataset.l;b.style.color='var(--navy)';b.style.borderColor='var(--navy)';}});
  setTimeout(()=>map.invalidateSize(),120);
 };
 const ed=X.evSpDist;
 $('gxMapNote').innerHTML=`Peta ini menyatukan tiga lapisan yang selama ini dianalisis terpisah. Pola yang muncul: <b>koridor Bodebek–Bekasi</b> memusatkan hampir seluruh titik biru (pelanggan EV) sementara <b>koridor Pantura Cirebon–Indramayu</b> memusatkan titik merah (gardu tertekan) hampir tanpa EV. Keduanya menuntut kebijakan yang berlawanan: Bodebek butuh <b>manajemen beban & percepatan SPKLU</b>, Pantura butuh <b>rehabilitasi jaringan lebih dulu</b> sebelum EV masuk. Sebagai konteks perilaku: median jarak pelanggan EV ke SPKLU terdekat hanya <b>${ed.med} km</b> dan <b>${f1(p1(ed.w5,M.nEVjoin))}%</b> berada dalam 5 km — pemilik EV Jabar praktis <b>tidak kekurangan SPKLU</b>; mereka memilih mengisi di rumah, sehingga tekanan jatuh ke jaringan tegangan rendah, bukan ke SPKLU.`;

 // --- kuadran ---
 const U=X.up3, mxEV=Math.max(...U.map(u=>u.evPer1k)), medEV=[...U.map(u=>u.evPer1k)].sort((a,b)=>a-b)[Math.floor(U.length/2)];
 const medSc=[...U.map(u=>u.score)].sort((a,b)=>a-b)[Math.floor(U.length/2)];
 if(C.cGxQuad)C.cGxQuad.destroy();
 C.cGxQuad=new Chart($('cGxQuad'),{type:'bubble',data:{datasets:[{
   data:U.map(u=>({x:u.evPer1k,y:u.score,r:Math.max(5,Math.sqrt(u.nSPKLU)*2.4),nm:u.up3,sp:u.nSPKLU,ev:u.nEV})),
   backgroundColor:U.map(u=>u.score>=medSc?(u.evPer1k>=medEV?'rgba(46,158,91,.68)':'rgba(58,110,165,.6)')
                                          :(u.evPer1k>=medEV?'rgba(214,68,60,.7)':'rgba(224,165,43,.62)')),
   borderColor:'#fff',borderWidth:1.2}]},
  options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},
   tooltip:{callbacks:{label:c=>{const d=c.raw;return [d.nm,'Skor kesiapan: '+f1(d.y),'EV per 1.000 gardu: '+f1(d.x),'Situs SPKLU: '+d.sp,'Pelanggan EV: '+fmt(d.ev)];}}}},
   scales:{x:{title:{display:true,text:'Adopsi EV — pelanggan per 1.000 gardu →',font:{size:11}},grid:{color:'#eef1f6'},beginAtZero:true},
           y:{title:{display:true,text:'Skor kesiapan jaringan →',font:{size:11}},grid:{color:'#eef1f6'},min:20,max:100}}}});
 $('cGxQuad').parentElement.style.height='430px';
 const hi=U.filter(u=>u.evPer1k>=medEV&&u.score<medSc).map(u=>u.up3);
 const lo=U.filter(u=>u.evPer1k<medEV&&u.score<medSc).map(u=>u.up3);
 const rd=U.filter(u=>u.evPer1k<medEV&&u.score>=medSc).map(u=>u.up3);
 const sync=U.filter(u=>u.evPer1k>=medEV&&u.score>=medSc);
 const expo=[...U].sort((a,b)=>b.nEVhot-a.nEVhot);
 const near=[...sync].sort((a,b)=>a.score-b.score).slice(0,2).map(u=>u.up3);
 $('gxQuadNote').innerHTML=`<b>Empat kuadran, empat kebijakan berbeda.</b><br>
 <span style="color:#2e9e5b">■</span> <b>Sinkron</b> (adopsi tinggi, jaringan siap): ${U.filter(u=>u.evPer1k>=medEV&&u.score>=medSc).map(u=>u.up3).join(', ')} — pertumbuhan EV bisa dilanjutkan tanpa hambatan jaringan.<br>
 <span style="color:#d6443c">■</span> <b>Tertekan</b> (adopsi tinggi, jaringan lemah): ${hi.length?'<b>'+hi.join(', ')+'</b> — prioritas nomor satu untuk uprating trafo &amp; manajemen beban malam.':'<b>kosong — dan ini temuan yang melegakan.</b> Tidak ada satu pun UP3 yang menggabungkan adopsi EV tinggi dengan jaringan lemah; adopsi EV Jabar sejauh ini justru tumbuh di wilayah berjaringan relatif sehat. Yang paling mendekati batas adalah <b>'+near.join(' dan ')+'</b>, sehingga keduanya layak dipantau lebih dulu bila laju adopsi berlanjut.'}<br>
 <span style="color:#3a6ea5">■</span> <b>Cadangan menganggur</b> (adopsi rendah, jaringan siap): ${rd.join(', ')||'—'} — kapasitas tersedia namun permintaan belum datang; sasaran alami perluasan SPKLU & insentif adopsi.<br>
 <span style="color:#e0a52b">■</span> <b>Rawan ganda</b> (adopsi rendah, jaringan lemah): <b>${lo.join(', ')||'—'}</b> — dipimpin ${lo.slice(-2).join(' dan ')}. Jaringan di sini sudah bermasalah <b>sebelum</b> EV tiba, sehingga setiap program EV <b>harus didahului rehabilitasi</b>, bukan mengikutinya.`;

 // --- tabel UP3 ---
 const pill=(v,g,y)=>`<span class="pill" style="background:${v>=g?'#2e9e5b':v>=y?'#e0a52b':'#d6443c'}">${f1(v)}</span>`;
 $('tGxUp3').innerHTML=`<thead><tr><th style="text-align:left">UP3</th><th>Skor kesiapan</th><th>Gardu</th><th>% siap ≥5 EV</th><th>% ≥80%</th><th>% overload</th><th>kVA headroom /gardu</th><th>% unbalance</th><th>EV /1.000 gardu</th><th>EV di gardu ≥80%</th><th>Situs SPKLU</th></tr></thead><tbody>`+
  U.map(u=>`<tr><td style="text-align:left;font-weight:600">${u.up3}</td><td style="text-align:center">${pill(u.score,70,55)}</td>
   <td style="text-align:right">${fmt(u.n)}</td><td style="text-align:right">${f1(u.pctReady)}%</td>
   <td style="text-align:right;color:${u.pctHot>=20?'#d6443c':'inherit'};font-weight:${u.pctHot>=20?700:400}">${f1(u.pctHot)}%</td>
   <td style="text-align:right;color:${u.pctOver>=5?'#d6443c':'inherit'};font-weight:${u.pctOver>=5?700:400}">${f1(u.pctOver)}%</td>
   <td style="text-align:right">${f1(u.headPerGardu)}</td><td style="text-align:right">${f1(u.unb)}%</td>
   <td style="text-align:right;font-weight:600">${f1(u.evPer1k)}</td>
   <td style="text-align:right;color:${u.pctEVhot>=20?'#d6443c':'inherit'};font-weight:${u.pctEVhot>=20?700:400}">${u.nEVhot} <span style="color:var(--mut);font-size:11px">(${f1(u.pctEVhot)}%)</span></td>
   <td style="text-align:right">${u.nSPKLU}</td></tr>`).join('')+`</tbody>`;

 // --- tabel gardu hotspot ---
 $('tGxGardu').innerHTML=`<thead><tr><th style="text-align:left">Gardu</th><th style="text-align:left">UP3</th><th>kVA</th><th>%kini</th><th>%proyeksi</th><th>EV</th><th style="text-align:left">Penyulang / GI</th></tr></thead><tbody>`+
  X.topGardu.map(g=>`<tr><td style="text-align:left;font-weight:600">${g.nm}</td><td style="text-align:left">${g.up3}</td>
   <td style="text-align:right">${g.kva}</td><td style="text-align:right">${f1(g.pb)}</td>
   <td style="text-align:right;font-weight:700;color:${g.post>=100?'#d6443c':'#e8742c'}">${f1(g.post)}</td>
   <td style="text-align:right">${g.nev}</td><td style="text-align:left;font-size:11px;color:var(--mut)">${g.peny||'–'} / ${g.gi||'–'}</td></tr>`).join('')+`</tbody>`;

 // --- tabel GI ---
 const GIhot=X.gi.filter(g=>g.mx>=80&&(g.nev+g.nsp)>0).slice(0,12);
 const GIopp=X.gi.filter(g=>g.mx<50&&g.nsp<=1).sort((a,b)=>a.mx-b.mx).slice(0,12);
 const girow=g=>`<tr><td style="text-align:left;font-weight:600">${g.nm}</td><td style="text-align:left">${g.up3}</td>
   <td style="text-align:right">${g.mva||'–'}</td><td style="text-align:right">${f1(g.ps)}</td>
   <td style="text-align:right;font-weight:${g.pm>=80?700:400};color:${g.pm>=80?'#d6443c':'inherit'}">${f1(g.pm)}</td>
   <td style="text-align:right">${g.nev}</td><td style="text-align:right">${g.nsp}</td><td style="text-align:right">${fmt(g.kw)}</td></tr>`;
 $('tGxGI').innerHTML=`<thead><tr><th style="text-align:left">Gardu Induk</th><th style="text-align:left">UP3</th><th>MVA</th><th>%siang</th><th>%malam</th><th>EV</th><th>SPKLU</th><th>kW</th></tr></thead><tbody>`+
  `<tr><td colspan="8" style="background:#fdecec;font-weight:700;color:#8a1f1a;font-size:11px">⛔ GI SESAK (≥80%) YANG SUDAH MENANGGUNG EV/SPKLU</td></tr>`+GIhot.map(girow).join('')+
  `<tr><td colspan="8" style="background:#eaf6ee;font-weight:700;color:#1f7a3d;font-size:11px">✅ GI LEGA (&lt;50%) DENGAN SPKLU MINIM — PELUANG EKSPANSI</td></tr>`+GIopp.map(girow).join('')+`</tbody>`;

 // --- tabel penyulang ---
 $('tGxFeeder').innerHTML=`<thead><tr><th style="text-align:left">Penyulang</th><th style="text-align:left">UP3</th><th>Trafo</th><th>kVA</th><th>%kini</th><th>SPKLU</th><th>EV</th><th>Porsi EV+SPKLU</th></tr></thead><tbody>`+
  X.feeder.map(f=>`<tr><td style="text-align:left;font-weight:600">${f.peny}</td><td style="text-align:left">${f.up3.replace('UP3 ','')}</td>
   <td style="text-align:right">${f.ntr}</td><td style="text-align:right">${fmt(f.kva)}</td><td style="text-align:right">${f1(f.pb)}</td>
   <td style="text-align:right">${f.nsp}</td><td style="text-align:right">${f.nev}</td>
   <td style="text-align:right;font-weight:700;color:${f.evshare>=100?'#d6443c':f.evshare>=40?'#e8742c':'inherit'}">${f1(f.evshare)}%</td></tr>`).join('')+`</tbody>`;

 // --- tabel kecamatan ---
 $('tGxKec').innerHTML=`<thead><tr><th style="text-align:left">Kecamatan</th><th style="text-align:left">Kab/Kota</th><th>EV</th><th>di gardu ≥80%</th><th>%</th><th>overload</th></tr></thead><tbody>`+
  X.kec.map(k=>`<tr><td style="text-align:left;font-weight:600">${k.kec}</td><td style="text-align:left;font-size:11px">${k.kab}</td>
   <td style="text-align:right">${k.n}</td><td style="text-align:right">${k.risk}</td>
   <td style="text-align:right;font-weight:700;color:${k.pct>=35?'#d6443c':k.pct>=20?'#e8742c':'inherit'}">${f1(k.pct)}%</td>
   <td style="text-align:right">${k.ov}</td></tr>`).join('')+`</tbody>`;

 // --- rekomendasi ---
 const worst=U[U.length-1], best=U[0];
 $('gxRecs').innerHTML=`<ol class="recs">
 <li><b>Ganti skrining EV dari level UP3 ke level gardu.</b> Persetujuan pasang-baru charger rumah sebaiknya memeriksa headroom gardu penyuplai, bukan sekadar kuota daya wilayah. ${fmt(noRoom)} gardu (${f1(p1(noRoom,M.nGardu))}%) hari ini sudah melampaui batas aman 80% begitu satu charger 7,7 kVA ditambahkan (pada keserempakan 0,6) — dan data koordinat gardu yang sudah tersedia membuat pemeriksaan ini bisa dijalankan otomatis saat permohonan masuk.</li>
 <li><b>Prioritaskan penguatan jaringan berdasar eksposur nyata, bukan jumlah EV.</b> Yang paling banyak menanggung EV di atas gardu ≥80% adalah <b>${expo.slice(0,3).map(u=>u.up3+' ('+u.nEVhot+' pelanggan, '+f1(u.pctEVhot)+'% dari EV-nya)').join(', ')}</b>. Peringkat ini berbeda dari peringkat jumlah EV — ${expo[0].up3} unggul bukan karena EV-nya terbanyak, melainkan karena EV-nya paling sering mendarat di gardu yang sudah sesak, dan di sanalah keluhan tegangan turun akan muncul lebih dulu.</li>
 <li><b>Jadikan <i>smart charging</i>/tarif malam-dalam sebagai instrumen investasi, bukan sekadar program efisiensi.</b> Menekan keserempakan dari 1,0 ke 0,35 menghindarkan ${s10.newOver-s35.newOver} gardu dari status overload — penghematan belanja modal yang diperoleh tanpa satu pun penggantian trafo.</li>
 <li><b>Arahkan ekspansi SPKLU ke GI berkapasitas lega.</b> ${GIopp.length} gardu induk beroperasi di bawah 50% dengan nyaris tanpa SPKLU. Menempatkan pengisian cepat di sana memperbaiki pemanfaatan aset sekaligus menghindari penambahan beban pada GI yang sudah ≥80%.</li>
 <li><b>Perlakukan ${lo.slice(-3).join(', ')} sebagai kasus rehabilitasi jaringan, bukan kasus EV.</b> ${worst.up3} memiliki ${f1(worst.pctHot)}% gardu ≥80% dan ${f1(worst.pctOver)}% sudah overload — beban tinggi ini muncul <b>sebelum</b> EV masuk, sehingga program EV di wilayah ini akan gagal jika tidak didahului perbaikan jaringan.</li>
 <li><b>Selesaikan ketidakseimbangan fasa lebih dulu — ini perbaikan termurah.</b> ${f1(U.reduce((a,u)=>a+u.unb*u.n,0)/U.reduce((a,u)=>a+u.n,0))}% gardu Jabar berstatus prioritas unbalance; charger rumah satu fasa memperburuknya. Penyeimbangan jurusan mengembalikan kapasitas efektif tanpa belanja modal.</li>
 </ol>`;

 $('gxMethod').innerHTML=`<b>Sumber data.</b> <i>Gardu_Beban_Lokasi_JABAR.xlsx</i> — ${fmt(M.nGarduRaw)} gardu distribusi dengan koordinat dan pengukuran arus per fasa siang &amp; malam (pengukuran lapangan 2023–2024), digabung dengan aset SSOT Jabar dan pembebanan trafo Gardu Induk. Sisi EV: ${fmt(M.nEV)} permohonan pasang-baru/tambah-daya pelanggan KBLBB (mayoritas 7.700 VA) dan ${fmt(M.nSP)} unit SPKLU pada ${fmt(M.nLoc)} situs (Master SPKLU Maret 2026).<br><br>
 <b>Cara menghubungkan.</b> Setiap pelanggan EV dipetakan ke gardu terdekat dalam radius 1 km (${fmt(M.nEVjoin)} dari ${fmt(M.nEV)} berhasil; ${f1(p1(M.nEVjoin,M.nEV))}%), setiap situs SPKLU dalam radius 2 km. %beban gardu = arus rata-rata tiga fasa ÷ arus nominal (kVA×1000 ÷ √3×400 V), diambil nilai maksimum antara siang dan malam. Headroom aman memakai batas 80% — praktik lazim perencanaan distribusi yang menyisakan margin untuk pertumbuhan dan kontingensi. Beban EV tambahan = jumlah charger × 7,7 kVA × faktor keserempakan (CF).<br><br>
 <b>Keterbatasan yang perlu diketahui pembaca.</b> (1) Kedekatan geografis <b>bukan bukti kelistrikan</b> — gardu terdekat belum tentu gardu penyuplai; untuk SPKLU ≥50 kW umumnya justru tersedia sambungan khusus, sehingga angka SPKLU di sini dibaca sebagai <i>konteks jaringan setempat</i>, bukan pembebanan literal. (2) Pengukuran arus bersifat <i>snapshot</i> dua titik waktu, bukan rekaman kontinu, sehingga puncak sebenarnya bisa terlewat. (3) Pembebanan Gardu Induk berasal dari rekap yang lebih lama daripada data gardu distribusi — dipakai untuk peringkat relatif, bukan angka mutlak. (4) ${fmt(M.nGarduRaw-M.nGardu)} gardu dikeluarkan karena koordinat di luar Jawa Barat, kapasitas di luar rentang 5–3.000 kVA, atau %beban >200% (indikasi salah rekam). (5) Faktor keserempakan tidak diukur, melainkan diasumsikan; CF 0,6 dipakai sebagai kasus dasar dan hasilnya sensitif terhadap asumsi ini — karena itu ketiga skenario ditampilkan berdampingan.`;
})();
