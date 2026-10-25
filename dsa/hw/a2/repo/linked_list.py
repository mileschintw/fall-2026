"""
Part C: A SINGLY LINKED LIST.

A linked list stores each value in its own small piece of memory, called a
NODE. A node holds a value and a link to the next node. There is no big block
of slots, so there is no capacity and nothing to grow or shift. The price is
that to reach the 5th value you must start at the front and follow 4 links.

    head --> [ 'a' | * ] --> [ 'b' | * ] --> [ 'c' | None ]

A NODE is a dict with two keys:
    'payload'  the value stored in this node
    'next'     the next node, or None if this is the last node

A LINKED LIST is a dict with two keys:
    'head'     the first node, or None if the list is empty
    'size'     how many nodes are in the list

THE RULES
  * Use nodes. Do not store the values in a Python list, and do not call
    array_list functions or any *_to_python_list function inside the functions
    you write (except linked_list_to_python_list, which builds a Python list).
    The tests check this.
  * Keep 'size' correct every time you add or remove a node.

THE FUNCTIONS
  Indexes work like the array list: reading and removing use 0 .. size-1,
  inserting uses 0 .. size, and negative indexes are NOT allowed. An invalid
  index raises an IndexError and the list must be left unchanged.

  To raise an error:      raise IndexError("index out of range")

Run the tests with:  python3 linked_list_test.py
"""

LIST_HEAD_KEY = 'head'
LIST_SIZE_KEY = 'size'
NODE_PAYLOAD_KEY = 'payload'
NODE_NEXT_KEY = 'next'


def create_node(value):
    """Creates a node holding the value, linked to nothing. (Provided.)"""
    return {NODE_PAYLOAD_KEY: value, NODE_NEXT_KEY: None}


def create_linked_list():
    """Creates a new, empty linked list. (Provided -- nothing to do here.)"""
    return {LIST_HEAD_KEY: None, LIST_SIZE_KEY: 0}


# ---------------------------------------------------------------------------
# TODO 1
# ---------------------------------------------------------------------------
def linked_list_length(lst):
    """
    Returns how many values are in the list.

    Args:
        lst (dict): A linked list.

    Returns:
        int: The number of nodes in the list.
    """
    return lst[LIST_SIZE_KEY]


# ---------------------------------------------------------------------------
# TODO 2
# ---------------------------------------------------------------------------
def linked_list_get(lst, index):
    """
    Returns the value at the given index. The list is not changed.

    Start at the head and follow 'next' links `index` times.

    Args:
        lst (dict): A linked list.
        index (int): A position, 0 .. size-1.

    Returns:
        The value stored in that node.

    Raises:
        IndexError: If index is not in 0 .. size-1 (negative indexes included).
    """
    size = lst[LIST_SIZE_KEY]
    if index < 0 or index >= size:
        raise IndexError("index out of range")

    node = lst[LIST_HEAD_KEY]
    for _ in range(index):
        node = node[NODE_NEXT_KEY]

    return node[NODE_PAYLOAD_KEY]


# ---------------------------------------------------------------------------
# TODO 3
# ---------------------------------------------------------------------------
def linked_list_insert_at(lst, index, value):
    """
    Inserts a new node holding the value so that it ends up at the given index.

    Hints: inserting at index 0 is special (there is no node before it: the
    list's 'head' changes). Otherwise, walk to the node just BEFORE the spot,
    and fix its 'next'. Draw it first. Don't forget 'size'.

    Args:
        lst (dict): A linked list. Changed in place.
        index (int): Where the new value should end up, 0 .. size.
        value: The value to insert (can be anything, including None).

    Returns:
        None

    Raises:
        IndexError: If index is not in 0 .. size (change nothing).
    """
    size = lst[LIST_SIZE_KEY]
    if index < 0 or index > size:
        raise IndexError("index out of range")

    new_node = create_node(value)
    if index == 0:
        new_node[NODE_NEXT_KEY] = lst[LIST_HEAD_KEY]
        lst[LIST_HEAD_KEY] = new_node
    else:
        node = lst[LIST_HEAD_KEY]
        for _ in range(index - 1):
            node = node[NODE_NEXT_KEY]

        new_node[NODE_NEXT_KEY] = node[NODE_NEXT_KEY]
        node[NODE_NEXT_KEY] = new_node

    lst[LIST_SIZE_KEY] += 1

# ---------------------------------------------------------------------------
# TODO 4
# ---------------------------------------------------------------------------
def linked_list_remove_at(lst, index):
    """
    Removes the node at the given index and returns its value.

    Hints: removing index 0 is special (the 'head' changes). Otherwise walk to
    the node just BEFORE the one you are removing and make it skip over it.
    Don't forget 'size'.

    Args:
        lst (dict): A linked list. Changed in place.
        index (int): The position to remove, 0 .. size-1.

    Returns:
        The value that was in the removed node.

    Raises:
        IndexError: If index is not in 0 .. size-1 (change nothing).
    """
    size = lst[LIST_SIZE_KEY]
    if index < 0 or index >= size:
        raise IndexError("index out of range")

    removed = None
    node = lst[LIST_HEAD_KEY]
    if index == 0:
        removed = node[NODE_PAYLOAD_KEY]
        node = node[NODE_NEXT_KEY]
        lst[LIST_HEAD_KEY] = node
    else:
        for _ in range(index - 1):
            node = node[NODE_NEXT_KEY]

        removed = node[NODE_NEXT_KEY][NODE_PAYLOAD_KEY]
        node[NODE_NEXT_KEY] = node[NODE_NEXT_KEY][NODE_NEXT_KEY]

    lst[LIST_SIZE_KEY] -= 1
    return removed


# ---------------------------------------------------------------------------
# TODO 5
# ---------------------------------------------------------------------------
def linked_list_reverse(lst):
    """
    Reverses the list IN PLACE: afterwards the first value is last and the last
    value is first.

    Do not create any new nodes: reuse the existing nodes and change their
    'next' links (and the list's 'head'). 'size' does not change. This one is a
    classic puzzle, so draw a three-node list and work out which link changes
    when.

    Args:
        lst (dict): A linked list. Changed in place.

    Returns:
        None
    """

    prev = None
    node = lst[LIST_HEAD_KEY]
    nxt = None

    while node:
        nxt = node[NODE_NEXT_KEY]
        node[NODE_NEXT_KEY] = prev
        prev = node
        node = nxt

    lst[LIST_HEAD_KEY] = prev


# ---------------------------------------------------------------------------
# TODO 6
# ---------------------------------------------------------------------------
def linked_list_to_python_list(lst):
    """
    Returns a NEW ordinary Python list holding the values in order, front to
    back. The linked list is not changed. This is the one function where you
    may use Python list tools such as append.

    Args:
        lst (dict): A linked list.

    Returns:
        list: The values, in order.
    """
    pass

    new_list = []

    node = lst[LIST_HEAD_KEY]
    while node:
        new_list.append(node[NODE_PAYLOAD_KEY])
        node = node[NODE_NEXT_KEY]

    return new_list
