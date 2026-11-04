# Findings

One row for every suspected bug you looked into, whether the idea came from you, an AI assistant, or
somewhere else. Add rows as needed (at least 4).

**Status** is one of:

- `confirmed`: you wrote a test (named in the last column) that FAILS on `help_desk_original.py` and passes on your fixed `help_desk.py`.
- `refuted`: you wrote a test that PASSES on both, showing the code was fine. (Looking wrong is not the same as being wrong.)
- `unproven`: you could not tell. Leave the last column empty.

`python3 check_hunt.py findings` checks each row by actually running the test you named.

| # | Function | What I think is wrong | Idea came from (me / AI / other) | Status | Test name |
| --- | --- | --- | --- | --- | --- |
| 1 | `da_append` | When full, capacity grows by 1 instead of doubling, so every append copies the whole array and n appends take O(n^2) instead of O(n) | me + AI | confirmed | test_append_is_linear_time |
| 2 | `da_remove_last` | Reads slots[size] instead of slots[size - 1], so it returns the slot past the end (None) instead of the last element | me + AI | confirmed | test_pop_return_correct_value |
| 3 | `stack_pop` | Calls list.pop() directly, so popping an empty stack raises IndexError instead of returning None | me + AI | confirmed | test_stack_pop |
| 4 | `queue_push_front` | Appends the value at the back (same as enqueue) instead of putting it at the front, so it is not the next one dequeued | me + AI | confirmed | test_new_element_position_when_append_left |
| 5 | `undo_close` | Puts the ticket back at the front of the open queue but never removes it from the closed list, so closed_ids and closed_count still include it | AI | confirmed | test_undo_close_removes_ticket_from_closed |
| 6 | `brackets_balanced` | Returns True at the end without checking the stack is empty, so text with unclosed brackets like '((' counts as balanced | AI | confirmed | test_unclosed_brackets_are_unbalanced |

## Reflection

Write your answer on the line after "Answer:" (a few sentences is plenty) and delete "(write here)".
Using no AI is fine; the questions work either way.

## 1. Which suspected bug turned out not to be one, or to be different from what you first thought? How did you find out?

Answer: The da_append bug. At first I saw it as two problems: the capacity grows by 1 instead of doubling, and appending is slow (O(n^2) instead of O(n)). I wrote them as two rows, then saw that both come from the same one-line mistake (`+ 1` instead of `* 2`), so I merged them into one finding. Also, my first test for da_remove_last checked len(arr['slots']) and still failed after the fix. That showed me the capacity never shrinks, so I changed the test to check the size instead.

## 2. What convinced you that a bug was real before you changed any code?

Answer: Before changing help_desk.py, I ran each test on the original code and checked that it failed with a message that matched the docstring. For example, the capacity was 5 instead of 8, da_remove_last returned None instead of 1, stack_pop on an empty stack raised IndexError instead of returning None, and queue_push_front left the old item at the front. Only then did I fix the code and check that the same test passed.

## 3. Did you use an AI assistant? If yes: one thing it did well and one thing it got wrong or missed. If no: one thing you would have liked help with.

Answer: Yes. It did well at explaining code I did not understand, for example why the queue keeps a head index instead of removing items, and it showed that my queue_push_front test only covered the case with no dequeue, with a concrete wrong fix that would still pass. It got things wrong too: it split the da_append bug into two rows when it was one bug, and when I asked only for two empty rows in this table, it also wrote tests and fixes for two more bugs, which I had to ask it to undo.
