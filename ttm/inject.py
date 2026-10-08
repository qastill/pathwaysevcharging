"""Sisipkan (atau perbarui) tab '⏱️ Akses Waktu Tempuh' di index.html dari ttm/.

Idempoten: blok lama dicopot lebih dulu. Batas blok: <!-- TTM:BEGIN/END --> (markup) dan /* TTM:BEGIN/END */ (skrip).
Payload (ttm/ttm.json ~0,6 MB, ttm/input/villages_simplified.geojson ~4 MB, ttm/input/spklu_sites.csv) TIDAK disisipkan;
render.js memuatnya saat tab dibuka pertama kali. Tab masuk grup navigasi 🎓 PhD Monash, setelah 'phddata'.

    python3 ttm/compute.py --kontur /path/kontur_ID.gpkg   # -> ttm/ttm.json
    python3 ttm/inject.py                                   # -> pasang tab (aman diulang)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TAB = '["ttm","⏱️ Akses Waktu Tempuh"]'
HOOK = "\n if(tb.dataset.p==='ttm'&&window.initTTM)setTimeout(window.initTTM,60);"
BEG, END = "<!-- TTM:BEGIN -->", "<!-- TTM:END -->"
JSBEG, JSEND = "/* TTM:BEGIN */", "/* TTM:END */"
NAV_RE = re.compile(r'(\["phd","🎓 PhD Monash",\[[^\]]*"phddata",)')

src = open("index.html", encoding="utf-8").read()


def once(hay, needle):
    assert hay.count(needle) == 1, "anchor tidak unik/tidak ditemukan: " + needle[:70]


# ---------------------------------------------------------------- copot lama
had = 'id="p-ttm"' in src
src = src.replace("," + TAB, "").replace(HOOK, "")
src = re.sub(r'(\["phd","🎓 PhD Monash",\[[^\]]*\])', lambda m: m.group(1).replace('"ttm",', ''), src, count=1)
src = re.sub(re.escape(BEG) + r".*?" + re.escape(END) + r"\n?", "", src, flags=re.S)
src = re.sub(re.escape(JSBEG) + r".*?" + re.escape(JSEND) + r"\n", "", src, flags=re.S)
src = src.replace("<script>\n</script>\n", "")
assert 'id="p-ttm"' not in src, "sisa injeksi lama tertinggal"
print("blok lama dicopot" if had else "injeksi pertama")

# ------------------------------------------------------------- 1) daftar tab
anchor_tab = '["phddata","🗃️ Data & Bukti"]'
once(src, anchor_tab)
src = src.replace(anchor_tab, anchor_tab + "," + TAB, 1)

# --------------------------------------------------- 2) pemicu init saat tab dibuka
hook_anchor = "if(tb.dataset.p==='sector'&&window.initSector)setTimeout(window.initSector,80);"
once(src, hook_anchor)
src = src.replace(hook_anchor, hook_anchor + HOOK, 1)

# ------------------------------------------------- 3) grup navigasi PhD Monash (sisip setelah "phddata")
assert len(NAV_RE.findall(src)) == 1, "grup navigasi PhD Monash tidak ditemukan"
src = NAV_RE.sub(lambda m: m.group(1) + '"ttm",', src, count=1)

# ------------------------------------------------------------- 4) markup halaman
anchor_page = "<!-- SUMMARY (paper) -->"
once(src, anchor_page)
page = open("ttm/page.html", encoding="utf-8").read()
src = src.replace(anchor_page, BEG + "\n" + page + END + "\n" + anchor_page, 1)

# ----------------------------------------------------------------- 5) renderer
tail_re = re.compile(r"</body>\s*</html>\s*$")
assert tail_re.search(src), "ekor index.html tidak seperti yang diharapkan"
js = open("ttm/render.js", encoding="utf-8").read()
block = "<script>\n" + JSBEG + js + JSEND + "\n</script>\n</body></html>\n"
src = tail_re.sub(lambda m: block, src, count=1)

open("index.html", "w", encoding="utf-8").write(src)
print("tab terpasang; ukuran index.html: %.0f KB" % (len(src) / 1024))
