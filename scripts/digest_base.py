"""No-login part of the morning brief: ICS deadlines (48h), today's classes, fixed reminders, new GitHub repos.
Prints Markdown sections; the browser layer (announcements / Piazza / Teams) is appended by the agent.
Usage: python scripts/digest_base.py [--hours 48]"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ics_fetch import collect  # noqa: E402
from tz import PACIFIC, now_pacific  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIXED = [  # BOOTSTRAP §8 fixed reminders (Pacific)
    ("2026-11-09T16:30", "DSA 期中考：實體紙筆，Moore 220"),
    ("2026-11-17T17:59", "GPU 專題 Proposal（syllabus 11:59 PM / 投影片 5:59 PM）"),
    ("2026-12-01T17:59", "GPU 專題 Design Spec"),
    ("2026-12-09T16:30", "DSA 期末考：實體紙筆，當天要到校"),
    ("2026-12-15T18:30", "GPU 專題發表（12/15–12/17，線上）"),
    ("2026-12-17T23:59", "GPU 專題報告與程式碼，不能延期"),
]
CLASSES = {  # weekday -> list (Mon=0)
    0: ["DSA 4:30–6:20 PM，Moore Hall 220 實體（另開 Zoom）", "GPU TA OH（Diya）6:30 PM，Teams"],
    1: ["GPU 6:30–9:30(9:50) PM，Teams「Weekly Live Lecture」（全線上）", "DSA TA OH（Hongyu）6–8 PM"],
    2: ["DSA 4:30–6:20 PM，Zoom（考試週改實體）"],
    5: ["DSA 老師 OH 9:30–11:00 AM，Zoom"],
}
NO_CLASS = {"2026-11-11": "Veterans Day 停課", "2026-11-25": "感恩節（可能改非同步）"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=48)
    a = ap.parse_args()
    now = now_pacific()
    items, stats = collect()
    print(f"# {now:%Y-%m-%d} 晨報\n")
    print("## 🔴 今明兩天到期")
    n = 0
    for it in items:
        st = datetime.fromisoformat(it["start"]).astimezone(PACIFIC)
        if it["kind"] != "due":
            continue
        end = st + timedelta(days=1) if it["all_day"] else st
        if now <= end and st <= now + timedelta(hours=a.hours):
            when = st.strftime("%m/%d (%a)") + (" 11:59 PM（全天項目，時間以 Canvas 為準）" if it["all_day"] else st.strftime(" %I:%M %p %Z"))
            print(f"- [{it['course']}] {it['summary']} — {when}")
            n += 1
    for iso, label in FIXED:
        t = datetime.fromisoformat(iso).replace(tzinfo=PACIFIC)
        if now <= t <= now + timedelta(days=7):
            print(f"- ⏰ {t:%m/%d (%a) %I:%M %p %Z}：{label}")
            n += 1
    if not n:
        print("- （無）")
    print("\n## 📅 今天的課（地點 / 線上）")
    today = now.strftime("%Y-%m-%d")
    if today in NO_CLASS:
        print(f"- {NO_CLASS[today]}")
    for c in CLASSES.get(now.weekday(), []) or ["- （今天沒有課）"]:
        print(c if c.startswith("- ") else f"- {c}")
    print("\n## 🆕 新 repo（GitHub）")
    try:
        out = subprocess.run(["pwsh", "-NoProfile", "-File", str(ROOT / "scripts/github_assignments.ps1")],
                             capture_output=True, text=True, timeout=90)
        new = [l[4:] for l in out.stdout.splitlines() if l.startswith("NEW ")]
        print("\n".join(f"- {l}" for l in new) if new else "- （無新增）")
        gh_ok = out.returncode == 0
    except Exception as e:  # noqa: BLE001
        print(f"- gh 失敗：{e}")
        gh_ok = False
    print("\n## ⚠️ 資料來源狀態（無需登入的部分）")
    for c, s in stats.items():
        print(f"- ICS {c}：" + (f"通（raw {s['raw']}，採用 {s['kept']}）" if "error" not in s else f"**不通**：{s['error']}"))
    print(f"- GitHub（gh）：{'通' if gh_ok else '**不通**'}")
    (ROOT / "state/last_digest_base.json").write_text(json.dumps({"at": now.isoformat(), "ics": stats, "gh": gh_ok}), encoding="utf-8")


if __name__ == "__main__":
    main()
