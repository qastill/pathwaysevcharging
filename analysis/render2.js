
/* ============ EV × JARINGAN — karbon, harga, lapisan jaringan ============ */
(function(){
 const Y=D.grid2; if(!Y) return;
 const CB=Y.carbon, PR=Y.price, MP=Y.map;
 const p1=(a,b)=>b?(100*a/b):0, f1=v=>(Math.round(v*10)/10).toFixed(1).replace('.',','),
       f2=v=>(Math.round(v*100)/100).toFixed(2).replace('.',','),
       fmt=n=>n==null?'–':Math.round(n).toLocaleString('id-ID'),
       rp=n=>'Rp '+fmt(n);

 /* ---------- KPI karbon ---------- */
 const J=CB.jamali, W=CB.west, E=CB.ev, A=PR.assume;
 $('gxCarbKpis').innerHTML=[
  ["Faktor emisi Jamali",f2(J.ef)+" kg/kWh","turunan dari bauran kapasitas"],
  ["Emisi EV",fmt(E.ev_g_km)+" gCO₂/km","pada "+f2(A.kwh_km)+" kWh/km"],
  ["vs mobil bensin","−"+f1(E.reduction)+"%","asumsi "+fmt(A.ice_g)+" gCO₂/km"],
  ["Pangsa EBT",f1(J.renew_gwh)+"%","energi (kapasitas "+f1(J.renew_mw)+"%)"],
  ["Emisi terhindarkan",fmt(E.avoided)+" tCO₂","Maret 2026, dari SPKLU saja"],
  ["Jejak scope-2",fmt(E.tco2)+" tCO₂","listrik SPKLU bulan itu"],
 ].map(x=>`<div class="kpi"><div class="l">${x[0]}</div><div class="v">${x[1]}</div><div class="s">${x[2]}</div></div>`).join('');

 /* ---------- bauran energi ---------- */
 const mix=J.rows.filter(r=>r.gwh>0).slice(0,9);
 const MC={PLTU:'#3d3a37',PLTGU:'#7d6b52',PLTG:'#a8916d',PLTMG:'#c2ad8c',PLTD:'#8a5a3c',
           PLTA:'#3a6ea5',PLTP:'#c1543a',PLTS:'#e0a52b',PLTB:'#5fa8a0',PLTSA:'#8a7fa0',
           PLTM:'#4d86bd',PLTMH:'#6fa0cf',PLTBG:'#6b9e5f','PLT BIOMASS':'#6b9e5f'};
 if(C.cGxMix)C.cGxMix.destroy();
 C.cGxMix=new Chart($('cGxMix'),{type:'doughnut',
  data:{labels:mix.map(r=>r.t+' — '+r.l),datasets:[{data:mix.map(r=>r.gwh),
    backgroundColor:mix.map(r=>MC[r.t]||'#9aa6bd'),borderWidth:1,borderColor:'#fff'}]},
  options:{responsive:true,maintainAspectRatio:false,cutout:'52%',
   plugins:{legend:{position:'right',labels:{font:{size:10},boxWidth:11}},
    tooltip:{callbacks:{label:c=>{const r=mix[c.dataIndex];
      return [r.t+': '+f1(r.sg)+'% energi',fmt(r.gwh)+' GWh/thn · '+fmt(r.mw)+' MW · '+r.u+' unit'];}}}}}});
 $('cGxMix').parentElement.style.height='300px';

 /* ---------- emisi per km ---------- */
 const evJ=E.ev_g_km, evW=W.ef*A.kwh_km*1000;
 if(C.cGxCO2)C.cGxCO2.destroy();
 C.cGxCO2=new Chart($('cGxCO2'),{type:'bar',
  data:{labels:['Mobil bensin','EV — bauran Jamali','EV — bauran Jawa barat','EV — 100% EBT'],
   datasets:[{data:[A.ice_g,evJ,evW,0],backgroundColor:['#8a5a3c','#d6443c','#e0a52b','#2e9e5b'],borderRadius:5}]},
  options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
   plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>fmt(c.raw)+' gCO₂/km'}}},
   scales:{x:{beginAtZero:true,grid:{color:'#eef1f6'},title:{display:true,text:'gCO₂ per km',font:{size:10}}},
           y:{grid:{display:false},ticks:{font:{size:11}}}}}});
 $('cGxCO2').parentElement.style.height='300px';

 const coal=J.rows.find(r=>r.t==='PLTU')||{sg:0}, gas=J.rows.find(r=>r.t==='PLTGU')||{sg:0};
 $('gxCarbNote').innerHTML=`<b>EV di Jawa hari ini memangkas emisi, tapi jauh dari nol.</b> Bauran Jamali masih bertumpu pada <b>PLTU ${f1(coal.sg)}%</b> dan <b>PLTGU ${f1(gas.sg)}%</b> energi, sehingga faktor emisinya <b>${f2(J.ef)} kgCO₂/kWh</b>. Dengan konsumsi ${f2(A.kwh_km)} kWh/km, satu EV mengeluarkan <b>${fmt(evJ)} gCO₂/km</b> — hanya <b>${f1(E.reduction)}% lebih rendah</b> dari mobil bensin, bukan 70–90% seperti yang sering diklaim. Sepanjang Maret 2026, seluruh penjualan SPKLU Jabar (${fmt(PR.kwh)} kWh) membawa jejak <b>${fmt(E.tco2)} tCO₂</b> dan menghindarkan <b>${fmt(E.avoided)} tCO₂</b> dibanding jarak yang sama dengan bensin.<br><br>
 <b>Implikasi kebijakannya tajam:</b> selama PLTU mendominasi, <b>setiap tambahan EV memindahkan emisi dari knalpot ke cerobong</b>, bukan menghapusnya. Manfaat iklim terbesar dari program EV justru datang dari <b>dekarbonisasi pembangkitan</b>, bukan dari percepatan penjualan mobil. Angka pembandingnya ada di grafik: pada bauran yang sama, EV bertenaga listrik 100% EBT akan turun ke nol — selisih <b>${fmt(evJ)} gCO₂/km</b> itulah nilai sesungguhnya dari transisi pembangkit.`;

 /* ---------- KPI harga ---------- */
 const CO=PR.cost;
 $('gxPriceKpis').innerHTML=[
  ["Tarif all-in SPKLU",rp(PR.allin)+"/kWh","dari "+fmt(PR.n)+" transaksi"],
  ["Komponen energi",rp(PR.energi)+"/kWh",f1(PR.share_energi)+"% tagihan · seragam se-Jabar"],
  ["Komponen PPJ",rp(PR.ppj)+"/kWh",f1(PR.share_ppj)+"% · 0–10% tergantung pemda"],
  ["100 km via SPKLU",rp(CO.spklu100),"pada "+f2(A.kwh_km)+" kWh/km"],
  ["100 km isi rumah",rp(CO.home100),"hemat "+f1(100*(1-CO.home100/CO.spklu100))+"% vs SPKLU"],
  ["Bensin impas",rp(CO.be_spklu)+"/L","di bawah ini bensin lebih murah"],
 ].map(x=>`<div class="kpi"><div class="l">${x[0]}</div><div class="v">${x[1]}</div><div class="s">${x[2]}</div></div>`).join('');

 /* ---------- biaya 100 km ---------- */
 if(C.cGxCost)C.cGxCost.destroy();
 C.cGxCost=new Chart($('cGxCost'),{type:'bar',
  data:{labels:['Bensin (asumsi '+rp(A.bbm)+'/L)','SPKLU publik','Isi di rumah'],
   datasets:[{data:[CO.ice100,CO.spklu100,CO.home100],
    backgroundColor:['#8a5a3c','#e8742c','#2e9e5b'],borderRadius:5}]},
  options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
   plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>rp(c.raw)+' per 100 km'}}},
   scales:{x:{beginAtZero:true,grid:{color:'#eef1f6'},ticks:{callback:v=>fmt(v/1000)+'rb'},
     title:{display:true,text:'rupiah per 100 km',font:{size:10}}},y:{grid:{display:false},ticks:{font:{size:11}}}}}});
 $('cGxCost').parentElement.style.height='300px';

 /* ---------- PPJ per pemda ---------- */
 const tc=s=>s.replace(/[A-ZÀ-Ý]{2,}/g,w=>w[0]+w.slice(1).toLowerCase());
 const PD=[...PR.pemda].sort((a,b)=>b.allin-a.allin);
 if(C.cGxPPJ)C.cGxPPJ.destroy();
 C.cGxPPJ=new Chart($('cGxPPJ'),{type:'bar',
  data:{labels:PD.map(p=>tc(p.pemda)),
   datasets:[{data:PD.map(p=>p.allin),
    backgroundColor:PD.map(p=>p.rate>=8?'#d6443c':p.rate>=5?'#e8742c':p.rate>0?'#e0a52b':'#2e9e5b'),borderRadius:3}]},
  options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
   plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>{const p=PD[c.dataIndex];
     return [rp(p.allin)+'/kWh all-in','PPJ '+f1(p.rate)+'% · '+fmt(p.n)+' transaksi'];}}}},
   scales:{x:{beginAtZero:false,min:2400,grid:{color:'#eef1f6'},title:{display:true,text:'Rp per kWh (all-in) — sumbu dimulai dari 2.400 agar selisih terlihat',font:{size:9.5}}},
           y:{grid:{display:false},ticks:{font:{size:9.5}}}}}});
 $('cGxPPJ').parentElement.style.height=Math.max(300,PD.length*17)+'px';

 const hi=PD[0], lo=PD[PD.length-1];
 $('gxPriceNote').innerHTML=`<b>Harga energinya seragam; yang membuat tidak adil adalah pajak daerah.</b> Komponen energi <b>${rp(PR.energi)}/kWh</b> sama persis di seluruh Jawa Barat — seluruh variasi harga berasal dari <b>Pajak Penerangan Jalan (PPJ)</b> yang ditetapkan tiap pemda, mulai <b>0%</b> (${PD.filter(p=>p.rate===0).map(p=>tc(p.pemda)).join(', ')}) sampai <b>10%</b>. Akibatnya mengisi di <b>${tc(hi.pemda)}</b> menelan <b>${rp(hi.allin)}/kWh</b> sementara di <b>${tc(lo.pemda)}</b> hanya <b>${rp(lo.allin)}/kWh</b> — selisih <b>${rp(hi.allin-lo.allin)} (${f1(100*(hi.allin-lo.allin)/lo.allin)}%)</b> untuk listrik yang identik.<br><br>
 <b>Yang perlu diperhatikan:</b> tarif tertinggi justru jatuh pada daerah dengan adopsi EV terendah dan SPKLU paling jarang — Pangandaran, Tasikmalaya, Subang. Pajak daerah karena itu bekerja <b>berlawanan arah</b> dengan tujuan pemerataan: wilayah yang paling perlu didorong justru dikenai harga tertinggi. Ini kebijakan yang berada di tangan pemda, bukan PLN, sehingga tidak bisa diselesaikan lewat penetapan tarif nasional.<br><br>
 Terhadap bensin, EV tetap unggul telak: <b>${rp(CO.spklu100)}</b> per 100 km lewat SPKLU dan <b>${rp(CO.home100)}</b> bila mengisi di rumah. Bensin baru menyamai SPKLU bila harganya turun ke <b>${rp(CO.be_spklu)}/liter</b>, dan menyamai pengisian rumah pada <b>${rp(CO.be_home)}/liter</b> — keduanya jauh di bawah harga pasar. Selisih rumah vs SPKLU (<b>${f1(100*(1-CO.home100/CO.spklu100))}%</b>) juga menjelaskan mengapa pemilik EV memilih mengisi di rumah, dan mengapa tekanan jatuh ke jaringan tegangan rendah.`;

 /* ---------- pola jam ---------- */
 const H=PR.hours, hk=H.map(h=>h.kwh/1000);
 if(C.cGxHour)C.cGxHour.destroy();
 C.cGxHour=new Chart($('cGxHour'),{type:'bar',
  data:{labels:H.map(h=>String(h.h).padStart(2,'0')),
   datasets:[{label:'kWh SPKLU publik',data:hk,
    backgroundColor:H.map(h=>(h.h>=22||h.h<5)?'#16305f':(h.h>=11&&h.h<=16)?'#e0a52b':'#9fb2cd'),borderRadius:3}]},
  options:{responsive:true,maintainAspectRatio:false,
   plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>{const h=H[c.dataIndex];
     return [fmt(h.kwh)+' kWh · '+fmt(h.n)+' sesi'];}}}},
   scales:{y:{beginAtZero:true,grid:{color:'#eef1f6'},title:{display:true,text:'MWh',font:{size:10}}},
           x:{grid:{display:false},ticks:{font:{size:9}},title:{display:true,text:'jam',font:{size:10}}}}}});
 $('cGxHour').parentElement.style.height='300px';

 const top=[...H].sort((a,b)=>b.kwh-a.kwh)[0];
 const dNote=(D.grid&&D.grid.diurnal)?D.grid.diurnal:null;
 $('gxHourNote').innerHTML=`<b>Dua jenis pengisian membebani jam yang berlawanan.</b> SPKLU publik memuncak <b>siang hari</b> — tertinggi pukul <b>${String(top.h).padStart(2,'0')}:00</b> — dan hanya <b>${f1(PR.night)}%</b> energinya terjual pada jendela 22:00–05:00. Pengisian rumah kebalikannya${dNote?`: gardu penyuplai pelanggan EV naik dari <b>${f1(dNote.evSiang)}%</b> siang ke <b>${f1(dNote.evMalam)}%</b> malam`:''}.<br><br>
 <b>Ini kabar baik yang belum dimanfaatkan.</b> Beban SPKLU tidak menumpuk di puncak malam, sehingga <b>perluasan pengisian cepat publik justru lebih ramah jaringan daripada mendorong charger rumah</b> — kesimpulan yang berlawanan dengan intuisi umum. Bila sebagian pengisian rumah bisa digeser ke SPKLU siang, atau ke jendela malam-dalam lewat tarif, tekanan pada trafo distribusi berkurang tanpa membangun apa pun.`;

 /* ---------- kelas daya ---------- */
 const T=PR.tiers;
 if(C.cGxTier)C.cGxTier.destroy();
 C.cGxTier=new Chart($('cGxTier'),{
  data:{labels:T.map(t=>t.tier),datasets:[
   {type:'bar',label:'kWh per sesi',data:T.map(t=>t.per),backgroundColor:'#16305f',borderRadius:4,yAxisID:'y'},
   {type:'line',label:'Rp per kWh',data:T.map(t=>t.rp),borderColor:'#d4af37',backgroundColor:'#d4af37',
    tension:.25,pointRadius:4,yAxisID:'y1'}]},
  options:{responsive:true,maintainAspectRatio:false,
   plugins:{legend:{position:'bottom',labels:{font:{size:10.5},boxWidth:12}}},
   scales:{y:{beginAtZero:true,position:'left',grid:{color:'#eef1f6'},title:{display:true,text:'kWh/sesi',font:{size:10}}},
           y1:{position:'right',min:2400,max:2800,grid:{display:false},title:{display:true,text:'Rp/kWh',font:{size:10}}},
           x:{grid:{display:false},ticks:{font:{size:9.5}}}}}});
 $('cGxTier').parentElement.style.height='300px';

 const lowT=T[0], hiT=T[T.length-1];
 const spread=Math.max(...T.map(t=>t.rp))-Math.min(...T.map(t=>t.rp));
 $('gxTierNote').innerHTML=`<b>Kecepatan tidak dihargai berbeda — dan itu janggal secara ekonomi.</b> Rentang harga antarkelas daya hanya <b>${rp(spread)}/kWh</b> (${f1(100*spread/PR.allin)}%), praktis datar, padahal charger <b>${hiT.tier}</b> jauh lebih mahal dibangun daripada <b>${lowT.tier}</b>. Yang berbeda justru perilakunya: sesi di charger cepat menyerap <b>${f1(hiT.per)} kWh</b> dibanding <b>${f1(lowT.per)} kWh</b> di AC lambat — pengguna memakai daya besar untuk mengisi lebih banyak, bukan membayar lebih mahal per satuannya.<br><br>
 <b>Konsekuensinya:</b> tanpa diferensiasi harga, pengisian cepat menanggung biaya modal dan biaya beban puncak yang lebih tinggi dengan pendapatan per kWh yang sama. Harga berbasis daya (atau biaya beban terpisah) akan memperbaiki keekonomian SPKLU cepat sekaligus mengarahkan pengisian yang tidak mendesak ke charger lambat yang lebih murah dan lebih ramah jaringan.`;

 /* ---------- tabel asumsi ---------- */
 const tech=CB.tech;
 $('tGxAssume').innerHTML=`<thead><tr><th style="text-align:left">Parameter</th><th style="text-align:left">Nilai</th><th style="text-align:left">Keterangan</th></tr></thead><tbody>`+
  [["Konsumsi EV",f2(A.kwh_km)+" kWh/km","dipakai untuk emisi per km dan biaya per 100 km"],
   ["Emisi mobil bensin",fmt(A.ice_g)+" gCO₂/km","tank-to-wheel, mobil sekelas"],
   ["Konsumsi mobil bensin",f1(A.ice_kmpl)+" km/liter","untuk biaya per 100 km"],
   ["Harga bensin",rp(A.bbm)+"/liter","<b>ubah sesuai harga saat ini</b> — hanya memengaruhi baris bensin"],
   ["Tarif listrik rumah",rp(A.tarif_rumah)+"/kWh","R-1 nonsubsidi; belum memperhitungkan diskon pengisian malam"],
   ["Jam setahun","8.760 jam","untuk mengubah MW menjadi GWh"]
  ].map(x=>`<tr><td style="text-align:left;font-weight:600">${x[0]}</td><td style="text-align:left">${x[1]}</td><td style="text-align:left;color:var(--mut);font-size:11.5px">${x[2]}</td></tr>`).join('')+
  `<tr><td colspan="3" style="background:#f4f6fa;font-weight:700;font-size:11px;color:var(--navy)">FAKTOR EMISI &amp; CAPACITY FACTOR PER JENIS PEMBANGKIT</td></tr>`+
  Object.entries(tech).map(([k,v])=>`<tr><td style="text-align:left;font-weight:600">${k}</td>
   <td style="text-align:left">${f2(v.ef)} kgCO₂/kWh · CF ${f2(v.cf)}${v.derate!==1?' · derate '+f2(v.derate):''}</td>
   <td style="text-align:left;color:var(--mut);font-size:11.5px">${v.l}${v.re?' · terbarukan':''}</td></tr>`).join('')+
  `</tbody>`;

 $('gxCarbCaveat').innerHTML=`<b>Yang membuat angka karbon di halaman ini perlu dibaca hati-hati.</b>
 <b>(1) Data ini kapasitas, bukan produksi.</b> Bauran energi di atas adalah <i>estimasi</i>: kapasitas terpasang tiap jenis pembangkit dikalikan capacity factor tipikal pada tabel ini. Angka pembangkitan sebenarnya hanya bisa datang dari data produksi PLN. Faktor emisi turunannya (<b>${f2(J.ef)} kgCO₂/kWh</b>) kebetulan jatuh di rentang yang lazim dikutip untuk sistem Jawa-Bali, yang menandakan asumsinya wajar — <b>tetapi untuk pelaporan resmi tetap gunakan faktor emisi jaringan yang diterbitkan pemerintah</b>, bukan angka ini.
 <b>(2) Listrik tidak punya alamat.</b> Pada jaringan sinkron, elektron dari PLTU dan dari PLTP bercampur; tidak ada faktor emisi "khusus" per gardu induk atau per UP3. Karena itu halaman ini sengaja <b>tidak</b> menghitung emisi per wilayah — angka Jawa bagian barat hanya menggambarkan <i>karakter pembangkitan di wilayah itu</i>, bukan listrik yang benar-benar diterima pelanggan di sana.
 <b>(3) Perbandingan bensin bersifat tank-to-wheel.</b> Emisi dari pengilangan dan distribusi bahan bakar tidak dihitung di kedua sisi, begitu pula emisi produksi baterai. Analisis daur hidup penuh akan menggeser angkanya — umumnya menguntungkan EV pada pemakaian jarak jauh, dan kurang menguntungkan pada pemakaian rendah.
 <b>(4) Harga adalah potret Maret 2026.</b> Tarif, PPJ, dan harga bensin berubah; parameter di tabel ini yang harus diperbarui, bukan kesimpulannya ditulis ulang.`;
})();
