"""Timezone helpers. Always tz-aware; never hard-code -7/-8 (DST ends 2026-11-01)."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

PACIFIC = ZoneInfo("America/Los_Angeles")


def to_pacific(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(PACIFIC)


def parse_utc(s: str) -> datetime:
    """Parse Canvas due_at like 2026-11-07T07:59:59Z."""
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def fmt(dt: datetime) -> str:
    p = to_pacific(dt)
    return p.strftime("%Y-%m-%d (%a) %I:%M %p ") + p.tzname()


def now_pacific() -> datetime:
    return datetime.now(PACIFIC)


if __name__ == "__main__":
    for s in ("2026-10-21T00:59:59Z", "2026-11-07T07:59:59Z"):
        print(s, "->", fmt(parse_utc(s)))
