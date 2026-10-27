"""Copy of the blank sheet with only the measured-data tables filled (timing, NCU, CPU vs GPU).

python fill_data_docx.py <blank HW2_Answers.docx> <results dir> <out HW2_Answers_data.docx>
"""
import csv
import io
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import docx
from docx.shared import Pt

KMAP = {"global": "global", "static": "static SMEM", "dynamic": "dynamic SMEM"}


def timing(path):
    """median of reps 2..N per (img, kernel); cpu t3 per img"""
    reps, cpu = defaultdict(list), {}
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        if not line.startswith("RESULT"):
            continue
        kv = dict(x.split("=", 1) for x in line.split()[1:])
        if kv["kernel"] == "cpu":
            cpu[int(kv["img"])] = float(kv["t3_ms"])
        elif int(kv["rep"]) > 1:
            reps[(int(kv["img"]), kv["kernel"])].append((float(kv["t1_ms"]), float(kv["t2_ms"])))
    med = {k: (statistics.median(a for a, _ in v), statistics.median(b for _, b in v)) for k, v in reps.items()}
    return med, cpu


def ncu(path):
    lines = [l for l in Path(path).read_text(encoding="utf-8-sig").splitlines() if l.startswith('"')]
    return {r["Metric Name"]: float(r["Metric Value"].replace(",", "")) for r in csv.DictReader(io.StringIO("\n".join(lines)))}


def put(cell, text):
    p = cell.paragraphs[0]
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    r = p.add_run(text)
    r.font.size = Pt(8.5)


def find(d, first_header, second_header):
    for t in d.tables:
        h = [c.text for c in t.rows[0].cells]
        if h[0] == first_header and h[1].startswith(second_header):
            return t
    raise LookupError(first_header)


def main(blank, res, out):
    res = Path(res)
    rel, cpu_rel = timing(res / "timing_release.txt")
    dbg, _ = timing(res / "timing_debug.txt")
    d = docx.Document(blank)

    t = find(d, "Image", "Kernel")
    for row in t.rows[1:]:
        img = int(row.cells[0].text.split()[0][1:])
        k = next(k for k, v in KMAP.items() if v == row.cells[1].text)
        for i, v in enumerate((*dbg[(img, k)], *rel[(img, k)]), start=2):
            put(row.cells[i], f"{v:.3f}")

    t = find(d, "Kernel", "Image")
    for row in t.rows[1:]:
        k = "global" if row.cells[0].text == "global" else "shared"
        img = int(row.cells[1].text[1:])
        m = ncu(res / "ncu" / f"ncu_{k}_img{img}.csv")
        cyc, ps = m["smsp__cycles_elapsed.sum"], m["smsp__cycles_elapsed.sum.per_second"]
        inst, db = m["smsp__inst_executed.sum"], m["dram__bytes.sum"]
        vals = [f"{cyc:,.0f}", f"{ps:.4g}", f"{inst:,.0f}", f"{db:,.0f}", f"{cyc / ps:.4e}", f"{inst / db:.2f}"]
        for i, v in enumerate(vals, start=2):
            put(row.cells[i], v)

    t = find(d, "Image", "CPU T3")
    for row in t.rows[1:]:
        img = int(row.cells[0].text.split()[0][1:])
        g = [rel[(img, k)][1] for k in ("global", "static", "dynamic")]
        vals = [f"{cpu_rel[img]:.2f}"] + [f"{v:.3f}" for v in g] + [f"{cpu_rel[img] / min(g):.0f}×"]
        for i, v in enumerate(vals, start=1):
            put(row.cells[i], v)

    d.save(out)


if __name__ == "__main__":
    main(*sys.argv[1:4])
