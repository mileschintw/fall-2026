"""
Helpers for checking a Hand (a doubly linked list stored in a dict) and for
checking that no cards are ever lost or duplicated.

The provided tests use these, and you are encouraged to call them in tests of
your own, for example right after every operation you write:

    add_card_to_hand(hand, card)
    assert_hand_valid(hand)

A hand is VALID when:
  * following the 'next' pointers from the first card visits every card exactly
    once and then ends (no cycles);
  * the number of cards found that way equals hand['num_cards_in_hand'];
  * the first card's 'prev' is None;
  * every other card's 'prev' points back at the card before it.

Cards are CONSERVED when the deck and the hands together hold exactly the cards
you started with: none missing, none duplicated, none invented.
"""
from collections import Counter

from game_structures import *

# A hand never has anywhere near this many cards; this only guards against a
# runaway loop if a student's pointers form a cycle.
_MAX_CARDS = 1000


def _label(card):
    if isinstance(card, tuple) and len(card) == 4:
        return str(card[CARD_NAME_INDEX])
    return str(card)


def hand_cards(hand):
    """Return the cards (payloads) in the hand, front to back, as a Python list.

    Stops early (instead of looping forever) if the 'next' pointers form a cycle.
    """
    cards = []
    seen = set()
    node = hand[HAND_FIRST_CARD_KEY]
    while node is not None and id(node) not in seen and len(cards) < _MAX_CARDS:
        seen.add(id(node))
        cards.append(node[CARD_NODE_PAYLOAD_KEY])
        node = node[CARD_NODE_NEXT_KEY]
    return cards


def hand_problems(hand):
    """Return a list of sentences describing everything wrong with the hand.

    An empty list means the hand is valid.
    """
    problems = []
    nodes = []
    seen = set()
    node = hand[HAND_FIRST_CARD_KEY]
    while node is not None:
        if id(node) in seen:
            problems.append("following 'next' pointers loops back to a card that was already "
                            "visited (a cycle) after %d cards" % len(nodes))
            break
        if len(nodes) >= _MAX_CARDS:
            problems.append("following 'next' pointers never ends")
            break
        seen.add(id(node))
        nodes.append(node)
        node = node[CARD_NODE_NEXT_KEY]

    claimed = hand[HAND_NUM_CARDS_KEY]
    if len(nodes) != claimed:
        problems.append("the hand says it has %d cards, but following 'next' pointers "
                        "finds %d" % (claimed, len(nodes)))

    if nodes and nodes[0][CARD_NODE_PREV_KEY] is not None:
        problems.append("the first card's 'prev' should be None")

    for i in range(1, len(nodes)):
        if nodes[i][CARD_NODE_PREV_KEY] is not nodes[i - 1]:
            problems.append("the 'prev' of the card at index %d does not point back at the "
                            "card at index %d" % (i, i - 1))
    return problems


def assert_hand_valid(hand):
    """Raise an AssertionError that explains what is wrong, unless the hand is valid."""
    problems = hand_problems(hand)
    if problems:
        cards = [_label(c) for c in hand_cards(hand)]
        raise AssertionError("Invalid hand:\n  - " + "\n  - ".join(problems) +
                             "\n  (cards found going forward: %s)" % cards)


def assert_cards_conserved(expected_cards, *places):
    """Raise an AssertionError unless `places` hold exactly `expected_cards`.

    Each place is either a deck (a Python list) or a hand (a dict). Order does not
    matter, but every card must appear exactly as many times as in expected_cards.
    """
    found = []
    for place in places:
        if isinstance(place, dict):
            found.extend(hand_cards(place))
        else:
            found.extend(place)
    expected_counts, found_counts = Counter(expected_cards), Counter(found)
    missing = list((expected_counts - found_counts).elements())
    extra = list((found_counts - expected_counts).elements())
    if missing or extra:
        message = ["Cards were lost or duplicated:"]
        if missing:
            message.append("  - missing: %s" % [_label(c) for c in missing])
        if extra:
            message.append("  - extra or duplicated: %s" % [_label(c) for c in extra])
        raise AssertionError("\n".join(message))
