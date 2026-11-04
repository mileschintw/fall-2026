"""A tiny help desk, built from the pieces we have covered in class.

Tickets are submitted into a queue, worked in order, and moved to a list of closed tickets.
The most recently closed ticket can be reopened with undo_close.

Everything is a function that takes the structure as its first argument (no classes). Read the
docstrings: each one says what the function must do, and that is the only definition of "correct".
"""

# ---------------------------------------------------------------- dynamic array

def da_create():
    """Return an empty dynamic array. It starts with room for 4 elements."""
    return {'slots': [None] * 4, 'size': 0}


def da_append(arr, value):
    """Add value at the end. When the array is full, its capacity doubles and every element is kept.
    Appending n items takes O(n) time in total."""
    if arr['size'] == len(arr['slots']):
        bigger = [None] * (len(arr['slots']) * 2)
        for i in range(arr['size']):
            bigger[i] = arr['slots'][i]
        arr['slots'] = bigger
    arr['slots'][arr['size']] = value
    arr['size'] += 1


def da_get(arr, index):
    """Return the element at index, for 0 <= index < size.
    Any other index, including a negative one, raises IndexError."""
    if index < 0 or index >= arr['size']:
        raise IndexError('index out of range')
    return arr['slots'][index]


def da_remove_last(arr):
    """Remove and return the last element. Raises IndexError if the array is empty."""
    if arr['size'] == 0:
        raise IndexError('array is empty')
    value = arr['slots'][arr['size'] - 1]
    arr['size'] -= 1
    arr['slots'][arr['size']] = None
    return value


def da_to_list(arr):
    """Return the elements, in order, as an ordinary list."""
    return [arr['slots'][i] for i in range(arr['size'])]


# ---------------------------------------------------------------- stack

def stack_create():
    """Return an empty stack."""
    return []


def stack_push(s, value):
    """Put value on top of the stack."""
    s.append(value)


def stack_pop(s):
    """Remove and return the top item. An empty stack returns None."""
    if len(s) == 0:
        return None
    return s.pop()


def stack_is_empty(s):
    """Return True if the stack has no items."""
    return len(s) == 0


# ---------------------------------------------------------------- queue

def queue_create():
    """Return an empty queue."""
    return {'items': [], 'head': 0}


def queue_enqueue(q, value):
    """Add value at the back of the queue."""
    q['items'].append(value)


def queue_dequeue(q):
    """Remove and return the front item. An empty queue returns None.
    Each call takes constant time, so dequeuing n items takes O(n) in total."""
    if q['head'] >= len(q['items']):
        return None
    value = q['items'][q['head']]
    q['head'] += 1
    return value


def queue_peek(q):
    """Return the front item without removing it. An empty queue returns None."""
    if q['head'] >= len(q['items']):
        return None
    return q['items'][q['head']]


def queue_size(q):
    """Return how many items are waiting in the queue."""
    return len(q['items']) - q['head']


def queue_push_front(q, value):
    """Put value at the FRONT of the queue, so it is the next one dequeued."""
    if q['head'] > 0:
        q['head'] -= 1
        q['items'][q['head']] = value
    else:
        q['items'].insert(0, value)


# ---------------------------------------------------------------- the help desk

def desk_create():
    """Return a new, empty help desk."""
    return {'open': queue_create(), 'undo': stack_create(), 'closed': da_create(), 'next_id': 1}


def submit(desk, text):
    """Add a ticket to the back of the open queue and return it.
    A ticket is a dict {'id': n, 'text': text}. The first ticket has id 1, then 2, 3, ...
    An id is never reused."""
    ticket = {'id': desk['next_id'], 'text': text}
    desk['next_id'] += 1
    queue_enqueue(desk['open'], ticket)
    return ticket


def work_next(desk):
    """Take the ticket at the front of the open queue and close it: it is added to the end of the
    closed list. Return that ticket, or None if no ticket is open."""
    ticket = queue_dequeue(desk['open'])
    if ticket is None:
        return None
    da_append(desk['closed'], ticket)
    stack_push(desk['undo'], ticket)
    return ticket


def undo_close(desk):
    """Reopen the most recently closed ticket that has not already been reopened.
    It leaves the closed list and goes back to the FRONT of the open queue, so it is worked next.
    Return that ticket, or None if there is nothing to undo."""
    ticket = stack_pop(desk['undo'])
    if ticket is None:
        return None
    da_remove_last(desk['closed'])
    queue_push_front(desk['open'], ticket)
    return ticket


def next_ticket(desk):
    """Return the ticket that work_next would close, without closing it, or None."""
    return queue_peek(desk['open'])


def open_count(desk):
    """Return the number of open tickets."""
    return queue_size(desk['open'])


def closed_count(desk):
    """Return the number of closed tickets."""
    return desk['closed']['size']


def closed_ids(desk):
    """Return the ids of the closed tickets, in the order they were closed."""
    return [t['id'] for t in da_to_list(desk['closed'])]


def brackets_balanced(text):
    """Return True if every (, [ and { in text is closed by the matching bracket, in the right order.
    All other characters are ignored. The empty string is balanced."""
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = stack_create()
    for ch in text:
        if ch in '([{':
            stack_push(stack, ch)
        elif ch in pairs:
            if stack_pop(stack) != pairs[ch]:
                return False
    return stack_is_empty(stack)
