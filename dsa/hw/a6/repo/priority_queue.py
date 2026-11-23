"""Part 1: a priority queue you can update.

A priority queue built on a min-heap, plus a dict that remembers where each item is
in the heap, so an item's priority can be changed (or the item removed) without
searching the whole heap. See the README for the details and the hints.

A PRIORITY QUEUE is a dict with three keys:
    'heap'      a Python list used as a min-heap of ENTRIES (see below)
    'position'  a dict: item -> the index of that item's entry in 'heap'
    'counter'   how many items have ever been inserted (it only goes up)

An ENTRY is a list [priority, order, item]:
    priority  a number; SMALLER means MORE urgent
    order     the value of 'counter' when the item was inserted. Ties in priority
              are broken by order, so equal priorities come out first come, first served.
    item      the item itself. Items must be hashable (they are dict keys) and unique.

After every function returns, these must all be true (pq_checks.assert_pq_valid checks them):
    * every entry comes after its parent: entry_less(heap[i], heap[(i - 1) // 2]) is False
    * pq['position'][item] == i exactly when heap[i] holds item, and position has nothing else
"""

PQ_HEAP_KEY = 'heap'
PQ_POSITION_KEY = 'position'
PQ_COUNTER_KEY = 'counter'

PRIORITY, ORDER, ITEM = 0, 1, 2


def create_pq():
    """Return a new, empty priority queue. (Provided.)"""
    return {PQ_HEAP_KEY: [], PQ_POSITION_KEY: {}, PQ_COUNTER_KEY: 0}


def entry_less(a, b):
    """True if entry a should come out before entry b. (Provided.)
    Compares priority first, then order. Never compares the items themselves."""
    return (a[PRIORITY], a[ORDER]) < (b[PRIORITY], b[ORDER])


def pq_size(pq):
    """Return how many items are in the queue."""
    raise NotImplementedError('TODO: pq_size')


def pq_is_empty(pq):
    """Return True if the queue has no items."""
    raise NotImplementedError('TODO: pq_is_empty')


def pq_contains(pq, item):
    """Return True if item is in the queue. This should take O(1) time."""
    raise NotImplementedError('TODO: pq_contains')


def pq_priority(pq, item):
    """Return item's current priority. Raise KeyError if item is not in the queue."""
    raise NotImplementedError('TODO: pq_priority')


def pq_insert(pq, item, priority):
    """Add item with the given priority. Raise ValueError if item is already in the queue.

    The new entry's order is the current counter, and the counter goes up by one.
    """
    raise NotImplementedError('TODO: pq_insert')


def pq_peek(pq):
    """Return (item, priority) for the most urgent item, without removing it.
    Raise IndexError if the queue is empty."""
    raise NotImplementedError('TODO: pq_peek')


def pq_remove_min(pq):
    """Remove the most urgent item and return (item, priority).
    Raise IndexError if the queue is empty."""
    raise NotImplementedError('TODO: pq_remove_min')


def pq_remove(pq, item):
    """Remove item from the queue, wherever it is, and return its priority.
    Raise KeyError if item is not in the queue. O(log n) time."""
    raise NotImplementedError('TODO: pq_remove')


def pq_change_priority(pq, item, new_priority):
    """Change item's priority to new_priority. Its order stays the same.
    Raise KeyError if item is not in the queue. O(log n) time."""
    raise NotImplementedError('TODO: pq_change_priority')
