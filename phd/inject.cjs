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
html=html.replace('["keadilan","⚖️ Ekuitas vs Kesetaraan"]','["keadilan","Equity & Equality"]').replace('["ekuitas","🗺️ Peta Ekuitas"]','["ekuitas","Equity Map"]');
const groupPattern = /const NAVGROUPS=(\[[\s\S]*?\]);/;
const match = html.match(groupPattern);
if (!match) throw new Error('NAVGROUPS not found');
const groups = JSON.parse(match[1]);
const moved = ['equity','keadilan','ekuitas','socio','perception'];
const next = groups.filter(g => g[0] !== 'phd').map(g => [g[0], g[1], g[2].filter(id => !moved.includes(id) && id !== 'phd')]);
next.splice(1,0,['phd','🎓 PhD Monash',['phd',...moved]]);
html = html.replace(groupPattern, 'const NAVGROUPS='+JSON.stringify(next)+';');
const section = `<!-- PHD:BEGIN -->
<div class="page" id="p-phd">${fs.readFileSync(path.join(__dirname,'section.html'),'utf8')}</div>
<!-- PHD:END -->`;
html=html.replace(/<!-- PHD:ASSETS -->[\s\S]*?<!-- PHD:ASSETS:END -->\s*/g,'');
html=html.replace('</head>','<!-- PHD:ASSETS --><link rel="stylesheet" href="phd/styles.css"><script src="phd/app.js" defer></script><!-- PHD:ASSETS:END -->\n</head>');
html = html.replace(/<!-- PHD:BEGIN -->[\s\S]*?<!-- PHD:END -->\s*/g,'');
if (!html.includes('<!-- OVERVIEW -->')) throw new Error('Overview anchor not found');
html = html.replace('<!-- OVERVIEW -->',section+'\n\n<!-- OVERVIEW -->');
fs.writeFileSync(file,html);
console.log('PhD Monash: workspace and five research modules registered.');
