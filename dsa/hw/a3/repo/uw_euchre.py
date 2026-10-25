import sys
from game_play import *

"""
This file is provided to play UW-Euchre with the implemented game_structures and 
game_play files. 

It *should* run properly if all the functions are implemented correctly. 
However, this file is NOT part of the assignment. If you need to tweak this file 
to make it work better for yourself, feel free. However, depending what you change, 
it may cover up a wrong implementation. 

"""

PRINT_OUT_DECK = False
PRINT_P1_HAND = False


def print_play(led_card, followed_card):
    print('Player 1 led with {} and Player 2 followed with {}'.format(led_card, followed_card))


def print_hand_for_human_player(hand):
    print('====')
    cur_card_node = hand[HAND_FIRST_CARD_KEY]
    index = 0
    while cur_card_node is not None:
        card = cur_card_node[CARD_NODE_PAYLOAD_KEY]
        print('{}: {}'.format(str(index), card[CARD_NAME_INDEX]))
        # print(f'{bcolors.WARNING}9\u2660{bcolors.ENDC}')
        cur_card_node = cur_card_node[CARD_NODE_NEXT_KEY]
        index += 1
    print('====')


def print_trump(suit):
    print('\n**************************')
    print('**** Trump is {} *****'.format(suit))
    print('**************************\n')


def print_score(score1, score2):
    print('Player 1: {}\tPlayer 2: {}'.format(score1, score2))


# Returns 1 or 2, based on who won.
def play_round(game_deck):
    shuffle(game_deck)
    if PRINT_OUT_DECK:
        print_deck(game_deck)
    # Deal the hand
    p1hand = create_hand()
    p2hand = create_hand()

    deal(game_deck, p1hand, p2hand)

    if PRINT_P1_HAND:
        print('Player 1: ')
        print_hand(p1hand)

    # For each round:

    # Determine trump Suit
    trump = peek_card(game_deck)[CARD_SUIT_INDEX]
    print_trump(trump)

    # Start playing.
    num_tricks = 0
    p1score = 0
    p2score = 0

    print('Starting the round...')

    while num_tricks < NUM_CARDS_IN_HAND:
        print('---------------------\n')

        led_card = take_player1_turn(p1hand, trump)
        followed_card = take_player2_turn(p2hand, trump)

        print_play(led_card, followed_card)

        if is_legal_move(p2hand, led_card, followed_card):
            # figure out who won
            if who_won(led_card, followed_card, trump):
                print('Player 1 took the trick. \n')
                # P1 won
                p1score += 1

            else:
                print('Player 2 took the trick. \n')
                # P2 won
                p2score += 1

            print_score(p1score, p2score)

        else:
            # It was not a legal move; player 2 loses!
            print('\nPlayer 2 did not make a legal move!! ')
            print('The round is over.')
            print('Player 1 wins by default. \n')

            # The round ends here: put every card back (so none are 'lost')
            # and give the round to Player 1.
            push_card_to_deck(game_deck, led_card)
            push_card_to_deck(game_deck, followed_card)
            return_hand_to_deck(p1hand, game_deck)
            return_hand_to_deck(p2hand, game_deck)
            return 1

        # Put the cards back in the deck
        # so we don't 'lose' them
        push_card_to_deck(game_deck, led_card)
        push_card_to_deck(game_deck, followed_card)

        num_tricks += 1

    print('\nPlayer {} won this round with {} tricks!'.format(
          1 if (p1score > p2score) else 2,
          p1score if (p1score > p2score) else p2score))

    ## There probably shouldn't be any cards left in the hands at this point,
    ## but let's make sure they get returned anyway.
    return_hand_to_deck(p1hand, game_deck)
    return_hand_to_deck(p2hand, game_deck)

    return 1 if (p1score > p2score) else 2


def play_game(deck):
    num_rounds = 5
    player1score, player2score = 0, 0

    for i in range(0, num_rounds):
        print('\n\n===========================')
        print('Round #{}'.format(i + 1))
        print('===========================\n')

        which_player_won = play_round(deck)

        if which_player_won == 1:
            player1score += 1
        else:
            player2score += 1

        print('Game Score so far:')
        print_score(player1score, player2score)
        print('===========================\n')

        print('When you\'re ready, press <enter> to go to the next round. \n')
        which_one = input()

    print('Player {} won the game!\n'.format(
          1 if (player1score > player2score) else 2))

    print_score(player1score, player2score)

    return 1 if (player1score > player2score) else 2


def main():
    print('Welcome to UW-Euchre!\n')
    print('When you\'re ready to play, press <enter>')
    user_input = input()

    print('Sweet! ')
    game_deck = create_deck()

    if PRINT_OUT_DECK:
        print_deck(game_deck)

    print('Would you like to play a [R]ound or a [G]ame?')
    user_input = input()

    if user_input == 'r' or user_input == 'R':
        play_round(game_deck)
    elif user_input == 'g' or user_input == 'G':
        play_game(game_deck)
    else:
        print('Quitting the game. ')

    return 0


if __name__ == '__main__':
    sys.exit(main())
