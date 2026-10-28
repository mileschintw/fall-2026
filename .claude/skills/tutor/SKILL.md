---
name: tutor
description: Interactive tutor for a Fall 2026 course, resuming from saved progress. Use when the user runs /tutor <gpu|dsa>, says they want to learn or review course material ("教我 GPU", "繼續上次的進度"), or asks to add a new lecture to their study plan.
argument-hint: <gpu|dsa> [module number | "new"]
---

# /tutor <course> [module | new]

Teaches the user from `learn/<course>/`. Done = one teaching step finished with the user, `learn/<course>/progress.md` updated, and the change committed.

## 1. Load the frame (every time, before saying anything)

1. Read `learn/<course>/CLAUDE.md` (student profile, reply style, module flow) and follow it for the whole session.
2. Read `learn/<course>/progress.md` and `learn/<course>/curriculum.md`.
3. If `learn/<course>/` does not exist (e.g. first `/tutor dsa`): copy the structure of `learn/gpu/` (CLAUDE.md, curriculum.md, progress.md, modules/, exercises/), rewrite the student profile and module map for that course from `<course>/lectures/*/notes.md`, ask the user what they already know, then stop for their answer.

## 2. Check for new course material

List `<course>/lectures/` and `<course>/hw/`. Any lecture date or HW not covered in `curriculum.md`'s 「已涵蓋到」 line is new:
- Has `notes.md`: draft the new module rows (same columns), add them to `curriculum.md` and `progress.md`, and tell the user in one line.
- Folder exists but no `notes.md`: say the notes aren't written yet and offer `/lecture-notes <course> <date>`.

## 3. Pick where to start

- Argument is a module number: start there.
- Argument is `new`: start at the first module added in step 2.
- No argument: resume at 「目前位置 → 下一步」. If the last session ended mid-module, say where it stopped and continue from that step.
- Open with a warm-up from 「待複習」 when it has entries (CLAUDE.md step 1).

## 4. Teach

Follow the module flow in `learn/<course>/CLAUDE.md`. Ground every concept in the course files: cite `notes.md` timestamps `[hh:mm:ss]` and slide pages. Read the relevant `notes.md` sections (and `slides.txt` / the transcript around a timestamp when notes are thin) before teaching a module, not from memory.

- Inline visuals: `show_widget` (call `mcp__visualize__read_me` first, once per session).
- Module main page: write `learn/<course>/modules/NN-slug.html` and publish with the Artifact tool (load the `artifact-design` skill first; first publish needs `icon`). Republish from the same path. Record the URL in `progress.md`.
- Exercises: write `learn/<course>/exercises/NN-slug.cu` (GPU) or `.py` (DSA). For GPU, compile and run it yourself once before giving it to the user (vcvars64 + nvcc as in `gpu/hw/hw2/src/build.bat`), so it is known to build.
- Stop and wait after every question you ask the user. Never answer your own prediction question in the same message.
- Homework that is still open: teach the concept with a different example; don't hand over the graded answer.

## 5. Save progress (end of every session, or when the user leaves)

Update `progress.md`: 目前位置, module status, 觀念掌握 rows with evidence (which question, right/wrong, date), 錯題與錯誤觀念, 待複習 (2–3 questions for next time), and a one-line 上課紀錄 entry with Pacific time (`python scripts/tz.py` if unsure). Then commit only `learn/` (and `.claude/skills/tutor/` if changed):

```
git add learn/<course> && git commit -m "<COURSE> 學習 <MM/DD HH:MM> PT: <模組與一句話進度>"
```
