"""
Tests for behavior that BOTH kinds of list must have.

You do not run this file. array_list_test.py and linked_list_test.py each use
it, plugging in their own functions, so exactly the same tests run on your
array list and on your linked list. That is the point of this assignment:
two very different structures, one job.

Each test follows the same three steps:
    1. Set up      build a list
    2. Execute     do the thing being tested
    3. Check       compare what you got with what you expected
"""
import random


class ListContractTests:
    """
    A "mixin": a bundle of tests that is not runnable by itself. The test files
    add the pieces below, so that `self.insert_at(...)` means array_list_insert_at
    in one place and linked_list_insert_at in the other.

    Pieces supplied by the test file:  new_list, length, get, insert_at,
    remove_at, to_python_list, contents (reads the raw values), assert_valid.
    """

    def build(self, values):
        """Make a list holding `values` in order, using your insert_at."""
        lst = self.new_list()
        for position, value in enumerate(values):
            self.insert_at(lst, position, value)
        return lst

    def check(self, lst, expected, context=''):
        """The list must be valid inside AND hold exactly the expected values."""
        try:
            self.assert_valid(lst)
        except AssertionError as error:
            self.fail('%s\n%s' % (context, error))
        self.assertEqual(expected, self.contents(lst), context)
        self.assertEqual(len(expected), self.length(lst), context)

    def test_new_list_is_empty(self):
        self.check(self.new_list(), [])

    def test_insert_at_the_end_builds_the_list_in_order(self):
        lst = self.new_list()
        expected = []
        for i in range(10):
            self.insert_at(lst, i, i * 10)
            expected.append(i * 10)
            self.check(lst, expected, 'after inserting %d values' % (i + 1))

    def test_insert_at_the_front_puts_the_newest_value_first(self):
        lst = self.new_list()
        expected = []
        for i in range(8):
            self.insert_at(lst, 0, i)
            expected.insert(0, i)
            self.check(lst, expected, 'after inserting %d values' % (i + 1))

    def test_insert_at_every_position(self):
        for position in range(6):
            lst = self.build([10, 20, 30, 40, 50])
            expected = [10, 20, 30, 40, 50]
            expected.insert(position, 99)

            self.insert_at(lst, position, 99)

            self.check(lst, expected, 'inserted at index %d' % position)

    def test_get_returns_the_value_at_each_index(self):
        values = ['a', 'b', 'c', 'd', 'e']
        lst = self.build(values)
        for index, value in enumerate(values):
            self.assertEqual(value, self.get(lst, index))
        self.check(lst, values, 'get must not change the list')

    def test_get_with_a_bad_index_raises_IndexError(self):
        lst = self.build([1, 2, 3])
        for index in (-1, 3, 4, 100):
            with self.assertRaises(IndexError, msg='index %d' % index):
                self.get(lst, index)
        with self.assertRaises(IndexError):
            self.get(self.new_list(), 0)
        self.check(lst, [1, 2, 3])

    def test_insert_with_a_bad_index_raises_IndexError_and_changes_nothing(self):
        lst = self.build([1, 2, 3])
        for index in (-1, 4, 5, 100):
            with self.assertRaises(IndexError, msg='index %d' % index):
                self.insert_at(lst, index, 99)
            self.check(lst, [1, 2, 3], 'after a failed insert at index %d' % index)
        empty = self.new_list()
        with self.assertRaises(IndexError):
            self.insert_at(empty, 1, 99)
        self.check(empty, [])

    def test_remove_at_every_position(self):
        for position in range(5):
            values = [10, 20, 30, 40, 50]
            lst = self.build(values)

            removed = self.remove_at(lst, position)

            self.assertEqual(values[position], removed, 'removed index %d' % position)
            del values[position]
            self.check(lst, values, 'removed index %d' % position)

    def test_remove_everything_from_the_front(self):
        values = [1, 2, 3, 4, 5]
        lst = self.build(values)
        while values:
            self.assertEqual(values.pop(0), self.remove_at(lst, 0))
            self.check(lst, values)

    def test_remove_everything_from_the_back(self):
        values = [1, 2, 3, 4, 5]
        lst = self.build(values)
        while values:
            last_index = len(values) - 1
            self.assertEqual(values.pop(), self.remove_at(lst, last_index))
            self.check(lst, values)

    def test_remove_with_a_bad_index_raises_IndexError_and_changes_nothing(self):
        lst = self.build([1, 2, 3])
        for index in (-1, 3, 4, 100):
            with self.assertRaises(IndexError, msg='index %d' % index):
                self.remove_at(lst, index)
            self.check(lst, [1, 2, 3], 'after a failed remove at index %d' % index)
        with self.assertRaises(IndexError):
            self.remove_at(self.new_list(), 0)

    def test_any_kind_of_value_can_be_stored(self):
        values = [None, 0, '', False, (1, 2), [3], 'text']
        lst = self.build(values)
        self.check(lst, values)
        for index, value in enumerate(values):
            self.assertIs(value, self.get(lst, index))
        for value in values:
            self.assertIs(value, self.remove_at(lst, 0))

    def test_to_python_list_returns_a_new_python_list(self):
        lst = self.build([1, 2, 3])

        result = self.to_python_list(lst)

        self.assertIsInstance(result, list)
        self.assertEqual([1, 2, 3], result)
        result.append(99)
        self.check(lst, [1, 2, 3], 'changing the returned list must not change the structure')
        self.assertEqual([], self.to_python_list(self.new_list()))

    def test_random_operations_always_match_a_python_list(self):
        """
        Do many random inserts, removes and gets on your list and on a plain
        Python list at the same time. They must always agree, and your list must
        always be valid. (The indexes include bad ones, which must raise.)
        """
        for seed in range(30):
            rng = random.Random(seed)
            lst = self.new_list()
            model = []
            for step in range(60):
                operation = rng.choice(['insert', 'insert', 'remove', 'get'])
                index = rng.randint(-1, len(model) + 1)
                context = 'seed %d, step %d: %s at index %d (size was %d)' % (
                    seed, step, operation, index, len(model))
                if operation == 'insert':
                    value = rng.randint(0, 99)
                    if 0 <= index <= len(model):
                        self.insert_at(lst, index, value)
                        model.insert(index, value)
                    else:
                        with self.assertRaises(IndexError, msg=context):
                            self.insert_at(lst, index, value)
                elif operation == 'remove':
                    if 0 <= index < len(model):
                        self.assertEqual(model.pop(index), self.remove_at(lst, index), context)
                    else:
                        with self.assertRaises(IndexError, msg=context):
                            self.remove_at(lst, index)
                else:
                    if 0 <= index < len(model):
                        self.assertEqual(model[index], self.get(lst, index), context)
                    else:
                        with self.assertRaises(IndexError, msg=context):
                            self.get(lst, index)
                self.check(lst, model, context)
