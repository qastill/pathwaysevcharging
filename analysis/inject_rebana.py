"""Tempel halaman Powering Rebana explorer (analysis/rebana_explorer.html) sebagai tab '🏭 Rebana' di grup 🎓 PhD Monash
pada index.html, setelah tab 'ladder1'. Idempoten: blok lama dicopot dulu (penanda REBANA:BEGIN/END).

    python3 analysis/inject_rebana.py
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
TAB = '["rebana","🏭 Rebana"]'
BEG, END = "<!-- REBANA:BEGIN -->", "<!-- REBANA:END -->"
src = open("index.html", encoding="utf-8").read()
# copot lama
src = src.replace("," + TAB, "")
src = re.sub(re.escape(BEG) + r".*?" + re.escape(END) + r"\n?", "", src, flags=re.S)
src = src.replace('"ladder1","rebana"', '"ladder1"')
# tab + grup nav
a = '["ladder1","🪜 Ladder 1"]'; assert src.count(a) == 1
src = src.replace(a, a + "," + TAB)
a = '["phd","🎓 PhD Monash",["phd","phdequity","phddata","ttm","ladder1","phdref"]]'; assert src.count(a) == 1
src = src.replace(a, '["phd","🎓 PhD Monash",["phd","phdequity","phddata","ttm","ladder1","rebana","phdref"]]')
page = BEG + '''
<div class="page" id="p-rebana">
<div class="card" style="padding:10px 14px;margin-bottom:10px;display:flex;gap:14px;align-items:center;flex-wrap:wrap">
 <div style="flex:1;min-width:260px"><b>🏭 Powering Rebana — facts, PLN data, projections and ideas (EN/ID)</b><br><span style="font-size:12px;color:var(--mut)">Twenty-five one-screen chapters for the 2nd Powering Rebana Workshop (Cirebon, 5–6 Nov 2026) on live CARTO / OpenStreetMap / Esri basemaps: the 13 industrial zones mapped with their build-out electricity demand, investment, gateways and power plants from public sources; the PhD data assets; an Indramayu field map (31 kecamatan, 4 ULP incl. Cikedung, GI loading) and UP3 Indramayu's Jan–Sep 2026 sales; an EV ecosystem and charging-equity part (factory-to-plug chain, utilisation and mudik peak, r5r travel-time equity over 1,981 villages, Lorenz/concentration indices, EV load vs substation headroom); Rebana-only facts computed from PLN SPKLU transactions, home-charging register and substation loading; three movable 2030 projections; four working work-package models (grid-first siting, rest-area solar pilot, next 12 charging sites, electrical workforce). Language switch EN/ID inside; ← → keys to move.</span></div>
 <a class="dl" href="analysis/rebana_explorer.html" target="_blank" rel="noopener">Open full page ↗</a>
</div>
<iframe id="rebanaFrame" title="Powering Rebana explorer" src="about:blank" data-src="analysis/rebana_explorer.html" style="width:100%;height:calc(100vh - 150px);min-height:640px;border:1px solid var(--line);border-radius:12px;background:#fff"></iframe>
</div>
''' + END + "\n"
anchor = '<div class="page phdp" id="p-phdref">'; assert src.count(anchor) == 1
src = src.replace(anchor, page + anchor)
hook_anchor = " if(tb.dataset.p==='ttm'&&window.initTTM)setTimeout(window.initTTM,60);"; assert src.count(hook_anchor) == 1
HOOK = "\n if(tb.dataset.p==='rebana'){const f=document.getElementById('rebanaFrame');if(f&&f.dataset.src){f.src=f.dataset.src;delete f.dataset.src;}}"
src = src.replace(HOOK, "")
src = src.replace(hook_anchor, hook_anchor + HOOK, 1)
open("index.html", "w", encoding="utf-8").write(src)
print("tab Rebana terpasang; index.html %.0f KB" % (len(src) / 1024))
