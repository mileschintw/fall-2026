"""Condense a WEBVTT/SRT transcript to plain text with a [hh:mm:ss] marker each new minute.
Usage: python scripts/condense_transcript.py <transcript.vtt|.srt> [out.txt]"""
import sys
from pathlib import Path

src = Path(sys.argv[1])
raw = src.read_text(encoding="utf-8").replace("\r", "")
out, cur = [], None
for block in raw.split("\n\n"):
    lines = [l for l in block.split("\n") if l]
    t = next((l for l in lines if "-->" in l), None)
    if not t:
        continue
    txt = " ".join(lines[lines.index(t) + 1:])
    stamp = t[:8].replace(",", ".")
    if stamp[:5] != cur:
        out.append(f"\n[{stamp}] ")
        cur = stamp[:5]
    out.append(txt + " ")
text = "".join(out).strip() + "\n"
if len(sys.argv) > 2:
    Path(sys.argv[2]).write_text(text, encoding="utf-8")
else:
    sys.stdout.write(text)
