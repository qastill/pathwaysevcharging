"""Pasang paket "West Java" ke instalasi ur-scape mana pun (macOS/Windows), idempoten.

    python3 install.py /path/ke/ur-scape/Data

Menyalin Sites/West Java/*.csv, lalu menambahkan grup/layer dari layers_add.csv ke Data/layers.csv dan baris
citations_add.csv ke Data/citations.csv (hanya yang belum ada). ur-scape mengonversi CSV ke .bin saat dibuka.
"""
import os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
data = sys.argv[1] if len(sys.argv) > 1 else None
if not data or not os.path.isfile(os.path.join(data, "layers.csv")):
    sys.exit("pakai: python3 install.py <folder Data ur-scape>  (folder yang berisi layers.csv)")

def rd(p): return open(p, encoding="utf-16").read().replace("\r\n", "\n").rstrip("\n")
def wr(p, s): open(p, "w", encoding="utf-16", newline="").write(s.replace("\n", "\r\n") + "\r\n")

dst = os.path.join(data, "Sites", "West Java"); os.makedirs(dst, exist_ok=True); n = 0
for f in os.listdir(os.path.join(HERE, "Sites", "West Java")):
    if f.endswith(".csv"):
        shutil.copy(os.path.join(HERE, "Sites", "West Java", f), os.path.join(dst, f)); n += 1
        old = os.path.join(dst, f[:-4] + ".bin")
        if os.path.exists(old): os.remove(old)            # paksa ur-scape konversi ulang
print(f"{n} layer grid disalin ke {dst}")

L = rd(os.path.join(data, "layers.csv")); grp = None; added = 0
for line in rd(os.path.join(HERE, "layers_add.csv")).split("\n")[1:]:
    if line.startswith("Group,"):
        grp = line
        if f"\n{grp}" not in L: L = L.rstrip("\n,") + f"\n,,,,\n{grp}"
    elif line.startswith("Layer,") and line.split(",")[1] and f"Layer,{line.split(',')[1]}," not in L:
        i = L.index(grp); j = L.find("\n,,,,", i); j = len(L) if j < 0 else j
        L = L[:j] + "\n" + line + L[j:]; added += 1
wr(os.path.join(data, "layers.csv"), L); print(f"{added} layer ditambahkan ke layers.csv")

C = rd(os.path.join(data, "citations.csv")); added = 0
for line in rd(os.path.join(HERE, "citations_add.csv")).split("\n")[1:]:
    if line and f"\n{line.split(',')[0]}," not in C: C += "\n" + line; added += 1
wr(os.path.join(data, "citations.csv"), C); print(f"{added} sitasi ditambahkan ke citations.csv")
print("selesai - buka ur-scape, pilih site 'West Java' di Site Browser")
