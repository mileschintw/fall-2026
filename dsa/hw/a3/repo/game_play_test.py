import random
import unittest

from game_play import *
from hand_invariants import assert_cards_conserved, assert_hand_valid, hand_cards


class DeckTestCase(unittest.TestCase):
    """
    Unit test suite for validating the functionality of card game operations.

    This test suite uses the unittest framework to verify the correctness of
    shuffle, deal, and return_hand_to_deck methods for handling a deck of cards
    and hands in a card game application. The tests ensure proper functionality
    and integrity of the deck and hands during different operations.
    """
    def test_shuffle(self):
        # Set up
        deck = create_deck()
        orig_list = deck[:]

        # Run the thing to test
        shuffle(deck)

        # Observe and check that things are as expected
        self.assertNotEqual(orig_list, deck)

    def test_deal(self):
        deck = create_deck()
        hand1 = create_hand()
        hand2 = create_hand()

        deal(deck, hand1, hand2)

        self.assertEqual(len(deck), NUM_CARDS_IN_DECK - 2 * (NUM_CARDS_IN_HAND))
        self.assertEqual(hand1[HAND_NUM_CARDS_KEY], NUM_CARDS_IN_HAND)
        self.assertEqual(hand2[HAND_NUM_CARDS_KEY], NUM_CARDS_IN_HAND)

    def test_return_hand_to_deck(self):
        deck = create_deck()
        hand1 = create_hand()
        hand2 = create_hand()
        deal(deck, hand1, hand2)

        return_hand_to_deck(hand1, deck)

        self.assertEqual(NUM_CARDS_IN_DECK - NUM_CARDS_IN_HAND, len(deck))
        self.assertTrue(is_hand_empty(hand1))

        return_hand_to_deck(hand2, deck)
        self.assertEqual(NUM_CARDS_IN_DECK, len(deck))
        self.assertTrue(is_hand_empty(hand2))



class GameTestCase(unittest.TestCase):
    def test_is_legal_move(self):
        hand = create_hand()
        # The 4 cards of the p2's hand 
        add_card_to_hand(hand, create_card(KING, SUIT_CLUBS))
        add_card_to_hand(hand, create_card(VAL_10, SUIT_SPADES))
        add_card_to_hand(hand, create_card(VAL_9, SUIT_HEARTS))
        add_card_to_hand(hand, create_card(QUEEN, SUIT_HEARTS))

        # p1's play
        p1_card = create_card(ACE, SUIT_CLUBS)
        # p2's play
        p2_card = create_card(QUEEN, SUIT_CLUBS)
        
        # This is a legal move because both are of the same suit.
        result = is_legal_move(hand, p1_card, p2_card)
        self.assertTrue(result)

        # p1's play
        p1_card = create_card(ACE, SUIT_CLUBS)
        # p2's play
        p2_card = create_card(VAL_9, SUIT_CLUBS)

        # This is a legal move because both are of the same suit.

        result = is_legal_move(hand, p1_card, p2_card)
        self.assertTrue(result)

        # p1's play
        p1_card = create_card(ACE, SUIT_CLUBS)
        # p2's play
        p2_card = create_card(VAL_10, SUIT_HEARTS)
        
        # This is not a legal move because the player has another card in the same suit but plays a different suit from p1.
        result = is_legal_move(hand, p1_card, p2_card)
        self.assertFalse(result)

        
        # p1's play
        p1_card = create_card(JACK, SUIT_DIAMONDS)
        # p2's play
        p2_card = create_card(VAL_9, SUIT_SPADES)
        
        # This is a legal move because the player does not have any cards in the same suit.
        result = is_legal_move(hand, p1_card, p2_card)
        self.assertTrue(result)

    def test_who_won(self):
        ## How this test is set up might depend how you implement your cards
        ## It can be okay to change it
        lead_card = create_card(ACE, SUIT_CLUBS) ## 'Ace', 'of', 'Clubs', 14)
        followed_card = create_card(VAL_9, SUIT_CLUBS) ##(9, 'of', 'Clubs', 9)
        trump = SUIT_HEARTS

        result = who_won(lead_card, followed_card, trump)
        self.assertTrue(result)

        clubs_9 = create_card(VAL_9, SUIT_CLUBS)
        diamonds_ace = create_card(ACE, SUIT_DIAMONDS)
        clubs_ace = create_card(ACE, SUIT_CLUBS)

        result = who_won( clubs_9, diamonds_ace, SUIT_DIAMONDS)
        self.assertFalse(result)

        result = who_won( clubs_9, diamonds_ace, SUIT_CLUBS)
        self.assertTrue(result)

        result = who_won( clubs_9, clubs_ace, SUIT_CLUBS)
        self.assertFalse(result)

    def test_swap_card_with_next_middle(self):
        hand = create_hand()
        card = create_card(JACK, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)
        card3 = create_card(KING, SUIT_HEARTS)
        card4 = create_card(KING, SUIT_CLUBS)
        card5 = create_card(KING, SUIT_SPADES)
        add_card_to_hand(hand, card)
        add_card_to_hand(hand, card2)
        add_card_to_hand(hand, card3)
        add_card_to_hand(hand, card4)
        add_card_to_hand(hand, card5)

        ## Confirm cards are in expected order
        self.assertEqual(card5, peek_card_at_index(hand, 0))
        self.assertEqual(card4, peek_card_at_index(hand, 1))
        self.assertEqual(card3, peek_card_at_index(hand, 2))
        self.assertEqual(card2, peek_card_at_index(hand, 3))
        self.assertEqual(card, peek_card_at_index(hand, 4))

        swap_card_with_next(hand, 1)

        ## Check for swap
        self.assertEqual(card5, peek_card_at_index(hand, 0))
        self.assertEqual(card3, peek_card_at_index(hand, 1))
        self.assertEqual(card4, peek_card_at_index(hand, 2))
        self.assertEqual(card2, peek_card_at_index(hand, 3))
        self.assertEqual(card, peek_card_at_index(hand, 4))

    def test_swap_card_with_next_beginning(self):
        hand = create_hand()
        card = create_card(JACK, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)
        card3 = create_card(KING, SUIT_HEARTS)
        card4 = create_card(KING, SUIT_CLUBS)
        card5 = create_card(KING, SUIT_SPADES)
        add_card_to_hand(hand, card)
        add_card_to_hand(hand, card2)
        add_card_to_hand(hand, card3)
        add_card_to_hand(hand, card4)
        add_card_to_hand(hand, card5)

        print_hand(hand)

        swap_card_with_next(hand, 0)

        print_hand(hand)

        self.assertEqual(card4, peek_card_at_index(hand, 0))
        self.assertEqual(card5, peek_card_at_index(hand, 1))
        self.assertEqual(card3, peek_card_at_index(hand, 2))
        self.assertEqual(card2, peek_card_at_index(hand, 3))
        self.assertEqual(card, peek_card_at_index(hand, 4))

    def test_swap_card_with_next_end(self):
        hand = create_hand()
        card = create_card(JACK, SUIT_HEARTS)
        card2 = create_card(QUEEN, SUIT_HEARTS)
        card3 = create_card(KING, SUIT_HEARTS)
        card4 = create_card(KING, SUIT_CLUBS)
        card5 = create_card(KING, SUIT_SPADES)
        add_card_to_hand(hand, card)
        add_card_to_hand(hand, card2)
        add_card_to_hand(hand, card3)
        add_card_to_hand(hand, card4)
        add_card_to_hand(hand, card5)

        swap_card_with_next(hand, 4)

        self.assertEqual(card5, peek_card_at_index(hand, 0))
        self.assertEqual(card4, peek_card_at_index(hand, 1))
        self.assertEqual(card3, peek_card_at_index(hand, 2))
        self.assertEqual(card2, peek_card_at_index(hand, 3))
        self.assertEqual(card, peek_card_at_index(hand, 4))

    def test_card_with_higher_rank(self):
        # Higher rank card should win
        ten_hearts = create_card(VAL_10, SUIT_HEARTS)
        nine_hearts = create_card(VAL_9, SUIT_HEARTS)
        self.assertTrue(is_this_card_bigger_than_that_card(ten_hearts, nine_hearts, SUIT_DIAMONDS))

    def test_card_with_equal_rank(self):
        # Cards with the same rank and suit should result in False
        ten_hearts = create_card(VAL_10, SUIT_HEARTS)
        ten_diamonds = create_card(VAL_10, SUIT_DIAMONDS)
        self.assertFalse(is_this_card_bigger_than_that_card(ten_hearts, ten_diamonds, SUIT_SPADES))

    def test_card_with_trump_suit_beating_non_trump(self):
        # Trump suit card should beat non-trump card
        ten_diamonds = create_card(VAL_10, SUIT_DIAMONDS)
        ace_hearts = create_card(ACE, SUIT_HEARTS)
        self.assertTrue(is_this_card_bigger_than_that_card(ten_diamonds, ace_hearts, SUIT_DIAMONDS))

    def test_card_with_non_trump_suit_losing_to_trump(self):
        # Non-trump suit card should lose to trump suit card
        ten_diamonds = create_card(VAL_10, SUIT_DIAMONDS)
        nine_hearts = create_card(VAL_9, SUIT_HEARTS)
        self.assertFalse(is_this_card_bigger_than_that_card(ten_diamonds, nine_hearts, SUIT_HEARTS))

    def test_cards_with_different_non_trump_suits(self):
        # When trump is not involved, comparison should be based on rank within the same suit
        jack_diamonds = create_card(JACK, SUIT_DIAMONDS)
        jack_clubs = create_card(JACK, SUIT_CLUBS)
        self.assertTrue(is_this_card_bigger_than_that_card(jack_clubs, jack_diamonds, SUIT_HEARTS))

    def test_card_with_trump_over_equal_rank_of_another_suit(self):
        # Trump card with the same rank should win over card of another suit
        jack_diamonds = create_card(JACK, SUIT_DIAMONDS)
        jack_hearts = create_card(JACK, SUIT_HEARTS)
        self.assertTrue(is_this_card_bigger_than_that_card(jack_diamonds, jack_hearts, SUIT_DIAMONDS))
        self.assertFalse(is_this_card_bigger_than_that_card(jack_hearts, jack_diamonds, SUIT_DIAMONDS))


    def test_sort_hand_full_hand_with_trump(self):
        ## Set up
        trump = SUIT_CLUBS
        hand = create_hand()
        jack_hearts = create_card(JACK, SUIT_HEARTS)
        queen_hearts = create_card(QUEEN, SUIT_HEARTS)
        king_hearts = create_card(KING, SUIT_HEARTS)
        trump_card4 = create_card(KING, SUIT_CLUBS)
        king_spades = create_card(KING, SUIT_SPADES)
        add_card_to_hand(hand, jack_hearts)
        add_card_to_hand(hand, queen_hearts)
        add_card_to_hand(hand, king_hearts)
        add_card_to_hand(hand, trump_card4)
        add_card_to_hand(hand, king_spades)

        sort_hand(hand, trump)

        print_hand(hand)

        self.assertEqual(trump_card4, hand[HAND_FIRST_CARD_KEY][CARD_NODE_PAYLOAD_KEY])
        self.assertEqual(king_hearts, peek_card_at_index(hand, 1))
        self.assertEqual(queen_hearts, peek_card_at_index(hand, 2))
        self.assertEqual(jack_hearts, peek_card_at_index(hand, 3))
        self.assertEqual(king_spades, peek_card_at_index(hand, 4))

class ConservationTestCase(unittest.TestCase):
    """
    Cards must never be lost or duplicated as they move between the deck and the
    hands, and a hand must stay a valid doubly linked list while it changes.
    See hand_invariants.py.
    """

    def build_hand(self, cards):
        hand = create_hand()
        for card in reversed(cards):  # add_card_to_hand puts each card at the front
            add_card_to_hand(hand, card)
        return hand

    def check_state(self, original, deck, hands, context=''):
        """Every hand is valid, and deck + hands hold exactly the original cards."""
        try:
            for hand in hands:
                assert_hand_valid(hand)
            assert_cards_conserved(original, deck, *hands)
        except AssertionError as error:
            self.fail('%s: %s' % (context, error))

    def test_deal_alternates_starting_with_player_1_from_the_top_of_the_deck(self):
        deck = create_deck()
        original = deck[:]
        hand1, hand2 = create_hand(), create_hand()

        deal(deck, hand1, hand2)

        # The top of the deck is the END of the list: Player 1 gets the 1st, 3rd, 5th... card.
        self.assertEqual(sorted(original[-1:-11:-2]), sorted(hand_cards(hand1)))
        self.assertEqual(sorted(original[-2:-11:-2]), sorted(hand_cards(hand2)))
        self.assertEqual(original[:-10], deck)

    def test_deal_never_loses_or_duplicates_a_card(self):
        for seed in range(10):
            random.seed(seed)
            deck = create_deck()
            shuffle(deck)
            original = deck[:]
            hand1, hand2 = create_hand(), create_hand()

            deal(deck, hand1, hand2)

            self.check_state(original, deck, [hand1, hand2], 'seed %d' % seed)

    def test_return_hand_to_deck_gives_back_every_card(self):
        deck = create_deck()
        original = deck[:]
        hand1, hand2 = create_hand(), create_hand()
        deal(deck, hand1, hand2)

        return_hand_to_deck(hand1, deck)
        self.check_state(original, deck, [hand1, hand2], 'after returning hand 1')
        self.assertIsNone(hand1[HAND_FIRST_CARD_KEY])
        self.assertEqual(0, hand1[HAND_NUM_CARDS_KEY])

        return_hand_to_deck(hand2, deck)
        self.check_state(original, deck, [hand1, hand2], 'after returning hand 2')
        self.assertEqual(NUM_CARDS_IN_DECK, len(deck))
        self.assertTrue(is_hand_empty(hand2))

    def test_return_empty_hand_to_deck_changes_nothing(self):
        deck = create_deck()
        original = deck[:]
        hand = create_hand()

        return_hand_to_deck(hand, deck)

        self.check_state(original, deck, [hand])
        self.assertEqual(original, deck)

    def test_swap_card_with_next_at_every_index(self):
        for index in range(5):
            cards = create_deck()[:5]
            hand = self.build_hand(cards)
            expected = cards[:]
            if index < 4:  # swapping the last card with "the next one" does nothing
                expected[index], expected[index + 1] = expected[index + 1], expected[index]

            swap_card_with_next(hand, index)

            self.check_state(cards, [], [hand], 'index %d' % index)
            self.assertEqual(expected, hand_cards(hand), 'index %d' % index)

    def test_swap_card_with_next_raises_for_an_index_past_the_end(self):
        hand = self.build_hand(create_deck()[:5])
        with self.assertRaises(IndexError):
            swap_card_with_next(hand, 5)

    def test_sort_hand_orders_the_cards_and_loses_none(self):
        all_cards = create_deck()
        for trump in SUITS:
            for seed in range(25):
                rng = random.Random(seed)
                for size in (0, 1, 2, 3, 5, 8):
                    cards = rng.sample(all_cards, size)
                    hand = self.build_hand(cards)
                    context = 'trump %s, seed %d, %d cards' % (trump, seed, size)

                    sort_hand(hand, trump)

                    self.check_state(cards, [], [hand], context)
                    # Trump first, then the other suits alphabetically; highest value first.
                    expected = sorted(cards, key=lambda c: (c[CARD_SUIT_INDEX] != trump,
                                                            c[CARD_SUIT_INDEX],
                                                            -c[CARD_VALUE_INDEX]))
                    self.assertEqual(expected, hand_cards(hand), context)

    def test_playing_a_whole_round_never_loses_or_duplicates_a_card(self):
        for seed in range(25):
            random.seed(seed)
            deck = create_deck()
            original = deck[:]
            shuffle(deck)
            hand1, hand2 = create_hand(), create_hand()
            deal(deck, hand1, hand2)
            trump = peek_card(deck)[CARD_SUIT_INDEX]

            for trick in range(NUM_CARDS_IN_HAND):
                context = 'seed %d, trick %d' % (seed, trick)
                lead = remove_card_at_index(hand1, 0)

                # Player 2 plays the first legal card in their hand.
                follow_index = None
                for i in range(hand2[HAND_NUM_CARDS_KEY]):
                    if is_legal_move(hand2, lead, peek_card_at_index(hand2, i)):
                        follow_index = i
                        break
                self.assertIsNotNone(follow_index, context + ': is_legal_move says no card can be played')
                followed = remove_card_at_index(hand2, follow_index)

                self.assertIn(who_won(lead, followed, trump), (True, False), context)

                # Like the real game: the two played cards go back on the deck.
                push_card_to_deck(deck, lead)
                push_card_to_deck(deck, followed)
                self.check_state(original, deck, [hand1, hand2], context)
                self.assertEqual(NUM_CARDS_IN_HAND - trick - 1, hand1[HAND_NUM_CARDS_KEY], context)
                self.assertEqual(NUM_CARDS_IN_HAND - trick - 1, hand2[HAND_NUM_CARDS_KEY], context)

            self.assertTrue(is_hand_empty(hand1))
            self.assertTrue(is_hand_empty(hand2))
            self.assertEqual(NUM_CARDS_IN_DECK, len(deck))


if __name__ == '__main__':
    unittest.main()
