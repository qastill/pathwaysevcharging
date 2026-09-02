
/* ============ PERPUSTAKAAN NASKAH PhD ============ */
(function(){
 const LIB=(typeof D!=='undefined'&&D.lib)||null; if(!LIB) return;
 const $=id=>document.getElementById(id);
 const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 const KEY=p=>'spklu.review.'+p;
 const TAGS={mayor:['Mayor','#d6443c'],minor:['Minor','#e0a52b'],
             tanya:['Pertanyaan','#3a6ea5'],setuju:['Setuju','#2e9e5b']};
 const STL={draft:'Draft',review:'Siap ditinjau',plan:'Rencana',submitted:'Sudah disubmit'};

 /* ---------- penyimpanan komentar (per peramban peninjau) ---------- */
 const load=id=>{try{return JSON.parse(localStorage.getItem(KEY(id))||'[]')}catch(e){return[]}};
 const save=(id,v)=>{try{localStorage.setItem(KEY(id),JSON.stringify(v))}catch(e){
   alert('Komentar tidak bisa disimpan di peramban ini. Unduh berkas komentar agar tidak hilang.');}};
 const who=()=>localStorage.getItem('spklu.review.who')||'';

 /* ---------- beranda ---------- */
 function home(){
  const tot=LIB.papers.length, rev=LIB.papers.filter(p=>p.status==='review').length;
  const cm=LIB.papers.reduce((a,p)=>a+load(p.id).filter(c=>!c.resolved).length,0);
  const words=LIB.papers.reduce((a,p)=>a+p.words,0);
  $('libKpi').innerHTML=[['Naskah dalam proyek',tot,'draft, working paper, dan conference paper'],
   ['Siap ditinjau pembimbing',rev,'status "review"'],
   ['Total panjang naskah',words.toLocaleString('id-ID')+' kata','gabungan seluruh naskah'],
   ['Komentar terbuka',cm,'tersimpan di peramban ini']]
   .map(k=>`<div class="kpi"><div class="l">${k[0]}</div><div class="v">${k[1]}</div><div class="s">${k[2]}</div></div>`).join('');

  $('libCards').innerHTML=LIB.papers.map(p=>{
   const n=load(p.id), open=n.filter(c=>!c.resolved).length;
   return `<div class="pc">
    <div class="no">Naskah ${p.n} · ${esc(p.kind)}</div>
    <h3>${esc(p.title)}</h3>
    <div class="ven">🎯 ${esc(p.venue)}</div>
    <div class="alt">Alternatif: ${esc(p.alt)}</div>
    <div><span class="st ${p.status}">${STL[p.status]||p.status}</span>
     ${open?`<span class="cbadge" style="margin-left:6px">${open} komentar terbuka</span>`:''}</div>
    <div class="bar"><i style="width:${p.pct}%"></i></div>
    <div class="meta"><b>${p.pct}%</b> · ${esc(p.stage)}<br>Target: <b>${esc(p.target)}</b> ·
     ${p.words.toLocaleString('id-ID')} kata</div>
    <div class="chips">${p.data.slice(0,4).map(d=>`<span class="chip">${esc(d)}</span>`).join('')}</div>
    <div class="btns">
     <button class="btn pri" data-libopen="${p.id}">Baca &amp; komentari</button>
     ${p.files.map(f=>`<a class="btn" href="${f[1]}" download>⬇ ${esc(f[0])}</a>`).join('')}
     ${p.tabs&&p.tabs.length?`<button class="btn" data-libtab="${p.tabs[0]}">📊 Data di dashboard</button>`:''}
    </div></div>`;}).join('');

  $('libPlan').innerHTML=LIB.plan.map(r=>`<tr><td class="q">${esc(r[0])}</td>
   <td><b>${esc(r[1])}</b><div style="font-size:11px;color:var(--mut);margin-top:2px">${esc(r[2])}</div></td>
   <td style="text-align:right"><button class="btn" data-libopen="${r[3]}">buka</button></td></tr>`).join('');

  document.querySelectorAll('#p-library [data-libopen]').forEach(b=>b.onclick=()=>open_(b.dataset.libopen));
  document.querySelectorAll('#p-library [data-libtab]').forEach(b=>b.onclick=()=>{
   const t=document.querySelector('.tab[data-p="'+b.dataset.libtab+'"]'); if(t)t.click();});
 }

 /* ---------- pembaca ---------- */
 let cur=null, notes=[], showDone=false;

 function open_(id){
  cur=LIB.papers.find(p=>p.id===id); if(!cur) return;
  notes=load(id); showDone=false; $('libShowDone').checked=false;
  $('libHome').style.display='none'; $('libReader').classList.add('on');
  $('libToc').innerHTML=cur.toc.map(t=>
   `<a href="#" class="l${t.lv}" data-libgo="${t.b}">${esc(t.t)}</a>`).join('');
  $('libBar').innerHTML=`<b style="font-size:13px;color:var(--navy)">Naskah ${cur.n}</b>
   <span class="st ${cur.status}">${STL[cur.status]||cur.status}</span>
   <span style="font-size:11.5px;color:var(--mut)">🎯 ${esc(cur.venue)} · target ${esc(cur.target)} ·
   ${cur.words.toLocaleString('id-ID')} kata</span>
   ${cur.files.map(f=>`<a class="btn" href="${f[1]}" download>⬇ ${esc(f[0])}</a>`).join('')}`;
  $('libDoc').innerHTML=cur.html+todoBlock(cur);
  $('libWho').value=who();
  document.querySelectorAll('#libToc [data-libgo]').forEach(a=>a.onclick=e=>{e.preventDefault();
   const el=$('libDoc').querySelector('[data-b="'+a.dataset.libgo+'"]');
   if(el) el.scrollIntoView({behavior:'smooth',block:'start'});});
  paint();
  window.scrollTo({top:0,behavior:'smooth'});
 }

 function todoBlock(p){
  return `<hr><h3>Daftar kerja sebelum submit</h3><ul>`+
   p.todo.map(t=>`<li>${esc(t)}</li>`).join('')+`</ul>
   <h4>Data yang dipakai</h4><ul>${p.data.map(d=>`<li>${esc(d)}</li>`).join('')}</ul>
   <h4>Metode</h4><ul>${p.method.map(d=>`<li>${esc(d)}</li>`).join('')}</ul>`;
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
  $('libRail').innerHTML=vis.length?vis.map((n,i)=>{
   const t=TAGS[n.tag]||TAGS.tanya;
   return `<div class="cm${n.resolved?' done':''}" data-libjump="${n.b}">
    <span class="who">${esc(n.who||'Peninjau')}</span>
    <span class="tg" style="background:${t[1]}">${t[0]}</span>
    ${n.quote?`<div class="q">“${esc(n.quote.slice(0,150))}${n.quote.length>150?'…':''}”</div>`:''}
    <div class="tx">${esc(n.text)}</div>
    <div class="ft"><span>${new Date(n.ts).toLocaleString('id-ID',{dateStyle:'short',timeStyle:'short'})}</span>
     <button data-libdone="${n.id}">${n.resolved?'buka lagi':'tandai selesai'}</button>
     <button data-libdel="${n.id}" style="color:#d6443c">hapus</button></div></div>`;}).join('')
   : `<div class="empty">Belum ada komentar. Sorot kalimat pada naskah lalu pilih <b>Komentari</b>.</div>`;

  $('libRail').querySelectorAll('[data-libjump]').forEach(c=>c.onclick=e=>{
   if(e.target.tagName==='BUTTON') return;
   const el=doc.querySelector('[data-b="'+c.dataset.libjump+'"]');
   if(el){el.scrollIntoView({behavior:'smooth',block:'center'});
    el.classList.add('sel');setTimeout(()=>el.classList.remove('sel'),1200);}});
  $('libRail').querySelectorAll('[data-libdone]').forEach(b=>b.onclick=()=>{
   const n=notes.find(x=>x.id===b.dataset.libdone); if(n){n.resolved=!n.resolved;save(cur.id,notes);paint();}});
  $('libRail').querySelectorAll('[data-libdel]').forEach(b=>b.onclick=()=>{
   if(!confirm('Hapus komentar ini?'))return;
   notes=notes.filter(x=>x.id!==b.dataset.libdel);save(cur.id,notes);paint();});
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
 function add(b,quote,text,tag){
  const nm=$('libWho').value.trim()||who()||'Peninjau';
  localStorage.setItem('spklu.review.who',nm);
  notes.push({id:Math.random().toString(36).slice(2,10),b:+b,quote,text,tag,who:nm,
              ts:Date.now(),resolved:false});
  notes.sort((a,b2)=>a.b-b2.b);
  save(cur.id,notes); paint();
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
  r.onload=()=>{try{
    const d=JSON.parse(r.result); const inc=Array.isArray(d)?d:d.notes;
    if(!Array.isArray(inc)) throw 0;
    if(d.paper&&d.paper!==cur.id&&!confirm(`Berkas ini untuk naskah "${d.paper}", bukan "${cur.id}". Tetap muat?`)) return;
    const have=new Set(notes.map(n=>n.id));
    let n0=0; inc.forEach(n=>{if(n&&n.text&&!have.has(n.id)){notes.push(n);n0++;}});
    notes.sort((a,b)=>a.b-b.b); save(cur.id,notes); paint();
    alert(n0+' komentar dimuat ('+(inc.length-n0)+' sudah ada).');
  }catch(err){alert('Berkas tidak terbaca sebagai komentar.');}};
  r.readAsText(f); e.target.value='';
 };

 window.initLibrary=function(){ if($('libReader').classList.contains('on')) return; home(); };
})();
