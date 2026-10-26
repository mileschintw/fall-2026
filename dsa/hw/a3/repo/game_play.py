from game_structures import *
import random

def shuffle(deck):
	random.shuffle(deck)

def deal(deck, p1_hand, p2_hand):
	"""
	Deals cards from the deck to two players, 5 cards to each player
	Cards are dealt one at a time from the top of the deck (the end of the list),
	alternating between players and starting with p1_hand. The function modifies the player hands in place.

	Args:
	    deck (Deck list): List representing the deck of cards to be dealt. Each
	        element corresponds to a card.
	    p1_hand (Hand Linked List): The first player's hand. Cards
	        dealt to player 1 are added to this list.
	    p2_hand (Hand Linked List): The second player's hand. Cards
	        dealt to player 2 are added to this list.
	"""
	for _ in range(5):
		card = pop_card(deck)
		add_card_to_hand(p1_hand, card)
		card = pop_card(deck)
		add_card_to_hand(p2_hand, card)


def hand_has_suit(hand, suit):
	"""
	Determines if the given hand contains a card of the specified suit.

	Walk the hand (a linked list) and check each card's suit (CARD_SUIT_INDEX).

	Args:
	    hand (dict): The hand (linked list) to search.
	    suit (str): The suit to look for, e.g. SUIT_HEARTS.

	Returns:
	    bool: True if any card in the hand has the given suit, otherwise False.
	"""
	if is_hand_empty(hand):
		return False

	curr_node = hand[HAND_FIRST_CARD_KEY]
	while curr_node:
		card = curr_node[CARD_NODE_PAYLOAD_KEY]
		if card[CARD_SUIT_INDEX] == suit:
			return True
		curr_node = curr_node[CARD_NODE_NEXT_KEY]

	return False

def is_legal_move(hand, lead_card, played_card):
	"""
	Determines whether the played card is a legal move for the player who followed.

	The follower must follow suit:
	    * If the hand has a card of the same suit as the lead card, the played card
	      must be of that suit.
	    * If the hand has no card of the lead card's suit, any card may be played.

	The hand may or may not still contain the played card; the answer is the same either way.

	Args:
	    hand (dict): The follower's hand (linked list).
	    lead_card (tuple): The card played first in the trick.
	    played_card (tuple): The card the follower is trying to play.

	Returns:
	    bool: True if the played card is a legal move, False otherwise.
	"""
	lead_card_suit = lead_card[CARD_SUIT_INDEX]
	played_card_suit = played_card[CARD_SUIT_INDEX]
	if played_card_suit == lead_card_suit:
		return True
	if not hand_has_suit(hand, lead_card_suit):
		return True

	return False

## Returns True if the LEAD card wins the trick, and False if the FOLLOWED card wins.
##   * Same suit (this includes trump vs. trump): the higher value wins.
##   * Different suits: the followed card wins only if it is trump; otherwise the lead card wins.
def who_won(lead_card, followed_card, trump):
	"""
	Determines who wins a trick: the player who led, or the player who followed.

	Assumes the followed card is a legal move (that is, if the suits are different, the
	follower has no card of the lead suit).

	Args:
	    lead_card (tuple): The card played first in the trick.
	    followed_card (tuple): The card played second in the trick.
	    trump (str): The trump suit chosen for the round, e.g. SUIT_HEARTS.

	Returns:
	    bool: True if the lead card wins the trick, False if the followed card wins.
	"""
	if followed_card[CARD_SUIT_INDEX] == trump:
		return False
	if followed_card[CARD_SUIT_INDEX] == lead_card[CARD_SUIT_INDEX] and followed_card[CARD_VALUE_INDEX] > lead_card[CARD_VALUE_INDEX]:
		return False

	return True


# Given the player1 hand, play a card.
# Player 1 is always the computer.
# This function should choose a card from the hand,
# remove it from the hand, print out a message
# saying what card was played, and return the played card.
# I recommend beginning with choosing the card in a very simple
# manner: just remove/return the first card in the hand, regardless
# if it's a "good" card or not.
def take_player1_turn(hand, trump):
	card = remove_card_at_index(hand, 0)
	print('Player 1 plays {}'.format(card[CARD_NAME_INDEX]))
	return card

# Given the player2 hand, play a card.
# Player 2 is always a human.
# This function should prompt the user to choose a card to play.
# It probably should print out the cards that are available to play.
# Once the human player chooses,
# remove it from the hand, print a message
# saying what card was played, and return the played card.
# This function does not have to enforce that a valid card is chosen.
def take_player2_turn(hand, trump):
	print('Your hand:')
	curr_node = hand[HAND_FIRST_CARD_KEY]
	index = 0
	while curr_node is not None:
		print('{}: {}'.format(index, curr_node[CARD_NODE_PAYLOAD_KEY][CARD_NAME_INDEX]))
		curr_node = curr_node[CARD_NODE_NEXT_KEY]
		index += 1

	card = None
	while card is None:
		choice = input('Choose a card to play (0-{}): '.format(index - 1))
		try:
			card = remove_card_at_index(hand, int(choice))
		except ValueError:
			card = None
		if card is None:
			print('Invalid choice, try again.')

	print('Player 2 plays {}'.format(card[CARD_NAME_INDEX]))
	return card

def return_hand_to_deck(hand, deck):
	"""
	Move every card from the hand back onto the deck.

	Each card is removed from the hand and pushed onto the deck. Afterwards the hand is
	empty (is_hand_empty() is True) and the deck has those cards back.

	Args:
	    hand (dict): The hand (linked list) to empty.
	    deck (list): The deck to put the cards on.
	"""
	while not is_hand_empty(hand):
		card = remove_card_at_index(hand, 0)
		push_card_to_deck(deck, card)


def swap_card_with_next(hand, index):
	"""
	Swap the card at the given index with the card right after it.

	Afterwards the two cards have traded places; every next/prev link and the hand's
	first card (if the swap involves index 0) must still be correct. If the index is the
	last card in the hand (nothing follows it), nothing happens.

	Args:
	    hand (dict): The hand (linked list).
	    index (int): The zero-based index of the first of the two cards to swap.

	Raises:
	    IndexError: If the index is greater than the last valid index of the hand.
	"""

	curr_node = find_node_at_index(hand, index)
	if curr_node is None:
		raise IndexError

	next_node = curr_node[CARD_NODE_NEXT_KEY]
	prev_node = curr_node[CARD_NODE_PREV_KEY]

	if next_node is None:
		return
	next_next_node = next_node[CARD_NODE_NEXT_KEY]

	# move next in front of curr
	next_node[CARD_NODE_NEXT_KEY] = curr_node
	next_node[CARD_NODE_PREV_KEY] = prev_node

	# update curr node
	curr_node[CARD_NODE_NEXT_KEY] = next_next_node
	curr_node[CARD_NODE_PREV_KEY] = next_node

	if next_next_node is not None:
		next_next_node[CARD_NODE_PREV_KEY] = curr_node

	if prev_node is None:
		hand[HAND_FIRST_CARD_KEY] = next_node
	else:
		prev_node[CARD_NODE_NEXT_KEY] = next_node

def is_this_card_bigger_than_that_card(this_card, that_card, trump):
	"""
	Determines whether this_card is bigger than that_card, given the trump suit.

	Rules, in order:
	    1. Same suit: the higher value is bigger (equal cards: False).
	    2. Different suits and one of them is trump: the trump card is bigger.
	    3. Different suits and neither is trump: the suit that comes FIRST alphabetically
	       is bigger, so Clubs > Diamonds > Hearts > Spades.

	This is similar to who_won(), but it must give an answer for any two cards.

	Args:
	    this_card (tuple): The card being compared.
	    that_card (tuple): The card to compare against.
	    trump (str): The trump suit, e.g. SUIT_HEARTS.

	Returns:
	    bool: True if this_card is bigger than that_card, False otherwise.
	"""
	this_suit = this_card[CARD_SUIT_INDEX]
	that_suit = that_card[CARD_SUIT_INDEX]
	if this_suit == that_suit:
		return this_card[CARD_VALUE_INDEX] > that_card[CARD_VALUE_INDEX]
	if this_suit == trump:
		return True
	if that_suit == trump:
		return False
	return this_suit < that_suit


def sort_hand(hand, trump):
	"""
	Sort a hand (linked list) in place, from the biggest card to the smallest.

	The order is the one defined by is_this_card_bigger_than_that_card(): trump cards
	first (highest value to lowest), then the other suits in alphabetical order (Clubs,
	Diamonds, Hearts, Spades), each from highest value to lowest.

	For full credit, write your own sort. (Hint: swap_card_with_next() makes a bubble
	sort straightforward.) The hand's card count and all next/prev links must stay correct.

	Args:
	    hand (dict): The hand (linked list) to sort.
	    trump (str): The trump suit, e.g. SUIT_HEARTS.

	Returns:
	    Nothing; the provided hand is modified in place.
	"""

	n = hand[HAND_NUM_CARDS_KEY]
	for i in range(n):
		curr_node = hand[HAND_FIRST_CARD_KEY]
		for j in range(0, n - i - 1):
			next_node = curr_node[CARD_NODE_NEXT_KEY]
			if is_this_card_bigger_than_that_card(next_node[CARD_NODE_PAYLOAD_KEY], curr_node[CARD_NODE_PAYLOAD_KEY], trump):
				swap_card_with_next(hand, j)
			else:
				curr_node = curr_node[CARD_NODE_NEXT_KEY]