"""
Part E: Write two tests of your own.

The provided tests are good, but they can't think of everything. Add one test
for your array list and one for your linked list. Each should check something
the provided tests do not check directly. Ideas:
  * a case you were unsure about while writing your code
  * a longer or stranger sequence of operations
  * a check on 'moves' or 'size' that you worked out on paper in Part A
Give each test a name that says what it checks, replace the `self.fail(...)`
line, and make sure it PASSES with your code.

A test is a method whose name starts with `test_`, inside a class that extends
unittest.TestCase. A good one has three steps: set up, execute, check.

    def test_removing_the_only_value_leaves_the_list_empty(self):
        lst = create_array_list()                       # 1. set up
        array_list_insert_at(lst, 0, 'only')
        removed = array_list_remove_at(lst, 0)          # 2. execute
        self.assertEqual('only', removed)               # 3. check
        self.assertEqual(0, array_list_length(lst))
        assert_array_list_valid(lst)

(That one is an example -- write a different test.)

Useful checks:  self.assertEqual(expected, actual)    self.assertTrue(x)
                self.assertIsNone(x)    self.assertIs(a, b)
                with self.assertRaises(IndexError):  <code that should raise>

Run with:  python3 student_tests.py
"""
import unittest

from array_list import *
from linked_list import *
from list_checks import assert_array_list_valid, assert_linked_list_valid


class MyArrayListTests(unittest.TestCase):
    def test_nine_inserts_at_the_end_grow_twice_and_copy_twelve_values(self):
        lst = create_array_list()
        for i in range(9):
            array_list_insert_at(lst, i, i)
        self.assertEqual(16, len(lst['data']))
        self.assertEqual(4 + 8, lst['moves'])
        self.assertEqual(list(range(9)), array_list_to_python_list(lst))
        assert_array_list_valid(lst)


class MyLinkedListTests(unittest.TestCase):
    def test_list_still_works_after_reverse(self):
        lst = create_linked_list()
        for i in range(3):
            linked_list_insert_at(lst, i, i)
        linked_list_reverse(lst)
        linked_list_insert_at(lst, 3, 'end')
        self.assertEqual(2, linked_list_remove_at(lst, 0))
        self.assertEqual([1, 0, 'end'], linked_list_to_python_list(lst))
        self.assertEqual(3, linked_list_length(lst))
        assert_linked_list_valid(lst)


if __name__ == '__main__':
    unittest.main()
