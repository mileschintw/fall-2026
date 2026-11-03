"""YOUR TESTS GO HERE.

For every bug you believe is real, write a test that FAILS on the original code (help_desk_original.py)
and PASSES once the bug is fixed (help_desk.py). Also write a test for any claim you decided was NOT a bug,
to prove the code was fine (it passes on both).

Run on your code:            python3 -m unittest test_regressions -v
Check everything at once:    python3 check_hunt.py

You may import: unittest, random, time, copy, itertools, math, string, collections, and anything from help_desk.
"""
import unittest

from help_desk import stack_create, stack_push, stack_pop


class TestHelpDesk(unittest.TestCase):
    def test_example_stack_is_last_in_first_out(self):
        # An example of the style. It passes on the original AND on the fixed code, so it proves nothing is
        # wrong with the stack's order. Delete it or keep it.
        s = stack_create()
        stack_push(s, 'a')
        stack_push(s, 'b')
        self.assertEqual(stack_pop(s), 'b')

    # Add your tests below.


if __name__ == '__main__':
    unittest.main()
