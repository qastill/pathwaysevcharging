"""Tambahkan transisi slide dan animasi masuk ke deck pptxgenjs.

Elemen yang objectName-nya berpola "a<langkah><efek>-..." dianimasikan:
  langkah = urutan kemunculan (1, 2, ...); elemen berlangkah sama muncul bersamaan
  efek    = f (fade) | u (wipe dari bawah) | r (wipe dari kiri)
Semua langkah berjalan otomatis setelah slide tampil ("After Previous"), sehingga slide
tersusun sendiri tanpa klik. Setiap slide juga diberi transisi fade.

Pemakaian:  python3 add_animations.py in.pptx out.pptx
"""
import re, sys, zipfile, shutil, os, tempfile
from lxml import etree

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
NAME = re.compile(r"^a(\d+)([fur])-")
DUR = {"f": 450, "u": 500, "r": 500}
STEP_GAP = 0  # langkah berikutnya mulai tepat setelah langkah sebelumnya selesai


def effect_xml(ids, spid, eff, delay_in_group):
    """Satu efek masuk untuk satu shape. ids = generator id cTn."""
    c = next(ids)
    set_id, anim_id = next(ids), next(ids)
    dur = DUR[eff]
    if eff == "f":
        preset, sub, filt = 10, 0, "fade"
    elif eff == "u":
        preset, sub, filt = 22, 4, "wipe(up)"
    else:
        preset, sub, filt = 22, 8, "wipe(right)"
    return (f'<p:par><p:cTn id="{c}" presetID="{preset}" presetClass="entr" presetSubtype="{sub}" fill="hold" grpId="0" nodeType="afterEffect">'
            f'<p:stCondLst><p:cond delay="{delay_in_group}"/></p:stCondLst><p:childTnLst>'
            f'<p:set><p:cBhvr><p:cTn id="{set_id}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="visible"/></p:to></p:set>'
            f'<p:animEffect transition="in" filter="{filt}"><p:cBhvr><p:cTn id="{anim_id}" dur="{dur}"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
            f'</p:childTnLst></p:cTn></p:par>'), dur


def build_timing(targets):
    """targets: list (langkah, efek, spid, jenis) -> string <p:timing>."""
    steps = sorted(set(t[0] for t in targets))
    counter = iter(range(3, 100000))
    groups, t_acc = [], 0
    for st in steps:
        members = [t for t in targets if t[0] == st]
        gid = next(counter)
        effs, longest = [], 0
        for _, eff, spid, _ in members:
            x, dur = effect_xml(counter, spid, eff, 0)
            effs.append(x)
            longest = max(longest, dur)
        groups.append(f'<p:par><p:cTn id="{gid}" fill="hold"><p:stCondLst><p:cond delay="{t_acc}"/></p:stCondLst>'
                      f'<p:childTnLst>{"".join(effs)}</p:childTnLst></p:cTn></p:par>')
        t_acc += longest + STEP_GAP
    outer = next(counter)
    bld = []
    seen = set()
    for _, _, spid, kind in targets:
        if spid in seen:
            continue
        seen.add(spid)
        if kind == "sp":
            bld.append(f'<p:bldP spid="{spid}" grpId="0" animBg="1"/>')
        elif kind == "graphicFrame":
            bld.append(f'<p:bldGraphic spid="{spid}" grpId="0"><p:bldAsOne/></p:bldGraphic>')
    return ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
            '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
            f'<p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
            '<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst>'
            f'<p:childTnLst>{"".join(groups)}</p:childTnLst></p:cTn></p:par>'
            '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
            '</p:childTnLst></p:cTn></p:par></p:tnLst>'
            + (f'<p:bldLst>{"".join(bld)}</p:bldLst>' if bld else '') + '</p:timing>')


def process_slide(xml):
    root = etree.fromstring(xml)
    targets = []
    for kind in ("sp", "pic", "graphicFrame"):
        for el in root.iter(f"{{{NS['p']}}}{kind}"):
            c = el.find(f".//{{{NS['p']}}}cNvPr")
            if c is None:
                continue
            m = NAME.match(c.get("name", ""))
            if m:
                targets.append((int(m.group(1)), m.group(2), c.get("id"), kind))
    s = xml.decode("utf-8")
    assert "<p:timing" not in s and "<p:transition" not in s, "slide sudah punya transisi/animasi"
    trans = '<p:transition spd="med"><p:fade/></p:transition>'
    timing = build_timing(targets) if targets else ""
    anchor = "</p:clrMapOvr>"
    assert anchor in s, "clrMapOvr tidak ditemukan"
    s = s.replace(anchor, anchor + trans + timing, 1)
    return s.encode("utf-8"), len(targets)


def main(src, dst):
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(src) as z:
        z.extractall(tmp)
        names = z.namelist()
    sd = os.path.join(tmp, "ppt", "slides")
    total = 0
    for f in sorted(os.listdir(sd), key=lambda x: (len(x), x)):
        if not f.endswith(".xml"):
            continue
        p = os.path.join(sd, f)
        new, k = process_slide(open(p, "rb").read())
        open(p, "wb").write(new)
        total += k
        print(f"  {f}: {k} elemen beranimasi")
    if os.path.exists(dst):
        os.remove(dst)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for nm in names:  # urutan asli, [Content_Types].xml tetap pertama
            full = os.path.join(tmp, nm)
            if os.path.isfile(full):
                z.write(full, nm)
    shutil.rmtree(tmp)
    print(f"selesai: {total} elemen beranimasi -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
