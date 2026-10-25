"""
Part D, step 2: time something yourself, two different ways.

Before you use the provided timing.py, get a feel for timing by doing it by hand.
You will time how long it takes to insert one value at the FRONT of your array
list that already holds n values (you know that has to shift all n values).

Run it with:   python3 my_timing.py
"""
import time
import timeit

from array_list import *


def build_array_list(n):
    """An array list holding the numbers 0 .. n-1. (Provided.)"""
    lst = create_array_list()
    for i in range(n):
        array_list_insert_at(lst, i, i)
    return lst


# ----------------------------------------------------------------------------
# Approach 1: a STOPWATCH. Note the time, do the thing once, note the time again.
# time.perf_counter() returns the current time in seconds, as a decimal number.
# ----------------------------------------------------------------------------
def stopwatch_microseconds(n):
    """Time ONE insert at index 0 into an array list holding n values. Returns microseconds."""
    lst = build_array_list(n)
    start = time.perf_counter()
    array_list_insert_at(lst, 0, -1)
    end = time.perf_counter()
    return (end - start) * 1_000_000        # seconds -> microseconds


# ----------------------------------------------------------------------------
# Approach 2: timeit. It runs a piece of code MANY times and tells you the TOTAL
# seconds, so you can average. Timing one run can be thrown off by anything else
# your computer is doing at that moment; an average of many runs is steadier.
#
#     seconds = timeit.timeit(some_function, number=20)
#
# `some_function` is a function that takes no arguments. To make one on the spot
# use a lambda:   lambda: array_list_get(lst, 0)
#
# Each repeat must leave the list the same size, or the list would keep getting
# bigger as you time it. So insert at the front and then remove from the front,
# and divide by 2 to get the cost of one operation. (Both shift n values.)
# ----------------------------------------------------------------------------
def timeit_microseconds(n, repeats=20):
    """Average microseconds for ONE insert at index 0, over `repeats` runs."""
    lst = build_array_list(n)
    seconds = timeit.timeit(
        lambda: (array_list_insert_at(lst, 0, -1), array_list_remove_at(lst, 0)),
        number=repeats)
    return seconds / repeats / 2 * 1_000_000


def main():
    print('microseconds to insert one value at the FRONT of an array list of n values')
    print('%10s %14s %14s' % ('n', 'stopwatch', 'timeit'))
    for n in (1_000, 10_000, 100_000):
        print('%10s %14.1f %14.1f' % (format(n, ','), stopwatch_microseconds(n), timeit_microseconds(n)))


if __name__ == '__main__':
    main()
