"""Record one scheduled-task run, then regenerate digests/INDEX.md from state/runs.json.

Usage:
  python scripts/log_run.py --task 晨報 --status new --summary "A3 剩 24h；Piazza 新 2 篇" --output digests/2026-10-19.md
  python scripts/log_run.py --rebuild        # only regenerate INDEX.md

status: new（有新東西）| ok（正常，沒新東西）| skip（跳過）| warn（部分來源失敗 / 需要重新登入）| fail（失敗）
state/runs.json and state/deadlines.json are also the dashboard's data files (automation/_finish.md).
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hub_config import hub  # noqa: E402
from tz import PACIFIC, now_pacific  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "state" / "runs.json"
INDEX = ROOT / "digests" / "INDEX.md"
SCHEDULED = ["晨報", "週規劃", "截止提醒", "上課筆記"]  # shown under 最新狀態
TASKS = SCHEDULED + ["學期至今版"]  # one-off runs: logged, only listed under 紀錄
ICON = {"new": "🆕", "ok": "✅", "skip": "⏭", "warn": "⚠️", "fail": "❌"}
WEEK = "一二三四五六日"


def label(iso):
    d = datetime.fromisoformat(iso).astimezone(PACIFIC)
    return f"{d.month}/{d.day} {WEEK[d.weekday()]} {d:%H:%M}"


def link(path):
    if not path:
        return "—"
    rel = Path(path).as_posix()
    rel = rel[len("digests/"):] if rel.startswith("digests/") else "../" + rel
    return f"[{Path(path).name}]({rel})"


def render(runs):
    latest = {}
    for r in runs:  # runs are newest first
        latest.setdefault(r["task"], r)
    lines = [
        "# 排程結果總覽",
        "",
        "> 這個檔案由 `scripts/log_run.py` 從 `state/runs.json` 產生，**不要手改**。每個排程跑完都會登記一列，最新的在最上面。",
        f"> 手機或瀏覽器看：[Fall 2026 學期中樞 dashboard]({hub()['dashboard_url']})（claude.ai 側欄已 pin；網址設定在 courses.yaml 的 hub.dashboard_url）。",
        "> 🆕 有新東西　✅ 正常　⏭ 跳過　⚠️ 部分來源失敗／需要重新登入　❌ 失敗",
        "",
        "## 最新狀態",
    ]
    for t in SCHEDULED:
        r = latest.get(t)
        lines.append(f"- {t}：" + (f"{label(r['at'])} {ICON[r['status']]} {r['summary']} → {link(r['output'])}" if r else "尚未執行"))
    lines += ["", "## 紀錄", "", "| 時間（Pacific） | 任務 | 狀態 | 重點 | 輸出 |", "|---|---|---|---|---|"]
    for r in runs:
        lines.append(f"| {label(r['at'])} | {r['task']} | {ICON[r['status']]} | {r['summary']} | {link(r['output'])} |")
    return "\n".join(lines) + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=TASKS)
    ap.add_argument("--status", choices=list(ICON))
    ap.add_argument("--summary", default="")
    ap.add_argument("--output", default="")
    ap.add_argument("--rebuild", action="store_true")
    a = ap.parse_args()
    runs = json.loads(RUNS.read_text(encoding="utf-8")) if RUNS.exists() else []
    if not a.rebuild:
        if not (a.task and a.status):
            ap.error("--task and --status are required unless --rebuild")
        runs.append({"at": now_pacific().isoformat(timespec="seconds"), "task": a.task, "status": a.status,
                     "summary": a.summary.replace("|", "／"), "output": a.output.replace("\\", "/")})
    runs.sort(key=lambda r: datetime.fromisoformat(r["at"]), reverse=True)
    RUNS.write_text(json.dumps(runs, ensure_ascii=False, indent=1), encoding="utf-8")
    INDEX.write_text(render(runs), encoding="utf-8")
    print(f"runs: {len(runs)}; wrote {INDEX.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
