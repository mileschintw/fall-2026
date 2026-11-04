"""Tests for Part 1. These check that your tree is probably right, not every corner of it.
Run them with:  python3 -m unittest bst_test -v
"""
import unittest

from bst import bst_insert, bst_search, bst_min, bst_max, bst_delete, search_steps
from tree_tools import inorder_values, tree_size
from avl import avl_insert

EXAMPLE = [8, 3, 10, 1, 6, 14, 4, 7, 13]     # the tree from class


def build(values):
    root = None
    for v in values:
        root = bst_insert(root, v)
    return root


class InsertTest(unittest.TestCase):
    def test_insert_into_an_empty_tree_makes_a_node(self):
        root = bst_insert(None, 5)
        self.assertEqual(root['payload'], 5)
        self.assertIsNone(root['left'])
        self.assertIsNone(root['right'])

    def test_the_example_tree_has_the_right_shape(self):
        root = build(EXAMPLE)
        self.assertEqual(root['payload'], 8)
        self.assertEqual(root['left']['payload'], 3)
        self.assertEqual(root['right']['payload'], 10)
        self.assertEqual(root['left']['right']['left']['payload'], 4)
        self.assertEqual(inorder_values(root), sorted(EXAMPLE))

    def test_a_duplicate_is_ignored(self):
        root = build(EXAMPLE + [6, 8])
        self.assertEqual(tree_size(root), len(EXAMPLE))


class SearchTest(unittest.TestCase):
    def test_every_value_is_found(self):
        root = build(EXAMPLE)
        for v in EXAMPLE:
            node = bst_search(root, v)
            self.assertIsNotNone(node, v)
            self.assertEqual(node['payload'], v)

    def test_a_missing_value_gives_none(self):
        root = build(EXAMPLE)
        for v in [0, 5, 9, 15]:
            self.assertIsNone(bst_search(root, v), v)

    def test_search_in_an_empty_tree(self):
        self.assertIsNone(bst_search(None, 5))


class MinMaxTest(unittest.TestCase):
    def test_min_and_max_of_the_example(self):
        root = build(EXAMPLE)
        self.assertEqual(bst_min(root)['payload'], 1)
        self.assertEqual(bst_max(root)['payload'], 14)

    def test_min_and_max_of_an_empty_tree(self):
        self.assertIsNone(bst_min(None))
        self.assertIsNone(bst_max(None))


class DeleteTest(unittest.TestCase):
    def check_delete(self, values, value):
        root = bst_delete(build(values), value)
        self.assertEqual(inorder_values(root), sorted(set(values) - {value}))
        return root

    def test_delete_a_leaf(self):
        self.check_delete(EXAMPLE, 1)

    def test_delete_a_node_with_one_child(self):
        self.check_delete(EXAMPLE, 14)        # 14 has only the left child 13
        self.check_delete([5, 3, 8, 9], 8)    # 8 has only the right child 9

    def test_delete_a_node_with_two_children(self):
        self.check_delete(EXAMPLE, 3)
        self.check_delete(EXAMPLE, 6)

    def test_delete_the_root(self):
        self.check_delete(EXAMPLE, 8)
        self.assertIsNone(bst_delete(build([5]), 5))

    def test_delete_a_missing_value_changes_nothing(self):
        self.check_delete(EXAMPLE, 5)

    def test_delete_everything(self):
        root = build(EXAMPLE)
        for v in [6, 14, 8, 1, 10, 7, 3, 13, 4]:
            root = bst_delete(root, v)
        self.assertIsNone(root)


class SearchStepsTest(unittest.TestCase):
    def test_steps_in_the_example(self):
        root = build(EXAMPLE)
        self.assertEqual(search_steps(root, 8), 1)
        self.assertEqual(search_steps(root, 10), 2)
        self.assertEqual(search_steps(root, 13), 4)    # 8, 10, 14, 13

    def test_steps_for_a_missing_value(self):
        root = build(EXAMPLE)
        self.assertEqual(search_steps(root, 5), 4)     # 8, 3, 6, 4, then off the tree
        self.assertEqual(search_steps(None, 5), 0)

    def test_steps_in_an_avl_tree(self):
        root = None
        for v in range(1, 8):                          # sorted input, but the AVL tree balances it
            root = avl_insert(root, v)
        self.assertEqual(search_steps(root, 4), 1)
        self.assertEqual(search_steps(root, 7), 3)


if __name__ == '__main__':
    unittest.main()
