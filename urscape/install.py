"""Install the "West Java" package into any ur-scape installation (macOS/Windows). Safe to run twice.

    python3 install.py /path/to/ur-scape/Data

Copies Sites/*/*.csv (West Java 0.5', Rebana 300 m), then adds the groups/layers from layers_add.csv to Data/layers.csv and the rows of
citations_add.csv to Data/citations.csv (only those not already present). ur-scape converts the CSVs to .bin on first open.
"""
import os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
data = sys.argv[1] if len(sys.argv) > 1 else None
if not data or not os.path.isfile(os.path.join(data, "layers.csv")):
    sys.exit("usage: python3 install.py <ur-scape Data folder>  (the folder that contains layers.csv)")

def rd(p): return open(p, encoding="utf-16").read().replace("\r\n", "\n").rstrip("\n")
def wr(p, s): open(p, "w", encoding="utf-16", newline="").write(s.replace("\n", "\r\n") + "\r\n")

n = 0
for site in sorted(os.listdir(os.path.join(HERE, "Sites"))):
    src = os.path.join(HERE, "Sites", site)
    if not os.path.isdir(src): continue
    dst = os.path.join(data, "Sites", site); os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        if f.endswith(".csv"):
            shutil.copy(os.path.join(src, f), os.path.join(dst, f)); n += 1
            old = os.path.join(dst, f[:-4] + ".bin")
            if os.path.exists(old): os.remove(old)            # force ur-scape to convert again
print(f"{n} grid files copied into {os.path.join(data, 'Sites')} (sites: West Java, Rebana)")

L = rd(os.path.join(data, "layers.csv")); grp = None; added = 0
for line in rd(os.path.join(HERE, "layers_add.csv")).split("\n")[1:]:
    if line.startswith("Group,"):
        grp = line
        if f"\n{grp}" not in L: L = L.rstrip("\n,") + f"\n,,,,\n{grp}"
    elif line.startswith("Layer,") and line.split(",")[1] and f"Layer,{line.split(',')[1]}," not in L:
        i = L.index(grp); j = L.find("\n,,,,", i); j = len(L) if j < 0 else j
        L = L[:j] + "\n" + line + L[j:]; added += 1
wr(os.path.join(data, "layers.csv"), L); print(f"{added} layers added to layers.csv")

C = rd(os.path.join(data, "citations.csv")); added = 0
for line in rd(os.path.join(HERE, "citations_add.csv")).split("\n")[1:]:
    if line and f"\n{line.split(',')[0]}," not in C: C += "\n" + line; added += 1
wr(os.path.join(data, "citations.csv"), C); print(f"{added} citations added to citations.csv")
print("done - open ur-scape and choose 'West Java' or 'Rebana' in the Site Browser")
