import random
import unittest

from game_structures import *
from hand_invariants import assert_hand_valid, hand_cards

class CardNodeTestCase(unittest.TestCase):
    def test_create_card_node(self):
        card_node = create_card_node("my_payload")

        self.assertEqual(card_node[CARD_NODE_PAYLOAD_KEY], 'my_payload')
        self.assertIsNone(card_node[CARD_NODE_NEXT_KEY])
        self.assertIsNone(card_node[CARD_NODE_PREV_KEY])

class DeckTestCase(unittest.TestCase):
    def test_create_deck(self):
        deck = create_deck()
        self.assertEqual(NUM_CARDS_IN_DECK, len(deck))

    def test_push_card_to_deck_adds_card(self):
        """Test that push_card_to_deck successfully adds a card to the deck."""
        deck = ["Ace of Spades", "2 of Hearts"]
        card = "King of Diamonds"
        push_card_to_deck(deck, card)
        self.assertTrue(card in deck)

    def test_push_card_to_deck_increases_size(self):
        """Test that push_card_to_deck increases the deck's size by 1."""
        deck = ["Ace of Spades", "2 of Hearts"]
        card = "King of Diamonds"
        initial_len = len(deck)
        push_card_to_deck(deck, card)
        self.assertEqual(len(deck), initial_len + 1)

    def test_push_card_to_deck_empty_deck(self):
        """Test that push_card_to_deck works correctly for an empty deck."""
        deck = []
        card = "Queen of Clubs"
        push_card_to_deck(deck, card)
        self.assertEqual(deck, ["Queen of Clubs"])

    def test_push_card_to_deck_duplicate_card(self):
        """Test that push_card_to_deck allows duplicate cards in the deck."""
        deck = ["Ace of Spades"]
        card = "Ace of Spades"
        push_card_to_deck(deck, card)
        self.assertEqual(deck.count(card), 2)

    def test_push_card_to_deck(self):
        deck = [] ## Using an empty "deck" to start with
        card1 = create_card(KING, SUIT_HEARTS)
        updated_deck = push_card_to_deck(deck, card1)

        self.assertIsNotNone(updated_deck)
        self.assertEqual(1, len(deck))

        card2 = create_card(QUEEN, SUIT_HEARTS)
        updated_deck = push_card_to_deck(deck, card2)

        self.assertIsNotNone(updated_deck)
        self.assertEqual(2, len(deck))

    def test_peek_deck(self):
        ## Set up
        card1 = create_card(KING, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)
        deck = [ card1, card2 ]

        ## Execute function to test
        card_on_top = peek_card(deck)

        ## Check Assertions
        self.assertIsNotNone(card_on_top)
        self.assertEqual(card2, card_on_top)
        self.assertEqual(2, len(deck))

    def test_pop_deck(self):
        ## Set up
        card1 = create_card(KING, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)
        deck = [ card1, card2 ]

        ## Execute function to test
        card_from_top = pop_card(deck)

        ## Check Assertions
        self.assertIsNotNone(card_from_top)
        self.assertEqual(card2, card_from_top)
        self.assertEqual(1, len(deck))

    def test_deck_is_empty_when_empty(self):
        ## Set up
        deck = [ ]

        ## Execute function to test
        is_empty = is_deck_empty(deck)

        ## Check Assertions
        self.assertTrue(is_empty)
        self.assertEqual(0, len(deck))

    def test_deck_is_empty_when_not_empty(self):
        ## Set up
        card1 = create_card(KING, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)
        deck = [ card1, card2 ]

        ## Execute function to test
        is_empty = is_deck_empty(deck)

        ## Check Assertions
        self.assertFalse(is_empty)
        self.assertEqual(2, len(deck))


class HandTestCase(unittest.TestCase):

    def test_create_hand(self):
        hand = create_hand()
        self.assertIsNone(hand[HAND_FIRST_CARD_KEY])
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 0)
        self.assertTrue(is_hand_empty(hand))

    def test_add_1card_to_hand(self):
        ## Set up
        hand = create_hand()
        card = create_card(JACK, SUIT_HEARTS)

        ## Execute the thing to test
        add_card_to_hand(hand, card)

        ## Evaluate the result for correctness
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 1)
        # self.assertIs(get_card_from_node(hand[HAND_FIRST_CARD]), card)
        self.assertIs(hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY], card)
        self.assertFalse(is_hand_empty(hand))

    def test_add_2cards_to_hand(self):
        ## Set up
        hand = create_hand()
        card = create_card(JACK, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)

        ## Execute the thing to test
        add_card_to_hand(hand, card)
        add_card_to_hand(hand, card2)

        ## Evaluate the result for correctness
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 2)
        self.assertTrue(is_card_in_hand(hand, card))
        self.assertTrue(is_card_in_hand(hand, card2))
        self.assertIs(hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY], card2)

    def test_remove_first_card_from_hand(self):
        ## Set up
        hand = create_hand()
        card = create_card(JACK, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)
        add_card_to_hand(hand, card)
        add_card_to_hand(hand, card2) ## Gets inserted at the head

        ## Execute the thing to test
        removed_card = remove_card_from_hand(hand, card2)

        ## Evaluate the result for correctness
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 1)
        self.assertTrue(is_card_in_hand(hand, card))
        self.assertFalse(is_card_in_hand(hand, card2))
        self.assertIs(removed_card, card2)
        self.assertIs(hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY], card)


    def test_remove_last_card_from_hand(self):
        ## Set up
        hand = create_hand()
        card = create_card(JACK, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)
        add_card_to_hand(hand, card)
        add_card_to_hand(hand, card2)

        ## Execute the thing to test
        removed_card = remove_card_from_hand(hand, card)

        ## Evaluate the result for correctness
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 1)
        self.assertFalse(is_card_in_hand(hand, card))
        self.assertTrue(is_card_in_hand(hand, card2))
        self.assertIs(removed_card, card)
        self.assertIs(hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY], card2)

    def test_remove_nonexistent_card_from_hand(self):
        ## Set up
        hand = create_hand()
        card = create_card(JACK, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)
        card3 = create_card(KING, SUIT_HEARTS)
        add_card_to_hand(hand, card)
        add_card_to_hand(hand, card2)

        ## Execute the thing to test
        removed_card = remove_card_from_hand(hand, card3)

        ## Evaluate the result for correctness
        self.assertIsNone(removed_card)
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 2)
        self.assertTrue(is_card_in_hand(hand, card))
        self.assertTrue(is_card_in_hand(hand, card2))

    def test_get_card_from_hand(self):
        ## Set up
        hand = create_hand()
        card = create_card(JACK, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)
        card3 = create_card(KING, SUIT_HEARTS)
        add_card_to_hand(hand, card)
        add_card_to_hand(hand, card2)
        add_card_to_hand(hand, card3)

        ## Execute the thing to test
        removed_card = remove_card_at_index(hand, 1) ## Remove the "Queen" card

        ## Evaluate the result for correctness
        self.assertEqual(2, hand[HAND_NUM_CARDS_KEY])
        self.assertFalse(is_card_in_hand(hand, card2))
        self.assertTrue(is_card_in_hand(hand, card))
        self.assertTrue(is_card_in_hand(hand, card3))
        self.assertIs(card2, removed_card)

    def test_get_card_from_hand_when_empty(self):
        ## Set up
        hand = create_hand()

        ## Execute the thing to test
        removed_card = remove_card_at_index(hand, 1)

        ## Evaluate the result for correctness
        self.assertEqual(0, hand[HAND_NUM_CARDS_KEY])
        self.assertIsNone(removed_card)

    def test_get_card_from_hand_when_index_is_too_big(self):
        ## Set up
        hand = create_hand()
        card = create_card(JACK, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)
        add_card_to_hand(hand, card)
        add_card_to_hand(hand, card2)

        ## Execute the thing to test
        removed_card = remove_card_at_index(hand, 3)

        ## Evaluate the result for correctness
        self.assertEqual(2, hand[HAND_NUM_CARDS_KEY])
        self.assertIsNone(removed_card)

    def test_add_card_to_hand_empty_hand(self):
        """Test that add_card_to_hand successfully adds a card to an empty hand."""
        hand = {HAND_FIRST_CARD_KEY: None, HAND_NUM_CARDS_KEY: 0}
        card = "Queen of Diamonds"
        add_card_to_hand(hand, card)
        assert hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY] == card
        assert hand[HAND_NUM_CARDS_KEY] == 1

    def test_add_card_to_hand_non_empty_hand(self):
        """Test that add_card_to_hand adds cards to a non-empty hand."""
        hand = {
            HAND_FIRST_CARD_KEY: create_card_node("Ace of Spades"),
            HAND_NUM_CARDS_KEY: 1,
        }
        card = "Jack of Hearts"
        add_card_to_hand(hand, card)
        assert hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY] == card
        assert (
                hand[HAND_FIRST_CARD_KEY][CARD_NODE_NEXT_KEY][CARD_NODE_PAYLOAD_KEY]
                == "Ace of Spades"
        )
        assert hand[HAND_NUM_CARDS_KEY] == 2

    def test_add_card_to_hand_duplicate_cards(self):
        """Test that add_card_to_hand allows duplicate cards in the hand."""
        hand = {
            HAND_FIRST_CARD_KEY: create_card_node("10 of Clubs"),
            HAND_NUM_CARDS_KEY: 1,
        }
        card = "10 of Clubs"
        add_card_to_hand(hand, card)
        assert hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY] == card
        assert hand[HAND_FIRST_CARD_KEY][CARD_NODE_NEXT_KEY][CARD_NODE_PAYLOAD_KEY] == card
        assert hand[HAND_NUM_CARDS_KEY] == 2


    def test_peek_card_at_index_valid_index(self):
        """Test peek_card_at_index returns the correct card for a valid index."""
        hand = create_hand()
        add_card_to_hand(hand, create_card(ACE, SUIT_SPADES))
        add_card_to_hand(hand, create_card(KING, SUIT_HEARTS))
        add_card_to_hand(hand, create_card(QUEEN, SUIT_DIAMONDS))
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 3)

        index = 1
        card = peek_card_at_index(hand, index)
        self.assertEqual(card[CARD_NAME_INDEX], "King of Hearts")
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 3)

    def test_peek_card_at_index_out_of_range_high(self):
        """Test peek_card_at_index returns None when index is out of range (too high)."""
        hand = create_hand()
        add_card_to_hand(hand, create_card(ACE, SUIT_SPADES))
        add_card_to_hand(hand, create_card(KING, SUIT_HEARTS))
        index = 5
        card = peek_card_at_index(hand, index)
        assert card is None

    def test_peek_card_at_index_out_of_range_negative(self):
        """Test peek_card_at_index returns None when index is out of range (negative)."""
        hand = create_hand()
        add_card_to_hand(hand, create_card(ACE, SUIT_SPADES))
        add_card_to_hand(hand, create_card(KING, SUIT_HEARTS))
        index = -3
        card = peek_card_at_index(hand, index)
        assert card is None

    def test_peek_card_at_index_empty_hand(self):
        """Test peek_card_at_index returns None when the hand is empty."""
        hand = create_hand()
        index = 0
        card = peek_card_at_index(hand, index)
        assert card is None

# Test cases for the functions in a3.py
class GeneralTest(unittest.TestCase):
    def test_deck(self):
        deck = create_deck()

        self.assertFalse(is_deck_empty(deck))
        self.assertEqual(len(deck), NUM_CARDS_IN_DECK)

        print_deck(deck)

    def test_remove_hand_front(self):
        hand = create_hand()
        add_card_to_hand(hand, (JACK, SUIT_HEARTS))
        add_card_to_hand(hand, (QUEEN, SUIT_HEARTS))
        add_card_to_hand(hand, (KING, SUIT_HEARTS))
        add_card_to_hand(hand, (ACE, SUIT_HEARTS))

        remove_card_from_hand(hand, (ACE, SUIT_HEARTS))
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 3)
        self.assertEqual(hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY], (KING, SUIT_HEARTS))

        remove_card_at_index(hand, 0)
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 2)
        self.assertEqual(hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY], (QUEEN, SUIT_HEARTS))

    def test_remove_hand_middle(self):
        hand = create_hand()
        add_card_to_hand(hand, (JACK, SUIT_HEARTS))
        add_card_to_hand(hand, (QUEEN, SUIT_HEARTS))
        add_card_to_hand(hand, (KING, SUIT_HEARTS))
        add_card_to_hand(hand, (ACE, SUIT_HEARTS))

        remove_card_from_hand(hand, (KING, SUIT_HEARTS))
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 3)
        self.assertEqual(hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY], (ACE, SUIT_HEARTS))
        remove_card_at_index(hand, 1)
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 2)
        self.assertEqual(hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY], (ACE, SUIT_HEARTS))

    def test_remove_hand_end(self):
        hand = create_hand()
        add_card_to_hand(hand, (JACK, SUIT_HEARTS))
        add_card_to_hand(hand, (QUEEN, SUIT_HEARTS))
        add_card_to_hand(hand, (KING, SUIT_HEARTS))
        add_card_to_hand(hand, (ACE, SUIT_HEARTS))

        remove_card_from_hand(hand, (JACK, SUIT_HEARTS))
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 3)
        self.assertEqual((ACE, SUIT_HEARTS), hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY])

        self.assertIsNone(remove_card_at_index(hand, 3))
        remove_card_at_index(hand, 2)
        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 2)
        self.assertEqual((ACE, SUIT_HEARTS), hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY])

    def test_remove_hand_all(self):
        hand = create_hand()
        add_card_to_hand(hand, (JACK, SUIT_HEARTS))
        add_card_to_hand(hand, (QUEEN, SUIT_HEARTS))
        add_card_to_hand(hand, (KING, SUIT_HEARTS))

        self.assertEqual((KING, SUIT_HEARTS), remove_card_at_index(hand, 0))
        self.assertEqual((QUEEN, SUIT_HEARTS), remove_card_at_index(hand, 0))
        self.assertEqual((JACK, SUIT_HEARTS), remove_card_at_index(hand, 0))

        self.assertEqual(hand[HAND_NUM_CARDS_KEY], 0)
        self.assertIsNone(remove_card_at_index(hand, 0))


class DeckOrderTestCase(unittest.TestCase):
    def test_deck_is_last_in_first_out(self):
        deck = []
        cards = [create_card(face, SUIT_SPADES) for face in (VAL_9, VAL_10, JACK)]
        for card in cards:
            push_card_to_deck(deck, card)

        self.assertEqual(cards[2], peek_card(deck))
        self.assertEqual(3, len(deck))
        self.assertEqual(cards[2], pop_card(deck))
        self.assertEqual(cards[1], pop_card(deck))
        self.assertEqual(cards[0], pop_card(deck))
        self.assertTrue(is_deck_empty(deck))


class HandInvariantTestCase(unittest.TestCase):
    """
    These tests check that the hand is a *correct* doubly linked list after every
    operation: the count is right, 'next' and 'prev' agree with each other, and
    there are no cycles. See hand_invariants.py for the exact rules.
    """

    def build_hand(self, cards):
        """Build a hand whose front-to-back order is `cards`.

        add_card_to_hand puts each card at the front, so the cards go in reversed.
        """
        hand = create_hand()
        for card in reversed(cards):
            add_card_to_hand(hand, card)
        return hand

    def check(self, hand, expected_cards, context=''):
        """The hand must be valid and hold exactly expected_cards, front to back."""
        try:
            assert_hand_valid(hand)
        except AssertionError as error:
            self.fail('%s %s' % (context, error))
        self.assertEqual(expected_cards, hand_cards(hand), context)
        self.assertEqual(len(expected_cards), hand[HAND_NUM_CARDS_KEY], context)
        self.assertEqual(len(expected_cards) == 0, is_hand_empty(hand), context)

    def test_empty_hand_is_valid(self):
        self.check(create_hand(), [])

    def test_add_card_puts_it_at_the_front_and_keeps_hand_valid(self):
        cards = create_deck()[:5]
        hand = create_hand()
        for i, card in enumerate(cards):
            add_card_to_hand(hand, card)
            self.check(hand, list(reversed(cards[:i + 1])), 'after adding card %d' % i)

    def test_remove_card_from_hand_at_every_position(self):
        for position in range(5):
            cards = create_deck()[:5]
            hand = self.build_hand(cards)

            removed = remove_card_from_hand(hand, cards[position])

            self.assertEqual(cards[position], removed)
            self.check(hand, cards[:position] + cards[position + 1:], 'removed position %d' % position)

    def test_remove_card_at_index_at_every_position(self):
        for position in range(5):
            cards = create_deck()[:5]
            hand = self.build_hand(cards)

            removed = remove_card_at_index(hand, position)

            self.assertEqual(cards[position], removed)
            self.check(hand, cards[:position] + cards[position + 1:], 'removed position %d' % position)

    def test_remove_every_card_from_the_front(self):
        cards = create_deck()[:5]
        hand = self.build_hand(cards)
        while cards:
            self.assertEqual(cards.pop(0), remove_card_at_index(hand, 0))
            self.check(hand, cards)
        self.assertIsNone(hand[HAND_FIRST_CARD_KEY])
        self.assertEqual(0, hand[HAND_NUM_CARDS_KEY])

    def test_remove_every_card_from_the_back(self):
        cards = create_deck()[:5]
        hand = self.build_hand(cards)
        while cards:
            last_index = len(cards) - 1
            self.assertEqual(cards.pop(), remove_card_at_index(hand, last_index))
            self.check(hand, cards)

    def test_remove_card_that_is_not_in_the_hand(self):
        cards = create_deck()[:5]
        hand = self.build_hand(cards)

        self.assertIsNone(remove_card_from_hand(hand, create_deck()[10]))

        self.check(hand, cards)

    def test_remove_card_at_index_out_of_range_changes_nothing(self):
        cards = create_deck()[:5]
        hand = self.build_hand(cards)

        for index in (-1, 5, 6, 100):
            self.assertIsNone(remove_card_at_index(hand, index))
            self.check(hand, cards, 'index %d' % index)

    def test_remove_card_from_hand_removes_only_the_first_match(self):
        ace_spades = create_card(ACE, SUIT_SPADES)
        king_hearts = create_card(KING, SUIT_HEARTS)
        hand = self.build_hand([ace_spades, king_hearts, ace_spades])  # same card twice

        self.assertEqual(ace_spades, remove_card_from_hand(hand, ace_spades))

        self.check(hand, [king_hearts, ace_spades])

    def test_remove_card_at_index_removes_that_position_even_with_equal_cards(self):
        ace_spades = create_card(ACE, SUIT_SPADES)
        king_hearts = create_card(KING, SUIT_HEARTS)
        hand = self.build_hand([ace_spades, king_hearts, ace_spades])  # same card at index 0 and 2

        self.assertEqual(ace_spades, remove_card_at_index(hand, 2))

        self.check(hand, [ace_spades, king_hearts])

    def test_hand_always_matches_a_python_list_under_random_operations(self):
        """
        Do many random operations on a hand and on a plain Python list at the same
        time. The two must always agree, and the hand must always be valid.
        (All the cards in a hand are different, like in a real deck.)
        """
        cards = create_deck()
        for seed in range(40):
            rng = random.Random(seed)
            hand = create_hand()
            model = []  # front to back
            for step in range(80):
                operation = rng.choice(['add', 'add', 'remove_card', 'remove_index', 'peek'])
                context = 'seed %d, step %d, %s' % (seed, step, operation)
                if operation == 'add':
                    not_in_hand = [c for c in cards if c not in model]
                    if not not_in_hand:
                        continue
                    card = rng.choice(not_in_hand)  # a real deck never has two equal cards
                    add_card_to_hand(hand, card)
                    model.insert(0, card)
                elif operation == 'remove_card':
                    card = rng.choice(cards)
                    expected = card if card in model else None
                    if card in model:
                        model.remove(card)  # removes the first match, like the hand should
                    self.assertEqual(expected, remove_card_from_hand(hand, card), context)
                elif operation == 'remove_index':
                    index = rng.randint(-1, len(model) + 1)
                    expected = model.pop(index) if 0 <= index < len(model) else None
                    self.assertEqual(expected, remove_card_at_index(hand, index), context)
                else:
                    index = rng.randint(-1, len(model) + 1)
                    expected = model[index] if 0 <= index < len(model) else None
                    self.assertEqual(expected, peek_card_at_index(hand, index), context)
                self.check(hand, model, context)


if __name__ == '__main__':
    unittest.main()
