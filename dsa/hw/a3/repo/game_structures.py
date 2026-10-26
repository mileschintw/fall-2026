

#  Copyright (c) 2025 by Adrienne Slaughter for University of Washington.


## These constants have been defined as a starting point.

NUM_CARDS_IN_HAND = 5
NUM_CARDS_IN_DECK = 24

SUIT_CLUBS = 'Clubs'
SUIT_SPADES = 'Spades'
SUIT_HEARTS = 'Hearts'
SUIT_DIAMONDS = 'Diamonds'

JACK = 'Jack'
QUEEN = 'Queen'
KING = 'King'
ACE = 'Ace'
VAL_9 = '9'
VAL_10 = '10'

SUITS = [SUIT_CLUBS, SUIT_SPADES, SUIT_HEARTS, SUIT_DIAMONDS]
FACES = [JACK, QUEEN, KING, ACE]
NUMBERED = [VAL_9, VAL_10]
COLOR_BLACK = 'BLACK'
COLOR_RED = 'RED'

CARD_TO_VALUE_MAP = {
	VAL_9: 9,
	VAL_10: 10,
	JACK: 11,
	QUEEN: 12,
	KING: 13,
	ACE: 14
}

CARD_NODE_PREV_KEY = 'prev'
CARD_NODE_NEXT_KEY = 'next'
CARD_NODE_PAYLOAD_KEY = 'payload'
HAND_NUM_CARDS_KEY = 'num_cards_in_hand'
HAND_FIRST_CARD_KEY = 'first_card'

CARD_NAME_INDEX = 0
CARD_SUIT_INDEX = 1
CARD_COLOR_INDEX = 2
CARD_VALUE_INDEX = 3


## A Card is a tuple of (name, suit, color, value)
## A Deck is a Python list structured as a stack
## A Card Node is a dict of {next, prev, payload}
## A Hand is a linked list, represented by a dict of {first_card, num_cards_in_hand}

# ----------------------------------------
#  Deck functions
# ----------------------------------------
#  Assume that the value of cards are:
#  Nine=9; Ten=10; Jack=11; and so on, up to Ace=14.
# ----------------------------------------
def create_card(card, suit):
	"""
	Generate a card with its details including name, suit, color, and value.

	This function combines the given card face and suit to create a full card
	name. Additionally, it assigns a corresponding color based on the suit and
	retrieves the card's value using a predefined mapping.

	Args:
	    card: The face of the card (e.g., '9', '10', 'Jack', 'Queen', 'King', 'Ace').
	    suit: The suit of the card (e.g., 'Hearts', 'Diamonds', 'Clubs', 'Spades').

	Returns:
	    A tuple containing:
	        - The full card name (str).
	        - The card's suit (str).
	        - The color of the card (str).
	        - The numerical value of the card (int).
	"""
	card_name = '{face} of {suit}'.format(face = card, suit = suit)
	card_color = COLOR_RED if suit in [SUIT_HEARTS, SUIT_DIAMONDS] else COLOR_BLACK
	return (card_name, suit, card_color, CARD_TO_VALUE_MAP[card])

def create_deck():
	"""
	Creates and returns a complete deck of cards.

	This function creates a deck of playing cards for UW-Euchre by iterating over all
	relevant suits and ranks (faces and numbered cards) to generate individual cards.
	The resulting deck contains all possible combinations of suits and ranks.

	Returns
	-------
	list
	    A list of cards, where each card is a combination of a suit and a rank.
	"""
	deck = []
	for suit in SUITS:
		for card in FACES + NUMBERED:
			deck.append(create_card(card, suit))
	return deck

def push_card_to_deck(deck, card):
	"""
	Adds a given card to the deck and returns the updated deck.

	This function modifies the provided deck by appending the given card
	to it. It then returns the updated deck for further use. The card
	is expected to be in the format that is compatible with the deck
	structure.

	Parameters:
	deck : list
	    The deck of cards to which the new card will be added.
	card
	    The card to add to the deck.

	Returns:
	list
	    The updated deck with the new card added.
	"""
	deck.append(card)
	return deck

def peek_card(deck):
	"""
	Fetches the top card from the deck without removing it.

	This function accesses the last element of the provided list representation
	of a deck of cards. It does not modify the input list but only retrieves
	the card positioned at the top (end of the list). Designed to work with lists
	that represent a deck where each element corresponds to a card.

	Parameters:
	deck : list
	    A list representing the deck of cards. The last element of the list
	    corresponds to the topmost card in the deck.

	Returns:
	Any
	    The topmost card from the deck.
	"""
	return deck[-1]

def pop_card(deck):
	"""
	Removes and returns the "top" card from the given deck.

	This function operates on a list representing a deck of cards. It removes the
	last card in the list and returns it to the caller. The deck should be a
	sequence of items where the removal of an item does not disrupt the intended
	ordering or structure.

	Parameters:
	deck: list
	    A list representing the deck of cards. The function will modify this list
	    in place by removing the last element.

	Returns:
	card
	    The last card from the deck that was removed. The type of the returned card
	    will match the elements present in the input list.
	"""
	return deck.pop()

def is_deck_empty(deck):
	"""
	Checks whether the provided deck is empty.

	This function accepts a list representing a deck of cards and checks if it
	contains any elements. It helps to determine if all cards have been utilized
	from a deck.

	Args:
	    deck (list): A list containing the deck of cards to check.

	Returns:
	    bool: True if the deck is empty, False otherwise.
	"""
	return not deck

## Prints the provided deck
## Do a little more than just calling "print()"-- make it look nice!
def print_deck(deck):
	"""
	Prints the elements of the given deck in a user-friendly format.

	This function receives a list of elements representing a deck of cards
	and prints each element sequentially. It does not return
	any value, modifying nothing in the input deck. Primarily intended
	for display purposes.

	Arguments:
	    deck (list): A list containing playing cards to be printed

	Returns:
	    None
	"""
	print(f"{'#':>3}  {'Name':<20} {'Suit':<10} {'Color':<7} {'Value':>5}")
	print("-" * 41)

	for i, (name, suit, color, value) in enumerate(deck, start=1):
			print(f"{i:>3}  {name:<20} {suit:<10} {color:<7} {value:>5}")

#----------------------------------------
# Hand functions
#----------------------------------------

## A Hand is a linked list, so we define CardNodes before
## defining the Hand

def create_card_node(card):
	"""
	Creates a doubly linked list node with the given card as a payload.

	The function takes a card object and encapsulates it within a
	node structure. The node contains the payload and pointers to
	the next and previous nodes in a doubly linked list.

	Args:
	    card: The payload to be stored in the node.

	Returns:
	    A dictionary containing the following keys:
	    - 'payload': The card data passed to the function.
	    - 'next': None, representing the pointer to the next node.
	    - 'prev': None, representing the pointer to the previous node.
	"""
	return {CARD_NODE_PAYLOAD_KEY: card,
			CARD_NODE_NEXT_KEY: None,
			CARD_NODE_PREV_KEY: None}

def create_hand():
	"""
	Creates an initial hand representation for a card game.

	Summary:
	This function returns a dictionary that represents a player's initial
	hand in a card game. The hand contains two fields: the 'first_card' field,
	which starts as None, and the 'num_cards_in_hand' field, which begins at
	0. The initial hand does not contain any cards.

	Returns:
	    dict: A dictionary with the keys 'first_card' and 'num_cards_in_hand'
	    representing the player's initial hand.
	"""
	return {HAND_FIRST_CARD_KEY: None,
			HAND_NUM_CARDS_KEY: 0}

def add_card_to_hand(hand, card):
	"""
	Add a card to the front (head) of the hand.

	The hand is a doubly linked list stored in a dict (see create_hand). Wrap the card
	in a new card node (create_card_node) and insert that node at the head of the list,
	so that afterwards:
	    * the new node is the hand's first card (HAND_FIRST_CARD_KEY) and its 'prev' is None
	    * the new node's 'next' is the old first node (None if the hand was empty)
	    * the old first node's 'prev' is the new node
	    * the hand's card count (HAND_NUM_CARDS_KEY) has gone up by one

	Args:
	    hand (dict): The hand (linked list) to add to.
	    card: The card to add (usually a card tuple); it is stored as the node's payload.

	Returns:
	    None: The hand is modified in place.
	"""
	curr_head = hand[HAND_FIRST_CARD_KEY]
	new_head = create_card_node(card)
	new_head[CARD_NODE_NEXT_KEY] = curr_head
	if curr_head:
		curr_head[CARD_NODE_PREV_KEY] = new_head
	hand[HAND_NUM_CARDS_KEY] += 1
	hand[HAND_FIRST_CARD_KEY] = new_head

def find_node_for_card(hand, card):
	curr_node = hand[HAND_FIRST_CARD_KEY]
	while curr_node:
		if curr_node[CARD_NODE_PAYLOAD_KEY] == card:
			return curr_node
		curr_node = curr_node[CARD_NODE_NEXT_KEY]
	return None

def find_node_at_index(hand, index):
	if index >= hand[HAND_NUM_CARDS_KEY] or index < 0:
		return None

	curr_node = hand[HAND_FIRST_CARD_KEY]
	for _ in range(index):
		curr_node = curr_node[CARD_NODE_NEXT_KEY]
	return curr_node

def unlink_node(hand, node):
	prev_node = node[CARD_NODE_PREV_KEY]
	next_node = node[CARD_NODE_NEXT_KEY]
	if prev_node:
		prev_node[CARD_NODE_NEXT_KEY] = next_node
	else:
		hand[HAND_FIRST_CARD_KEY] = next_node
	if next_node:
		next_node[CARD_NODE_PREV_KEY] = prev_node
	hand[HAND_NUM_CARDS_KEY] -= 1

def remove_card_from_hand(hand, card):
	"""
	Remove the first card in the hand that equals the given card.

	Search from the head of the hand. If a match is found, unlink its node (fixing the
	neighbors' 'next'/'prev' links, and the hand's first card if the head was removed)
	and decrease the hand's card count. If there is no match, the hand is unchanged.

	Args:
	    hand (dict): The hand (linked list) to remove from.
	    card: The card to remove.

	Returns:
	    The card that was removed (the payload, not the card node), or None if the
	    card was not found.
	"""
	node = find_node_for_card(hand, card)
	if node is None:
		return None
	unlink_node(hand, node)
	return node[CARD_NODE_PAYLOAD_KEY]

def remove_card_at_index(hand, index):
	"""
	Remove the card at the given position in the hand and return it.

	Index 0 is the first card (the head). Unlink the node, keeping every link and the
	hand's card count correct. If the index is out of range, the hand is unchanged.

	Args:
	    hand (dict): The hand (linked list) to remove from.
	    index (int): The zero-based position of the card to remove.

	Returns:
	    The card that was removed (the payload, not the card node), or None if the
	    index is out of range.
	"""
	node = find_node_at_index(hand, index)
	if node is None:
		return None
	unlink_node(hand, node)
	return node[CARD_NODE_PAYLOAD_KEY]

def peek_card_at_index(hand, index):
	"""
	Look at the card at the given position in the hand without removing it.

	Index 0 is the first card (the head). The hand is not modified.

	Args:
	    hand (dict): The hand (linked list) to look in.
	    index (int): The zero-based position of the card to look at.

	Returns:
	    The card at that position (the payload, not the card node), or None if the
	    index is out of range (too big, or negative).
	"""
	node = find_node_at_index(hand, index)
	if node is None:
		return None
	return node[CARD_NODE_PAYLOAD_KEY]

def is_card_in_hand(hand, card):
	"""
	Determines whether a specific card is in the hand.

	Walk the hand (a linked list) from the head, comparing each node's payload to the card.

	Args:
	    hand (dict): The hand (linked list) to search.
	    card: The card to look for.

	Returns:
	    bool: True if the card is in the hand, False otherwise.
	"""
	return find_node_for_card(hand, card) is not None


def is_hand_empty(hand):
	"""
	Determines if the provided card hand is empty.

	This function checks whether the 'first_card' key in the given dictionary
	representing a card hand is `None`. Alternatively, it could be used to confirm
	if the number of cards in the hand is zero.

	Parameters:
	    hand (dict): A dictionary representing a card hand where 'first_card' is a
	        key storing the first card in the hand or None if the hand is empty.

	Returns:
	    bool: True if the hand is empty, i.e., 'first_card' is None; otherwise,
	    returns False.
	"""
	return hand[HAND_FIRST_CARD_KEY] is None

def print_card(card):
	"""
	Prints a card's full name, for example "King of Hearts".

	Args:
	    card (tuple): A card tuple (name, suit, color, value). The full name is at
	        CARD_NAME_INDEX.

	Returns:
	    None
	"""
	print(card[CARD_NAME_INDEX])

def print_hand(hand):
	"""
	Prints the hand of cards in a specified format.

	This function iterates through a linked list-like structure of cards
	and prints each card's details using the `print_card` function.

	Parameters:
	    hand (dict): A dictionary representing the hand of cards.
	    It contains the key 'first_card', which points to the first
	    card node in the linked structure. Each card node is a
	    dictionary with keys 'payload' and 'next'. The key 'payload'
	    contains the card data, and the key 'next' points to the next
	    card node in the sequence.

	Raises:
	    None
	"""
	print('====')
	cur_card_node = hand[HAND_FIRST_CARD_KEY]
	while cur_card_node is not None:
		print_card(cur_card_node[CARD_NODE_PAYLOAD_KEY])
		cur_card_node = cur_card_node[CARD_NODE_NEXT_KEY]
	print('====')

