"""Sisipkan tab '⚡ EV × Jaringan' (markup + payload + renderer) ke index.html."""
import json

src = open("index.html", encoding="utf-8").read()
if "p-jaringan" in src:
    raise SystemExit("Tab sudah ada di index.html — jalankan `git checkout index.html` lebih dulu.")

def once(hay, needle):
    assert hay.count(needle) == 1, "anchor tidak unik/tidak ditemukan: " + needle[:60]

# 1) daftar tab
tab = '["pelanggan","🏠 Pelanggan EV"]'
once(src, tab); src = src.replace(tab, tab + ',["jaringan","⚡ EV × Jaringan"]', 1)

# 2) inisialisasi peta saat tab dibuka
hook = "if(tb.dataset.p==='pelanggan'&&window.initPel)setTimeout(window.initPel,80);"
once(src, hook)
src = src.replace(hook, hook + "\n if(tb.dataset.p==='jaringan'&&window.initGx)setTimeout(window.initGx,80);", 1)

# 3) markup halaman
anchor = "<!-- GEOSPKLU (self-contained ArcGIS app"
once(src, anchor)
src = src.replace(anchor, open("analysis/page.html", encoding="utf-8").read() + "\n" + anchor, 1)

# 4) payload data
marker = "const fmt=n=>n==null?'–':Math.round(n).toLocaleString('en-US');"
once(src, marker)
blob = "Object.assign(D,{grid:" + json.dumps(json.load(open("analysis/grid.json")),
                                             separators=(",", ":"), ensure_ascii=False) + "});\n"
src = src.replace(marker, blob + marker, 1)

# 5) renderer
tail = "\n</script></body></html>"
assert src.endswith(tail)
src = src[:-len(tail)] + open("analysis/render.js", encoding="utf-8").read() + tail

open("index.html", "w", encoding="utf-8").write(src)
print("tab tersisip; ukuran index.html:", len(src))
