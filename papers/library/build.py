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
def img_html(z, target, no, media):
    """Satu gambar tertanam: diekstrak bila media diminta, selain itu placeholder."""
    if not media:
        return f'<p class="imgph">[gambar: {html.escape(os.path.basename(target))}]</p>'
    dest, url = media
    ext = os.path.splitext(target)[1].lower() or ".png"
    name = f"fig{no}{ext}"
    d = os.path.join(ROOT, dest)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, name), "wb").write(z.read("word/" + target))
    return f'<p class="fig"><img src="{url}/{name}" alt="Gambar {no}" loading="lazy"></p>'


def docx_to_html(path, media=None):
    """Ubah .docx menjadi HTML siap baca.

    media=(dir_tujuan, prefiks_url) mengekstrak gambar tertanam ke berkas
    fig1.png, fig2.png, ... menurut urutan kemunculan dan menyisipkannya
    sebagai <img>. Tanpa media, gambar tetap menjadi placeholder teks.
    """
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
                    out.append(img_html(z, part, len(imgs), media))
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
            # keterangan gambar/tabel selalu "Fig. …", "Figure 1. …", "Table 2 – …";
            # prosa seperti "Figure 2(a) shows …" atau "Table 1 ranks …" bukan keterangan.
            elif re.match(r"^(Fig\.\s|(Figure|Table)\s+\d+\s*[.:\u2013\u2014-]\s)", up):
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
    paras = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<p[^>]*>(.*?)</p>", m.group(2), re.S)]
    # baris kata kunci mengekor abstrak di beberapa naskah — bukan bagian abstraknya
    txt = " ".join(x for x in paras if x and not re.match(r"^Keywords?\s*[:.]", x, re.I))
    return re.sub(r"\s+", " ", txt).strip()


FILES = "papers/library/files/"
MEDIA = "papers/library/media/"


def chapter_html(fname, slug):
    """Naskah bab CUPUM 2027.

    Ketiganya berbagi bentuk kepala yang sama — baris 1 seri buku, baris 2 judul,
    baris 3–5 penulis — yang keluar dari docx_to_html sebagai <p> biasa. Di sini
    kepala itu dijadikan judul + blok penulis, dan keempat gambarnya diekstrak.
    """
    h = docx_to_html(os.path.join(ROOT, FILES + fname),
                     media=(MEDIA + slug, MEDIA + slug))
    head = re.findall(r"<p>(.*?)</p>", h, re.S)[:5]
    assert len(head) == 5 and head[0].startswith("CUPUM"), "kepala naskah tak seperti dugaan: " + fname
    for blk in head:
        h = h.replace(f"<p>{blk}</p>\n", "", 1)
    series, title, *authors = head
    return (f"<h2>{title}</h2>\n"
            f'<p class="authors">{" · ".join(authors)}</p>\n'
            f'<blockquote>{series}</blockquote>\n') + h


# Isi poster ditulis ulang dari poster yang dirender (teks PDF-nya berkolom dan
# ber-tracking lebar, sehingga ekstraksi otomatis tidak terbaca andal). Gambar
# poster asli disertakan supaya pembaca selalu bisa memeriksa sumbernya.
POSTER_HTML = """
<h2>Bayesian models for spatial equity: separating latent demand from supply in EV charging infrastructure</h2>
<p class="authors">Qashtalani Haramaini · PhD candidate · Monash University Indonesia · RACE for 2030 ·
Bayesian Analysis &amp; Modelling Workshop 2026, PhD Poster Prize · Monash Caulfield, 18–19 November 2026</p>

<blockquote>Demand that has never been built for is never observed. This study proposes a hierarchical framework
that separates latent charging demand from the supply filter through which it is recorded — and propagates that
uncertainty into the siting decision itself.</blockquote>

<p class="imgph"><img src="papers/library/files/poster_bayesian_2026.png"
 alt="Poster Bayesian models for spatial equity" style="width:100%;border-radius:8px;border:1px solid #e6e9f0"></p>
<p class="figcap">Poster utuh. Unduh versi PDF lewat tombol di atas untuk membacanya pada ukuran penuh.</p>

<h3>Argumen dalam satu baris</h3>
<div class="tw"><table><thead><tr>
<th>Yang tercatat</th><th>Yang dimodelkan</th><th>Yang dipulihkan</th><th>Yang diputuskan</th></tr></thead>
<tbody><tr>
<td>Sesi <i>y</i> — cacahan yang <i>under-detected</i>. Hanya permintaan yang bertemu charger menjadi data.</td>
<td>Capture <i>a</i> × demand <i>d</i>, dipisahkan oleh kovariat sisi pasokan yang hanya menggerakkan <i>a</i>.</td>
<td>Posterior untuk setiap wilayah — permintaan laten dengan ketidakpastian yang jujur, paling lebar di tempat rekaman paling tipis.</td>
<td><i>P</i>(permintaan tak terpenuhi &gt; τ) — situs diperingkat menurut peluang pembangunan layak.</td>
</tr></tbody></table></div>

<h3>1. Pengamatan bersyarat pada pasokan</h3>
<p>Infrastruktur pengisian ditempatkan di tempat utilisasi sudah tinggi, sehingga bukti yang dipakai perencana
adalah sampel yang diseleksi oleh keputusan yang hendak diinformasikannya. Hasilnya memperkuat diri sendiri:
kapasitas mengalir ke daerah yang sudah punya, permintaan laten di tempat lain tetap tak terlihat karena tidak
pernah menjadi sesi, dan keadilan lalu dinilai di atas rekaman yang sama — yang membuat permintaan tampak jauh
lebih terkonsentrasi daripada sebenarnya.</p>

<h3>2. Mengapa masalah ini Bayesian, bukan sekadar difit</h3>
<ul>
<li><b>Kelangkaan tidak punya jawaban maximum-likelihood.</b> Sebagian besar unit mencatat nol sesi karena memang
nol charger; laju tingkat-wilayah tak terdefinisi atau sangat tidak stabil. Prior hierarkis meminjam kekuatan dari
tetangga alih-alih membuang unitnya.</li>
<li><b>Struktur spasial adalah parameter, bukan gangguan.</b> Reparameterisasi BYM2 memisahkan heterogenitas
terstruktur dari tak terstruktur di bawah parameter pencampur ρ yang dapat ditafsirkan.</li>
<li><b>Keputusan butuh probabilitas, bukan estimasi titik.</b> Komite penempatan seharusnya menanyakan
<i>P</i>(permintaan tak terpenuhi &gt; ambang kelayakan), yang dikembalikan posterior secara langsung.</li>
<li><b>Indeks ketimpangan adalah fungsional non-linear.</b> Gini dan Lorenz atas laju terestimasi tidak punya
galat baku analitik yang bersih; draw posterior meneruskan ketidakpastian menembusnya secara tepat.</li>
</ul>

<h3>3. Model: permintaan dan capture, diestimasi bersama</h3>
<p>Struktur imperfect-detection (N-mixture) kanonik: sesi teramati <i>y<sub>i</sub></i> adalah permintaan penduduk
laten <i>d<sub>i</sub></i> yang ditipiskan oleh probabilitas capture <i>a<sub>i</sub></i> ∈ (0,1), ditambah aliran
koridor <i>c<sub>i</sub></i> untuk lalu lintas lintas-wilayah.</p>
<ul>
<li><b>Observasi</b> — <i>y<sub>i</sub></i> ~ NegBin(μ<sub>i</sub>, φ), μ<sub>i</sub> = <i>d<sub>i</sub></i> ·
<i>a<sub>i</sub></i> + <i>c<sub>i</sub></i>; <i>c<sub>i</sub></i> hanya bukan-nol di wilayah berkoridor tol.</li>
<li><b>Permintaan laten</b> — log <i>d<sub>i</sub></i> = β₀ + x<sub>i</sub>ᵀβ + u<sub>i</sub> + v<sub>i</sub>
(armada EV terdaftar, instalasi pengisian rumah, populasi &amp; kepadatan aktivitas, pembangkitan perjalanan,
pendapatan, campuran POI).</li>
<li><b>Saringan capture</b> — logit <i>a<sub>i</sub></i> = γ₀ + z<sub>i</sub>ᵀγ: hanya sisi pasokan — jarak ke
gardu tegangan menengah dengan kapasitas cadangan, ketersediaan lahan, waktu tempuh penduduk ke charger terdekat,
topologi jaringan, bukan preferensi pengemudi.</li>
<li><b>Prior spasial BYM2</b> — u + v = τ<sup>−½</sup>(√ρ · u* + √(1−ρ) · v*), u* ~ ICAR(W), v* ~ N(0,1);
prior PC pada τ dan φ; ρ ~ Beta(½, ½).</li>
</ul>

<h3>4. Masalah identifikasi, dinyatakan terus terang</h3>
<p>Tidak ada dalam data yang membedakan <i>permintaan rendah, terlayani baik</i> dari <i>permintaan tinggi, nyaris
tak terlayani</i>: keduanya menghasilkan sedikit sesi. Memisahkan <i>d</i> dari <i>a</i> menuntut argumen, bukan
data lebih banyak. Argumennya adalah <b>exclusion restriction</b>: headroom jaringan dan ketersediaan lahan
menentukan di mana charger <i>secara fisik dapat dibangun</i>; keduanya tidak membawa informasi tentang apakah
pengemudi di wilayah itu <i>ingin</i> mengisi. Keduanya menggerakkan <i>a</i>, bukan <i>d</i>. Asumsi inilah mata
rantai terlemah dan diperlakukan sebagai demikian: analisis sensitivitas prior atas γ, kalibrasi berbasis simulasi
pada data sintetik dengan <i>d</i> diketahui, dan uji pemalsuan pada wilayah yang pasokannya meluas karena alasan
tak berkaitan dengan permintaan.</p>

<h3>5. Latar dan data — Jawa Barat</h3>
<p>Jawa Barat: 27 kota dan kabupaten, ±50 juta penduduk, front paling aktif dari roll-out pengisian publik
Indonesia. Rekaman Maret 2026 terurai menjadi <b>14 wilayah layanan operator</b> (41,1 juta penduduk, 633 unit
charger); analisis dilakukan pada tingkat wilayah layanan, dengan disagregasi lebih halus pada grid 1 km sebagai
tahap berikutnya.</p>
<div class="tw"><table><thead><tr><th>Lapisan</th><th>Sumber</th></tr></thead><tbody>
<tr><td>Lokasi charger, daya, operator, status</td><td>Registri stasiun induk, utilitas Jawa Barat, Mar 2026</td></tr>
<tr><td>Rincian transaksi: kWh, durasi, pendapatan</td><td>101.020 sesi, Mar 2026</td></tr>
<tr><td>Instalasi pengisian rumah pelanggan EV</td><td>Aplikasi pelanggan, Nov 2025 – Jun 2026</td></tr>
<tr><td>Persepsi kualitas layanan per stasiun</td><td>Sentimen berbasis ulasan, 584 stasiun (tahap berikutnya)</td></tr>
<tr><td>Jaringan jalan, titik minat, proksi perjalanan</td><td>OpenStreetMap</td></tr>
<tr><td>Populasi (Sensus 2022), IPM 2023, tingkat pendapatan</td><td>Badan statistik nasional</td></tr>
</tbody></table></div>
<p>Rekaman tingkat pelanggan diagregasi ke tingkat wilayah dan dianonimkan, dipakai di bawah perjanjian data
dengan utilitas; tidak ada pelanggan perorangan yang dapat diidentifikasi.</p>

<h3>6. Indeks keadilan yang mempertahankan ketidakpastiannya</h3>
<p>Dua ketidakadilan harus dipisahkan: <b>ketimpangan akses</b> (pasokan terkonsentrasi di sedikit wilayah) dan
<b>ketimpangan permintaan tak terpenuhi</b> (kebutuhan tertinggal tanpa layanan). Hanya yang kedua menunjukkan di
mana intervensi mengubah kesejahteraan. Keduanya lazim dilaporkan sebagai satu angka Gini; karena kuantitas yang
mendasarinya <i>diestimasi</i>, indeksnya adalah distribusi posterior dan lebarnya adalah selisih antara pembelaan
yang dapat dipertahankan dan hiasan belaka.</p>

<h3>7. Kesimpulan: apa yang dibeli perlakuan Bayesian</h3>
<p><b>Temuan.</b> Dipasang pada rekaman Maret 2026 — 101.020 sesi, 633 unit charger, 14 wilayah layanan, 41,1 juta
penduduk — model mengembalikan permintaan laten agregat <b>229.000 kejadian melawan 101.020 yang tercatat
(selisih ×2,3)</b>. Capture permintaan penduduk membentang 0,15–0,72 antar-wilayah (agregat 0,42 setelah dikurangi
±4.800 sesi aliran koridor); rasio celah berkisar 0,7×–6,6×. Sesi teramati terdistribusi lebih timpang
(G = 0,41) daripada permintaan terestimasi (G = 0,33). Permintaan tak terpenuhi setelah penyesuaian kapasitas
≈2.260 kejadian/hari.</p>
<p><b>Susunan spasial.</b> Ketiga indeks Gini terurut jelas: penyediaan charger paling timpang (G = 0,19 — catatan
poster), sesi teramati paling terkonsentrasi (G = 0,41). Konsentrasi dalam rekaman karena itu dihasilkan oleh
capture, bukan oleh tempat orang tinggal — koridor tol terlayani berlebih sementara wilayah pedalaman berpenduduk
padat kurang terlayani.</p>
<p><b>Metodologis.</b> Model gabungan permintaan–capture dengan struktur spasial BYM2 mengubah rekaman operator
yang under-detected menjadi estimasi permintaan penduduk yang rekaman itu sendiri tidak bisa menunjukkannya —
dengan indeks ketimpangan yang membawa selang kredibel.</p>
<p><b>Praktis.</b> Memeringkat wilayah kandidat atas sesi mentah hanya mereproduksi peta pasokan yang sudah ada;
memeringkatnya atas <i>P</i>(permintaan tak terpenuhi &gt; τ) tidak. Kedua urutan berbeda secara material:
Indramayu naik dari dasar tabel sesi ke peringkat 6 dan menjadi wilayah yang layak diselidiki meski hanya
mencatat 1.508 sesi — dekat Purwakarta dan Cirebon yang sibuk dalam rekaman tetapi jatuh ke separuh bawah begitu
capture diperhitungkan.</p>

<h3>Peringkat keluaran keputusan — P(permintaan tak terpenuhi &gt; 100/hari)</h3>
<div class="tw"><table><thead><tr><th>Wilayah</th><th>P</th><th>Wilayah</th><th>P</th></tr></thead><tbody>
<tr><td>Bekasi</td><td>0,96</td><td>Sukabumi</td><td>0,32</td></tr>
<tr><td>Bogor</td><td>0,94</td><td>Cimahi</td><td>0,32</td></tr>
<tr><td>Bandung</td><td>0,89</td><td>Purwakarta</td><td>0,26</td></tr>
<tr><td>Depok</td><td>0,65</td><td>Tasikmalaya</td><td>0,24</td></tr>
<tr><td>Karawang</td><td>0,65</td><td>Garut</td><td>0,23</td></tr>
<tr><td><b>Indramayu</b></td><td><b>0,55</b></td><td>Cianjur</td><td>0,19</td></tr>
<tr><td></td><td></td><td>Cirebon</td><td>0,16</td></tr>
<tr><td></td><td></td><td>Sumedang</td><td>0,13</td></tr>
</tbody></table></div>
<p class="figcap">Membaca peringkat: P &gt; 0,85 bertindak sekarang · 0,5–0,85 selidiki · 0,3–0,5 pantau ·
P &lt; 0,3 tunda. Probabilitas membawa galat baku Monte Carlo ±0,02, sehingga beda satu peringkat tidak bermakna.</p>

<h3>Rekomendasi</h3>
<ol>
<li><b>Tempatkan atas permintaan tak terpenuhi, bukan atas sesi.</b> Memeringkat wilayah kandidat atas
<i>P</i>(permintaan tak terpenuhi &gt; τ) menaikkan Indramayu dari dasar ke peringkat 6 dan menjadikannya layak
diselidiki hanya atas 1.508 sesi tercatat.</li>
<li><b>Audit keadilan atas permintaan laten.</b> Regulator yang melaporkan Gini berbasis sesi melebih-lebihkan
konsentrasi dan melewatkan celah struktural.</li>
<li><b>Disagregasi sebelum menyatakan cakupan.</b> Georeferensikan stasiun dan sesi ke kabupaten/kota agar celah
di dalam satu wilayah layanan menjadi terlihat.</li>
<li><b>Publikasikan ketidakpastian bersama setiap indeks.</b> Danai keputusan atas selang kredibel, dan pasang
ulang model tiap kali rekaman bulan baru tiba.</li>
</ol>

<h3>Dasbor data langsung</h3>
<p>Poster ini menunjuk dasbor ini sendiri sebagai sumber datanya: rekaman Maret 2026, indeks keadilan, dan model
pemilihan situs di baliknya diterbitkan di <b>jabar-ev.vercel.app</b>.</p>

<h3>Pendanaan &amp; etika data</h3>
<p>Disupervisi Alyas Widita; didanai Ariel Liebman RACE for 2030 PhD Scholarship, Monash University Indonesia.
Rekaman pelanggan utilitas diagregasi ke tingkat wilayah dan dianonimkan, dipakai di bawah perjanjian data;
tidak ada pelanggan perorangan yang dapat diidentifikasi.</p>
"""


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
    dict(
        id="poster-bayes", n=9, category="akses", tags=["akses", "jaringan"],
        title="Bayesian models for spatial equity: separating latent demand from supply in EV charging infrastructure",
        short="Poster — model Bayesian permintaan laten vs pasokan",
        kind="Conference poster",
        venue="Bayesian Analysis & Modelling Workshop 2026 — PhD Poster Prize, Monash Caulfield, 18–19 Nov 2026",
        alt="Dasar Paper 1 (RQ1) — prediksi ex-ante penjualan energi per stasiun",
        venue_src="dinyatakan di poster",
        status="submitted", stage="Poster final — sudah dikirim ke Poster Prize", pct=95,
        abstract=("Permintaan yang belum pernah dibangunkan infrastruktur tidak pernah teramati. Poster ini "
                  "mengusulkan kerangka hierarkis yang memisahkan permintaan pengisian laten dari saringan pasokan "
                  "yang merekamnya — dan meneruskan ketidakpastian itu sampai ke keputusan penempatan itu sendiri. "
                  "Sesi teramati diperlakukan sebagai permintaan penduduk laten yang ditipiskan oleh probabilitas "
                  "capture, dengan aliran koridor tol sebagai suku tambahan; permintaan dan capture diestimasi "
                  "bersama di bawah prior spasial BYM2. Dipasang pada rekaman Maret 2026 Jawa Barat (101.020 sesi, "
                  "633 unit charger, 14 wilayah layanan, 41,1 juta penduduk), model mengembalikan permintaan laten "
                  "agregat 229.000 kejadian melawan 101.020 yang tercatat — selisih ×2,3 — dengan capture 0,15–0,72 "
                  "antar-wilayah dan rasio celah 0,7×–6,6×. Sesi teramati jauh lebih timpang (Gini 0,41) daripada "
                  "permintaan tersirat (Gini 0,33), sehingga konsentrasi dalam rekaman dihasilkan oleh capture, "
                  "bukan oleh tempat orang tinggal. Memeringkat wilayah kandidat atas P(permintaan tak terpenuhi > τ) "
                  "alih-alih atas sesi mentah menaikkan Indramayu dari dasar tabel ke peringkat 6."),
        target="18–19 Nov 2026", lead="Qashtalani Haramaini",
        goal="Memisahkan permintaan pengisian yang laten dari saringan pasokan yang merekamnya: sesi hanya tercatat di tempat charger sudah ada, sehingga rekaman operator meremehkan permintaan justru di daerah yang paling kurang terlayani — lalu meneruskan ketidakpastian itu sampai ke keputusan penempatan.",
        finding="Permintaan laten agregat 229.000 kejadian melawan 101.020 yang tercatat (selisih ×2,3); probabilitas tertangkap a berkisar 0,15–0,72 antar-wilayah; rasio celah 0,7×–6,6× (Indramayu tertinggi); sesi teramati jauh lebih timpang (Gini 0,41) daripada permintaan tersirat (Gini 0,33) sementara Gini penyediaan charger hanya 0,19; peringkat P(permintaan tak terpenuhi > 100/hari) menaikkan Indramayu dari dasar ke peringkat 6.",
        data=["101.020 sesi pengisian · 2,26 GWh (Maret 2026)", "633 unit charger · 14 wilayah layanan operator",
              "41,1 juta penduduk (Sensus 2022, IPM 2023)", "Jaringan jalan & POI (OpenStreetMap)",
              "Instalasi pengisian rumah pelanggan EV (Nov 2025–Jun 2026)"],
        method=["Model N-mixture: y ~ NegBin(μ,φ), μ = d·a + c", "log d = β₀ + xᵀβ + u + v (permintaan laten)",
                "logit a = γ₀ + zᵀγ (saringan ketersediaan pasokan)", "Prior spasial BYM2 (ICAR + iid, prior PC)",
                "Stan NUTS 24.000 iterasi / 1.000 draw; varian dengan INLA",
                "Validasi SBC, PPC, PSIS-LOO; keluaran keputusan P(permintaan tak terpenuhi > τ)"],
        tabs=["capacity", "equity", "locint"],
        html=POSTER_HTML,
        files=[["Poster (.pdf)", FILES + "Poster_Bayesian_Spatial_Equity_BAM2026.pdf"],
               ["Poster (.png)", FILES + "poster_bayesian_2026.png"]],
        todo=["Disagregasi ke tingkat kecamatan dan pasang suku spasial BYM2 di tahap itu",
              "Replikasi bulanan Jan 2024–Jun 2026 (420 area-bulan) untuk mengidentifikasi model N-mixture temporal",
              "Kembangkan menjadi Paper 1 (IEEE) sesuai rencana RQ1 — target submit Mar 2027",
              "Uji asumsi exclusion restriction (headroom jaringan & ketersediaan lahan) sebagai instrumen"],
    ),
    dict(
        id="cupum-objective", n=10, category="akses", tags=["akses", "bisnis"],
        title="One model, two cities: the objective function as an unaccountable planning decision in algorithmic EV charging deployment",
        short="Satu model, dua provinsi — fungsi tujuan sebagai keputusan perencanaan",
        kind="Book chapter (CUPUM 2027)",
        venue="CUPUM 2027 — Future Cities in the Era of AI (bab buku)",
        alt="—", venue_src="dinyatakan di naskah",
        status="review", stage="Naskah utuh (5.522 kata) — siap ditinjau pembimbing", pct=75,
        target="CUPUM 2027 (tenggat: cek panggilan bab buku)",
        lead="Qashtalani Haramaini, Alyas Widita, Liz Taylor",
        goal="Memperlakukan model penempatan SPKLU di dalam utilitas terintegrasi vertikal sebagai objek kajian perencanaan: di Indonesia bukan otoritas perencanaan yang mengalokasikan pengisian publik, melainkan fungsi tujuan sebuah model — sehingga bobot di dalamnya sudah menjadi kebijakan tata guna lahan.",
        finding="Bukti dan anggaran yang sama (50 situs baru dari 111 sel layak) menghasilkan dua provinsi berbeda. Portofolio komersial memusat di 9 kabupaten/kota, menaruh 20 % situs di kabupaten berpendapatan rendah, menjangkau 577 pemilik yang kini tak terlayani; portofolio keadilan menyebar ke 14 kabupaten/kota, 54 % situs di kabupaten berpendapatan rendah, menjangkau 723 pemilik — dengan ongkos 42 % energi prediksi model. Hanya 21 situs muncul di kedua daftar (berbeda di 29 dari 50). Sapuan bobot keadilan λ = 0 → 1 menunjukkan trade-off yang mulus dan monoton: pilihan politik yang menyamar sebagai parameter.",
        data=["101.020 sesi pengisian Maret 2026 · 636 unit / 348 situs (330 tergeokode)",
              "3.687 rumah tangga pelanggan EV tergeokode (tarif home charging)",
              "53.797 catatan trafo distribusi (41.129 layak pakai)",
              "BPS 2022/2023 + tipologi Klassen: populasi, IPM, tingkat pendapatan (19 kelompok kota/kabupaten)"],
        method=["Random forest atas energi teramati per situs pada grid 5 km",
                "Model paparan Bayesian atas pemilik EV terdaftar",
                "Saringan kelayakan headroom trafo ≥ 240 kVA",
                "Dua fungsi tujuan: komersial (maksimum energi) vs keadilan (pemilik tak terlayani, jarak ke charger, pendapatan kabupaten)",
                "Sapuan bobot keadilan λ = 0 → 1 dan perbandingan portofolio 50 situs",
                "Standar akuntabilitas minimum: terbitkan tujuan, bobot, portofolio tandingan, dan versi model"],
        tabs=["locint", "capacity", "equity"],
        html=chapter_html("CUPUM2027_Ch1_One_Model_Two_Cities.docx", "cupum-objective"),
        files=[["Naskah (.docx)", FILES + "CUPUM2027_Ch1_One_Model_Two_Cities.docx"]],
        todo=["Konfirmasi tenggat dan templat panggilan bab buku CUPUM 2027",
              "Selaraskan jumlah situs dengan Bab 2 dan naskah CIRED (330 vs 331 situs tergeokode)",
              "Terbitkan portofolio tandingan beserta bobotnya di repositori terbuka seperti yang naskah usulkan",
              "Isi versi model dan tanggal snapshot pada pernyataan akuntabilitas"],
    ),
    dict(
        id="cupum-sparsity", n=11, category="akses", tags=["akses", "jaringan"],
        title="Training on the past: feedback loops, latent demand and the politics of sparse data in charging networks",
        short="Melatih model pada masa lalu — umpan balik & permintaan laten",
        kind="Book chapter (CUPUM 2027)",
        venue="CUPUM 2027 — Future Cities in the Era of AI (bab buku)",
        alt="—", venue_src="dinyatakan di naskah",
        status="review", stage="Naskah utuh (4.607 kata) — siap ditinjau pembimbing", pct=75,
        target="CUPUM 2027 (tenggat: cek panggilan bab buku)",
        lead="Qashtalani Haramaini, Alyas Widita, Liz Taylor",
        goal="Menunjukkan bahwa pada jaringan yang dibangun mendahului permintaan, rekaman transaksi yang dipelajari model penempatan bukanlah sampel permintaan melainkan catatan keputusan alokasi sebelumnya — sehingga pipeline siting berbasis data mengandung umpan balik yang berkonsekuensi distributif, secara struktural sama dengan predictive policing.",
        finding="Transaksi hanya ada di 174 dari 1.295 sel 5 km; 132 sel memuat 908 pemilik EV terdaftar tanpa satu pun charger. Random forest atas data teramati dan model hierarkis Gamma–Poisson atas permintaan laten hanya sepakat lemah tentang lokasi berikutnya (Spearman ρ = 0,30; 26 dari 50 sel teratas beririsan), dan ketidakpastian posterior paling lebar justru di tempat tanpa infrastruktur maupun observasi. Simulasi deployment sepuluh putaran menutup lingkarannya: permintaan dari sel tak terlayani dikreditkan ke situs terdekat, model dilatih ulang atas rekaman itu dan terus merekomendasikan pemadatan — menyisakan 19 % permintaan laten di kabupaten berpendapatan rendah tak terlayani, melawan 7 % untuk aturan permintaan laten.",
        data=["101.020 sesi pengisian Maret 2026 — hanya di 174 dari 1.295 sel 5 km",
              "3.687 rumah tangga terdaftar tarif home charging sebagai sinyal paparan bebas-penempatan",
              "53.797 survei beban trafo distribusi (headroom terkoreksi pertumbuhan)",
              "Populasi, IPM & tingkat pendapatan kabupaten/kota (BPS)"],
        method=["Model A — random forest atas transaksi teramati (kovariat jaringan & geografi)",
                "Model B — hierarkis Gamma–Poisson dengan partial pooling atas paparan pemilik terdaftar",
                "Perbandingan peringkat 50 sel teratas (Spearman ρ, ukuran irisan)",
                "Simulasi deployment 10 putaran: permintaan tak terlayani dikreditkan ke situs terdekat, model dilatih ulang",
                "Pelaporan ketidakpastian posterior sebagai keluaran kelas satu planning support system"],
        tabs=["locint", "capacity", "equity"],
        html=chapter_html("CUPUM2027_Ch2_Training_on_the_Past.docx", "cupum-sparsity"),
        files=[["Naskah (.docx)", FILES + "CUPUM2027_Ch2_Training_on_the_Past.docx"]],
        todo=["Konfirmasi tenggat dan templat panggilan bab buku CUPUM 2027",
              "Rujuk silang model Gamma–Poisson di sini dengan model N-mixture BYM2 pada poster BAM 2026",
              "Uji ketahanan simulasi 10 putaran terhadap aturan pengalihan permintaan yang berbeda",
              "Sinkronkan jumlah sel (1.295 / 238 / 132) dengan angka naskah CIRED (1.292 / 235 / 129)"],
    ),
    dict(
        id="cupum-participation", n=12, category="akses", tags=["akses"],
        title="From access to use: large language models as a participation surface for charging infrastructure, and the class filter they inherit",
        short="Dari akses ke penggunaan — LLM sebagai permukaan partisipasi",
        kind="Book chapter (CUPUM 2027)",
        venue="CUPUM 2027 — Future Cities in the Era of AI (bab buku)",
        alt="—", venue_src="dinyatakan di naskah",
        status="review", stage="Naskah utuh (4.512 kata) — siap ditinjau pembimbing", pct=75,
        target="CUPUM 2027 (tenggat: cek panggilan bab buku)",
        lead="Qashtalani Haramaini, Alyas Widita, Liz Taylor",
        goal="Menghitung charger mengukur keberadaan, bukan kebergunaan. Di tempat tanpa kanal partisipasi formal, satu-satunya rekaman sistematis tentang bagaimana pengisian dialami adalah teks ulasan pengguna; naskah ini memperlakukannya sebagai permukaan partisipasi lalu menanyakan dua hal sekaligus — apa yang diungkapnya, dan siapa yang tidak terdengar olehnya.",
        finding="Reliabilitas dan ketersediaan mendominasi kualitas yang dirasakan; tujuh aspek menjelaskan 63 % ragam SQI. Perangkat keras tersebar hampir netral (CI = +0,06) sementara penggunaan sangat pro-kaya (energi per kapita CI = +0,34; kepemilikan EV CI = +0,45), dan kualitas yang dirasakan datar sepanjang gradien pendapatan (CI = −0,02) — masalah reliabilitas bersifat jaringan-luas, bukan pinggiran. Namun permukaan yang melaporkannya miring: situs PLN di tercile IPM tertinggi menarik 8,3 ulasan per situs melawan 4,0 di tercile terendah, dan hanya 38 % situs IPM rendah punya cukup ulasan untuk diskor. Umpan balik yang dimediasi LLM mereproduksi saringan kelas sambil tampil sebagai suara publik.",
        data=["Korpus ulasan publik 894 lokasi; 584 lokasi cukup volume untuk diskor (244 Jawa Barat, 340 luar)",
              "Master SPKLU (636 unit / 348 situs) + 101.020 transaksi Maret 2026",
              "BPS & tipologi Klassen: populasi, IPM, tingkat pendapatan 19 kota/kabupaten"],
        method=["ABSA dengan large language model: tujuh aspek layanan per ulasan → Station Quality Index",
                "Dampak aspek (selisih rerata SQI positif vs negatif) + OLS SQI ~ tujuh aspek (R² = 0,63)",
                "Indeks konsentrasi tertimbang populasi atas peringkat IPM (unit, energi, kepemilikan, SQI)",
                "Audit cakupan: lokasi terskor & ulasan per situs menurut tercile IPM",
                "Kerangka keadilan dua dimensi — akses × pengalaman"],
        tabs=["perception", "equity", "socio"],
        html=chapter_html("CUPUM2027_Ch3_From_Access_to_Use.docx", "cupum-participation"),
        files=[["Naskah (.docx)", FILES + "CUPUM2027_Ch3_From_Access_to_Use.docx"]],
        todo=["Konfirmasi tenggat dan templat panggilan bab buku CUPUM 2027",
              "Selaraskan definisi SQI dan korpus ulasan dengan Paper 1 (equity & perception)",
              "Uji ketahanan audit cakupan bila situs operator swasta dimasukkan",
              "Jadikan audit cakupan prosedur baku sebelum sentimen hasil scraping dipakai dalam perencanaan"],
    ),
]

PLAN = [
    ["2026 Q3", "CIRED 2027 — Capacity maps (full paper)", "Draft selesai · tinjauan pembimbing", "cired2027"],
    ["2026 Q3", "CIRED 2027 — Energy forecast → network load (Session 5)", "Full paper · tinjauan pembimbing", "dndp"],
    ["2026 Q4", "Paper 1 — Spatial equity & perception", "Verifikasi angka · sitasi · submit ERSS", "equity"],
    ["2026 Q4", "ASEAN working paper", "Finalisasi & pilih jurnal sasaran", "asean"],
    ["2026 Q4", "IAEE 2027 — Balance sheet problem (abstrak)", "Kalibrasi fsQCA · submit abstrak", "swap"],
    ["2026 Q4", "CUPUM 2027 — Bab 1: One model, two cities", "Tinjauan pembimbing · konfirmasi tenggat bab buku", "cupum-objective"],
    ["2026 Q4", "CUPUM 2027 — Bab 2: Training on the past", "Tinjauan pembimbing · konfirmasi tenggat bab buku", "cupum-sparsity"],
    ["2026 Q4", "CUPUM 2027 — Bab 3: From access to use", "Tinjauan pembimbing · konfirmasi tenggat bab buku", "cupum-participation"],
    ["2027 Q1", "Tailpipe to smokestack", "Tetapkan jurnal · submit", "tailpipe"],
    ["2027 Q1", "Captive generation & CBAM", "Tetapkan jurnal · submit", "cbam"],
    ["2027 Q1", "Paper 2 — Coverage to capability", "Validasi model siting · submit SCS", "siting"],
    ["2027 Q2", "CIRED 2027 — presentasi (2 makalah)", "Perbaikan pasca-tinjauan", "cired2027"],
]


def brief_html(p):
    """Naskah rencana belum punya manuskrip — halaman bacanya dibangun dari brief risetnya."""
    li = lambda a: "".join(f"<li>{html.escape(x)}</li>" for x in a)
    return f"""
<h2>{html.escape(p['title'])}</h2>
<p class="authors">{html.escape(p['lead'])} · {html.escape(p['venue'])}</p>
<blockquote>Naskah belum ada. Halaman ini menampilkan <b>brief riset</b> dari rencana disertasi
(<i>Pathways PhD Research Plan</i>, {html.escape(p['part_label'])}). Unggah manuskripnya lewat tombol
<b>Unggah naskah baru</b> begitu draft pertama siap — id yang sama akan menimpa entri ini.</blockquote>
<h3>Pertanyaan riset</h3><p>{html.escape(p['rq'])}</p>
<h3>Tujuan</h3><p>{html.escape(p['goal'])}</p>
<h3>Status menurut rencana disertasi</h3><p>{html.escape(p['stage'])}</p>
<h3>Data</h3><ul>{li(p['data'])}</ul>
<h3>Metode</h3><ul>{li(p['method'])}</ul>
<h3>Keluaran yang direncanakan</h3><ul>{li(p['outputs'])}</ul>
<h3>Daftar kerja</h3><ul>{li(p['todo'])}</ul>
"""


PLANNED_PAPERS = [
    dict(
        id="rq1-exante", n=13, category="akses", tags=["akses"], part="P1",
        part_label="Part 1 — From Latent Demand to Right-Sized Supply",
        title="Ex-ante prediction of station-level energy sales",
        short="Prediksi ex-ante penjualan energi per stasiun (RQ1)",
        kind="Journal article", venue="IEEE journal (Q1)", alt="Applied Energy · eTransportation",
        venue_src="dinyatakan di rencana disertasi",
        status="draft", stage="Full draft sudah ada — fokus Tahun 1 adalah mengetatkan validasi dan submit jurnal.",
        pct=60, target="Submit Mar 2027", lead="Qashtalani Haramaini",
        rq=("Berapa besar permintaan pengisian laten di tiap lokasi, dan bagaimana pasokan dapat "
            "ditakar tepat — dengan mengoreksi bias bahwa permintaan hanya teramati di tempat stasiun sudah ada?"),
        goal=("Memprediksi kWh yang akan terjual di lokasi kandidat sebelum dibangun, dengan koreksi bias "
              "seleksi sampel, sebagai fondasi permintaan yang dipakai Bagian 2–4."),
        data=["101.020 transaksi, 330 SPKLU (Jawa Barat)", "Atribut stasiun: kapasitas, jenis konektor, operator",
              "Kepadatan POI, jaringan jalan, tata guna lahan, grid populasi"],
        method=["Model permintaan dua parameter terkalibrasi transaksi",
                "Random forest dengan spatial k-fold CV (vs random k-fold)",
                "Koreksi bias: permintaan laten vs teramati; aksesibilitas berbasis jaringan",
                "Validasi out-of-bag, diagnostik fitur gaya SHAP"],
        outputs=["Paper 1 — jurnal IEEE", "Prediksi kWh untuk situs kandidat sebelum konstruksi",
                 "Alat keputusan penempatan (dasbor GeoSPKLU)"],
        todo=["Ketatkan validasi spatial k-fold dan laporkan bandingannya dengan random k-fold",
              "Selaraskan jendela data dengan Paper 2", "Siapkan format IEEE dan submit (target Mar 2027)",
              "Unggah manuskripnya ke perpustakaan ini begitu siap ditinjau"],
    ),
    dict(
        id="rq3-causal", n=14, category="akses", tags=["akses", "bisnis"], part="P3",
        part_label="Part 3 — Create or Redistribute Demand?",
        title="Does building more charging create or redistribute demand?",
        short="Menciptakan atau memindahkan permintaan? (RQ3)",
        kind="Journal article", venue="Belum ditetapkan", alt="Transport Policy · Journal of Transport Geography",
        venue_src="belum ditetapkan",
        status="plan", stage="Belum dimulai — dirancang di Tahun 1, dieksekusi di Tahun 2 setelah panel pasca-ekspansi cukup panjang.",
        pct=5, target="Tahun 2 (2027–2028)", lead="Qashtalani Haramaini",
        rq=("Apakah stasiun baru menghasilkan permintaan pengisian tambahan (pertumbuhan pasar), atau "
            "mengkanibalisasi permintaan dari stasiun terdekat yang sudah ada (redistribusi)?"),
        goal=("Mengidentifikasi efek kausal pembangunan infrastruktur pengisian baru dengan memanfaatkan "
              "roll-out SPKLU Indonesia yang bertahap sebagai eksperimen kuasi-alami."),
        data=["Panel kWh stasiun-bulan dengan tanggal pembukaan bertahap",
              "Ekspansi 300 % 2023–2024 = penentuan waktu yang secara masuk akal eksogen",
              "Cincin jarak di sekitar tiap entran baru (intensitas perlakuan)"],
        method=["Staggered Difference-in-Differences (estimator gaya Callaway–Sant'Anna)",
                "Desain event-study: pre-trend, efek dinamis",
                "Spesifikasi spillover spasial: efek menurut pita jarak",
                "Ketahanan: kelompok kontrol alternatif, pembukaan plasebo"],
        outputs=["Paper 3 — estimasi kausal penciptaan vs redistribusi permintaan",
                 "Elastisitas penggunaan jaringan terhadap kepadatan jaringan",
                 "Panduan penempatan: di mana stasiun baru menambah nilai vs mengkanibalisasi"],
        todo=["Rancang desain identifikasi dan pra-daftarkan spesifikasinya di Tahun 1",
              "Bangun panel stasiun-bulan dengan tanggal pembukaan yang terverifikasi",
              "Tunggu panel pasca-ekspansi cukup panjang sebelum estimasi"],
    ),
    dict(
        id="rq4-synthesis", n=15, category="akses", tags=["akses"], part="P4",
        part_label="Part 4 — Inequity & Inequality",
        title="Inequity and inequality in charging access: horizontal vs vertical equity",
        short="Ketidakadilan vs ketimpangan — sintesis & kerangka kebijakan (RQ4)",
        kind="Journal article + bab disertasi", venue="Belum ditetapkan",
        alt="Energy Research & Social Science · Transport Policy", venue_src="belum ditetapkan",
        status="plan", stage="Tahap konseptual — bab integratif yang mengubah tiga paper empiris menjadi satu argumen kebijakan.",
        pct=5, target="Tahun 3 (2028–2029)", lead="Qashtalani Haramaini",
        rq=("Bagaimana ketidakadilan (inequity) dan ketimpangan (inequality) akses pengisian berbeda "
            "menurut garis urban–rural dan pendapatan — dan tuas kebijakan mana yang menutup celah yang mana?"),
        goal=("Memisahkan akses yang tidak adil dari akses yang tidak merata, lalu menurunkan kerangka "
              "kebijakan yang memasangkan tiap tuas intervensi dengan celah yang benar-benar ditutupnya."),
        data=["Keluaran terintegrasi Bagian 1–3 (permintaan, keadilan, efek kausal)",
              "Tipologi urban–rural; strata pendapatan dan kepemilikan kendaraan",
              "Skenario kebijakan: aturan penempatan, desain tarif, penargetan insentif"],
        method=["Dekomposisi horizontal vs vertical equity",
                "Indeks ketimpangan (Theil, dekomposisi antar/dalam kelompok)",
                "Aksesibilitas terkoreksi kebutuhan: akses setara ≠ akses adil",
                "Analisis skenario di atas model penempatan Bagian 1"],
        outputs=["Paper 4 — paper sintesis + bab penutup disertasi",
                 "Kerangka kebijakan: intervensi mana menargetkan inequity vs inequality",
                 "Rekomendasi untuk PLN, pemerintah daerah, dan regulator"],
        todo=["Kunci definisi operasional inequity vs inequality bersama pembimbing",
              "Tunggu keluaran Bagian 1–3 sebelum sintesis", "Rancang skenario kebijakan yang dapat diuji"],
    ),
]

for _p in PLANNED_PAPERS:
    _p["html"] = brief_html(_p)
    _p["abstract"] = _p["goal"]
    _p["files"] = [["Rencana disertasi (.pptx)", FILES + "Pathways_PhD_Research_Plan.pptx"]]
    _p["tabs"] = ["locint"] if _p["id"] == "rq1-exante" else ["equity"]
    _p["manuscript"] = False
PAPERS += PLANNED_PAPERS


# ---------------------------------------------------------------- kerangka PhD
PHD = dict(
    title="Pathways to Advancing Sustainable Transportation — Spatial Equity of EV Charging Infrastructure (SPKLU) in West Java, Indonesia",
    program="Monash University · Ariel Liebman RACE for 2030 PhD Program",
    supervisors=["Dr. Alyas Widita", "Dr. Liz Taylor"],
    lead="Qashtalani Haramaini",
    shape="Disertasi tiga tahun dalam empat bagian — empat pertanyaan riset",
    year1="Tahun 1: Agu 2026 – Jul 2027",
    argument=("Transisi EV yang adil menuntut pengisian dibangun di titik tempat permintaan laten dan "
              "kebutuhan sosial bertemu — bukan sekadar di tempat yang paling mudah."),
    backbone=["±3.000 SPKLU nasional; 330 di Jawa Barat dengan kapasitas & status",
              "101.020 sesi pengisian, kWh per stasiun, Jan 2024 – Jun 2026",
              "Ulasan pengguna: Google Maps & aplikasi PLN — teks tak terstruktur, bergeotag",
              "BPS: proksi pendapatan, urbanisasi, kepadatan penduduk"],
)

PARTS = [
    dict(id="P1", no=1, kind="Predictive", name="From Latent Demand to Right-Sized Supply",
         subtitle="Kerangka penempatan pengisian EV yang terkoreksi bias dan berbasis jaringan",
         rq="RQ1 — Berapa besar permintaan laten di tiap lokasi, dan bagaimana pasokan ditakar tepat — mengoreksi bias seleksi sampel karena permintaan hanya teramati di tempat stasiun sudah ada?",
         stage="Full draft sudah ada — fokus Tahun 1 mengetatkan validasi dan submit jurnal. Memberi baseline permintaan yang dipakai Bagian 2–4.",
         papers=["rq1-exante", "poster-bayes", "cupum-sparsity", "cupum-objective"]),
    dict(id="P2", no=2, kind="Evaluative", name="Spatial Equity × User-Perceived Performance",
         subtitle="Menilai bersama keadilan distributif dan keandalan serta aksesibilitas yang dirasakan",
         rq="RQ2 — Sejauh mana distribusi SPKLU adil relatif terhadap kondisi sosial-ekonomi, dan bagaimana pengguna mempersepsikan keandalan serta aksesibilitasnya?",
         stage="Full draft sudah ada. Tugas kunci: menyelaraskan jendela data dengan Paper 1 dan memfinalkan kerangka gabungan keadilan–persepsi.",
         papers=["equity", "siting", "cupum-participation"]),
    dict(id="P3", no=3, kind="Causal", name="Create or Redistribute Demand?",
         subtitle="Efek kausal pembangunan infrastruktur pengisian baru",
         rq="RQ3 — Apakah stasiun baru menghasilkan permintaan tambahan (pertumbuhan pasar), atau memindahkan permintaan dari stasiun terdekat (redistribusi)?",
         stage="Belum dimulai — dirancang di Tahun 1, dieksekusi di Tahun 2 setelah panel pasca-ekspansi cukup panjang.",
         papers=["rq3-causal"]),
    dict(id="P4", no=4, kind="Synthesis", name="Inequity & Inequality",
         subtitle="Horizontal vs vertical equity — sintesis dan kerangka kebijakan",
         rq="RQ4 — Bagaimana inequity dan inequality akses pengisian berbeda menurut garis urban–rural dan pendapatan — dan tuas kebijakan mana yang menutup celah yang mana?",
         stage="Tahap konseptual — bab integratif yang mengubah tiga paper empiris menjadi satu argumen kebijakan.",
         papers=["rq4-synthesis"]),
]

# Naskah di luar keempat bagian: aliran riset tambahan yang tumbuh dari data yang sama.
SIDE_STREAM = dict(
    id="SS", name="Aliran tambahan — jaringan, emisi, pasar",
    subtitle="Naskah yang tumbuh dari tulang punggung data yang sama tetapi di luar keempat bagian disertasi",
    papers=["cired2027", "dndp", "tailpipe", "cbam", "asean", "swap"],
)

MILESTONES = [
    ["Agu 2026", "PhD dimulai — Tahun 1", "Ariel Liebman RACE for 2030 PhD Scholarship, Monash University Indonesia.", "done", ""],
    ["Sep 2026", "Dasbor riset daring", "jabar-ev.vercel.app — 17 tab analitik; dikutip poster BAM 2026 sebagai sumber datanya.", "done", "https://jabar-ev.vercel.app"],
    ["2026", "Peta web ArcGIS", "Publikasi peta daring — milestone geospasial proyek.", "done", "https://arcg.is/1LKWDv4"],
    ["Okt 2026", "Proposal riset bersih disubmit", "Struktur empat bagian dikunci bersama pembimbing.", "upcoming", ""],
    ["Nov 2026", "Persetujuan etik (MUHREC)", "Mencakup pengumpulan & penanganan data ulasan pengguna.", "upcoming", ""],
    ["18–19 Nov 2026", "BAM 2026 — PhD Poster Prize", "Poster 'Bayesian Models for Spatial Equity', Monash Caulfield.", "upcoming", ""],
    ["2026 Q4", "CUPUM 2027 — tiga bab buku", "Naskah utuh Bab 1–3 (Future Cities in the Era of AI) selesai; tinjauan pembimbing lalu submit — tenggat menunggu panggilan bab buku.", "upcoming", ""],
    ["Mar 2027", "Paper 1 disubmit — jurnal Q1", "Prediksi ex-ante kWh tingkat stasiun (IEEE).", "upcoming", ""],
    ["Jun–Jul 2027", "Confirmation of Candidature", "Paper 2 draft lanjut; desain Bagian 3 selesai.", "upcoming", ""],
    ["Jul–Agu 2027", "Mobility — Monash Melbourne", "Penempatan 6 bulan berdana, RACE for 2030.", "upcoming", ""],
]

OUTPUTS = [
    ["Naskah", "15 naskah dalam pipeline", "4 draft jurnal, 3 conference paper, 3 bab buku CUPUM 2027, 1 working paper, 1 poster, 3 rencana", ""],
    ["Dasbor", "jabar-ev.vercel.app", "17 tab: peta, keadilan, persepsi, permintaan, jaringan, karbon, perpustakaan naskah", "https://jabar-ev.vercel.app"],
    ["Peta", "GeoSPKLU", "Peta geospasial SPKLU dengan status dan kapasitas, tertanam di dasbor", ""],
    ["Peta", "Peta web ArcGIS", "Publikasi peta daring — buka tautan untuk melihat petanya", "https://arcg.is/1LKWDv4"],
    ["Kode", "Pipeline analisis terbuka", "prepare.py, build.py, inject_papers.py — seluruh angka dapat dibangun ulang dari data mentah", ""],
    ["Data", "Payload teragregasi", "capacity.json, grid.json, grid2.json, library.json — teragregasi & dianonimkan", ""],
]

for p in PAPERS:
    p.setdefault("manuscript", True)
    p["html"] = number_blocks(p["html"])
    p["toc"] = toc_of(p["html"])
    p["words"] = words(p["html"])
    p["abstract"] = p.get("abstract") or abstract_of(p["html"])
    assert p["abstract"], "abstrak tidak ditemukan: " + p["id"]

_by = {p["id"]: p for p in PAPERS}
for part in PARTS:
    got = [_by[i] for i in part["papers"] if i in _by]
    part["pct"] = round(sum(g["pct"] for g in got) / len(got)) if got else 0
    part["titles"] = [[g["id"], g["short"], g["pct"], g["status"]] for g in got]
SIDE_STREAM["titles"] = [[_by[i]["id"], _by[i]["short"], _by[i]["pct"], _by[i]["status"]]
                         for i in SIDE_STREAM["papers"] if i in _by]
SIDE_STREAM["pct"] = round(sum(t[2] for t in SIDE_STREAM["titles"]) / len(SIDE_STREAM["titles"]))

out = dict(papers=PAPERS, plan=PLAN, categories=CATEGORIES, phd=PHD, parts=PARTS,
           side=SIDE_STREAM, milestones=MILESTONES, outputs=OUTPUTS)
s = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
open(os.path.join(ROOT, "papers/library/library.json"), "w", encoding="utf-8").write(s)
for p in PAPERS:
    print(f'  [{p["id"]:9s}] {p["words"]:5d} kata · {len(p["toc"]):2d} judul · {p["pct"]:3d}% · '
          f'{CATEGORIES[p["category"]][0][:26]:26s} · {"naskah" if p["manuscript"] else "brief "} '
          f'· abstrak {len(p["abstract"].split())} kata')
for part in PARTS + [SIDE_STREAM]:
    print(f'  <{part["id"]}> {part["pct"]:3d}% · {part["name"][:44]:44s} · {len(part["titles"])} naskah')
print(f"library.json ditulis: {len(s)/1024:.0f} KB")
