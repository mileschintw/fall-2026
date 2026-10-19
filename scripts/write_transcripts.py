"""Write {date: {sha, len, src, vtt|srt}} JSON into <course>/lectures/<date>/transcript.<ext>, verifying sha256."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data_path, course, ext = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.loads(Path(data_path).read_text(encoding="utf-8"))
for date, d in data.items():
    body = d[ext]
    ok = hashlib.sha256(body.encode("utf-8")).hexdigest() == d["sha"] and len(body) == d["len"]
    out = ROOT / course / "lectures" / date / f"transcript.{ext}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body.encode("utf-8"))  # keep original line endings
    print(date, "sha_ok" if ok else "SHA_MISMATCH", len(body), out.relative_to(ROOT))
