"""Sisipkan (atau perbarui) tab '⚖️ Ekuitas vs Kesetaraan' di index.html (grup Analisis SPKLU, setelah Spatial Equity).

Idempoten. Batas blok: <!-- KD:BEGIN/END -->, /* KD:BEGIN/END */, payload `Object.assign(D,{kd:...});`.

    python3 equitymap/keadilan.py
    python3 equitymap/keadilan_inject.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TAB = '["keadilan","⚖️ Ekuitas vs Kesetaraan"]'
HOOK = "\n if(tb.dataset.p==='keadilan'&&window.initKeadilan)setTimeout(window.initKeadilan,60);"
BEG, END = "<!-- KD:BEGIN -->", "<!-- KD:END -->"
JSBEG, JSEND = "/* KD:BEGIN */", "/* KD:END */"
NAV_RE = re.compile(r'(\["analisis","📊 Analisis SPKLU",\[[^\]]*"equity",)')

src = open("index.html", encoding="utf-8").read()


def once(hay, needle):
    assert hay.count(needle) == 1, "anchor tidak unik/tidak ditemukan: " + needle[:70]


had = 'id="p-keadilan"' in src
src = src.replace("," + TAB, "").replace(HOOK, "")
src = re.sub(r'(\["analisis","📊 Analisis SPKLU",\[[^\]]*\])', lambda m: m.group(1).replace('"keadilan",', ''), src, count=1)
src = re.sub(re.escape(BEG) + r".*?" + re.escape(END) + r"\n?", "", src, flags=re.S)
src = re.sub(re.escape(JSBEG) + r".*?" + re.escape(JSEND) + r"\n", "", src, flags=re.S)
src = src.replace("<script>\n</script>\n", "")
src = re.sub(r"Object\.assign\(D,\{kd:.*?\}\);\n", "", src, count=1, flags=re.S)
assert 'id="p-keadilan"' not in src, "sisa injeksi lama tertinggal"
print("blok lama dicopot" if had else "injeksi pertama")

anchor_tab = '["equity","Spatial Equity"]'
once(src, anchor_tab)
src = src.replace(anchor_tab, anchor_tab + "," + TAB, 1)

hook_anchor = "if(tb.dataset.p==='sector'&&window.initSector)setTimeout(window.initSector,80);"
once(src, hook_anchor)
src = src.replace(hook_anchor, hook_anchor + HOOK, 1)

assert len(NAV_RE.findall(src)) == 1, "grup navigasi Analisis SPKLU tidak ditemukan"
src = NAV_RE.sub(lambda m: m.group(0) + '"keadilan",', src, count=1)

anchor_page = "<!-- SUMMARY (paper) -->"
once(src, anchor_page)
page = open("equitymap/keadilan_page.html", encoding="utf-8").read()
src = src.replace(anchor_page, BEG + "\n" + page + END + "\n" + anchor_page, 1)

data_anchor = "Object.assign(D,{grid:"
once(src, data_anchor)
payload = open("equitymap/keadilan.json", encoding="utf-8").read().strip()
src = src.replace(data_anchor, "Object.assign(D,{kd:%s});\n" % payload + data_anchor, 1)

tail_re = re.compile(r"</body>\s*</html>\s*$")
assert tail_re.search(src), "ekor index.html tidak seperti yang diharapkan"
js = open("equitymap/keadilan_render.js", encoding="utf-8").read()
block = "<script>\n" + JSBEG + js + JSEND + "\n</script>\n</body></html>\n"
src = tail_re.sub(lambda m: block, src, count=1)

open("index.html", "w", encoding="utf-8").write(src)
print("tab terpasang; ukuran index.html: %.0f KB" % (len(src) / 1024))
