"""Part 1: a binary search tree, written by hand.

Every function takes the root of a tree (a node dict, or None for an empty tree).
Nodes are made with create_tree_node. Loops or recursion: your choice.
"""
from tree_tools import create_tree_node


def bst_insert(root, value):
    """Insert value into the tree in place and return the root.

    An empty tree (None) gets a brand-new node, which is returned.
    A value already in the tree is ignored.
    """
    raise NotImplementedError('TODO: bst_insert')


def bst_search(root, value):
    """Return the node holding value, or None if it is not in the tree."""
    raise NotImplementedError('TODO: bst_search')


def bst_min(root):
    """Return the node with the smallest value, or None for an empty tree."""
    raise NotImplementedError('TODO: bst_min')


def bst_max(root):
    """Return the node with the largest value, or None for an empty tree."""
    raise NotImplementedError('TODO: bst_max')


def bst_delete(root, value):
    """Delete value from the tree in place and return the root of the result.

    If value is not in the tree, nothing changes. Otherwise the node holding value
    is removed (no children, one child, or two children; see the README).
    The result is still a binary search tree.
    """
    raise NotImplementedError('TODO: bst_delete')


def search_steps(root, value):
    """Return how many nodes a search for value visits.

    Search exactly the way bst_search does, and count every node you look at,
    including the one holding value if it is found. An empty tree takes 0 steps.
    This works on the AVL tree in avl.py too, because its nodes have the same
    'payload', 'left' and 'right' keys.
    """
    raise NotImplementedError('TODO: search_steps')
