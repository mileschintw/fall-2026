"""
Part B: A list stored in an ARRAY.

An array is a block of memory with a FIXED number of slots. You can read or
write any slot instantly (that is what makes arrays fast), but you cannot make
the block bigger. Python's own `list` hides this from you: it quietly grows
whenever you append. In this file you build that "growing" behavior yourself.

To do that we use an ordinary Python list as if it were a fixed-size array:

    data = [None] * capacity      # made once; its length never changes

THE RULES
  * Never change the length of a `data` list. In the functions you write (all of
    them except array_list_to_python_list) do NOT use any of these:
        append, insert, pop, remove, extend, clear, copy, sort, reverse, index,
        del, slicing like data[a:b], list(...), sorted(...), reversed(...)
    You only read and write single slots (data[i] = ...) and use loops.
    The tests check this.
  * When you need more room, make a NEW, bigger `data` list and copy the values
    over one at a time.

AN ARRAY LIST is a dict with three keys:
    'data'   the fixed-size Python list. Its length is the CAPACITY.
    'size'   how many values are stored. They live in slots 0 .. size-1.
    'moves'  a running count of how many values have been copied or shifted so
             far. (Your code updates it; see each function. The tests and the
             timing experiment use it to measure how much work was done.)

Slots from `size` onward are EMPTY, and an empty slot always holds None.

THE FUNCTIONS
  Your array lists use zero-based indexes, just like Python lists. A valid
  index for reading or removing is 0 .. size-1. For inserting it is 0 .. size
  (inserting at `size` adds at the end). Negative indexes are NOT allowed.
  An invalid index raises an IndexError, and the list must be left unchanged
  (as if you had never called the function).

  To raise an error:      raise IndexError("index out of range")

Run the tests with:  python3 array_list_test.py
"""

ARRAY_DATA_KEY = 'data'
ARRAY_SIZE_KEY = 'size'
ARRAY_MOVES_KEY = 'moves'

DEFAULT_CAPACITY = 4
GROWTH_FACTOR = 2


def create_array_list(capacity=DEFAULT_CAPACITY):
    """
    Creates a new, empty array list. (Provided -- nothing to do here.)

    Args:
        capacity (int): The number of slots to start with. Must be at least 1.

    Returns:
        dict: {'data': [None, None, ...], 'size': 0, 'moves': 0}
    """
    assert capacity >= 1, 'capacity must be at least 1'
    return {ARRAY_DATA_KEY: [None] * capacity,
            ARRAY_SIZE_KEY: 0,
            ARRAY_MOVES_KEY: 0}


# ---------------------------------------------------------------------------
# TODO 1
# ---------------------------------------------------------------------------
def array_list_length(lst):
    """
    Returns how many values are stored in the list (NOT the capacity).

    Args:
        lst (dict): An array list.

    Returns:
        int: The number of values stored.
    """
    return lst[ARRAY_SIZE_KEY]


# ---------------------------------------------------------------------------
# TODO 2
# ---------------------------------------------------------------------------
def array_list_get(lst, index):
    """
    Returns the value stored at the given index. The list is not changed.

    Args:
        lst (dict): An array list.
        index (int): A position, 0 .. size-1.

    Returns:
        The value at that position.

    Raises:
        IndexError: If index is not in 0 .. size-1 (negative indexes included).
    """
    if index < 0 or index >= lst[ARRAY_SIZE_KEY]:
        raise IndexError("index out of range")

    return lst[ARRAY_DATA_KEY][index]


# ---------------------------------------------------------------------------
# TODO 3
# ---------------------------------------------------------------------------
def array_list_grow(lst):
    """
    Makes room: replaces the list's data with a NEW list that has
    GROWTH_FACTOR times as many slots, and copies the stored values into it.

    * The new data list has capacity (old capacity * GROWTH_FACTOR) slots.
    * Copy the `size` stored values into the same positions, one at a time.
    * Every slot past the stored values is None.
    * 'size' does not change. Add the number of values you copied to 'moves'.

    Args:
        lst (dict): An array list. Changed in place.

    Returns:
        None
    """

    capacity = len(lst[ARRAY_DATA_KEY])
    new_list = [None] * capacity * GROWTH_FACTOR

    for i in range(lst[ARRAY_SIZE_KEY]):
        lst[ARRAY_MOVES_KEY] += 1
        new_list[i] = lst[ARRAY_DATA_KEY][i]

    lst[ARRAY_DATA_KEY] = new_list


# ---------------------------------------------------------------------------
# TODO 4
# ---------------------------------------------------------------------------
def array_list_insert_at(lst, index, value):
    """
    Inserts a value so that it ends up at the given index. Values at that index
    and after it move one position toward the end.

    Steps:
      1. If index is not in 0 .. size, raise IndexError. Do this FIRST, before
         changing anything (a failed insert must not even grow the list).
      2. If the array is full (size == capacity), call array_list_grow.
      3. Shift the values at index .. size-1 one slot to the right. Start from
         the END so you do not overwrite anything. Add 1 to 'moves' for every
         value you shift. (Inserting at the end shifts nothing.)
      4. Store the new value at the index and add 1 to 'size'.

    Args:
        lst (dict): An array list. Changed in place.
        index (int): Where the new value should end up, 0 .. size.
        value: The value to insert (can be anything, including None).

    Returns:
        None

    Raises:
        IndexError: If index is not in 0 .. size.
    """

    size = lst[ARRAY_SIZE_KEY]
    if index < 0 or index > size:
        raise IndexError("index out of range")

    if size == len(lst[ARRAY_DATA_KEY]):
        array_list_grow(lst)

    data = lst[ARRAY_DATA_KEY]
    for i in range(size, index, -1):
        data[i] = data[i-1]
        lst[ARRAY_MOVES_KEY] += 1

    data[index] = value
    lst[ARRAY_SIZE_KEY] += 1


# ---------------------------------------------------------------------------
# TODO 5
# ---------------------------------------------------------------------------
def array_list_remove_at(lst, index):
    """
    Removes the value at the given index and returns it. Values after it move
    one position toward the front.

    Steps:
      1. If index is not in 0 .. size-1, raise IndexError (change nothing).
      2. Remember the value at the index (you will return it).
      3. Shift the values at index+1 .. size-1 one slot to the LEFT. Add 1 to
         'moves' for every value you shift. (Removing the last value shifts
         nothing.)
      4. The slot that is now unused (the old last slot) must be set back to
         None. Subtract 1 from 'size'. Do not shrink the array.
      5. Return the value you remembered.

    Args:
        lst (dict): An array list. Changed in place.
        index (int): The position to remove, 0 .. size-1.

    Returns:
        The value that was removed.

    Raises:
        IndexError: If index is not in 0 .. size-1.
    """

    size = lst[ARRAY_SIZE_KEY]
    if index < 0 or index >= size:
        raise IndexError("index out of range")

    data = lst[ARRAY_DATA_KEY]
    removed = data[index]
    for i in range(index, size - 1):
        data[i] = data[i+1]
        lst[ARRAY_MOVES_KEY] += 1

    data[size - 1] = None
    lst[ARRAY_SIZE_KEY] -= 1
    return removed



# ---------------------------------------------------------------------------
# TODO 6
# ---------------------------------------------------------------------------
def array_list_to_python_list(lst):
    """
    Returns a NEW ordinary Python list holding the stored values in order.
    (Only the stored values: not the empty slots.) The array list and its
    'moves' count are not changed. This is the one function where you may use
    Python list tools such as append.

    Args:
        lst (dict): An array list.

    Returns:
        list: The stored values, in order.
    """

    new_list = []
    for i in range(lst[ARRAY_SIZE_KEY]):
        new_list.append(lst[ARRAY_DATA_KEY][i])

    return new_list
