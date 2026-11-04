# A5: BSTs and AVLs

> 來源：Canvas assignment 11814818（https://canvas.uw.edu/courses/1917417/assignments/11814818），抓取 2026-11-04 07:44 PST。
> 這個檔案由 `scripts/assignment_specs.py` 產生，內容是原文，每次來源有變動就整份重寫，不要手改。整理過的版本在 README.md。

- 截止（Canvas `due_at`）：2026-11-22 (Sun) 11:59 PM PST

## Canvas 作業說明

（空白）

## Starter repo README（uw-python-fall2026/assignment-5-mileschintw，blob 2d037e3）

# Assignment 5: Binary search trees (150 points)

One repo, one submission, two parts:

| Folder | Part | AI assistant? | Points |
| --- | --- | --- | --- |
| `part1/` | **Write a binary search tree**, then measure it against an AVL tree. Instructions in `part1/README.md`. | **No** | 50 |
| `part2/` | **Mutant hunt**: write tests that catch buggy trees. Instructions in `part2/README.md`. | Yes, in `part2/` only | 100 |

**Due: Sunday, November 22, 11:59 pm.** I suggest doing Part 1 before the midterm on November 9: it is the best
practice you'll get for the tree questions.

## AI, and the exams

Part 1 is for you to do alone, no AI assistance. Part 2 allows an AI assistant, but only for the files in `part2/`. If you point an
assistant or agent at this repo, tell it to stay out of `part1/`, and check that it did.

The midterm and final are on paper, without AI. They may ask you to write and trace tree code (Part 1) and
to find bugs and write the tests that catch them (Part 2). Whatever help you use, make sure you can do both
yourself.

## Points

| What | Points | Graded |
| --- | --- | --- |
| Part 1 tests | 35 | GitHub, when you push |
| Part 1 `ANALYSIS.md` | 15 | by hand |
| Part 2 gate, practice mutants, AI note | 40 | GitHub, when you push |
| Part 2 hidden mutants | 60 | after the deadline |
| **Total** | **150** | |

The Actions tab on GitHub shows the 75 points it can check. The rest is added after the deadline.

## Working in this repo

Open the whole repo in PyCharm. Run each part's commands from inside its folder:

```
cd part1
python3 -m unittest bst_test -v
python3 compare.py

cd ../part2
python3 check_tests.py
```

If PyCharm can't find a module (`ModuleNotFoundError`), right-click `part1` and `part2` and choose
**Mark Directory as > Sources Root** for each.

## Submit

Commit and push to `master` before the deadline, with both parts in it. We grade the last push before the
deadline. Check the Actions tab after your last push.

Do not edit the provided test and helper files, or the workflow in `.github`. The instructor runs the
original files.

## Starter repo 其他檔案

原檔存在 `repo/` 底下（stub 的 docstring、測試、CI workflow 才是函式規格和配分的細節）。

- [`.github/workflows/classroom.yml`](repo/.github/workflows/classroom.yml)（5428 bytes，blob 59e7d29）
- [`.gitignore`](repo/.gitignore)（58 bytes，blob 538248f）
- [`part1/ANALYSIS.md`](repo/part1/ANALYSIS.md)（1622 bytes，blob fde4c02）
- [`part1/README.md`](repo/part1/README.md)（4353 bytes，blob b50d4f4）
- [`part1/avl.py`](repo/part1/avl.py)（2434 bytes，blob bc42062）
- [`part1/bst.py`](repo/part1/bst.py)（1758 bytes，blob 52d6268）
- [`part1/bst_test.py`](repo/part1/bst_test.py)（4054 bytes，blob 8629750）
- [`part1/compare.py`](repo/part1/compare.py)（1943 bytes，blob bf3aed8）
- [`part1/tree_tools.py`](repo/part1/tree_tools.py)（1614 bytes，blob 63178a1）
- [`part2/AI_NOTE.md`](repo/part2/AI_NOTE.md)（785 bytes，blob 96a9ef9）
- [`part2/README.md`](repo/part2/README.md)（4679 bytes，blob 8b88601）
- [`part2/bst_reference.py`](repo/part2/bst_reference.py)（2802 bytes，blob 248176e）
- [`part2/check_tests.py`](repo/part2/check_tests.py)（9002 bytes，blob 30d89d9）
- [`part2/practice_mutants/p1.py`](repo/part2/practice_mutants/p1.py)（2783 bytes，blob 49bee7d）
- [`part2/practice_mutants/p2.py`](repo/part2/practice_mutants/p2.py)（2881 bytes，blob 409cf85）
- [`part2/practice_mutants/p3.py`](repo/part2/practice_mutants/p3.py)（2756 bytes，blob 07afe5f）
- [`part2/practice_mutants/p4.py`](repo/part2/practice_mutants/p4.py)（2839 bytes，blob 5cae3af）
- [`part2/test_bst.py`](repo/part2/test_bst.py)（1148 bytes，blob bf96623）
- [`part2/tree_tools.py`](repo/part2/tree_tools.py)（1614 bytes，blob 63178a1）
