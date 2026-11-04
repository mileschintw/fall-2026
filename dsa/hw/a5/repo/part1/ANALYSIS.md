# Part 1 analysis: your BST against an AVL tree

Fill in each section below. Short answers are fine: a few sentences each. This part is graded by hand (15 points),
on your reasoning, not on polish.

## 1. Predict first (before you run compare.py)

The values 1 to 1,000 go into each tree, once in sorted order and once shuffled. Guess the height of each tree, and
say in a sentence or two why. You are graded on the reasoning, not on whether the guess is right, so do not change
these after you run the comparison.

| Tree | Sorted: height | Shuffled: height |
| --- | --- | --- |
| Your BST | | |
| AVL tree | | |

Why:

## 2. Results

Run `python3 compare.py` and paste the table it prints here.

## 3. Your BST, sorted against shuffled

Why is your BST so much taller when the values arrive sorted? What does the "BST avg steps" column say about how
long a search takes in each case, in terms of n?

## 4. The AVL tree

How does the AVL tree's height compare with log2(n), and with the bound from class (about 1.44 log2(n))? Why does
sorted input not hurt it? Look closely: for the AVL tree, is sorted input worse or better than shuffled? Can you
explain why?

## 5. Recursion

Did any row say `RecursionError`? If yes, which function raised it, at what size, and why that size? If no, explain
what would happen to a recursive `bst_insert` on these inputs and roughly at what size. Either way: why is the
AVL tree's recursive insert safe here?

## 6. Where sorted data shows up

Name one realistic situation where values would arrive in sorted (or nearly sorted) order. What would you use
instead of a plain BST there?
