---
name: tutor
description: Tutor for a Fall 2026 course (gpu|dsa), resuming from learn/<course>/progress.md. Use when the user runs /tutor, asks to be taught or quizzed on GPU/DSA material ("教我 GPU", "繼續上次"), or asks to add a lecture to their study plan (not to write lecture notes — that is /lecture-notes).
argument-hint: <gpu|dsa> [module number | "new"]
---

# /tutor <course> [module | new]

Teaches the user from `learn/<course>/`. How to teach lives in `learn/<course>/CLAUDE.md`; this skill only loads it, picks the starting point, and saves progress.

Done = the user has answered every question asked this session, `learn/<course>/progress.md`'s 目前位置 names the next concrete step (module # / flow step / question #), and the change is committed.

## 1. Load the frame (before saying anything)

Read `learn/<course>/CLAUDE.md`, `progress.md` and `curriculum.md`, and follow CLAUDE.md for the whole session.

If `learn/<course>/` does not exist: create the same file skeleton as `learn/gpu/` (CLAUDE.md, curriculum.md, progress.md, modules/, exercises/) with course-specific content only — module map drawn from `<course>/lectures/*/notes.md`; leave the student goal and starting level empty. Ask the user for their goal and what they already know, then stop and wait.

## 2. Check for new course material

Use the rule on curriculum.md's 「已涵蓋到」 line to find new lectures:
- New lecture with `notes.md`: add module rows (same columns) to `curriculum.md` and `progress.md`, move the 「已涵蓋到」 date forward, and tell the user in one line.
- Lecture folder without `notes.md`: say the notes aren't written yet and offer `/lecture-notes <course> <date>`.

## 3. Pick where to start

- Module number given: start there.
- `new`: start at the first module added in step 2.
- Otherwise: resume at progress.md 「目前位置」, at the exact flow step and question it names.

## 4. Teach

Follow `learn/<course>/CLAUDE.md`. Tool notes:
- Inline visuals: `show_widget` (call `mcp__visualize__read_me` once per session first).
- Module page: load the `artifact-design` skill, write `learn/<course>/modules/NN-slug.html`, publish with the Artifact tool (`icon` on first publish), republish from the same path.
- Exercises: build per `learn/<course>/exercises/README.md`.

## 5. Save progress (end of every session, or when the user leaves)

Update `progress.md` as CLAUDE.md's 「進度怎麼記」 says (Pacific time: `python -c "import sys; sys.path.insert(0,'scripts'); import tz; print(tz.now_pacific())"`). Commit only `learn/<course>`:

```
git add learn/<course> && git commit -m "<COURSE> 學習 <MM/DD HH:MM> PT: <模組與一句話進度>"
```
