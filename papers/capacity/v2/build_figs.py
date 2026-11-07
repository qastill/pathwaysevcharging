import json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

D = json.load(open("papers/capacity/capacity.json"))
OUT = "papers/capacity/v2/"
INK, MUTED, GRID = "#1B2A3A", "#6B7785", "#D5DAE0"
TEAL, CORAL, AMBER, NEUTRAL = "#0F7C6E", "#D1495B", "#E0A526", "#B8BEC6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
DEG = D["meta"]["cell_deg"]
cells = D["cells"]  # lat, lon, h(kVA), hraw, kva, n, gi, ev, chg, kwh, q, kab
MED_EV, MED_H = D["med"]["ev"], D["med"]["h"]
FEAS = D["meta"]["feasible"]

# ---------- Fig 1: headroom map
fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=220)
hmax = max(c[2] for c in cells)
cmap = plt.get_cmap("GnBu")
for lat, lon, h, hraw, kva, n, gi, ev, chg, kwh, q, kab in cells:
    if h <= 0: continue
    col = cmap(0.12 + 0.8 * min(h / 30000.0, 1.0))
    ax.add_patch(Rectangle((lon - DEG/2, lat - DEG/2), DEG, DEG, facecolor=col, edgecolor="white", lw=0.3, zorder=1))
gap = [c for c in cells if c[10] == "HL" and c[8] == 0]
for lat, lon, *_ in gap:
    ax.add_patch(Rectangle((lon - DEG/2, lat - DEG/2), DEG, DEG, facecolor="none", edgecolor=CORAL, hatch="////", lw=0.8, zorder=2))
sites = D["sites"]
ax.scatter([s["lon"] for s in sites], [s["lat"] for s in sites],
           s=[8 + math.sqrt(s["kwh"]) / 25 for s in sites], color=INK, edgecolor="white", lw=0.4, zorder=3, alpha=0.9)
lats = [c[0] for c in cells if c[2] > 0]; lons = [c[1] for c in cells if c[2] > 0]
ax.set_xlim(min(lons) - 0.05, max(lons) + 0.05); ax.set_ylim(min(lats) - 0.05, max(lats) + 0.05)
ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(False)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 30)); sm.set_array([])
cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02, shrink=0.6)
cb.set_label("2026-adjusted transformer headroom per 5 km cell (MVA, capped at 30)", fontsize=8, color=INK)
cb.outline.set_visible(False)
ax.legend(handles=[Line2D([0],[0], marker="o", color="w", markerfacecolor=INK, markersize=6, label="public charger site (size = 2026 energy)"),
                   Rectangle((0,0),1,1, facecolor="none", edgecolor=CORAL, hatch="////", label="unserved: owners above median, headroom below median")],
          loc="lower left", fontsize=7.5, frameon=True, framealpha=0.95, edgecolor=GRID)
fig.tight_layout(); fig.savefig(OUT + "fig1_headroom_map.png", facecolor="white"); plt.close(fig)

# ---------- Fig 2: quadrant
fig, ax = plt.subplots(figsize=(6.2, 5.0), dpi=220)
pts = [c for c in cells if c[7] > 0]
xs = [max(c[2] / 1000.0, 0.01) for c in pts]; ys = [c[7] for c in pts]
ax.scatter(xs, ys, s=[14 + math.sqrt(c[9]) / 30 if c[8] else 12 for c in pts],
           color=[TEAL if c[8] else NEUTRAL for c in pts], edgecolor="white", lw=0.4, alpha=0.9, zorder=3)
ax.axvline(MED_H / 1000.0, color=MUTED, ls="--", lw=0.8); ax.axhline(MED_EV, color=MUTED, ls="--", lw=0.8)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Cell headroom at 80 % limit, 2026-adjusted (MVA, log)")
ax.set_ylabel("Registered EV owners in cell (log)")
for s in ("top", "right"): ax.spines[s].set_visible(False)
q = D["quad"]
def lab(x, y, t, c, ha="left"): ax.text(x, y, t, color=c, fontsize=8, ha=ha, va="top", fontweight="bold")
lab(0.012, 420, f"HIGH DEMAND · LOW HEADROOM\n{q['HL']['evp']:.1f} % of owners · {q['HL']['chgp']:.1f} % of chargers\n{D['gap']['cells']} cells unserved ({D['gap']['ev']} owners)", CORAL)
lab(3.3, 420, f"HIGH DEMAND · HIGH HEADROOM\n{q['HH']['evp']:.1f} % of owners · {q['HH']['chgp']:.1f} % of chargers", INK)
ax.text(3.3, 1.45, f"LOW DEMAND · HIGH HEADROOM\n{q['LH']['evp']:.1f} % of owners · {q['LH']['chgp']:.1f} % of chargers", color=MUTED, fontsize=7.5, va="top")
ax.text(0.012, 1.45, f"LOW · LOW\n{q['LL']['evp']:.1f} % of owners · {q['LL']['chgp']:.1f} % of chargers", color=MUTED, fontsize=7.5, va="top")
ax.legend(handles=[Line2D([0],[0], marker="o", color="w", markerfacecolor=TEAL, markersize=6, label="has public charger"),
                   Line2D([0],[0], marker="o", color="w", markerfacecolor=NEUTRAL, markersize=6, label="no public charger")],
          loc="center left", fontsize=7.5, frameon=False, bbox_to_anchor=(0.0, 0.42))
fig.tight_layout(); fig.savefig(OUT + "fig2_quadrant.png", facecolor="white"); plt.close(fig)

# ---------- Fig 3: siting rules (four panels)
R = {r["key"]: r for r in D["rules"]}
order = [("headroom", "Headroom-only", CORAL), ("demand", "Demand-only", AMBER), ("dwh", "Demand within\nheadroom", TEAL)]
fig, axes = plt.subplots(1, 4, figsize=(11.5, 3.6), dpi=220)
panels = [("owners", "EV owners newly reached\n(50 new sites)", None),
          ("stranded", "Sites in below-median-\ndemand cells (stranded)", None),
          ("infeas", f"Sites below {FEAS:.0f} kVA\nfeasibility threshold", None),
          ("gini", "Between-regency Gini\n(lower = more even)", D["baseline"]["gini"])]
for ax, (k, title, base) in zip(axes, panels):
    vals = [R[o[0]][k] for o in order]
    bars = ax.bar(range(3), vals, color=[o[2] for o in order], width=0.62, zorder=3)
    for b, v in zip(bars, vals):
        fmt = f"{v:.3f}" if k == "gini" else f"{v:d}"
        ax.text(b.get_x() + b.get_width()/2, v * 1.01 + (0.004 if k == "gini" else 0), fmt, ha="center", va="bottom", fontsize=9, color=INK, fontweight="bold")
    if base is not None:
        ax.axhline(base, color=MUTED, ls="--", lw=0.8, zorder=2)
        ax.text(2.45, base, f"today {base:.3f}", color=MUTED, fontsize=7.5, va="bottom", ha="right")
    ax.set_title(title, fontsize=9, loc="left", color=INK)
    ax.set_xticks(range(3)); ax.set_xticklabels([o[1] for o in order], fontsize=7.5)
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, max(vals) * 1.18 if k != "gini" else 0.6)
    ax.set_yticks([]); 
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.grid(False)
fig.tight_layout(w_pad=2.0); fig.savefig(OUT + "fig3_rules.png", facecolor="white"); plt.close(fig)

# ---------- Fig 4: readiness + growth (two panels)
A = D["audit"]
checks = [("Not linked to a primary substation (GI)", A["gi"], CORAL),
          ("Survey vs asset-register coordinates > 1 km apart", A["koord"], CORAL),
          ("Load measurement missing", A["beban"], CORAL),
          ("Rated capacity missing", A["kva"], CORAL),
          ("Coordinates missing or not VALID", A["geo"], NEUTRAL),
          ("Field-staff names recorded (must be removed)", A["pii"], CORAL)]
checks = sorted(checks, key=lambda t: t[1])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 3.9), dpi=220, gridspec_kw={"width_ratios": [1.35, 1]})
a1.barh([c[0] for c in checks], [c[1] for c in checks], color=[c[2] for c in checks], height=0.6, zorder=3)
for i, c in enumerate(checks):
    a1.text(c[1] + 1, i, f"{c[1]:.1f} %", va="center", fontsize=8.5, color=INK)
a1.set_xlim(0, 100); a1.set_xticks([]); a1.tick_params(axis="y", length=0, labelsize=8)
for s in ("top", "right", "bottom"): a1.spines[s].set_visible(False)
a1.set_title(f"Share of {D['meta']['total']:,} transformer records failing each check", fontsize=9, loc="left", color=INK)
sc = D["scen"]
labels = ["As measured\n(Apr 2020–2024)", "+3.0 %/yr\n(DSO sales)", "+5.9 %/yr\n(capacity growth)", "+9.7 %/yr\n(upper bound)"]
x = range(4); w = 0.38
tr = [round(s["trafo"]) for s in sc]; gi = [round(s["gi"]) for s in sc]
b1 = a2.bar([i - w/2 for i in x], tr, w, color=INK, label="Distribution transformers", zorder=3)
b2 = a2.bar([i + w/2 for i in x], gi, w, color=NEUTRAL, label="Primary substations (GI)", zorder=3)
for bars in (b1, b2):
    for b in bars:
        a2.text(b.get_x() + b.get_width()/2, b.get_height() + 40, f"{b.get_height():,.0f}", ha="center", fontsize=7.5, color=INK)
a2.set_xticks(list(x)); a2.set_xticklabels(labels, fontsize=7.2); a2.tick_params(axis="x", length=0)
a2.set_yticks([]); a2.set_ylim(0, 3000)
for s in ("top", "right", "left"): a2.spines[s].set_visible(False)
a2.legend(fontsize=7.5, frameon=False, loc="upper right")
a2.set_title("Headroom at 80 % limit (MVA), by growth", fontsize=9, loc="left", color=INK)
fig.tight_layout(w_pad=3); fig.savefig(OUT + "fig4_readiness.png", facecolor="white"); plt.close(fig)
print("ok")
