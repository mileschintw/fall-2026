---
name: lecture-notes
description: Produce lecture notes for a Fall 2026 class from its recording transcript plus slides. Use when the user runs /lecture-notes <gpu|dsa> <YYYY-MM-DD>, asks for notes on a lecture, or a scheduled task asks for the weekly lecture notes.
argument-hint: <gpu|dsa> <YYYY-MM-DD>
---

# /lecture-notes <gpu|dsa> <YYYY-MM-DD>

Writes `<course>/lectures/<date>/notes.md` in 繁體中文（術語保留英文）.

## 1. Get the transcript (skip if the file already exists)

- **GPU**: `gpu/lectures/<date>/transcript.vtt`. If missing, open the SharePoint document library in the built-in browser, set `window.SKIP_DATES` to the dates already saved, run `scripts/browser/sharepoint.js`, then save the oversized result:
  `python scripts/save_browser_result.py <tool-results file> state/_gpu.tmp && python scripts/write_transcripts.py state/_gpu.tmp gpu vtt`
- **DSA**: `dsa/lectures/<date>/transcript.srt`. If missing, open any `uw.hosted.panopto.com` page, run `scripts/browser/panopto.js` (`window.LIST_ONLY=true` first to see sessions and dates), then the same two scripts with `dsa srt`. Panopto StartTime can be the upload date. Use the class date from the Canvas module title and update `dsa/lectures/README.md`.
- Login-page check: if `location.origin` is an IdP, Microsoft login, or `canvas.uw.edu/login/oauth2/confirm`, **stop**. Report "需要重新登入：<來源>". Never type passwords or click authorize.
- Large browser results never go through chat. The harness saves them to `tool-results/*.txt` and the scripts above extract them. Pad a result with `_pad:'x'.repeat(60000)` to force that save.

## 2. Get the slides

- GPU: Canvas Files. Known IDs: L1 `154353784`, L2 `154353786`. Others: `/api/v1/courses/1917398/files?search_term=Lecture`.
- DSA: Canvas module items (`/courses/1917417/files` returns 403, so use `/api/v1/courses/1917417/files/<id>` from module items).
- Extract the text with pdf.js (cdnjs 4.0.379) in a Canvas tab, as in BOOTSTRAP §4.1. Save it to `<course>/lectures/<date>/slides.txt`.

## 3. Read

- Condense the transcript to timestamped plain text, one line per minute, before reading it. The code is in `scripts/condense_transcript.py`.
- Textbook mapping: GPU → PMPP 4th ed. Chapters come from the Canvas page `weekly-reading-sets`. DSA → Grokking Algorithms.
- Cross-check against `gpu/assignments.md` / `dsa/assignments.md` for related deadlines.

## 4. Write notes.md with these sections

```
# <COURSE> <Lecture N> — <date>（<topic>）
> 來源：transcript（cues / 長度）、slides（檔名, 頁數）、閱讀章節。逐字稿是自動產生，專有名詞可能聽錯。
## 重點摘要
## 名詞解釋
## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）
## 和作業 / 考試的關聯
## 還要釐清的問題
```

Rules:
- Every claim in 老師強調 carries a transcript timestamp. Do not invent quotes. Paraphrase, and keep any direct quote under 15 words.
- When the transcript contradicts the slides, the transcript wins (BOOTSTRAP §3). Note the conflict.
- Course AI policy: the user has said they don't mind. If the notes would amount to producing a GPU homework or project solution, add a one-line reminder.
