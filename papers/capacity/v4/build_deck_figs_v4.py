"""Figur khusus deck v4 (ilustratif): peta hero, peta berlabel kota, peta celah dengan callout.

Membaca papers/capacity/capacity.json dan papers/capacity/v3/strengthen.json.
Jalankan dari akar repositori:  python3 papers/capacity/v4/build_deck_figs_v4.py
"""
import json, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch, FancyBboxPatch
from matplotlib.lines import Line2D
from matplotlib.colors import LogNorm
import matplotlib.patheffects as pe

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
D = json.load(open(os.path.join(ROOT, "papers/capacity/capacity.json")))
S = json.load(open(os.path.join(ROOT, "papers/capacity/v3/strengthen.json")))
B = S["base"]
OUT = os.path.join(ROOT, "papers/capacity/v4/figs/")
os.makedirs(OUT, exist_ok=True)

INK, MUTED = "#1B2A3A", "#6B7785"
TEAL, CORAL, AMBER, NEUTRAL, BASEC = "#0F7C6E", "#D1495B", "#E0A526", "#B8BEC6", "#EEF1F4"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
DEG = D["meta"]["cell_deg"]; FEAS = D["meta"]["feasible"]
cells = D["cells"]; sites = D["sites"]
lats = [c[0] for c in cells]; lons = [c[1] for c in cells]
XL, YL = (min(lons) - 0.06, max(lons) + 0.06), (min(lats) - 0.06, max(lats) + 0.06)
CITIES = [("Bogor", -6.595, 106.799), ("Depok", -6.402, 106.794), ("Bekasi", -6.238, 106.976),
          ("Karawang", -6.305, 107.303), ("Bandung", -6.914, 107.609), ("Sukabumi", -6.922, 106.927),
          ("Cirebon", -6.732, 108.552), ("Tasikmalaya", -7.327, 108.220), ("Purwakarta", -6.556, 107.443)]


def tile(ax, lat, lon, **kw):
    ax.add_patch(Rectangle((lon - DEG / 2, lat - DEG / 2), DEG, DEG, **kw))


def clean(ax):
    ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def cities(ax, names=None, size=8.5, color=INK):
    for nm, la, lo in CITIES:
        if names and nm not in names:
            continue
        ax.text(lo, la + 0.07, nm, fontsize=size, color=color, ha="center", va="bottom", fontweight="bold",
                path_effects=[pe.withStroke(linewidth=2.6, foreground="white")], zorder=10)


def save(fig, name, transparent=False):
    fig.savefig(OUT + name, dpi=200, bbox_inches="tight", pad_inches=0.05, transparent=transparent,
                facecolor="none" if transparent else "white")
    plt.close(fig)


# ---------------------------------------------------------------- hero (latar gelap, transparan)
fig, ax = plt.subplots(figsize=(8, 5.4))
cm = plt.get_cmap("GnBu")
for c in cells:
    if c[7] > 0:
        a = 0.35 + 0.6 * min(math.log10(c[7] + 1) / 2, 1)
        tile(ax, c[0], c[1], facecolor=AMBER, alpha=a, edgecolor="none")
    elif c[2] > 0:
        tile(ax, c[0], c[1], facecolor=cm(0.35 + 0.6 * min(c[2] / 20000, 1)), alpha=0.55, edgecolor="none")
ax.scatter([s["lon"] for s in sites], [s["lat"] for s in sites], s=[3 + math.sqrt(s["kwh"]) / 45 for s in sites],
           color="white", alpha=0.95, lw=0, zorder=3)
clean(ax)
save(fig, "hero_map.png", transparent=True)

# ---------------------------------------------------------------- dua permukaan, berlabel
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
cm_h = plt.get_cmap("GnBu"); cm_d = plt.get_cmap("YlOrBr"); dn = LogNorm(1, 120)
for c in cells:
    tile(axes[0], c[0], c[1], facecolor=cm_h(0.12 + 0.85 * min(c[2] / 30000.0, 1)) if c[2] > 0 else BASEC, edgecolor="white", lw=0.25)
    tile(axes[1], c[0], c[1], facecolor=cm_d(0.2 + 0.78 * dn(min(c[7], 120))) if c[7] > 0 else BASEC, edgecolor="white", lw=0.25)
    tile(axes[2], c[0], c[1], facecolor="#F6D5DA" if (c[7] > 0 and c[8] == 0) else BASEC, edgecolor="white", lw=0.25)
for c in cells:
    if c[10] == "HL" and c[8] == 0:
        tile(axes[2], c[0], c[1], facecolor="none", edgecolor=CORAL, hatch="////", lw=0.9)
axes[2].scatter([s["lon"] for s in sites], [s["lat"] for s in sites], s=[5 + math.sqrt(s["kwh"]) / 32 for s in sites],
                color=INK, edgecolor="white", lw=0.3, zorder=3)
for ax in axes:
    clean(ax)
    cities(ax, ["Bogor", "Bekasi", "Karawang", "Bandung", "Cirebon", "Tasikmalaya", "Sukabumi"], size=8)
save(fig, "map_surfaces_labeled.png")

# ---------------------------------------------------------------- peta celah besar dengan callout
fig, ax = plt.subplots(figsize=(9, 6))
for c in cells:
    tile(ax, c[0], c[1], facecolor="#F6D5DA" if (c[7] > 0 and c[8] == 0) else BASEC, edgecolor="white", lw=0.3)
gap = [c for c in cells if c[10] == "HL" and c[8] == 0]
for c in gap:
    tile(ax, c[0], c[1], facecolor=CORAL, alpha=0.85, edgecolor="white", lw=0.6)
ax.scatter([s["lon"] for s in sites], [s["lat"] for s in sites], s=[5 + math.sqrt(s["kwh"]) / 30 for s in sites],
           color=INK, edgecolor="white", lw=0.3, zorder=3)
cities(ax, ["Bogor", "Depok", "Bekasi", "Karawang", "Bandung", "Cirebon", "Sukabumi", "Purwakarta"])
# callout per klaster: panah ke pusat sel-sel yang benar-benar berdekatan
CLUSTERS = [("Bogor–Depok", lambda c: c[1] < 107.05 and c[0] >= -6.75, (106.65, -5.88)),
            ("Sukabumi", lambda c: c[1] < 107.05 and c[0] < -6.75, (106.75, -7.5)),
            ("Bandung", lambda c: 107.3 <= c[1] < 108.0 and c[0] < -6.7, (108.0, -7.5)),
            ("Karawang–Subang", lambda c: 107.05 <= c[1] < 108.0 and c[0] >= -6.7, (108.25, -5.88)),
            ("Cirebon", lambda c: c[1] >= 108.0, (108.85, -7.0))]
used = 0
for name, f, (tx, ty) in CLUSTERS:
    cl = [c for c in gap if f(c)]
    if not cl:
        continue
    used += len(cl)
    cx = sum(c[1] for c in cl) / len(cl); cy = sum(c[0] for c in cl) / len(cl)
    ax.annotate(f"{name}: {len(cl)} cell{'s' if len(cl) > 1 else ''}, {sum(c[7] for c in cl)} owners",
                xy=(cx, cy), xytext=(tx, ty), fontsize=9, color=CORAL, fontweight="bold", ha="center",
                arrowprops=dict(arrowstyle="-|>", color=CORAL, lw=1.3, shrinkB=4), zorder=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=CORAL))
assert used == len(gap), (used, len(gap))
YL = (YL[0] - 0.12, YL[1] + 0.12)
clean(ax)
ax.legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor=INK, markersize=6, label="public charger"),
                   Patch(facecolor="#F6D5DA", label="owners, no charger"),
                   Patch(facecolor=CORAL, label="high demand, low headroom, no charger")],
          loc="lower left", fontsize=8.5, frameon=False)
save(fig, "map_gap_callouts.png")

# ---------------------------------------------------------------- peta situs per aturan, berlabel
RULES = [("headroom", CORAL), ("demand", AMBER), ("dwh", TEAL)]
medp = B["med_pool"]
for k, col in RULES:
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    for c in cells:
        tile(ax, c[0], c[1], facecolor=BASEC, edgecolor="white", lw=0.25)
    ax.scatter([s["lon"] for s in sites], [s["lat"] for s in sites], s=3, color=MUTED, alpha=0.5, lw=0, zorder=2)
    sel = B["rules"][k]["sel"]
    ok = [s for s in sel if s[2] >= medp and s[3] >= FEAS]
    st = [s for s in sel if s[2] < medp]
    inf = [s for s in sel if s[3] < FEAS]
    ax.scatter([s[1] for s in ok], [s[0] for s in ok], s=[18 + 6 * math.sqrt(s[2]) for s in ok], color=col, edgecolor="white", lw=0.6, zorder=4)
    ax.scatter([s[1] for s in st], [s[0] for s in st], s=30, facecolor="white", edgecolor=col, lw=1.4, zorder=4)
    ax.scatter([s[1] for s in inf], [s[0] for s in inf], s=70, marker="X", color=INK, zorder=5)
    cities(ax, ["Bogor", "Bekasi", "Bandung", "Cirebon"], size=7.5)
    clean(ax)
    save(fig, f"sites_{k}.png")
print("ok:", sorted(os.listdir(OUT)))


# ---------------------------------------------------------------- waffle "dari 100 pemilik"
def waffle(name, k, col_on, col_off=NEUTRAL):
    fig, ax = plt.subplots(figsize=(2.6, 2.6))
    for i in range(100):
        r, c = divmod(i, 10)
        ax.add_patch(FancyBboxPatch((c + 0.08, 9 - r + 0.08), 0.84, 0.84, boxstyle="round,pad=0,rounding_size=0.18",
                                    facecolor=col_on if i < k else col_off, edgecolor="none"))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_aspect("equal"); ax.axis("off")
    save(fig, name, transparent=True)


cov_all = round(B["baseline"]["cov"])
waffle("waffle_all_today.png", cov_all, TEAL, CORAL)
for key, col in (("base", NEUTRAL), ("headroom", CORAL), ("demand", AMBER), ("dwh", TEAL)):
    v = B["baseline"]["terc"][0] if key == "base" else B["rules"][key]["terc"][0]
    waffle(f"waffle_poor_{key}.png", round(v), INK if key == "base" else col, "#E4E8EC")


# ---------------------------------------------------------------- piktogram 50 situs per aturan
def pictogram(key, col):
    sel = B["rules"][key]["sel"]
    st = sorted(sel, key=lambda s: (s[3] < FEAS, s[2] < medp))  # tercapai dulu, lalu terlantar, lalu tak layak
    fig, ax = plt.subplots(figsize=(6.2, 1.35))
    for i, s in enumerate(st):
        r, c = divmod(i, 25)
        x, y = c, 1 - r
        if s[3] < FEAS:
            ax.scatter([x], [y], marker="X", s=150, color=INK)
        elif s[2] < medp:
            ax.scatter([x], [y], s=130, facecolor="white", edgecolor=col, lw=2)
        else:
            ax.scatter([x], [y], s=130, color=col, lw=0)
    ax.set_xlim(-0.7, 24.7); ax.set_ylim(-0.7, 1.7); ax.axis("off")
    save(fig, f"picto_{key}.png", transparent=True)


for key, col in RULES:
    pictogram(key, col)
print("ok:", sorted(os.listdir(OUT)))
