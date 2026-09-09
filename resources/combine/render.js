
/* ============ KOMBINASI — data repo × sumber terbuka terkatalog (D.kb) ============ */
(function(){
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const md=s=>esc(s).replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>').replace(/\*([^*]+)\*/g,'<i>$1</i>');
const fmt=n=>(n==null||isNaN(n))?'—':(+n).toLocaleString('id-ID');
const NAVY='#16305f',GOLD='#d4af37',BLUE='#3a6ea5',GREEN='#2e9e5b',RED='#d6443c',MUT='#9aa6bd';
const C={};let K=null,built=false;
function mk(id,cfg){if(C[id])C[id].destroy();const el=$(id);if(!el||typeof Chart==='undefined')return;C[id]=new Chart(el,cfg);}
const noLeg={legend:{display:false}};
const yAx=(t)=>({beginAtZero:true,grid:{color:'#eef1f6'},title:{display:!!t,text:t,font:{size:10}},ticks:{font:{size:10}}});
const xAx=(t)=>({grid:{display:false},title:{display:!!t,text:t,font:{size:10}},ticks:{font:{size:10}}});

/* ---------- sumber ---------- */
function srcChip(s){
 if(s.t==='repo')return `<span class="sc repo">📦 <b>data repo</b> · ${esc(s.label)}</span>`;
 const gh=/^[\w.-]+\/[\w.-]+$/.test(s.id);
 const url=gh?('https://github.com/'+s.id):s.id;
 const q=gh?s.id.split('/')[1]:s.label.split('—')[0].trim();
 return `<span class="sc cat" data-q="${esc(q)}" title="lihat entri ini di Repositori Riset">🧰 <b>katalog</b> · ${esc(s.label)}</span>`
      + `<a class="sc" href="${esc(url)}" target="_blank" rel="noopener" title="buka sumbernya">↗</a>`;
}

/* ---------- grafik per kombinasi ---------- */
function chartFor(c){
 if(c.id==='ladder'){
  return '<div class="kbchart"><div class="ct">Daya nominal vs daya yang benar-benar mengalir</div><div style="height:290px"><canvas id="kbLadder"></canvas></div>'+
   '<div class="ct" style="margin-top:14px">Pemanfaatan daya terpasang (median sesi)</div><div style="height:150px"><canvas id="kbUtil"></canvas></div></div>';
 }
 if(c.id==='surya'){
  return '<div class="kbchart"><div class="ct">Profil per jam — pengisian vs produksi surya (pangsa harian, %)</div><div style="height:290px"><canvas id="kbSun"></canvas></div>'+
   '<div class="ct" style="margin-top:14px">Swasembada menurut ukuran array PV (× energi harian)</div><div style="height:150px"><canvas id="kbSize"></canvas></div></div>';
 }
 if(c.id==='gurun'){
  const pins=c.pins.map(p=>`<tr><td>${p.lat.toFixed(6)}, ${p.lon.toFixed(6)}</td><td class="n">${p.n}</td><td class="n">${p.kab}</td></tr>`).join('');
  const rows=c.deserts.map(d=>`<tr><td>${d.lat.toFixed(2)}, ${d.lon.toFixed(2)}</td><td class="n">${d.owners}</td><td class="n">${d.km.toFixed(1)} km</td></tr>`).join('');
  return '<div class="kbchart"><div class="ct">Pin default yang dibuang <span class="warn">bukan alamat</span></div>'+
   '<table class="kt"><thead><tr><th>koordinat</th><th style="text-align:right">pemohon</th><th style="text-align:right">kabupaten berbeda</th></tr></thead><tbody>'+pins+'</tbody></table>'+
   '<div style="font-size:10.5px;color:var(--mut);margin:9px 0 4px;line-height:1.6">Satu koordinat enam desimal dipakai bersama pemohon dari belasan kabupaten — pin bawaan peta di sekitar Monas, bukan rumah. '+c.pinned+' pemohon dibuang sebelum gurun dihitung.</div>'+
   '<div class="ct" style="margin-top:14px">Heksagon gurun terbesar setelah dibersihkan (H3 res '+c.res+', rusuk '+c.edge+' km)</div>'+
   '<table class="kt"><thead><tr><th>pusat heksagon</th><th style="text-align:right">pemilik EV</th><th style="text-align:right">SPKLU terdekat</th></tr></thead><tbody>'+rows+'</tbody></table></div>';
 }
 if(c.id==='standar'){
  const rows=c.stds.map(s=>`<tr><td><b>${esc(s.std)}</b></td><td class="n">${fmt(s.n)}</td><td class="n">${fmt(Math.round(s.kwh))}</td><td class="n">${s.pct}%</td><td class="n">${s.chargers}</td></tr>`).join('');
  return '<div class="kbchart"><div class="ct">Pangsa energi menurut standar konektor</div><div style="height:230px"><canvas id="kbStd"></canvas></div>'+
   '<table class="kt" style="margin-top:12px"><thead><tr><th>standar</th><th style="text-align:right">sesi</th><th style="text-align:right">kWh</th><th style="text-align:right">% energi</th><th style="text-align:right">charger</th></tr></thead><tbody>'+rows+'</tbody></table></div>';
 }
 if(c.id==='jaringan'){
  return '<div class="kbchart"><div class="ct">Energi bulanan per situs menurut jarak ke gardu induk</div><div style="height:250px"><canvas id="kbGi"></canvas></div>'+
   '<div class="ct" style="margin-top:14px">Bauran kapasitas pembangkit Jawa Barat (MW)</div><div style="height:190px"><canvas id="kbGen"></canvas></div></div>';
 }
 if(c.id==='karbon'){
  return '<div class="kbchart"><div class="ct">Penurunan emisi sebulan (tCO₂) — dua jalur</div><div style="height:250px"><canvas id="kbCo2"></canvas></div>'+
   '<div style="font-size:10.5px;color:var(--mut);margin-top:9px;line-height:1.6">Jalur B ditampilkan pada rentang asumsinya (selisih faktor emisi marjinal siang–malam 8–30 persen). Bahkan pada batas atas, jalur A tetap jauh lebih besar.</div></div>';
 }
 return '';
}

/* grafik yang perlu dibuat setelah markup masuk DOM */
function chartsAfter(c){
 if(c.id==='ladder'){
  const b=c.bands;
  mk('kbLadder',{data:{labels:b.map(x=>x.rated+' kW'),datasets:[
    {type:'bar',label:'daya terpasang',data:b.map(x=>x.rated),backgroundColor:'#dde5f2',borderRadius:3,order:3},
    {type:'bar',label:'terkirim p95',data:b.map(x=>x.p95),backgroundColor:GOLD,borderRadius:3,order:2},
    {type:'bar',label:'terkirim median',data:b.map(x=>x.p50),backgroundColor:NAVY,borderRadius:3,order:1},
    {type:'line',label:'langit-langit armada',data:b.map(()=>c.fleet_dc),borderColor:RED,borderWidth:2,borderDash:[6,4],pointRadius:0,order:0}
   ]},options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},
    scales:{y:yAx('kW'),x:xAx('daya nominal charger')}}});
  mk('kbUtil',{type:'bar',data:{labels:b.map(x=>x.rated+' kW'),datasets:[{data:b.map(x=>x.util),
    backgroundColor:b.map(x=>x.util>=60?GREEN:x.util>=35?GOLD:RED),borderRadius:3}]},
   options:{maintainAspectRatio:false,plugins:{...noLeg,tooltip:{callbacks:{label:x=>x.raw+'% daya nominal terpakai'}}},
    scales:{y:yAx('% terpakai'),x:xAx('')}}});
 }
 if(c.id==='surya'){
  mk('kbSun',{data:{labels:c.hours.map(h=>h.h),datasets:[
    {type:'line',label:'produksi surya (langit cerah)',data:c.hours.map(h=>h.pv),borderColor:GOLD,backgroundColor:'rgba(212,175,55,.25)',fill:true,tension:.35,pointRadius:0,borderWidth:2},
    {type:'line',label:'energi pengisian SPKLU',data:c.hours.map(h=>h.chg),borderColor:NAVY,backgroundColor:'rgba(22,48,95,.10)',fill:true,tension:.35,pointRadius:0,borderWidth:2}
   ]},options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},
    scales:{y:yAx('% energi harian'),x:xAx('jam (WIB)')}}});
  mk('kbSize',{type:'bar',data:{labels:c.sizes.map(s=>s.k+'×'),datasets:[{data:c.sizes.map(s=>s.sc),
    backgroundColor:c.sizes.map(s=>s.k===1?NAVY:'#c3d1e6'),borderRadius:3}]},
   options:{maintainAspectRatio:false,plugins:{...noLeg,tooltip:{callbacks:{label:x=>x.raw+'% energi langsung dari PV'}}},
    scales:{y:yAx('% swasembada'),x:xAx('ukuran PV relatif terhadap energi harian')}}});
 }
 if(c.id==='standar'){
  mk('kbStd',{type:'doughnut',data:{labels:c.stds.map(s=>s.std),datasets:[{data:c.stds.map(s=>s.pct),
    backgroundColor:[NAVY,GOLD,RED,BLUE,MUT]}]},options:{maintainAspectRatio:false,cutout:'58%',
    plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}},
    tooltip:{callbacks:{label:x=>x.label+': '+x.raw+'% energi'}}}}});
 }
 if(c.id==='jaringan'){
  mk('kbGi',{data:{labels:c.quartiles.map(q=>q.q+' · '+q.gi_km+' km'),datasets:[
    {type:'bar',label:'energi median per situs (kWh/bulan)',data:c.quartiles.map(q=>q.kwh_med),backgroundColor:NAVY,borderRadius:3,yAxisID:'y'},
    {type:'line',label:'jarak median ke gardu induk (km)',data:c.quartiles.map(q=>q.gi_km),borderColor:GOLD,borderWidth:2,pointRadius:4,pointBackgroundColor:GOLD,yAxisID:'y1',tension:.3}
   ]},options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},
    scales:{y:yAx('kWh/bulan'),y1:{position:'right',beginAtZero:true,grid:{display:false},title:{display:true,text:'km',font:{size:10}},ticks:{font:{size:10}}},x:xAx('kuartil jarak ke gardu induk')}}});
  const g=c.genmix.filter(x=>x.mw>0).slice(0,10);
  mk('kbGen',{type:'bar',data:{labels:g.map(x=>x.t),datasets:[{data:g.map(x=>x.mw),
    backgroundColor:g.map(x=>x.re?GREEN:'#6b7686'),borderRadius:3}]},
   options:{indexAxis:'y',maintainAspectRatio:false,plugins:{...noLeg,tooltip:{callbacks:{label:x=>fmt(x.raw)+' MW'+(g[x.dataIndex].re?' · terbarukan':'')}}},
    scales:{x:yAx('MW'),y:xAx('')}}});
 }
 if(c.id==='karbon'){
  mk('kbCo2',{type:'bar',data:{labels:['Jalur A — PV di situs','Jalur B — geser jam (8%)','Jalur B — batas atas (30%)'],
   datasets:[{data:[c.pv,c.shift,c.shift_hi],backgroundColor:[GOLD,'#c3d1e6','#8fa6c6'],borderRadius:4}]},
   options:{maintainAspectRatio:false,plugins:{...noLeg,tooltip:{callbacks:{label:x=>fmt(Math.round(x.raw))+' tCO₂/bulan'}}},
    scales:{y:yAx('tCO₂ per bulan'),x:xAx('')}}});
 }
}

/* ---------- kartu ---------- */
function block(c){
 return `<div class="kb" id="kb-${c.id}">
  <h3>${c.icon} ${esc(c.title)}</h3>
  <div class="q">${esc(c.question)}</div>
  <div class="src"><span class="lbl">disambungkan dari</span>${c.sources.map(srcChip).join('')}</div>
  <div class="kpis4">${c.kpi.map(k=>`<div class="kpi4"><div class="v">${esc(k.v)}</div><div class="t">${esc(k.t)}</div></div>`).join('')}</div>
  <div class="kbbody">
   ${chartFor(c)}
   <div><div class="ins">${md(c.insight)}</div><div class="act">${md(c.action)}</div></div>
  </div>
  <details class="mc"><summary>Metode, batas keberlakuan${c.fleet?' & armada yang dipakai':''}</summary>
   <div class="mb"><span class="k">Metode</span>${esc(c.method)}
   <span class="k">Batas keberlakuan</span>${esc(c.caveat)}
   ${c.fleet?fleetTable(c):''}</div></details>
 </div>`;
}
function fleetTable(c){
 const f=c.fleet.slice(0,14);
 return '<span class="k">Armada Jawa Barat yang dipakai untuk langit-langit daya</span>'+
  '<table class="kt"><thead><tr><th>merek</th><th style="text-align:right">pemilik</th><th style="text-align:right">DC maks (kW)</th><th>rentang model</th></tr></thead><tbody>'+
  f.map(x=>`<tr><td>${esc(x.brand)}${x.assumed?' <span class="warn">anggapan</span>':''}</td><td class="n">${fmt(x.n)}</td><td class="n">${x.dc}</td><td>${x.lo===x.hi?'—':x.lo+'–'+x.hi}</td></tr>`).join('')+
  '</tbody></table>';
}

function render(){
 $('kbList').innerHTML=K.combos.map(block).join('');
 K.combos.forEach(chartsAfter);
 $('kbList').querySelectorAll('.sc.cat').forEach(el=>el.onclick=()=>{if(window.rsFind)window.rsFind(el.dataset.q);});
 $('kbNav').innerHTML=K.combos.map((c,i)=>`<div class="kbn${i===0?' active':''}" data-i="${c.id}">${c.icon} ${esc(c.title.split('—')[0].trim())}</div>`).join('');
 $('kbNav').querySelectorAll('.kbn').forEach(el=>el.onclick=()=>{
  $('kbNav').querySelectorAll('.kbn').forEach(x=>x.classList.remove('active'));el.classList.add('active');
  const t=$('kb-'+el.dataset.i);if(t)t.scrollIntoView({behavior:'smooth',block:'start'});});
}

window.initCombine=function(){
 if(built)return;
 K=(typeof D!=="undefined"&&D.kb)||null;
 if(!K){$('kbList').innerHTML='<div class="kb">Payload D.kb tidak ditemukan — jalankan <code>python3 resources/combine/inject.py</code></div>';return;}
 built=true;
 const m=K.meta;
 $('kbMeta').innerHTML=[[m.combos,'kombinasi'],[fmt(m.sessions),'sesi dipakai'],[(m.kwh/1e6).toFixed(2)+' GWh','energi'],
  [fmt(m.sites),'situs SPKLU'],[fmt(m.owners),'rumah pemilik EV'],[m.generated,'dihitung']]
  .map(x=>`<div><div class="n">${esc(x[0])}</div><div class="t">${esc(x[1])}</div></div>`).join('');
 $('kbFoot').innerHTML='Seluruh angka di halaman ini dihitung ulang oleh <code>resources/combine/prepare.py</code> '+
  'dari berkas mentah di akar repositori — tidak ada yang diketik tangan. Periode data '+esc(m.periode)+'. '+
  'Pustaka: pvlib '+esc(m.libs.pvlib)+' · h3 '+esc(m.libs.h3)+' · pandas '+esc(m.libs.pandas)+' · numpy '+esc(m.libs.numpy)+'. '+
  'Klik chip <b>katalog</b> untuk melompat ke entri sumbernya di tab Repositori Riset.';
 render();
};
})();
