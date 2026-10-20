# A3: Stacks, Queues and Testing

> 來源：Canvas assignment 11814801（https://canvas.uw.edu/courses/1917417/assignments/11814801），抓取 2026-10-20 02:11 PDT。
> 這個檔案由 `scripts/assignment_specs.py` 產生，內容是原文，每次來源有變動就整份重寫，不要手改。整理過的版本在 README.md。

- 截止（Canvas `due_at`）：2026-10-25 (Sun) 11:59 PM PDT

## Canvas 作業說明

（空白）

## Starter repo README（uw-python-fall2026/assignment-3-mileschintw，blob a169e62）

# Assignment 3: UW-Euchre

## Objectives

* Implement applied data structures (a stack and a doubly linked list)
* Use those data structures to build something that works: a card game
* Implement your first sort function
* Become familiar with a Python testing framework (`unittest`)
* Learn to check your own data structure for correctness, not just "it seems to work"

# Overview

In this assignment, you are going to implement some key components to a card game.
The card game is a version of Euchre (pronounced "U-ker"). Euchre is a 4-player game
that is modified to be a 2-player for this assignment.
To get a sense of the game, you can play the traditional version at
https://cardgames.io/euchre/.

There are two parts to this assignment:

* **Part 1: Data structures** (`game_structures.py`). You implement the deck (a stack) and the
  hand (a doubly linked list), plus the cards and nodes that go in them.
* **Part 2: Game play** (`game_play.py`). You implement the game functions (shuffle, deal, legal
  moves, who won a trick, sort a hand, and so on) using the data structures from Part 1.

Do Part 1 first. Part 2 builds on it, so a bug in a Part 1 function will show up as a mysterious
failure in Part 2.

We'll use the `unittest` testing module. We've provided tests to get started, but it will
very likely help you to write some tests of your own too.

# Details

The rules of UW-Euchre are below. UW-Euchre is inspired by Euchre, but
some of the play details are simplified to make it easier to understand and implement.

## Basic Rules Of UW-Euchre

* UW-Euchre is a 2-player game.
* The player with the most points after 5 rounds wins.
* A player wins a round by "collecting the most tricks".
* A **_round_** consists of each player being dealt 5 cards, choosing a trump
(a suit designated as the highest/most powerful for this round),
and then each player takes turns playing cards for a "trick".

A player wins a trick by playing the highest value card in a round.

**There are a couple of rules that must be followed for playing a card:**
the first player can play any card, but the second player must "follow suit".
If the second player has a card of the same suit, they must play it (but they can choose
which card they want to play). Further, a card of the trump suit is higher
than all other cards in the deck. For example, if Spades is trump, a 9 of Spades is
higher than an Ace of Diamonds.

Within a suit, including trump, the face value of the
card is highest, with Aces being the highest value card.

In this version of the game, Player 1 (the computer) ALWAYS goes first and
leads the first card. This makes the game less fun, but more simple to implement.

The deck used for UW-Euchre is a subset of the traditional 52-card deck.
It includes the Ace, King, Queen, Jack, 10 & 9 of all four suits (Spades, Diamonds,
Hearts, and Clubs).

## Provided Starter Code

* `game_structures.py` contains the data structures you implement first (**Part 1**): the deck
  and the hand (a doubly linked list).
* `game_structures_test.py` provides tests to check that your data structures work properly.
* `game_play.py` specifies the game functions you implement next (**Part 2**), using those
  data structures.
* `game_play_test.py` provides tests to check that your game functions work properly.
* `hand_invariants.py` has helpers that check that a hand is a correct linked list
  (`assert_hand_valid`) and that no cards were lost or duplicated (`assert_cards_conserved`).
  The tests use them, and you can use them in your own tests. See "Checking your own work" below.
* `uw_euchre.py` plays the game in your terminal once everything is implemented.
  You do not need to change it.

**Please do not edit** the provided test files or `hand_invariants.py`. If you want to write
tests of your own (a good idea!), put them in a new file, for example `my_tests.py`.

## Running

To run the tests, use `unittest`. In the terminal window, run the tests for Part 1:

```bash
python3 -m unittest game_structures_test
```

and for Part 2:

```bash
python3 -m unittest game_play_test
```

To run a single test, give its full name. This is the best way to work on one thing at a time:

```bash
python3 -m unittest game_structures_test.HandTestCase.test_add_1card_to_hand
```

Add `-v` to see the name of every test as it runs. These are the same commands the autograder uses.

To play the game (after you have finished Parts 1 and 2):

```shell
python3 uw_euchre.py
```

## Checking your own work

Passing a test only tells you that one situation worked. A linked list can look right and still be
broken: a `prev` pointer that points at the wrong card, a count that is off by one, a card that
vanishes when you remove from the middle. Many of the provided tests catch this by calling
`assert_hand_valid(hand)`, which checks that the hand is a **valid** doubly linked list:

* going forward through the `next` pointers visits every card exactly once and then ends (no cycles);
* the number of cards you find equals `hand['num_cards_in_hand']`;
* the first card's `prev` is `None`;
* every other card's `prev` points back at the card before it.

Other tests call `assert_cards_conserved`, which checks that the deck and both hands together hold
exactly the cards you started with: no card lost, none duplicated, none invented.

When one of these checks fails, the message tells you what is wrong ("the 'prev' of the card at index 3
does not point back at the card at index 2"). You can use the same helpers in your own tests and while debugging, for example
right after each operation you write:

```python
add_card_to_hand(hand, card)
assert_hand_valid(hand)
```

# Grading

The autograder runs every time you push to GitHub. Look at the **Actions** tab of your repository
to see which steps passed. Each step below runs a group of tests, and you earn its points only when
**all** of the tests in that group pass, so you get partial credit by group.

## Automatic points (100)

| Part | Step | Points |
|------|------|-------:|
| 1 | Deck: create, push, peek | 7 |
| 1 | Deck: pop, is empty, last in first out | 6 |
| 1 | Card node and empty hand | 4 |
| 1 | Hand: add a card | 8 |
| 1 | Hand: peek at a card | 6 |
| 1 | Hand: remove a card | 12 |
| 1 | Hand: stays a valid linked list when removing | 8 |
| 1 | Hand: random operations match a Python list | 4 |
| | **Part 1 total** | **55** |
| 2 | Shuffle and deal | 8 |
| 2 | Return a hand to the deck | 6 |
| 2 | Legal moves | 5 |
| 2 | Compare cards | 8 |
| 2 | Who won the trick | 4 |
| 2 | Swap a card with the next one | 6 |
| 2 | Sort a hand | 6 |
| 2 | Play a whole round | 2 |
| | **Part 2 total** | **45** |

Each step runs with a time limit, so an infinite loop in your code will fail that step instead of
hanging.

## Assignment Review (25)

In addition to the automated points from tests (above), your assignment 
will be graded for the code quality such as naming, structure, legibility, and 
efficiency. 


# Rules and notes

* Let the tests guide your approach to this: run the tests, and work on one at a time until it passes.
* Start with `game_structures.py`. These are your basic data structures for the game.
* After the structures are done, work on `game_play.py`. These are the building blocks of the game.
* Once both are done, the game will play!
* The hand must be a real doubly linked list built from card nodes. The tests check the structure,
  not just the answers, so a Python list will not pass. The deck is a Python list used as a stack.
* For full credit on `sort_hand`, write your own sort. Do not use `sorted()` or `list.sort()`.
  (Hint: `swap_card_with_next()` makes a bubble sort straightforward.)
* **It is NOT okay** to put any of this code into ChatGPT or any other AI assistant for help as part
  of this assignment.

## Submission

Push your code to GitHub before the deadline, and submit a link to your GitHub repo on Canvas.

## Updates to the assignment

Any updates or clarifications to the assignment will be noted here and on Piazza.

We may periodically deploy updates to the assignment. You will need to resolve any conflicts that
occur. Please come to office hours or post on Piazza if you have any issues. If significant changes have been made,
we will do our best to send an announcement to the class.
