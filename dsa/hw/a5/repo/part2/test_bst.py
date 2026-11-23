"""YOUR TESTS GO HERE.

Write tests for the five functions in bst_reference.py. The docstrings there and the
README are the specification; a buggy version breaks some part of it.

Run them:            python3 -m unittest test_bst -v
Check your progress: python3 check_tests.py

You may import: unittest, random, time, copy, itertools, math, string, collections,
and the names below. See the README for what is not allowed (short version: test what
the functions DO, not how they are written).

Layout:
  TestFuzz     random operations checked step by step against a Python set (the model)
  TestEdges    inputs random sequences rarely produce: empty tree, == vs is, 0 and '', types
  TestDelete   one hand-made case per kind of delete, so a failure says what broke
  TestDeep     5,000-deep chains (the size rule)
  TestSpeed    time proportional to height, not to the number of values (the speed rule)
"""
import random
import time
import unittest

from bst_reference import bst_insert, bst_search, bst_min, bst_max, bst_delete
from tree_tools import create_tree_node, inorder_values, tree_size, tree_height


# ---------------------------------------------------------------- helpers

def build(values):
    """Insert the values one after another and return the root."""
    root = None
    for v in values:
        root = bst_insert(root, v)
    return root


def shape(root):
    """The exact structure of a tree, as {path: payload}; path is a string of 'L' and 'R'."""
    out = {}
    todo = [(root, '')] if root is not None else []
    while todo:
        node, path = todo.pop()
        out[path] = node['payload']
        if node['left'] is not None:
            todo.append((node['left'], path + 'L'))
        if node['right'] is not None:
            todo.append((node['right'], path + 'R'))
    return out


def insert_path(tree_shape, value):
    """Where plain BST insertion puts value in a tree given by shape(), or None if it is there."""
    path = ''
    while path in tree_shape:
        if value == tree_shape[path]:
            return None
        path += 'L' if value < tree_shape[path] else 'R'
    return path


def expected_shape(values):
    """The structure plain BST insertion must give, worked out independently."""
    tree = {}
    for v in values:
        path = insert_path(tree, v)
        if path is not None:
            tree[path] = v
    return tree


def node_ids(root):
    """id() of every node object in the tree."""
    out = set()
    todo = [root] if root is not None else []
    while todo:
        node = todo.pop()
        out.add(id(node))
        for side in ('left', 'right'):
            if node[side] is not None:
                todo.append(node[side])
    return out


def balanced_order(values):
    """An insertion order of the sorted values that gives a perfectly balanced tree."""
    values = sorted(values)
    out, todo = [], [(0, len(values) - 1)]
    while todo:
        lo, hi = todo.pop(0)
        if lo > hi:
            continue
        mid = (lo + hi) // 2
        out.append(values[mid])
        todo.append((lo, mid - 1))
        todo.append((mid + 1, hi))
    return out


def right_chain(n):
    """0 -> 1 -> ... -> n-1, every node a right child: height n-1. Built without bst_insert."""
    node = None
    for v in reversed(range(n)):
        node = create_tree_node(v, None, node)
    return node


def left_chain(n):
    """n-1 -> n-2 -> ... -> 0, every node a left child: height n-1."""
    node = None
    for v in range(n):
        node = create_tree_node(v, node, None)
    return node


class BSTCase(unittest.TestCase):
    def assertValidBST(self, root, expected_values):
        """In-order is strictly increasing, holds exactly expected_values, and is a real tree."""
        values = inorder_values(root)
        self.assertEqual(values, sorted(set(expected_values)))
        self.assertEqual(tree_size(root), len(values))


# ---------------------------------------------------------------- fuzzing

class TestFuzz(BSTCase):
    """Random sequences of all five operations. After every step the tree is compared with a
    Python set holding what the tree should hold, and each operation's own rule is checked."""

    def fuzz(self, seed, gen, runs=40, steps=200):
        rng = random.Random(seed)
        for run in range(runs):
            root, model = None, set()
            for step in range(steps):
                where = 'seed %d run %d step %d' % (seed, run, step)
                op = rng.random()
                v = gen(rng)
                before = shape(root)
                if op < 0.45:
                    root = self.check_insert(root, model, v, before, where)
                elif op < 0.75:
                    root = self.check_delete(root, model, v, before, where)
                else:
                    self.check_lookups(root, model, v, before, where)
                self.assertValidBST(root, model)

    def check_insert(self, root, model, v, before, where):
        new = bst_insert(root, v)
        if root is None:
            # An empty tree gets a new node, which is returned.
            self.assertEqual(new, {'payload': v, 'left': None, 'right': None}, where)
        else:
            # Changed in place, and its root is returned.
            self.assertIs(new, root, where)
        expected = dict(before)
        path = insert_path(before, v)
        if path is not None:
            # A new value becomes one new leaf, exactly where plain BST insertion puts it;
            # nothing else moves. A value already there (by ==) is ignored: no change at all.
            expected[path] = v
        self.assertEqual(shape(new), expected, where)
        model.add(v)
        return new

    def check_delete(self, root, model, v, before, where):
        height = tree_height(root)
        new = bst_delete(root, v)
        if v not in model:
            # Not in the tree: nothing changes.
            self.assertIs(new, root, where)
            self.assertEqual(shape(new), before, where)
            return new
        model.discard(v)
        if not model:
            self.assertIsNone(new, where)
        if root['payload'] != v:
            # Changed in place: the root stays the root.
            self.assertIs(new, root, where)
        # Never taller than before.
        self.assertLessEqual(tree_height(new), height, where)
        return new

    def check_lookups(self, root, model, v, before, where):
        ids = node_ids(root)
        found = bst_search(root, v)
        if v in model:
            # The node itself, from this tree - not the payload, not a copy.
            self.assertIn(id(found), ids, where)
            self.assertEqual(found['payload'], v, where)
        else:
            self.assertIsNone(found, where)
        lo, hi = bst_min(root), bst_max(root)
        if model:
            self.assertIn(id(lo), ids, where)
            self.assertIn(id(hi), ids, where)
            self.assertEqual(lo['payload'], min(model), where)
            self.assertEqual(hi['payload'], max(model), where)
        else:
            self.assertIsNone(lo, where)
            self.assertIsNone(hi, where)
        # Looking does not change anything.
        self.assertEqual(shape(root), before, where)

    def test_fuzz_ints(self):
        self.fuzz(1, lambda rng: rng.randint(-30, 30))

    def test_fuzz_mixed_numbers(self):
        # ints, floats between them, and floats equal to ints (3.0 == 3), negatives and zero.
        def gen(rng):
            n = rng.randint(-15, 15)
            return rng.choice([n, n + 0.5, float(n), n / 4])
        self.fuzz(2, gen)

    def test_fuzz_strings(self):
        # Short strings, including '' and upper/lower case ('B' < 'a').
        letters = 'aAbB'
        def gen(rng):
            return ''.join(rng.choice(letters) for _ in range(rng.randint(0, 3)))
        self.fuzz(3, gen)


# ---------------------------------------------------------------- edge cases

class TestEdges(BSTCase):
    def test_empty_tree(self):
        self.assertEqual(bst_insert(None, 7), {'payload': 7, 'left': None, 'right': None})
        self.assertIsNone(bst_search(None, 7))
        self.assertIsNone(bst_min(None))
        self.assertIsNone(bst_max(None))
        self.assertIsNone(bst_delete(None, 7))
        self.assertIsNone(bst_delete(build([7]), 7))

    def test_equality_not_identity(self):
        # Values are compared with ==. 1 == 1.0, and two equal big numbers made separately are
        # different objects; a version that uses `is` treats them as different values.
        a = 10 ** 12
        b = int(str(a))  # equal to a, but a different object
        root = build([5, 1, a, 3])
        bst_insert(root, 1.0)
        bst_insert(root, b)
        self.assertEqual(tree_size(root), 4)
        self.assertEqual(bst_search(root, 3.0)['payload'], 3)
        self.assertEqual(bst_search(root, b)['payload'], a)
        root = bst_delete(root, b)
        root = bst_delete(root, 1.0)
        self.assertValidBST(root, [5, 3])

    def test_falsy_values(self):
        # 0 and '' are values like any other; catches `if value:` / `if node['payload']:` slips.
        root = bst_insert(None, 0)
        self.assertEqual(root['payload'], 0)
        root = build([0, -1, 1])
        self.assertEqual(bst_search(root, 0)['payload'], 0)
        self.assertEqual(bst_max(build([-1, 0]))['payload'], 0)
        root = bst_delete(root, 0)
        self.assertValidBST(root, [-1, 1])
        root = build(['', 'a', 'b'])
        self.assertEqual(bst_search(root, '')['payload'], '')
        self.assertEqual(bst_min(root)['payload'], '')
        root = bst_delete(root, '')
        self.assertValidBST(root, ['a', 'b'])

    def test_value_types_keep_their_own_order(self):
        # Numbers as numbers (9 < 10), strings as strings ('10' < '9', 'B' < 'a'),
        # floats exactly (no rounding: 1.2, 1.25 and 1.7 are three values).
        for values in ([9, 10, -1, 0, 100, -100, 2],
                       ['m', 'apple', 'Banana', 'z', '10', '9', '', 'ma'],
                       [1.5, 1.2, 1.7, 1.25, -0.5, 0.0, 1.0]):
            root = build(values)
            self.assertValidBST(root, values)
            self.assertEqual(shape(root), expected_shape(values))

    def test_insert_hand_checked_shape(self):
        root = build([5, 3, 8, 1, 4, 7, 9])
        self.assertEqual(shape(root), {'': 5, 'L': 3, 'R': 8, 'LL': 1, 'LR': 4, 'RL': 7, 'RR': 9})

    def test_min_max_go_all_the_way_or_stop_at_root(self):
        # The minimum is deep down the left spine (not one step short); when the root has no left
        # child the root itself is the minimum, however big its right subtree. Same for max.
        root = build([50, 40, 30, 20, 10, 60, 70, 80, 45, 55])
        self.assertIs(bst_min(root), root['left']['left']['left']['left'])
        self.assertIs(bst_max(root), root['right']['right']['right'])
        root = build([10, 20, 15, 12, 30])
        self.assertIs(bst_min(root), root)
        root = build([10, 5, 7, 8, 1])
        self.assertIs(bst_max(root), root)
        root = build([4])
        self.assertIs(bst_min(root), root)
        self.assertIs(bst_max(root), root)

    def test_missing_values(self):
        # Below the minimum, above the maximum, in every gap, between integers.
        # search returns None (not the last node visited); delete changes nothing.
        values = [50, 30, 70, 20, 40, 60, 80, 35, 65]
        for missing in [-1, 0, 25, 33, 36, 45, 55, 62, 67, 75, 100, 35.5, 64.9]:
            root = build(values)
            before = shape(root)
            self.assertIsNone(bst_search(root, missing), missing)
            self.assertIs(bst_delete(root, missing), root)
            self.assertEqual(shape(root), before)


# ---------------------------------------------------------------- delete, by hand

class TestDelete(BSTCase):
    def test_delete_leaf(self):
        root = build([50, 30, 70, 20, 40])
        self.assertIs(bst_delete(root, 20), root)
        self.assertEqual(shape(root), {'': 50, 'L': 30, 'R': 70, 'LR': 40})
        self.assertIs(bst_delete(root, 70), root)
        self.assertEqual(shape(root), {'': 50, 'L': 30, 'LR': 40})

    def test_delete_node_with_one_child(self):
        # Only a left child, only a right child; the node is a left child or a right child.
        root = build([50, 30, 20, 70, 60])
        self.assertIs(bst_delete(root, 30), root)
        self.assertIs(bst_delete(root, 70), root)
        self.assertEqual(shape(root), {'': 50, 'L': 20, 'R': 60})
        root = build([50, 30, 40, 70, 80])
        self.assertIs(bst_delete(root, 30), root)
        self.assertIs(bst_delete(root, 70), root)
        self.assertEqual(shape(root), {'': 50, 'L': 40, 'R': 80})

    def test_delete_root_with_one_child(self):
        # The child becomes the new root, and is returned.
        new = bst_delete(build([50, 30, 20, 40]), 50)
        self.assertEqual(shape(new), {'': 30, 'L': 20, 'R': 40})
        new = bst_delete(build([50, 70, 60, 80]), 50)
        self.assertEqual(shape(new), {'': 70, 'L': 60, 'R': 80})

    def test_delete_two_children_successor_is_right_child(self):
        # The right child has no left child, so it is itself the next value up.
        # A classic slip: unlinking it from the wrong side of the wrong parent.
        values = [50, 30, 70, 20, 40, 80, 90]
        root = build(values)
        self.assertIs(bst_delete(root, 70), root)
        self.assertValidBST(root, [v for v in values if v != 70])
        root = bst_delete(build(values), 50)
        self.assertValidBST(root, [v for v in values if v != 50])
        # Never taller: hanging 30's subtree below 70 would make it taller.
        root = bst_delete(build([50, 30, 70, 20, 40, 60, 80]), 50)
        self.assertLessEqual(tree_height(root), 2)

    def test_delete_two_children_successor_deep(self):
        # The next value up is deep down the left side of the right subtree and has a right child
        # of its own, which must be kept.
        values = [50, 30, 80, 20, 40, 70, 90, 60, 75, 55, 65, 57]
        for gone in (50, 30, 80):
            root = build(values)
            self.assertIs(bst_delete(root, gone), root)
            self.assertValidBST(root, [v for v in values if v != gone])
            self.assertLessEqual(tree_height(root), tree_height(build(values)))


# ---------------------------------------------------------------- 5,000 values

class TestDeep(BSTCase):
    """Rule: every function works on any tree of up to 5,000 values, in any order. Sorted input
    gives a chain 5,000 deep; a recursive version runs out of stack on it."""

    def test_insert_into_5000_chain(self):
        root = right_chain(5000)
        self.assertIs(bst_insert(root, 5000), root)
        self.assertIs(bst_insert(root, 4999), root)    # duplicate at the very bottom
        self.assertEqual(tree_height(root), 5000)
        root = left_chain(5000)
        self.assertIs(bst_insert(root, -1), root)
        self.assertEqual(tree_height(root), 5000)

    def test_search_min_max_on_5000_chain(self):
        root = right_chain(5000)
        self.assertEqual(bst_search(root, 4999)['payload'], 4999)
        self.assertIsNone(bst_search(root, 5000))
        self.assertIsNone(bst_search(root, 4998.5))
        self.assertEqual(bst_max(root)['payload'], 4999)
        self.assertEqual(bst_min(root)['payload'], 0)
        root = left_chain(5000)
        self.assertEqual(bst_search(root, 0)['payload'], 0)
        self.assertIsNone(bst_search(root, -1))
        self.assertEqual(bst_min(root)['payload'], 0)
        self.assertEqual(bst_max(root)['payload'], 4999)

    def test_delete_on_5000_chain(self):
        root = right_chain(5000)
        self.assertIs(bst_delete(root, 4999), root)        # the deepest leaf
        self.assertIs(bst_delete(root, 2500), root)        # middle, one child
        self.assertIs(bst_delete(root, 7777), root)        # missing, off the bottom
        self.assertIsNone(bst_search(root, 2500))
        self.assertEqual(bst_max(root)['payload'], 4998)
        new = bst_delete(root, 0)                          # the root, one child
        self.assertEqual(new['payload'], 1)
        self.assertEqual(tree_size(new), 4997)
        root = left_chain(5000)
        self.assertIs(bst_delete(root, 0), root)
        self.assertEqual(bst_min(root)['payload'], 1)


# ---------------------------------------------------------------- speed

class TestSpeed(unittest.TestCase):
    """Rule: each function takes time proportional to the HEIGHT of the tree, not to the number
    of values. A balanced tree of 4,095 values has height 11; one of 15 values has height 3.
    The same number of calls runs on both. A correct version is about 3 times slower on the big
    tree (11 levels against 3); one that walks the whole tree is hundreds of times slower.

    Comparing two runs on the same machine cancels out how fast the machine is. Each run is
    repeated and the fastest kept, which filters out pauses from the rest of the computer.
    A run on the big tree stops as soon as it is clearly too slow, so a slow version FAILS within
    a fraction of a second instead of making the whole suite run out of time."""

    LIMIT = 25          # big/small time ratio allowed; correct is about 3, whole-tree is 250+
    CALLS = 2000
    REPEATS = 5

    def run_ops(self, op, root, queries, deadline=None):
        """Seconds for op(state, q) over all queries; None if it passed the deadline."""
        state = {'root': root}
        start = time.perf_counter()
        for i, q in enumerate(queries):
            op(state, q)
            if deadline is not None and i % 50 == 0 and time.perf_counter() > deadline:
                return None
        return time.perf_counter() - start

    def check_speed(self, op, make_queries):
        """op(state, q) does one operation on state['root'] (and may replace it).
        make_queries(values) gives the CALLS queries for a tree holding those values."""
        trees = {}
        for n in (4095, 15):
            values = list(range(n))
            trees[n] = (build(balanced_order(values)), make_queries(values))
        small = min(self.run_ops(op, *trees[15]) for _ in range(self.REPEATS))
        allowed = max(small, 1e-6) * self.LIMIT
        big = None
        for _ in range(self.REPEATS):
            t = self.run_ops(op, *trees[4095], deadline=time.perf_counter() + 2 * allowed)
            if t is not None and (big is None or t < big):
                big = t
        if big is None:
            self.fail('every run on the 4,095-value tree took over %d times as long as on the '
                      '15-value tree: the time grows with the number of values' % (2 * self.LIMIT))
        self.assertLess(big, allowed, 'big/small = %.1f' % (big / max(small, 1e-6)))

    def queries(self, seed, offsets=(0, 0, 0.5, -0.5)):
        def make(values):
            rng = random.Random(seed)
            return [rng.choice(values) + rng.choice(offsets) for _ in range(self.CALLS)]
        return make

    def test_search_speed(self):
        # Values that are there and values that are not.
        self.check_speed(lambda s, q: bst_search(s['root'], q), self.queries(10))

    def test_min_max_speed(self):
        def op(s, q):
            bst_min(s['root'])
            bst_max(s['root'])
        self.check_speed(op, self.queries(11))

    def test_insert_existing_speed(self):
        # Values already present are ignored, so the tree stays the same.
        self.check_speed(lambda s, q: bst_insert(s['root'], q), self.queries(12, (0,)))

    def test_insert_new_and_delete_leaf_speed(self):
        # Insert a new leaf, then delete it again, so the tree stays the same.
        def op(s, q):
            bst_insert(s['root'], q)
            bst_delete(s['root'], q)
        self.check_speed(op, self.queries(13, (0.25,)))

    def test_delete_speed(self):
        # Delete a value that is there (leaf, one child or two children) and put it back, then
        # delete a value that is missing. The height grows by at most a few levels.
        def op(s, q):
            s['root'] = bst_delete(s['root'], q)
            s['root'] = bst_insert(s['root'], q)
            s['root'] = bst_delete(s['root'], q + 0.5)
        self.check_speed(op, self.queries(14, (0,)))


if __name__ == '__main__':
    unittest.main()
