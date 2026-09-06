"""Sisipkan (atau perbarui) tab '⚡ EV × Jaringan' di index.html.

Idempoten: bila tab sudah ada, blok lama dicopot lebih dulu lalu dipasang ulang,
sehingga skrip ini aman dijalankan berkali-kali tanpa `git checkout index.html`.
"""
import json, re

BEG = "<!-- GX:BEGIN -->"
END = "<!-- GX:END -->"
JS_BEG = "/* GX:BEGIN */"
JS_END = "/* GX:END */"
TAB = ',["jaringan","⚡ EV × Jaringan"]'
HOOK = "\n if(tb.dataset.p==='jaringan'&&window.initGx)setTimeout(window.initGx,80);"

src = open("index.html", encoding="utf-8").read()


def strip_previous(s):
    """Copot hasil injeksi sebelumnya, baik yang bertanda maupun versi awal tanpa tanda."""
    s = s.replace(TAB, "").replace(HOOK, "")

    # markup halaman
    if BEG in s and END in s:
        s = re.sub(re.escape(BEG) + r".*?" + re.escape(END) + r"\n?", "", s, flags=re.S)
    else:
        i = s.find('<div class="page" id="p-jaringan">')
        j = s.find("<!-- GEOSPKLU", i if i >= 0 else 0)
        if i >= 0 and j > i:
            s = s[:i] + s[j:]

    # payload data
    for key in ("grid", "grid2"):
        s = re.sub(r'Object\.assign\(D,\{' + key + r':.*?\}\);\n', "", s, count=1, flags=re.S)

    # renderer
    if JS_BEG in s and JS_END in s:
        s = re.sub(re.escape(JS_BEG) + r".*?" + re.escape(JS_END), "", s, flags=re.S)
    else:
        i = s.find("\n/* ============ EV × JARINGAN")
        if i >= 0:
            s = s[:i] + "\n</script></body></html>"
    return s


had_tab = "p-jaringan" in src
src = strip_previous(src)
assert "p-jaringan" not in src, "sisa injeksi lama masih tertinggal"
print("blok lama dicopot" if had_tab else "injeksi pertama")


def once(hay, needle):
    assert hay.count(needle) == 1, "anchor tidak unik/tidak ditemukan: " + needle[:60]


# 1) daftar tab
base = '["pelanggan","🏠 Pelanggan EV"]'
once(src, base); src = src.replace(base, base + TAB, 1)

# 2) inisialisasi peta saat tab dibuka
hook_anchor = "if(tb.dataset.p==='pelanggan'&&window.initPel)setTimeout(window.initPel,80);"
once(src, hook_anchor); src = src.replace(hook_anchor, hook_anchor + HOOK, 1)

# 3) markup halaman
anchor = "<!-- GEOSPKLU (self-contained ArcGIS app"
once(src, anchor)
page = BEG + "\n" + open("analysis/page.html", encoding="utf-8").read() + END + "\n"
src = src.replace(anchor, page + anchor, 1)

# 4) payload data
marker = "const fmt=n=>n==null?'–':Math.round(n).toLocaleString('en-US');"
once(src, marker)
blob = ""
for key, path in (("grid", "analysis/grid.json"), ("grid2", "analysis/grid2.json")):
    blob += ("Object.assign(D,{" + key + ":"
             + json.dumps(json.load(open(path)), separators=(",", ":"), ensure_ascii=False) + "});\n")
src = src.replace(marker, blob + marker, 1)

# 5) renderer
tail = "\n</script></body></html>"
assert src.endswith(tail)
src = (src[:-len(tail)] + JS_BEG
       + open("analysis/render.js", encoding="utf-8").read()
       + open("analysis/render2.js", encoding="utf-8").read()
       + JS_END + tail)

open("index.html", "w", encoding="utf-8").write(src)
print("tab terpasang; ukuran index.html:", len(src))
