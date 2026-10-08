
/* ============ AKSES WAKTU TEMPUH — desa -> SPKLU (ttm/ttm.json + ttm/input/villages_simplified.geojson, dimuat malas) ============ */
(function(){
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>(n==null||isNaN(n))?'—':Math.round(+n).toLocaleString('id-ID');
const f1=n=>(n==null||isNaN(n))?'—':(+n).toLocaleString('id-ID',{maximumFractionDigits:1,minimumFractionDigits:1});
const f2=n=>(n==null||isNaN(n))?'—':(+n).toLocaleString('id-ID',{maximumFractionDigits:2,minimumFractionDigits:2});
const f3=n=>(n==null||isNaN(n))?'—':(+n).toLocaleString('id-ID',{maximumFractionDigits:3,minimumFractionDigits:3});
const pct=n=>(n==null||isNaN(n))?'—':(100*n).toLocaleString('id-ID',{maximumFractionDigits:1})+' %';
const jt=n=>n>=1e6?(n/1e6).toLocaleString('id-ID',{maximumFractionDigits:2})+' jt':n>=1e3?(n/1e3).toLocaleString('id-ID',{maximumFractionDigits:0})+' rb':fmt(n);
const NAVY='#16305f',GOLD='#d4af37',BLUE='#3a6ea5',GREEN='#2e9e5b',RED='#d6443c',ORANGE='#e8742c',MUT='#9aa6bd';
/* skala magma 7 kelas (meniru peta supervisor) — gelap = rendah */
const MAGMA=['#000004','#2c115f','#721f81','#b73779','#f1605d','#feb078','#fcfdbf'];
const C={};let D=null,GJ=null,map=null,layer=null,sitesLayer=null,built=false,S={l:'access',kab:'all'},VI=new Map(),sortK='pop',sortD=-1;

function loadScript(src){return new Promise((res,rej)=>{const s=document.createElement('script');s.src=src;s.onload=res;s.onerror=()=>rej(new Error('gagal memuat '+src));document.head.appendChild(s);});}
function mk(id,cfg){if(C[id])C[id].destroy();const el=$(id);if(!el||typeof Chart==='undefined')return;C[id]=new Chart(el,cfg);}
const isTTM=()=>D.summary.mode==='ttm';
const unit=()=>D.summary.unit;

/* ---------- warna ---------- */
function breaks(){
 const s=D.summary;
 if(S.l==='access')return isTTM()?[5,10,15,20,30,45]:[1,2,5,10,15,25];
 if(S.l==='far')return isTTM()?[1,5,20,50,100,250]:[1,5,20,50,100,250];
 if(S.l==='villages30')return [10,25,50,100,150,250];
 if(S.l==='chargers')return [1,2,4,8,16,32];
 if(S.l==='dens')return [250,1000,2500,5000,10000,20000];
}
function colorOf(v){
 if(v==null)return S.l==='access'?'#222':'#dfe3ea';
 const b=breaks();let i=0;while(i<b.length&&v>b[i])i++;
 /* akses: kecil = baik = terang; lainnya: besar = terang */
 return S.l==='access'?MAGMA[6-i]:MAGMA[i];
}
function valueOf(r){
 if(S.l==='access')return r.access;
 if(S.l==='far')return r.far;
 if(S.l==='villages30')return r.villages30;
 if(S.l==='chargers')return r.chargers;
 if(S.l==='dens')return r.pop/Math.max(r.area||1,0.01);
}
function legend(){
 const b=breaks(),u=S.l==='access'?' '+unit():S.l==='dens'?' jiwa/km²':'';
 const labs=[];for(let i=0;i<=b.length;i++){labs.push(i===0?'≤ '+b[0]+u:i===b.length?'> '+b[b.length-1]+u:b[i-1]+'–'+b[i]+u);}
 $('ttLegend').innerHTML=labs.map((t,i)=>`<span><i style="background:${S.l==='access'?MAGMA[6-i]:MAGMA[i]}"></i>${t}</span>`).join('')+
  (S.l==='access'?`<span><i style="background:#222"></i>${isTTM()?'> 60 mnt / tak terjangkau':'tanpa nilai'}</span>`:'')+
  `<span style="color:${MUT}">${{access:isTTM()?'menit berkendara ke desa ber-SPKLU terdekat (p50, Selasa 14.00)':'km garis lurus ke lokasi SPKLU terdekat (ukuran antara)',
    far:'unit charger yang bisa dicapai dalam '+D.summary.th[1]+' '+unit(),villages30:'jumlah desa lain yang bisa dicapai ≤30 menit (replikasi peta supervisor)',
    chargers:'unit charger yang berlokasi di dalam desa',dens:'penduduk Kontur 2023 ÷ luas desa'}[S.l]}</span>`;
}

/* ---------- peta ---------- */
function buildMap(){
 if(map)return;
 map=L.map('ttMap',{preferCanvas:true}).setView([-6.6,107.3],8);
 L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',{attribution:'© OpenStreetMap, © CARTO',maxZoom:18}).addTo(map);
 L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png',{pane:'overlayPane',maxZoom:18}).addTo(map);
 layer=L.geoJSON(GJ,{style:styleOf,onEachFeature:(f,ly)=>{ly.on('click',()=>{const r=VI.get(f.properties.id);if(!r)return;const nm=D.names[r.id]||['','',''];
  ly.bindPopup(`<b>${esc(nm[0])}</b><br>Kec. ${esc(nm[1])}, ${esc(nm[2])}<br><span style="color:${MUT}">kode ${r.id}</span><hr style="margin:5px 0;border:none;border-top:1px solid #eee">
   ${isTTM()?'Waktu ke desa ber-SPKLU terdekat':'Jarak ke SPKLU terdekat'}: <b>${r.access==null?(isTTM()?'> 60 mnt':'—'):f1(r.access)+' '+unit()}</b><br>
   Charger terjangkau ≤${D.summary.th[0]} ${unit()}: <b>${fmt(r.near)}</b> · ≤${D.summary.th[1]} ${unit()}: <b>${fmt(r.far)}</b><br>
   ${isTTM()?'Desa terjangkau ≤30 mnt: <b>'+fmt(r.villages30)+'</b><br>':''}Charger di desa ini: <b>${fmt(r.chargers)}</b><br>Penduduk (Kontur 2023): <b>${fmt(r.pop)}</b> · ${fmt(r.pop/Math.max(r.area||1,.01))} jiwa/km²`).openPopup();});}}).addTo(map);
 sitesLayer=L.layerGroup().addTo(map);
 fetch('ttm/input/spklu_sites.csv').then(r=>r.text()).then(t=>{const rows=t.trim().split('\n').slice(1);rows.forEach(l=>{const c=l.match(/("[^"]*"|[^,]*)(,|$)/g).map(x=>x.replace(/,$/,'').replace(/^"|"$/g,''));
  const lon=+c[2],lat=+c[3];if(!isFinite(lon)||!isFinite(lat))return;L.circleMarker([lat,lon],{radius:2.6,color:'#fff',weight:.6,fillColor:c[8]==='PLN'?GOLD:BLUE,fillOpacity:.95}).bindTooltip(`${esc(c[1])} · ${c[6]} kW · ${c[7]} charger · ${esc(c[8])}`).addTo(sitesLayer);});}).catch(()=>{});
 $('ttSites').onchange=e=>{if(e.target.checked)sitesLayer.addTo(map);else map.removeLayer(sitesLayer);};
}
function styleOf(f){const r=VI.get(f.properties.id);const hide=S.kab!=='all'&&f.properties.k!==S.kab;
 return {color:'#ffffff',weight:hide?0.1:0.25,opacity:hide?.25:.6,fillColor:r?colorOf(valueOf(r)):'#eee',fillOpacity:hide?.08:.88};}
function restyle(){if(layer)layer.setStyle(styleOf);legend();$('ttMapTitle').textContent={access:isTTM()?'waktu tempuh ke desa ber-SPKLU terdekat':'jarak ke SPKLU terdekat (antara)',far:'charger terjangkau ≤'+D.summary.th[1]+' '+unit(),villages30:'desa terjangkau ≤30 menit',chargers:'charger di dalam desa',dens:'kepadatan penduduk'}[S.l];
 if(S.kab!=='all'&&layer){const b=L.latLngBounds([]);layer.eachLayer(l=>{if(l.feature.properties.k===S.kab)b.extend(l.getBounds());});if(b.isValid())map.fitBounds(b,{padding:[10,10]});}}

/* ---------- kartu & narasi ---------- */
function head(){
 const s=D.summary,T=isTTM();
 $('ttMode').textContent=T?'MODE: WAKTU TEMPUH r5r':'MODE ANTARA: JARAK GARIS LURUS';$('ttMode').className='mode '+s.mode;
 $('ttMeta').innerHTML=[[fmt(s.n_villages),'desa / kelurahan'],[jt(s.pop),'penduduk (Kontur 2023)'],[fmt(s.sites),'lokasi SPKLU'],[fmt(s.chargers),'unit charger'],[fmt(s.n_spklu_villages),'desa ber-SPKLU'],[T?fmt(s.rows):'—',T?'baris matriks r5r':'matriks r5r: belum dimuat']].map(x=>`<div><div class="n">${x[0]}</div><div class="t">${x[1]}</div></div>`).join('');
 if(!T){$('ttWarn').style.display='';$('ttWarn').innerHTML=`<b>Matriks waktu tempuh belum tersedia di repositori.</b> Angka di halaman ini memakai <b>jarak garis lurus</b> desa → lokasi SPKLU terdekat
  (ambang 5 dan 10 km) sebagai ukuran antara. Begitu <code>west_java_ttm_car.csv</code> (keluaran r5r supervisor) ditaruh di <code>ttm/input/</code> dan <code>python3 ttm/compute.py</code> dijalankan ulang,
  seluruh halaman — peta, KPI, Gini, indeks konsentrasi, kuintil — beralih otomatis ke <b>menit berkendara</b> (ambang 15 dan 30 menit) tanpa mengubah kode. Jarak garis lurus
  menilai akses terlalu baik di wilayah bergunung (Garut, Cianjur, Sukabumi selatan) dan terlalu buruk di koridor tol; bacalah pola, bukan angkanya.`;}
 const U=unit(),[t1,t2]=s.th;
 $('ttKpi').innerHTML=[
  [pct(s.pop_within1/s.pop),`penduduk ≤ ${t1} ${U} dari SPKLU`,`${jt(s.pop_within1)} jiwa · ${fmt(s.vil_within1)} desa`],
  [pct(s.pop_within2/s.pop),`penduduk ≤ ${t2} ${U}`,`${jt(s.pop_within2)} jiwa · ${fmt(s.vil_within2)} desa`],
  [jt(s.pop_beyond),T?'penduduk > 60 menit / tak terjangkau':`penduduk > ${t2} km`,`${pct(s.pop_beyond/s.pop)} dari area studi`],
  [f1(s.median_access_pop)+' '+U,'akses median (tertimbang penduduk)',`rata-rata ${f1(s.mean_access_pop)} ${U}`],
  [f3(s.gini_far),`Gini charger terjangkau ≤${t2} ${U}`,'antar desa, bobot penduduk — kesetaraan'],
  [f3(s.ci.density),'CI charger terjangkau ~ kepadatan','+ = terkonsentrasi di desa padat'],
  [s.ci.expend!=null?f3(s.ci.expend):'—','CI charger terjangkau ~ pengeluaran','Jabar 27 kab/kota · + = pro-kaya'],
  [f3(s.gini_kab_per100k),'Gini charger/100 rb antar kab/kota','36 kab/kota, bobot penduduk']
 ].map(k=>`<div class="kpi"><div class="l">${k[1]}</div><div class="v">${k[0]}</div><div class="s">${k[2]}</div></div>`).join('');
 $('ttSteps').innerHTML=[
  `<b>Area studi</b> mengikuti <code>java_ttm_01.R</code>: provinsi Jakarta Raya, Jawa Barat, Banten; Cilegon, Kota Serang, Lebak, Pandeglang, Serang, Kepulauan Seribu dibuang. Poligon desa HDX-BPS 2020 (kode BPS 10 digit) — ${fmt(s.n_villages)} desa.`,
  `<b>Titik asal</b> = satu titik yang dijamin di dalam tiap poligon desa (<code>st_point_on_surface</code> ↔ <code>representative_point</code>), bukan centroid.`,
  `<b>Stasiun</b>: ${fmt(s.sites)} lokasi SPKLU master nasional (Juni 2026) jatuh di area studi lewat <i>point-in-polygon</i> → ${fmt(s.n_spklu_villages)} desa ber-SPKLU, ${fmt(s.chargers)} unit charger.`,
  T?`<b>Waktu tempuh</b>: r5r (<code>travel_time_matrix</code>, mode CAR, keberangkatan Selasa 13 Mei 2025 14.00, maks 60 menit) atas ekstrak OSM Jawa Barat; ${fmt(s.rows)} pasangan asal–tujuan. Akses desa = waktu p50 ke desa ber-SPKLU terdekat; charger terjangkau = jumlah unit di desa-desa yang tercapai ≤15/≤30 menit.`
   :`<b>Akses (antara)</b>: jarak lingkaran besar dari titik desa ke lokasi SPKLU terdekat; charger terjangkau = unit dalam radius 5/10 km. Akan diganti waktu tempuh r5r (15/30 menit) saat matriks dimuat.`,
  `<b>Kebutuhan</b>: penduduk Kontur 2023 (H3 res 8, ~0,74 km²) dijatuhkan ke poligon desa → ${jt(s.pop)} jiwa. Semua pangsa, median, Gini, dan CI ditimbang penduduk desa, bukan jumlah desa.`,
  `<b>Kesetaraan</b>: Gini antar desa atas charger terjangkau; Gini antar kab/kota atas charger per 100 rb. <b>Ekuitas</b>: indeks konsentrasi (Wagstaff; Erreygers untuk variabel pangsa 0–1) dengan desa diurut menurut kepadatan, dan menurut pengeluaran per kapita / IPM kab/kota induk (Jabar).`
 ].map(t=>`<li>${t}</li>`).join('');
 const m=s.metros,jb=m.find(x=>x.key==='jabodetabek'),lu=m.find(x=>x.key==='luar'),q=s.quintiles_expend;
 $('ttRead').innerHTML=`<p><b>Kesetaraan</b> bertanya apakah akses sama rata. Jawabannya tidak: Gini charger terjangkau antar desa <b>${f3(s.gini_far)}</b>; ${pct(s.pop_within2/s.pop)} penduduk berada ≤${t2} ${U} dari SPKLU, tetapi ${jt(s.pop_beyond)} jiwa ${T?'tidak mencapai satu pun desa ber-SPKLU dalam 60 menit':'berjarak > '+t2+' km'}. Jabodetabek ${pct(jb.share2)} vs luar metropolitan ${pct(lu.share2)}; charger per 100 rb ${f2(jb.per100k)} vs ${f2(lu.per100k)} (${f1(jb.per100k/lu.per100k)}×).</p>
 <p style="margin-top:7px"><b>Ekuitas</b> bertanya apakah ketaksetaraan itu mengikuti kebutuhan. CI charger terjangkau terhadap kepadatan <b>${f3(s.ci.density)}</b>: akses terkonsentrasi di desa padat — sebagian wajar, karena di sanalah orang tinggal. ${q?`Tetapi terhadap pengeluaran per kapita kab/kota (Jabar) CI juga <b>${f3(s.ci.expend)}</b> (IPM ${f3(s.ci.ipm)}): kuintil termiskin ${pct(q[0].share2)} penduduknya ≤${t2} ${U}, kuintil terkaya ${pct(q[4].share2)}; charger terjangkau rata-rata ${f1(q[4].far)} vs ${f1(q[0].far)} unit (${f1(q[4].far/Math.max(q[0].far,.1))}×).`:''} Inilah pemisahan yang diminta: <i>unequal</i> sudah pasti; pertanyaan disertasinya adalah seberapa jauh ia <i>inequitable</i> — dan jawaban itu berbeda antar kawasan metropolitan.</p>`;
 if(!T){$('ttBtnV30').disabled=true;$('ttBtnV30').title='hanya tersedia pada mode waktu tempuh';$('ttBtnV30').style.opacity=.45;}
}
function charts(){
 const s=D.summary,U=unit(),h=s.hist,labs=h.edges.slice(0,-1).map((e,i)=>e+'–'+h.edges[i+1]);
 if(isTTM()){labs[labs.length-1]='55–60';}
 $('ttHistLab').textContent=isTTM()?'menit ke desa ber-SPKLU terdekat':'km ke SPKLU terdekat (antara)';
 mk('ttHist',{type:'bar',data:{labels:labs,datasets:[{label:'penduduk (jt)',data:h.pop.map(x=>x/1e6),backgroundColor:labs.map((_,i)=>MAGMA[Math.max(0,6-Math.floor(i*7/labs.length))]),borderRadius:4,yAxisID:'y'},
  {label:'desa',data:h.villages,type:'line',borderColor:NAVY,backgroundColor:NAVY,pointRadius:3,yAxisID:'y1',tension:.3}]},
  options:{plugins:{legend:{position:'bottom'}},scales:{y:{title:{display:true,text:'penduduk (juta)'},beginAtZero:true},y1:{position:'right',title:{display:true,text:'desa'},grid:{drawOnChartArea:false},beginAtZero:true},x:{title:{display:true,text:U}}}}});
 const top=h.pop[0]/s.pop;
 $('ttHistNote').innerHTML=`${pct(top)} penduduk berada di kelas pertama (≤${h.edges[1]} ${U}); ekor kanan adalah ${isTTM()?'desa yang hanya mencapai SPKLU setelah 45–60 menit':'desa pegunungan selatan dan pantai utara timur'} — populasinya kecil, tetapi inilah kelompok yang akan gagal di anak tangga pertama (<i>reachable</i>) tangga layanan proposal.`;
 const lz=s.lorenz_far;
 mk('ttLorenz',{type:'line',data:{datasets:[{label:'charger terjangkau ≤'+s.th[1]+' '+U+' (Gini '+f3(s.gini_far)+')',data:lz.map(p=>({x:p[0],y:p[1]})),borderColor:RED,backgroundColor:'rgba(214,68,60,.12)',fill:true,pointRadius:0,tension:.2},
  {label:'charger di desa per kapita (Gini '+f3(s.gini_chargers_village)+')',data:s.lorenz_pop_vs_chargers.map(p=>({x:p[0],y:p[1]})),borderColor:BLUE,pointRadius:0,borderDash:[5,4],tension:.2},
  {label:'kesetaraan sempurna',data:[{x:0,y:0},{x:1,y:1}],borderColor:MUT,pointRadius:0,borderDash:[2,3]}]},
  options:{plugins:{legend:{position:'bottom'}},scales:{x:{type:'linear',min:0,max:1,title:{display:true,text:'kumulatif penduduk (diurut dari akses terburuk)'}},y:{min:0,max:1,title:{display:true,text:'kumulatif charger terjangkau'}}}}});
 $('ttLorenzNote').innerHTML=`Garis merah: <b>akses</b> (charger yang bisa dicapai) — lebih merata daripada garis biru, <b>kepemilikan</b> (charger yang berlokasi di desa sendiri, Gini ${f3(s.gini_chargers_village)}), karena satu charger melayani banyak desa sekitarnya. Inilah alasan berpindah dari menghitung charger per wilayah ke menghitung jangkauan dari tiap desa.`;
 const q=s.quintiles_expend;
 if(q){mk('ttQuint',{type:'bar',data:{labels:q.map(x=>'Q'+x.q+(x.q===1?' termiskin':x.q===5?' terkaya':'')),datasets:[{label:'penduduk ≤'+s.th[1]+' '+U+' (%)',data:q.map(x=>100*x.share2),backgroundColor:NAVY,borderRadius:4,yAxisID:'y'},
  {label:'penduduk ≤'+s.th[0]+' '+U+' (%)',data:q.map(x=>100*x.share1),backgroundColor:GOLD,borderRadius:4,yAxisID:'y'},
  {label:'charger terjangkau rata-rata',data:q.map(x=>x.far),type:'line',borderColor:RED,backgroundColor:RED,yAxisID:'y1',tension:.3}]},
  options:{plugins:{legend:{position:'bottom'}},scales:{y:{min:0,max:100,title:{display:true,text:'% penduduk'}},y1:{position:'right',grid:{drawOnChartArea:false},title:{display:true,text:'unit charger'},beginAtZero:true}}}});
  $('ttQuintNote').innerHTML=`Penduduk Jawa Barat (${jt(s.ci.n_jabar_pop)} jiwa) dibagi lima kuintil menurut pengeluaran per kapita kab/kota induk (BPS 2024). Gradien dari Q1 ke Q5 adalah <b>ekuitas vertikal</b>; CI Erreygers pangsa ≤${s.th[1]} ${U} ~ pengeluaran = <b>${f3(s.ci.expend_share2)}</b>. Catatan: variabel peringkat masih tingkat kab/kota — Meta RWI atau PODES akan menurunkannya ke desa.`;}
 else{$('ttQuintNote').textContent='Data sosial-ekonomi kab/kota belum tersedia.';}
}
function metroTable(){
 const s=D.summary,U=unit();
 $('ttMetro').innerHTML=`<table><thead><tr><th>Kawasan</th><th class="n">Kab/kota</th><th class="n">Penduduk</th><th class="n">Charger</th><th class="n">per 100 rb</th><th class="n">≤${s.th[0]} ${U}</th><th class="n">≤${s.th[1]} ${U}</th><th class="n">Median</th><th class="n">Charger terjangkau</th><th class="n">Gini</th></tr></thead><tbody>`+
  s.metros.map(m=>`<tr><td><b>${esc(m.label)}</b></td><td class="n">${m.n_kab}</td><td class="n">${jt(m.pop)}</td><td class="n">${fmt(m.chargers)}</td><td class="n">${f2(m.per100k)}</td><td class="n"><span class="bar"><i style="width:${100*m.share1}%;background:${GOLD}"></i></span>${pct(m.share1)}</td><td class="n"><span class="bar"><i style="width:${100*m.share2}%;background:${NAVY}"></i></span>${pct(m.share2)}</td><td class="n">${f1(m.median)} ${U}</td><td class="n">${f1(m.far_mean)}</td><td class="n">${f3(m.gini_far)}</td></tr>`).join('')+'</tbody></table>';
}
function table(){
 const s=D.summary,U=unit();
 const cols=[['name','Kab/kota'],['prov','Prov.'],['n','Desa'],['pop','Penduduk'],['sites','Lokasi'],['chargers','Charger'],['per100k','per 100 rb'],['share1','≤'+s.th[0]+' '+U],['share2','≤'+s.th[1]+' '+U],['median','Median'],['far_mean','Charger terjangkau'],['gini_far','Gini'],['expend','Pengeluaran/kap'],['ipm','IPM'],['p0','P0 %']];
 const rows=[...D.kabs].sort((a,b)=>{const x=a[sortK],y=b[sortK];if(x==null)return 1;if(y==null)return -1;return (typeof x==='string'?x.localeCompare(y):x-y)*sortD;});
 $('ttTable').innerHTML=`<table><thead><tr>${cols.map(c=>`<th data-k="${c[0]}" style="cursor:pointer${['name','prov'].includes(c[0])?'':';text-align:right'}">${c[1]}${sortK===c[0]?(sortD<0?' ▼':' ▲'):''}</th>`).join('')}</tr></thead><tbody>`+
  rows.map(r=>`<tr data-k="${r.code}" style="cursor:pointer"><td><b>${esc(r.name)}</b> <span style="color:${MUT};font-size:10px">${r.metro==='luar'?'':esc(s.metros.find(m=>m.key===r.metro).label)}</span></td><td>${esc(r.prov.replace('Jawa Barat','Jabar').replace('DKI Jakarta','DKI'))}</td><td class="n">${fmt(r.n)}</td><td class="n">${jt(r.pop)}</td><td class="n">${fmt(r.sites)}</td><td class="n">${fmt(r.chargers)}</td><td class="n">${f2(r.per100k)}</td>
   <td class="n"><span class="bar"><i style="width:${100*r.share1}%;background:${GOLD}"></i></span>${pct(r.share1)}</td><td class="n"><span class="bar"><i style="width:${100*r.share2}%;background:${NAVY}"></i></span>${pct(r.share2)}</td><td class="n">${f1(r.median)}</td><td class="n">${f1(r.far_mean)}</td><td class="n">${f3(r.gini_far)}</td><td class="n">${r.expend!=null?fmt(r.expend):'—'}</td><td class="n">${r.ipm!=null?f1(r.ipm):'—'}</td><td class="n">${r.p0!=null?f1(r.p0):'—'}</td></tr>`).join('')+'</tbody></table>';
 $('ttTable').querySelectorAll('th').forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(sortK===k)sortD*=-1;else{sortK=k;sortD=['name','prov'].includes(k)?1:-1;}table();});
 $('ttTable').querySelectorAll('tbody tr').forEach(tr=>tr.onclick=()=>{S.kab=tr.dataset.k;$('ttKab').value=S.kab;restyle();$('ttMap').scrollIntoView({behavior:'smooth',block:'center'});});
}
function next(){
 const T=isTTM();
 $('ttNext').innerHTML=[
  ['done','Pilot pipeline Jabar–Jakarta–Tangerang','Rantai koordinat → desa → akses → kebutuhan → Gini/CI berjalan ujung ke ujung (halaman ini).'],
  [T?'done':'wait','Matriks waktu tempuh r5r dimuat','Mengganti jarak garis lurus dengan menit berkendara (p50) dan ambang 15/30 menit; menghidupkan lapisan "desa terjangkau ≤30 mnt" yang mereplikasi peta supervisor.'],
  ['todo','Replikasi ke kawasan metropolitan nasional','Ekstrak OSM per kawasan (Geofabrik) + GADM level 4 + master SPKLU nasional → satu tabel akses per desa untuk Jabodetabek, Bandung Raya, Gerbangkertosusila, Mebidangro, Kedungsepur, Mamminasata, Sarbagita, Palembang, Yogyakarta, Cirebon.'],
  ['todo','Perbandingan (in)equality antar-metropolitan','Gini akses & kurva Lorenz per kawasan; Theil dalam-vs-antar kawasan; peringkat kawasan menurut pangsa penduduk ≤15/30 menit.'],
  ['todo','Perbandingan (in)equity antar-metropolitan','CI akses terhadap pengeluaran/IPM/RWI per kawasan; kuintil termiskin vs terkaya di tiap kawasan; uji apakah gradien pro-kaya sama kuatnya di semua kota.'],
  ['todo','Dari jangkauan ke kecukupan (tangga layanan)','Anak tangga 1 (reachable) = ≤15/30 menit; anak tangga 2 (sufficient power) = E2SFCA kW per rumah tangga tanpa charging rumah dalam catchment waktu tempuh; anak tangga 3–5 dari transaksi dan ulasan.'],
  ['todo','Penyebut kebutuhan N2','Mengganti total penduduk dengan rumah tangga yang bergantung pada charging publik (PLN ≥2.200 VA rumah tapak / PODES) agar pangsa terjangkau tidak menilai lebih baik kawasan padat apartemen.'],
  ['todo','Kurva spesifikasi','Ambang (15/30/45 menit) × titik asal (desa/heksagon) × penyebut (N1/N2) × perlakuan charger koridor tol → apakah peringkat kawasan stabil.']
 ].map(x=>`<div class="it"><span class="st ${x[0]}">${{done:'SELESAI',wait:'MENUNGGU DATA',todo:'BERIKUTNYA'}[x[0]]}</span><b>${x[1]}</b>${x[2]}</div>`).join('');
}

/* ---------- init ---------- */
window.initTTM=async function(){
 if(built){if(map)setTimeout(()=>map.invalidateSize(),50);return;}built=true;
 try{
  if(typeof L==='undefined'){await loadScript('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js');}
  const [d,g]=await Promise.all([fetch('ttm/ttm.json').then(r=>{if(!r.ok)throw new Error('ttm.json');return r.json();}),fetch('ttm/input/villages_simplified.geojson').then(r=>{if(!r.ok)throw new Error('geojson');return r.json();})]);
  D=d;GJ=g;
  const vc=D.village_cols;D.villages.forEach(a=>{const r={};vc.forEach((c,i)=>r[c]=a[i]);VI.set(r.id,r);});
  $('ttLoading').style.display='none';
  const kabs=[...D.kabs].sort((a,b)=>a.name.localeCompare(b.name));$('ttKab').innerHTML='<option value="all">Semua (36 kab/kota)</option>'+kabs.map(k=>`<option value="${k.code}">${esc(k.name)}</option>`).join('');
  $('ttKab').onchange=e=>{S.kab=e.target.value;restyle();if(S.kab==='all')map.setView([-6.6,107.3],8);};
  $('ttLayerSeg').querySelectorAll('button').forEach(b=>b.onclick=()=>{if(b.disabled)return;S.l=b.dataset.l;$('ttLayerSeg').querySelectorAll('button').forEach(x=>x.classList.toggle('active',x===b));restyle();});
  head();buildMap();legend();charts();metroTable();table();next();
  setTimeout(()=>map.invalidateSize(),80);
 }catch(e){$('ttLoading').innerHTML='Gagal memuat: '+esc(e.message)+'. Jalankan <code>python3 ttm/compute.py</code> lalu muat ulang.';console.error(e);}
};
/* tautan langsung #tab=ttm: gotoTab() sudah berjalan sebelum skrip ini terdefinisi, jadi panggil sendiri bila halaman sudah aktif */
if(document.querySelector('#p-ttm.active')||(location.hash.match(/tab=([a-z0-9_-]+)/)||[])[1]==='ttm')setTimeout(window.initTTM,60);
})();
