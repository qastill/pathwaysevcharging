
/* ============ PERPUSTAKAAN NASKAH PhD ============ */
(function(){
 const LIB=(typeof D!=='undefined'&&D.lib)||null; if(!LIB) return;
 const $=id=>document.getElementById(id);
 const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 const KEY=p=>'spklu.review.'+p;
 const TAGS={mayor:['Mayor','#d6443c'],minor:['Minor','#e0a52b'],
             tanya:['Pertanyaan','#3a6ea5'],setuju:['Setuju','#2e9e5b']};
 const STL={draft:'Draft',review:'Siap ditinjau',plan:'Rencana',submitted:'Sudah disubmit'};
 const CATS=LIB.categories||{};
 const catLab=k=>(CATS[k]||['Lain-lain','#9aa7bd'])[0], catCol=k=>(CATS[k]||['','#9aa7bd'])[1];
 let filter='all';
 const uid=()=>Math.random().toString(36).slice(2,10)+Date.now().toString(36).slice(-4);

 /* ---------- backend: Supabase lewat /api/papers, atau mode lokal ---------- */
 // SB = {url,key,upload} bila env Vercel sudah diatur; null = semua tersimpan di peramban ini.
 let SB=null, remotePapers=[];
 async function loadConfig(){
  try{ const r=await fetch('/api/papers',{cache:'no-store'}); if(!r.ok) return;
   const c=await r.json(); if(c&&c.configured&&c.url&&c.anonKey) SB={url:c.url,key:c.anonKey,upload:!!c.upload};
  }catch(e){}
 }
 const sbH=()=>({apikey:SB.key,Authorization:'Bearer '+SB.key,'Content-Type':'application/json'});
 async function sb(path,opt){
  const r=await fetch(SB.url+'/rest/v1/'+path,Object.assign({headers:sbH()},opt||{}));
  if(!r.ok) throw new Error('Supabase '+r.status+': '+(await r.text()).slice(0,200));
  return r.status===204?null:r.json();
 }
 async function loadRemotePapers(){
  if(!SB){ remotePapers=localPapers(); return; }
  try{ remotePapers=(await sb('papers?select=id,n,title,short,kind,venue,alt,status,stage,pct,target,lead,data,method,todo,tabs,words,category,abstract,goal,finding,manuscript,file_name,file_path,created_at&order=n.asc.nullslast,created_at.asc'))
        .map(p=>Object.assign(p,{remote:true,files:p.file_path?[[ 'Berkas asli ('+(p.file_name||'').split('.').pop()+')',SB.url+'/storage/v1/object/public/papers/'+p.file_path]]:[]}));
  }catch(e){ console.warn('naskah jarak jauh gagal dimuat:',e.message); remotePapers=[]; }
 }
 // mode lokal: naskah unggahan disimpan di localStorage (indeks + isi terpisah supaya ringan)
 const localPapers=()=>{try{return JSON.parse(localStorage.getItem('spklu.papers')||'[]').map(p=>Object.assign(p,{local:true,files:[]}))}catch(e){return[]}};
 const localHtml=id=>{try{return localStorage.getItem('spklu.paper.'+id)||''}catch(e){return''}};

 // komentar
 const loadLocal=id=>{try{return JSON.parse(localStorage.getItem(KEY(id))||'[]')}catch(e){return[]}};
 const saveLocal=(id,v)=>{try{localStorage.setItem(KEY(id),JSON.stringify(v))}catch(e){
   alert('Komentar tidak bisa disimpan di peramban ini. Unduh berkas komentar agar tidak hilang.');}};
 async function loadNotes(id){
  if(!SB) return loadLocal(id);
  try{ return await sb('paper_comments?paper_id=eq.'+encodeURIComponent(id)+'&order=b.asc,ts.asc'); }
  catch(e){ console.warn(e.message); return loadLocal(id); }
 }
 async function persist(op,n){
  if(!SB){ saveLocal(cur.id,notes); return; }
  try{
   if(op==='delete') await sb('paper_comments?id=eq.'+encodeURIComponent(n.id),{method:'DELETE'});
   else await sb('paper_comments?on_conflict=id',{method:'POST',
     headers:Object.assign(sbH(),{Prefer:'resolution=merge-duplicates'}),
     body:JSON.stringify({id:n.id,paper_id:cur.id,b:n.b,quote:n.quote,text:n.text,tag:n.tag,who:n.who,resolved:!!n.resolved,ts:n.ts})});
  }catch(e){ alert('Gagal menyimpan ke server: '+e.message+'\nKomentar disalin ke penyimpanan lokal.'); saveLocal(cur.id,notes); }
 }
 const who=()=>localStorage.getItem('spklu.review.who')||'';
 const allPapers=()=>LIB.papers.concat(remotePapers);


 /* ---------- panel progres PhD ---------- */
 const KIND={Predictive:'#3a6ea5',Evaluative:'#2e9e5b',Causal:'#e0a52b',Synthesis:'#8b5cf6'};
 function ring(pct){
  const r=40,c=2*Math.PI*r,off=c*(1-pct/100);
  return `<svg width="100" height="100" viewBox="0 0 100 100">
   <circle cx="50" cy="50" r="${r}" fill="none" stroke="#eef1f6" stroke-width="9"/>
   <circle cx="50" cy="50" r="${r}" fill="none" stroke="var(--gold)" stroke-width="9" stroke-linecap="round"
     stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}" transform="rotate(-90 50 50)"/>
   <text class="rv" x="50" y="57" text-anchor="middle">${pct}%</text></svg>`;
 }
 function phdPanel(P){
  const H=LIB.phd, PT=LIB.parts||[], SD=LIB.side;
  if(!H||!PT.length){ $('libPhdCard').hidden=true; return; }
  // Progres keseluruhan = rata-rata kesiapan seluruh naskah dalam pipeline (termasuk yang masih rencana).
  const all=P.filter(p=>typeof p.pct==='number');
  const overall=all.length?Math.round(all.reduce((a,p)=>a+p.pct,0)/all.length):0;
  $('libPhdTitle').textContent=H.title;
  $('libPhdMeta').innerHTML=`${esc(H.program)}<br>${esc(H.lead)} · pembimbing ${H.supervisors.map(esc).join(' · ')}
   <br>${esc(H.shape)} · ${esc(H.year1)}`;
  $('libRing').innerHTML=ring(overall)+`<div class="rl">rata-rata kesiapan<br>${all.length} naskah</div>`;
  $('libPhdArg').textContent='“'+H.argument+'”';

  const plist=t=>t.map(x=>`<a data-libopen="${x[0]}"><i>${x[2]}%</i>${esc(x[1])}</a>`).join('');
  $('libParts').innerHTML=PT.map(pt=>`<div class="pt">
   <div class="n"><b>PART ${pt.no}</b>
    <span class="kind" style="background:${KIND[pt.kind]||'#9aa7bd'}">${esc(pt.kind)}</span></div>
   <h4>${esc(pt.name)}</h4>
   <div class="sx">${esc(pt.subtitle)}</div>
   <div class="bar"><i style="width:${pt.pct}%"></i></div>
   <div class="sx" style="margin:4px 0 8px"><b>${pt.pct}%</b> · ${esc(pt.stage)}</div>
   <div class="rq">${esc(pt.rq)}</div>
   <div class="pl">${plist(pt.titles)}</div></div>`).join('');

  $('libSide').innerHTML=SD?`<h4>${esc(SD.name)} — ${SD.pct}%</h4>
   <div class="sx" style="font-size:10.5px;color:var(--mut);line-height:1.55">${esc(SD.subtitle)}</div>
   <div class="pl">${SD.titles.map(x=>`<a data-libopen="${x[0]}">${esc(x[1])} · ${x[2]}%</a>`).join('')}</div>`:'';

  $('libMiles').innerHTML=(LIB.milestones||[]).map(m=>`<div class="m">
   <div class="dot${m[3]==='upcoming'?' up':''}"></div>
   <div class="w">${esc(m[0])}</div>
   <div class="b">${m[4]?`<a href="${m[4]}" target="_blank" rel="noopener" style="color:var(--blue);text-decoration:none">${esc(m[1])} ↗</a>`:esc(m[1])}
    <s>${esc(m[2])}</s></div></div>`).join('');

  $('libOuts').innerHTML=(LIB.outputs||[]).map(o=>`<div class="o">
   <div class="t">${esc(o[0])}</div>
   <div class="b">${o[3]?`<a href="${o[3]}" target="_blank" rel="noopener" style="color:var(--blue);text-decoration:none">${esc(o[1])} ↗</a>`:`<b>${esc(o[1])}</b>`}
    <s>${esc(o[2])}</s></div></div>`).join('');
 }

 /* ---------- beranda ---------- */
 function home(){
  const P=allPapers();
  const tot=P.length, rev=P.filter(p=>p.status==='review').length;
  const words=P.reduce((a,p)=>a+(p.words||0),0);
  $('libKpi').innerHTML=[['Naskah dalam proyek',tot,'draft, working paper, dan conference paper'],
   ['Siap ditinjau pembimbing',rev,'status "review"'],
   ['Total panjang naskah',words.toLocaleString('id-ID')+' kata','gabungan seluruh naskah'],
   ['Naskah unggahan',remotePapers.length,SB?'tersimpan di Supabase':'tersimpan di peramban ini']]
   .map(k=>`<div class="kpi"><div class="l">${k[0]}</div><div class="v">${k[1]}</div><div class="s">${k[2]}</div></div>`).join('');
  $('libMode').innerHTML=SB
   ?`<b>Mode bersama.</b> Naskah unggahan dan komentar tersimpan di Supabase — terlihat oleh semua pembimbing.${SB.upload?'':' <i>(kunci unggah belum diatur di Vercel; unggah belum aktif)</i>'}`
   :`<b>Mode lokal.</b> Backend belum disetel, jadi naskah unggahan dan komentar tersimpan di peramban ini saja. Lihat <code>papers/README.md</code> untuk mengaktifkan penyimpanan bersama.`;
  $('libStoreNote').innerHTML=SB
   ?`<b>Penyimpanan bersama aktif.</b> Komentar langsung tersimpan di server dan terlihat oleh semua peninjau; tombol unduh/muat tetap tersedia sebagai cadangan.`
   :`<b>Catatan penyimpanan.</b> Backend belum disetel, jadi komentar disimpan di <i>localStorage</i> peramban masing-masing peninjau — tidak terkirim ke server dan tidak terlihat oleh peninjau lain sampai berkas komentarnya dipertukarkan lewat tombol unduh/muat.`;

  // ---- baris filter kategori
  const counts={}; P.forEach(p=>{const k=p.category||'lain';counts[k]=(counts[k]||0)+1;});
  $('libCats').innerHTML=`<button class="cb${filter==='all'?' on':''}" data-libcat="all"
     style="${filter==='all'?'background:var(--navy)':''}">Semua <b>${P.length}</b></button>`+
   Object.keys(CATS).filter(k=>counts[k]).map(k=>`<button class="cb${filter===k?' on':''}" data-libcat="${k}"
     style="${filter===k?'background:'+catCol(k):''}">${esc(catLab(k))} <b>${counts[k]}</b></button>`).join('');

  const shown=P.filter(p=>filter==='all'||p.category===filter);
  $('libCards').innerHTML=shown.map(p=>`<div class="pc" style="border-top-color:${catCol(p.category)}">
    <div class="no">Naskah ${p.n||'–'} · ${esc(p.kind)}${p.manuscript===false?'<span class="nom">brief · belum ada naskah</span>':''}${p.remote?'<span class="src">● unggahan</span>':p.local?'<span class="src" style="color:#e0a52b">● lokal</span>':''}</div>
    <div class="cat" style="background:${catCol(p.category)}">${esc(catLab(p.category))}</div>
    <h3>${esc(p.title)}</h3>
    <div class="ven">🎯 ${esc(p.venue||'—')}${p.venue_src&&/usulan/.test(p.venue_src)?' <span class="usul">usulan</span>':''}</div>
    <div class="alt">Alternatif: ${esc(p.alt||'—')}</div>
    <div><span class="st ${p.status}">${STL[p.status]||p.status}</span>
     <span class="cbadge" style="margin-left:6px" data-libcnt="${p.id}" hidden></span></div>
    <div class="bar"><i style="width:${p.pct||0}%"></i></div>
    <div class="meta"><b>${p.pct||0}%</b> · ${esc(p.stage||'')}<br>Target: <b>${esc(p.target||'—')}</b> ·
     ${(p.words||0).toLocaleString('id-ID')} kata</div>
    ${p.goal||p.finding?`<div class="brief">
      ${p.goal?`<b>Tujuan</b><span>${esc(p.goal)}</span>`:''}
      ${p.finding?`<b>Temuan</b><span>${esc(p.finding)}</span>`:''}</div>`:''}
    ${p.abstract?`<details><summary>Abstrak</summary><p>${esc(p.abstract)}</p></details>`:''}
    <div class="chips">${(p.method||[]).slice(0,3).map(d=>`<span class="chip">⚙ ${esc(d)}</span>`).join('')}
     ${(p.data||[]).slice(0,2).map(d=>`<span class="chip">${esc(d)}</span>`).join('')}</div>
    <div class="btns">
     <button class="btn pri" data-libopen="${p.id}">Baca &amp; komentari</button>
     ${(p.files||[]).map(f=>`<a class="btn" href="${f[1]}" download>⬇ ${esc(f[0])}</a>`).join('')}
     ${p.tabs&&p.tabs.length?`<button class="btn" data-libtab="${p.tabs[0]}">📊 Data di dashboard</button>`:''}
    </div></div>`).join('');

  // ---- tabel rencana publikasi
  $('libPub').innerHTML='<thead><tr>'+['Naskah','Kategori','Jenis','Rencana publikasi','Alternatif','Status','Siap','Target']
   .map(h=>`<th>${h}</th>`).join('')+'</tr></thead><tbody>'+
   P.map(p=>`<tr><td><b>${esc(p.short||p.title)}</b></td>
    <td><span class="cat" style="background:${catCol(p.category)};margin:0">${esc(catLab(p.category))}</span></td>
    <td>${esc(p.kind)}</td>
    <td><b>${esc(p.venue||'—')}</b>${p.venue_src&&/usulan/.test(p.venue_src)?'<span class="usul">usulan</span>':''}</td>
    <td style="color:var(--mut)">${esc(p.alt||'—')}</td>
    <td><span class="st ${p.status}">${STL[p.status]||p.status}</span></td>
    <td><b>${p.pct||0}%</b></td><td>${esc(p.target||'—')}</td></tr>`).join('')+'</tbody>';

  $('libPlan').innerHTML=LIB.plan.map(r=>`<tr><td class="q">${esc(r[0])}</td>
   <td><b>${esc(r[1])}</b><div style="font-size:11px;color:var(--mut);margin-top:2px">${esc(r[2])}</div></td>
   <td style="text-align:right"><button class="btn" data-libopen="${r[3]}">buka</button></td></tr>`).join('');

  document.querySelectorAll('#libCats [data-libcat]').forEach(b=>b.onclick=()=>{filter=b.dataset.libcat;home();});
  phdPanel(P);
  document.querySelectorAll('#p-library [data-libopen]').forEach(b=>b.onclick=()=>open_(b.dataset.libopen));
  document.querySelectorAll('#p-library [data-libtab]').forEach(b=>b.onclick=()=>{
   const t=document.querySelector('.tab[data-p="'+b.dataset.libtab+'"]'); if(t)t.click();});
  // lencana komentar terbuka per naskah (lokal langsung; jarak jauh diambil ringkas)
  P.forEach(async p=>{const el=document.querySelector('[data-libcnt="'+p.id+'"]'); if(!el) return;
   let open=0;
   if(SB){try{open=(await sb('paper_comments?select=id&paper_id=eq.'+encodeURIComponent(p.id)+'&resolved=eq.false')).length}catch(e){}}
   else open=loadLocal(p.id).filter(c=>!c.resolved).length;
   if(open){el.textContent=open+' komentar terbuka';el.hidden=false;}});
 }

 /* ---------- pembaca ---------- */
 let cur=null, notes=[], showDone=false;

 async function open_(id){
  cur=allPapers().find(p=>p.id===id); if(!cur) return;
  showDone=false; $('libShowDone').checked=false;
  $('libHome').style.display='none'; $('libReader').classList.add('on');
  $('libDoc').innerHTML='<p class="empty">Memuat naskah…</p>'; $('libRail').innerHTML='';
  let html=cur.html;
  if(cur.remote&&!html){ try{ html=(await sb('papers?select=html&id=eq.'+encodeURIComponent(id)))[0].html; }catch(e){ html='<p>Gagal memuat isi: '+esc(e.message)+'</p>'; } cur.html=html; }
  if(cur.local&&!html){ html=localHtml(id); cur.html=html; }
  if(!cur.toc) cur.toc=tocOf(html);
  $('libToc').innerHTML=cur.toc.map(t=>`<a href="#" class="l${t.lv}" data-libgo="${t.b}">${esc(t.t)}</a>`).join('');
  $('libBar').innerHTML=`<b style="font-size:13px;color:var(--navy)">Naskah ${cur.n||'–'}</b>
   <span class="st ${cur.status}">${STL[cur.status]||cur.status}</span>
   <span style="font-size:11.5px;color:var(--mut)">🎯 ${esc(cur.venue||'—')} · target ${esc(cur.target||'—')} ·
   ${(cur.words||0).toLocaleString('id-ID')} kata</span>
   ${(cur.files||[]).map(f=>`<a class="btn" href="${f[1]}" download>⬇ ${esc(f[0])}</a>`).join('')}`;
  $('libDoc').innerHTML=briefBlock(cur)+html+todoBlock(cur);
  $('libWho').value=who();
  document.querySelectorAll('#libToc [data-libgo]').forEach(a=>a.onclick=e=>{e.preventDefault();
   const el=$('libDoc').querySelector('[data-b="'+a.dataset.libgo+'"]');
   if(el) el.scrollIntoView({behavior:'smooth',block:'start'});});
  notes=await loadNotes(id);
  paint();
  window.scrollTo({top:0,behavior:'smooth'});
 }

 function briefBlock(p){
  if(!p.goal&&!p.finding) return '';
  return `<div class="insight" style="margin-bottom:18px">
   <div style="font-size:9.5px;letter-spacing:1px;text-transform:uppercase;color:${catCol(p.category)};font-weight:700;margin-bottom:7px">
    ${esc(catLab(p.category))} · brief riset</div>
   ${p.goal?`<div style="margin-bottom:6px"><b>Tujuan.</b> ${esc(p.goal)}</div>`:''}
   ${p.finding?`<div><b>Temuan kunci.</b> ${esc(p.finding)}</div>`:''}
   <div style="margin-top:7px;font-size:11.5px">🎯 Rencana publikasi: <b>${esc(p.venue||'—')}</b>${
     p.venue_src?` <span style="color:var(--mut)">(${esc(p.venue_src)})</span>`:''}</div></div>`;
 }
 function todoBlock(p){
  const li=a=>(a||[]).map(t=>`<li>${esc(t)}</li>`).join('');
  return `<hr><h3>Daftar kerja sebelum submit</h3><ul>${li(p.todo)||'<li><i>belum diisi</i></li>'}</ul>
   <h4>Data yang dipakai</h4><ul>${li(p.data)||'<li><i>belum diisi</i></li>'}</ul>
   <h4>Metode</h4><ul>${li(p.method)||'<li><i>belum diisi</i></li>'}</ul>`;
 }

 $('libBack').onclick=()=>{$('libReader').classList.remove('on');$('libHome').style.display='';home();};
 $('libShowDone').onchange=e=>{showDone=e.target.checked;paint();};
 $('libWho').oninput=e=>localStorage.setItem('spklu.review.who',e.target.value.trim());

 /* ---------- gambar komentar + sorotan ---------- */
 function paint(){
  const doc=$('libDoc');
  doc.querySelectorAll('[data-b]').forEach(el=>el.classList.remove('hasc'));
  doc.querySelectorAll('mark.hl').forEach(m=>m.replaceWith(...m.childNodes));
  const vis=notes.filter(n=>showDone||!n.resolved);
  vis.forEach(n=>{
   const el=doc.querySelector('[data-b="'+n.b+'"]'); if(!el) return;
   el.classList.add('hasc');
   if(n.quote) hilite(el,n.quote);
  });
  $('libCount').textContent=notes.filter(n=>!n.resolved).length;
  $('libRail').innerHTML=vis.length?vis.map(n=>{
   const t=TAGS[n.tag]||TAGS.tanya;
   return `<div class="cm${n.resolved?' done':''}" data-libjump="${n.b}">
    <span class="who">${esc(n.who||'Peninjau')}</span>
    <span class="tg" style="background:${t[1]}">${t[0]}</span>
    ${n.quote?`<div class="q">“${esc(n.quote.slice(0,150))}${n.quote.length>150?'…':''}”</div>`:''}
    <div class="tx">${esc(n.text)}</div>
    <div class="ft"><span>${new Date(Number(n.ts)||Date.now()).toLocaleString('id-ID',{dateStyle:'short',timeStyle:'short'})}</span>
     <button data-libdone="${n.id}">${n.resolved?'buka lagi':'tandai selesai'}</button>
     <button data-libdel="${n.id}" style="color:#d6443c">hapus</button></div></div>`;}).join('')
   : `<div class="empty">Belum ada komentar. Sorot kalimat pada naskah lalu pilih <b>Komentari</b>.</div>`;

  $('libRail').querySelectorAll('[data-libjump]').forEach(c=>c.onclick=e=>{
   if(e.target.tagName==='BUTTON') return;
   const el=doc.querySelector('[data-b="'+c.dataset.libjump+'"]');
   if(el){el.scrollIntoView({behavior:'smooth',block:'center'});
    el.classList.add('sel');setTimeout(()=>el.classList.remove('sel'),1200);}});
  $('libRail').querySelectorAll('[data-libdone]').forEach(b=>b.onclick=async()=>{
   const n=notes.find(x=>x.id===b.dataset.libdone); if(n){n.resolved=!n.resolved;await persist('upsert',n);paint();}});
  $('libRail').querySelectorAll('[data-libdel]').forEach(b=>b.onclick=async()=>{
   if(!confirm('Hapus komentar ini?'))return;
   const n=notes.find(x=>x.id===b.dataset.libdel);
   notes=notes.filter(x=>x.id!==b.dataset.libdel); await persist('delete',n); paint();});
 }

 function hilite(el,q){
  const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
  const nodes=[];let n;while((n=w.nextNode()))nodes.push(n);
  const full=nodes.map(x=>x.nodeValue).join('');
  const at=full.indexOf(q); if(at<0) return;
  let pos=0;
  for(const t of nodes){
   const a=pos,b=pos+t.nodeValue.length;pos=b;
   const s=Math.max(at,a),e=Math.min(at+q.length,b);
   if(s>=e) continue;
   const r=document.createRange();r.setStart(t,s-a);r.setEnd(t,e-a);
   const m=document.createElement('mark');m.className='hl';
   try{r.surroundContents(m)}catch(err){}
   break;  // satu potongan cukup sebagai penanda visual
  }
 }

 /* ---------- seleksi teks -> popup ---------- */
 const pop=$('libPop');
 document.addEventListener('mouseup',e=>{
  if(!$('libReader').classList.contains('on')) return;
  if(pop.contains(e.target)) return;
  const s=window.getSelection();
  const q=s&&String(s).trim();
  if(!q||q.length<3){pop.classList.remove('on');return;}
  let node=s.anchorNode; while(node&&node!==document.body&&!(node.dataset&&node.dataset.b))node=node.parentNode;
  if(!node||!node.dataset||!node.dataset.b||!$('libDoc').contains(node)){pop.classList.remove('on');return;}
  const r=s.getRangeAt(0).getBoundingClientRect();
  pop.style.left=(r.left+window.scrollX)+'px';
  pop.style.top=(r.top+window.scrollY-42)+'px';
  pop.classList.add('on');
  pop.dataset.b=node.dataset.b; pop.dataset.q=q;
 });
 pop.querySelectorAll('button').forEach(b=>b.onclick=()=>{
  const b_=pop.dataset.b,q=pop.dataset.q; pop.classList.remove('on');
  if(b.dataset.act==='mark'){ add(b_,q,'(ditandai)','minor'); return; }
  const nm=$('libWho').value.trim();
  if(!nm){ $('libWho').focus(); alert('Isi nama peninjau lebih dulu di kolom kanan.'); return; }
  const t=prompt('Komentar untuk kalimat:\n\n“'+q.slice(0,180)+(q.length>180?'…':'')+'”\n\n'+
   'Awali dengan "mayor:", "minor:", "tanya:" atau "setuju:" bila ingin memberi label.');
  if(t===null||!t.trim()) return;
  let tag='tanya',tx=t.trim();
  const m=tx.match(/^(mayor|minor|tanya|setuju)\s*:\s*/i);
  if(m){tag=m[1].toLowerCase();tx=tx.slice(m[0].length);}
  add(b_,q,tx,tag);
 });
 async function add(b,quote,text,tag){
  const nm=$('libWho').value.trim()||who()||'Peninjau';
  localStorage.setItem('spklu.review.who',nm);
  const n={id:uid(),b:+b,quote,text,tag,who:nm,ts:Date.now(),resolved:false};
  notes.push(n); notes.sort((a,b2)=>a.b-b2.b);
  await persist('upsert',n); paint();
  window.getSelection().removeAllRanges();
 }

 /* ---------- ekspor / impor ---------- */
 function dl(name,txt,mime){
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([txt],{type:mime||'application/json'}));
  a.download=name; document.body.appendChild(a); a.click();
  setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},400);
 }
 $('libExp').onclick=()=>{
  if(!notes.length){alert('Belum ada komentar untuk diunduh.');return;}
  const stamp=new Date().toISOString().slice(0,10);
  dl(`komentar_${cur.id}_${stamp}.json`,
     JSON.stringify({paper:cur.id,title:cur.title,exported:new Date().toISOString(),notes},null,1));
  const md=[`# Komentar — ${cur.title}`,``,`Naskah: **${cur.id}** · diekspor ${stamp} · ${notes.length} catatan`,``]
   .concat(notes.map((n,i)=>[`## ${i+1}. ${(TAGS[n.tag]||TAGS.tanya)[0]} — ${n.who||'Peninjau'}`,
     n.quote?`> ${n.quote}`:'',``,n.text,``,`*(blok ${n.b}${n.resolved?', selesai':''})*`,``].join('\n')));
  setTimeout(()=>dl(`komentar_${cur.id}_${stamp}.md`,md.join('\n'),'text/markdown'),500);
 };
 $('libImp').onclick=()=>$('libFile').click();
 $('libFile').onchange=e=>{
  const f=e.target.files[0]; if(!f) return;
  const r=new FileReader();
  r.onload=async()=>{try{
    const d=JSON.parse(r.result); const inc=Array.isArray(d)?d:d.notes;
    if(!Array.isArray(inc)) throw 0;
    if(d.paper&&d.paper!==cur.id&&!confirm(`Berkas ini untuk naskah "${d.paper}", bukan "${cur.id}". Tetap muat?`)) return;
    const have=new Set(notes.map(n=>n.id));
    let n0=0; for(const n of inc){ if(n&&n.text&&!have.has(n.id)){ notes.push(n); n0++; await persist('upsert',n);} }
    notes.sort((a,b)=>a.b-b.b); if(!SB) saveLocal(cur.id,notes); paint();
    alert(n0+' komentar dimuat ('+(inc.length-n0)+' sudah ada).');
  }catch(err){alert('Berkas tidak terbaca sebagai komentar.');}};
  r.readAsText(f); e.target.value='';
 };

 /* ---------- unggah naskah: parse di peramban ---------- */
 // Padanan JS dari papers/library/build.py (md_to_html + number_blocks + toc_of), supaya
 // naskah unggahan mendapat struktur dan indeks blok yang sama dengan naskah bawaan.
 const inline=s=>esc(s).replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>')
   .replace(/(^|[^*\w])\*([^*]+)\*(?!\*)/g,'$1<i>$2</i>')
   .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>')
   .replace(/\[VERIFY([^\]]*)\]/g,'<span class="verify">[VERIFY$1]</span>');
 function mdToHtml(text){
  const L=text.replace(/\r/g,'').split('\n'), out=[]; let i=0;
  const isList=l=>/^\s*([-*+]|\d+\.)\s+/.test(l||'');
  while(i<L.length){
   const ln=L[i].replace(/\s+$/,'');
   if(!ln.trim()){i++;continue;}
   if(ln.startsWith('|')&&i+1<L.length&&/^[\s|:-]+$/.test(L[i+1])){
    const head=ln.replace(/^\||\|$/g,'').split('|').map(c=>c.trim()); i+=2; const body=[];
    while(i<L.length&&L[i].trim().startsWith('|')){body.push(L[i].trim().replace(/^\||\|$/g,'').split('|').map(c=>c.trim()));i++;}
    out.push('<div class="tw"><table><thead><tr>'+head.map(h=>`<th>${inline(h)}</th>`).join('')+'</tr></thead><tbody>'+
     body.map(r=>'<tr>'+r.map(c=>`<td>${inline(c)}</td>`).join('')+'</tr>').join('')+'</tbody></table></div>'); continue;}
   let m=ln.match(/^(#{1,6})\s+(.*)$/);
   if(m){const lv=Math.min(m[1].length+1,6);out.push(`<h${lv}>${inline(m[2])}</h${lv}>`);i++;continue;}
   if(/^(---|\*\*\*|___)$/.test(ln.trim())){out.push('<hr>');i++;continue;}
   if(ln.startsWith('>')){const buf=[];while(i<L.length&&L[i].startsWith('>')){buf.push(L[i].replace(/^>\s?/,''));i++;}
    out.push('<blockquote>'+inline(buf.join(' '))+'</blockquote>');continue;}
   if(isList(ln)){const ord=/^\s*\d+\./.test(ln);const items=[];
    while(i<L.length&&isList(L[i])){let c=L[i].replace(/^\s*([-*+]|\d+\.)\s+/,'');i++;
     while(i<L.length&&/^ {4}/.test(L[i])&&!isList(L[i])){c+=' '+L[i].trim();i++;} items.push(c);}
    out.push(`<${ord?'ol':'ul'}>`+items.map(x=>`<li>${inline(x)}</li>`).join('')+`</${ord?'ol':'ul'}>`);continue;}
   const buf=[];
   while(i<L.length&&L[i].trim()&&!/^(#{1,6}\s|\||>)/.test(L[i])&&!isList(L[i])&&!/^(---|\*\*\*|___)$/.test(L[i].trim())){buf.push(L[i].trim());i++;}
   if(buf.length) out.push('<p>'+inline(buf.join(' '))+'</p>');
  }
  return out.join('\n');
 }
 function numberBlocks(h){
  let n=0; h=h.replace(/<(h[2-6]|p|ul|ol|blockquote|hr)(?=[ >])/g,(m,t)=>`<${t} data-b="${++n}"`);
  const parts=h.split('<div class="tw">');
  return parts[0]+parts.slice(1).map(q=>`<div class="tw" data-b="${++n}">`+q).join('');
 }
 const tocOf=h=>Array.from(h.matchAll(/<(h[3-4]) data-b="(\d+)">(.*?)<\/h[3-4]>/gs))
   .map(m=>({b:+m[2],lv:+m[1][1],t:m[3].replace(/<[^>]+>/g,'').trim()}));
 const wordsOf=h=>h.replace(/<[^>]+>/g,' ').split(/\s+/).filter(Boolean).length;
 // padanan abstract_of() di build.py: ambil paragraf setelah heading Abstract/Summary
 function abstractOf(h){
  const m=h.match(/<h[2-6][^>]*>\s*(?:Abstract|Structured abstract[^<]*|Summary of Research)\s*<\/h[2-6]>([\s\S]*?)(?=<h[2-6]|$)/i);
  if(!m) return '';
  return Array.from(m[1].matchAll(/<p[^>]*>([\s\S]*?)<\/p>/g))
   .map(x=>x[1].replace(/<[^>]+>/g,'').trim()).filter(Boolean).join(' ').replace(/\s+/g,' ').trim();
 }
 function normaliseDocx(h){
  // mammoth memberi h1..h6/p/ul/ol/table polos; samakan dengan konvensi naskah bawaan
  h=h.replace(/<h1>/g,'<h2>').replace(/<\/h1>/g,'</h2>')
     .replace(/<table>/g,'<div class="tw"><table>').replace(/<\/table>/g,'</table></div>')
     .replace(/<p>\s*<\/p>/g,'').replace(/<p>(Fig\.|Table)\s/g,'<p class="figcap">$1 ')
     .replace(/<p>(\[\d+\])/g,'<p class="ref">$1');
  return h;
 }
 let mammothP=null;
 const loadMammoth=()=>mammothP||(mammothP=new Promise((ok,no)=>{ if(window.mammoth) return ok();
  const s=document.createElement('script');
  s.src='https://cdnjs.cloudflare.com/ajax/libs/mammoth/1.8.0/mammoth.browser.min.js';
  s.onload=()=>ok(); s.onerror=()=>no(new Error('pustaka pembaca .docx gagal dimuat')); document.head.appendChild(s);}));
 async function parseFile(f){
  const name=f.name.toLowerCase();
  if(/\.(md|markdown|txt)$/.test(name)) return mdToHtml(await f.text());
  if(name.endsWith('.docx')){ await loadMammoth();
   const r=await window.mammoth.convertToHtml({arrayBuffer:await f.arrayBuffer()},{styleMap:['p[style-name="Caption"] => p.figcap']});
   return normaliseDocx(r.value); }
  throw new Error('Format belum didukung: unggah .docx, .md, atau .txt');
 }
 const lines=id=>$(id).value.split('\n').map(s=>s.trim()).filter(Boolean);
 const slug=s=>s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,60);
 const b64=f=>new Promise((ok,no)=>{const r=new FileReader();r.onload=()=>ok(String(r.result).split(',')[1]);r.onerror=no;r.readAsDataURL(f);});

 $('upCat').innerHTML=Object.keys(CATS).map(k=>`<option value="${k}">${esc(catLab(k))}</option>`).join('');
 $('libUpBtn').onclick=()=>{$('libUpForm').hidden=!$('libUpForm').hidden; if(!$('libUpForm').hidden) $('libUpForm').scrollIntoView({behavior:'smooth'});};
 $('upCancel').onclick=()=>{$('libUpForm').hidden=true;};
 $('upFile').onchange=()=>{const f=$('upFile').files[0]; if(!f) return;
  if(!$('upTitle').value) $('upTitle').value=f.name.replace(/\.[^.]+$/,'').replace(/[_-]+/g,' ');
  if(!$('upId').value) $('upId').value=slug($('upTitle').value);};
 $('upTitle').oninput=()=>{if(!$('upId').dataset.touched) $('upId').value=slug($('upTitle').value);};
 $('upId').oninput=()=>{$('upId').dataset.touched='1';};

 $('upGo').onclick=async()=>{
  const msg=$('upMsg'); const f=$('upFile').files[0];
  const id=$('upId').value.trim(), title=$('upTitle').value.trim();
  if(!f){msg.textContent='Pilih berkas naskah dulu.';return;}
  if(!/^[a-z0-9][a-z0-9-]{1,60}$/.test(id)){msg.textContent='Slug/id tidak valid.';return;}
  if(!title){msg.textContent='Judul wajib diisi.';return;}
  if(allPapers().some(p=>p.id===id)&&!confirm('Naskah dengan id "'+id+'" sudah ada. Timpa?')) return;
  try{
   msg.textContent='Mem-parse '+f.name+' …';
   const html=numberBlocks(await parseFile(f));
   $('upPreview').innerHTML=html;
   const abs=$('upAbs').value.trim()||abstractOf(html);
   const paper={id,title,short:$('upShort').value.trim(),kind:$('upKind').value,venue:$('upVenue').value.trim(),
    category:$('upCat').value,abstract:abs,goal:$('upGoal').value.trim(),finding:$('upFind').value.trim(),
    alt:$('upAlt').value.trim(),status:$('upStatus').value,stage:$('upStage').value.trim(),pct:+$('upPct').value||0,
    target:$('upTarget').value.trim(),lead:$('upLead').value.trim(),data:lines('upData'),method:lines('upMethod'),
    todo:lines('upTodo'),tabs:[],html,words:wordsOf(html),uploaded_by:$('upBy').value.trim(),
    n:allPapers().length+1};
   if(SB&&SB.upload){
    msg.textContent='Mengunggah ke server …';
    const r=await fetch('/api/papers',{method:'POST',headers:{'Content-Type':'application/json'},
     body:JSON.stringify({key:$('upKey').value,paper,file:{name:f.name,type:f.type,base64:await b64(f)}})});
    const j=await r.json(); if(!r.ok) throw new Error(j.error||('HTTP '+r.status));
    msg.textContent='Tersimpan di server ✔';
   }else{
    // mode lokal: simpan indeks ringan + isi terpisah
    const idx=localPapers().filter(p=>p.id!==id); const {html:_h,...meta}=paper;
    idx.push(meta); localStorage.setItem('spklu.papers',JSON.stringify(idx));
    localStorage.setItem('spklu.paper.'+id,html);
    msg.textContent=SB?'Kunci unggah belum diatur di Vercel — disimpan di peramban ini saja.':'Tersimpan di peramban ini (mode lokal) ✔';
   }
   await loadRemotePapers(); home(); $('libUpForm').hidden=true;
   setTimeout(()=>open_(id),150);
  }catch(e){ msg.textContent='Gagal: '+e.message; }
 };

 /* ---------- gambar naskah: klik untuk memperbesar ---------- */
 $('libDoc').addEventListener('click',e=>{
  const img=e.target.closest('.fig img'); if(!img) return;
  img.classList.toggle('zoom');
 });

 let booted=false;
 window.initLibrary=async function(){
  if($('libReader').classList.contains('on')) return;
  if(!booted){ booted=true; await loadConfig(); await loadRemotePapers();
   if(SB&&!SB.upload){$('upKey').placeholder='kunci unggah belum diatur';} }
  home();
 };
})();
