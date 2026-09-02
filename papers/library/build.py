"""Bangun papers/library/library.json — katalog naskah PhD + isi naskah siap baca.

Sumber:
  papers/paper1_equity_perception.md
  papers/paper2_national_siting_condition.md
  ASEAN_EV_Comparative_Paper.docx
  papers/capacity/CIRED2027_capacity_maps_equity.docx

Setiap blok teks diberi indeks stabil (data-b) supaya komentar pembimbing
bisa ditambatkan ke paragraf tertentu dan tetap menempel antar-kunjungan.

Jalankan dari akar repositori:  python3 papers/library/build.py
"""
import json, os, re, html, zipfile
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


# ----------------------------------------------------------------- markdown
def inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    s = re.sub(r"\[VERIFY([^\]]*)\]", r'<span class="verify">[VERIFY\1]</span>', s)
    return s


def md_to_html(text):
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("|") and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
            head = [c.strip() for c in ln.strip("|").split("|")]
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append('<div class="tw"><table><thead><tr>' +
                       "".join(f"<th>{inline(h)}</th>" for h in head) + "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) +
                       "</tbody></table></div>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            lv = min(len(m.group(1)) + 1, 6)
            out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>")
            i += 1
            continue
        if ln.strip() in ("---", "***", "___"):
            out.append("<hr>")
            i += 1
            continue
        if ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").rstrip())
                i += 1
            out.append("<blockquote>" + inline(" ".join(buf)) + "</blockquote>")
            continue
        if re.match(r"^\s*([-*+]|\d+\.)\s+", ln):
            ordered = bool(re.match(r"^\s*\d+\.", ln))
            items = []
            while i < len(lines) and re.match(r"^\s*([-*+]|\d+\.)\s+", lines[i] or ""):
                cur = re.sub(r"^\s*([-*+]|\d+\.)\s+", "", lines[i].rstrip())
                i += 1
                while i < len(lines) and lines[i].startswith("    ") and \
                        not re.match(r"^\s*([-*+]|\d+\.)\s+", lines[i]):
                    cur += " " + lines[i].strip()
                    i += 1
                items.append(cur)
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|\||>|\s*([-*+]|\d+\.)\s)", lines[i]) \
                and lines[i].strip() not in ("---", "***", "___"):
            buf.append(lines[i].strip())
            i += 1
        if buf:
            out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n".join(out)


# --------------------------------------------------------------------- docx
def docx_to_html(path):
    z = zipfile.ZipFile(path)
    rels = {e.get("Id"): e.get("Target") for e in ET.fromstring(z.read("word/_rels/document.xml.rels"))}
    body = ET.fromstring(z.read("word/document.xml")).find(W + "body")

    def txt(p):
        o = []
        for n in p.iter():
            t = n.tag.split("}")[1]
            if t == "t":
                o.append(n.text or "")
            elif t == "tab":
                o.append(" ")
            elif t == "br":
                o.append(" ")
            elif t == "blip":
                o.append("\x00" + (rels.get(n.get(R + "embed")) or ""))
        return "".join(o)

    out, imgs = [], []
    for ch in body:
        tag = ch.tag.split("}")[1]
        if tag == "p":
            s = txt(ch)
            if "\x00" in s:
                for part in s.split("\x00")[1:]:
                    imgs.append(part)
                    out.append(f'<p class="imgph">[gambar: {html.escape(os.path.basename(part))}]</p>')
                s = s.split("\x00")[0]
            if not s.strip():
                continue
            st = ch.find(W + "pPr/" + W + "pStyle")
            style = st.get(W + "val") if st is not None else ""
            up = s.strip()
            if not out and up.isupper():
                out.append(f"<h2>{html.escape(up.title())}</h2>")
            elif re.match(r"^\d+(\.\d+)?\.?\s+[A-Z]", up) and len(up) < 90:
                lv = 4 if re.match(r"^\d+\.\d+", up) else 3
                out.append(f"<h{lv}>{html.escape(up)}</h{lv}>")
            elif up.isupper() and len(up) < 90:
                out.append(f"<h3>{html.escape(up.title())}</h3>")
            elif style.lower().startswith("heading"):
                out.append(f"<h4>{html.escape(up)}</h4>")
            elif re.match(r"^(Fig\.|Table)\s", up):
                out.append(f'<p class="figcap">{html.escape(up)}</p>')
            elif re.match(r"^\[\d+\]", up):
                out.append(f'<p class="ref">{html.escape(up)}</p>')
            else:
                out.append(f"<p>{html.escape(up)}</p>")
        elif tag == "tbl":
            rows = []
            for tr in ch.findall(W + "tr"):
                rows.append([" ".join(txt(p) for p in tc.findall(W + "p")).strip()
                             for tc in tr.findall(W + "tc")])
            if not rows:
                continue
            if len(rows) == 1:   # baris tunggal (mis. blok penulis) -> paragraf biasa
                out.append('<p class="authors">' +
                           " · ".join(html.escape(c) for c in rows[0] if c.strip()) + "</p>")
                continue
            out.append('<div class="tw"><table><thead><tr>' +
                       "".join(f"<th>{html.escape(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in r) + "</tr>"
                               for r in rows[1:]) + "</tbody></table></div>")
    z.close()
    return "\n".join(out)


# ------------------------------------------------------- penomoran blok + daftar isi
def next_b(n):
    n[0] += 1
    return n[0]


def number_blocks(h):
    """Beri indeks berurutan pada tiap blok supaya komentar bisa ditambatkan ke blok tertentu."""
    n = [0]
    h = re.sub(r"<(h[2-6]|p|ul|ol|blockquote|hr)(?=[ >])",
               lambda m: f'<{m.group(1)} data-b="{next_b(n)}"', h)
    parts = h.split('<div class="tw">')
    h = parts[0] + "".join(f'<div class="tw" data-b="{next_b(n)}">' + q for q in parts[1:])
    return h


def toc_of(h):
    return [dict(b=int(m.group(2)), lv=int(m.group(1)[1]), t=re.sub(r"<[^>]+>", "", m.group(3)).strip())
            for m in re.finditer(r'<(h[3-4]) data-b="(\d+)">(.*?)</h[3-4]>', h, re.S)]


def words(h):
    return len(re.sub(r"<[^>]+>", " ", h).split())


# ------------------------------------------------------------------ katalog
def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


PAPERS = [
    dict(
        id="equity", n=1,
        title="Who is left behind? Spatial equity and public perception of public EV charging infrastructure in a developing-country megaregion",
        short="Spatial equity & public perception (Jawa Barat)",
        kind="Journal article", venue="Energy Research & Social Science (Q1)",
        alt="Energy Policy · Journal of Transport Geography",
        status="draft", stage="Draft lengkap — angka perlu verifikasi ulang", pct=55,
        target="Q4 2026", lead="Qashtalani Haramaini",
        data=["Master SPKLU (636 unit / 348 situs)", "101.020 transaksi Maret 2026",
              "Korpus ulasan ABSA (894 lokasi)", "BPS: populasi, IPM, kemiskinan"],
        method=["Lorenz & Gini (unit vs populasi, kWh vs populasi)", "Equity Priority Index",
                "Kontras kota vs kabupaten", "Model pendorong Service Quality Index"],
        tabs=["equity", "perception", "socio"],
        html=md_to_html(rd("papers/paper1_equity_perception.md")),
        files=[["Naskah (.md)", "papers/paper1_equity_perception.md"]],
        todo=["Ganti seluruh penanda [VERIFY] dengan sitasi nyata",
              "Verifikasi ulang Gini 0,19 / 0,45 terhadap tabel sumber",
              "Tambahkan aksesibilitas 2SFCA sebagai uji ketahanan",
              "Pernyataan ketersediaan data + izin penggunaan data PLN"],
    ),
    dict(
        id="siting", n=2,
        title="From coverage to capability: data-driven siting and a utilisation–availability diagnosis of a rapidly scaling national EV-charging network",
        short="Dari cakupan ke kapabilitas — siting nasional",
        kind="Journal article", venue="Sustainable Cities and Society (Q1)",
        alt="Applied Energy · eTransportation · CEUS",
        status="draft", stage="Draft lengkap — model siting perlu validasi akhir", pct=50,
        target="Q1 2027", lead="Qashtalani Haramaini",
        data=["Master SPKLU nasional (±3.200 situs)", "Deret konsumsi bulanan Jan 2024–Jun 2026",
              "101.020 transaksi Jawa Barat", "56.740 transaksi Jakarta Raya"],
        method=["Analisis pertumbuhan & konsentrasi", "Diagnosis status operasional (availability)",
                "Klasifikasi utilisasi menurut jenis lokasi", "MCDA + catchment + payback"],
        tabs=["national", "locint", "sector", "jraya"],
        html=md_to_html(rd("papers/paper2_national_siting_condition.md")),
        files=[["Naskah (.md)", "papers/paper2_national_siting_condition.md"]],
        todo=["Sitasi nyata untuk seluruh [VERIFY]",
              "Ungkap metode estimasi provinsi dari koordinat secara eksplisit",
              "Validasi model MCDA terhadap utilisasi teramati",
              "Perjelas kehati-hatian tafsir status 'offline' (snapshot vs downtime)"],
    ),
    dict(
        id="asean", n=3,
        title="Comparative analysis of electric vehicle markets, charging tariffs, and charge-point-operator business models in ASEAN",
        short="Perbandingan pasar & tarif CPO ASEAN",
        kind="Working paper", venue="Working paper → jurnal kebijakan energi",
        alt="Energy Policy · Energy Strategy Reviews",
        status="review", stage="Naskah utuh — siap dibaca pembimbing", pct=75,
        target="Q4 2026", lead="Qashtalani Haramaini",
        data=["Regulator & utilitas 6 negara ASEAN", "Rate card operator (V-Green, PEA Volta, Gentari, dll.)",
              "Riset sekunder: Maybank, Ember, ICCT, USGS"],
        method=["Riset meja komparatif 2025–2026", "Tipologi lima arketipe struktur pasar",
                "Normalisasi tarif ke USD/kWh", "Analisis unit economics CPO"],
        tabs=["asean"],
        html=docx_to_html(os.path.join(ROOT, "ASEAN_EV_Comparative_Paper.docx")),
        files=[["Naskah (.docx)", "ASEAN_EV_Comparative_Paper.docx"]],
        todo=["Kunci tanggal akses tiap sumber tarif",
              "Tegaskan bahwa jumlah charger antar-negara tidak sebanding satuannya",
              "Pilih jurnal sasaran dan sesuaikan format"],
    ),
    dict(
        id="cired2027", n=4,
        title="Capacity maps as an equity instrument: publishing charging demand and network headroom as open data in a vertically integrated DSO",
        short="Peta kapasitas sebagai instrumen keadilan (CIRED 2027)",
        kind="Conference full paper", venue="CIRED 2027",
        alt="—", status="review", stage="Draft full paper — siap ditinjau pembimbing", pct=80,
        target="CIRED 2027 (batas abstrak: cek panggilan makalah)",
        lead="Qashtalani Haramaini, Alyas Widita, Liz Taylor",
        data=["53.797 survei beban trafo distribusi (41.129 layak)", "182 trafo Gardu Induk / 9.790 MVA",
              "101.020 sesi pengisian / 636 charger / 331 situs", "3.687 pelanggan EV tergeokode"],
        method=["Headroom dua tingkat pada batas 80 %", "Koreksi pertumbuhan beban ke Maret 2026",
                "Agregasi sel 5 km + klasifikasi permintaan × headroom",
                "Tiga aturan penempatan tandingan 50 situs", "Audit kesiapan publikasi data"],
        tabs=["capacity", "jaringan"],
        html=docx_to_html(os.path.join(ROOT, "papers/capacity/CIRED2027_capacity_maps_equity.docx")),
        files=[["Naskah (.docx)", "papers/capacity/CIRED2027_capacity_maps_equity.docx"],
               ["Payload peta (.json)", "papers/capacity/capacity.json"],
               ["Pipeline analisis (.py)", "papers/capacity/prepare.py"]],
        todo=["Tambahkan tingkat penyulang (2.574 penyulang, Apr 2022) ke analisis",
              "Rincikan definisi Gini yang dipakai (hitung ulang berbeda dari naskah)",
              "Sebutkan sumber umur survei Gardu Induk atau nyatakan asumsinya",
              "Format ulang ke templat CIRED (4–6 halaman) sebelum unggah"],
    ),
]

PLAN = [
    ["2026 Q3", "CIRED 2027 full paper", "Draft selesai · tinjauan pembimbing", "cired2027"],
    ["2026 Q4", "Paper 1 — Spatial equity & perception", "Verifikasi angka · sitasi · submit ERSS", "equity"],
    ["2026 Q4", "ASEAN working paper", "Finalisasi & pilih jurnal sasaran", "asean"],
    ["2027 Q1", "Paper 2 — Coverage to capability", "Validasi model siting · submit SCS", "siting"],
    ["2027 Q2", "CIRED 2027 — presentasi", "Perbaikan pasca-tinjauan", "cired2027"],
]

for p in PAPERS:
    p["html"] = number_blocks(p["html"])
    p["toc"] = toc_of(p["html"])
    p["words"] = words(p["html"])

out = dict(papers=PAPERS, plan=PLAN)
s = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
open(os.path.join(ROOT, "papers/library/library.json"), "w", encoding="utf-8").write(s)
for p in PAPERS:
    print(f'  [{p["id"]:9s}] {p["words"]:5d} kata · {len(p["toc"]):2d} judul · {p["pct"]}%')
print(f"library.json ditulis: {len(s)/1024:.0f} KB")
