"""A priority queue on a heap WITHOUT a position dict. (Provided, for compare.py. You do not edit it.)

It uses Python's heapq module for the heap. Inserting and removing the most urgent entry are
fast, but heapq has no way to find an item, so changing an item's priority scans the list to
find it, changes it, and then rebuilds the heap (heapq.heapify), which also looks at every entry.
An entry is [priority, order, item], as in priority_queue.py. (Lists compare element by element,
so priority decides first, then order; order is unique, so the items are never compared.)
"""
import heapq


def scan_create():
    return {'heap': [], 'counter': 0}


def scan_size(pq):
    return len(pq['heap'])


def scan_insert(pq, item, priority):
    heapq.heappush(pq['heap'], [priority, pq['counter'], item])
    pq['counter'] += 1


def scan_remove_min(pq):
    if not pq['heap']:
        raise IndexError('remove from an empty priority queue')
    entry = heapq.heappop(pq['heap'])
    return entry[2], entry[0]


def scan_change_priority(pq, item, new_priority):
    heap = pq['heap']
    for entry in heap:
        if entry[2] == item:
            entry[0] = new_priority
            heapq.heapify(heap)
            return
    raise KeyError(item)
