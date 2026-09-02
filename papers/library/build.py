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
            elif re.match(r"^(Summary of Research|Methodology|Methods?|Results( and Findings)?|Conclusions?|"
                          r"Discussion|Abstract|References|Acknowledgements?|Limitations)\s*$", up):
                out.append(f"<h3>{html.escape(up)}</h3>")
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


CATEGORIES = {
    "akses":   ["Akses & keadilan infrastruktur pengisian", "#3a6ea5"],
    "jaringan":["Jaringan distribusi & perencanaan", "#2e9e5b"],
    "emisi":   ["Emisi & dekarbonisasi", "#d6443c"],
    "bisnis":  ["Model bisnis, pasar & kebijakan", "#e0a52b"],
}


def abstract_of(html):
    """Ambil paragraf abstrak apa adanya dari HTML naskah (sampai heading berikutnya)."""
    m = re.search(r"<h[2-6][^>]*>\s*(Abstract|Structured abstract[^<]*|Summary of Research)\s*</h[2-6]>(.*?)(?=<h[2-6]|$)",
                  html, re.S | re.I)
    if not m:
        return ""
    paras = re.findall(r"<p[^>]*>(.*?)</p>", m.group(2), re.S)
    txt = " ".join(re.sub(r"<[^>]+>", "", x).strip() for x in paras if x.strip())
    return re.sub(r"\s+", " ", txt).strip()


FILES = "papers/library/files/"
PAPERS = [
    dict(
        id="equity", n=1, category="akses", tags=["akses"],
        title="Who is left behind? Spatial equity and public perception of public EV charging infrastructure in a developing-country megaregion",
        short="Spatial equity & public perception (Jawa Barat)",
        kind="Journal article", venue="Energy Research & Social Science (Q1)",
        alt="Energy Policy · Journal of Transport Geography", venue_src="dinyatakan di naskah",
        status="draft", stage="Draft lengkap — angka perlu verifikasi ulang", pct=55,
        target="Q4 2026", lead="Qashtalani Haramaini",
        goal="Mengukur seberapa tidak merata sebaran unit dan konsumsi SPKLU di Jawa Barat, dan menguji apakah ketimpangan distributif itu berhimpit dengan kualitas layanan yang dirasakan pengguna.",
        finding="Gini unit-vs-populasi ≈0,19 tetapi konsumsi-vs-populasi ≈0,45; reliabilitas dan ketersediaan mendominasi persepsi; wilayah kurang terlayani berpendapatan rendah juga bernilai SQI terendah — ketimpangan saling menguatkan.",
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
        id="siting", n=2, category="akses", tags=["akses", "bisnis"],
        title="From coverage to capability: data-driven siting and a utilisation–availability diagnosis of a rapidly scaling national EV-charging network",
        short="Dari cakupan ke kapabilitas — siting nasional",
        kind="Journal article", venue="Sustainable Cities and Society (Q1)",
        alt="Applied Energy · eTransportation · CEUS", venue_src="dinyatakan di naskah",
        status="draft", stage="Draft lengkap — model siting perlu validasi akhir", pct=50,
        target="Q1 2027", lead="Qashtalani Haramaini",
        goal="Mengganti tolok ukur 'cakupan' dengan 'kapabilitas' — tersedia, terutilisasi, sesuai permintaan — untuk jaringan SPKLU nasional, dan memvalidasi kerangka siting berbasis transaksi.",
        finding="Energi nasional naik ≈5× dalam setahun; ≈32 % stasiun berstatus offline; rest area tol menjual ≈3,5× energi per situs dibanding kantor PLN dan ≈13× hotel; model MCDA + catchment + payback mereproduksi urutan itu.",
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
        id="asean", n=3, category="bisnis", tags=["bisnis"],
        title="Comparative analysis of electric vehicle markets, charging tariffs, and charge-point-operator business models in ASEAN",
        short="Perbandingan pasar & tarif CPO ASEAN",
        kind="Working paper", venue="Working paper → jurnal kebijakan energi",
        alt="Energy Policy · Energy Strategy Reviews", venue_src="belum ditetapkan",
        status="review", stage="Naskah utuh — siap dibaca pembimbing", pct=75,
        target="Q4 2026", lead="Qashtalani Haramaini",
        goal="Membandingkan adopsi EV, tarif pengisian, ekonomi CPO, dan struktur pasar enam negara ASEAN, lalu memposisikan Indonesia di dalamnya.",
        finding="Harga DC fast charging berbeda 5× antar-negara; lima arketipe struktur pasar; tidak ada satu negara yang unggul di semua segmen investasi; Indonesia punya pipeline terbesar tetapi unit economics CPO swasta tertekan tarif regulasi dan geografi.",
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
        id="cired2027", n=4, category="jaringan", tags=["jaringan", "akses"],
        title="Capacity maps as an equity instrument: publishing charging demand and network headroom as open data in a vertically integrated DSO",
        short="Peta kapasitas sebagai instrumen keadilan (CIRED 2027)",
        kind="Conference full paper", venue="CIRED 2027",
        alt="—", venue_src="dinyatakan di naskah",
        status="review", stage="Draft full paper — siap ditinjau pembimbing", pct=80,
        target="CIRED 2027 (batas abstrak: cek panggilan makalah)",
        lead="Qashtalani Haramaini, Alyas Widita, Liz Taylor",
        goal="Menunjukkan bahwa peta hosting-capacity bukan informasi netral melainkan instrumen alokasi: lapisan yang dipublikasikan DSO menentukan di mana charger dibangun dan siapa yang terlayani.",
        finding="Roll-out mengikuti kepadatan jaringan, bukan sisa kapasitas; sel permintaan-tinggi/headroom-rendah memuat 12,8 % pemilik tetapi 7,2 % charger; aturan demand-within-headroom menjangkau 12 % pemilik lebih banyak tanpa situs terlantar; dua tingkat jaringan berlawanan di 51 % sel.",
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
              "Format ulang ke templat CIRED (4–6 halaman) sebelum unggah"],
    ),
    dict(
        id="dndp", n=5, category="jaringan", tags=["jaringan"],
        title="From energy forecast to network load: a demand modelling methodology for EV charging in distribution network development planning",
        short="Dari prakiraan energi ke beban jaringan (DNDP)",
        kind="Conference full paper",
        venue="CIRED 2027 — Session 5, Planning of Power Distribution Systems (Demand and Generation Forecast)",
        alt="IEEE PES ISGT Asia · CIGRE", venue_src="dinyatakan di naskah",
        status="review", stage="Full paper — hasil lengkap, siap ditinjau", pct=75,
        target="CIRED 2027", lead="Qashtalani Haramaini",
        goal="Menyediakan lapisan penerjemah yang hilang antara prakiraan energi SPKLU (kWh/bulan) dan satuan rencana pengembangan jaringan distribusi (kW pada trafo tertentu, pada jam puncak).",
        finding="Fast charging publik bukan beban off-peak (88–91 % dari maksimum harian bertahan di 18:00–22:00); hubungan energi→puncak sub-linear P = 0,133·E^0,695 sehingga aturan nameplate×koinsidensi melebih-lebihkan 74 % situs; 41.128 trafo bisa menampung 452 GWh/bulan (≈20× kebutuhan 2030) tetapi 49 % trafo yang kini menampung charging akan melebihi 100 % bila roll-out mengikuti permintaan — masalahnya alokasi, bukan kapasitas.",
        data=["101.020 sesi pengisian bermeter dari 328 stasiun publik", "Pembebanan terukur 41.128 trafo distribusi Jawa Barat",
              "Lintasan wajib cakupan SPKLU 2025–2030 (Kepmen ESDM 24.K/2025)"],
        method=["Rekonstruksi kurva beban pengisian resolusi 15 menit", "Fungsi transfer energi→puncak (regresi pangkat)",
                "Analisis koinsidensi & diversitas antar-situs", "Headroom jaringan dihargai dalam kWh/bulan",
                "Alokasi spasial lintasan 2030 (demand-led vs coverage-led) pada sel 2 km"],
        tabs=["jaringan", "capacity"],
        html=docx_to_html(os.path.join(ROOT, FILES + "Energy_Forecast_to_Network_Load_DNDP.docx")),
        files=[["Naskah (.docx)", FILES + "Energy_Forecast_to_Network_Load_DNDP.docx"]],
        todo=["Cek konsistensi jumlah stasiun (328) dan trafo (41.128) dengan naskah CIRED lain (331 / 41.129)",
              "Format ke templat CIRED Session 5", "Uji ketahanan fungsi transfer pada subset AC-only vs DC"],
    ),
    dict(
        id="tailpipe", n=6, category="emisi", tags=["emisi", "akses"],
        title="Tailpipe to smokestack: marginal emission factors and the illusion of zero-emission mobility on a coal-dominated grid",
        short="Faktor emisi marjinal & ilusi mobilitas nol-emisi",
        kind="Journal article", venue="Usulan: Transportation Research Part D · Applied Energy",
        alt="Energy Policy · Environmental Research Letters", venue_src="usulan — belum dinyatakan di naskah",
        status="review", stage="Full paper — hasil & metrik baru lengkap", pct=70,
        target="Q1 2027", lead="Qashtalani Haramaini",
        goal="Menguji klaim 'nol emisi' EV pada sistem tenaga kepulauan yang didominasi batu bara dengan memperhitungkan dua ekor distribusi yang dihapus akuntansi konvensional: ekor merit-order (pasokan marjinal) dan ekor infrastruktur (utilisasi charger yang timpang).",
        finding="Energi per stasiun sangat timpang (Gini 0,769; separuh stasiun terendah hanya 2,6 % energi); karbon infrastruktur teramortisasi 4–749 g CO₂/kWh; BEV yang mengisi di stasiun persentil-90 memancarkan 281–318 g CO₂/km, 1,56–1,76× mobil konvensional; metrik baru A* (utilisasi impas karbon) tak terdefinisi di Sulawesi & Maluku; kedua ekor berhimpit secara spasial sehingga pemerataan dan minimisasi karbon saat ini berkonflik.",
        data=["528 unit pembangkit tergeoreferensi (87,4 GW), 8 sistem interkoneksi", "3.201 SPKLU tergeoreferensi (4.997 charger, 121,6 MW)",
              "101.020 sesi pengisian bermeter"],
        method=["Penetapan sistem & pita faktor emisi marjinal (mid-merit vs peaking)", "Distribusi empiris utilisasi stasiun → karbon infrastruktur teramortisasi",
                "Metrik carbon-breakeven utilisation A* dan Compound Tail Index", "Transfer bentuk distribusi ke sistem tanpa metering"],
        tabs=["jaringan", "national"],
        html=docx_to_html(os.path.join(ROOT, FILES + "Tailpipe_to_Smokestack_Marginal_Emission_Factors.docx")),
        files=[["Naskah (.docx)", FILES + "Tailpipe_to_Smokestack_Marginal_Emission_Factors.docx"]],
        todo=["Tetapkan jurnal sasaran (usulan TR Part D / Applied Energy) dan sesuaikan format",
              "Kalibrasi faktor emisi berbasis kapasitas terhadap faktor sistem resmi bila tersedia",
              "Sinkronkan inventaris pembangkit (528 unit / 87,4 GW) dengan naskah CBAM (526 / 95,4 GW)"],
    ),
    dict(
        id="cbam", n=7, category="emisi", tags=["emisi", "bisnis"],
        title="Captive generation and the verification-incentive inversion: spatially differentiated grid emission factors and CBAM exposure of Indonesia's export industry",
        short="Pembangkit captive & inversi insentif verifikasi CBAM",
        kind="Journal article", venue="Usulan: Energy Policy · Energy Economics",
        alt="Climate Policy · Journal of Cleaner Production", venue_src="usulan — belum dinyatakan di naskah",
        status="review", stage="Full paper — hasil & implikasi kebijakan lengkap", pct=70,
        target="Q1 2027", lead="Qashtalani Haramaini",
        goal="Menunjukkan bahwa pilihan biner CBAM (nilai default nasional vs nilai terverifikasi per instalasi) membalik insentif yang ingin diciptakannya bila intensitas karbon nasional bersifat bimodal secara spasial — dengan menghitung faktor emisi zonal yang memasukkan pembangkit captive.",
        finding="Unit captive memegang 17,7 % kapasitas tetapi 27,6 % CO₂ pembangkitan; memasukkannya menaikkan faktor Sulawesi 38 %, Papua 40 %, Maluku 27 %; faktor provinsi berbeda 3,1×; beban CBAM aluminium berbeda EUR 324/ton antar-zona; produsen di 5 dari 8 zona (seluruh sabuk nikel) justru rugi bila memverifikasi.",
        data=["526 unit pembangkit tergeoreferensi (95,4 GW) di 8 sistem", "933 gardu induk transmisi",
              "Registri pembangkit captive yang dapat diaudit", "Regulasi CBAM (EU 2023/956, 2025/2547, 2025/2621)"],
        method=["Klasifikasi grid-connected vs captive", "Estimator faktor emisi zonal dengan propagasi ketidakpastian Monte Carlo",
                "Perhitungan paparan CBAM & insentif verifikasi per zona pada EUR 75,36/tCO₂"],
        tabs=["jaringan"],
        html=docx_to_html(os.path.join(ROOT, FILES + "Captive_Generation_CBAM_Exposure.docx")),
        files=[["Naskah (.docx)", FILES + "Captive_Generation_CBAM_Exposure.docx"]],
        todo=["Tetapkan jurnal sasaran (usulan Energy Policy / Energy Economics)",
              "Kalibrasi estimator zonal terhadap faktor sistem yang dipublikasikan resmi",
              "Uji apakah inversi juga muncul di negara ASEAN lain dengan captive power besar"],
    ),
    dict(
        id="swap", n=8, category="bisnis", tags=["bisnis"],
        title="The balance sheet problem: why battery-swapping networks migrate to public ownership",
        short="Mengapa jaringan tukar baterai bermigrasi ke kepemilikan publik",
        kind="Conference paper (abstrak diperluas)",
        venue="IAEE International Conference 2027 — kode spesialisasi 10.3 Transportation: EV & systems",
        alt="Energy Policy · Energy Research & Social Science", venue_src="format & kode IAEE dinyatakan di naskah",
        status="draft", stage="Abstrak diperluas — hasil awal, solusi fsQCA penuh belum", pct=35,
        target="IAEE 2027 (abstrak) → full paper", lead="Qashtalani Haramaini",
        goal="Menjelaskan mengapa jaringan tukar baterai yang secara teknis serupa bisa gagal (Better Place, Ample) atau berhasil (Gogoro, NIO), dengan berargumen bahwa pembedanya adalah siapa yang memikul inventaris baterai di neraca, bukan teknologi.",
        finding="Throughput memisahkan jaringan yang bertahan menurut segmen kendaraan (roda dua ≈3,7× per stasiun dibanding roda empat); jaringan terbesar tidak menyelesaikan masalah modal secara komersial melainkan memindahkannya ke neraca publik/BUMN; setiap swap mobil penumpang multi-pabrikan di pasar dengan home charging melimpah gagal; Indonesia memenuhi hampir semua syarat kecuali standar interoperabilitas pak yang mengikat.",
        data=["16–20 kasus nasional termasuk kegagalan historis (Israel, Denmark, AS)", "Statistik publik 8 kondisi terkalibrasi",
              "Pengungkapan perusahaan NIO & Gogoro 2026"],
        method=["Fuzzy-set Qualitative Comparative Analysis (fsQCA) — kondisi perlu vs cukup",
                "Model impas per stasiun N* = (C·CRF + O + B·δ)/(p − c·e) dengan biaya pikul inventaris baterai B·δ"],
        tabs=["asean"],
        html=docx_to_html(os.path.join(ROOT, FILES + "Balance_Sheet_Problem_Battery_Swapping.docx")),
        files=[["Naskah (.docx)", FILES + "Balance_Sheet_Problem_Battery_Swapping.docx"]],
        todo=["Lengkapi kalibrasi 8 kondisi untuk seluruh 16–20 kasus dan jalankan solusi fsQCA penuh",
              "Isi alamat surel penulis (masih [insert email])", "Kembangkan menjadi full paper pasca-IAEE"],
    ),
]

PLAN = [
    ["2026 Q3", "CIRED 2027 — Capacity maps (full paper)", "Draft selesai · tinjauan pembimbing", "cired2027"],
    ["2026 Q3", "CIRED 2027 — Energy forecast → network load (Session 5)", "Full paper · tinjauan pembimbing", "dndp"],
    ["2026 Q4", "Paper 1 — Spatial equity & perception", "Verifikasi angka · sitasi · submit ERSS", "equity"],
    ["2026 Q4", "ASEAN working paper", "Finalisasi & pilih jurnal sasaran", "asean"],
    ["2026 Q4", "IAEE 2027 — Balance sheet problem (abstrak)", "Kalibrasi fsQCA · submit abstrak", "swap"],
    ["2027 Q1", "Tailpipe to smokestack", "Tetapkan jurnal · submit", "tailpipe"],
    ["2027 Q1", "Captive generation & CBAM", "Tetapkan jurnal · submit", "cbam"],
    ["2027 Q1", "Paper 2 — Coverage to capability", "Validasi model siting · submit SCS", "siting"],
    ["2027 Q2", "CIRED 2027 — presentasi (2 makalah)", "Perbaikan pasca-tinjauan", "cired2027"],
]

for p in PAPERS:
    p["html"] = number_blocks(p["html"])
    p["toc"] = toc_of(p["html"])
    p["words"] = words(p["html"])
    p["abstract"] = p.get("abstract") or abstract_of(p["html"])
    assert p["abstract"], "abstrak tidak ditemukan: " + p["id"]

out = dict(papers=PAPERS, plan=PLAN, categories=CATEGORIES)
s = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
open(os.path.join(ROOT, "papers/library/library.json"), "w", encoding="utf-8").write(s)
for p in PAPERS:
    print(f'  [{p["id"]:9s}] {p["words"]:5d} kata · {len(p["toc"]):2d} judul · {p["pct"]:3d}% · '
          f'{CATEGORIES[p["category"]][0][:28]:28s} · abstrak {len(p["abstract"].split())} kata')
print(f"library.json ditulis: {len(s)/1024:.0f} KB")
