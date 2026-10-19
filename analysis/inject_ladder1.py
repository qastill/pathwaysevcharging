"""Tempel halaman cerita bahasa Inggris (analysis/charging_equity_en.html) sebagai tab '🪜 Ladder 1' di grup 🎓 PhD Monash
pada index.html, setelah tab 'ttm'. Idempoten: blok lama dicopot dulu (penanda LADDER1:BEGIN/END).

    python3 analysis/inject_ladder1.py
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
TAB = '["ladder1","🪜 Ladder 1"]'
BEG, END = "<!-- LADDER1:BEGIN -->", "<!-- LADDER1:END -->"
src = open("index.html", encoding="utf-8").read()
# copot lama
src = src.replace("," + TAB, "")
src = re.sub(re.escape(BEG) + r".*?" + re.escape(END) + r"\n?", "", src, flags=re.S)
src = src.replace('"ttm","ladder1"', '"ttm"')
# tab + grup nav
a = '["ttm","⏱️ Akses Waktu Tempuh"]'; assert src.count(a) == 1
src = src.replace(a, a + "," + TAB)
a = '["phd","🎓 PhD Monash",["phd","phdequity","phddata","ttm","phdref"]]'; assert src.count(a) == 1
src = src.replace(a, '["phd","🎓 PhD Monash",["phd","phdequity","phddata","ttm","ladder1","phdref"]]')
# halaman: iframe setinggi viewport, deep link ke bab travel time, dengan tautan buka penuh
page = BEG + '''
<div class="page" id="p-ladder1">
<div class="card" style="padding:10px 14px;margin-bottom:10px;display:flex;gap:14px;align-items:center;flex-wrap:wrap">
 <div style="flex:1;min-width:260px"><b>🪜 Ladder 1 — Charging equity story (English)</b><br><span style="font-size:12px;color:var(--mut)">Ten one-screen chapters: who gets Indonesia's / West Java's public chargers, the 10-minute reach and E2SFCA capacity rungs of the service ladder (RQ1), concentration indices with a within-district filter, Theil sources, evidence and method. Use the sidebar inside, or the ← → keys.</span></div>
 <a class="dl" href="analysis/charging_equity_en.html#jabar/travel" target="_blank" rel="noopener">Open full page ↗</a>
</div>
<iframe id="ladder1Frame" title="Charging equity story" src="about:blank" data-src="analysis/charging_equity_en.html#jabar/travel" style="width:100%;height:calc(100vh - 150px);min-height:640px;border:1px solid var(--line);border-radius:12px;background:#fff"></iframe>
</div>
''' + END + "\n"
anchor = '<div class="page phdp" id="p-phdref">'; assert src.count(anchor) == 1
src = src.replace(anchor, page + anchor)
# muat iframe saat tab dibuka pertama kali (hook yang sama dengan ttm)
hook_anchor = " if(tb.dataset.p==='ttm'&&window.initTTM)setTimeout(window.initTTM,60);"; assert src.count(hook_anchor) == 1
HOOK = "\n if(tb.dataset.p==='ladder1'){const f=document.getElementById('ladder1Frame');if(f&&f.dataset.src){f.src=f.dataset.src;delete f.dataset.src;}}"
src = src.replace(HOOK, "")
src = src.replace(hook_anchor, hook_anchor + HOOK, 1)
open("index.html", "w", encoding="utf-8").write(src)
print("tab Ladder 1 terpasang; index.html %.0f KB" % (len(src) / 1024))
