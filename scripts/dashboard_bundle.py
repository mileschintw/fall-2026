"""Build the dashboard's store documents as local JSON files, so ArtifactData can send them with `file_path`.

The dashboard (a "Dashboard" Artifact type, URL in courses.yaml hub.dashboard_url) holds four documents:
  dash/meta               {title}
  datasets/deadlines      file source -> state/deadlines.json (uploaded as an asset)
  datasets/runs           file source -> state/runs.json      (uploaded as an asset)
  files/index.html        {text} <- automation/dashboard/index.html

Usage:
  python scripts/dashboard_bundle.py --out <dir> --page-only
      -> <dir>/index.html.json            (after editing automation/dashboard/index.html)
  python scripts/dashboard_bundle.py --out <dir> --deadlines-blob <id> --runs-blob <id> --by "<who>"
      -> <dir>/meta.json, deadlines.json, runs.json, index.html.json   (full rebuild, automation/MIGRATION.md)
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TITLE = "Fall 2026 學期中樞"
DATASETS = {
    "deadlines": {
        "title": "作業與考試時程",
        "description": "GPU 和 DSA 全學期每個要交或要到場的項目，含 Canvas 繳交狀態。由排程（晨報）從 Canvas 更新，來源檔 state/deadlines.json。",
        "schedule": "每次排程任務跑完更新（晨報每天 07:00 會重新比對 Canvas 狀態）",
        "staleAfterHours": 48,
    },
    "runs": {
        "title": "排程執行紀錄",
        "description": "每個排程任務每次執行的結果，一列一次，來源檔 state/runs.json（和 repo 的 digests/INDEX.md 同步）。",
        "schedule": "每次排程任務跑完更新",
        "staleAfterHours": 36,
    },
}


def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    print(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--page-only", action="store_true")
    ap.add_argument("--deadlines-blob", help="asset id (32 hex), not the /_blob/ url: Git Bash rewrites leading slashes")
    ap.add_argument("--runs-blob")
    ap.add_argument("--by", default="Claude")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    write(out / "index.html.json", {"text": (ROOT / "automation" / "dashboard" / "index.html").read_text(encoding="utf-8")})
    if a.page_only:
        return
    if not (a.deadlines_blob and a.runs_blob):
        ap.error("--deadlines-blob and --runs-blob are required for a full rebuild")
    from datetime import datetime
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds")
    write(out / "meta.json", {"title": TITLE})
    for ds, blob in (("deadlines", a.deadlines_blob), ("runs", a.runs_blob)):
        url = "/_blob/" + blob.rsplit("/", 1)[-1]
        write(out / f"{ds}.json", {**DATASETS[ds], "source": {"kind": "file", "url": url, "name": f"{ds}.json"},
                                   "updated": {"at": now, "by": a.by}})


if __name__ == "__main__":
    main()
