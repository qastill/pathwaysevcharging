/* ============ PAPER: CHARGING WITHOUT SELLING ELECTRICITY (P2P, Jawa Barat) ============ */
(function(){
 const P=(typeof D!=='undefined'&&D.p2p)||null; if(!P) return;
 const $=id=>document.getElementById(id);
 const nf=(v,d=0)=>Number(v).toLocaleString('id-ID',{minimumFractionDigits:d,maximumFractionDigits:d});
 const rp=(v,d=0)=>'Rp '+nf(v,d);
 const NAVY='#1c2b4a',GOLD='#d4af37',BLUE='#3a6ea5',GREEN='#2e9e5b',RED='#d6443c',MUT='#8a94a6';
 const tbl=(id,head,rows,numFrom)=>{const el=$(id); if(!el)return;
  const nfm=i=>(numFrom!==undefined&&i>=numFrom)?' class="num"':'';
  el.innerHTML='<table><thead><tr>'+head.map((h,i)=>`<th${nfm(i)}>${h}</th>`).join('')+
   '</tr></thead><tbody>'+rows.map(r=>'<tr>'+r.map((c,i)=>`<td${nfm(i)}>${c}</td>`).join('')+'</tr>').join('')+
   '</tbody></table>';};
 const charts=[];
 const mk=(id,cfg)=>{const el=$(id); if(!el)return; charts.push(new Chart(el,cfg));};

 /* ------------------------------------------------------------------ abstrak */
 $('p2pAbs').innerHTML=`<b>Pertanyaan.</b> Dapatkah pasar pengisian peer-to-peer dibangun tanpa
  jual-beli energi — dan apa akibatnya bagi harga, pendapatan host, ekonomi platform, pendapatan
  PLN, beban puncak jaringan, dan keadilan spasial? <b>Data.</b> ${nf(P.A.sessions)} sesi bermeter
  (${nf(P.A.kwh/1e6,2)} GWh, ${rp(P.A.rev/1e9,2)} miliar, Maret 2026) di ${P.A.sites} SPKLU Jawa
  Barat, plus register ${nf(P.meta.hosts)} permohonan home charging (${nf(P.meta.hosts_done)}
  selesai) sampai Juni 2026, tergeokode ke ${nf(P.meta.kel)} kelurahan. <b>Temuan.</b> Seluruh
  bisnisnya hidup di dalam pita <b>${rp(P.band.malam.lo)}–${nf(P.band.malam.hi)} per jam</b> pada
  7 kW, yang kedua tepinya ditetapkan tarif di luar kendali pasar; harga berbasis waktu punya
  <i>lantai</i>, sehingga baru mengalahkan SPKLU di atas dwell impas
  <b>${nf(P.des.tstar,2)} jam (${nf(P.des.kwh_tstar,1)} kWh)</b>; karena pendapatan host mengalir
  per jam alih-alih per kWh, insentifnya adalah <b>keterisian, bukan perputaran</b> — kendala
  hukumnya justru menyelaraskan kepentingan pribadi dengan kepentingan sistem;
  ${nf(P.meta.hosts_done)} charger rumah terpasang menyimpan <b>${nf(P.idle.terpasang.kwh/1e6,2)}
  GWh/bulan kapasitas malam menganggur, ${nf(P.idle.terpasang.rasio,2)}× keluaran seluruh jaringan
  publik</b>; ${nf(P.base.share_n,1)} % sesi (${nf(P.base.share_kwh,1)} % energi) secara teknis
  tersubstitusi. <b>Tetapi</b> host <b>lebih terkonsentrasi</b> daripada jaringan publik yang
  hendak dilengkapinya (Gini ${nf(P.eq.gini_host,3)} vs ${nf(P.eq.gini_situs,3)}; ρ =
  ${nf(P.eq.rho_host_kwh,2)} terhadap permintaan yang sudah ada). P2P adalah instrumen efisiensi,
  bukan instrumen keadilan.`;

 /* -------------------------------------------------------------- angka kunci */
 $('p2pFacts').innerHTML=[
  [rp(P.price.allin)+'/kWh','harga SPKLU all-in Maret 2026 — energi '+rp(P.price.energi)+' + PPJ '+rp(P.price.ppj)],
  [rp(P.price.surplus_malam)+'/kWh','surplus yang tersedia dibagi empat pihak (tarif rumah malam)'],
  [rp(P.band.malam.lebar)+'/jam','lebar pita komersial di jendela malam pada 7 kW'],
  [nf(P.idle.idle_pct,0)+' %','malam charger rumah yang menganggur — pemakaian sendiri hanya '+nf(P.idle.malam_sendiri,1)+' malam dari '+P.idle.malam],
  [nf(P.idle.terpasang.rasio,2)+'×','kapasitas malam menganggur '+nf(P.meta.hosts_done)+' host vs seluruh keluaran SPKLU'],
  [nf(P.base.share_kwh,1)+' %','energi SPKLU yang tersubstitusi charger rumah (radius '+P.meta.r_base+' km)'],
  [nf(P.des.tstar,2)+' jam','dwell impas — di bawah ini P2P lebih mahal daripada SPKLU'],
  [nf(P.eq.gini_host,3)+' / '+nf(P.eq.gini_situs,3),'Gini host vs Gini situs SPKLU terhadap populasi'],
 ].map(f=>`<div class="f"><div class="n">${f[0]}</div><div class="l">${f[1]}</div></div>`).join('');

 /* --------------------------------------------------------- Tabel 1: hukum */
 tbl('p2pLegal',['Fakta','Instrumen','Akibat bagi P2P'],[
  ['Penyediaan tenaga listrik untuk umum adalah kegiatan berizin; menjual kelebihan tenaga listrik tanpa persetujuan pemerintah dilarang dan dipidana',
   'UU 30/2009 Pasal 49(3), diubah UU 6/2023','Rumah tangga tidak boleh memasang harga Rp/kWh'],
  ['SPKLU adalah KBLI 35114 <i>penjualan tenaga listrik</i> — risiko tinggi, wajib NIB + izin usaha penyediaan tenaga listrik',
   'Permen ESDM 1/2023 Pasal 10 &amp; 15; PP 5/2021 Pasal 15(1)','Menjadi badan usaha berizin tidak proporsional untuk satu stopkontak 7 kW'],
  ['Harga SPKLU kepada pemilik KBLBB diturunkan dari tarif layanan khusus dengan faktor pengali N ≤ 1,5',
   'Ketentuan tarif Permen ESDM 1/2023','Harga publik ditetapkan administratif — jadi ia plafon yang stabil untuk diacu'],
 ]);

 /* ------------------------------------------------- Gambar 1: pita sewa */
 const W=P.win;
 mk('p2pBand',{type:'bar',data:{labels:W.map(w=>w.win.replace(/\s*\(.*\)/,'')),
   datasets:[
    {label:'batas bawah — biaya energi host',data:W.map(w=>[0,w.lo]),backgroundColor:'rgba(214,68,60,.22)',
     borderColor:RED,borderWidth:1,borderSkipped:false},
    {label:'pita layak',data:W.map(w=>[w.lo,w.hi]),backgroundColor:'rgba(46,158,91,.45)',
     borderColor:GREEN,borderWidth:1,borderSkipped:false}]},
  options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
   plugins:{legend:{labels:{boxWidth:9,font:{size:9.5}}},
    tooltip:{callbacks:{label:i=>i.datasetIndex===1
      ?`layak ${rp(W[i.dataIndex].lo)} – ${nf(W[i.dataIndex].hi)}/jam · lebar ${rp(W[i.dataIndex].lebar)}`
      :`host menombok di bawah ${rp(W[i.dataIndex].lo)}/jam`}}},
   scales:{x:{stacked:false,title:{display:true,text:'sewa parkir (Rp/jam, 7 kW)',font:{size:10}},
     ticks:{font:{size:9},callback:v=>nf(v)}},y:{ticks:{font:{size:9.5}}}}},
  plugins:[{id:'ceil',afterDraw(ch){const{ctx,chartArea:a,scales:s}=ch;ctx.save();
    const x=s.x.getPixelForValue(P.band.malam.hi);ctx.setLineDash([5,4]);ctx.strokeStyle=NAVY;ctx.lineWidth=1.2;
    ctx.beginPath();ctx.moveTo(x,a.top);ctx.lineTo(x,a.bottom);ctx.stroke();
    ctx.setLineDash([]);ctx.fillStyle=NAVY;ctx.font='9px sans-serif';ctx.textAlign='right';
    ctx.fillText('plafon = harga SPKLU',x-4,a.top+11);ctx.restore();}}]});

 /* ------------------------------------- Gambar 2: harga efektif vs dwell */
 const CV=P.curve.filter(c=>[11000,P.par.r,15000,17000].includes(c.r));
 mk('p2pCurve',{type:'line',data:{labels:CV[0].t.map(x=>x[0]),
   datasets:CV.map((c,i)=>({label:'r = '+nf(c.r)+'/jam',data:c.t.map(x=>x[1]),
     borderColor:[GREEN,BLUE,GOLD,RED][i],backgroundColor:'transparent',borderWidth:2,
     pointRadius:0,tension:.25}))
    .concat([{label:'harga SPKLU',data:CV[0].t.map(()=>P.price.allin),borderColor:NAVY,
      borderDash:[6,4],borderWidth:1.5,pointRadius:0,backgroundColor:'transparent'}])},
  options:{responsive:true,maintainAspectRatio:false,
   plugins:{legend:{labels:{boxWidth:9,font:{size:9}}},
    tooltip:{callbacks:{label:i=>i.dataset.label+': '+rp(i.parsed.y)+'/kWh'}}},
   scales:{x:{title:{display:true,text:'lama dwell (jam)',font:{size:10}},ticks:{font:{size:9}}},
    y:{min:1500,max:5000,title:{display:true,text:'harga efektif (Rp/kWh baterai)',font:{size:10}},
     ticks:{font:{size:9},callback:v=>nf(v)}}}}});

 /* ------------------------------------------------ Tabel 2 + narasi idle */
 $('p2pIdleP').innerHTML=`Satu rumah tangga yang menempuh ${nf(P.idle.km)} km/bulan pada
  ${nf(P.par.kw,0)} kW hanya memakai chargernya <b>${nf(P.idle.jam_sendiri,1)} jam per bulan</b> —
  setara ${nf(P.idle.malam_sendiri,1)} malam penuh dari ${P.idle.malam}. Terhadap jendela berbagi
  ${nf(P.idle.jendela,0)} jam per malam, <b>${nf(P.idle.idle_pct,1)} % kapasitas malamnya tidak
  terpakai</b>, atau ${nf(P.idle.kwh_host)} kWh per host per bulan. Perbandingannya sengaja dibuat
  telanjang: kapasitas malam yang menganggur pada charger rumah yang <i>sudah</i> terpasang di Jawa
  Barat melampaui keluaran bulanan seluruh SPKLU provinsi sebesar
  <b>${nf(100*(P.idle.terpasang.rasio-1),0)} %</b> — tanpa modal baru sepeser pun, hanya butuh
  transaksi yang sah.`;
 tbl('p2pIdle',['Armada','Kapasitas menganggur','Rasio ke jaringan publik','Setara situs SPKLU','Setara modal'],
  [['%s permohonan selesai'.replace('%s',nf(P.meta.hosts_done)),
    nf(P.idle.terpasang.kwh/1e6,2)+' GWh/bulan',nf(P.idle.terpasang.rasio,2)+'×',
    nf(P.idle.terpasang.situs,0)+' situs','≈ '+rp(P.idle.terpasang.capex/1e9,0)+' miliar'],
   ['%s seluruh permohonan'.replace('%s',nf(P.meta.hosts)),
    nf(P.idle['seluruh permohonan'].kwh/1e6,2)+' GWh/bulan',nf(P.idle['seluruh permohonan'].rasio,2)+'×',
    nf(P.idle['seluruh permohonan'].situs,0)+' situs','≈ '+rp(P.idle['seluruh permohonan'].capex/1e9,0)+' miliar'],
   ['Jaringan publik (pembanding)',nf(P.A.kwh/1e6,2)+' GWh/bulan','1,00×',P.A.sites+' situs','—']],1);

 /* ------------------------------------------------- Gambar 3-4: corong */
 mk('p2pFunnel',{type:'bar',data:{labels:P.funnel.map(f=>f.k),
   datasets:[{data:P.funnel.map(f=>f.n),backgroundColor:[NAVY,BLUE,'#6a9bc9',GREEN]}]},
  options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
   plugins:{legend:{display:false},tooltip:{callbacks:{label:i=>
     nf(i.parsed.x)+' sesi ('+nf(100*i.parsed.x/P.A.sessions,1)+' %)'}}},
   scales:{x:{ticks:{font:{size:9},callback:v=>nf(v)}},y:{ticks:{font:{size:9},autoSkip:false}}}}});

 mk('p2pRadius',{type:'line',data:{labels:P.addr.map(a=>a.r+' km'),
   datasets:[{label:'% sesi',data:P.addr.map(a=>a.share_n),borderColor:BLUE,backgroundColor:'transparent',
     borderWidth:2,tension:.3,pointRadius:3},
    {label:'% energi',data:P.addr.map(a=>a.share_kwh),borderColor:GOLD,backgroundColor:'transparent',
     borderWidth:2,tension:.3,pointRadius:3}]},
  options:{responsive:true,maintainAspectRatio:false,
   plugins:{legend:{labels:{boxWidth:9,font:{size:9.5}}},
    tooltip:{callbacks:{label:i=>i.dataset.label+': '+nf(i.parsed.y,1)+' %'}}},
   scales:{x:{title:{display:true,text:'ambang jarak situs ke host terdekat',font:{size:10}},ticks:{font:{size:9}}},
    y:{min:40,max:75,ticks:{font:{size:9},callback:v=>v+' %'}}}}});

 /* -------------------------------------------- Tabel 3: ekonomi sesi */
 $('p2pDesP').innerHTML=`Dengan sewa <b>${rp(P.par.r)}/jam</b> (di dalam pita malam, di atas lantai
  siang) dan jasa <b>${rp(P.par.fee)}/sesi</b>: lantai harga <b>${rp(P.des.floor)}/kWh</b>,
  ${nf(100*(P.price.allin-P.des.floor)/P.price.allin,1)} % di bawah jaringan publik; dwell impas
  <b>${nf(P.des.tstar,2)} jam</b> atau ${nf(P.des.kwh_tstar,1)} kWh — di bawah itu pengemudi
  seharusnya memakai SPKLU.`;
 tbl('p2pSes',['Dwell','kWh baterai','kWh termeter','Pengemudi bayar','Rp/kWh efektif','vs SPKLU','Host bersih (malam)','Host bersih (siang)'],
  P.ses.map(s=>[s.t+' jam',nf(s.kwh,1),nf(s.meter,1),rp(s.bayar),nf(s.eff),
   '−'+nf(s.hemat_pct,1)+' %',rp(s.host_malam),rp(s.host_siang)]),1);

 /* --------------------------------------------- Model A vs B, harga sama */
 const AB=P.ab;
 $('p2pAB').innerHTML=`
  <div class="qb good"><b>Model B — sewa ${nf(P.par.r)}/jam + jasa tetap ${nf(P.par.fee)}</b>
   <div class="s">Host menerima <b>${rp(AB.B.host)}</b> · platform <b>${rp(AB.B.plat)}</b></div></div>
  <div class="qb warn"><b>Model A — per kWh, komisi ${nf(100*P.theta,0)} %</b>
   <div class="s">Host menerima <b>${rp(AB.A.host)}</b> · platform <b>${rp(AB.A.plat)}</b></div></div>
  <div class="qb" style="grid-column:1/-1"><b>Sesi ${AB.t} jam · ${nf(AB.kwh,1)} kWh · pengemudi
   membayar ${rp(AB.driver_rp)} (${rp(AB.driver_kwh)}/kWh) dalam kedua model</b>
   <div class="s">Arsitektur yang sah memindahkan <b>${rp(AB.B.host-AB.A.host)} per sesi</b> dari
   platform ke host. Kendalanya bukan sekadar tertanggungkan bagi host — pada dimensi ini justru
   lebih baik bagi mereka. Yang membayar ongkos kendala itu adalah platform.</div></div>`;

 /* ------------------------------------------------------- host & pengemudi */
 tbl('p2pHost',['Pesanan/minggu','Dwell','Bersih/bulan','Imbal hasil aset terpasang','Payback bila dibeli untuk disewakan'],
  P.host.filter(h=>[2,3,5].includes(h.spm)).map(h=>[h.spm+'×',h.t+' jam',rp(h.net),
   nf(h.yld,1)+' %/th',nf(h.payback,0)+' bulan']),2);
 const DR=P.driver;
 tbl('p2pDriver',['Sumber','Biaya/bulan','vs SPKLU'],[
  ['SPKLU '+rp(P.price.allin)+'/kWh',rp(DR.spklu),'—'],
  ['<b>P2P pada desain acuan</b>','<b>'+rp(DR.p2p)+'</b>','<b>−'+nf(DR.hemat_pct,1)+' %</b>'],
  ['Charger rumah sendiri, tarif malam',rp(DR.rumah_malam),'−'+nf(100*(DR.spklu-DR.rumah_malam)/DR.spklu,1)+' %'],
  ['Setara bensin (11 km/l)',rp(DR.bbm),'+'+nf(100*(DR.bbm-DR.spklu)/DR.spklu,0)+' %'],
 ],1);

 /* ------------------------------------------------------ platform & PLN */
 tbl('p2pPlat',['Penetrasi','Sesi/bulan','GMV/bulan','Pendapatan platform','Kolam host','Host aktif'],
  P.plat.map(x=>[nf(x.pen,0)+' %',nf(x.sesi),rp(x.gmv/1e6,0)+' jt',rp(x.fee/1e6,1)+' jt',
   rp(x.host/1e6,1)+' jt','≈ '+nf(x.host_n,0)]),1);
 tbl('p2pPln',['Penetrasi','Energi pindah/bln','Dilusi/tahun','Situs setara','Modal+O&amp;M terhindar/th','Neto/th'],
  P.pln.map(x=>[nf(x.pen,0)+' %',nf(x.kwh)+' kWh',rp(x.dilusi_th/1e9,2)+' M',nf(x.situs,1),
   rp(x.anuitas/1e9,2)+' M','<b style="color:'+GREEN+'">+'+rp(x.net_th/1e9,2)+' M</b>']),1);

 /* --------------------------------------------------- Gambar 5-6: jaringan */
 const HR=P.hours;
 mk('p2pHours',{type:'bar',data:{labels:HR.map(h=>h.h+':00'),
   datasets:[{label:'kWh per jam (Maret 2026)',data:HR.map(h=>h.kwh),
     backgroundColor:HR.map(h=>h.h>=17&&h.h<22?RED:(h.h>=22||h.h<5?GREEN:'#c9d3e2'))}]},
  options:{responsive:true,maintainAspectRatio:false,
   plugins:{legend:{display:false},tooltip:{callbacks:{
     label:i=>nf(i.parsed.y)+' kWh · '+nf(HR[i.dataIndex].share,1)+' % energi bulan',
     title:i=>i[0].label+(HR[i[0].dataIndex].h>=17&&HR[i[0].dataIndex].h<22?' — puncak sistem':
       (HR[i[0].dataIndex].h>=22||HR[i[0].dataIndex].h<5?' — jendela diskon malam':''))}}},
   scales:{x:{ticks:{font:{size:8},maxRotation:0,autoSkip:true,maxTicksLimit:12}},
    y:{ticks:{font:{size:9},callback:v=>nf(v/1000)+'k'}}}}});

 mk('p2pShift',{type:'bar',data:{labels:P.shift.map(s=>nf(s.pen,0)+' %'),
   datasets:[{label:'MW puncak yang lepas',data:P.shift.map(s=>s.mw),backgroundColor:BLUE,yAxisID:'y'},
    {label:'% dari puncak pengisian',data:P.shift.map(s=>s.pct_peak),type:'line',borderColor:GOLD,
     backgroundColor:'transparent',borderWidth:2,pointRadius:3,yAxisID:'y1'}]},
  options:{responsive:true,maintainAspectRatio:false,
   plugins:{legend:{labels:{boxWidth:9,font:{size:9.5}}}},
   scales:{x:{title:{display:true,text:'penetrasi segmen tersubstitusi',font:{size:10}},ticks:{font:{size:9}}},
    y:{position:'left',title:{display:true,text:'MW',font:{size:10}},ticks:{font:{size:9}}},
    y1:{position:'right',grid:{drawOnChartArea:false},ticks:{font:{size:9},callback:v=>v+' %'}}}}});

 $('p2pGridP').innerHTML=`Pengisian publik di Jawa Barat bukan beban luar puncak: jam
  17.00–21.59 memikul <b>${nf(P.grid.peak_share,1)} % energi bulanan</b> dalam 20,8 % waktu,
  rata-rata <b>${nf(P.grid.peak_mw,2)} MW</b> se-provinsi melawan ${nf(P.grid.off_mw,2)} MW pada
  tujuh jam malam. Besaran mutlaknya masih kecil hari ini, dan itu bukan intinya. Yang berbeda
  secara jenis adalah <b>bentuknya</b>: satu situs publik memusatkan ${nf(P.grid.dc_kw_situs)} kW
  pada satu sambungan tegangan rendah, sedangkan energi yang sama lewat host tersebar pada
  <b>${nf(P.grid.host_setara,0)} sambungan ${nf(P.par.kw,0)} kW</b> yang berbeda — dan pada Model B
  host tidak punya alasan pendapatan untuk menaikkan daya itu.`;

 /* --------------------------------------------------- Gambar 7-8: keadilan */
 const dia=[[0,0],[1,1]];
 mk('p2pLorenz',{type:'line',data:{datasets:[
   {label:'situs SPKLU (G='+nf(P.eq.gini_situs,3)+')',data:P.eq.lorenz_situs.map(p=>({x:p[0],y:p[1]})),
    borderColor:BLUE,backgroundColor:'transparent',borderWidth:2,pointRadius:0,tension:.1},
   {label:'energi publik (G='+nf(P.eq.gini_kwh,3)+')',data:P.eq.lorenz_kwh.map(p=>({x:p[0],y:p[1]})),
    borderColor:GOLD,backgroundColor:'transparent',borderWidth:2,pointRadius:0,tension:.1},
   {label:'host P2P (G='+nf(P.eq.gini_host,3)+')',data:P.eq.lorenz_host.map(p=>({x:p[0],y:p[1]})),
    borderColor:RED,backgroundColor:'transparent',borderWidth:2.5,pointRadius:0,tension:.1},
   {label:'pemerataan sempurna',data:dia.map(p=>({x:p[0],y:p[1]})),borderColor:MUT,
    borderDash:[5,4],borderWidth:1,pointRadius:0,backgroundColor:'transparent'}]},
  options:{responsive:true,maintainAspectRatio:false,parsing:false,
   plugins:{legend:{labels:{boxWidth:9,font:{size:9}}}},
   scales:{x:{type:'linear',min:0,max:1,title:{display:true,text:'proporsi kumulatif populasi',font:{size:10}},
     ticks:{font:{size:9}}},
    y:{min:0,max:1,title:{display:true,text:'proporsi kumulatif',font:{size:10}},ticks:{font:{size:9}}}}}});

 const SC=P.kab.filter(k=>k.pop&&k.host>0&&k.kwh>0);
 mk('p2pScatter',{type:'scatter',data:{datasets:[{label:'kota/kabupaten',
   data:SC.map(k=>({x:k.kwh,y:k.host,k:k.kab})),backgroundColor:'rgba(58,110,165,.65)',pointRadius:5}]},
  options:{responsive:true,maintainAspectRatio:false,
   plugins:{legend:{display:false},tooltip:{callbacks:{label:i=>
     `${i.raw.k} — ${nf(i.raw.y)} host · ${nf(i.raw.x)} kWh`}}},
   scales:{x:{type:'logarithmic',title:{display:true,text:'energi SPKLU Maret 2026 (kWh, log)',font:{size:10}},
     ticks:{font:{size:9}}},
    y:{type:'logarithmic',title:{display:true,text:'host home charging (log)',font:{size:10}},
     ticks:{font:{size:9}}}}}});

 $('p2pEqP').innerHTML=`Charger rumah <b>lebih tidak merata</b> daripada jaringan publik yang
  seharusnya dilengkapinya (Gini ${nf(P.eq.gini_host,3)} vs ${nf(P.eq.gini_situs,3)} terhadap
  populasi) dan lebih tidak merata daripada konsumsi publik itu sendiri
  (${nf(P.eq.gini_kwh,3)}). Korelasi peringkat menegaskan mekanismenya: jumlah host berkorelasi
  ρ = ${nf(P.eq.rho_host_kwh,2)} dengan energi publik yang sudah ada dan ρ =
  ${nf(P.eq.rho_host_situs,2)} dengan jumlah situs. Host muncul di tempat permintaan sudah ada.
  Sebabnya struktural, bukan kebetulan: sambungan home charging menuntut kepemilikan rumah atau izin
  pemilik, halaman atau garasi, dan modal sekitar ${rp(P.par.capex_wallbox/1e6,0)} juta — syarat yang
  terdistribusi seperti kekayaan, dan kekayaan terdistribusi seperti jaringan yang sudah ada.
  <b>Kesimpulannya tidak perlu dilunakkan: P2P adalah instrumen efisiensi, bukan instrumen
  keadilan.</b> Ada satu keuntungan distributif yang tersembunyi di dalam agregat — pelanggan P2P
  menurut definisinya adalah pengemudi yang <i>tidak bisa</i> memasang wallbox, dan ia menghemat
  ${rp(DR.hemat_vs_spklu)}/bulan. P2P progresif di dalam wilayah, regresif antarwilayah.`;

 /* ------------------------------------------------------ Tabel 8: daya */
 tbl('p2pPow',['Daya AC diterima mobil','kWh baterai dalam 8 jam','Pengemudi bayar','Rp/kWh efektif','vs SPKLU'],
  P.pow.map(x=>[nf(x.kw,1)+' kW',nf(x.jam8,1),rp(x.bayar8),
   '<b>'+nf(x.eff8)+'</b>',(x.eff8>P.price.allin?'<span style="color:'+RED+'">+':'<span style="color:'+GREEN+'">')+
    nf(100*(x.eff8-P.price.allin)/P.price.allin,0)+' %</span>']),1);

 /* ------------------------------------------------ Tabel 9: skema Airbnb */
 tbl('p2pAirbnb',['Primitif Airbnb','Padanan pengisian P2P','Catatan'],[
  ['Listing','Petak: koordinat, daya, konektor, foto, petunjuk akses','Daya harus <i>diverifikasi</i> — ia yang menentukan harga riil pengemudi'],
  ['Kalender','Jendela malam, bawaan 21.00–05.00','Jendela malam adalah inventarisnya'],
  ['Harga','<b>Sewa parkir Rp/jam</b> di dalam pita layak','Tidak pernah Rp/kWh — lihat bagian 2'],
  ['Biaya layanan','Rp/sesi tetap kepada platform','Alternatif: persentase dari <i>sewa parkir</i>, bukan dari energi'],
  ['Ulasan','Dua arah: akses, keandalan, keselamatan, ketepatan daya','Keandalan mendominasi persepsi di pasar ini (Naskah 1)'],
  ['Kepercayaan &amp; keselamatan','Verifikasi identitas, sertifikat laik operasi, uji ELCB','Tidak opsional: tamu mencolok ke instalasi tetap milik host'],
  ['Asuransi','Tanggung jawab host atas instalasi dan kendaraan','Celah paling jelas di pasar Indonesia'],
  ['Pembatalan','Bebas sampai T−2 jam; penalti host tidak hadir','Petak yang terkunci adalah perjalanan yang batal, bukan sekadar kamar kosong'],
  ['Pencairan','Transfer mingguan ke host, ditagih platform','Agregasi pembayaran adalah kegiatan berizin'],
 ]);

 /* -------------------------------------------------------- 10. kebijakan */
 const F16=P.front.find(f=>f.p===1600)||P.front[2];
 const F16r=F16.r.find(x=>x.r===15000);
 const FN=P.front[0];
 $('p2pPolicy').innerHTML=[
  ['Langkah 1 — Tegaskan tertulis bahwa sewa petak berbasis waktu bukan jual-beli tenaga listrik',
   `Intervensi termurah yang tersedia. Satu surat edaran direktorat jenderal yang menyatakan bahwa
    imbalan atas pemakaian petak parkir dan perlengkapan pengisian terpasang, yang dihargai per
    satuan waktu dan bukan per kWh, tidak merupakan penjualan tenaga listrik menurut UU 30/2009 dan
    tidak memerlukan izin SPKLU, membuka seluruh arsitektur ini dengan biaya fiskal nol. Beri
    batasnya: pagu daya (≤ 7.700 VA), pagu sesi, kewajiban registrasi, dan larangan penyaluran
    lanjutan.`],
  ['Langkah 2 — Buat golongan tarif meter host, dan jadikan diskon malam struktural',
   `Dua cacat melekat pada tarif sekarang. Diskon malam adalah <b>promosi bertanggal kedaluwarsa</b>,
    dan pada ${rp(P.price.rumah_malam)}/kWh ia hanya melampaui biaya pokok penyediaan sekitar
    <b>${rp(FN.atas_bpp)}/kWh</b> — tidak ada margin di sana untuk membiayai sebuah pasar. Keduanya
    diperbaiki instrumen yang sama: golongan tarif <i>host P2P</i> terdaftar pada meter home
    charging, dihargai di antara tarif rumah dan tarif SPKLU, permanen alih-alih promosional. Pada
    ${rp(F16.p)}/kWh pitanya masih selebar ${rp(F16.lebar)}/jam — cukup untuk harga pengemudi
    ${rp(F16r.eff)}/kWh dan margin host ${rp(F16r.margin)}/jam — sekaligus memangkas dilusi
    pendapatan PLN dari ${rp(FN.dilusi)} menjadi ${rp(F16.dilusi)} per kWh
    (<b>−${nf(100*(FN.dilusi-F16.dilusi)/FN.dilusi,0)} %</b>) dan melampaui biaya pokok
    ${rp(F16.atas_bpp)}/kWh. Itulah harga saat PLN bisa menjadi penaja, bukan lawan transaksi yang
    terpaksa.`],
  ['Langkah 3 — Jadikan modal yang terhindar itu nyata',
   `Manfaat pada tabel PLN bergantung pada situs yang <i>tidak jadi</i> dibangun. Kewajiban cakupan
    yang dinyatakan dalam <i>jumlah stasiun per wilayah</i> akan memaksa situs itu tetap dibangun dan
    mengubah seluruh latihan ini menjadi dilusi murni. Tulis ulang kewajibannya sebagai
    <b>permintaan terlayani dalam standar keterjangkauan</b>, dan izinkan petak P2P terdaftar
    dihitung ke dalamnya dengan bobot terdiskon yang mencerminkan daya lebih rendah dan kepemilikan
    privat.`],
  ['Langkah 4 — Wajibkan pengungkapan harga efektif saat pemesanan',
   `Tarif berbasis waktu menyembunyikan biaya per kWh-nya, dan tabel 8 menunjukkan biaya tersembunyi
    itu bisa <b>${nf(P.pow[0].eff8/P.price.allin*100-100,0)} % di atas</b> jaringan publik untuk mobil
    yang mengisi pelan. Wajibkan tiap listing menampilkan, sebelum pembayaran, perkiraan Rp/kWh
    efektif untuk kendaraan yang dipesan — dihitung dari daya petak yang terverifikasi dan batas
    onboard charger kendaraan — berdampingan dengan harga jaringan publik. Wajibkan daya petak
    diverifikasi, bukan dideklarasikan sendiri.`],
  ['Langkah 5 — Arahkan, atau ia akan memusat',
   `Gini host ${nf(P.eq.gini_host,3)} adalah hasil yang seharusnya mengatur ke mana uang publik
    pergi di sini. Subsidi host yang dibagikan menurut permintaan akan diklaim di Bogor, Depok,
    Bandung dan Bekasi, tempat host memang sudah ada. Dukungan publik apa pun — subsidi pemasangan,
    pembebasan biaya penyambungan, jaminan utilisasi minimum — harus <b>disyaratkan menurut
    lokasi</b>, menyasar kabupaten dengan pemilik EV terdaftar tinggi dan kepadatan host rendah, dan
    dievaluasi terhadap Gini host, bukan terhadap jumlah host. Program yang menaikkan jumlah host
    tetapi meninggalkan Gini di ${nf(P.eq.gini_host,3)} telah membeli efisiensi lalu menamainya
    akses.`],
 ].map(x=>`<div class="step"><b>${x[0]}</b><div class="s">${x[1]}</div></div>`).join('')
  +`<p style="margin-top:12px"><b>Urutan.</b> Langkah 1 dan 4 bersifat administratif dan bisa
    dikerjakan tahun ini. Langkah 2 menuntut keputusan tarif. Langkah 3 menuntut penulisan ulang
    kewajiban cakupan. Langkah 5 menuntut satu mata anggaran. Hanya Langkah 1 yang mutlak diperlukan
    agar pasarnya ada; hanya Langkah 5 yang membuatnya adil.</p>`;

 /* ------------------------------------------------------------- batas */
 $('p2pLim').innerHTML=`<ol style="margin-left:18px">
  <li>Satu bulan permintaan (Maret 2026), satu provinsi. Musiman dan puncak koridor Lebaran tidak terwakili.</li>
  <li>Substitusi adalah <b>batas atas</b>: yang diukur adalah kecocokan geografis, bukan kesediaan.
   Tidak ada pengemudi dalam data yang ditanya apakah ia mau menginapkan mobilnya di rumah orang lain.</li>
  <li>Register host ≠ host aktif. ${nf(P.meta.hosts_done)} pemasangan selesai adalah pasokan
   potensial, bukan pasokan yang menyetujui.</li>
  <li>Tolok ukur modal bersifat indikatif (${rp(P.par.capex_spklu/1e9,1)} miliar/situs,
   ${rp(P.par.opex_spklu/1e6,0)} juta/tahun O&amp;M, ${rp(P.par.capex_wallbox/1e6,0)} juta/wallbox)
   dan menggerakkan tabel PLN — bacalah sebagai sensitivitas, bukan sebagai hasil.</li>
  <li>Situs yang terhindar dinilai pada keluaran rata-rata, bukan marginal; arah biasnya dinyatakan,
   tidak dikoreksi.</li>
  <li>Pembacaan hukum bersifat sekunder dan seluruhnya bertanda VERIFY — makalah ini berargumen
   tentang sebuah desain di bawah kendala, bukan memberi nasihat hukum.</li>
  <li>Tidak ada model perilaku penetapan harga, dan tidak ada model antrean: pencocokan diperlakukan
   nirgesekan dalam radius ${P.meta.r_base} km.</li>
 </ol>`;

 /* ------------------------------------------- tautan ke perpustakaan */
 const lnk=$('p2pToLib');
 if(lnk) lnk.onclick=e=>{e.preventDefault();
  const t=document.querySelector('.tab[data-p="library"]'); if(t){t.click();
   setTimeout(()=>{const b=document.querySelector('[data-libopen="p2p"]'); if(b) b.click();},120);}};

 window.initP2p=function(){charts.forEach(c=>{try{c.resize();}catch(_){}})};
})();
