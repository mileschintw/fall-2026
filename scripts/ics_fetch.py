"""Fetch both Canvas course ICS feeds (no login), drop stale past-year items, print/emit in Pacific.

Usage: python scripts/ics_fetch.py [--json out.json] [--days N]
Reads CANVAS_ICS_GPU / CANVAS_ICS_DSA from .env (never commit .env).
"""
import argparse
import json
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tz import PACIFIC, now_pacific  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CUTOFF = datetime(2026, 9, 1, tzinfo=PACIFIC)  # BOOTSTRAP §3.2: only items on/after 2026-09-01
COURSES = {"GPU": "CANVAS_ICS_GPU", "DSA": "CANVAS_ICS_DSA"}


def load_env():
    env = {}
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def unfold(text):
    lines = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def unescape(v):
    return v.replace("\\n", "\n").replace("\\,", ",").replace("\\;", ";").replace("\\\\", "\\")


def parse_dt(params, value):
    """Return (datetime in Pacific, all_day)."""
    if "VALUE=DATE" in params or (len(value) == 8 and value.isdigit()):
        d = date(int(value[:4]), int(value[4:6]), int(value[6:8]))
        return datetime(d.year, d.month, d.day, tzinfo=PACIFIC), True
    if value.endswith("Z"):
        dt = datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    else:
        tzid = next((p.split("=", 1)[1] for p in params if p.startswith("TZID=")), None)
        from zoneinfo import ZoneInfo
        dt = datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=ZoneInfo(tzid) if tzid else PACIFIC)
    return dt.astimezone(PACIFIC), False


def parse_ics(text):
    events, cur = [], None
    for line in unfold(text):
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT" and cur is not None:
            events.append(cur)
            cur = None
        elif cur is not None and ":" in line:
            head, value = line.split(":", 1)
            name, *params = head.split(";")
            if name in ("DTSTART", "DTEND"):
                cur[name], all_day = parse_dt(params, value)
                if name == "DTSTART":
                    cur["all_day"] = all_day
            elif name in ("SUMMARY", "LOCATION", "URL", "UID"):
                cur[name] = unescape(value)
    return events


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "fall-2026-hub"})
    with urllib.request.urlopen(req, timeout=30) as r:
        ctype = r.headers.get("Content-Type", "")
        body = r.read().decode("utf-8", "replace")
    if "text/calendar" not in ctype or "BEGIN:VCALENDAR" not in body:
        raise RuntimeError(f"not an ICS response (Content-Type={ctype!r})")
    return body


def kind(summary, uid):
    s = summary.lower()
    if "assignment" in (uid or "") or any(k in s for k in ("hw", "homework", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "exam", "midterm", "project", "task")):
        return "due"
    return "event"


def collect():
    env = load_env()
    out, stats = [], {}
    for course, key in COURSES.items():
        url = env.get(key)
        if not url:
            stats[course] = {"error": f"{key} missing in .env"}
            continue
        try:
            evs = parse_ics(fetch(url))
        except Exception as e:  # noqa: BLE001
            stats[course] = {"error": str(e)}
            continue
        kept = [e for e in evs if e.get("DTSTART") and e["DTSTART"] >= CUTOFF]
        stats[course] = {"raw": len(evs), "kept": len(kept)}
        for e in kept:
            out.append({
                "course": course,
                "summary": e.get("SUMMARY", ""),
                "start": e["DTSTART"].isoformat(),
                "all_day": e.get("all_day", False),
                # DSA location field is unreliable (BOOTSTRAP §3.2)
                "location": None if course == "DSA" else e.get("LOCATION"),
                "kind": kind(e.get("SUMMARY", ""), e.get("UID")),
                "url": e.get("URL"),
            })
    out.sort(key=lambda x: x["start"])
    return out, stats


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--days", type=int, default=None, help="only show items within N days from now")
    a = ap.parse_args()
    items, stats = collect()
    print("stats:", json.dumps(stats))
    now = now_pacific()
    for it in items:
        st = datetime.fromisoformat(it["start"]).astimezone(PACIFIC)
        last = st + timedelta(days=1) if it["all_day"] else st  # all-day: due sometime that day (time only in Canvas)
        if a.days is not None and not (now - timedelta(hours=1) <= last and st <= now + timedelta(days=a.days)):
            continue
        when = st.strftime("%m/%d %a") + ("" if it["all_day"] else st.strftime(" %I:%M %p ") + st.tzname())
        print(f"[{it['course']}] {when}  {it['summary']}")
    if a.json:
        Path(a.json).write_text(json.dumps({"fetched_at": now.isoformat(), "stats": stats, "items": items}, ensure_ascii=False, indent=1), encoding="utf-8")
    if any("error" in s for s in stats.values()):
        sys.exit(2)


if __name__ == "__main__":
    main()
