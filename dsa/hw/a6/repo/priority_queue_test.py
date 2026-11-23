"""Tests for Part 1. These check that your priority queue is probably right, not every corner of it.
Run them with:  python3 -m unittest priority_queue_test -v
Run one group with, for example:  python3 -m unittest priority_queue_test.ChangePriorityTest
"""
import random
import time
import unittest

from priority_queue import (create_pq, pq_size, pq_is_empty, pq_contains, pq_priority, pq_insert,
                            pq_peek, pq_remove_min, pq_remove, pq_change_priority)
from pq_checks import assert_pq_valid


def filled(pairs):
    """A queue with the (item, priority) pairs inserted in order, checked after each insert."""
    pq = create_pq()
    for item, priority in pairs:
        pq_insert(pq, item, priority)
        assert_pq_valid(pq)
    return pq


def drain(pq):
    """Remove everything, checking the queue after each remove. Returns the (item, priority) pairs."""
    out = []
    while not pq_is_empty(pq):
        out.append(pq_remove_min(pq))
        assert_pq_valid(pq)
    return out


TICKETS = [('printer', 3), ('wifi', 2), ('server', 1), ('email', 2), ('chair', 5), ('vpn', 1), ('badge', 4)]
IN_ORDER = [('server', 1), ('vpn', 1), ('wifi', 2), ('email', 2), ('printer', 3), ('badge', 4), ('chair', 5)]


class BasicsTest(unittest.TestCase):
    def test_a_new_queue_is_empty(self):
        pq = create_pq()
        self.assertEqual(pq_size(pq), 0)
        self.assertTrue(pq_is_empty(pq))
        self.assertFalse(pq_contains(pq, 'printer'))

    def test_insert_one(self):
        pq = filled([('printer', 3)])
        self.assertEqual(pq_size(pq), 1)
        self.assertFalse(pq_is_empty(pq))
        self.assertTrue(pq_contains(pq, 'printer'))
        self.assertEqual(pq['heap'], [[3, 0, 'printer']])
        self.assertEqual(pq['position'], {'printer': 0})
        self.assertEqual(pq['counter'], 1)

    def test_peek_shows_the_most_urgent_and_leaves_it(self):
        pq = filled(TICKETS)
        self.assertEqual(pq_peek(pq), ('server', 1))
        self.assertEqual(pq_peek(pq), ('server', 1))
        self.assertEqual(pq_size(pq), len(TICKETS))

    def test_the_heap_after_four_inserts(self):
        pq = filled([('a', 5), ('b', 3), ('c', 8), ('d', 1)])
        self.assertEqual(pq['heap'], [[1, 3, 'd'], [3, 1, 'b'], [8, 2, 'c'], [5, 0, 'a']])
        self.assertEqual(pq['position'], {'d': 0, 'b': 1, 'c': 2, 'a': 3})


class RemoveMinTest(unittest.TestCase):
    def test_items_come_out_most_urgent_first(self):
        self.assertEqual(drain(filled(TICKETS)), IN_ORDER)

    def test_ties_come_out_first_come_first_served(self):
        pq = filled([('n%d' % i, 7) for i in range(12)])
        self.assertEqual([item for item, _ in drain(pq)], ['n%d' % i for i in range(12)])

    def test_ties_among_mixed_priorities(self):
        pairs = [('a', 2), ('b', 1), ('c', 2), ('d', 1), ('e', 2), ('f', 1), ('g', 3), ('h', 1)]
        self.assertEqual([item for item, _ in drain(filled(pairs))], ['b', 'd', 'f', 'h', 'a', 'c', 'e', 'g'])

    def test_inserts_and_removes_mixed(self):
        pq = filled([('a', 5), ('b', 3)])
        self.assertEqual(pq_remove_min(pq), ('b', 3))
        pq_insert(pq, 'c', 4)
        pq_insert(pq, 'd', 9)
        assert_pq_valid(pq)
        self.assertEqual(pq_remove_min(pq), ('c', 4))
        assert_pq_valid(pq)
        self.assertEqual(drain(pq), [('a', 5), ('d', 9)])
        self.assertFalse(pq_contains(pq, 'a'))

    def test_a_removed_item_can_come_back(self):
        pq = filled([('a', 1), ('b', 1)])
        pq_remove_min(pq)
        pq_insert(pq, 'a', 1)
        assert_pq_valid(pq)
        self.assertEqual(drain(pq), [('b', 1), ('a', 1)])

    def test_two_hundred_items(self):
        rng = random.Random(1)
        pairs = [(i, rng.randint(1, 20)) for i in range(200)]
        out = drain(filled(pairs))
        self.assertEqual(out, sorted(pairs, key=lambda p: (p[1], p[0])))


class LookupTest(unittest.TestCase):
    def test_priority_of_each_item(self):
        pq = filled(TICKETS)
        for item, priority in TICKETS:
            self.assertEqual(pq_priority(pq, item), priority)

    def test_contains_after_removes(self):
        pq = filled(TICKETS)
        pq_remove_min(pq)
        pq_remove_min(pq)
        self.assertFalse(pq_contains(pq, 'server'))
        self.assertFalse(pq_contains(pq, 'vpn'))
        for item in ['wifi', 'email', 'printer', 'badge', 'chair']:
            self.assertTrue(pq_contains(pq, item))
        self.assertEqual(pq_size(pq), 5)


class ChangePriorityTest(unittest.TestCase):
    def test_more_urgent_moves_to_the_front(self):
        pq = filled(TICKETS)
        pq_change_priority(pq, 'chair', 0)
        assert_pq_valid(pq)
        self.assertEqual(pq_peek(pq), ('chair', 0))
        self.assertEqual(pq_priority(pq, 'chair'), 0)

    def test_less_urgent_moves_back(self):
        pq = filled(TICKETS)
        pq_change_priority(pq, 'server', 9)
        assert_pq_valid(pq)
        self.assertEqual(pq_peek(pq), ('vpn', 1))
        self.assertEqual(drain(pq)[-1], ('server', 9))

    def test_the_heap_after_a_change(self):
        pq = filled([('a', 5), ('b', 3), ('c', 8), ('d', 1), ('e', 4)])
        pq_change_priority(pq, 'c', 2)
        self.assertEqual(pq['heap'], [[1, 3, 'd'], [3, 1, 'b'], [2, 2, 'c'], [5, 0, 'a'], [4, 4, 'e']])
        pq_change_priority(pq, 'd', 6)
        self.assertEqual(pq['heap'], [[2, 2, 'c'], [3, 1, 'b'], [6, 3, 'd'], [5, 0, 'a'], [4, 4, 'e']])
        assert_pq_valid(pq)

    def test_a_change_keeps_the_original_order(self):
        pq = filled([('a', 5), ('b', 2), ('c', 2)])
        pq_change_priority(pq, 'a', 2)
        assert_pq_valid(pq)
        self.assertEqual([item for item, _ in drain(pq)], ['a', 'b', 'c'])

    def test_a_change_to_the_same_priority(self):
        pq = filled(TICKETS)
        pq_change_priority(pq, 'email', 2)
        assert_pq_valid(pq)
        self.assertEqual(drain(pq), IN_ORDER)

    def test_many_changes(self):
        rng = random.Random(2)
        pq = filled([(i, rng.randint(1, 50)) for i in range(100)])
        current = {}
        for _ in range(300):
            item, priority = rng.randrange(100), rng.randint(1, 50)
            pq_change_priority(pq, item, priority)
            current[item] = priority
            assert_pq_valid(pq)
        for item, priority in current.items():
            self.assertEqual(pq_priority(pq, item), priority)


class RemoveTest(unittest.TestCase):
    def test_remove_from_the_middle(self):
        pq = filled(TICKETS)
        self.assertEqual(pq_remove(pq, 'email'), 2)
        assert_pq_valid(pq)
        self.assertFalse(pq_contains(pq, 'email'))
        self.assertEqual(drain(pq), [p for p in IN_ORDER if p[0] != 'email'])

    def test_remove_the_most_urgent(self):
        pq = filled(TICKETS)
        self.assertEqual(pq_remove(pq, 'server'), 1)
        assert_pq_valid(pq)
        self.assertEqual(pq_peek(pq), ('vpn', 1))

    def test_remove_the_last_entry(self):
        pq = filled(TICKETS)
        last_item = pq['heap'][-1][2]
        pq_remove(pq, last_item)
        assert_pq_valid(pq)
        self.assertEqual(pq_size(pq), len(TICKETS) - 1)

    def test_remove_the_only_item(self):
        pq = filled([('a', 1)])
        self.assertEqual(pq_remove(pq, 'a'), 1)
        assert_pq_valid(pq)
        self.assertTrue(pq_is_empty(pq))

    def test_a_remove_that_must_move_an_entry_up(self):
        # Removing 'd' moves the last entry ('g', priority 4) into d's spot, under 'b' (priority 10),
        # so it has to move UP. A remove that only sifts down leaves the heap broken.
        pq = filled([('a', 1), ('b', 10), ('c', 2), ('d', 11), ('e', 12), ('f', 3), ('g', 4)])
        pq_remove(pq, 'd')
        assert_pq_valid(pq)
        pq_remove(pq, 'e')
        assert_pq_valid(pq)
        self.assertEqual([item for item, _ in drain(pq)], ['a', 'c', 'f', 'g', 'b'])

    def test_remove_everything_in_random_order(self):
        rng = random.Random(3)
        pairs = [(i, rng.randint(1, 30)) for i in range(120)]
        pq = filled(pairs)
        items = [i for i, _ in pairs]
        rng.shuffle(items)
        for item in items:
            self.assertEqual(pq_remove(pq, item), dict(pairs)[item])
            assert_pq_valid(pq)
        self.assertTrue(pq_is_empty(pq))


class ErrorsTest(unittest.TestCase):
    def test_empty_queue_errors(self):
        pq = create_pq()
        self.assertRaises(IndexError, pq_peek, pq)
        self.assertRaises(IndexError, pq_remove_min, pq)

    def test_missing_item_errors(self):
        pq = filled(TICKETS)
        self.assertRaises(KeyError, pq_priority, pq, 'toaster')
        self.assertRaises(KeyError, pq_change_priority, pq, 'toaster', 1)
        self.assertRaises(KeyError, pq_remove, pq, 'toaster')
        assert_pq_valid(pq)

    def test_inserting_an_item_twice_is_an_error(self):
        pq = filled(TICKETS)
        self.assertRaises(ValueError, pq_insert, pq, 'wifi', 1)
        assert_pq_valid(pq)
        self.assertEqual(pq_priority(pq, 'wifi'), 2)
        self.assertEqual(pq_size(pq), len(TICKETS))


class RandomTest(unittest.TestCase):
    """Thousands of random operations, each checked against a simple (slow) model."""

    def check(self, seed, steps):
        rng = random.Random(seed)
        pq = create_pq()
        model = {}          # item -> [priority, order]
        order = 0
        next_item = 0
        for _ in range(steps):
            choice = rng.random()
            if choice < 0.35 or not model:
                item, priority = next_item, rng.randint(1, 10)
                next_item += 1
                pq_insert(pq, item, priority)
                model[item] = [priority, order]
                order += 1
            elif choice < 0.55:
                best = min(model, key=lambda k: model[k])
                self.assertEqual(pq_remove_min(pq), (best, model.pop(best)[0]))
            elif choice < 0.8:
                item, priority = rng.choice(list(model)), rng.randint(1, 10)
                pq_change_priority(pq, item, priority)
                model[item][0] = priority
            else:
                item = rng.choice(list(model))
                self.assertEqual(pq_remove(pq, item), model.pop(item)[0])
            assert_pq_valid(pq)
            self.assertEqual(pq_size(pq), len(model))

    def test_random_operations(self):
        self.check(10, 3000)

    def test_more_random_operations(self):
        self.check(11, 3000)


class SpeedTest(unittest.TestCase):
    """Change and remove should take O(log n) time. Finding an item by searching the heap is O(n),
    and that makes this test far too slow."""

    def test_twenty_thousand_of_everything(self):
        n = 20000
        rng = random.Random(4)
        start = time.perf_counter()
        pq = create_pq()
        for i in range(n):
            pq_insert(pq, i, rng.randint(1, 10 ** 6))
        for _ in range(n):
            pq_change_priority(pq, rng.randrange(n), rng.randint(1, 10 ** 6))
        for i in range(0, n, 2):
            pq_remove(pq, i)
        while not pq_is_empty(pq):
            pq_remove_min(pq)
        seconds = time.perf_counter() - start
        self.assertLess(seconds, 5.0, 'took %.1f seconds; a heap with a position dict needs well under 1' % seconds)
