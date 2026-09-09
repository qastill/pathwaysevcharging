
/* ============ PARKIR × CHARGER — akses 10 menit, perilaku parkir, ChargeScore (window.PARKIR, dimuat malas) ============ */
(function(){
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>(n==null||isNaN(n))?'—':Math.round(+n).toLocaleString('id-ID');
const f1=n=>(n==null||isNaN(n))?'—':(+n).toLocaleString('id-ID',{maximumFractionDigits:1,minimumFractionDigits:1});
const jt=n=>n>=1e6?(n/1e6).toLocaleString('id-ID',{maximumFractionDigits:2})+' jt':n>=1e3?(n/1e3).toLocaleString('id-ID',{maximumFractionDigits:0})+' rb':fmt(n);
const NAVY='#16305f',GOLD='#d4af37',BLUE='#3a6ea5',GREEN='#2e9e5b',RED='#d6443c',ORANGE='#e8742c',MUT='#9aa6bd';
let P=null,built=false,map=null,canvas=null,siteLayer=null,prioLayer=null,walkLayer=null;
const C={};
const S={prov:'all',kab:'all',cats:new Set(),src:'jabar'};
let sortK='rank',sortD=1,tableRows=[];
function loadScript(src){return new Promise((res,rej)=>{const s=document.createElement('script');s.src=src;s.onload=res;s.onerror=()=>rej(new Error('gagal memuat '+src));document.head.appendChild(s);});}
function mk(id,cfg){if(C[id])C[id].destroy();const el=$(id);if(!el||typeof Chart==='undefined')return;C[id]=new Chart(el,cfg);}
const catOf=i=>P.cats[i];
const yAx=t=>({beginAtZero:true,grid:{color:'#eef1f6'},title:{display:!!t,text:t,font:{size:10}},ticks:{font:{size:10}}});
const xAx=t=>({grid:{display:false},title:{display:!!t,text:t,font:{size:10}},ticks:{font:{size:10}}});

/* ---------- lingkup ---------- */
const scopeName=()=>S.kab!=='all'?P.kabs[+S.kab].name:S.prov==='all'?'Indonesia':P.provs[+S.prov];
const kabInScope=k=>(S.prov==='all'||P.kabs[k.idx].prov===+S.prov)&&(S.kab==='all'||k.idx===+S.kab);
const siteInScope=s=>(S.prov==='all'||P.kabs[s[9]].prov===+S.prov)&&(S.kab==='all'||s[9]===+S.kab);
function aggScope(){
 const ks=P.kab_stats.filter(kabInScope);const pop=ks.reduce((a,k)=>a+k.pop,0)||1;
 const w=(f)=>ks.reduce((a,k)=>a+k.pop*(k[f]||0),0)/pop;
 const ss=P.sites.filter(s=>siteInScope(s)&&s[4]);
 const ch=ss.reduce((a,s)=>a+s[6],0);
 const catCh={};P.cats.forEach((c,i)=>catCh[c.id]=ss.filter(s=>s[2]===i).reduce((a,s)=>a+s[6],0));
 const park=catCh.transit+catCh.destinasi+catCh.kerja;
 return {ks,pop,walk:w('walk'),drive:w('drive'),walk_park:w('walk_park'),drive_dc:w('drive_dc'),sites:ss.length,ch,catCh,park_share:ch?100*park/ch:0,
  prio_pop:ks.reduce((a,k)=>a+k.prio_pop,0),dc:ss.filter(s=>s[7]>=50).length};
}

/* ---------- peta ---------- */
function initMap(){
 map=L.map('pkMap',{preferCanvas:true}).setView([-2.3,118],5);
 L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{attribution:'© OSM © CARTO · Kontur Population · PLN',maxZoom:19}).addTo(map);
 canvas=L.canvas({padding:.4});
}
function drawMap(){
 [siteLayer,prioLayer,walkLayer].forEach(l=>{if(l)l.remove();});siteLayer=prioLayer=walkLayer=null;
 const sites=P.sites.filter(s=>siteInScope(s)&&S.cats.has(catOf(s[2]).id));
 // heksagon prioritas: per kabupaten dalam lingkup (nasional: hanya 100 kota terpadat supaya ringan)
 if($('pkLyPrio').checked&&typeof h3!=='undefined'){prioLayer=L.layerGroup().addTo(map);
  let kabs=P.kab_stats.filter(kabInScope);if(S.prov==='all'&&S.kab==='all')kabs=kabs.slice().sort((a,b)=>b.pop-a.pop).slice(0,100);
  kabs.forEach(k=>(P.prio[k.idx]||[]).forEach(h=>{L.polygon(h3.cellToBoundary(h[0]),{renderer:canvas,stroke:false,fillColor:h[2]>5?RED:ORANGE,fillOpacity:.55,interactive:false}).addTo(prioLayer);}));}
 if($('pkLyWalk').checked&&(S.kab!=='all'||sites.length<=400)){walkLayer=L.layerGroup().addTo(map);
  sites.forEach(s=>L.circle([s[0],s[1]],{radius:P.meta.walk_km*1000,renderer:canvas,stroke:true,color:'#1b6b46',weight:.6,fillColor:'#7fc39a',fillOpacity:.12,interactive:false}).addTo(walkLayer));}
 siteLayer=L.layerGroup().addTo(map);
 sites.forEach(s=>{const c=catOf(s[2]);
  L.circleMarker([s[0],s[1]],{renderer:canvas,radius:s[6]>=4?5:s[6]>=2?4:3,fillColor:c.color,color:'#fff',weight:.7,fillOpacity:s[4]?.95:.35})
   .bindPopup(`<b>${esc(s[8])}</b><br>${c.icon} ${esc(c.label)} · ${esc(s[3])}<br>${s[7]} kW · ${s[6]} charger · ${s[5]?'PLN':'mitra non-PLN'} · ${s[4]?'operasional':'tidak aktif'}<br>${esc(P.kabs[s[9]].name)}`).addTo(siteLayer);});
 $('pkLegend').innerHTML=P.cats.map(c=>`<span><i style="background:${c.color}"></i>${c.label}</span>`).join('')+
  '<span><i style="background:'+RED+';opacity:.6"></i>heksagon prioritas &gt;5 km dari charger</span><span><i style="background:'+ORANGE+';opacity:.6"></i>0,8–5 km</span>';
 $('pkMapSub').textContent=`— ${sites.length.toLocaleString('id-ID')} situs · ${scopeName()} · heksagon prioritas = 25 terpadat per kabupaten di luar 10 menit jalan kaki`;
}
function zoomScope(){
 const sites=P.sites.filter(siteInScope);const pts=sites.map(s=>[s[0],s[1]]);
 (P.kab_stats.filter(kabInScope)).forEach(k=>(P.prio[k.idx]||[]).forEach(h=>{const [la,lo]=h3.cellToLatLng(h[0]);pts.push([la,lo]);}));
 if(pts.length<2){map.setView([-2.3,118],5);return;}
 let s=1e9,n=-1e9,w=1e9,e=-1e9;pts.forEach(([la,lo])=>{s=Math.min(s,la);n=Math.max(n,la);w=Math.min(w,lo);e=Math.max(e,lo);});
 map.fitBounds([[s-.03,w-.03],[n+.03,e+.03]]);
}

/* ---------- ringkasan & grafik akses ---------- */
function summarize(){
 const a=aggScope(),n=P.nat;
 $('pkStats').innerHTML=[[jt(a.pop),'penduduk '+scopeName()],[f1(a.walk)+'%','≤0,8 km — 10 menit jalan kaki'],[f1(a.drive)+'%','≤5 km — 10 menit berkendara'],
  [f1(a.walk_park)+'%','≤0,8 km dari charger di parkir umum'],[f1(a.drive_dc)+'%','≤5 km dari situs DC ≥50 kW'],[fmt(a.sites),'situs operasional'],[fmt(a.ch),'charger operasional'],
  [f1(a.park_share)+'%','charger di parkir umum (transit·destinasi·kerja)'],[jt(a.prio_pop),'jiwa di luar 10 menit jalan kaki']]
  .map(x=>`<div class="s"><div class="n">${x[0]}</div><div class="t">${x[1]}</div></div>`).join('');
 const top=a.ks.slice().sort((x,y)=>y.prio_pop-x.prio_pop).slice(0,3);
 const best=a.ks.filter(k=>k.pop>200000).sort((x,y)=>y.walk-x.walk).slice(0,3);
 $('pkInsight').innerHTML=`<b>Bacaan ParkServe untuk charger — ${esc(scopeName())}.</b> Hanya <b>${f1(a.walk)}%</b> penduduk tinggal dalam 10 menit berjalan kaki (0,8 km) dari SPKLU operasional,
  dan ${f1(a.drive)}% dalam 10 menit berkendara (5 km). Ukuran "jalan kaki" milik taman tidak cocok untuk charger — orang datang dengan mobil — tetapi ia menjawab satu hal:
  <i>siapa yang bisa menitipkan mobil mengisi sambil pulang berjalan kaki</i>, yakni penduduk hunian padat tanpa garasi. ${a.ks.length>1?`Terbaik (≥200 rb jiwa): ${best.map(k=>esc(k.name)+' '+f1(k.walk)+'%').join(', ')}. `:''}
  Jiwa terbanyak di luar jangkauan jalan kaki: ${top.map(k=>'<b>'+esc(k.name)+'</b> ('+jt(k.prio_pop)+')').join(', ')} — heksagon merah/oranye di peta adalah 25 kantong terpadat per kabupaten,
  padanan <i>park priority areas</i>. Dari ${fmt(a.ch)} charger operasional, <b>${f1(a.park_share)}%</b> berdiri di lahan parkir umum (transit, destinasi, kerja/publik); sisanya di perumahan, dealer, atau tempat yang tidak terklasifikasi.`;
 // pita jarak nasional
 mk('cPkBands',{type:'bar',data:{labels:['≤0,4 km','0,4–0,8','0,8–2','2–5','5–10','>10 km'],datasets:[{data:n.bands.map(b=>Math.round(b/1e6*100)/100),backgroundColor:['#1b6b46','#7fc39a','#c5e0b4','#e0a52b',ORANGE,RED],borderRadius:3}]},
  options:{maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:x=>x.raw+' juta jiwa'}}},scales:{y:yAx('juta jiwa'),x:xAx('jarak ke SPKLU operasional terdekat')}}});
 // charger per kategori
 mk('cPkCat',{type:'bar',data:{labels:P.cats.map(c=>c.label),datasets:[{data:P.cats.map(c=>a.catCh[c.id]),backgroundColor:P.cats.map(c=>c.color),borderRadius:3}]},
  options:{indexAxis:'y',maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:yAx('charger operasional'),y:{grid:{display:false},ticks:{font:{size:10}}}}}});
 $('pkCatSub').textContent=scopeName();
 // peringkat
 let units,title;
 if(S.prov==='all'&&S.kab==='all'){const m={};P.kab_stats.forEach(k=>{const p=P.kabs[k.idx].prov;m[p]=m[p]||{name:P.provs[p],pop:0,w:0,d:0};m[p].pop+=k.pop;m[p].w+=k.pop*k.walk;m[p].d+=k.pop*k.drive;});
  units=Object.values(m).map(u=>({name:u.name,walk:u.w/u.pop,drive:u.d/u.pop}));title='provinsi';}
 else{units=a.ks.slice().sort((x,y)=>y.pop-x.pop).slice(0,30).map(k=>({name:k.name,walk:k.walk,drive:k.drive}));title=S.kab!=='all'?'kabupaten terpilih':'kabupaten/kota — '+P.provs[+S.prov]+' (30 terpadat)';}
 units.sort((x,y)=>y.drive-x.drive);$('pkRankTitle').textContent=title;
 mk('cPkRank',{type:'bar',data:{labels:units.map(u=>u.name),datasets:[{label:'≤0,8 km (jalan kaki)',data:units.map(u=>+u.walk.toFixed(1)),backgroundColor:NAVY,borderRadius:2},{label:'≤5 km (berkendara)',data:units.map(u=>+u.drive.toFixed(1)),backgroundColor:'#c9d4e8',borderRadius:2}]},
  options:{indexAxis:'y',maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},scales:{x:{min:0,max:100,grid:{color:'#eef1f6'},ticks:{font:{size:10}}},y:{grid:{display:false},ticks:{font:{size:units.length>25?8:10},autoSkip:false}}}}});
}

/* ---------- perilaku parkir ---------- */
function behaviour(){
 const V=P.venue[S.src],days=S.src==='jabar'?P.meta.days_jb:P.meta.days_jk,nsess=S.src==='jabar'?P.meta.n_jb:P.meta.n_jk;
 const cats=P.cats.filter(c=>V[c.id]);
 $('pkBehSub').textContent=S.src==='jabar'?`— Jawa Barat, Maret 2026 (${fmt(nsess)} sesi, ${days} hari, tag lokasi resmi PLN)`:`— Jakarta Raya, 1–8 Juni 2026 (${fmt(nsess)} sesi, ${days} hari, kategori dari nama situs)`;
 $('pkCatCards').innerHTML=cats.map(c=>{const v=V[c.id];return `<div class="catcard" style="border-top-color:${c.color}"><div class="h">${c.icon} ${esc(c.label)}</div><div class="d">${esc(c.desc)}</div>
  <div class="kv"><span><b>${f1(v.dwell_med)}</b> mnt parkir (median)</span><span><b>${f1(v.occ)}%</b> okupansi bay</span><span><b>${v.turnover}</b> sesi/bay/hari</span><span><b>${v.kw_eff}</b> kW efektif</span><span><b>${fmt(v.n)}</b> sesi · ${v.sites} situs</span><span><b>${f1(v.kwh_sess)}</b> kWh/sesi</span></div></div>`;}).join('');
 const lab=cats.map(c=>c.label),col=cats.map(c=>c.color);
 mk('cPkDwell',{type:'bar',data:{labels:lab,datasets:[{label:'median',data:cats.map(c=>V[c.id].dwell_med),backgroundColor:col,borderRadius:3},
   {label:'p75',data:cats.map(c=>V[c.id].dwell_p75),backgroundColor:'rgba(22,48,95,.15)',borderRadius:3}]},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},scales:{y:yAx('menit'),x:{grid:{display:false},ticks:{font:{size:9}}}}}});
 mk('cPkOcc',{data:{labels:lab,datasets:[{type:'bar',label:'okupansi bay %',data:cats.map(c=>V[c.id].occ),backgroundColor:col,borderRadius:3,yAxisID:'y'},
   {type:'line',label:'perputaran sesi/bay/hari',data:cats.map(c=>V[c.id].turnover),borderColor:NAVY,backgroundColor:NAVY,pointRadius:4,yAxisID:'y2'}]},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},scales:{y:yAx('% jam terisi'),y2:{position:'right',beginAtZero:true,grid:{display:false},title:{display:true,text:'sesi/bay/hari',font:{size:10}},ticks:{font:{size:10}}},x:{grid:{display:false},ticks:{font:{size:9}}}}}});
 const HL=P.meta.dwell_labels,hc=['#1b6b46','#7fc39a','#e0a52b',ORANGE,RED,'#8a2e27'];
 mk('cPkHist',{type:'bar',data:{labels:lab,datasets:HL.map((h,i)=>({label:h,data:cats.map(c=>V[c.id].hist_pct[i]),backgroundColor:hc[i],stack:'s'}))},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:9}}}},scales:{y:{stacked:true,max:100,grid:{color:'#eef1f6'},ticks:{font:{size:10}},title:{display:true,text:'% sesi',font:{size:10}}},x:{stacked:true,grid:{display:false},ticks:{font:{size:9}}}}}});
 mk('cPkProf',{type:'line',data:{labels:[...Array(24).keys()].map(h=>h+':00'),datasets:cats.map(c=>({label:c.label,data:V[c.id].prof,borderColor:c.color,backgroundColor:c.color,pointRadius:0,borderWidth:2,tension:.3}))},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:9}}}},scales:{y:yAx('% bay terisi'),x:{grid:{display:false},ticks:{font:{size:9},maxTicksLimit:12}}}}});
 const pw=P.venue.power;
 mk('cPkPower',{data:{labels:pw.map(p=>p.band),datasets:[{type:'bar',label:'durasi parkir median (mnt)',data:pw.map(p=>p.dwell_med),backgroundColor:GOLD,borderRadius:3,yAxisID:'y'},
   {type:'line',label:'kWh per sesi',data:pw.map(p=>p.kwh_sess),borderColor:NAVY,backgroundColor:NAVY,pointRadius:4,yAxisID:'y2'}]},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},scales:{y:yAx('menit'),y2:{position:'right',beginAtZero:true,grid:{display:false},title:{display:true,text:'kWh/sesi',font:{size:10}},ticks:{font:{size:10}}},x:xAx('daya charger')}}});
 const J=P.venue.jabar,K=P.venue.jakarta;
 const peak=c=>{const p=V[c].prof;let m=0;p.forEach((v,i)=>{if(v>p[m])m=i;});return m;};
 $('pkBehInsight').innerHTML=`<b>Apa yang dikatakan data parkir.</b> Durasi parkir saat mengisi nyaris seragam antar-lahan — median ${f1(J.transit.dwell_med)} menit di rest area tol hingga ${f1(J.hunian.dwell_med)} menit di perumahan (Jawa Barat) —
  padahal mobil di mal atau kantor diparkir berjam-jam. Yang menentukan lama parkir di bay charger bukan alasan parkirnya, melainkan <b>daya charger</b>: ${pw[0].band} → ${f1(pw[0].dwell_med)} menit, ≥150 kW → ${f1(pw[pw.length-1].dwell_med)} menit.
  Artinya bay charger di lahan parkir destinasi diperlakukan seperti pom bensin (isi lalu pindah), bukan sebagai parkir yang kebetulan mengisi — <b>peluang AC murah berjam-jam di mal/kantor belum terpakai</b> (kW efektif destinasi ${J.destinasi.kw_eff} kW, okupansi ${f1(J.destinasi.occ)}%).
  Okupansi bay tertinggi di <b>dealer</b> (${f1(J.dealer.occ)}% Jawa Barat, ${f1(K.dealer.occ)}% Jakarta) dan <b>transit</b> (${f1(J.transit.occ)}% / ${f1(K.transit.occ)}%), terendah di destinasi (${f1(J.destinasi.occ)}%) — dealer memuncak pukul ${peak('dealer')}:00, kerja/publik pukul ${peak('kerja')}:00.
  <span class="warn">catatan</span> "bay" = jumlah charger di master PLN; bila master mencatat lebih sedikit dari fisik (lazim di dealer), okupansi dan perputaran terangkat.`;
}

/* ---------- ChargeScore ---------- */
const PC={akses:BLUE,kapasitas:GREEN,ketersediaan:GOLD,parkir:'#8a6fb0'};
function renderTable(){
 const q=($('pkSearch').value||'').toLowerCase();
 let rows=tableRows.filter(k=>!q||k.name.toLowerCase().includes(q)||k.provn.toLowerCase().includes(q));
 rows.sort((a,b)=>{const x=a[sortK],y=b[sortK];return (typeof x==='string')?sortD*x.localeCompare(y):sortD*((x==null?-1:x)-(y==null?-1:y));});
 const pts=(v,max,c)=>`<span class="pts" style="background:${c};opacity:${.35+.65*v/max}">${v}</span>`;
 const bar=v=>`<span class="bar"><i style="width:${v}%;background:${NAVY}"></i></span>${f1(v)}`;
 $('tblPk').querySelector('tbody').innerHTML=rows.map(k=>`<tr data-k="${k.idx}" style="cursor:pointer">
  <td class="n">${k.rank}</td><td><b>${esc(k.name)}</b></td><td>${esc(k.provn)}</td><td class="n">${fmt(k.pop)}</td><td>${bar(k.score)}</td>
  <td class="n">${pts(k.akses,10,PC.akses)}</td><td class="n">${pts(k.kapasitas,10,PC.kapasitas)}</td><td class="n">${pts(k.ketersediaan,10,PC.ketersediaan)}</td><td class="n">${pts(k.parkir,10,PC.parkir)}</td>
  <td class="n">${f1(k.walk)}</td><td class="n">${f1(k.drive)}</td><td class="n">${f1(k.per100k)}</td><td class="n">${k.avail==null?'—':f1(k.avail)}</td><td class="n">${k.park_share==null?'—':f1(k.park_share)}</td><td class="n">${fmt(k.prio_pop)}</td></tr>`).join('');
 $('tblPk').querySelectorAll('tbody tr').forEach(tr=>tr.onclick=()=>{const k=+tr.dataset.k;S.prov=String(P.kabs[k].prov);$('pkProv').value=S.prov;fillKab();S.kab=String(k);$('pkKab').value=S.kab;update();zoomScope();});
}
function csv(){
 const h=['peringkat','kabupaten','provinsi','penduduk','chargescore','akses','kapasitas','ketersediaan','parkir','pct_0.8km','pct_5km','charger_per_100k','pln_aktif_pct','di_parkir_umum_pct','jiwa_luar_10mnt'];
 const lines=[h.join(',')].concat(tableRows.map(k=>[k.rank,k.name,k.provn,k.pop,k.score,k.akses,k.kapasitas,k.ketersediaan,k.parkir,k.walk,k.drive,k.per100k,k.avail??'',k.park_share??'',k.prio_pop].map(v=>/[",]/.test(v)?'"'+String(v).replace(/"/g,'""')+'"':v).join(',')));
 const blob=new Blob([lines.join('\n')],{type:'text/csv;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='chargescore_100_kota.csv';a.click();
}

/* ---------- kontrol ---------- */
function fillKab(){
 const sel=$('pkKab');const cur=S.kab;
 const ks=P.kab_stats.filter(k=>S.prov==='all'||P.kabs[k.idx].prov===+S.prov).slice().sort((a,b)=>a.name.localeCompare(b.name));
 sel.innerHTML='<option value="all">Semua</option>'+ks.map(k=>`<option value="${k.idx}">${esc(k.name)}${S.prov==='all'?' · '+esc(P.provs[P.kabs[k.idx].prov]):''}</option>`).join('');
 sel.value=ks.some(k=>String(k.idx)===cur)?cur:'all';S.kab=sel.value;
}
function update(){summarize();drawMap();}
function note(){
 const n=P.nat,m=P.meta;
 $('pkNote').innerHTML=`<b>Akses 10 menit.</b> ParkServe memakai 10 menit berjalan kaki ≈ 0,5 mil = 0,8 km lewat jaringan jalan; di sini jarak garis lurus dari pusat tiap heksagon Kontur res 8 (≈0,74 km², ${fmt(n.hex)} heksagon, ${jt(n.pop)} jiwa) ke SPKLU operasional terdekat,
  dengan dua ambang: <b>${m.walk_km} km</b> (10 menit jalan kaki) dan <b>${m.drive_km} km</b> (10 menit berkendara ≈30 km/jam dalam kota). Situs operasional = PLN <i>available/inuse</i> + seluruh mitra non-PLN (status <i>offline mode</i> = tidak terpantau PLN, bukan mati).
  Heksagon prioritas = 25 heksagon berpenduduk ≥150 jiwa terpadat per kabupaten yang berada di luar 0,8 km; merah bila &gt;5 km. Dihitung sekali oleh <code>parkir/access.py</code> (butuh cache Kontur) → <code>parkir/input/access.json</code>.<br>
  <b>Kategori lahan parkir.</b> Tiap situs diklasifikasi dari namanya (aturan yang sama dengan tab 🇮🇩 Indonesia) lalu dikelompokkan: <b>transit</b> (rest area tol, terminal/stasiun/bandara, SPBU), <b>destinasi</b> (mal, hotel, F&amp;B, wisata, rumah sakit), <b>kerja &amp; publik</b> (perkantoran, kantor pemerintah/kampus, kantor PLN), <b>hunian</b>, <b>dealer</b>, <b>lainnya</b>.
  Untuk transaksi Jawa Barat dipakai <i>Jenis Titik Lokasi</i> resmi PLN (12 jenis) yang dipetakan ke kategori yang sama; Jakarta Raya memakai klasifikasi nama.<br>
  <b>Perilaku parkir.</b> Durasi = kolom durasi transaksi (menit); okupansi bay = jam-bay terisi ÷ (bay × 24 jam × hari), bay = jumlah charger situs di master; perputaran = sesi ÷ (bay × hari); kW efektif = kWh ÷ jam-bay; profil jam menyebarkan tiap sesi ke jam-jam yang dilewatinya.<br>
  <b>ChargeScore.</b> 100 kabupaten/kota terpadat (Kontur). Delapan ukuran dalam empat kategori: ${m.measures.map(x=>`<i>${esc(x.label)}</i> (${x.cat})`).join(' · ')}. Tiap ukuran diberi 1–5 poin menurut kuintil relatif terhadap 100 kota (nilai nol = 1 poin); skor = jumlah poin ÷ 40 × 100. Seperti ParkScore, skor bersifat <i>relatif</i> — kota terbaik belum tentu baik, hanya lebih baik dari 99 lainnya.<br>
  <b>Batas.</b> <span class="warn">1</span> Garis lurus, bukan jaringan jalan; jalan tol dan sungai tidak menjadi penghalang. <span class="warn">2</span> Poligon lahan parkir tidak tersedia — "lahan parkir" diwakili SPKLU yang berdiri di atasnya; lahan parkir besar <i>tanpa</i> charger (yang justru kandidat) belum terpetakan (butuh OSM <code>amenity=parking</code>).
  <span class="warn">3</span> Master PLN tidak memuat wilayah PLN Batam. <span class="warn">4</span> Klasifikasi nama bersifat heuristik (${fmt(n.cat_sites.lainnya)} situs "lainnya"). <span class="warn">5</span> Jakarta hanya 8 hari; okupansi Jakarta memakai bay dari master nasional. <span class="warn">6</span> Tidak ada kategori keadilan di ChargeScore karena data pendapatan hanya tingkat provinsi.<br>
  <b>Reproduksi.</b> <code>python3 parkir/access.py</code> (sekali) → <code>python3 parkir/prepare.py</code> → <code>python3 parkir/inject.py</code>. Rincian di <code>parkir/README.md</code>; intisari ParkServe/ParkScore di <a href="#" data-pklib="bacaan-parkserve">Perpustakaan</a>.`;
 document.querySelectorAll('#p-parkir [data-pklib]').forEach(a=>a.onclick=e=>{e.preventDefault();if(window.gotoTab)gotoTab('library');setTimeout(()=>{const b=document.querySelector('#p-library [data-libopen="'+a.dataset.pklib+'"]');if(b)b.click();},400);});
}

function build(){
 $('pkLoading').style.display='none';$('pkBody').style.display='block';
 const n=P.nat;
 $('pkMeta').innerHTML=[[f1(n.walk)+'%','penduduk ≤0,8 km dari SPKLU'],[f1(n.drive)+'%','penduduk ≤5 km'],[fmt(n.active),'situs operasional'],[fmt(n.chargers),'charger operasional'],[f1(100*(n.cat_ch.transit+n.cat_ch.destinasi+n.cat_ch.kerja)/n.chargers)+'%','charger di lahan parkir umum'],[fmt(P.meta.n_jb+P.meta.n_jk),'sesi parkir-mengisi dianalisis'],[P.score.length,'kota dalam ChargeScore']]
  .map(x=>`<div><div class="n">${x[0]}</div><div class="t">${x[1]}</div></div>`).join('');
 $('pkProv').innerHTML='<option value="all">Seluruh Indonesia</option>'+P.provs.map((p,i)=>`<option value="${i}">${esc(p)}</option>`).join('');
 P.cats.forEach(c=>S.cats.add(c.id));
 $('pkCats').innerHTML=P.cats.map(c=>`<span class="chip" data-c="${c.id}"><i style="background:${c.color}"></i>${c.icon} ${esc(c.label)}</span>`).join('');
 $('pkCats').querySelectorAll('.chip').forEach(ch=>ch.onclick=()=>{const id=ch.dataset.c;if(S.cats.has(id)){S.cats.delete(id);ch.classList.add('off');}else{S.cats.add(id);ch.classList.remove('off');}drawMap();});
 fillKab();initMap();note();
 tableRows=P.score.map(r=>({...r,provn:P.provs[r.prov],akses:r.cat_pts.akses,kapasitas:r.cat_pts.kapasitas,ketersediaan:r.cat_pts.ketersediaan,parkir:r.cat_pts.parkir}));
 renderTable();behaviour();
 $('pkProv').onchange=()=>{S.prov=$('pkProv').value;S.kab='all';fillKab();update();zoomScope();};
 $('pkKab').onchange=()=>{S.kab=$('pkKab').value;update();zoomScope();};
 $('pkLyPrio').onchange=drawMap;$('pkLyWalk').onchange=drawMap;
 document.querySelectorAll('#p-parkir .seg button').forEach(b=>b.onclick=()=>{document.querySelectorAll('#p-parkir .seg button').forEach(x=>{x.style.background='#fff';x.style.color='';});b.style.background='var(--navy)';b.style.color='var(--gold)';S.src=b.dataset.s;behaviour();});
 $('tblPk').querySelectorAll('th').forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(!k)return;if(k===sortK)sortD*=-1;else{sortK=k;sortD=(k==='name'||k==='provn'||k==='rank')?1:-1;}renderTable();});
 $('pkSearch').oninput=renderTable;$('pkCsv').onclick=csv;
 update();setTimeout(()=>map.invalidateSize(),150);
 built=true;
}

window.initParkir=async function(){
 if(built){if(map)map.invalidateSize();return;}
 if(window.pkLoadingNow)return;window.pkLoadingNow=true;
 try{
  if(typeof h3==='undefined')await loadScript('equitymap/vendor/h3-js.umd.js');
  if(!window.PARKIR)await loadScript('parkir/parkir.js');
  P=window.PARKIR;build();
 }catch(e){$('pkLoading').innerHTML='<b>Gagal memuat:</b> '+esc(e.message)+'. Jalankan <code>python3 parkir/prepare.py</code>.';}
 finally{window.pkLoadingNow=false;}
};
if(document.querySelector('#p-parkir.active'))setTimeout(window.initParkir,60);
})();
