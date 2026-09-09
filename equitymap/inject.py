"""Sisipkan (atau perbarui) tab '🗺️ Peta Ekuitas' di index.html dari equitymap/.

Idempoten: blok lama dicopot lebih dulu, jadi aman dijalankan berkali-kali tanpa
`git checkout index.html`. Batas blok: <!-- EQ:BEGIN/END --> (markup) dan /* EQ:BEGIN/END */ (skrip).
Payload TIDAK disisipkan ke index.html: `equitymap/equity.js` (2,6 MB) dan `equitymap/vendor/h3-js.umd.js`
dimuat oleh render.js hanya saat tab dibuka pertama kali.

Jalankan dari akar repositori:
    python3 equitymap/prepare.py     # -> equitymap/equity.js
    python3 equitymap/inject.py      # -> pasang tab (aman diulang)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TAB = '["ekuitas","🗺️ Peta Ekuitas"]'
HOOK = "\n if(tb.dataset.p==='ekuitas'&&window.initEquity)setTimeout(window.initEquity,60);"
BEG, END = "<!-- EQ:BEGIN -->", "<!-- EQ:END -->"
JSBEG, JSEND = "/* EQ:BEGIN */", "/* EQ:END */"
NAV_OLD = '["peta","🗺️ Peta & Jaringan",["map","locint","geopeta","jaringan"]]'
NAV_NEW = '["peta","🗺️ Peta & Jaringan",["map","locint","ekuitas","geopeta","jaringan"]]'

src = open("index.html", encoding="utf-8").read()


def once(hay, needle):
    assert hay.count(needle) == 1, "anchor tidak unik/tidak ditemukan: " + needle[:70]


# ---------------------------------------------------------------- copot lama
had = 'id="p-ekuitas"' in src
src = src.replace("," + TAB, "").replace(HOOK, "").replace(NAV_NEW, NAV_OLD)
src = re.sub(re.escape(BEG) + r".*?" + re.escape(END) + r"\n?", "", src, flags=re.S)
src = re.sub(re.escape(JSBEG) + r".*?" + re.escape(JSEND) + r"\n", "", src, flags=re.S)
src = src.replace("<script>\n</script>\n", "")
assert 'id="p-ekuitas"' not in src, "sisa injeksi lama tertinggal"
print("blok lama dicopot" if had else "injeksi pertama")

# ------------------------------------------------------------- 1) daftar tab
anchor_tab = '["locint","Location Intelligence"]'
once(src, anchor_tab)
src = src.replace(anchor_tab, anchor_tab + "," + TAB, 1)

# --------------------------------------------------- 2) pemicu init saat tab dibuka
hook_anchor = "if(tb.dataset.p==='sector'&&window.initSector)setTimeout(window.initSector,80);"
once(src, hook_anchor)
src = src.replace(hook_anchor, hook_anchor + HOOK, 1)

# ------------------------------------------------- 3) grup navigasi Peta & Jaringan
once(src, NAV_OLD)
src = src.replace(NAV_OLD, NAV_NEW, 1)

# ------------------------------------------------------------- 4) markup halaman
anchor_page = "<!-- SUMMARY (paper) -->"
once(src, anchor_page)
page = open("equitymap/page.html", encoding="utf-8").read()
src = src.replace(anchor_page, BEG + "\n" + page + END + "\n" + anchor_page, 1)

# ----------------------------------------------------------------- 5) renderer
tail_re = re.compile(r"</body>\s*</html>\s*$")
assert tail_re.search(src), "ekor index.html tidak seperti yang diharapkan"
js = open("equitymap/render.js", encoding="utf-8").read()
block = "<script>\n" + JSBEG + js + JSEND + "\n</script>\n</body></html>\n"
src = tail_re.sub(lambda m: block, src, count=1)  # lambda: isi skrip disisipkan apa adanya

open("index.html", "w", encoding="utf-8").write(src)
print("tab terpasang; ukuran index.html: %.0f KB" % (len(src) / 1024))
