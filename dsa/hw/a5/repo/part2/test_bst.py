"""YOUR TESTS GO HERE.

Write tests for the five functions in bst_reference.py. The docstrings there and the
README are the specification; a buggy version breaks some part of it.

Run them:            python3 -m unittest test_bst -v
Check your progress: python3 check_tests.py

You may import: unittest, random, time, copy, itertools, math, string, collections,
and the names below. See the README for what is not allowed (short version: test what
the functions DO, not how they are written).
"""
import unittest

from bst_reference import bst_insert, bst_search, bst_min, bst_max, bst_delete
from tree_tools import create_tree_node, inorder_values, tree_size, tree_height


def build(values):
    """Insert the values one after another and return the root."""
    root = None
    for v in values:
        root = bst_insert(root, v)
    return root


class TestBST(unittest.TestCase):
    def test_example_of_a_test(self):
        # An example to copy the style from. It catches almost nothing.
        root = build([5])
        self.assertEqual(root['payload'], 5)

    # Add your own tests below.


if __name__ == '__main__':
    unittest.main()
