"""Sisipkan (atau perbarui) tab '🌏 ASEAN Paper' di index.html. Idempoten."""
import re

BEG, END = "<!-- ASEAN:BEGIN -->", "<!-- ASEAN:END -->"
JS_BEG, JS_END = "/* ASEAN:BEGIN */", "/* ASEAN:END */"
TAB = ',["asean","🌏 ASEAN Paper"]'

src = open("index.html", encoding="utf-8").read()

had = "p-asean" in src
src = src.replace(TAB, "")
src = re.sub(re.escape(BEG) + r".*?" + re.escape(END) + r"\n?", "", src, flags=re.S)
src = re.sub(re.escape(JS_BEG) + r".*?" + re.escape(JS_END), "", src, flags=re.S)
assert "p-asean" not in src, "sisa injeksi lama masih tertinggal"
print("blok lama dicopot" if had else "injeksi pertama")

def once(hay, needle):
    assert hay.count(needle) == 1, "anchor tidak unik/tidak ditemukan: " + needle[:60]

# 1) daftar tab — sisipkan tepat sebelum Summary
base = '["summary","Summary"]'
once(src, base); src = src.replace(base, TAB.lstrip(",") + "," + base, 1)

# 2) markup halaman — sebelum blok tab EV x Jaringan
anchor = "<!-- GX:BEGIN -->"
once(src, anchor)
page = BEG + "\n" + open("papers/asean/page.html", encoding="utf-8").read() + END + "\n"
src = src.replace(anchor, page + anchor, 1)

# 3) renderer
tail = "\n</script></body></html>"
assert src.endswith(tail)
src = (src[:-len(tail)] + JS_BEG
       + open("papers/asean/render.js", encoding="utf-8").read()
       + JS_END + tail)

open("index.html", "w", encoding="utf-8").write(src)
print("tab ASEAN terpasang; ukuran index.html:", len(src))
