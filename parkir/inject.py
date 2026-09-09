"""Sisipkan (atau perbarui) tab '🅿️ Parkir × Charger' di index.html dari parkir/.

Idempoten: blok lama dicopot lebih dulu. Batas blok: <!-- PK:BEGIN/END --> (markup) dan
/* PK:BEGIN/END */ (skrip). Payload `parkir/parkir.js` (≈1 MB) dimuat malas oleh render.js.

    python3 parkir/prepare.py
    python3 parkir/inject.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TAB = '["parkir","🅿️ Parkir × Charger"]'
HOOK = "\n if(tb.dataset.p==='parkir'&&window.initParkir)setTimeout(window.initParkir,60);"
BEG, END = "<!-- PK:BEGIN -->", "<!-- PK:END -->"
JSBEG, JSEND = "/* PK:BEGIN */", "/* PK:END */"
NAV_RE = re.compile(r'(\["peta","🗺️ Peta & Jaringan",\[[^\]]*"locint",(?:"ekuitas",)?)')   # sisip setelah locint/ekuitas

src = open("index.html", encoding="utf-8").read()


def once(hay, needle):
    assert hay.count(needle) == 1, "anchor tidak unik/tidak ditemukan: " + needle[:70]


had = 'id="p-parkir"' in src
src = src.replace("," + TAB, "").replace(HOOK, "")
src = re.sub(r'(\["peta","🗺️ Peta & Jaringan",\[[^\]]*\])', lambda m: m.group(1).replace('"parkir",', ''), src, count=1)  # cabut dari grup navigasi saja
src = re.sub(re.escape(BEG) + r".*?" + re.escape(END) + r"\n?", "", src, flags=re.S)
src = re.sub(re.escape(JSBEG) + r".*?" + re.escape(JSEND) + r"\n", "", src, flags=re.S)
src = src.replace("<script>\n</script>\n", "")
assert 'id="p-parkir"' not in src, "sisa injeksi lama tertinggal"
print("blok lama dicopot" if had else "injeksi pertama")

anchor_tab = '["ekuitas","🗺️ Peta Ekuitas"]'
once(src, anchor_tab)
src = src.replace(anchor_tab, anchor_tab + "," + TAB, 1)

hook_anchor = "if(tb.dataset.p==='sector'&&window.initSector)setTimeout(window.initSector,80);"
once(src, hook_anchor)
src = src.replace(hook_anchor, hook_anchor + HOOK, 1)

assert len(NAV_RE.findall(src)) == 1, "grup navigasi Peta & Jaringan tidak ditemukan"
src = NAV_RE.sub(lambda m: m.group(0) + '"parkir",', src, count=1)

anchor_page = "<!-- SUMMARY (paper) -->"
once(src, anchor_page)
page = open("parkir/page.html", encoding="utf-8").read()
src = src.replace(anchor_page, BEG + "\n" + page + END + "\n" + anchor_page, 1)

tail_re = re.compile(r"</body>\s*</html>\s*$")
assert tail_re.search(src), "ekor index.html tidak seperti yang diharapkan"
js = open("parkir/render.js", encoding="utf-8").read()
block = "<script>\n" + JSBEG + js + JSEND + "\n</script>\n</body></html>\n"
src = tail_re.sub(lambda m: block, src, count=1)

open("index.html", "w", encoding="utf-8").write(src)
print("tab terpasang; ukuran index.html: %.0f KB" % (len(src) / 1024))
