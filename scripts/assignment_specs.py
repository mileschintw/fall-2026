"""Archive assignment specs (Canvas description, linked Canvas files, DSA repo README) into <course>/hw/<slug>/.

Usage:
  python scripts/assignment_specs.py                  # fetch, archive new/changed specs, print a JSON report
  python scripts/assignment_specs.py --done gpu/hw1   # README.md summary written: mark it done, rebuild the index

Per assignment directory:
  spec.md     verbatim sources, regenerated on every change (do not edit)
  spec.pdf    original Canvas file the description links to (spec-1.pdf, spec-2.pdf… when there are several)
  README.md   structured summary written by the agent (automation/assignment-specs.md)
State: state/assignment_specs.json (fingerprints per Canvas assignment id; `summary_done` false until --done).
Old versions live in git history; spec.md is overwritten in place.

Exit codes: 0 ok (report printed); 3 Canvas login expired; 1 Canvas list failed (the JSON on stdout has
`canvas_error`). When the list step fails nothing is written. Each assignment is built in a temp dir and swapped in
only when complete, so a login that expires mid-run keeps the assignments already archived and leaves the rest as before.
A failure on one file or README only skips that assignment (listed under "errors"; the next run retries it).
Canvas download URLs carry a verifier token: only file ids and bytes are kept, never the URL.
"""
import argparse
import base64
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tz import PACIFIC, fmt, now_pacific, parse_utc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state" / "assignment_specs.json"
TMP = ROOT / "state" / "_specs.tmp"
COURSES = {"1917398": "gpu", "1917417": "dsa"}
CANVAS = "https://canvas.uw.edu/courses/"
DSA_ORG, DSA_REPO = "uw-python-fall2026", "assignment-{n}-mileschintw"  # courses.yaml dsa.assignment_repo_pattern


class LoginExpired(Exception):
    pass


def pw(snippet, pre="", course="1917398"):
    """Run one browser snippet through pw_run.py; return its JSON value."""
    cmd = [sys.executable, str(ROOT / "scripts" / "pw_run.py"), str(ROOT / "scripts" / "browser" / snippet),
           str(TMP), "--url", CANVAS + course] + (["--pre", pre] if pre else [])
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    try:
        if r.returncode == 3:
            raise LoginExpired(r.stdout.strip())
        if r.returncode != 0:
            raise RuntimeError(f"{snippet}: " + (r.stdout + r.stderr).strip().splitlines()[-1])
        return json.loads(TMP.read_text(encoding="utf-8"))
    finally:
        TMP.unlink(missing_ok=True)


def slug(course, name):
    for pat, fmt_ in ((r"Homework\s*#?\s*(\d+)", "hw{}"), (r"^A(\d+)\b", "a{}"), (r"Task\s*(\d+)", "task{}")):
        m = re.search(pat, name, re.I)
        if m:
            return fmt_.format(int(m.group(1)))
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40]


def readme(name):
    """DSA starter repo README -> (repo, sha, text) or None when the repo/README does not exist yet."""
    m = re.match(r"A(\d+)\b", name)
    if not m:
        return None
    repo = DSA_REPO.format(n=m.group(1))
    r = subprocess.run(["gh", "api", f"repos/{DSA_ORG}/{repo}/readme"], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        if "404" in r.stdout + r.stderr:
            return None
        raise RuntimeError(f"gh {repo}: " + (r.stdout + r.stderr).strip().splitlines()[-1])
    j = json.loads(r.stdout)
    return {"repo": f"{DSA_ORG}/{repo}", "sha": j["sha"], "text": base64.b64decode(j["content"]).decode("utf-8")}


def fingerprint(a, rd):
    return {"text": hashlib.sha256(a["text"].encode()).hexdigest()[:16],
             "links": [x["href"] for x in a["links"]],
             "files": {str(f["id"]): f.get("updated_at") for f in a["files"]},
             "readme": rd["sha"] if rd else None,
             "due_at": a["due_at"]}


def diff(old, new):
    if not old:
        return ["new"]
    out = []
    if old["text"] != new["text"] or old["links"] != new["links"]:
        out.append("Canvas 說明文字改了")
    for fid, up in new["files"].items():
        if fid not in old["files"]:
            out.append(f"新檔案 {fid}")
        elif old["files"][fid] != up:
            out.append(f"檔案 {fid} 更新（{old['files'][fid]} → {up}）")
    out += [f"檔案 {fid} 從說明移除" for fid in old["files"] if fid not in new["files"]]
    if old["readme"] != new["readme"]:
        out.append("repo README 改了")
    if old["due_at"] != new["due_at"]:
        out.append(f"due_at {old['due_at']} → {new['due_at']}")
    return out


def archive(cid, a, rd, d, old_files):
    """Build spec.md and the original files in a temp dir, then swap them into d (README.md is kept).
    Returns the file names written. A failure leaves d untouched."""
    tmp = d.parent / f".{d.name}.tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    try:
        written = build(cid, a, rd, tmp)
        d.mkdir(exist_ok=True)
        for fn in written:
            (tmp / fn).replace(d / fn)
        for fn in set(old_files) - set(written):  # stale names only, after the new set is in place
            (d / fn).unlink(missing_ok=True)
        return written
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def build(cid, a, rd, d):
    due = fmt(parse_utc(a["due_at"])) if a["due_at"] else "（Canvas 沒有設定）"
    md = [f"# {a['name'].strip()}", "",
          f"> 來源：Canvas assignment {a['id']}（{a['html_url']}），抓取 {now_pacific():%Y-%m-%d %H:%M %Z}。",
          "> 這個檔案由 `scripts/assignment_specs.py` 產生，內容是原文，每次來源有變動就整份重寫，不要手改。整理過的版本在 README.md。", "",
          f"- 截止（Canvas `due_at`）：{due}", "", "## Canvas 作業說明", "", a["text"] or "（空白）"]
    if a["links"]:
        md += ["", "### 說明裡的連結", ""] + [f"- {x['text'] or x['href']}: {x['href']}" for x in a["links"]]
    written = []
    for i, f in enumerate(a["files"], 1):
        if "error" in f:
            raise RuntimeError(f"Canvas file {f['id']}: HTTP {f['error']}")
        v = pw("canvas_file.js", f"window.COURSE={cid}; window.FILE_ID={f['id']}", cid)
        fn = ("spec" if len(a["files"]) == 1 else f"spec-{i}") + Path(f["name"]).suffix.lower()
        (d / fn).write_bytes(base64.b64decode(v["b64"]))
        written.append(fn)
        md += ["", f"## {f['name']}", "",
               f"> Canvas file {f['id']}（原檔名 {f['name']}），updated_at {f['updated_at']}，{f['size']} bytes。原檔：[{fn}]({fn})", ""]
        if f.get("content_type") == "application/pdf" or fn.lower().endswith(".pdf"):
            t = pw("pdf_text.js", f"window.COURSE={cid}; window.FILE_ID={f['id']}", cid)
            md.append(t["text"].strip() or "（PDF 抽不出文字，可能是掃描檔，請看原檔）")
        else:
            md.append("（不是 PDF，沒有轉文字，請看原檔）")
    if rd:
        md += ["", f"## Starter repo README（{rd['repo']}，blob {rd['sha'][:7]}）", "", rd["text"].strip()]
    text = re.sub(r"verifier=[^&\s)\]>]+", "verifier=REDACTED", "\n".join(md) + "\n")  # CLAUDE.md 密鑰
    (d / "spec.md").write_text(text, encoding="utf-8")
    return written + ["spec.md"]


def index(state):
    for course in ("gpu", "dsa"):
        rows = sorted((v for v in state.values() if v["course"] == course), key=lambda v: v["due_at"] or "9")
        if not rows:
            continue
        lines = [f"# {course.upper()} 作業說明索引", "",
                 "> 由 `scripts/assignment_specs.py` 產生，不要手改。每份作業一個資料夾：`spec.md` 是原文，`README.md` 是整理過的摘要。", "",
                 "| 作業 | 截止（Pacific） | 摘要 | 原文 |", "|---|---|---|---|"]
        for v in rows:
            due = fmt(parse_utc(v["due_at"])) if v["due_at"] else "—"
            summ = f"[README]({v['slug']}/README.md)" if v["summary_done"] else "（待整理）"
            lines.append(f"| {v['name'].strip()} | {due} | {summ} | [spec.md]({v['slug']}/spec.md) |")
        (ROOT / course / "hw" / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def load():
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def save(state):
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    index(state)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--done", metavar="COURSE/SLUG")
    a = ap.parse_args()
    state = load()
    if a.done:
        hit = [k for k, v in state.items() if f"{v['course']}/{v['slug']}" == a.done]
        if not hit:
            sys.exit(f"unknown spec {a.done}; known: " + ", ".join(f"{v['course']}/{v['slug']}" for v in state.values()))
        v, md = state[hit[0]], ROOT / state[hit[0]]["dir"] / "README.md"
        if not md.exists():
            sys.exit(f"{v['dir']}/README.md does not exist yet")
        if datetime.fromtimestamp(md.stat().st_mtime, PACIFIC) < datetime.fromisoformat(v["archived_at"]):
            sys.exit(f"{v['dir']}/README.md is older than spec.md (archived {v['archived_at']}): update it first")
        state[hit[0]]["summary_done"] = True
        save(state)
        print("done:", state[hit[0]]["dir"])
        return

    try:
        canvas = pw("canvas_specs.js")
    except LoginExpired as e:
        print(json.dumps({"login_expired": str(e)}, ensure_ascii=False))
        sys.exit(3)
    except RuntimeError as e:
        print(json.dumps({"canvas_error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    report = {"pending": [], "unchanged": [], "no_spec": [], "errors": []}
    for cid, items in canvas.items():
        course = COURSES[cid]
        for asg in items:
            if not asg["published"]:
                continue
            key = str(asg["id"])
            s = state[key]["slug"] if key in state else slug(course, asg["name"])
            if any(k != key and v["course"] == course and v["slug"] == s for k, v in state.items()):
                s = f"{s}-{key}"  # two assignments map to the same slug: keep both
            label = f"{course}/{s}"
            try:
                rd = readme(asg["name"]) if course == "dsa" else None
                if not (asg["text"] or asg["files"] or rd):
                    report["no_spec"].append(asg["name"].strip())
                    continue
                fp, old = fingerprint(asg, rd), state.get(key)
                changes = diff(old and old["fp"], fp)
                d = ROOT / course / "hw" / s
                if changes:
                    files = archive(cid, asg, rd, d, (old or {}).get("files", []))
                    if old and not old["summary_done"]:  # summary still owed: keep what it has to cover
                        changes = old["changes"] + [c for c in changes if c not in old["changes"]]
                    state[key] = {"course": course, "slug": s, "dir": d.relative_to(ROOT).as_posix(), "name": asg["name"],
                                  "due_at": asg["due_at"], "fp": fp, "files": files,
                                  "archived_at": now_pacific().isoformat(timespec="seconds"), "summary_done": False,
                                  "changes": changes,
                                  "history": (old or {}).get("history", []) + [{"at": now_pacific().isoformat(timespec="seconds"), "changes": diff(old and old["fp"], fp)}]}
                    save(state)
                if not state[key]["summary_done"]:
                    report["pending"].append({"spec": label, "dir": state[key]["dir"], "name": asg["name"].strip(),
                                              "canvas_id": asg["id"], "changes": state[key]["changes"]})
                else:
                    report["unchanged"].append(label)
            except LoginExpired as e:
                print(json.dumps({"login_expired": str(e), "partial": report}, ensure_ascii=False))
                sys.exit(3)
            except Exception as e:  # one assignment failing must not block the others
                report["errors"].append({"spec": label, "error": str(e)})
    save(state)
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
