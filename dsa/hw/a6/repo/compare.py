"""Time three priority queues on the same work.  Run:  python3 compare.py

The three priority queues:
    list       an unsorted list (list_pq.py)
    scan heap  a heap with no position dict (scan_heap_pq.py)
    your heap  your priority_queue.py, a heap with a position dict

The work, for each size n:
    1. insert      n items, with random priorities from 1 to 1,000,000
    2. change      n changes of priority, each to a random item still in the queue
    3. remove      remove_min until the queue is empty

It prints one table per priority queue, with the seconds each step took. A cell says
"skipped" when that priority queue took too long at a smaller size. Copy the tables into
ANALYSIS.md. You do not need to edit this file. The whole run takes under a minute.
"""
import random
import time

import list_pq
import scan_heap_pq
import priority_queue as mine

SIZES = [1000, 2000, 4000, 8000]
SEED = 590
TOO_SLOW = 4.0          # seconds; after a size takes longer than this, bigger sizes are skipped

QUEUES = [
    ('list', list_pq.list_create, list_pq.list_insert, list_pq.list_change_priority, list_pq.list_remove_min),
    ('scan heap', scan_heap_pq.scan_create, scan_heap_pq.scan_insert, scan_heap_pq.scan_change_priority,
     scan_heap_pq.scan_remove_min),
    ('your heap', mine.create_pq, mine.pq_insert, mine.pq_change_priority, mine.pq_remove_min),
]


def workload(n):
    rng = random.Random(SEED + n)
    priorities = [rng.randint(1, 1000000) for _ in range(n)]
    changes = [(rng.randrange(n), rng.randint(1, 1000000)) for _ in range(n)]
    return priorities, changes


def run(create, insert, change, remove_min, n):
    priorities, changes = workload(n)
    pq = create()
    t0 = time.perf_counter()
    for item, p in enumerate(priorities):
        insert(pq, item, p)
    t1 = time.perf_counter()
    for item, p in changes:
        change(pq, item, p)
    t2 = time.perf_counter()
    out = []
    for _ in range(n):
        out.append(remove_min(pq))
    t3 = time.perf_counter()
    return t1 - t0, t2 - t1, t3 - t2, out


def main():
    answers = {}
    for name, create, insert, change, remove_min in QUEUES:
        print()
        print('**%s**' % name)
        print()
        print('| n | insert (s) | change (s) | remove (s) | total (s) |')
        print('| --- | --- | --- | --- | --- |')
        skip = False
        for n in SIZES:
            if skip:
                print('| %d | skipped | skipped | skipped | skipped |' % n)
                continue
            try:
                a, b, c, out = run(create, insert, change, remove_min, n)
            except NotImplementedError as e:
                print('| %d | %s | | | |' % (n, e))
                skip = True
                continue
            answers.setdefault(n, {})[name] = [p for _, p in out]
            print('| %d | %.4f | %.4f | %.4f | %.4f |' % (n, a, b, c, a + b + c))
            if a + b + c > TOO_SLOW:
                skip = True
    print()
    for n, by_name in answers.items():
        if len(set(tuple(v) for v in by_name.values())) > 1:
            print('WARNING: at n = %d the queues did not remove the same priorities in the same order.' % n)


if __name__ == '__main__':
    main()
