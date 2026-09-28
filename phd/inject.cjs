/* Reapply PhD navigation after existing dashboard generators. Safe to run repeatedly. */
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const file = path.join(root, 'index.html');
let html = fs.readFileSync(file, 'utf8');
if (!html.includes('const TABS=[') || !html.includes('const NAVGROUPS=[')) throw new Error('Dashboard navigation format changed; review PhD integration.');
if (!html.includes('["phd","PhD Workspace"]')) html = html.replace('const TABS=[', 'const TABS=[["phd","PhD Workspace"],');
// Preserve Overview as the initial page even when PhD is added before the original tabs.
html = html.replace("${i==0?' active':''}", "${t[0]==='overview'?' active':''}");
const groupPattern = /const NAVGROUPS=(\[[\s\S]*?\]);/;
const match = html.match(groupPattern);
if (!match) throw new Error('NAVGROUPS not found');
const groups = JSON.parse(match[1]);
const moved = ['equity','keadilan','ekuitas','socio','perception'];
const next = groups.filter(g => g[0] !== 'phd').map(g => [g[0], g[1], g[2].filter(id => !moved.includes(id) && id !== 'phd')]);
next.splice(1,0,['phd','🎓 PhD Monash',['phd',...moved]]);
html = html.replace(groupPattern, 'const NAVGROUPS='+JSON.stringify(next)+';');
const section = `<!-- PHD:BEGIN -->
<div class="page" id="p-phd">
<div style="display:flex;justify-content:space-between;gap:12px;align-items:center;padding:14px 0;font-size:12px"><span>PhD Monash · catatan, metode, dan checkpoint penelitian. Filter wilayah tidak berlaku untuk ruang kerja ini.</span><a href="phd/" target="_blank" rel="noopener" style="white-space:nowrap">Buka layar penuh ↗</a></div>
<iframe src="phd/" title="PhD Monash research workspace" loading="lazy" style="width:100%;height:1150px;border:1px solid #dde4df;border-radius:12px;background:#f5f6f2"></iframe>
</div>
<!-- PHD:END -->`;
html = html.replace(/<!-- PHD:BEGIN -->[\s\S]*?<!-- PHD:END -->\s*/g,'');
if (!html.includes('<!-- OVERVIEW -->')) throw new Error('Overview anchor not found');
html = html.replace('<!-- OVERVIEW -->',section+'\n\n<!-- OVERVIEW -->');
fs.writeFileSync(file,html);
console.log('PhD Monash: workspace and five research modules registered.');
