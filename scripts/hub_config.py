"""Read the hub section of courses.yaml (the one place to change when the claude.ai account changes).

Usage:
  python scripts/hub_config.py dashboard_url        # print one value
  python scripts/hub_config.py scheduled_tasks      # print the task list as JSON
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def hub():
    return yaml.safe_load((ROOT / "courses.yaml").read_text(encoding="utf-8"))["hub"]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    v = hub()[sys.argv[1]] if len(sys.argv) > 1 else hub()
    print(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, indent=1))
