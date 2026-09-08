
/* ===================== REPOSITORI RISET — database sumber terbuka (D.res) ===================== */
(function(){
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>(n==null||isNaN(n))?'—':(+n).toLocaleString('en-US');
const KIND={repo:'Repo',org:'Org',topic:'Topic',dataset:'Dataset',portal:'Portal',standard:'Standar'};
const S={group:'',cat:'',sub:'',q:'',kind:'',theme:'',sort:'cat',feat:false};
let R=null,stars={},built=false;
const HASH0=location.hash; // dibaca saat muat: gotoTab() menimpa hash sebelum tab sempat diinisialisasi

function data(){R=R||(typeof D!=="undefined"&&D.res)||null;return R;}
function cat(id){return R.cats.find(c=>c.id===id);}
function group(id){return R.groups.find(g=>g.id===id);}
function catsOf(g){return R.cats.filter(c=>!g||c.group===g);}

/* ---------- cache bintang: localStorage, 7 hari ---------- */
function loadCache(){try{const c=JSON.parse(localStorage.getItem('rsStars')||'{}');if(c.ts&&Date.now()-c.ts<7*864e5)stars=c.d||{};}catch(e){}}
function saveCache(){try{localStorage.setItem('rsStars',JSON.stringify({ts:Date.now(),d:stars}));}catch(e){}}

/* ---------- penyaringan ---------- */
function visible(){
 const q=S.q.trim().toLowerCase();
 let it=R.items.filter(i=>{
  if(S.group&&cat(i.cat).group!==S.group)return false;
  if(S.cat&&i.cat!==S.cat)return false;
  if(S.sub&&i.sub!==S.sub)return false;
  if(S.kind&&i.kind!==S.kind)return false;
  if(S.theme&&!i.themes.includes(S.theme))return false;
  if(S.feat&&!i.featured)return false;
  if(q){const hay=(i.name+' '+i.id+' '+i.desc+' '+i.role+' '+i.tags.join(' ')+' '+(i.sub||'')).toLowerCase();if(!hay.includes(q))return false;}
  return true;
 });
 const order={};R.cats.forEach((c,k)=>order[c.id]=k);
 if(S.sort==='name')it.sort((a,b)=>a.name.localeCompare(b.name));
 else if(S.sort==='stars')it.sort((a,b)=>((stars[b.id]||{}).s||-1)-((stars[a.id]||{}).s||-1)||a.name.localeCompare(b.name));
 else it.sort((a,b)=>(order[a.cat]-order[b.cat])||((b.featured?1:0)-(a.featured?1:0))||a.name.localeCompare(b.name));
 return it;
}

/* ---------- kontrol ---------- */
function renderGroups(){
 const all=R.items.length;
 const g=[['','Semua',all]].concat(R.groups.map(x=>[x.id,x.icon+' '+x.label,R.items.filter(i=>cat(i.cat).group===x.id).length]));
 $('rsGroups').innerHTML=g.map(x=>`<div class="rsg${S.group===x[0]?' active':''}" data-g="${x[0]}">${esc(x[1])}<span class="n">${x[2]}</span></div>`).join('');
 $('rsGroups').querySelectorAll('.rsg').forEach(el=>el.onclick=()=>{S.group=el.dataset.g;S.cat='';S.sub='';renderAll();});
}
function renderCats(){
 const cs=catsOf(S.group);
 $('rsCats').innerHTML=`<div class="rsc${!S.cat?' active':''}" data-c="">Semua kategori <span class="n">${cs.reduce((a,c)=>a+c.n,0)}</span></div>`+
  cs.map(c=>`<div class="rsc${S.cat===c.id?' active':''}" data-c="${c.id}"><i style="background:${c.color}"></i>${esc(c.label)}<span class="n">${c.n}</span></div>`).join('');
 $('rsCats').querySelectorAll('.rsc').forEach(el=>el.onclick=()=>{S.cat=el.dataset.c;S.sub='';renderAll();});
 const c=S.cat?cat(S.cat):null;
 const subs=c&&c.subs&&c.subs.length?c.subs:[];
 $('rsSubs').innerHTML=subs.length?`<div class="rss${!S.sub?' active':''}" data-s="">Semua sub</div>`+subs.map(s=>{const n=R.items.filter(i=>i.cat===c.id&&i.sub===s).length;return `<div class="rss${S.sub===s?' active':''}" data-s="${esc(s)}">${esc(s)} · ${n}</div>`;}).join(''):'';
 $('rsSubs').querySelectorAll('.rss').forEach(el=>el.onclick=()=>{S.sub=el.dataset.s;renderAll();});
 const info=$('rsCatInfo');
 if(c)info.innerHTML=`<b>${esc(c.label)}.</b> ${esc(c.desc)}`;
 else if(S.group){const g=group(S.group);info.innerHTML=`<b>${esc(g.label)}.</b> ${esc(g.desc)}`;}
 else info.innerHTML=`<b>Cara membaca.</b> Pilih grup → kategori → (sub-kategori). Kartu bertepi emas = <b>inti</b> untuk riset ini. Baris kuning di tiap kartu menjelaskan <b>perannya</b> dalam riset SPKLU; chip berwarna = tema riset yang sama dengan Perpustakaan; chip biru = tab dashboard yang memakai sumber itu.`;
}
function renderStats(){
 const repos=R.items.filter(i=>i.kind==='repo').length;
 const linked=R.items.filter(i=>i.tabs.length).length;
 $('rsStats').innerHTML=[[R.items.length,'entri'],[repos,'repo GitHub'],[R.cats.length,'kategori'],[R.meta.featured,'inti'],[linked,'dipakai di tab'],[R.meta.generated,'diperbarui']]
  .map(s=>`<div class="s"><div class="n">${esc(s[0])}</div><div class="t">${s[1]}</div></div>`).join('');
}

/* ---------- kartu ---------- */
function card(i){
 const c=cat(i.cat);
 const th=i.themes.map(t=>`<span class="ch th" style="background:${R.themes[t][1]}" title="${esc(R.themes[t][0])}">${t}</span>`).join('');
 const tb=i.tabs.map(t=>`<span class="ch tb" data-t="${t}" title="buka tab">↗ ${esc(R.tab_labels[t]||t)}</span>`).join('');
 const tg=i.tags.map(t=>`<span class="ch">${esc(t)}</span>`).join('');
 const links=[`<a href="${esc(i.url)}" target="_blank" rel="noopener">${i.kind==='repo'||i.kind==='org'||i.kind==='topic'?'GitHub':'buka'} ↗</a>`]
  .concat(i.links.map(l=>`<a href="${esc(l[1])}" target="_blank" rel="noopener">${esc(l[0])} ↗</a>`)).join('');
 const st=stars[i.id];
 const gh=i.kind==='repo'?`<div class="gh" id="rsgh-${esc(i.id.replace(/[^a-z0-9]/gi,'_'))}">${st?ghHtml(st):''}</div>`:'';
 return `<div class="rc${i.featured?' feat':''}" data-id="${esc(i.id)}">
  <div class="top"><div class="nm"><a href="${esc(i.url)}" target="_blank" rel="noopener">${esc(i.name)}</a></div><span class="kind ${i.kind}">${KIND[i.kind]||i.kind}</span></div>
  ${i.path?`<div class="path">${esc(i.path)}</div>`:''}
  <div class="cat" style="color:${c.color}"><i style="background:${c.color}"></i>${esc(c.label)}${i.sub?` <span class="sub">· ${esc(i.sub)}</span>`:''}</div>
  <div class="ds">${esc(i.desc)}</div>
  <div class="rl">🔬 ${esc(i.role)}</div>
  <div class="chips">${th}${tb}${tg}</div>
  ${gh}
  <div class="links">${links}</div>
 </div>`;
}
function ghHtml(d){return `<span>★ <b>${fmt(d.s)}</b></span><span>⑂ ${fmt(d.f)}</span>${d.l?'<span>● '+esc(d.l)+'</span>':''}<span>push ${d.p?d.p.slice(0,10):'—'}</span>`;}

function renderGrid(){
 const it=visible();
 $('rsGrid').innerHTML=it.length?it.map(card).join(''):'<div class="rsempty">Tidak ada entri yang cocok. Longgarkan filter atau kosongkan pencarian.</div>';
 $('rsCount').textContent=it.length+' / '+R.items.length+' entri';
 $('rsGrid').querySelectorAll('.tb').forEach(el=>el.onclick=()=>{if(window.gotoTab)window.gotoTab(el.dataset.t);});
}
function renderAll(){renderGroups();renderCats();renderGrid();}

/* ---------- statistik GitHub (hanya yang tampil, ≤50 per klik, cache 7 hari) ---------- */
async function loadStars(){
 const btn=$('rsStarsBtn');const want=visible().filter(i=>i.kind==='repo'&&!stars[i.id]).slice(0,50);
 if(!want.length){btn.textContent='★ Statistik sudah dimuat';renderGrid();return;}
 btn.disabled=true;btn.textContent='★ Mengambil '+want.length+' repo…';
 let ok=0,rate=false;
 await Promise.all(want.map(async i=>{
  try{const r=await fetch('https://api.github.com/repos/'+(i.path||i.id));
   if(r.status===403||r.status===429){rate=true;return;}
   if(r.ok){const j=await r.json();stars[i.id]={s:j.stargazers_count,f:j.forks_count,l:j.language,p:j.pushed_at};ok++;}
  }catch(e){}
 }));
 saveCache();btn.disabled=false;
 const left=visible().filter(i=>i.kind==='repo'&&!stars[i.id]).length;
 btn.textContent=rate?'⚠️ GitHub membatasi laju — coba lagi nanti ('+ok+' dimuat)':(left?'★ Muat '+left+' repo lagi':'★ Statistik sudah dimuat');
 renderGrid();
}

/* ---------- ekspor Markdown untuk daftar yang sedang tampil ---------- */
function exportMd(){
 const it=visible();const by={};it.forEach(i=>(by[i.cat]=by[i.cat]||[]).push(i));
 let md='# Repositori riset SPKLU — '+it.length+' entri ('+R.meta.generated+')\n\n';
 R.cats.forEach(c=>{if(!by[c.id])return;md+='## '+c.label+'\n\n';by[c.id].forEach(i=>{md+='- ['+i.name+']('+i.url+')'+(i.sub?' _('+i.sub+')_':'')+' — '+i.desc+' **Peran:** '+i.role+(i.themes.length?' `'+i.themes.join('` `')+'`':'')+'\n';});md+='\n';});
 const done=()=>{const b=$('rsExport');b.textContent='✓ Tersalin';setTimeout(()=>b.textContent='⬇ Salin Markdown',1800);};
 if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(md).then(done).catch(()=>download(md));else download(md);
}
function download(md){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([md],{type:'text/markdown'}));a.download='repositori-riset.md';a.click();}

/* ---------- init ---------- */
window.initResources=function(){
 if(!data()){$('rsGrid').innerHTML='<div class="rsempty">Payload D.res tidak ditemukan — jalankan python3 resources/inject.py</div>';return;}
 if(built){return;}built=true;loadCache();
 const m=(HASH0.match(/cat=([A-Za-z0-9_-]+)/)||[])[1];if(m&&cat(m)){S.cat=m;S.group=cat(m).group;}
 $('rsTheme').innerHTML='<option value="">Semua tema riset</option>'+Object.keys(R.themes).map(k=>`<option value="${k}">${esc(R.themes[k][0])}</option>`).join('');
 $('rsSearch').oninput=()=>{S.q=$('rsSearch').value;renderGrid();};
 $('rsKind').onchange=()=>{S.kind=$('rsKind').value;renderGrid();};
 $('rsTheme').onchange=()=>{S.theme=$('rsTheme').value;renderGrid();};
 $('rsSort').onchange=()=>{S.sort=$('rsSort').value;renderGrid();};
 $('rsFeat').onclick=()=>{S.feat=!S.feat;$('rsFeat').classList.toggle('active',S.feat);renderGrid();};
 $('rsStarsBtn').onclick=loadStars;
 $('rsExport').onclick=exportMd;
 $('rsFoot').innerHTML='Sumber kebenaran: <code>resources/catalog.py</code> → <code>resources/resources.json</code> → tab ini (<code>python3 resources/inject.py</code>). '+
  'Statistik GitHub diambil langsung dari api.github.com tanpa kunci (60 permintaan/jam), disimpan 7 hari di browser. '+
  'Tema riset mengikuti kategori Perpustakaan; klik chip biru untuk lompat ke tab yang memakai sumber itu.';
 renderStats();renderAll();
};
})();
