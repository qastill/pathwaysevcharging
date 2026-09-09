"""🅿️ Parkir × Charger — pipeline (offline) untuk tab dashboard.

    pip install numpy openpyxl h3
    python3 parkir/access.py     # sekali, butuh cache Kontur -> parkir/input/access.json (sudah di-commit)
    python3 parkir/prepare.py    # -> parkir/parkir.js (payload, dimuat malas) + parkir/summary.json
    python3 parkir/inject.py     # -> pasang tab ke index.html

Tiga blok, meniru tiga produk Trust for Public Land (ParkServe / park priority areas / ParkScore)
dengan lahan parkir + charger sebagai objeknya:

  A. Akses 10 menit   — % penduduk ≤0,8 km (jalan kaki) dan ≤5 km (berkendara) dari SPKLU operasional,
                        per kabupaten/kota; heksagon prioritas = penduduk terbanyak di luar 10 menit jalan kaki.
  B. Perilaku parkir  — dari 101.020 sesi Jawa Barat (Mar 2026) + 56.740 sesi Jakarta Raya (1–8 Jun 2026):
                        durasi parkir (dwell), okupansi bay, perputaran, kWh per jam-bay, profil jam, per
                        kategori lahan parkir (transit · destinasi · kerja/publik · hunian · dealer).
  C. ChargeScore      — indeks ala ParkScore untuk 100 kabupaten/kota terpadat: 4 kategori, 8 ukuran,
                        poin per kuintil relatif terhadap 100 kota, dinormalkan ke 100.
"""
import csv, json, math, os, sys, datetime, collections

import h3
import numpy as np
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, HERE)
from venue import load_sites, CATS, JENIS_CAT, PARKING_CATS, venue_of, VENUE_CAT  # noqa: E402

JABAR = "Detail Transaksi SPKLU Jawa Barat - Maret 2026.csv"
JKT = "Detail Transaksi 08-06-2026 (1).xlsx"
DWELL_BINS = [15, 30, 60, 120, 240]          # menit
DWELL_LABELS = ["≤15 mnt", "15–30", "30–60", "1–2 jam", "2–4 jam", ">4 jam"]
TOP_SCORE = 100
CAT_IDS = [c["id"] for c in CATS]


def hav(lat1, lng1, lat2, lng2):
    R = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lng2 - lng1) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


# ============================================================================ A. situs + kabupaten
kabs = list(csv.DictReader(open("equitymap/input/kabupaten.csv", encoding="utf-8")))
kab6 = {r["h3"]: int(r["kab"]) for r in csv.DictReader(open("equitymap/input/hex_r6.csv"))}
prov_names = list(dict.fromkeys(k["prov"] for k in kabs))
prov_idx = {p: i for i, p in enumerate(prov_names)}
sites = load_sites()
byid = {s["id"]: s for s in sites}
H6 = list(kab6)
ll6 = np.array([h3.cell_to_latlng(h) for h in H6])
for s in sites:
    h = h3.latlng_to_cell(s["lat"], s["lng"], 6)
    k = kab6.get(h)
    if k is None:
        for n in h3.grid_disk(h, 3):
            if n in kab6:
                k = kab6[n]; break
    if k is None:
        k = kab6[H6[int(hav(s["lat"], s["lng"], ll6[:, 0], ll6[:, 1]).argmin())]]
    s["kab"] = k
access = json.load(open(os.path.join(HERE, "input", "access.json"), encoding="utf-8"))
acc_kab = {a["idx"]: a for a in access["kab"]}
print(f"situs {len(sites):,} · operasional {sum(s['active'] for s in sites):,} · kabupaten dengan akses terhitung {len(acc_kab)}")


# ============================================================================ B. transaksi
def dur_min(s):
    """'HH:MM:SS' -> menit; None bila tak terbaca."""
    try:
        h, m, sec = str(s).split(":")
        return int(h) * 60 + int(m) + int(sec) / 60
    except Exception:
        return None


def kw_of(s):
    try:
        return float(str(s).lower().replace("kw", "").replace(",", ".").strip())
    except Exception:
        return 0.0


def load_jabar():
    out = []
    for d in csv.DictReader(open(JABAR, encoding="utf-8-sig")):
        dm = dur_min(d["Durasi"])
        if dm is None or dm <= 0:
            continue
        try:
            kwh = float(d["Energi (kWh)"])
        except ValueError:
            continue
        t = d["Waktu Transaksi"]
        hh = int(t[11:13]); mm = int(t[14:16])
        out.append(dict(sid=d["ID SPKLU"].zfill(5), name=d["Nama SPKLU"], jenis=d["Jenis Titik Lokasi"],
                        cat=JENIS_CAT.get(d["Jenis Titik Lokasi"], "lainnya"), kw=kw_of(d["Daya Charger"]),
                        kwh=kwh, dur=dm, start=hh * 60 + mm, day=d["Tanggal"], kota=d["Kota/Kabupaten"]))
    return out


def load_jkt():
    wb = openpyxl.load_workbook(JKT, read_only=True)
    ws = wb.worksheets[0]
    it = ws.iter_rows(values_only=True, min_row=2)
    hdr = [str(c) for c in next(it)]
    out = []
    for r in it:
        d = dict(zip(hdr, r))
        dm = dur_min(d.get("durasi"))
        t = d.get("Tanggal")
        if dm is None or dm <= 0 or not isinstance(t, datetime.datetime) or d.get("kwh") is None:
            continue
        v = venue_of(d.get("Nama SPKLU"))
        out.append(dict(sid=str(d["IdSpklu"]).zfill(5), name=d["Nama SPKLU"], jenis=v, cat=VENUE_CAT[v],
                        kw=kw_of(d.get("Daya Charger")), kwh=float(d["kwh"]), dur=dm, start=t.hour * 60 + t.minute,
                        day=t.strftime("%Y-%m-%d"), kota=str(d.get("Pemda/Pemkot") or "")))
    return out


def stats(sess, days, key="cat"):
    """Statistik parkir per kelompok: dwell, okupansi bay, perputaran, kWh/jam-bay, histogram & profil jam."""
    groups = collections.defaultdict(list)
    for s in sess:
        groups[s[key]].append(s)
    out = {}
    for g, rows in groups.items():
        d = np.array([r["dur"] for r in rows]); kwh = np.array([r["kwh"] for r in rows])
        sids = set(r["sid"] for r in rows)
        # bay = charger pada situs (master); situs tanpa padanan master dihitung 1 bay
        bays = sum(max(byid[s]["ch"], 1) if s in byid else 1 for s in sids)
        bay_hours = float(d.sum()) / 60
        hist = np.histogram(d, bins=[0] + DWELL_BINS + [1e9])[0]
        prof = np.zeros(24)  # rata-rata bay terisi tiap jam (jumlah menit terisi di jam itu ÷ 60 ÷ hari ÷ bay)
        for r in rows:
            t0, t1 = r["start"], r["start"] + r["dur"]
            h = int(t0 // 60)
            while t0 < t1 and h < 48:
                edge = (h + 1) * 60
                prof[h % 24] += min(t1, edge) - t0
                t0 = edge; h += 1
        prof = prof / 60 / days / max(bays, 1)
        out[g] = dict(n=len(rows), sites=len(sids), bays=bays, kwh=round(float(kwh.sum())),
                      dwell_med=round(float(np.median(d)), 1), dwell_p25=round(float(np.percentile(d, 25)), 1),
                      dwell_p75=round(float(np.percentile(d, 75)), 1), dwell_mean=round(float(d.mean()), 1),
                      kwh_sess=round(float(kwh.mean()), 2), kw_eff=round(float(kwh.sum() / bay_hours), 1),
                      kw_rated=round(float(np.mean([r["kw"] for r in rows])), 1),
                      occ=round(100 * bay_hours / (bays * 24 * days), 1),
                      turnover=round(len(rows) / (bays * days), 2),
                      sess_site_day=round(len(rows) / (len(sids) * days), 2),
                      hist=[int(x) for x in hist], hist_pct=[round(100 * float(x) / len(rows), 1) for x in hist],
                      prof=[round(float(x) * 100, 2) for x in prof])
    return out


jb = load_jabar(); jk = load_jkt()
DAYS_JB, DAYS_JK = len(set(s["day"] for s in jb)), len(set(s["day"] for s in jk))
print(f"sesi Jawa Barat {len(jb):,} ({DAYS_JB} hari) · Jakarta Raya {len(jk):,} ({DAYS_JK} hari)")
cat_jb = stats(jb, DAYS_JB); cat_jk = stats(jk, DAYS_JK)
jenis_jb = stats(jb, DAYS_JB, key="jenis")
allst = stats(jb + jk, 1)  # hanya untuk histogram gabungan; okupansi tidak bermakna lintas jendela
# korelasi daya vs dwell (per sesi, Jawa Barat): kelas daya
pw = collections.defaultdict(list)
for s in jb:
    band = "≤7 kW" if s["kw"] <= 7.5 else "11–25 kW" if s["kw"] <= 25 else "30–60 kW" if s["kw"] <= 60 else "100–120 kW" if s["kw"] <= 120 else "≥150 kW"
    pw[band].append(s)
power = [dict(band=b, n=len(v), dwell_med=round(float(np.median([r["dur"] for r in v])), 1),
              kwh_sess=round(float(np.mean([r["kwh"] for r in v])), 1))
         for b, v in sorted(pw.items(), key=lambda kv: np.mean([r["kw"] for r in kv[1]]))]

# ============================================================================ C. kabupaten & ChargeScore
kab_rows = []
for i, k in enumerate(kabs):
    a = acc_kab.get(i)
    if not a:
        continue
    ss = [s for s in sites if s["kab"] == i]
    sa = [s for s in ss if s["active"]]
    pln = [s for s in ss if s["pln"]]
    ch = sum(s["ch"] for s in sa)
    cat_ch = {c: sum(s["ch"] for s in sa if s["cat"] == c) for c in CAT_IDS}
    kab_rows.append(dict(idx=i, name=k["name"], prov=prov_idx[k["prov"]], pop=a["pop"],
                         walk=a["walk"], drive=a["drive"], walk_park=a["walk_park"], drive_park=a["drive_park"],
                         drive_dc=a["drive_dc"], d_med=a["d_med"], prio_pop=a["prio_pop"],
                         sites=len(ss), active=len(sa), chargers=ch,
                         per100k=round(1e5 * ch / a["pop"], 2) if a["pop"] else 0,
                         kw100k=round(1e5 * sum(s["kw"] * s["ch"] for s in sa) / a["pop"], 1) if a["pop"] else 0,
                         avail=round(100 * sum(1 for s in pln if s["st"] in ("available", "inuse")) / len(pln), 1) if pln else None,
                         park_share=round(100 * sum(cat_ch[c] for c in PARKING_CATS) / ch, 1) if ch else None,
                         dc_share=round(100 * sum(1 for s in sa if s["kw"] >= 50) / len(sa), 1) if sa else None,
                         cat_ch=cat_ch))

# ChargeScore: 100 kabupaten/kota terpadat, poin 1–5 per kuintil relatif (padanan bracket ParkScore)
MEASURES = [  # (kunci, kategori, label, arah)
    ("walk", "akses", "% penduduk ≤0,8 km (10 mnt jalan kaki)", +1),
    ("drive", "akses", "% penduduk ≤5 km (10 mnt berkendara)", +1),
    ("per100k", "kapasitas", "charger operasional per 100 rb jiwa", +1),
    ("kw100k", "kapasitas", "kW terpasang per 100 rb jiwa", +1),
    ("avail", "ketersediaan", "% situs PLN berstatus available/inuse", +1),
    ("dc_share", "ketersediaan", "% situs DC ≥50 kW", +1),
    ("park_share", "parkir", "% charger di lahan parkir umum (transit·destinasi·kerja)", +1),
    ("walk_park", "parkir", "% penduduk ≤0,8 km dari charger di lahan parkir umum", +1),
]
top = sorted(kab_rows, key=lambda r: -r["pop"])[:TOP_SCORE]
for m, cat, lab, sgn in MEASURES:
    vals = np.array([r[m] if r[m] is not None else 0.0 for r in top], float)
    qs = np.quantile(vals, [0.2, 0.4, 0.6, 0.8])
    for r, v in zip(top, vals):
        pts = 1 + int(np.sum(v > qs))       # 1..5 (nilai terendah bracket 1)
        if v <= 0 and m in ("per100k", "kw100k", "walk", "walk_park"):
            pts = 1
        r.setdefault("pts", {})[m] = pts
CATSCORE = ["akses", "kapasitas", "ketersediaan", "parkir"]
for r in top:
    r["cat_pts"] = {c: sum(r["pts"][m] for m, cc, _, _ in MEASURES if cc == c) for c in CATSCORE}
    r["score"] = round(100 * sum(r["pts"].values()) / (5 * len(MEASURES)), 1)
top.sort(key=lambda r: -r["score"])
for rank, r in enumerate(top, 1):
    r["rank"] = rank

# ============================================================================ payload
nat = access["nat"]
nat.update(sites=len(sites), active=sum(s["active"] for s in sites),
           chargers=sum(s["ch"] for s in sites if s["active"]),
           cat_sites={c: sum(1 for s in sites if s["active"] and s["cat"] == c) for c in CAT_IDS},
           cat_ch={c: sum(s["ch"] for s in sites if s["active"] and s["cat"] == c) for c in CAT_IDS},
           venue_sites=collections.Counter(s["venue"] for s in sites if s["active"]).most_common())
payload = dict(
    meta=dict(walk_km=access["meta"]["walk_km"], drive_km=access["meta"]["drive_km"], top_prio=access["meta"]["top_prio"],
              days_jb=DAYS_JB, days_jk=DAYS_JK, n_jb=len(jb), n_jk=len(jk), dwell_labels=DWELL_LABELS,
              measures=[dict(k=m, cat=c, label=l) for m, c, l, _ in MEASURES], catscore=CATSCORE,
              sources=["Kontur Population 2023 (H3 res 8)", "Master SPKLU PLN 8 Jun 2026", "Rincian transaksi Jawa Barat Mar 2026",
                       "Rincian transaksi Jakarta Raya 1–8 Jun 2026", "geoBoundaries ADM2 (via equitymap/input)"]),
    cats=CATS, provs=prov_names,
    kabs=[dict(name=k["name"], prov=prov_idx[k["prov"]]) for k in kabs],
    sites=[[round(s["lat"], 4), round(s["lng"], 4), CAT_IDS.index(s["cat"]), s["venue"], 1 if s["active"] else 0,
            1 if s["pln"] else 0, s["ch"], s["kw"], s["name"][:60], s["kab"]] for s in sites],
    kab_stats=kab_rows, score=top, prio=access["prio"],
    venue=dict(jabar=cat_jb, jakarta=cat_jk, jenis=jenis_jb, power=power, all_hist=allst),
    nat=nat,
)
js = "window.PARKIR=" + json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + ";\n"
open(os.path.join(HERE, "parkir.js"), "w", encoding="utf-8").write(js)
json.dump(dict(nat=nat, score_top=top[:15], score_bottom=top[-10:], cat_jb=cat_jb, cat_jk=cat_jk, power=power,
               kab_best_walk=sorted(kab_rows, key=lambda r: -r["walk"])[:10],
               kab_prio=sorted(kab_rows, key=lambda r: -r["prio_pop"])[:10]),
          open(os.path.join(HERE, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"parkir.js: {len(js)/1024/1024:.2f} MB · kabupaten {len(kab_rows)} · ChargeScore {len(top)}")
for c in CAT_IDS:
    j = cat_jb.get(c)
    if j:
        print(f"  {c:<10} Jabar: sesi {j['n']:>6,} · dwell med {j['dwell_med']:>5} mnt · okupansi {j['occ']:>5}% · perputaran {j['turnover']} sesi/bay/hari · {j['kw_eff']} kW efektif")
print("ChargeScore teratas:", [(r['name'], r['score']) for r in top[:5]], "terbawah:", [(r['name'], r['score']) for r in top[-3:]])
