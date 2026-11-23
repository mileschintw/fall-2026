"""A priority queue kept as an UNSORTED Python list. (Provided, for compare.py. You do not edit it.)

Same functions as priority_queue.py, with a 'list_' prefix. Inserting just appends. Everything
else scans the whole list: to find the most urgent entry, or to find a given item.
An entry is [priority, order, item], as in priority_queue.py.
"""


def list_create():
    return {'entries': [], 'counter': 0}


def list_size(pq):
    return len(pq['entries'])


def list_insert(pq, item, priority):
    if _find(pq, item) is not None:
        raise ValueError('item is already in the priority queue: %r' % (item,))
    pq['entries'].append([priority, pq['counter'], item])
    pq['counter'] += 1


def _find(pq, item):
    for i, entry in enumerate(pq['entries']):
        if entry[2] == item:
            return i
    return None


def _most_urgent(pq):
    entries = pq['entries']
    best = 0
    for i in range(1, len(entries)):
        if (entries[i][0], entries[i][1]) < (entries[best][0], entries[best][1]):
            best = i
    return best


def list_remove_min(pq):
    if not pq['entries']:
        raise IndexError('remove from an empty priority queue')
    i = _most_urgent(pq)
    entries = pq['entries']
    entries[i], entries[-1] = entries[-1], entries[i]
    entry = entries.pop()
    return entry[2], entry[0]


def list_change_priority(pq, item, new_priority):
    i = _find(pq, item)
    if i is None:
        raise KeyError(item)
    pq['entries'][i][0] = new_priority
