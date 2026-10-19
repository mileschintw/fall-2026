"""Extract the JSON object a browser javascript_tool call returned, from the harness's saved
oversized-result file (tool-results/*.txt), so big payloads (VTT/SRT) never pass through chat.

Usage: python scripts/save_browser_result.py <saved-result.txt> <out.json>
"""
import json
import sys
from pathlib import Path

src, dst = sys.argv[1], sys.argv[2]
blocks = json.loads(Path(src).read_text(encoding="utf-8"))
text = blocks[0]["text"]
obj, _ = json.JSONDecoder().raw_decode(text.lstrip())
Path(dst).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
print("keys:", list(obj) if isinstance(obj, dict) else type(obj).__name__)
