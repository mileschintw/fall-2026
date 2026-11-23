# Analysis

Fill in each section below. Short answers are fine: a few sentences each. This part is graded by hand
(25 points), on your reasoning, not on polish. Write it yourself: an AI can help you understand something,
but these answers should be in your words.

## 1. Predict first, before you run compare.py (3 points)

`compare.py` times three priority queues on n inserts, then n priority changes, then n removes (see the
README). For each one, write the cost of a **single** operation in Big-O, then guess what happens to the
time of the **whole step** when n doubles: about the same, about 2 times, a bit more than 2 times, or
about 4 times. You are graded on the reasoning, not on whether the guess is right, so do not change these
after you run it.

| Priority queue | one insert | one change | one remove_min | whole step, when n doubles (insert / change / remove) |
| --- | --- | --- | --- | --- |
| list (`list_pq.py`) | | | | |
| scan heap (`scan_heap_pq.py`) | | | | |
| your heap | | | | |

Why:

## 2. Results (2 points)

Run `python3 compare.py` and paste the three tables it prints here.

## 3. Explain the times (5 points)

a. Which predictions were right, and which were wrong? For one that was wrong, say what you missed.

b. Appending to a Python list is O(1), yet the list's insert step grows like n squared. Look at
`list_insert` and explain why.

c. The scan heap is fast at two of the three steps and slow at one. Why that one? What, exactly, does your
position dict let you skip?

d. The position dict isn't free. What does it cost, in memory and in work on every swap?

## 4. The help desk (5 points)

Run `python3 scenarios.py` and paste the table here.

a. Compare 2 agents with 3 agents (no aging). Which priority pays for having only 2 agents, and by how much?

b. In the 2-agent, no-aging row, look at the longest priority-3 wait. Explain how a priority-3 ticket can
wait that long even though every ticket eventually gets served. This is called *starvation*.

## 5. Aging (5 points)

a. With 2 agents, what did aging every 30 minutes do to each priority's average and longest wait? Who
gained and who lost?

b. The longest priority-1 wait went up a lot with aging every 30 minutes. Explain why. (Hint: what happens
when an old priority-3 ticket reaches priority 1? Which one wins a tie?)

c. If you ran this help desk, would you add aging, add a third agent, or something else? One or two
sentences, using the numbers.

d. Each escalation is one `pq_change_priority`. With the list or the scan heap instead of yours, how much
would one escalation cost, in Big-O, with n tickets waiting? Why does that matter more on a busy day?

## 6. By hand (5 points)

Do this on paper first, without running anything. This is the kind of question the final asks.

Start with an empty priority queue and insert, in this order: `p` with priority 6, `q` 2, `r` 9, `s` 4,
`t` 7, `u` 1. Then:

1. Write the heap (each entry as `[priority, order, item]`) and the position dict after all six inserts.
2. Then `pq_change_priority(pq, 's', 8)`. Write the heap and the position dict.
3. Then `pq_remove_min(pq)`. What does it return? Write the heap and the position dict.

Now check your answers with your code (`show_pq` in `pq_checks.py` prints a queue). Did you match? If not,
which step went wrong, and why?
