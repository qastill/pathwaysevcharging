"""Sisipkan (atau perbarui) tab '🧰 Repositori Riset' di index.html dari resources/.

Idempoten: blok lama dicopot lebih dulu, jadi aman dijalankan berkali-kali
tanpa `git checkout index.html`. Batas blok: <!-- RES:BEGIN/END --> (markup),
/* RES:BEGIN/END */ (skrip), dan payload `Object.assign(D,{res:...});`.

Jalankan dari akar repositori:
    python3 resources/catalog.py   # bangun resources.json
    python3 resources/inject.py    # pasang ke index.html
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TAB = '["resources","🧰 Repositori Riset"]'
HOOK = "\n if(tb.dataset.p==='resources'&&window.initResources)setTimeout(window.initResources,60);"
BEG, END = "<!-- RES:BEGIN -->", "<!-- RES:END -->"
JSBEG, JSEND = "/* RES:BEGIN */", "/* RES:END */"

src = open("index.html", encoding="utf-8").read()


def once(hay, needle):
    assert hay.count(needle) == 1, "anchor tidak unik/tidak ditemukan: " + needle[:70]


# ---------------------------------------------------------------- copot lama
had = 'id="p-resources"' in src
src = src.replace("," + TAB, "").replace(HOOK, "")
src = re.sub(re.escape(BEG) + r".*?" + re.escape(END) + r"\n?", "", src, flags=re.S)
src = re.sub(re.escape(JSBEG) + r".*?" + re.escape(JSEND) + r"\n", "", src, flags=re.S)
src = src.replace("<script>\n</script>\n", "")  # wadah kosong bila tidak ada skrip lain yang menumpang
src = re.sub(r"Object\.assign\(D,\{res:.*?\}\);\n", "", src, count=1, flags=re.S)
assert 'id="p-resources"' not in src, "sisa injeksi lama tertinggal"
print("blok lama dicopot" if had else "injeksi pertama")

# ------------------------------------------------------------- 1) daftar tab
anchor_tab = '["library","📚 Perpustakaan"]'
once(src, anchor_tab)
src = src.replace(anchor_tab, anchor_tab + "," + TAB, 1)

# --------------------------------------------------- 2) pemicu init saat tab dibuka
hook_anchor = "if(tb.dataset.p==='library'&&window.initLibrary)setTimeout(window.initLibrary,60);"
once(src, hook_anchor)
src = src.replace(hook_anchor, hook_anchor + HOOK, 1)

# ------------------------------------------------------------- 3) markup halaman
anchor_page = "<!-- SUMMARY (paper) -->"
once(src, anchor_page)
page = open("resources/page.html", encoding="utf-8").read()
src = src.replace(anchor_page, BEG + "\n" + page + END + "\n" + anchor_page, 1)

# ------------------------------------------------------------------ 4) payload
data_anchor = "Object.assign(D,{grid:"
once(src, data_anchor)
payload = open("resources/resources.json", encoding="utf-8").read().strip()
src = src.replace(data_anchor, "Object.assign(D,{res:%s});\n" % payload + data_anchor, 1)

# ----------------------------------------------------------------- 5) renderer
tail_re = re.compile(r"</body>\s*</html>\s*$")
assert tail_re.search(src), "ekor index.html tidak seperti yang diharapkan"
js = open("resources/render.js", encoding="utf-8").read()
block = "<script>\n" + JSBEG + js + JSEND + "\n</script>\n</body></html>\n"
src = tail_re.sub(lambda m: block, src, count=1)  # lambda: isi skrip disisipkan apa adanya (tanpa tafsir \n)

open("index.html", "w", encoding="utf-8").write(src)
print("tab terpasang; ukuran index.html: %.0f KB" % (len(src) / 1024))
