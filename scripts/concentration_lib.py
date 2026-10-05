"""Alat ukur konsentrasi yang dipakai bersama oleh skrip concentration_*_jabar.py."""
import numpy as np

RNG = np.random.default_rng(2026)
N_BOOT = 2000


def hhi(shares):
    s = np.asarray(shares, float); s = s[s > 0] / s.sum()
    return float(np.sum(s ** 2) * 10000)


def gini(v):
    v = np.sort(np.asarray(v, float)); n = len(v)
    if n == 0 or v.sum() == 0:
        return float("nan")
    return float((2 * np.sum((np.arange(1, n + 1)) * v) / (n * v.sum())) - (n + 1) / n)


def conc_stats(values):
    """HHI (0–10.000), ukuran efektif 1/HHI, rasio konsentrasi CR1/4/10, Gini — unit bernilai nol dibuang."""
    v = np.asarray(values, float); v = v[v > 0]
    s = np.sort(v)[::-1] / v.sum()
    h = hhi(s)
    return dict(n=int(len(v)), hhi=round(h, 1), n_effective=round(10000 / h, 2), cr1=round(float(s[:1].sum()), 4),
                cr4=round(float(s[:4].sum()), 4), cr10=round(float(s[:10].sum()), 4), gini=round(gini(v), 3))


def weighted_ranks(r, w):
    """Peringkat fraksional tertimbang pada [0,1]; unit dengan r sama memakai rata-rata tertimbang peringkatnya."""
    r, w = np.asarray(r, float), np.asarray(w, float)
    o = np.argsort(r, kind="stable"); rs = r[o]; ws = w[o]
    cum = np.cumsum(ws) / ws.sum()
    mid = cum - ws / ws.sum() / 2
    out = np.empty_like(mid)
    i = 0
    while i < len(rs):
        j = i
        while j + 1 < len(rs) and rs[j + 1] == rs[i]:
            j += 1
        out[i:j + 1] = np.average(mid[i:j + 1], weights=ws[i:j + 1]); i = j + 1
    res = np.empty_like(out); res[o] = out
    return res


def ci(h, r, w):
    """Indeks konsentrasi Wagstaff/Kakwani tertimbang: C = 2·cov_w(h/w, rank_w) / mean_w(h/w).
    h = pasokan per unit (total), r = variabel peringkat (rendah → tinggi), w = penduduk. C>0: menumpuk di r tinggi."""
    h, r, w = (np.asarray(x, float) for x in (h, r, w))
    if h.sum() <= 0:
        return float("nan")
    R = weighted_ranks(r, w)
    pc = h / w
    mu = np.sum(w * pc) / w.sum()
    cov = np.sum(w * (pc - mu) * (R - np.sum(w * R) / w.sum())) / w.sum()
    return float(2 * cov / mu)


def ci_boot(h, r, w, n_boot=N_BOOT):
    h, r, w = (np.asarray(x, float) for x in (h, r, w))
    est = ci(h, r, w); n = len(h); b = []
    for _ in range(n_boot):
        ix = RNG.integers(0, n, n)
        if len(np.unique(r[ix])) < 3 or h[ix].sum() <= 0:
            continue
        b.append(ci(h[ix], r[ix], w[ix]))
    lo, hi = np.percentile(b, [2.5, 97.5])
    return dict(ci=round(est, 3), lo=round(float(lo), 3), hi=round(float(hi), 3), signif=bool(lo > 0 or hi < 0))


def curve(h, r, w, npts=40):
    """Titik kurva konsentrasi (porsi kumulatif penduduk, porsi kumulatif pasokan), diurut menurut r."""
    o = np.argsort(np.asarray(r, float), kind="stable")
    w, h = np.asarray(w, float)[o], np.asarray(h, float)[o]
    cp = np.concatenate([[0], np.cumsum(w) / w.sum()]); cv = np.concatenate([[0], np.cumsum(h) / max(h.sum(), 1e-9)])
    step = max(1, len(cp) // npts)
    pts = [[round(float(a), 4), round(float(b), 4)] for a, b in zip(cp[::step], cv[::step])]
    if pts[-1] != [1.0, 1.0]:
        pts.append([1.0, 1.0])
    return pts


def erreygers(ind, r, w, a=0.0, b=1.0):
    """Indeks konsentrasi Erreygers (2009) untuk variabel terbatas [a, b], mis. indikator 0/1 "kecamatan punya charger"
    atau "kecamatan kekurangan". E = 8·cov_w(ind, R)/(b − a) = 4·mean_w(ind)·C/(b − a). Tanda: E>0 menumpuk di
    peringkat tinggi; untuk variabel KEKURANGAN, E<0 berarti kekurangan menumpuk di wilayah kurang maju."""
    ind, r, w = (np.asarray(x, float) for x in (ind, r, w))
    R = weighted_ranks(r, w)
    W = w.sum(); mu = np.sum(w * ind) / W; mR = np.sum(w * R) / W
    cov = np.sum(w * (ind - mu) * (R - mR)) / W
    return float(8 * cov / (b - a))


def erreygers_boot(ind, r, w, n_boot=N_BOOT, a=0.0, b=1.0):
    ind, r, w = (np.asarray(x, float) for x in (ind, r, w))
    est = erreygers(ind, r, w, a, b); n = len(ind); out = []
    for _ in range(n_boot):
        ix = RNG.integers(0, n, n)
        if len(np.unique(r[ix])) < 3:
            continue
        out.append(erreygers(ind[ix], r[ix], w[ix], a, b))
    lo, hi = np.percentile(out, [2.5, 97.5])
    return dict(e=round(est, 3), lo=round(float(lo), 3), hi=round(float(hi), 3), signif=bool(lo > 0 or hi < 0))
