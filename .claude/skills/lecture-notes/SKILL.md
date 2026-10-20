---
name: lecture-notes
description: Produce lecture notes for a Fall 2026 class from its recording transcript plus slides. Use when the user runs /lecture-notes <gpu|dsa> <YYYY-MM-DD>, asks for notes on a lecture, or a scheduled task asks for the weekly lecture notes.
argument-hint: <gpu|dsa> <YYYY-MM-DD>
---

# /lecture-notes <gpu|dsa> <YYYY-MM-DD>

Writes `<course>/lectures/<date>/notes.md` in 繁體中文（術語保留英文）. Done = notes.md has every section of step 4, and every file this run wrote is listed in the final reply.

Browser work goes through Playwright (`python scripts/pw_run.py`, see CLAUDE.md), one call at a time: all calls drive the same page. The built-in browser cannot open the UW login domain.
- Exit 3 = login page (IdP, Microsoft login, or `canvas.uw.edu/login/oauth2/confirm`): **stop** and report "需要重新登入：<來源>". Never type passwords or click authorize.
- Exit 1 = snippet error: rerun the same command once; if it fails again, stop and report the first error line.
- `pw_run.py` writes results straight to the file, so large transcripts never go through chat. Delete every `state/_*.tmp` before finishing.

## 1. Get the transcript (skip if the file already exists)

- **GPU**: `gpu/lectures/<date>/transcript.vtt`. If missing:
  `python scripts/pw_run.py scripts/browser/sharepoint.js state/_gpu.tmp --pre "window.SKIP_DATES=['<every date already under gpu/lectures/>']" --url "https://uwnetid.sharepoint.com/sites/og_EEP_524_A_B_-_GPU_Computing/Shared%20Documents/Forms/AllItems.aspx"`, then `python scripts/write_transcripts.py state/_gpu.tmp gpu vtt`.
- **DSA**: `dsa/lectures/<date>/transcript.srt`. If missing:
  `python scripts/pw_run.py scripts/browser/panopto.js state/_dsa.tmp --pre "window.SKIP_IDS=['<every Viewer session id in dsa/lectures/README.md>']" --url https://uw.hosted.panopto.com/Panopto/Pages/Home.aspx`.
  The keys of `state/_dsa.tmp` are Panopto StartTime dates, which can be the upload date. The class date is the one in the Canvas module title (`scripts/browser/canvas.js` → `mods`). Rename any key that differs to the class date, then run `python scripts/write_transcripts.py state/_dsa.tmp dsa srt`.
- `write_transcripts.py` prints `sha_ok` per file. `SHA_MISMATCH` means a broken download: delete that transcript and rerun the fetch once.
- The result has no entry for `<date>`: the recording is not published yet. Stop and report "尚未發布".
- Add a row for each new transcript to `<course>/lectures/README.md`, with the same columns as the existing rows.

## 2. Get the slides

- Find the file ID:
  - GPU: Canvas Files. Known IDs: L1 `154353784`, L2 `154353786`. For later lectures, run `scripts/browser/canvas.js` and take the `files` entry whose name is `Au26_GPU-Compute_Lecture<N>.pdf`.
  - DSA: `/courses/1917417/files` returns 403. Run `scripts/browser/canvas.js` and use the `mods` item of type `File` in the module item whose title names this class (e.g. "Class 6 outline…"). Its `id` is the file ID.
  - No matching file yet: write notes from the transcript alone and say "講義尚未發布" in the 來源 line. Use only this lecture's file.
- Extract the text: `python scripts/pw_run.py scripts/browser/pdf_text.js state/_slides.tmp --pre "window.COURSE=<1917398|1917417>; window.FILE_ID=<id>" --url https://canvas.uw.edu/courses/<course id>`. Write its `text` field to `<course>/lectures/<date>/slides.txt`.

## 3. Read

- Condense the transcript before reading it: `python scripts/condense_transcript.py <course>/lectures/<date>/transcript.<vtt|srt> state/_condensed.tmp` (one `[hh:mm:ss]` line per minute). Read all of `state/_condensed.tmp`, start to end.
- Textbook mapping: GPU → PMPP 4th ed. Get the chapters for this lecture from `python scripts/pw_run.py scripts/browser/canvas_page.js state/_page.tmp --pre "window.COURSE=1917398; window.PAGE='weekly-reading-sets'" --url https://canvas.uw.edu/courses/1917398`. DSA → Grokking Algorithms. The course assigns no chapters, so label any chapter mapping as your own (自行對照).
- Cross-check against `gpu/assignments.md` / `dsa/assignments.md` for related deadlines.

## 4. Write notes.md with these sections

```
# <COURSE> <Lecture N | Class N> — <date>（<topic>）
> 來源：transcript（cues / 長度）、slides（檔名, 頁數）、閱讀章節。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：<聽錯的詞> → <正確術語>；…
## 重點摘要
## 名詞解釋
## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）
## 和作業 / 考試的關聯
## 還要釐清的問題
```

Rules:
- Every claim in 老師強調 carries a transcript timestamp. Paraphrase; keep any direct quote under 15 words and taken verbatim from the transcript.
- Slide-only material (not said in class) is marked（講義 pN）instead of a timestamp.
- When the transcript contradicts the slides, the transcript wins (BOOTSTRAP §3). Note the conflict.
- Course AI policy: the user has said they don't mind. If the notes would amount to producing a GPU homework or project solution, add a one-line reminder.
