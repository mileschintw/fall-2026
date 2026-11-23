"""GPU final project leaderboard (public page, no login) -> Markdown lines for the morning brief.

Usage:
  python scripts/leaderboard.py           # print the report, do not touch state
  python scripts/leaderboard.py --save    # same, then write state/leaderboard_seen.json

Reads courses.yaml courses.gpu.leaderboard (by_tier URL, team name). Compares with state/leaderboard_seen.json
(the last saved board) and reports: whether the board was regraded, our team's rows (valid, by tier) or our
invalid entry with its reason, and the leader of each tier.
Exit codes: 0 ok; 1 fetch or parse failed (prints FETCH_FAILED / PARSE_FAILED, state untouched: a failed fetch is
not an empty board).
"""
import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tz import to_pacific  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state" / "leaderboard_seen.json"


class Board(HTMLParser):
    """Collects the summary line, footer, and every table with the h2 (category) / h3 (tier) it sits under."""

    def __init__(self):
        super().__init__()
        self.h2 = self.h3 = ""
        self.tag = None          # 'h2' | 'h3' | 'summary' | 'footer' while inside one
        self.buf = ""
        self.summary = self.footer = ""
        self.tables, self.table, self.row, self.cell = [], None, None, None

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "")
        if tag in ("h2", "h3", "footer") or (tag == "p" and cls == "summary"):
            self.tag, self.buf = ("summary" if tag == "p" else tag), ""
        elif tag == "table":
            self.table = {"category": self.h2, "section": self.h3, "headers": [], "rows": []}
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = ""

    def handle_endtag(self, tag):
        if self.tag and tag == {"summary": "p"}.get(self.tag, self.tag):
            text = " ".join(self.buf.split())
            if self.tag == "h2":
                self.h2, self.h3 = text, ""
            elif self.tag == "h3":
                self.h3 = text
            else:
                setattr(self, self.tag, text)
            self.tag = None
        elif tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join(self.cell.split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row and not self.table["headers"]:
                self.table["headers"] = self.row   # first row is the <thead> row
            elif self.row:
                self.table["rows"].append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data
        if self.tag:
            self.buf += data


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "fall-2026-hub/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def as_dicts(t):
    return [dict(zip(t["headers"], r)) for r in t["rows"]]


def pacific_updated(footer):
    m = re.search(r"Updated (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC", footer)
    if not m:
        return None, None
    dt = datetime.fromisoformat(f"{m[1]}T{m[2]}:00+00:00")
    p = to_pacific(dt)
    return dt.isoformat().replace("+00:00", "Z"), f"{p:%m/%d} {p:%I:%M %p} {p.tzname()}".replace(" 0", " ")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--html", help="parse a saved copy of board_by_tier.html instead of fetching (for testing)")
    a = ap.parse_args()
    cfg = yaml.safe_load((ROOT / "courses.yaml").read_text(encoding="utf-8"))["courses"]["gpu"]["leaderboard"]
    team = cfg["team"]
    try:
        html = Path(a.html).read_text(encoding="utf-8") if a.html else fetch(cfg["by_tier"])
    except Exception as e:  # noqa: BLE001
        print(f"FETCH_FAILED: {type(e).__name__}: {e}")
        return 1
    b = Board()
    b.feed(html)
    updated_utc, updated_pt = pacific_updated(b.footer)
    if not b.summary or not updated_utc:
        print(f"PARSE_FAILED: summary={b.summary!r} footer={b.footer[:80]!r}")
        return 1

    ours, leaders, invalid_ours = [], [], []
    for t in b.tables:
        rows = as_dicts(t)
        if re.search(r"invalid", t["category"] + " " + t["section"], re.I):
            invalid_ours += [r for r in rows if team in " ".join(r.values())]
            continue
        if not re.match(r"Tier", t["section"]):  # efficiency ranking etc.
            continue
        cat = t["category"].replace(" category", "")
        tier = t["section"].split(" (")[0]
        if rows:
            r0 = rows[0]
            leaders.append(f"{cat} {tier}：{r0.get('Team')} {r0.get('images/s')} images/s（{len(rows)} 隊）")
        for r in rows:
            if r.get("Team") == team:
                ours.append({"category": cat, "tier": tier, **r})
    if not invalid_ours and team in html and not ours:  # our name is on the page but not in a ranked table
        invalid_ours.append({"note": "名字出現在頁面上，但不在任何 tier 的排名表（可能在 invalid 清單），請人工看"})

    prev = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    regraded = prev.get("updated_utc") != updated_utc
    ours_changed = prev.get("ours") != ours or prev.get("invalid_ours") != invalid_ours

    print(f"STATUS: 通（board 更新於 {updated_pt}；{b.summary.rstrip('.')}）")
    print(f"- board {'有新一輪評分' if regraded and prev else ('第一次記錄' if not prev else '沒有新一輪評分')}："
          f"更新於 {updated_pt}（{updated_utc}），{b.summary.rstrip('.')}")
    if ours:
        for r in ours:
            print(f"- **{team}**：{r['category']} {r['tier']} 第 {r.get('# in tier')} 名（overall #{r.get('# overall')}），"
                  f"{r.get('images/s')} images/s，{r.get('% roofline')}% roofline，top-1/top-5 err {r.get('top-1 err %')}%/"
                  f"{r.get('top-5 err %')}%，batch {r.get('batch')}，SM {r.get('SM MHz')} MHz，submitted {r.get('submitted')}"
                  + ("（新）" if ours_changed else ""))
    if invalid_ours:
        for r in invalid_ours:
            print(f"- ⚠️ **{team} 在 invalid 清單**：{json.dumps(r, ensure_ascii=False)}")
    if not ours and not invalid_ours:
        print(f"- {team}：還沒出現在 board 上（等 grader 下一輪）")
    print("- 各 tier 第一名：" + ("；".join(leaders) if leaders else "無"))
    print(f"CHANGED: {'yes' if (regraded or ours_changed) else 'no'}")

    if a.save:
        STATE.write_text(json.dumps({"updated_utc": updated_utc, "summary": b.summary, "ours": ours,
                                     "invalid_ours": invalid_ours, "leaders": leaders,
                                     "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds")},
                                    ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
