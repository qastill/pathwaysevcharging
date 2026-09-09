"""Sisipkan (atau perbarui) tab '🔗 Kombinasi' di index.html dari resources/combine/.

Idempoten: blok lama dicopot lebih dulu, jadi aman dijalankan berkali-kali tanpa
`git checkout index.html`. Batas blok: <!-- KB:BEGIN/END --> (markup),
/* KB:BEGIN/END */ (skrip), dan payload `Object.assign(D,{kb:...});`.

Jalankan dari akar repositori:
    python3 resources/combine/prepare.py
    python3 resources/combine/inject.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

TAB = '["combine","🔗 Kombinasi"]'
HOOK = "\n if(tb.dataset.p==='combine'&&window.initCombine)setTimeout(window.initCombine,60);"
BEG, END = "<!-- KB:BEGIN -->", "<!-- KB:END -->"
JSBEG, JSEND = "/* KB:BEGIN */", "/* KB:END */"

src = open("index.html", encoding="utf-8").read()


def once(hay, needle):
    assert hay.count(needle) == 1, "anchor tidak unik/tidak ditemukan: " + needle[:70]


# ---------------------------------------------------------------- copot lama
had = 'id="p-combine"' in src
src = src.replace("," + TAB, "").replace(HOOK, "")
src = re.sub(re.escape(BEG) + r".*?" + re.escape(END) + r"\n?", "", src, flags=re.S)
src = re.sub(re.escape(JSBEG) + r".*?" + re.escape(JSEND) + r"\n", "", src, flags=re.S)
src = src.replace("<script>\n</script>\n", "")
src = src.replace('"resources","combine"]', '"resources"]')  # cabut dari grup navigasi
src = re.sub(r"Object\.assign\(D,\{kb:.*?\}\);\n", "", src, count=1, flags=re.S)
assert 'id="p-combine"' not in src, "sisa injeksi lama tertinggal"
print("blok lama dicopot" if had else "injeksi pertama")

# ------------------------------------------------------------- 1) daftar tab
anchor_tab = '["resources","🧰 Repositori Riset"]'
once(src, anchor_tab)
src = src.replace(anchor_tab, anchor_tab + "," + TAB, 1)

# --------------------------------------------------- 2) pemicu init saat tab dibuka
hook_anchor = "if(tb.dataset.p==='resources'&&window.initResources)setTimeout(window.initResources,60);"
once(src, hook_anchor)
src = src.replace(hook_anchor, hook_anchor + HOOK, 1)

# ------------------------------------------------- 3) masukkan ke grup navigasi
nav_anchor = '["open","🌍 Open Source & Data Dunia",["insight","ocm","evmodels","resources"]]'
once(src, nav_anchor)
src = src.replace(nav_anchor, nav_anchor.replace('"resources"]', '"resources","combine"]'), 1)

# ------------------------------------------------------------- 4) markup halaman
anchor_page = "<!-- SUMMARY (paper) -->"
once(src, anchor_page)
page = open("resources/combine/page.html", encoding="utf-8").read()
src = src.replace(anchor_page, BEG + "\n" + page + END + "\n" + anchor_page, 1)

# ------------------------------------------------------------------ 5) payload
data_anchor = "Object.assign(D,{grid:"
once(src, data_anchor)
payload = open("resources/combine/combine.json", encoding="utf-8").read().strip()
src = src.replace(data_anchor, "Object.assign(D,{kb:%s});\n" % payload + data_anchor, 1)

# ----------------------------------------------------------------- 6) renderer
tail_re = re.compile(r"</body>\s*</html>\s*$")
assert tail_re.search(src), "ekor index.html tidak seperti yang diharapkan"
js = open("resources/combine/render.js", encoding="utf-8").read()
block = "<script>\n" + JSBEG + js + JSEND + "\n</script>\n</body></html>\n"
src = tail_re.sub(lambda m: block, src, count=1)  # lambda: isi skrip disisipkan apa adanya

open("index.html", "w", encoding="utf-8").write(src)
print("tab terpasang; ukuran index.html: %.0f KB" % (len(src) / 1024))
