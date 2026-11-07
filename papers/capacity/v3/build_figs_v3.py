"""Figur v3 untuk naskah & slide "Capacity maps as an equity instrument".

Membaca papers/capacity/capacity.json (prepare.py) dan papers/capacity/v3/strengthen.json (strengthen.py).
Jalankan dari akar repositori:  python3 papers/capacity/v3/build_figs_v3.py
Keluaran: papers/capacity/v3/figs/fig*.png  (fig3 & fig10 disalin dari v2)
"""
import json, math, os, statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
from matplotlib.colors import LogNorm

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
D = json.load(open(os.path.join(ROOT, "papers/capacity/capacity.json")))
S = json.load(open(os.path.join(ROOT, "papers/capacity/v3/strengthen.json")))
B = S["base"]
OUT = os.path.join(ROOT, "papers/capacity/v3/figs/")
os.makedirs(OUT, exist_ok=True)
import shutil
for src, dst in (("fig2_quadrant.png", "fig3_quadrant.png"), ("fig4_readiness.png", "fig10_readiness.png")):
    shutil.copyfile(os.path.join(ROOT, "papers/capacity/v2", src), OUT + dst)

INK, MUTED, GRID = "#1B2A3A", "#6B7785", "#D5DAE0"
TEAL, CORAL, AMBER, NEUTRAL, BASEC = "#0F7C6E", "#D1495B", "#E0A526", "#B8BEC6", "#EEF1F4"
RULES = [("headroom", "Headroom-only", CORAL), ("demand", "Demand-only", AMBER), ("dwh", "Demand within\nheadroom", TEAL)]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlecolor": INK})
DEG = D["meta"]["cell_deg"]
FEAS = D["meta"]["feasible"]
cells = D["cells"]  # lat, lon, h, hraw, kva, n, gi, ev, chg, kwh, q, kab
lats = [c[0] for c in cells]; lons = [c[1] for c in cells]
XL, YL = (min(lons) - 0.06, max(lons) + 0.06), (min(lats) - 0.06, max(lats) + 0.06)


def clean_map(ax):
    ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def tile(ax, lat, lon, **kw):
    ax.add_patch(Rectangle((lon - DEG / 2, lat - DEG / 2), DEG, DEG, **kw))


def save(fig, name):
    fig.savefig(OUT + name, facecolor="white", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


# ---------------------------------------------------------------- Fig 1: dua permukaan
fig, axes = plt.subplots(1, 3, figsize=(15, 4.9), dpi=200)
cm_h = plt.get_cmap("GnBu"); cm_d = plt.get_cmap("YlOrBr")
for c in cells:
    if c[2] > 0:
        tile(axes[0], c[0], c[1], facecolor=cm_h(0.12 + 0.85 * min(c[2] / 30000.0, 1)), edgecolor="white", lw=0.25)
    else:
        tile(axes[0], c[0], c[1], facecolor=BASEC, edgecolor="white", lw=0.25)
    tile(axes[1], c[0], c[1], facecolor=BASEC, edgecolor="white", lw=0.25)
    tile(axes[2], c[0], c[1], facecolor=BASEC, edgecolor="white", lw=0.25)
dn = LogNorm(1, 120)
for c in cells:
    if c[7] > 0:
        tile(axes[1], c[0], c[1], facecolor=cm_d(0.2 + 0.78 * dn(min(c[7], 120))), edgecolor="white", lw=0.25)
for c in cells:
    if c[7] > 0 and c[8] == 0:
        tile(axes[2], c[0], c[1], facecolor="#F6D5DA", edgecolor="white", lw=0.25)
gap = [c for c in cells if c[10] == "HL" and c[8] == 0]
for c in gap:
    tile(axes[2], c[0], c[1], facecolor="none", edgecolor=CORAL, hatch="////", lw=0.9)
S_ = D["sites"]
axes[2].scatter([s["lon"] for s in S_], [s["lat"] for s in S_], s=[6 + math.sqrt(s["kwh"]) / 30 for s in S_],
                color=INK, edgecolor="white", lw=0.3, zorder=3)
titles = ["a  Network headroom (DSO)", "b  Charging demand (EV owners)", "c  Where they meet"]
subs = [f"2026-adjusted transformer headroom per 5 km cell", f"{D['meta']['ev']:,} geocoded owners, log scale",
        "chargers (dots), unserved owner cells (pink),\nhigh-demand / low-headroom gaps (hatched)"]
for ax, t, s in zip(axes, titles, subs):
    clean_map(ax)
    ax.set_title(t, loc="left", fontsize=12)
    ax.text(0.0, 0.99, s, transform=ax.transAxes, fontsize=8.5, color=MUTED, va="top")
sm = plt.cm.ScalarMappable(cmap=cm_h, norm=plt.Normalize(0, 30)); sm.set_array([])
cb = fig.colorbar(sm, cax=axes[0].inset_axes([0.05, 0.02, 0.5, 0.035]), orientation="horizontal")
cb.set_label("MVA per cell (capped at 30)", fontsize=8); cb.outline.set_visible(False)
sm2 = plt.cm.ScalarMappable(cmap=cm_d, norm=LogNorm(1, 120)); sm2.set_array([])
cb2 = fig.colorbar(sm2, cax=axes[1].inset_axes([0.05, 0.02, 0.5, 0.035]), orientation="horizontal")
cb2.set_label("registered EV owners per cell", fontsize=8); cb2.outline.set_visible(False)
axes[2].legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor=INK, markersize=6, label="public charger site"),
                        Patch(facecolor="#F6D5DA", label="owners, no charger"),
                        Patch(facecolor="none", edgecolor=CORAL, hatch="////", label="high demand, low headroom, no charger")],
               loc="lower left", bbox_to_anchor=(0.0, -0.02), ncol=1, fontsize=7.5, frameon=False)
fig.subplots_adjust(wspace=0.04)
save(fig, "fig1_two_surfaces.png")

# ---------------------------------------------------------------- Fig 2: kepadatan, bukan ruang sisa
f1 = B["f1"]
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13, 3.9), dpi=200, gridspec_kw={"width_ratios": [1.7, 1, 1]})
items = [("Installed transformer kVA", f1["auc"]["kva"], INK), ("Number of transformers", f1["auc"]["ntr"], INK),
         ("Absolute headroom (kVA)", f1["auc"]["abs"], INK), ("Registered EV owners", f1["auc"]["ev"], AMBER),
         ("Relative headroom (% of kVA)", f1["auc"]["rel"], CORAL)]
y = list(range(len(items)))[::-1]
a1.barh(y, [i[1] - 0.5 for i in items], left=0.5, color=[i[2] for i in items], height=0.6, zorder=3)
a1.axvline(0.5, color=MUTED, lw=1, ls="--")
a1.text(0.49, -0.75, "coin toss", color=MUTED, fontsize=8, ha="right")
for yi, it in zip(y, items):
    a1.text(max(it[1], 0.5) + 0.01, yi, f"{it[1]:.2f}", va="center", fontsize=9, fontweight="bold", color=INK)
a1.set_yticks(y); a1.set_yticklabels([i[0] for i in items], fontsize=9)
a1.set_xlim(0.35, 1.0); a1.tick_params(axis="y", length=0)
a1.set_xlabel("AUC: how well the variable separates cells with a charger from cells without")
for s in ("top", "right", "left"): a1.spines[s].set_visible(False)
a1.set_title(f"a  What predicts a charger? ({f1['n_pos']} cells with vs {f1['n_neg']:,} without)", loc="left", fontsize=10.5)
mk, mr = f1["med_kva"], f1["med_rel"]
a2.bar([0, 1], [mk["chg"], mk["nochg"]], color=[INK, NEUTRAL], width=0.6, zorder=3)
for i, v in enumerate([mk["chg"], mk["nochg"]]):
    a2.text(i, v * 1.02, f"{v:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
a2.set_xticks([0, 1]); a2.set_xticklabels(["with\ncharger", "without\ncharger"], fontsize=9)
a2.set_yticks([]); a2.set_ylim(0, mk["chg"] * 1.25)
a2.set_title(f"b  Median installed kVA\n    ({mk['chg'] / mk['nochg']:.0f}× higher)", loc="left", fontsize=10.5)
a3.bar([0, 1], [100 * mr["chg"], 100 * mr["nochg"]], color=[CORAL, NEUTRAL], width=0.6, zorder=3)
for i, v in enumerate([mr["chg"], mr["nochg"]]):
    a3.text(i, 100 * v + 0.8, f"{100 * v:.1f} %", ha="center", va="bottom", fontsize=9, fontweight="bold")
a3.set_xticks([0, 1]); a3.set_xticklabels(["with\ncharger", "without\ncharger"], fontsize=9)
a3.set_yticks([]); a3.set_ylim(0, 45)
a3.set_title("c  Median spare capacity\n    (% of installed kVA)", loc="left", fontsize=10.5)
for ax in (a2, a3):
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.tick_params(axis="x", length=0)
fig.tight_layout(w_pad=2.5)
save(fig, "fig2_density_not_capacity.png")

# ---------------------------------------------------------------- Fig 4: peta penempatan per aturan
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), dpi=200)
medp = B["med_pool"]
for ax, (k, lab, col) in zip(axes, RULES):
    for c in cells:
        tile(ax, c[0], c[1], facecolor=BASEC, edgecolor="white", lw=0.25)
    ax.scatter([s["lon"] for s in S_], [s["lat"] for s in S_], s=4, color=MUTED, alpha=0.6, zorder=2, lw=0)
    sel = B["rules"][k]["sel"]
    ok = [s for s in sel if s[2] >= medp and s[3] >= FEAS]
    st = [s for s in sel if s[2] < medp]
    inf = [s for s in sel if s[3] < FEAS]
    ax.scatter([s[1] for s in ok], [s[0] for s in ok], s=[20 + 6 * math.sqrt(s[2]) for s in ok], color=col,
               edgecolor="white", lw=0.6, zorder=4)
    ax.scatter([s[1] for s in st], [s[0] for s in st], s=34, facecolor="white", edgecolor=col, lw=1.4, zorder=4)
    ax.scatter([s[1] for s in inf], [s[0] for s in inf], s=60, marker="X", color=INK, zorder=5)
    r = B["rules"][k]
    clean_map(ax)
    ax.set_title(f"{lab.replace(chr(10), ' ')}", loc="left", fontsize=12, color=col)
    ax.text(0.0, 0.99, f"{r['owners']} owners reached · {r['stranded']} stranded · {r['infeas']} infeasible",
            transform=ax.transAxes, fontsize=9, color=INK, va="top")
axes[1].legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor=NEUTRAL, markeredgecolor=INK, markersize=8, label="new site (size = owners in cell)"),
                        Line2D([0], [0], marker="o", color="w", markerfacecolor="white", markeredgecolor=INK, markersize=7, label="stranded: below-median demand"),
                        Line2D([0], [0], marker="X", color="w", markerfacecolor=INK, markersize=9, label=f"infeasible: < {FEAS:.0f} kVA headroom"),
                        Line2D([0], [0], marker="o", color="w", markerfacecolor=MUTED, markersize=4, label="existing charger")],
               loc="lower center", bbox_to_anchor=(0.5, -0.17), ncol=4, fontsize=8.5, frameon=False)
fig.subplots_adjust(wspace=0.03)
save(fig, "fig4_site_maps.png")

# ---------------------------------------------------------------- Fig 5: hasil aturan vs acak
R = B["rules"]; RD = B["random"]
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8), dpi=200)
for ax, (key, title, rmean) in zip(axes, [("owners", "EV owners newly reached", RD["owners_mean"]),
                                          ("stranded", "Stranded sites\n(below-median demand)", RD["stranded_mean"]),
                                          ("infeas", f"Infeasible sites\n(< {FEAS:.0f} kVA headroom)", RD["infeas_mean"])]):
    vals = [R[k][key] for k, _, _ in RULES]
    bars = ax.bar(range(3), vals, color=[c for _, _, c in RULES], width=0.62, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + max(vals + [rmean]) * 0.02, f"{v}", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=INK)
    ax.axhline(rmean, color=MUTED, ls="--", lw=1, zorder=2)
    ax.text(-0.45, rmean * 1.02 + max(vals + [rmean]) * 0.01, f"random 50 sites: {rmean:.0f}" if key == "owners" else f"random 50 sites: {rmean:.1f}",
            color=MUTED, fontsize=8, va="bottom", ha="left", bbox=dict(facecolor="white", edgecolor="none", pad=1), zorder=4)
    ax.set_title(title, loc="left", fontsize=10.5)
    ax.set_xticks(range(3)); ax.set_xticklabels([l for _, l, _ in RULES], fontsize=8.5)
    ax.tick_params(axis="x", length=0); ax.set_yticks([])
    ax.set_ylim(0, max(vals + [rmean]) * 1.22)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
fig.tight_layout(w_pad=2.5)
save(fig, "fig5_rule_outcomes.png")

# ---------------------------------------------------------------- Fig 6: ekuitas pendapatan
regs = B["regencies"]
ranked = sorted(regs, key=lambda r: r["exp"])
terc_owners = [sum(r["owners"] for r in ranked[i * 9:(i + 1) * 9]) for i in range(3)]
scen = [("Today", B["baseline"]["terc"], NEUTRAL)] + [(lab.replace("\n", " "), R[k]["terc"], col) for k, lab, col in RULES]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.2), dpi=200, gridspec_kw={"width_ratios": [1.7, 1]})
w = 0.2
groups = [f"Poorest third\n({terc_owners[0]} owners)", f"Middle third\n({terc_owners[1]:,} owners)",
          f"Richest third\n({terc_owners[2]:,} owners)"]
for i, (lab, vals, col) in enumerate(scen):
    xs = [g + (i - 1.5) * w for g in range(3)]
    a1.bar(xs, vals, w * 0.92, color=col, label=lab, zorder=3)
    for x, v in zip(xs, vals):
        a1.text(x, v + 1, f"{v:.0f}", ha="center", va="bottom", fontsize=7.5, color=INK)
a1.set_xticks(range(3)); a1.set_xticklabels(groups, fontsize=9); a1.tick_params(axis="x", length=0)
a1.set_ylim(0, 112); a1.set_yticks([0, 25, 50, 75, 100]); a1.set_ylabel("% of owners living in a cell with a charger")
a1.grid(axis="y", color=GRID, lw=0.6, zorder=0)
for s in ("top", "right"): a1.spines[s].set_visible(False)
a1.legend(fontsize=8, frameon=False, ncol=4, loc="upper left", bbox_to_anchor=(0, 1.12))
a1.set_title("a  Coverage by regency per-capita expenditure", loc="left", fontsize=10.5, pad=24)
gain_poor = [v[0] - B["baseline"]["terc"][0] for _, v, _ in scen[1:]]
gain_rich = [v[2] - B["baseline"]["terc"][2] for _, v, _ in scen[1:]]
yy = [2, 1, 0]
a2.barh([y + 0.18 for y in yy], gain_poor, 0.34, color=[c for _, _, c in scen[1:]], zorder=3, label="poorest third")
a2.barh([y - 0.18 for y in yy], gain_rich, 0.34, color=[c for _, _, c in scen[1:]], alpha=0.35, zorder=3, label="richest third")
for y, gp, gr in zip(yy, gain_poor, gain_rich):
    a2.text(gp + 0.4, y + 0.18, f"+{gp:.1f} poorest", va="center", fontsize=8.5, fontweight="bold")
    a2.text(gr + 0.4, y - 0.18, f"+{gr:.1f} richest", va="center", fontsize=8.5, color=MUTED)
a2.set_yticks(yy); a2.set_yticklabels([t[0] for t in scen[1:]], fontsize=9); a2.tick_params(axis="y", length=0)
a2.set_xlim(0, 36); a2.set_xticks([])
for s in ("top", "right", "bottom"): a2.spines[s].set_visible(False)
a2.set_title("b  Coverage gain, percentage points", loc="left", fontsize=10.5, pad=24)
fig.tight_layout(w_pad=3)
save(fig, "fig6_income_equity.png")

# ---------------------------------------------------------------- Fig 7: baseline acak
fig, ax = plt.subplots(figsize=(8.5, 3.6), dpi=200)
ax.hist(RD["owners"], bins=40, color=NEUTRAL, edgecolor="white", zorder=2)
ymax = ax.get_ylim()[1]
for k, lab, col in RULES:
    v = R[k]["owners"]
    ax.axvline(v, color=col, lw=2.2, zorder=3)
    ax.text(v, ymax * (0.95 if k != "dwh" else 0.78), f"{lab.replace(chr(10), ' ')}\n{v}", color=col, fontsize=8.5,
            ha="right" if k == "dwh" else "left", va="top", fontweight="bold")
ax.axvline(RD["owners_mean"], color=MUTED, ls="--", lw=1)
ax.text(RD["owners_mean"], ymax * 0.98, f"random mean\n{RD['owners_mean']:.0f}", color=MUTED, fontsize=8.5, ha="center", va="top")
ax.set_xlim(80, 900)
ax.set_xlabel(f"EV owners reached by 50 sites placed at random in the same {B['pool']} cells ({RD['n']:,} draws)")
ax.set_yticks([])
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
fig.tight_layout()
save(fig, "fig7_random_baseline.png")

# ---------------------------------------------------------------- Fig 8: uji ketahanan
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(14, 4.0), dpi=200)
NS = B["nsweep"]
for k, lab, col in RULES:
    a1.plot([r["N"] for r in NS], [r[k]["owners"] for r in NS], color=col, lw=2.2, label=lab.replace("\n", " "))
a1.axvline(50, color=MUTED, ls=":", lw=1); a1.text(52, 230, "50 sites", color=MUTED, fontsize=8)
a1.set_xlabel("Number of new sites"); a1.set_ylabel("EV owners reached")
a1.legend(fontsize=8, frameon=False, loc="lower right")
a1.set_title("a  Portfolio size", loc="left", fontsize=10.5)
FS = B["feas"]
xs = list(range(len(FS)))
for k, lab, col in RULES:
    a2.plot(xs, [r[k]["owners"] for r in FS], color=col, lw=2.2, marker="o")
for x, r in zip(xs, FS):
    a2.text(x, r["demand"]["owners"] + 12, f"{r['demand']['infeas']} infeasible", color=AMBER, fontsize=8, ha="center")
a2.set_xticks(xs); a2.set_xticklabels([f"{r['kva']} kVA" for r in FS], fontsize=8.5)
a2.set_ylim(600, 880); a2.set_ylabel("EV owners reached (50 sites)")
a2.set_xlabel("Feasibility threshold (site size)")
a2.set_title("b  Feasibility threshold", loc="left", fontsize=10.5)
V = S["variants"]
lab3 = [f"{v['cell']:.3f}°\n(≈{v['cell'] * 111:.0f} km)" for v in V]
gain = [100 * (v["rules_prop"]["dwh"]["owners"] / v["rules_prop"]["headroom"]["owners"] - 1) for v in V]
gd = [100 * (v["rules_prop"]["demand"]["owners"] / v["rules_prop"]["headroom"]["owners"] - 1) for v in V]
x3 = list(range(len(V)))
a3.bar([x - 0.18 for x in x3], gd, 0.34, color=AMBER, zorder=3, label="Demand-only")
a3.bar([x + 0.18 for x in x3], gain, 0.34, color=TEAL, zorder=3, label="Demand within headroom")
for x, g1, g2, v in zip(x3, gd, gain, V):
    a3.text(x - 0.18, g1 + 1, f"+{g1:.0f}%", ha="center", fontsize=7.5)
    a3.text(x + 0.18, g2 + 1, f"+{g2:.0f}%", ha="center", fontsize=7.5, fontweight="bold")
    a3.text(x - 0.18, -6, f"{v['rules_prop']['demand']['infeas']} inf.", ha="center", fontsize=7, color=AMBER)
a3.set_xticks(x3); a3.set_xticklabels(lab3, fontsize=8); a3.tick_params(axis="x", length=0)
a3.axhline(0, color=MUTED, lw=0.8)
a3.set_ylim(-9, 50); a3.set_yticks([])
a3.set_title("c  Owners reached vs headroom-only,\n    by cell size (N = 38 % of pool)", loc="left", fontsize=10.5)
a3.legend(fontsize=7.5, frameon=False, loc="upper left")
for ax in (a1, a2, a3):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
a3.spines["left"].set_visible(False)
fig.tight_layout(w_pad=2.5)
save(fig, "fig8_robustness.png")

# ---------------------------------------------------------------- Fig 9: dua tingkat
T = B["two"]
fig, ax = plt.subplots(figsize=(6.4, 5.0), dpi=200)
xs = [max(p[0] / 1000, 0.01) for p in T["pts"]]; ys = [max(p[1], 0.1) for p in T["pts"]]
ax.scatter(xs, ys, s=[14 + math.sqrt(p[2]) / 30 for p in T["pts"]], color=TEAL, edgecolor="white", lw=0.4, alpha=0.85, zorder=3)
mx, my = statistics.median(xs), statistics.median(ys)
ax.axvline(mx, color=MUTED, ls="--", lw=0.8); ax.axhline(my, color=MUTED, ls="--", lw=0.8)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Transformer headroom in cell (MVA, log)"); ax.set_ylabel("Supplying primary substation headroom (MVA, log)")
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.text(0.02, 0.98, f"tight transformer,\nample substation: {T['tight_tr_ample_gi']}", transform=ax.transAxes, fontsize=8.5, va="top", color=CORAL, fontweight="bold")
ax.text(0.98, 0.04, f"ample transformer,\ntight substation: {T['ample_tr_tight_gi']}", transform=ax.transAxes, fontsize=8.5, ha="right", color=CORAL, fontweight="bold")
ax.set_title(f"Spearman ρ = {T['rho']:+.2f}  (95 % CI {T['rho_ci'][0]:+.2f} to {T['rho_ci'][1]:+.2f}),  n = {T['n']}", loc="left", fontsize=10)
fig.tight_layout()
save(fig, "fig9_two_levels.png")
print("ok:", sorted(os.listdir(OUT)))
