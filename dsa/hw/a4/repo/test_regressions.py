"""YOUR TESTS GO HERE.

For every bug you believe is real, write a test that FAILS on the original code (help_desk_original.py)
and PASSES once the bug is fixed (help_desk.py). Also write a test for any claim you decided was NOT a bug,
to prove the code was fine (it passes on both).

Run on your code:            python3 -m unittest test_regressions -v
Check everything at once:    python3 check_hunt.py

You may import: unittest, random, time, copy, itertools, math, string, collections, and anything from help_desk.
"""
import time
import unittest

from help_desk import stack_create, stack_push, stack_pop, da_create, da_append, da_to_list, da_remove_last, queue_create, queue_enqueue, queue_push_front, queue_peek, queue_dequeue, desk_create, submit, work_next, undo_close, closed_ids, closed_count, next_ticket, brackets_balanced


class TestHelpDesk(unittest.TestCase):
    def test_example_stack_is_last_in_first_out(self):
        # An example of the style. It passes on the original AND on the fixed code, so it proves nothing is
        # wrong with the stack's order. Delete it or keep it.
        s = stack_create()
        stack_push(s, 'a')
        stack_push(s, 'b')
        self.assertEqual(stack_pop(s), 'b')

    # Add your tests below.
    def test_append_size_per_expand(self):
        arr = da_create()
        self.assertEqual(len(arr['slots']), 4)
        for _ in range(5):
            da_append(arr, 0)
        self.assertEqual(len(arr['slots']), 8)
        for _ in range(4):
            da_append(arr, 0)
        self.assertEqual(len(arr['slots']), 16)

    def test_append_is_linear_time(self):
        arr = da_create()
        start = time.time()
        for i in range(20000):
            da_append(arr, i)
        self.assertLess(time.time() - start, 1.0)
        self.assertEqual(da_to_list(arr), list(range(20000)))

    def test_pop_return_correct_value(self):
        arr = da_create()
        for i in range(2):
            da_append(arr, i)
        last_element = da_remove_last(arr)
        self.assertEqual(last_element, 1)
        self.assertEqual(arr['size'], 1)
        last_element = da_remove_last(arr)
        self.assertEqual(last_element, 0)
        self.assertEqual(arr['size'], 0)

    def test_stack_pop(self):
        s = stack_create()
        stack_push(s, 0)
        self.assertEqual(len(s), 1)
        popped = stack_pop(s)
        self.assertEqual(popped, 0)
        self.assertEqual(len(s), 0)
        popped = stack_pop(s)
        self.assertEqual(popped, None)
        self.assertEqual(len(s), 0)

    def test_new_element_position_when_append_left(self):
        q = queue_create()
        queue_enqueue(q, 0)
        self.assertEqual(queue_peek(q), 0)
        queue_push_front(q, 1)
        self.assertEqual(queue_peek(q), 1)

    def test_push_front_after_dequeue(self):
        q = queue_create()
        for i in range(3):
            queue_enqueue(q, i)
        queue_dequeue(q)
        queue_push_front(q, 'x')
        self.assertEqual(queue_dequeue(q), 'x')
        self.assertEqual(queue_dequeue(q), 1)
        self.assertEqual(queue_dequeue(q), 2)
        self.assertEqual(queue_dequeue(q), None)

    def test_undo_close_removes_ticket_from_closed(self):
        desk = desk_create()
        submit(desk, 'a')
        submit(desk, 'b')
        work_next(desk)
        work_next(desk)
        self.assertEqual(undo_close(desk)['id'], 2)
        self.assertEqual(closed_ids(desk), [1])
        self.assertEqual(closed_count(desk), 1)
        self.assertEqual(next_ticket(desk)['id'], 2)

    def test_unclosed_brackets_are_unbalanced(self):
        for text in ['(', '((', '{[', 'a(b']:
            self.assertFalse(brackets_balanced(text), text)


if __name__ == '__main__':
    unittest.main()
