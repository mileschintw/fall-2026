"""
Tests for Part B (array_list.py).  Run with:  python3 array_list_test.py

How to read the results:
    .   a test passed
    F   a test FAILED: your code ran but gave a wrong answer
    E   a test had an ERROR: your code crashed (or isn't written yet)
Scroll up to the first failure and read the message. It tells you which test,
which line of the test, and what was expected vs. what you got.

Tip: get the tests passing one at a time. To run just one:
    python3 -m unittest array_list_test.ArrayListOnlyTests.test_grow_doubles_the_capacity_and_keeps_the_values
"""
import ast
import inspect
import textwrap
import unittest

from array_list import *
from list_checks import array_contents, assert_array_list_valid
from shared_list_tests import ListContractTests


def array_list_by_hand(capacity, values):
    """Builds an array list directly (without using your functions), for set-up."""
    lst = create_array_list(capacity)
    for position, value in enumerate(values):
        lst[ARRAY_DATA_KEY][position] = value
    lst[ARRAY_SIZE_KEY] = len(values)
    return lst


FORBIDDEN_METHODS = {'append', 'insert', 'pop', 'remove', 'extend', 'clear',
                     'copy', 'sort', 'reverse', 'index'}
FORBIDDEN_FUNCTIONS = {'list', 'sorted', 'reversed', 'tuple', 'copy', 'deepcopy'}


def shortcuts_used_by(function):
    """Names the Python list tools a function uses that this part forbids."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in FORBIDDEN_METHODS:
                found.add('.%s(...)' % node.func.attr)
            elif isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_FUNCTIONS:
                found.add('%s(...)' % node.func.id)
        elif isinstance(node, ast.Slice):
            found.add('slicing like data[a:b]')
        elif isinstance(node, ast.Delete):
            found.add('del')
    return sorted(found)


def is_unwritten(function):
    """True if the function's body is nothing but `pass` (after the docstring)."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
    body = tree.body[0].body
    statements = [s for s in body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    return all(isinstance(s, ast.Pass) for s in statements)


class ArrayListContractTests(ListContractTests, unittest.TestCase):
    """The behavior every list must have. (See shared_list_tests.py.)"""

    def new_list(self):
        return create_array_list(2)     # a tiny array, so it has to grow often

    length = staticmethod(array_list_length)
    get = staticmethod(array_list_get)
    insert_at = staticmethod(array_list_insert_at)
    remove_at = staticmethod(array_list_remove_at)
    to_python_list = staticmethod(array_list_to_python_list)
    contents = staticmethod(array_contents)
    assert_valid = staticmethod(assert_array_list_valid)


class ArrayListOnlyTests(unittest.TestCase):
    """Things that are specific to an array: capacity, growing, and counting moves."""

    def test_length_is_the_number_of_values_not_the_capacity(self):
        self.assertEqual(3, array_list_length(array_list_by_hand(10, ['a', 'b', 'c'])))
        self.assertEqual(0, array_list_length(create_array_list(10)))

    def test_get_reads_the_right_slot(self):
        lst = array_list_by_hand(10, ['a', 'b', 'c'])
        self.assertEqual('a', array_list_get(lst, 0))
        self.assertEqual('c', array_list_get(lst, 2))

    def test_get_and_length_do_not_count_moves(self):
        lst = array_list_by_hand(10, ['a', 'b', 'c'])
        self.assertEqual('b', array_list_get(lst, 1))
        self.assertEqual(3, array_list_length(lst))
        self.assertEqual(0, lst[ARRAY_MOVES_KEY])

    def test_grow_doubles_the_capacity_and_keeps_the_values(self):
        lst = array_list_by_hand(4, [1, 2, 3, 4])

        array_list_grow(lst)

        self.assertEqual(4 * GROWTH_FACTOR, len(lst[ARRAY_DATA_KEY]))
        self.assertEqual([1, 2, 3, 4], array_contents(lst))
        self.assertEqual(4, lst[ARRAY_SIZE_KEY])
        assert_array_list_valid(lst)

    def test_grow_counts_one_move_per_value_copied(self):
        lst = array_list_by_hand(4, [1, 2, 3, 4])
        array_list_grow(lst)
        self.assertEqual(4, lst[ARRAY_MOVES_KEY])

        partly_full = array_list_by_hand(4, [1, 2])
        array_list_grow(partly_full)
        self.assertEqual(2, partly_full[ARRAY_MOVES_KEY])

    def test_grow_makes_a_new_data_list(self):
        lst = array_list_by_hand(4, [1, 2, 3, 4])
        old_data = lst[ARRAY_DATA_KEY]

        array_list_grow(lst)

        self.assertIsNot(old_data, lst[ARRAY_DATA_KEY])

    def test_insert_into_a_list_with_room_does_not_grow(self):
        lst = array_list_by_hand(10, [1, 2, 3])
        array_list_insert_at(lst, 1, 99)
        self.assertEqual(10, len(lst[ARRAY_DATA_KEY]))
        self.assertEqual([1, 99, 2, 3], array_contents(lst))

    def test_insert_into_a_full_list_grows_it_first(self):
        lst = array_list_by_hand(4, [1, 2, 3, 4])

        array_list_insert_at(lst, 0, 0)

        self.assertEqual(8, len(lst[ARRAY_DATA_KEY]))
        self.assertEqual([0, 1, 2, 3, 4], array_contents(lst))
        assert_array_list_valid(lst)

    def test_insert_counts_one_move_per_shifted_value(self):
        for index in range(6):
            lst = array_list_by_hand(10, [1, 2, 3, 4, 5])

            array_list_insert_at(lst, index, 99)

            self.assertEqual(5 - index, lst[ARRAY_MOVES_KEY],
                             'inserting at index %d shifts %d values' % (index, 5 - index))


    def test_remove_counts_one_move_per_shifted_value(self):
        for index in range(5):
            lst = array_list_by_hand(10, [1, 2, 3, 4, 5])

            array_list_remove_at(lst, index)

            self.assertEqual(4 - index, lst[ARRAY_MOVES_KEY],
                             'removing index %d shifts %d values' % (index, 4 - index))

    def test_remove_sets_the_vacated_slot_back_to_none(self):
        lst = array_list_by_hand(6, [1, 2, 3])

        array_list_remove_at(lst, 0)

        self.assertIsNone(lst[ARRAY_DATA_KEY][2])
        assert_array_list_valid(lst)

    def test_remove_does_not_shrink_the_array(self):
        lst = array_list_by_hand(8, [1, 2, 3])
        self.assertEqual(2, array_list_remove_at(lst, 1))
        self.assertEqual(8, len(lst[ARRAY_DATA_KEY]))


    def test_the_array_functions_do_not_use_python_list_shortcuts(self):
        for function in (array_list_length, array_list_get, array_list_grow,
                         array_list_insert_at, array_list_remove_at):
            self.assertFalse(is_unwritten(function), '%s is not written yet' % function.__name__)
            self.assertEqual([], shortcuts_used_by(function),
                             '%s may not use these (see the rules at the top of array_list.py)'
                             % function.__name__)


if __name__ == '__main__':
    unittest.main()
