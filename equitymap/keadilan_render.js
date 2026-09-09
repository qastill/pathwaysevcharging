
/* ============ EKUITAS vs KESETARAAN — analisis mendalam nasional (D.kd) ============ */
(function(){
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>(n==null||isNaN(n))?'—':Math.round(+n).toLocaleString('id-ID');
const f1=n=>(n==null||isNaN(n))?'—':(+n).toLocaleString('id-ID',{maximumFractionDigits:1,minimumFractionDigits:1});
const f2=n=>(n==null||isNaN(n))?'—':(+n).toLocaleString('id-ID',{maximumFractionDigits:2,minimumFractionDigits:2});
const jt=n=>n>=1e6?(n/1e6).toLocaleString('id-ID',{maximumFractionDigits:1})+' jt':n>=1e3?(n/1e3).toLocaleString('id-ID',{maximumFractionDigits:0})+' rb':fmt(n);
const NAVY='#16305f',GOLD='#d4af37',BLUE='#3a6ea5',GREEN='#2e9e5b',RED='#d6443c',ORANGE='#e8742c',MUT='#9aa6bd',PURPLE='#8a6fb0';
const C={};let built=false;
function mk(id,cfg){if(C[id])C[id].destroy();const el=$(id);if(!el||typeof Chart==='undefined')return;C[id]=new Chart(el,cfg);}
const yAx=t=>({beginAtZero:true,grid:{color:'#eef1f6'},title:{display:!!t,text:t,font:{size:10}},ticks:{font:{size:10}}});
const xAx=t=>({grid:{display:false},title:{display:!!t,text:t,font:{size:10}},ticks:{font:{size:10}}});
const unit01=t=>({type:'linear',min:0,max:1,title:{display:true,text:t,font:{size:9}},ticks:{font:{size:9}},grid:{color:'#eef1f6'}});
const kv=(arr)=>arr.map(x=>`<div class="${x[2]||''}"><div class="v">${x[0]}</div><div class="t">${x[1]}</div></div>`).join('');
const diag=()=>({label:'kesetaraan sempurna',data:[{x:0,y:0},{x:1,y:1}],borderColor:MUT,borderDash:[5,4],pointRadius:0,borderWidth:1.5});
const pts=a=>a.map(p=>({x:p[0],y:p[1]}));

function build(){
 const K=D.kd;if(!K)return;const W=K.why,G=K.gini,T=K.theil,CI=K.ci,CV=K.coverage,DF=K.deficit;
 $('kdMeta').innerHTML=[[G.chargers,'Gini charger/kapita (kab)'],[T.prov.between_pct+'%','ketimpangan antar-provinsi (Theil)'],[K.ratio2020+'×','rasio 20:20'],[CI.hdi,'CI terhadap IPM (pro-kaya)'],[fmt(DF.total),'charger defisit menuju kesetaraan'],[W.kab_zero,'kabupaten tanpa charger']]
  .map(x=>`<div><div class="n">${x[0]}</div><div class="t">${x[1]}</div></div>`).join('');

 /* ---- 1 kesetaraan */
 $('kdKv1').innerHTML=kv([[G.chargers,'Gini charger per kapita, 508 kab/kota','g'],[G.kw,'Gini kW terpasang per kapita'],[G.sites,'Gini situs per kapita'],[G.access,'Gini akses (penduduk ≤10 km)'],[G.hex,'Gini per heksagon (charger dalam 10 km)'],[W.median100k+' vs '+W.mean100k,'median vs rata-rata charger/100 rb']]);
 const L=G.lorenz;
 mk('cKdLorenz',{type:'line',data:{datasets:[
   {label:'charger (G '+G.chargers+')',data:pts(L.chargers),borderColor:NAVY,pointRadius:0,borderWidth:2.2,tension:.1},
   {label:'kW terpasang (G '+G.kw+')',data:pts(L.kw),borderColor:RED,pointRadius:0,borderWidth:1.8,tension:.1},
   {label:'situs (G '+G.sites+')',data:pts(L.sites),borderColor:BLUE,pointRadius:0,borderWidth:1.8,tension:.1},
   {label:'akses ≤10 km (G '+G.access+')',data:pts(L.access),borderColor:GREEN,pointRadius:0,borderWidth:1.8,tension:.1},
   {label:'per heksagon, charger dalam 10 km (G '+G.hex+')',data:pts(L.hex),borderColor:PURPLE,borderDash:[3,3],pointRadius:0,borderWidth:1.6,tension:.1},diag()]},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}},tooltip:{callbacks:{label:x=>`${x.dataset.label}: ${Math.round(x.raw.x*100)}% penduduk → ${Math.round(x.raw.y*100)}%`}}},
   scales:{x:unit01('kumulatif penduduk (unit diurut dari porsi terkecil)'),y:unit01('kumulatif ukuran')}}});
 mk('cKdVar',{type:'bar',data:{labels:G.variants.map(v=>v[0]),datasets:[{data:G.variants.map(v=>v[1]),backgroundColor:G.variants.map((v,i)=>i?BLUE:NAVY),borderRadius:3}]},
  options:{indexAxis:'y',maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{min:0,max:1,grid:{color:'#eef1f6'},ticks:{font:{size:10}}},y:{grid:{display:false},ticks:{font:{size:10}}}}}});
 mk('cKdTheil',{type:'bar',data:{labels:['Dikelompokkan per provinsi','Dikelompokkan kota vs kabupaten'],datasets:[
   {label:'antar-kelompok',data:[T.prov.between,T.kota.between],backgroundColor:NAVY,stack:'s'},{label:'dalam-kelompok',data:[T.prov.within,T.kota.within],backgroundColor:'#c9d4e8',stack:'s'}]},
  options:{indexAxis:'y',maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}},tooltip:{callbacks:{label:x=>x.dataset.label+': '+x.raw.toFixed(3)}}},scales:{x:{stacked:true,grid:{color:'#eef1f6'},ticks:{font:{size:10}},title:{display:true,text:'Theil T = '+T.prov.T,font:{size:10}}},y:{stacked:true,grid:{display:false},ticks:{font:{size:10}}}}}});
 const noDki=G.variants[1][1],kotaOnly=G.variants[4][1],kabOnly=G.variants[5][1];
 $('kdWhy1').innerHTML=`<b>Mengapa Gini-nya 0,595.</b><ol>
  <li><b>Bukan kabut, tapi tumpukan.</b> 10 kabupaten/kota teratas memegang <b>${W.top10_share}%</b> charger untuk ${W.top10_pop_share}% penduduk; DKI Jakarta sendiri ${W.dki_ch}% charger untuk ${W.dki_pop}% penduduk (Jakarta Selatan ${W.top10[0].per100k} charger/100 rb — ${Math.round(W.top10[0].per100k/W.mean100k)}× rata-rata nasional). Di ujung lain, <b>${W.kab_zero} kabupaten</b> berpenduduk ${jt(W.pop_zero)} jiwa (${W.pct_pop_zero}%) tidak punya satu charger operasional pun, dan ${W.kab_below_mean} dari ${W.n_kab} kabupaten (${Math.round(100*W.kab_below_mean/W.n_kab)}%) berada di bawah rata-rata. Kurva Lorenz karena itu menempel di lantai untuk 20% penduduk pertama (hanya ${K.s20}% charger) dan melonjak di ekor (20% teratas memegang ${K.s80}%): rasio 20:20 = <b>${K.ratio2020}×</b>, Palma ${K.palma}.</li>
  <li><b>Kapasitas lebih timpang daripada jumlah.</b> Gini kW (${G.kw}) &gt; Gini charger (${G.chargers}) &gt; Gini situs (${G.sites}): daerah yang sudah punya situs juga mendapat charger lebih banyak per situs dan daya lebih besar (DC). Ketimpangan bertingkat — situs → unit → kW — sehingga ukuran "jumlah situs" saja meremehkannya.</li>
  <li><b>Akses jauh lebih setara daripada kepemilikan.</b> Gini akses (penduduk ≤10 km) hanya ${G.access}: satu situs melayani banyak orang sekaligus, jadi <i>keberadaan</i> charger tersebar lebih merata daripada <i>jumlahnya</i>. Inilah sebabnya 63,7% penduduk "tercakup" bisa hidup berdampingan dengan Gini 0,6 — cakupan mengukur ada/tidak, Gini mengukur berapa banyak.</li>
  <li><b>Per heksagon lebih timpang lagi</b> (${G.hex}) karena di dalam satu kabupaten pun charger mengelompok di pusat kota dan koridor tol; angka kabupaten menyembunyikan ketimpangan intra-kabupaten.</li>
  <li><b>Lapisan penyumbang.</b> Membuang DKI menurunkan Gini ke ${noDki}; di dalam kota saja ${kotaOnly}, di dalam kabupaten saja ${kabOnly} — ketimpangan tetap tinggi di semua lapisan. Theil menegaskan: <b>${T.prov.between_pct}%</b> ketimpangan adalah <i>antar-provinsi</i> (${T.prov.between} dari ${T.prov.T}), sisanya dalam-provinsi; bila dikelompokkan kota vs kabupaten, ${T.kota.between_pct}% adalah celah kota–kabupaten. Jadi ketimpangan nasional terutama soal <i>provinsi mana</i>, baru soal <i>kota atau bukan</i>.</li></ol>`;

 /* ---- 2 kota/kab, jawa */
 const grp=K.kota_kab.concat(K.java);
 mk('cKdGroups',{type:'bar',data:{labels:grp.map(g=>g.label),datasets:[{label:'charger /100 rb',data:grp.map(g=>g.per100k),backgroundColor:NAVY,yAxisID:'y'},{label:'≤10 km %',data:grp.map(g=>g.within10),backgroundColor:GREEN,yAxisID:'y2'},{label:'>25 km %',data:grp.map(g=>g.beyond25),backgroundColor:RED,yAxisID:'y2'}]},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},scales:{y:yAx('charger /100 rb'),y2:{position:'right',beginAtZero:true,max:100,grid:{display:false},title:{display:true,text:'% penduduk',font:{size:10}},ticks:{font:{size:10}}},x:xAx('')}}});
 mk('cKdShare',{type:'bar',data:{labels:['Kota','Kabupaten','Jawa','Luar Jawa','DKI Jakarta','10 kab teratas'],datasets:[{label:'% penduduk',data:[W.kota_pop,100-W.kota_pop,W.java_pop,100-W.java_pop,W.dki_pop,W.top10_pop_share],backgroundColor:'#c9d4e8'},{label:'% charger',data:[W.kota_ch,100-W.kota_ch,W.java_ch,100-W.java_ch,W.dki_ch,W.top10_share],backgroundColor:NAVY}]},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},scales:{y:{beginAtZero:true,max:100,grid:{color:'#eef1f6'},ticks:{font:{size:10}}},x:xAx('')}}});
 $('tblKdGroups').querySelector('tbody').innerHTML=grp.map(g=>`<tr><td><b>${g.label}</b></td><td class="n">${g.n}</td><td class="n">${fmt(g.pop)}</td><td class="n">${fmt(g.chargers)}</td><td class="n">${f2(g.per100k)}</td><td class="n">${f1(g.within10)}</td><td class="n">${f1(g.beyond25)}</td><td class="n">${f1(g.d_mean)}</td><td class="n">${g.zero}</td><td class="n">${g.dc}</td></tr>`).join('');
 const [ko,ka]=K.kota_kab,[jw,lj]=K.java;
 $('kdWhy2').innerHTML=`<b>Mengapa dua garis ini yang menentukan.</b><ol>
  <li><b>Kota vs kabupaten: ${(ko.per100k/ka.per100k).toFixed(1)}× per kapita.</b> ${ko.n} kota (${W.kota_pop}% penduduk) memegang ${W.kota_ch}% charger; ${ko.within10}% penduduk kota tinggal ≤10 km dari SPKLU, kabupaten hanya ${ka.within10}%, dan ${ka.beyond25}% penduduk kabupaten (≈${jt(ka.pop*ka.beyond25/100)} jiwa) lebih dari 25 km. Semua ${W.kab_zero} kabupaten tanpa charger adalah kabupaten, bukan kota. Jarak rata-rata tertimbang penduduk: kota ${ko.d_mean} km, kabupaten ${ka.d_mean} km.</li>
  <li><b>Jawa vs luar Jawa: ${(jw.per100k/lj.per100k).toFixed(1)}× per kapita, tetapi celah aksesnya lebih besar lagi.</b> Jawa (${W.java_pop}% penduduk, ${W.java_ch}% charger) mencapai ${jw.within10}% penduduk ≤10 km dengan hanya ${jw.beyond25}% &gt;25 km; luar Jawa ${lj.within10}% dan <b>${lj.beyond25}%</b> &gt;25 km — hampir seperempat penduduk luar Jawa (${jt(lj.pop*lj.beyond25/100)} jiwa) berada di gurun pengisian. Kepadatan Jawa membuat tiap situs mencakup lebih banyak orang; di luar Jawa, per-kapita yang sama pun tidak akan menghasilkan cakupan yang sama.</li>
  <li><b>Kesimpulan mekanis:</b> 63,7% nasional adalah rata-rata dari dua dunia — Jawa ${jw.within10}% dan luar Jawa ${lj.within10}% — bukan kondisi yang dialami siapa pun. Angka nasional tunggal menutupi bahwa masalah luar Jawa adalah <i>ketiadaan</i> (gurun 25 km), sedangkan masalah Jawa adalah <i>ketebalan</i> (kota padat dengan sedikit charger per orang).</li></ol>`;

 /* ---- 3 ekuitas vertikal */
 $('kdKv3').innerHTML=kv([[CI.grdp,'CI charger ~ PDRB/kapita provinsi','g'],[CI.hdi,'CI charger ~ IPM'],[CI.poverty,'CI charger ~ kemiskinan (miskin→kaya)'],[CI.access_grdp,'CI akses ≤10 km ~ PDRB'],[CI.density,'CI charger ~ kepadatan kabupaten']]);
 const CC=CI.curves;
 mk('cKdConc',{type:'line',data:{datasets:[
   {label:'~ PDRB/kapita (CI '+CI.grdp+')',data:pts(CC.grdp),borderColor:NAVY,pointRadius:0,borderWidth:2,tension:.1},
   {label:'~ IPM (CI '+CI.hdi+')',data:pts(CC.hdi),borderColor:RED,pointRadius:0,borderWidth:2,tension:.1},
   {label:'~ kemiskinan (CI '+CI.poverty+')',data:pts(CC.poverty),borderColor:ORANGE,pointRadius:0,borderWidth:1.8,tension:.1},
   {label:'akses ≤10 km ~ PDRB (CI '+CI.access_grdp+')',data:pts(CC.access_grdp),borderColor:GREEN,pointRadius:0,borderWidth:1.8,tension:.1},
   {label:'~ kepadatan kabupaten (CI '+CI.density+')',data:pts(CC.density),borderColor:PURPLE,borderDash:[3,3],pointRadius:0,borderWidth:1.6,tension:.1},diag()]},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}},tooltip:{callbacks:{label:x=>`${x.dataset.label}: ${Math.round(x.raw.x*100)}% penduduk termiskin → ${Math.round(x.raw.y*100)}% charger`}}},
   scales:{x:unit01('kumulatif penduduk, termiskin → terkaya'),y:unit01('kumulatif charger')}}});
 const Q=K.quint;
 mk('cKdQuint',{data:{labels:Q.map(q=>'Q'+q.q+' · PDRB '+Math.round(q.grdp)+' jt'),datasets:[{type:'bar',label:'charger /100 rb',data:Q.map(q=>q.per100k),backgroundColor:NAVY,yAxisID:'y',borderRadius:3},{type:'line',label:'≤10 km %',data:Q.map(q=>q.within10),borderColor:GREEN,backgroundColor:GREEN,pointRadius:4,yAxisID:'y2'},{type:'line',label:'>25 km %',data:Q.map(q=>q.beyond25),borderColor:RED,backgroundColor:RED,pointRadius:4,yAxisID:'y2'}]},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},scales:{y:yAx('charger /100 rb'),y2:{position:'right',beginAtZero:true,max:100,grid:{display:false},title:{display:true,text:'% penduduk',font:{size:10}},ticks:{font:{size:10}}},x:xAx('kuintil provinsi termiskin → terkaya')}}});
 $('tblKdQuint').querySelector('tbody').innerHTML=Q.map(q=>`<tr><td><b>Q${q.q}</b></td><td style="font-size:11px">${q.provs.map(esc).join(', ')}</td><td class="n">${fmt(q.pop)}</td><td class="n">${f1(q.grdp)}</td><td class="n">${f1(q.poverty)}</td><td class="n">${f2(q.per100k)}</td><td class="n">${f1(q.within10)}</td><td class="n">${f1(q.beyond25)}</td></tr>`).join('');
 const q1=Q[0],q5=Q[Q.length-1],q2=Q[1];
 $('kdWhy3').innerHTML=`<b>Mengapa CI-nya positif tetapi tidak sebesar Gini.</b><ol>
  <li><b>Charger pro-kaya, tetapi gradiennya bukan uang melainkan pembangunan manusia.</b> CI terhadap PDRB/kapita hanya ${CI.grdp}, terhadap IPM ${CI.hdi}, terhadap kemiskinan ${CI.poverty}. Sebabnya: provinsi ber-PDRB tinggi karena sumber daya alam (Riau, Kalimantan Timur/Utara, Papua Barat) berpenduduk jarang dan minim charger, sehingga "kaya" versi PDRB tidak berarti terlayani. IPM — yang mengikuti urbanisasi dan pendidikan — jauh lebih menjelaskan ke mana charger pergi.</li>
  <li><b>Kuintil termiskin (Q1: ${q1.provs.length} provinsi, ${jt(q1.pop)} jiwa, kemiskinan ${q1.poverty}%)</b> mendapat ${q1.per100k} charger/100 rb dan ${q1.within10}% penduduk ≤10 km, dengan ${q1.beyond25}% &gt;25 km; kuintil terkaya (Q5) ${q5.per100k} charger/100 rb — <b>${(q5.per100k/q1.per100k).toFixed(1)}×</b>. Tetapi Q2 (${q2.provs.join(' & ')}) — miskin menurut PDRB tetapi padat — mencapai ${q2.within10}% ≤10 km: kepadatanlah yang membeli cakupan, bukan pendapatan.</li>
  <li><b>Akses hampir netral terhadap pendapatan</b> (CI akses ~PDRB ${CI.access_grdp}, nyaris nol) sementara kepemilikan charger jelas pro-padat (CI ~kepadatan ${CI.density}). Dibaca bersama: jaringan yang ada sudah "cukup adil" dalam soal <i>ada atau tidak</i> lintas kelas pendapatan provinsi, tetapi <i>berapa banyak</i> ditentukan kepadatan dan IPM. Ketidakadilan vertikal Indonesia hari ini adalah ketidakadilan <b>kedalaman</b>, bukan keberadaan — sampai ke Q1 di mana ia menjadi ketiadaan.</li>
  <li><b>Catatan metodologis yang jujur:</b> indikator pendapatan hanya tingkat provinsi (34 unit), sehingga CI di sini adalah CI antar-provinsi; ketidakadilan dalam-provinsi (kota kaya vs kabupaten miskin di provinsi yang sama) belum terukur — itulah yang ditangkap Spatial Equity Jawa Barat (EPI, CI per kabupaten IPM) dan yang membutuhkan data BPS tingkat kabupaten untuk seluruh Indonesia.</li></ol>`;

 /* ---- 4 defisit */
 $('kdKv4').innerHTML=kv([[fmt(DF.total),'charger yang harus ditambah agar semua kabupaten ≥ rata-rata nasional','g'],[Math.round(100*DF.total/4795)+'%','dari jaringan operasional saat ini'],[fmt(DF.surplus),'charger "surplus" di kabupaten di atas rata-rata'],[W.kab_below_mean+' / '+W.n_kab,'kabupaten di bawah rata-rata'],[f2(DF.mean100k),'rata-rata nasional charger /100 rb']]);
 $('tblKdDef').querySelector('tbody').innerHTML=DF.top.map(r=>`<tr><td><b>${esc(r.name)}</b></td><td>${esc(r.prov)}</td><td class="n">${fmt(r.pop)}</td><td class="n">${r.chargers}</td><td class="n" style="color:${RED};font-weight:700">+${r.deficit}</td></tr>`).join('');
 $('tblKdSur').querySelector('tbody').innerHTML=DF.top_surplus.map(r=>`<tr><td><b>${esc(r.name)}</b></td><td>${esc(r.prov)}</td><td class="n">${fmt(r.pop)}</td><td class="n">${r.chargers}</td><td class="n" style="color:${GREEN};font-weight:700">+${r.surplus}</td></tr>`).join('');
 $('kdWhy4').innerHTML=`<b>Cara membaca defisit.</b><ol>
  <li>Defisit dan surplus <i>sama besar</i> (${fmt(DF.total)}) karena keduanya diukur terhadap rata-rata yang sama; artinya kesetaraan sempurna bisa dicapai dengan <b>memindahkan</b> ${fmt(DF.total)} charger, atau dengan <b>menambah</b> ${fmt(DF.total)} (+${Math.round(100*DF.total/4795)}%) tanpa mengambil dari siapa pun. Yang kedua lebih realistis dan itulah skala kebijakannya: jaringan harus tumbuh hampir separuh lagi <i>hanya</i> di kabupaten yang tertinggal untuk sekadar setara per kapita.</li>
  <li>Defisit terbesar bukan di Papua melainkan di <b>kabupaten padat di Jawa</b> (${DF.top.slice(0,4).map(r=>esc(r.name)).join(', ')}) — kesetaraan per kapita memihak jumlah orang. Ini titik di mana kesetaraan dan ekuitas berbeda: ukuran per kapita menempatkan ${jt(DF.top[0].pop)} jiwa Malang di atas 230 ribu jiwa Deiyai yang jaraknya 90 km ke charger terdekat.</li>
  <li>Surplus terbesar ada di Jakarta dan kota-kota Tangerang — bukan "kelebihan" dalam arti mubazir (utilisasinya tinggi), melainkan tanda bahwa ukuran per kapita <i>tidak</i> menangkap permintaan armada dan komuter. Karena itu defisit adalah ukuran <b>kesetaraan</b>, bukan target pembangunan.</li></ol>`;

 /* ---- 5 kurva cakupan */
 const n=CV.eq.length,last=n-1,i100=Math.min(99,last);
 $('kdKv5').innerHTML=kv([[CV.base+'%','cakupan awal (≤10 km)'],[CV.eq[i100]+'% / '+CV.ek[i100]+'%','+100 situs: aturan kesetaraan / ekuitas','g'],[CV.eq[last]+'% / '+CV.ek[last]+'%','+'+n+' situs: kesetaraan / ekuitas'],[CV.q1_eq[last]+'% → '+CV.q1_ek[last]+'%','cakupan kuintil termiskin setelah +'+n+' (kesetaraan → ekuitas)']]);
 const xs=[...Array(n).keys()].map(i=>i+1);
 mk('cKdCov',{type:'line',data:{labels:xs,datasets:[{label:'aturan kesetaraan (maks. penduduk baru)',data:CV.eq,borderColor:NAVY,pointRadius:0,borderWidth:2},{label:'aturan ekuitas (bobot beban provinsi ≤2×)',data:CV.ek,borderColor:GOLD,pointRadius:0,borderWidth:2,borderDash:[5,3]}]},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},scales:{y:{min:60,max:90,grid:{color:'#eef1f6'},ticks:{font:{size:10}},title:{display:true,text:'% penduduk ≤10 km',font:{size:10}}},x:xAx('situs baru (radius ≈10 km, greedy)')}}});
 mk('cKdCovQ1',{type:'line',data:{labels:xs,datasets:[{label:'kesetaraan',data:CV.q1_eq,borderColor:NAVY,pointRadius:0,borderWidth:2},{label:'ekuitas',data:CV.q1_ek,borderColor:GOLD,pointRadius:0,borderWidth:2,borderDash:[5,3]}]},
  options:{maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},scales:{y:{min:40,max:80,grid:{color:'#eef1f6'},ticks:{font:{size:10}},title:{display:true,text:'% penduduk Q1 ≤10 km',font:{size:10}}},x:xAx('situs baru')}}});
 const pick=(rows,id)=>$(id).querySelector('tbody').innerHTML=rows.slice(0,20).map((p,i)=>`<tr><td class="n">${i+1}</td><td><b>${esc(p.kab)}</b></td><td>${esc(p.prov)}</td><td class="n">${fmt(p.pop)}</td></tr>`).join('');
 pick(CV.picks_eq,'tblKdPickEq');pick(CV.picks_ek,'tblKdPickEk');
 const dNat=(CV.eq[last]-CV.ek[last]).toFixed(2),dQ1=(CV.q1_ek[last]-CV.q1_eq[last]).toFixed(1);
 $('kdWhy5').innerHTML=`<b>Mengapa hasilnya nyaris sama secara nasional tetapi berbeda bagi yang termiskin.</b><ol>
  <li>Seratus situs pertama menaikkan cakupan dari ${CV.base}% ke ≈${CV.eq[i100]}% pada kedua aturan — <b>situs marjinal terbaik adalah kabupaten padat di Jawa yang belum tercakup</b> (${CV.picks_eq.slice(0,4).map(p=>esc(p.kab)).join(', ')}), dan kedua aturan setuju karena penduduk yang tercakup di sana sangat besar. Kurva melandai setelah ±150 situs: sisa penduduk tak tercakup tersebar tipis (kepulauan, pegunungan), tiap situs tambahan hanya menambah puluhan ribu jiwa.</li>
  <li>Bobot ekuitas (≤2× untuk provinsi termiskin) menggeser urutan sejak situs ke-4 (Paniai, Lombok Timur) tetapi <b>hanya mengorbankan ${dNat} poin cakupan nasional</b> setelah ${n} situs, sementara cakupan kuintil termiskin naik <b>${dQ1} poin</b> (${CV.q1_eq[last]}% → ${CV.q1_ek[last]}%). Harga ekuitas di sini nyaris nol — karena provinsi miskin yang padat (NTB, NTT, Aceh) adalah target yang baik menurut kedua ukuran.</li>
  <li>Kesimpulan uji: dalam rezim "cakupan 10 km", <b>kesetaraan dan ekuitas tidak bertentangan sampai ±300 situs</b>; konflik keduanya baru muncul di ukuran <i>per kapita</i> (defisit §4) dan pada situs-situs ekor (Papua pegunungan) yang mahal secara jaringan — persis wilayah "prioritas tinggi, jaringan lemah" di Peta Ekuitas.</li></ol>`;

 /* ---- 6 kesimpulan */
 $('kdConcl').innerHTML=`<ol style="margin-left:18px">
  <li><b>Jaringan SPKLU Indonesia tidak setara (Gini ${G.chargers}, 20:20 = ${K.ratio2020}×) dan ketidaksetaraannya terstruktur:</b> ${T.prov.between_pct}% antar-provinsi, lalu kota vs kabupaten (${(ko.per100k/ka.per100k).toFixed(1)}× per kapita), lalu pusat vs pinggiran di dalam kabupaten (Gini heksagon ${G.hex}). Ukuran yang benar untuk RQ4 karena itu harus bertingkat, bukan satu Gini nasional.</li>
  <li><b>Akses dan kepemilikan adalah dua hal berbeda dan keduanya harus dilaporkan.</b> 63,7% penduduk tercakup 10 km (Gini akses ${G.access}) hidup berdampingan dengan Gini charger ${G.chargers}; kebijakan yang mengejar cakupan akan "selesai" jauh sebelum kesetaraan tercapai.</li>
  <li><b>Ketidakadilan vertikal Indonesia adalah ketidakadilan kedalaman yang berubah menjadi ketiadaan di kuintil termiskin.</b> CI terhadap IPM ${CI.hdi} (pro-kaya), Q1 mendapat ${q1.per100k} charger/100 rb dan ${q1.beyond25}% penduduknya &gt;25 km dari charger; gradiennya IPM dan kepadatan, bukan PDRB.</li>
  <li><b>Kesetaraan per kapita menuntut +${fmt(DF.total)} charger (+${Math.round(100*DF.total/4795)}%) di ${W.kab_below_mean} kabupaten</b> — dan menaruh kabupaten padat Jawa di depan Papua; ini ukuran keadilan horizontal, bukan rencana pembangunan.</li>
  <li><b>Ekuitas nyaris gratis di rezim cakupan:</b> memberi bobot 2× pada provinsi termiskin mengorbankan ${dNat} poin cakupan nasional dan menambah ${dQ1} poin bagi 25 juta penduduk termiskin. Rekomendasi kebijakan yang bisa dipertahankan: <i>gunakan aturan ekuitas untuk 300 situs berikutnya, ukur keberhasilan dengan cakupan kuintil termiskin, bukan cakupan nasional</i>.</li>
  <li><b>Yang belum bisa dijawab data ini:</b> ketidakadilan dalam-provinsi menurut pendapatan (perlu BPS tingkat kabupaten), akses menurut waktu tempuh jalan, dan siapa yang benar-benar bisa mengisi di rumah (garasi). Ketiganya adalah agenda RQ4 berikutnya, dan Spatial Equity Jawa Barat menunjukkan bentuk jawabannya.</li></ol>`;
 $('kdLimit').innerHTML=`<b>Batas & cara menghitung ulang.</b> Semua angka dihitung <code>equitymap/keadilan.py</code> dari payload Peta Ekuitas (<code>equity.js</code>): 508 kabupaten/kota berpenduduk, 31.405 heksagon res 6 ≥100 jiwa, charger = unit pada situs operasional (PLN <i>available/inuse</i> + mitra non-PLN). Gini memakai integral trapesium kurva Lorenz; Theil T dengan dekomposisi antar/dalam; CI = 1 − 2×luas kurva konsentrasi dengan unit provinsi (PDRB, IPM, kemiskinan BPS ~2023 indikatif) atau kabupaten (kepadatan); kuintil dipotong pada kumulatif penduduk provinsi terurut PDRB; kurva cakupan = greedy maximum coverage dengan radius dua cincin heksagon res 6 (≈10–13 km), kandidat = pusat heksagon berpenduduk, aturan ekuitas memakai bobot 1 + beban provinsi ternormalisasi (1–2×). Jarak garis lurus; master PLN tanpa wilayah PLN Batam; populasi Kontur 2023 (estimasi model).`;
 document.querySelectorAll('#p-keadilan [data-kdtab]').forEach(a=>a.onclick=e=>{e.preventDefault();if(window.gotoTab)gotoTab(a.dataset.kdtab);});
 built=true;
}
window.initKeadilan=function(){if(!built)build();};
if(document.querySelector('#p-keadilan.active'))setTimeout(window.initKeadilan,60);
})();
