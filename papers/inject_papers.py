"""Sisipkan (atau perbarui) tab '🔌 Capacity Maps' dan '📚 Perpustakaan' di index.html.

Idempoten: blok lama dicopot lebih dulu, jadi aman dijalankan berkali-kali
tanpa `git checkout index.html`.

Jalankan dari akar repositori:  python3 papers/inject_papers.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BLOCKS = [
    dict(key="capacity", tab='["capacity","🔌 Capacity Maps"]',
         beg="<!-- CAP:BEGIN -->", end="<!-- CAP:END -->",
         jsbeg="/* CAP:BEGIN */", jsend="/* CAP:END */",
         page="papers/capacity/page.html", js="papers/capacity/render.js",
         data=[("cap", "papers/capacity/capacity.json")],
         hook="\n if(tb.dataset.p==='capacity'&&window.initCapacity)setTimeout(window.initCapacity,80);"),
    dict(key="library", tab='["library","📚 Perpustakaan"]',
         beg="<!-- LIB:BEGIN -->", end="<!-- LIB:END -->",
         jsbeg="/* LIB:BEGIN */", jsend="/* LIB:END */",
         page="papers/library/page.html", js="papers/library/render.js",
         data=[("lib", "papers/library/library.json")],
         hook="\n if(tb.dataset.p==='library'&&window.initLibrary)setTimeout(window.initLibrary,60);"),
]

src = open("index.html", encoding="utf-8").read()

# ---------------------------------------------------------------- copot lama
for b in BLOCKS:
    had = ('"p-%s"' % b["key"]) in src or ("id=\"p-%s\"" % b["key"]) in src
    src = src.replace("," + b["tab"], "").replace(b["hook"], "")
    src = re.sub(re.escape(b["beg"]) + r".*?" + re.escape(b["end"]) + r"\n?", "", src, flags=re.S)
    src = re.sub(re.escape(b["jsbeg"]) + r".*?" + re.escape(b["jsend"]), "", src, flags=re.S)
    for name, _ in b["data"]:
        src = re.sub(r"Object\.assign\(D,\{" + name + r":.*?\}\);\n", "", src, count=1, flags=re.S)
    assert 'id="p-%s"' % b["key"] not in src, "sisa injeksi lama tertinggal: " + b["key"]
    print(("blok lama dicopot: " if had else "injeksi pertama: ") + b["key"])


def once(hay, needle):
    assert hay.count(needle) == 1, "anchor tidak unik/tidak ditemukan: " + needle[:70]


# ------------------------------------------------------------- 1) daftar tab
anchor_tab = '["asean","🌏 ASEAN Paper"]'
once(src, anchor_tab)
src = src.replace(anchor_tab,
                  anchor_tab + "," + BLOCKS[0]["tab"] + "," + BLOCKS[1]["tab"], 1)

# --------------------------------------------------- 2) pemicu init saat tab dibuka
hook_anchor = "if(tb.dataset.p==='jaringan'&&window.initGx)setTimeout(window.initGx,80);"
once(src, hook_anchor)
src = src.replace(hook_anchor, hook_anchor + BLOCKS[0]["hook"] + BLOCKS[1]["hook"], 1)

# ------------------------------------------------------------- 3) markup halaman
anchor_page = '<div class="page" id="p-summary">'
if src.count(anchor_page) != 1:
    anchor_page = "<!-- ASEAN:BEGIN -->"
    once(src, anchor_page)
pages = "".join(b["beg"] + "\n" + open(b["page"], encoding="utf-8").read() + b["end"] + "\n"
                for b in BLOCKS)
src = src.replace(anchor_page, pages + anchor_page, 1)

# ------------------------------------------------------------------ 4) payload
data_anchor = "Object.assign(D,{grid:"
idx = src.index(data_anchor)
inject = ""
for b in BLOCKS:
    for name, path in b["data"]:
        inject += "Object.assign(D,{%s:%s});\n" % (name, open(path, encoding="utf-8").read().strip())
src = src[:idx] + inject + src[idx:]

# ----------------------------------------------------------------- 5) renderer
tail = "\n</script></body></html>"
assert src.endswith(tail), "ekor index.html tidak seperti yang diharapkan"
body = "".join(b["jsbeg"] + open(b["js"], encoding="utf-8").read() + b["jsend"] for b in BLOCKS)
src = src[:-len(tail)] + body + tail

open("index.html", "w", encoding="utf-8").write(src)
print("tab terpasang; ukuran index.html: %.0f KB" % (len(src) / 1024))
