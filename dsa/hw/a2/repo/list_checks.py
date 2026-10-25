"""
Helpers that check a list is correct INSIDE, not just that its values look right.

A list can print the right values and still be broken inside: a 'size' that is
off by one, a vacated slot that was never cleared, a link that goes nowhere or
loops back. Bugs like that blow up later, far from where they were made.

The provided tests call these helpers after every operation, and you are
encouraged to do the same in your own tests:

    array_list_insert_at(lst, 0, 'x')
    assert_array_list_valid(lst)

An ARRAY LIST is valid when:
  * 'data' is a Python list with at least one slot
  * 0 <= 'size' <= the number of slots (the capacity)
  * every slot from 'size' onward is None

A LINKED LIST is valid when:
  * following the 'next' links from the head reaches the end (None) without
    going in a circle
  * the number of nodes found that way equals 'size'
"""
from array_list import ARRAY_DATA_KEY, ARRAY_SIZE_KEY, ARRAY_MOVES_KEY
from linked_list import LIST_HEAD_KEY, LIST_SIZE_KEY, NODE_PAYLOAD_KEY, NODE_NEXT_KEY

_MAX_NODES = 1000000   # only a guard against a runaway loop if links form a circle


# ------------------------------- array list -------------------------------
def array_contents(lst):
    """The stored values (slots 0 .. size-1), read directly from the structure."""
    data, size = lst[ARRAY_DATA_KEY], lst[ARRAY_SIZE_KEY]
    return [data[i] for i in range(min(size, len(data)))]


def array_problems(lst):
    """Returns a list of sentences describing what is wrong (empty = valid)."""
    problems = []
    data, size, moves = lst[ARRAY_DATA_KEY], lst[ARRAY_SIZE_KEY], lst[ARRAY_MOVES_KEY]
    if not isinstance(data, list) or len(data) < 1:
        return ["'data' must be a Python list with at least one slot"]
    if not isinstance(size, int) or size < 0:
        return ["'size' must be a whole number that is not negative (it is %r)" % (size,)]
    if size > len(data):
        problems.append("'size' (%d) is bigger than the number of slots (%d)" % (size, len(data)))
    for i in range(size, len(data)):
        if data[i] is not None:
            problems.append("slot %d is past the end of the list (size is %d) but holds %r. "
                            "Empty slots must be None" % (i, size, data[i]))
            break
    if not isinstance(moves, int) or moves < 0:
        problems.append("'moves' must be a whole number that is not negative (it is %r)" % (moves,))
    return problems


def assert_array_list_valid(lst):
    """Raises an AssertionError that explains the problem, unless the list is valid."""
    problems = array_problems(lst)
    if problems:
        raise AssertionError("Invalid array list:\n  - " + "\n  - ".join(problems) +
                             "\n  (values found: %s)" % (array_contents(lst),))


# ------------------------------ linked list ------------------------------
def linked_nodes(lst):
    """The nodes in order, starting at the head. Stops if the links go in a circle."""
    nodes, seen = [], set()
    node = lst[LIST_HEAD_KEY]
    while node is not None and id(node) not in seen and len(nodes) < _MAX_NODES:
        seen.add(id(node))
        nodes.append(node)
        node = node[NODE_NEXT_KEY]
    return nodes


def linked_contents(lst):
    """The values in order, read directly from the nodes."""
    return [node[NODE_PAYLOAD_KEY] for node in linked_nodes(lst)]


def linked_problems(lst):
    """Returns a list of sentences describing what is wrong (empty = valid)."""
    problems = []
    nodes = linked_nodes(lst)
    last = nodes[-1] if nodes else None
    if last is not None and last[NODE_NEXT_KEY] is not None:
        problems.append("following 'next' links goes in a circle: the last node reached "
                        "links back to a node that was already visited")
    if len(nodes) != lst[LIST_SIZE_KEY]:
        problems.append("the list says its 'size' is %r, but following the links finds %d nodes"
                        % (lst[LIST_SIZE_KEY], len(nodes)))
    return problems


def assert_linked_list_valid(lst):
    """Raises an AssertionError that explains the problem, unless the list is valid."""
    problems = linked_problems(lst)
    if problems:
        raise AssertionError("Invalid linked list:\n  - " + "\n  - ".join(problems) +
                             "\n  (values found: %s)" % (linked_contents(lst),))
