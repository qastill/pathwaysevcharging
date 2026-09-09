"""Pembaca tabel BPS kabupaten/kota → equitymap/input/kabupaten_sosek.csv

    python3 equitymap/sosek.py --poverty "<unduhan BPS>.xlsx" --hdi "<unduhan BPS>.xlsx" --expend "<unduhan BPS>.xlsx" [--year 2024]

Tabel yang dimaksud (bps.go.id → Statistik menurut subjek, unduh xlsx/csv):
  --poverty  "Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota"           (persen)
  --hdi      "Indeks Pembangunan Manusia menurut Kabupaten/Kota"                  (indeks 0–100)
  --expend   "Pengeluaran per Kapita Disesuaikan menurut Kabupaten/Kota"          (ribu rupiah/orang/tahun)
Satu berkas boleh dipakai untuk beberapa indikator (--sheet-poverty dst. memilih lembar).

Cara kerja (tahan terhadap tata letak BPS yang berubah-ubah): di tiap lembar dicari kolom yang sel-selnya paling
banyak cocok dengan 515 nama kabupaten/kota geoBoundaries (input/kabupaten.csv); nilai diambil dari kolom tahun
yang diminta (--year, dicari di baris judul) atau, bila tidak ada, sel numerik paling kanan di baris itu (tahun
terbaru). Nama dicocokkan lewat kunci padat (huruf kecil, tanpa spasi/tanda baca, awalan "kab./kabupaten"
dibuang, awalan "kota" dipertahankan), tabel alias untuk ejaan BPS ≠ geoBoundaries, lalu difflib ≥0,88.
Nama yang tidak cocok dicetak supaya ALIAS bisa ditambah. Hasil: idx,name,prov,poverty,hdi,expend.
"""
import argparse, csv, difflib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "input", "kabupaten_sosek.csv")

ALIAS = {  # kunci padat BPS -> kunci padat geoBoundaries
    "pangkajenedankepulauan": "pangkajenekepulauan", "pangkep": "pangkajenekepulauan",
    "kotapadangsidempuan": "kotapadangsidimpuan", "kepulauansiautagulandangbiaro": "siautagulandangbiaro",
    "mahakamhulu": "mahakamulu", "toba": "tobasamosir", "pohuwato": "pahuwato", "tolitoli": "tolitoli",
    "kotapangkalpinang": "kotapangkalpinang", "kotatidorekepulauan": "kotatidorekepulauan",
    "kepulauanseribu": "kepulauanseribu", "kotajakartapusat": "kotajakartapusat",
    "musirawasutara": "musirawasutara", "penukalabablematangilir": "penukalabablematangilir",
    "banyuasin": "banyuasin", "kotasubulussalam": "kotasubulussalam", "kotasungaipenuh": "kotasungaipenuh",
    "gunungkidul": "gunungkidul", "kulonprogo": "kulonprogo", "kotayogyakarta": "kotayogyakarta",
    "kotabatu": "kotabatu", "kotasurakarta": "kotasurakarta", "kotasalatiga": "kotasalatiga",
    "kotamataram": "kotamataram", "kotabima": "kotabima", "kotakupang": "kotakupang",
    "labuhanbatu": "labuhanbatu", "labuhanbatuutara": "labuhanbatuutara", "labuhanbatuselatan": "labuhanbatuselatan",
    "batubara": "batubara", "kotatanjungbalai": "kotatanjungbalai", "kotapematangsiantar": "kotapematangsiantar",
    "kotagunungsitoli": "kotagunungsitoli", "limapuluhkota": "limapuluhkota", "kotasawahlunto": "kotasawahlunto",
    "kotapariaman": "kotapariaman", "kotatanjungpinang": "kotatanjungpinang", "mukomuko": "mukomuko",
    "kotapalangkaraya": "kotapalangkaraya", "kotabaubau": "kotabaubau", "kotaparepare": "kotaparepare",
    "kotapalopo": "kotapalopo", "kotakotamobagu": "kotakotamobagu", "fakfak": "fakfak",
}


def key(s):
    s = str(s or "").strip().lower()
    s = re.sub(r"^(kab\.?|kabupaten|kota adm\.?|kota administrasi)\s+", lambda m: "kota " if m.group(1).startswith("kota") else "", s)
    s = re.sub(r"[^a-z0-9]", "", s)
    return s


def parse_num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(" ", " ")
    if not s or s in ("-", "–", "…", "...", "n.a", "na", "NA"):
        return None
    s = s.replace(" ", "")
    if re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", s):          # 10.250,5 → ribuan titik, desimal koma
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(,\d{3})+(\.\d+)?", s):        # 10,250.5 → ribuan koma
        s = s.replace(",", "")
    else:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def load_sheets(path, sheet=None):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        with open(path, encoding="utf-8-sig", newline="") as f:
            sample = f.read(4096); f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample else csv.excel
            return {"csv": [row for row in csv.reader(f, dialect)]}
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = {}
    for ws in wb.worksheets:
        if sheet and ws.title != sheet:
            continue
        out[ws.title] = [list(r) for r in ws.iter_rows(values_only=True)]
    return out


def extract(path, kabs, year=None, sheet=None, label=""):
    """→ dict idx -> nilai. Memilih lembar & kolom nama dengan kecocokan terbanyak."""
    by_key = {key(k["name"]): int(k["idx"]) for k in kabs}
    keys = list(by_key)
    best = None
    for title, rows in load_sheets(path, sheet).items():
        ncol = max((len(r) for r in rows), default=0)
        for c in range(ncol):
            hits = 0
            for r in rows:
                if c < len(r) and r[c] is not None and match(key(r[c]), by_key, keys) is not None:
                    hits += 1
            if best is None or hits > best[0]:
                best = (hits, title, c, rows)
    if not best or best[0] < 50:
        sys.exit(f"[{label}] tidak menemukan kolom nama kabupaten di {path} (kecocokan terbanyak {best[0] if best else 0})")
    hits, title, c, rows = best
    ycol = None
    if year:
        for r in rows[:15]:
            for j, v in enumerate(r):
                if v is not None and str(year) in str(v) and j != c:
                    ycol = j; break
            if ycol is not None:
                break
        if ycol is None:
            print(f"[{label}] peringatan: kolom tahun {year} tidak ditemukan di lembar '{title}', memakai kolom numerik paling kanan")
    vals, unmatched = {}, []
    for r in rows:
        if c >= len(r) or r[c] is None:
            continue
        idx = match(key(r[c]), by_key, keys)
        if idx is None:
            k = key(r[c])
            if k and not re.search(r"(provinsi|indonesia|kabupatenkota|sumber|catatan|tahun)", k):
                unmatched.append(str(r[c]).strip())
            continue
        if ycol is not None:
            v = parse_num(r[ycol]) if ycol < len(r) else None
        else:
            v = None
            for j in range(len(r) - 1, c, -1):
                v = parse_num(r[j])
                if v is not None:
                    break
        if v is not None:
            vals[idx] = v
    print(f"[{label}] lembar '{title}', kolom {c}: {len(vals)} kabupaten bernilai · {len(set(unmatched))} nama tidak cocok"
          + (": " + "; ".join(sorted(set(unmatched))[:40]) if unmatched else ""))
    return vals


_fuzzy_cache = {}


def match(k, by_key, keys):
    if not k:
        return None
    if k in by_key:
        return by_key[k]
    if ALIAS.get(k) in by_key:
        return by_key[ALIAS[k]]
    if k in _fuzzy_cache:
        return _fuzzy_cache[k]
    cand = difflib.get_close_matches(k, keys, n=1, cutoff=0.88)
    # jangan biarkan "kota x" cocok dengan "x" atau sebaliknya
    res = by_key[cand[0]] if cand and (cand[0].startswith("kota") == k.startswith("kota")) else None
    _fuzzy_cache[k] = res
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for ind in ("poverty", "hdi", "expend"):
        ap.add_argument("--" + ind); ap.add_argument("--sheet-" + ind)
    ap.add_argument("--year", type=int)
    a = ap.parse_args()
    kabs = list(csv.DictReader(open(os.path.join(HERE, "input", "kabupaten.csv"), encoding="utf-8")))
    ranges = dict(poverty=(0, 60), hdi=(30, 95), expend=(2000, 30000))
    cols = {}
    for ind in ("poverty", "hdi", "expend"):
        p = getattr(a, ind)
        if not p:
            continue
        v = extract(p, kabs, a.year, getattr(a, "sheet_" + ind), ind)
        lo, hi = ranges[ind]
        bad = {i: x for i, x in v.items() if not (lo <= x <= hi)}
        if bad:
            print(f"[{ind}] peringatan: {len(bad)} nilai di luar rentang {lo}–{hi} (mis. {list(bad.items())[:3]}) — periksa satuan/pemisah desimal")
        cols[ind] = v
    if not cols:
        sys.exit("tidak ada berkas yang diberikan; lihat --help")
    old = {}
    if os.path.exists(OUT):
        old = {int(r["idx"]): r for r in csv.DictReader(open(OUT, encoding="utf-8"))}
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["idx", "name", "prov", "poverty", "hdi", "expend"])
        n_full = 0
        for k in kabs:
            i = int(k["idx"]); row = [i, k["name"], k["prov"]]
            for ind in ("poverty", "hdi", "expend"):
                v = cols.get(ind, {}).get(i)
                if v is None and i in old and old[i].get(ind):
                    v = old[i][ind]
                row.append("" if v is None else v)
            n_full += all(x != "" for x in row[3:])
            w.writerow(row)
    print(f"→ {OUT}: {len(kabs)} baris, {n_full} lengkap (kemiskinan+IPM+pengeluaran). Jalankan ulang keadilan.py + keadilan_inject.py.")


if __name__ == "__main__":
    main()
