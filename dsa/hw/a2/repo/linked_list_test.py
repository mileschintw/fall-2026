"""
Tests for Part C (linked_list.py).  Run with:  python3 linked_list_test.py

How to read the results:
    .   a test passed
    F   a test FAILED: your code ran but gave a wrong answer
    E   a test had an ERROR: your code crashed (or isn't written yet)
Scroll up to the first failure and read the message.

To run just one test:
    python3 -m unittest linked_list_test.LinkedListOnlyTests.test_reverse_reuses_the_same_nodes
"""
import ast
import inspect
import textwrap
import unittest

from linked_list import *
from list_checks import linked_contents, linked_nodes, assert_linked_list_valid
from shared_list_tests import ListContractTests


def linked_list_by_hand(values):
    """Builds a linked list directly (without using your functions), for set-up."""
    lst = create_linked_list()
    previous = None
    for value in values:
        node = create_node(value)
        if previous is None:
            lst[LIST_HEAD_KEY] = node
        else:
            previous[NODE_NEXT_KEY] = node
        previous = node
    lst[LIST_SIZE_KEY] = len(values)
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
            elif isinstance(node.func, ast.Name):
                name = node.func.id
                if (name in FORBIDDEN_FUNCTIONS or name.startswith('array_list_')
                        or name.endswith('to_python_list')):
                    found.add('%s(...)' % name)
        elif isinstance(node, (ast.List, ast.ListComp)):
            found.add('a Python list ([...])')
    return sorted(found)


def is_unwritten(function):
    """True if the function's body is nothing but `pass` (after the docstring)."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
    body = tree.body[0].body
    statements = [s for s in body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    return all(isinstance(s, ast.Pass) for s in statements)


class LinkedListContractTests(ListContractTests, unittest.TestCase):
    """The behavior every list must have. (See shared_list_tests.py.)"""

    def new_list(self):
        return create_linked_list()

    length = staticmethod(linked_list_length)
    get = staticmethod(linked_list_get)
    insert_at = staticmethod(linked_list_insert_at)
    remove_at = staticmethod(linked_list_remove_at)
    to_python_list = staticmethod(linked_list_to_python_list)
    contents = staticmethod(linked_contents)
    assert_valid = staticmethod(assert_linked_list_valid)


class LinkedListOnlyTests(unittest.TestCase):
    """Things that are specific to nodes and links."""

    def test_length_reads_the_size(self):
        self.assertEqual(3, linked_list_length(linked_list_by_hand(['a', 'b', 'c'])))
        self.assertEqual(0, linked_list_length(create_linked_list()))

    def test_get_follows_the_links(self):
        lst = linked_list_by_hand(['a', 'b', 'c', 'd'])
        self.assertEqual('a', linked_list_get(lst, 0))
        self.assertEqual('d', linked_list_get(lst, 3))

    def test_insert_at_the_front_changes_the_head(self):
        lst = linked_list_by_hand(['b', 'c'])
        old_head = lst[LIST_HEAD_KEY]

        linked_list_insert_at(lst, 0, 'a')

        self.assertEqual('a', lst[LIST_HEAD_KEY][NODE_PAYLOAD_KEY])
        self.assertIs(old_head, lst[LIST_HEAD_KEY][NODE_NEXT_KEY])
        assert_linked_list_valid(lst)

    def test_insert_in_the_middle_keeps_the_existing_nodes(self):
        lst = linked_list_by_hand(['a', 'c', 'd'])
        before = linked_nodes(lst)

        linked_list_insert_at(lst, 1, 'b')

        after = linked_nodes(lst)
        self.assertEqual(['a', 'b', 'c', 'd'], linked_contents(lst))
        self.assertEqual([id(before[0]), id(before[1]), id(before[2])],
                         [id(after[0]), id(after[2]), id(after[3])],
                         'the old nodes should still be in the list, in order')
        assert_linked_list_valid(lst)

    def test_remove_the_first_node_changes_the_head(self):
        lst = linked_list_by_hand(['a', 'b', 'c'])
        second = lst[LIST_HEAD_KEY][NODE_NEXT_KEY]

        self.assertEqual('a', linked_list_remove_at(lst, 0))

        self.assertIs(second, lst[LIST_HEAD_KEY])
        assert_linked_list_valid(lst)

    def test_remove_the_last_node_leaves_a_proper_end(self):
        lst = linked_list_by_hand(['a', 'b', 'c'])

        self.assertEqual('c', linked_list_remove_at(lst, 2))

        self.assertIsNone(linked_nodes(lst)[-1][NODE_NEXT_KEY])
        assert_linked_list_valid(lst)

    def test_remove_a_middle_node_cuts_it_out(self):
        lst = linked_list_by_hand(['a', 'b', 'c'])
        before = linked_nodes(lst)

        self.assertEqual('b', linked_list_remove_at(lst, 1))

        self.assertEqual([id(before[0]), id(before[2])], [id(n) for n in linked_nodes(lst)])
        assert_linked_list_valid(lst)

    def test_removing_the_only_node_leaves_an_empty_list(self):
        lst = linked_list_by_hand(['only'])
        self.assertEqual('only', linked_list_remove_at(lst, 0))
        self.assertIsNone(lst[LIST_HEAD_KEY])
        self.assertEqual(0, lst[LIST_SIZE_KEY])

    def test_reverse(self):
        for size in range(8):
            values = list(range(size))
            lst = linked_list_by_hand(values)

            linked_list_reverse(lst)

            self.assertEqual(list(reversed(values)), linked_contents(lst), 'size %d' % size)
            self.assertEqual(size, lst[LIST_SIZE_KEY], 'size %d' % size)
            assert_linked_list_valid(lst)

    def test_reverse_reuses_the_same_nodes(self):
        lst = linked_list_by_hand(['a', 'b', 'c', 'd'])
        before = [id(node) for node in linked_nodes(lst)]

        linked_list_reverse(lst)

        after = [id(node) for node in linked_nodes(lst)]
        self.assertEqual(list(reversed(before)), after,
                         'reverse should relink the existing nodes, not make new ones')

    def test_reversing_twice_restores_the_order(self):
        lst = linked_list_by_hand([1, 2, 3, 4, 5])
        linked_list_reverse(lst)
        self.assertEqual([5, 4, 3, 2, 1], linked_contents(lst))
        linked_list_reverse(lst)
        self.assertEqual([1, 2, 3, 4, 5], linked_contents(lst))
        assert_linked_list_valid(lst)

    def test_the_linked_list_functions_do_not_use_python_lists(self):
        for function in (linked_list_length, linked_list_get, linked_list_insert_at,
                         linked_list_remove_at, linked_list_reverse):
            self.assertFalse(is_unwritten(function), '%s is not written yet' % function.__name__)
            self.assertEqual([], shortcuts_used_by(function),
                             '%s may not use these (see the rules at the top of linked_list.py)'
                             % function.__name__)


if __name__ == '__main__':
    unittest.main()
