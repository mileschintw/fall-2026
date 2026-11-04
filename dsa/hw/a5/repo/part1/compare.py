"""Compare your binary search tree with an AVL tree.  Run:  python3 compare.py

For each size n, the same values 1..n go into both trees, once in sorted order and once
shuffled. For each tree it reports the height and the average number of nodes a search
visits (using your search_steps), averaged over every value in the tree.
Copy the table it prints into ANALYSIS.md. You do not need to edit this file.
"""
import math
import random

from bst import bst_insert, search_steps
from avl import avl_insert
from tree_tools import tree_height

SIZES = [100, 500, 1000, 2000]
SEED = 590


def build(insert, values):
    root = None
    for v in values:
        root = insert(root, v)
    return root


def measure(insert, values):
    """Return (height, average steps) as strings, or the name of the error if one happened."""
    try:
        root = build(insert, values)
    except RecursionError:
        return 'RecursionError (insert)', '-'
    height = tree_height(root)
    try:
        average = sum(search_steps(root, v) for v in values) / len(values)
    except RecursionError:
        return str(height), 'RecursionError (search_steps)'
    return str(height), '%.2f' % average


def main():
    rows = []
    for n in SIZES:
        in_order = list(range(1, n + 1))
        shuffled = in_order[:]
        random.Random(SEED).shuffle(shuffled)
        for name, values in [('sorted', in_order), ('shuffled', shuffled)]:
            bst_h, bst_avg = measure(bst_insert, values)
            avl_h, avl_avg = measure(avl_insert, values)
            rows.append([str(n), name, bst_h, bst_avg, avl_h, avl_avg, '%.1f' % math.log2(n)])
    header = ['n', 'order', 'BST height', 'BST avg steps', 'AVL height', 'AVL avg steps', 'log2(n)']
    print('| ' + ' | '.join(header) + ' |')
    print('|' + '|'.join([' --- '] * len(header)) + '|')
    for row in rows:
        print('| ' + ' | '.join(row) + ' |')


if __name__ == '__main__':
    main()
