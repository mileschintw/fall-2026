# A2: Lists, lists and more lists

> 來源：Canvas assignment 11814777（https://canvas.uw.edu/courses/1917417/assignments/11814777），抓取 2026-10-24 21:48 PDT。
> 這個檔案由 `scripts/assignment_specs.py` 產生，內容是原文，每次來源有變動就整份重寫，不要手改。整理過的版本在 README.md。

- 截止（Canvas `due_at`）：2026-10-18 (Sun) 11:59 PM PDT

## Canvas 作業說明

Objectives
Get familiar with unit testing and timing tools in Python
Implementing data structures with uniform interfaces
Analyze and compare implementations 
Overview

This is your first assignment with two new tools: Python's `unittest` framework, which checks your code automatically, and **timing code**, which measures how fast your code really runs.

You will build the same job, a list of values, in two different ways and then compare them:

an array list: values live in a fixed-size block of slots (like Python's own `list`, but you build the growing yourself)
a singly linked list: each value lives in its own node, and nodes point to the next node

Then you will time your structures against Python's built-in `list`, `array.array`, and `deque`, and explain what you see. Reading about Big-O is one thing. Watching a "slow" operation get 10 times slower when you make the list 10 times bigger is another.

Details

The assignment details are on Github. You should be invited to a repo in the course organization (uw-python-fall2026) named something like assignment-2-<githubId>. Pull the repo into PyCharm and follow the instructions in the README.md. 

Submission

When you are done with your assignment: 

Commit and push your code to Github 
Here on Canvas, submit the URL to the repository for the assignment

Your assignment is not considered submitted unless it is pushed to Github AND a link submitted on Canvas before the deadline. The grade will be entered on Canvas, and feedback will be provided on Github.

## Starter repo README（uw-python-fall2026/assignment-2-mileschintw，blob 602c986）

# EE 590a: Data Structures and Algorithms with Python
## Programming Assignment 2: Arrays vs. Linked Lists

## Getting Started

Open your repo in PyCharm the same way you did for Programming Assignment 1
(File -> New Project from VCS, then paste the URL for your repo). You do not need to install
anything new: everything here uses Python's standard library.

## Overview

This is your **first assignment with two new tools**: Python's `unittest` framework, which checks
your code automatically, and **timing code**, which measures how fast your code really runs.

You will build the same job, a list of values, in two different ways and then compare them:

* an **array list**: values live in a fixed-size block of slots (like Python's own `list`, but you build the
  growing yourself)
* a **singly linked list**: each value lives in its own node, and nodes point to the next node

Then you will time your structures against Python's built-in `list`, `array.array`, and `deque`, and
explain what you see. Reading about Big-O is one thing. Watching a "slow" operation get 10 times
slower when you make the list 10 times bigger is another.

## Objectives

* Implement an array that grows when it fills up, and count the work it does
* Implement a linked list and keep its links and its size correct
* Run unit tests, read their output, and use it to find and fix bugs
* Write your own tests
* Measure running time, and connect the numbers to Big-O
* Explain why Python's built-in structures behave the way they do

## The Files

| File | What it is | Do you edit it? |
| --- | --- | --- |
| `array_list.py` | Part B: the array list | **Yes**: you write 6 functions |
| `linked_list.py` | Part C: the linked list | **Yes**: you write 6 functions |
| `array_list_test.py`, `linked_list_test.py` | The provided tests for Parts B and C | No |
| `shared_list_tests.py` | Tests that run on **both** structures | No |
| `list_checks.py` | Helpers that check a list is correct *inside* (see below) | No |
| `student_tests.py` | Part E: you write two tests of your own | **Yes** |
| `analysis.md` | Parts A and D: your written answers | **Yes** |
| `my_timing.py` | Part D: time something yourself | **Yes** (two TODOs) |
| `timing.py` | Part D: the timing experiment | No: just run it |
| `analysis_test.py` | Checks that you filled in `analysis.md` and `my_timing.py` | No |
| `part_e_checks.py` | Checks that your Part E tests are real, passing tests | No |

## What To Do

### Part A: On paper (`analysis.md`)

Before writing any code, answer questions A1-A4 in `analysis.md`. Draw the arrays and
linked lists. Doing this first will save you hours later.

### Part B: The array list (`array_list.py`)

Write the six functions marked `TODO`. Read the comment at the top of the file first: it explains the
representation and **the rules** (for example: you may not use `append`, `insert`, `pop`, or slicing on the
array: you move the values yourself, one at a time). The tests check the rules.

Your array list also keeps a `'moves'` count: how many values it has copied or shifted. This is how
you will *measure work* without a stopwatch. If your counts are right, inserting at the front of a big
list shows up as lots of moves, and appending shows up as almost none.

### Part C: The linked list (`linked_list.py`)

Write the six functions marked `TODO`. The functions have the same names and meanings as the array
list's, so the **same tests** check both. `linked_list_reverse` is the tricky one. Draw it.

### Part D: Timing (`my_timing.py`, `timing.py`, `analysis.md`)

1. Answer predictions P1-P3 in `analysis.md` **before you run any timing code**.
2. Finish the two TODOs in `my_timing.py` and answer T1. You will time the same operation with a
   stopwatch and with `timeit`.
3. Run `python3 timing.py` and paste **all** of its output into `analysis.md`. Answer Q1-Q7 using
   your own numbers.

### Part E: Your own tests (`student_tests.py`)

Write one test for your array list and one for your linked list. Each should check something the
provided tests do not. Make sure they pass.

### A suggested week

* **Days 1-2:** Part A. Array list `TODO 1-3` (length, get, grow).
* **Day 3:** Array list `TODO 4-6` (insert, remove, to_python_list). Don't rush: this is the hardest part.
* **Day 4:** The linked list.
* **Day 5:** Part E. `my_timing.py`.
* **Day 6:** `timing.py` and the analysis.
* **Day 7:** Finish up, make sure everything is committed and pushed.

## A Quick Guide To Testing With `unittest`

A **unit test** is a small function that runs a piece of your code and checks the answer. If you don't get
the answer you expected, the test fails and tells you what went wrong. In `unittest`, a test is a method
whose name starts with `test_`, inside a class that extends `unittest.TestCase`. Every test has three steps:

```python
def test_removing_the_only_value_leaves_the_list_empty(self):
    lst = create_array_list()                       # 1. Set up: make what you need
    array_list_insert_at(lst, 0, 'only')
    removed = array_list_remove_at(lst, 0)          # 2. Execute: do the thing being tested
    self.assertEqual('only', removed)               # 3. Check: is it what you expected?
    self.assertEqual(0, array_list_length(lst))
```

The `assert...` methods are the checks: `assertEqual(expected, actual)`, `assertTrue(x)`,
`assertIsNone(x)`, and `with self.assertRaises(IndexError):` for code that *should* raise an error.

### Running the tests

* **PyCharm:** right-click `array_list_test.py` in the project panel and choose *Run 'Python tests in
  array_list_test.py'*, or click the green arrow next to a single test.
* **Terminal:** `python3 array_list_test.py` (on Windows, `python` instead of `python3`)
* **One test:** `python3 -m unittest array_list_test.ArrayListOnlyTests.test_grow_doubles_the_capacity_and_keeps_the_values`
* **Everything:** `python3 -m unittest discover -p "*test*.py"`

### Reading the results

Each test prints a symbol: `.` passed, `F` **failed** (your code ran but gave a wrong answer), `E` **error**
(your code crashed, or isn't written yet). A summary comes at the end. When something fails, scroll up
to the **first** failure and read from the bottom of that message. Here is a real one:

```text
======================================================================
FAIL: test_get_returns_the_value_at_each_index (array_list_test.ArrayListContractTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "shared_list_tests.py", line 76, in test_get_returns_the_value_at_each_index
    self.assertEqual(value, self.get(lst, index))
AssertionError: 'a' != None
```

The last line is the clue: the test expected `'a'` and your function returned `None`. Fix the first failure,
re-run, repeat. Later failures are often caused by the first one. Work on **one test at a time**: in an
`E`/`F` pile, don't panic; most of them usually disappear together.

### What are the "invariant" checks?

A list can print the right values and still be broken inside: a wrong `size`, a slot that should be empty
but isn't, a link that loops back. `list_checks.py` has `assert_array_list_valid(lst)` and
`assert_linked_list_valid(lst)`, which check the inside of your list and explain the problem. The provided
tests call them after every operation. **You can call them in your own tests**: it is one of the best ways to
catch a bug right where it happens.

## A Quick Guide To Timing

"This operation is O(n)" is a *prediction*. Timing is how you test it.

**Approach 1, a stopwatch:** note the time, do the thing, note the time again.

```python
start = time.perf_counter()        # the current time, in seconds
do_the_thing()
end = time.perf_counter()
print((end - start) * 1_000_000, 'microseconds')
```

**Approach 2, `timeit`:** run something many times and get the total, so you can average.

```python
seconds = timeit.timeit(do_the_thing, number=100)
print(seconds / 100 * 1_000_000, 'microseconds per run')
```

Timing one run is noisy: anything else your computer is doing can change it. Averaging many runs is
steadier, which is why `timing.py` uses `timeit`. Even so, exact numbers differ between computers and
between runs, so **don't compare your numbers to a friend's. Look at how your own numbers change as the
list gets bigger.**

When the size goes up 10x:
* if the time stays about the same, the operation is about **O(1)**
* if the time goes up about 10x, it is about **O(n)**

A tip for `timing.py`: close other programs, and run it twice to see how much the numbers move.

## Rules

* Use only Python's standard library.
* Follow the rules at the top of `array_list.py` and `linked_list.py` (the tests check them).
* **It is NOT okay to put any of this code into ChatGPT or any other AI assistant for help as part of this
  assignment.** The point is to build your own picture of how these structures work, and the
  analysis only makes sense if it is your own timing numbers explained in your own words.
* Any updates or clarifications to the assignment will be noted here and on the class forum.

## Grading Criteria

* 30 points: Array list. The tests in `array_list_test.py` pass (partial credit: the autograder scores them in groups, e.g. "insert", "remove")
* 30 points: Linked list. The tests in `linked_list_test.py` pass (partial credit by group, e.g. "insert", "reverse")
* 10 points: Part E. Two tests of your own that pass and check something meaningful (5 each). The autograder
  confirms each test exists, passes, and checks your code; a person confirms it is meaningful
* 25 points: `analysis.md` and `my_timing.py`. Your drawings, predictions, results, and explanations. We are
  looking for specific answers that use your own numbers, not long ones. 10 of these points are automatic
  (every question answered, results pasted, both `my_timing.py` functions work); the other 15 are
  graded by a person reading your answers
* 5 points: Turned in on time on both Github and Canvas, with at least 3 commits

## Submission

Push your code to Github before the deadline, and submit a link to your Github repo on Canvas.

## Updates to the assignment - Will announce if you need to do

We may periodically deploy updates to the assignment.
You will need to resolve any conflicts that occur. Please come to office hours if you have any issues.

If significant changes have been made, we will do our best to send an announcement to the class.

## Starter repo 其他檔案

原檔存在 `repo/` 底下（stub 的 docstring、測試、CI workflow 才是函式規格和配分的細節）。

- [`.github/workflows/classroom.yml`](repo/.github/workflows/classroom.yml)（13612 bytes，blob 1aa51e8）
- [`.gitignore`](repo/.gitignore)（51 bytes，blob 4a74d7e）
- [`analysis.md`](repo/analysis.md)（10415 bytes，blob 8fee722）
- [`analysis_test.py`](repo/analysis_test.py)（2475 bytes，blob bbaea82）
- [`array_list.py`](repo/array_list.py)（8304 bytes，blob 16b6f28）
- [`array_list_test.py`](repo/array_list_test.py)（7081 bytes，blob 47892ec）
- [`linked_list.py`](repo/linked_list.py)（7167 bytes，blob 5dc9217）
- [`linked_list_test.py`](repo/linked_list_test.py)（7389 bytes，blob 5910522）
- [`list_checks.py`](repo/list_checks.py)（4351 bytes，blob eea8c22）
- [`my_timing.py`](repo/my_timing.py)（2747 bytes，blob 8b4abcc）
- [`part_e_checks.py`](repo/part_e_checks.py)（2196 bytes，blob 7e843db）
- [`shared_list_tests.py`](repo/shared_list_tests.py)（7811 bytes，blob a867a8a）
- [`student_tests.py`](repo/student_tests.py)（2536 bytes，blob d0ba20e）
- [`timing.py`](repo/timing.py)（6716 bytes，blob 8f34477）
