# A6: Heaps

> 來源：Canvas assignment 11814820（https://canvas.uw.edu/courses/1917417/assignments/11814820），抓取 2026-11-23 07:44 PST。
> 這個檔案由 `scripts/assignment_specs.py` 產生，內容是原文，每次來源有變動就整份重寫，不要手改。整理過的版本在 README.md。

- 截止（Canvas `due_at`）：2026-12-06 (Sun) 11:59 PM PST

## Canvas 作業說明

（空白）

## Starter repo README（uw-python-fall2026/assignment-6-mileschintw，blob 81d1834）

# Assignment 6: A priority queue you can update, and a help desk that uses it (100 points)

**Due: Sunday, December 6, 11:59 pm.**

In class, our heap could do two things: insert, and remove the smallest. Real priority queues need one
more: **change the priority of something already waiting**. A help desk ticket gets escalated. A network
route gets cheaper (you'll see this in graphs, in Dijkstra's algorithm). A scheduler bumps up a job that
has waited too long.

To change an item's priority you first have to find it, and a heap has no fast way to do that: searching
the list is O(n). The fix is a dict that remembers where every item is in the heap. Keeping that dict
correct through every swap is what this assignment is about.

| Part | What | Files you change | Points |
| --- | --- | --- | --- |
| 1 | An updatable priority queue | `priority_queue.py` | 50 |
| 2 | A help desk simulation that uses it | `helpdesk_sim.py` | 15 |
| 3 | Timings, scenarios and a trace by hand | `ANALYSIS.md` | 25 |
| | The AI note | `AI_NOTE.md` | 10 |

## AI, and the final

**You may use an AI assistant for this assignment**, including for the code. Tell us how in `AI_NOTE.md`;
that's 10 points for filling it in honestly, and nothing in it lowers your grade.

The final is on paper, without AI. Expect to trace heap operations by hand, write short heap code, and
explain what operations cost. Section 6 of `ANALYSIS.md` is practice for exactly that, so do it on paper
before you check it. If an assistant writes your `_sift_down`, make sure you could write it yourself.

## Part 1: the priority queue (`priority_queue.py`)

A priority queue is a dict with three keys:

| Key | What it holds |
| --- | --- |
| `'heap'` | a list used as a min-heap of **entries**, each a list `[priority, order, item]` |
| `'position'` | a dict: `item -> index` of that item's entry in `'heap'` |
| `'counter'` | how many items have ever been inserted; each insert uses it as the new entry's `order`, then adds one |

**Smaller priority means more urgent.** Entries are compared by priority, then by order (`entry_less`, which
is provided, does this). So two tickets with the same priority come out first come, first served. Changing
an item's priority keeps its order.

After every function returns, two things must be true:

1. **Heap order.** No entry comes before its parent: `entry_less(heap[i], heap[(i - 1) // 2])` is False.
2. **Positions.** `position[item] == i` exactly when `heap[i]` holds `item`, and `position` holds nothing else.

`pq_checks.py` has `assert_pq_valid(pq)`, which checks both and says what is wrong, and `show_pq(pq)`, which
prints a queue. The tests call it after nearly every operation. Use it while you debug.

| Function | What it does |
| --- | --- |
| `pq_size(pq)`, `pq_is_empty(pq)` | how many items; whether there are none |
| `pq_contains(pq, item)` | True if `item` is waiting. O(1). |
| `pq_priority(pq, item)` | `item`'s current priority. `KeyError` if it isn't there. |
| `pq_insert(pq, item, priority)` | add it. `ValueError` if it is already there. |
| `pq_peek(pq)` | `(item, priority)` of the most urgent, without removing it. `IndexError` if empty. |
| `pq_remove_min(pq)` | remove the most urgent and return `(item, priority)`. `IndexError` if empty. |
| `pq_remove(pq, item)` | remove `item` from wherever it is and return its priority. `KeyError` if it isn't there. |
| `pq_change_priority(pq, item, new_priority)` | change it, and move the entry to where it belongs. `KeyError` if it isn't there. |

`create_pq` and `entry_less` are provided. Change, remove and remove_min must be O(log n); a `SpeedTest`
checks.

**Hints.**

* Start from the heap code we wrote in class (`sift_up`, `sift_down`, insert, remove_min). Compare entries
  with `entry_less`, not `<`.
* Write one helper, `_swap(pq, i, j)`, that swaps two entries **and** updates both of their positions. If
  every move in the heap goes through `_swap`, the position dict can't fall out of date.
* After a change, the entry might need to go up (more urgent) or down (less urgent). Calling sift up and
  then sift down from wherever it ends up is fine: at most one of them moves it.
* To remove the entry at index `i`: swap it with the last entry, pop it off the end, delete its position,
  and then fix the entry that moved into `i`. That entry may need to go **up**, not just down. (Remove_min
  is the case `i = 0`, where up is never needed.) There is a test for this.
* Don't forget the position dict when an entry is added or popped, not just when it is swapped.

## Part 2: the help desk (`helpdesk_sim.py`)

Tickets arrive at a help desk with a few agents. A ticket is a dict with an `'id'`, the minute it
`'arrive'`s, a `'priority'` (1 urgent, 2 normal, 3 whenever) and a `'duration'` in minutes.
`helpdesk_tools.py` (provided) makes them. Write `simulate(tickets, num_agents, escalations)`. Waiting
tickets go in **your** priority queue, keyed by ticket id.

**The rules.** Each minute, starting at minute 0, in this order:

1. Tickets that arrive this minute go into the queue, in order of id, with their priority.
2. The escalations for this minute are applied, in the order listed. An escalation is
   `(minute, ticket_id, new_priority)`; it changes the priority of a ticket that is **still waiting**. If
   the ticket has not arrived yet, or an agent already started on it, the escalation is ignored.
3. Agents, in number order (agent 0 first): an agent who is free takes the most urgent waiting ticket and
   starts on it this minute. An agent who starts a ticket of duration `d` at minute `m` is free again at
   minute `m + d`.

Stop when every ticket has started. Return one record per ticket, in the order they started:
`(ticket_id, start_minute, agent_number)`.

`helpdesk_tools.aging_escalations(tickets, every)` turns a policy into escalations: every `every` minutes a
ticket waits, it moves up one level. `scenarios.py` runs 20 simulated days with 2 and 3 agents, with and
without aging. Sections 4 and 5 of `ANALYSIS.md` ask about what it prints.

## Part 3: `ANALYSIS.md`

`compare.py` times three priority queues on the same work: an unsorted list (`list_pq.py`), a heap with
no position dict that finds items by scanning (`scan_heap_pq.py`), and yours. For each n it does n inserts,
n priority changes and n removes, and prints the time for each step. Fill in section 1 of `ANALYSIS.md`
**before** you run it. The whole run takes under a minute.

Then answer the rest, using `compare.py` and `scenarios.py`. Section 6 is a trace by hand.

## Run the tests

From this folder, in a terminal (or right-click a test file in PyCharm and choose Run):

```
python3 -m unittest priority_queue_test -v
python3 -m unittest helpdesk_sim_test -v
python3 check_note.py
python3 compare.py
python3 scenarios.py
```

Run one group while you work, for example `python3 -m unittest priority_queue_test.ChangePriorityTest`. At
the start every test fails with `NotImplementedError`; that is the starting line, not a broken repo. The
help desk tests use your priority queue, so get Part 1 passing first. The tests check that your code is
probably right; passing them is not proof that it is.

## Points

When you push, GitHub runs the tests and shows the 75 points it can check on the Actions tab.
`ANALYSIS.md` is graded by hand after the deadline.

| What | Points | Graded |
| --- | --- | --- |
| Basics | 6 | GitHub |
| Remove min (including ties) | 10 | GitHub |
| Lookups | 4 | GitHub |
| Change priority | 10 | GitHub |
| Remove | 8 | GitHub |
| Errors | 4 | GitHub |
| Random operations | 4 | GitHub |
| Speed | 4 | GitHub |
| Help desk: one agent | 5 | GitHub |
| Help desk: several agents | 4 | GitHub |
| Help desk: escalations | 3 | GitHub |
| Help desk: one full day | 3 | GitHub |
| `AI_NOTE.md` filled in | 10 | GitHub |
| `ANALYSIS.md` | 25 | by hand |
| **Total** | **100** | |

## Submit

Commit and push to `master` before the deadline. We grade the last push before the deadline. Check the
Actions tab after your last push.

Change only `priority_queue.py`, `helpdesk_sim.py`, `ANALYSIS.md` and `AI_NOTE.md`. Do not edit the tests,
the provided helpers, `compare.py`, `scenarios.py` or the workflow in `.github`: the instructor runs the
original files.

## Starter repo 其他檔案

原檔存在 `repo/` 底下（stub 的 docstring、測試、CI workflow 才是函式規格和配分的細節）。

- [`.github/workflows/classroom.yml`](repo/.github/workflows/classroom.yml)（5687 bytes，blob 6a1151e）
- [`.gitignore`](repo/.gitignore)（58 bytes，blob 538248f）
- [`AI_NOTE.md`](repo/AI_NOTE.md)（954 bytes，blob a7c0e28）
- [`ANALYSIS.md`](repo/ANALYSIS.md)（3324 bytes，blob 4a04981）
- [`check_note.py`](repo/check_note.py)（1360 bytes，blob d6f5810）
- [`compare.py`](repo/compare.py)（3215 bytes，blob 7af6b7d）
- [`helpdesk_sim.py`](repo/helpdesk_sim.py)（918 bytes，blob 21ce89b）
- [`helpdesk_sim_test.py`](repo/helpdesk_sim_test.py)（4041 bytes，blob c1adc77）
- [`helpdesk_tools.py`](repo/helpdesk_tools.py)（2858 bytes，blob 4ff9d3b）
- [`list_pq.py`](repo/list_pq.py)（1493 bytes，blob ce72c3d）
- [`pq_checks.py`](repo/pq_checks.py)（2798 bytes，blob 9f1a9d8）
- [`priority_queue.py`](repo/priority_queue.py)（3346 bytes，blob 988cae6）
- [`priority_queue_test.py`](repo/priority_queue_test.py)（11258 bytes，blob 3d83312）
- [`scan_heap_pq.py`](repo/scan_heap_pq.py)（1245 bytes，blob 004481f）
- [`scenarios.py`](repo/scenarios.py)（1862 bytes，blob 92cd71e）
