# A4: Bug Hunt

> 來源：Canvas assignment 11814804（https://canvas.uw.edu/courses/1917417/assignments/11814804），抓取 2026-11-02 20:17 PST。
> 這個檔案由 `scripts/assignment_specs.py` 產生，內容是原文，每次來源有變動就整份重寫，不要手改。整理過的版本在 README.md。

- 截止（Canvas `due_at`）：2026-11-01 (Sun) 11:59 PM PST

## Canvas 作業說明

（空白）

## Starter repo README（uw-python-fall2026/assignment-4-mileschintw，blob 5e06266）

# Assignment 4: Help desk bug hunt (60 points)

A small help desk program has bugs in it. Your job is to **find them, prove they are real, and fix them**,
and to leave behind a test for each one so the bug can never quietly come back.

This is a warm-up for working with AI assistants, and **using one is optional**. Assistants are fast at
suggesting bugs and often wrong about them: they will report problems that are not problems and miss
real ones. Whoever the suggestion comes from (an assistant, a friend, your own eyes), it is only a
**suspicion** until a test proves it. This assignment is designed to build that habit. 


> [!IMPORTANT]
> **Please keep your AI history.** I am not asking you to submit your conversations with an AI assistant,
> and nothing in your grade depends on them. But please do not delete them until the course grades are final.
> If a question ever comes up about how a submission was produced, your own record is the clearest way to
> show your work, and it protects you from being assumed to have done something you did not. If you did not
> use an AI assistant, there is nothing to keep.

## The code

`help_desk.py` is built from the pieces from class: a dynamic array, a stack, a queue, and a few functions
that use them to run a help desk, plus a bracket checker. Running a help desk means that tickets are submitted, they are addressed in order, and it's possible to "fix" the ticket in the wrong way, so a closed ticket can be un-done. 

Read the docstrings. **Each docstring says what the function must do, and that is the only definition of
"correct".** If the code disagrees with its docstring, that is a bug. 

There are several bugs. They are not all the same kind: some give a wrong answer, some crash where they
should not, and some are about speed.

## What to do

1. **Hunt.** Read the code, run it, try things, and (if you like) ask an assistant for suspects.
2. **Prove it.** For each suspicion, write a test in `test_regressions.py`:
   - If you think it is a **bug**, write a test that **fails on `help_desk_original.py`** (an untouched copy of
     the code you were given) and **passes after you fix `help_desk.py`**.
   - If you checked a suspicion and the code was **fine**, write a test that **passes on both**.
3. **Fix** `help_desk.py`. Keep every function name and docstring contract. Do not edit `help_desk_original.py`.
4. **Record.** Fill in the table in `FINDINGS.md`: one row for each suspicion you looked into, with its status and
   the name of its test. Then answer the three reflection questions.

You can run the same tests as the autograder on your computer:

```
python3 -m unittest test_regressions -v     # your tests, on your fixed code
python3 -m unittest test_already_correct -v # behavior that worked and must keep working
python3 check_hunt.py                       # everything the checker looks at, with a summary
```

To test the original on its own, a quick way is to temporarily copy `help_desk_original.py` over
`help_desk.py` in a scratch folder, or just run `python3 check_hunt.py`, which does it for you.

## Rules for the tests

- Allowed imports: `unittest`, `random`, `time`, `copy`, `itertools`, `math`, `string`, `collections`, and
  anything from `help_desk`.
- Not allowed: reading files, `inspect`, `os`, `sys`, `eval`/`exec`, `sleep`, or anything with a double
  underscore such as `__code__`. Test what the functions **do**, not how they are written.
- A test can measure its own time (`time.time()`) if the thing you suspect is speed.
- Use `random.Random(seed)` instead of unseeded `random`, so a test gives the same answer every time.

## Points

| Part | Points | Shown on GitHub? |
| --- | --- | --- |
| Your tests all pass on your fixed code (at least 3 tests) | 4 | yes |
| Behavior that was already correct still works (`test_already_correct.py`; needs at least one change to `help_desk.py`) | 8 | yes |
| `FINDINGS.md` table: at least 4 rows, and each row's test really behaves as the row says | 6 | yes |
| `FINDINGS.md` reflection answered | 6 | yes |
| Each real bug is fixed | 3 each | after the deadline |
| Each real bug has a regression test of yours that fails on a copy with only that bug | 3 each | after the deadline |

GitHub shows the first 24 points when you push. The remaining 36 are added by the instructor after the
deadline, together with a list of anything that was missed. Changing a function that was not buggy (for
example "fixing" correct code) will fail the already-correct tests and may break a fix.

The reflection is graded on being complete and honest, not on whether you used an AI assistant.

## Submit

Commit and push `help_desk.py`, `test_regressions.py` and `FINDINGS.md` to `master`. Only those three files
are used for grading; changes to anything else in your repo are ignored.

## Starter repo 其他檔案

原檔存在 `repo/` 底下（stub 的 docstring、測試、CI workflow 才是函式規格和配分的細節）。

- [`.github/workflows/classroom.yml`](repo/.github/workflows/classroom.yml)（2294 bytes，blob 423ed3f）
- [`.gitignore`](repo/.gitignore)（58 bytes，blob 538248f）
- [`FINDINGS.md`](repo/FINDINGS.md)（1389 bytes，blob 6a1e359）
- [`check_hunt.py`](repo/check_hunt.py)（11503 bytes，blob aee6603）
- [`help_desk.py`](repo/help_desk.py)（5610 bytes，blob 44a44ce）
- [`help_desk_original.py`](repo/help_desk_original.py)（5610 bytes，blob 44a44ce）
- [`test_already_correct.py`](repo/test_already_correct.py)（3899 bytes，blob e97bb5f）
- [`test_regressions.py`](repo/test_regressions.py)（1067 bytes，blob ef1e774）
