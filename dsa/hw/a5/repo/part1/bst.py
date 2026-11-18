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
    if root is None:
        return create_tree_node(value)

    if value < root['payload']:
        root['left'] = bst_insert(root['left'], value)
    elif value > root['payload']:
        root['right'] = bst_insert(root['right'], value)

    return root



def bst_search(root, value):
    """Return the node holding value, or None if it is not in the tree."""
    if root is None:
        return None
    if value == root['payload']:
        return root
    if value < root['payload']:
        return bst_search(root['left'], value)
    if value > root['payload']:
        return bst_search(root['right'], value)


def bst_min(root):
    """Return the node with the smallest value, or None for an empty tree."""
    if root is None:
        return None

    left_min = bst_min(root['left'])
    return left_min if left_min is not None else root


def bst_max(root):
    """Return the node with the largest value, or None for an empty tree."""
    if root is None:
        return None

    right_max = bst_max(root['right'])
    return right_max if right_max is not None else root


def bst_delete(root, value):
    """Delete value from the tree in place and return the root of the result.

    If value is not in the tree, nothing changes. Otherwise the node holding value
    is removed (no children, one child, or two children; see the README).
    The result is still a binary search tree.
    """
    if root is None:
        return None

    if value < root['payload']:
        root['left'] = bst_delete(root['left'], value)
    elif value > root['payload']:
        root['right'] = bst_delete(root['right'], value)
    else:
        if not root['left'] and not root['right']:
            return None

        if not root['left']:
            return root['right']

        if not root['right']:
            return root['left']

        successor = bst_min(root['right'])
        root['payload'] = successor['payload']
        root['right'] = bst_delete(root['right'], successor['payload'])

    return root


def search_steps(root, value):
    """Return how many nodes a search for value visits.

    Search exactly the way bst_search does, and count every node you look at,
    including the one holding value if it is found. An empty tree takes 0 steps.
    This works on the AVL tree in avl.py too, because its nodes have the same
    'payload', 'left' and 'right' keys.
    """
    node = root
    cnt = 0
    while node is not None:
        if value == node['payload']:
            cnt += 1
            return cnt
        elif value < node['payload']:
            node = node['left']
            cnt += 1
        else:
            node = node['right']
            cnt += 1

    return cnt
