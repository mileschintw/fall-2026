# Part 1 analysis: your BST against an AVL tree

Fill in each section below. Short answers are fine: a few sentences each. This part is graded by hand (15 points),
on your reasoning, not on polish.

## 1. Predict first (before you run compare.py)

The values 1 to 1,000 go into each tree, once in sorted order and once shuffled. Guess the height of each tree, and
say in a sentence or two why. You are graded on the reasoning, not on whether the guess is right, so do not change
these after you run the comparison.

| Tree     | Sorted: height | Shuffled: height |
| -------- | -------------- | ---------------- |
| Your BST | 999            | about 25         |
| AVL tree | about 10 to 14 | about 10 to 14   |

Why: With sorted input every new value is larger than everything already in the BST, so it always goes to the right and the tree becomes a chain of 1,000 nodes (height 999). Shuffled input splits values roughly evenly at each node, so the height should be a small multiple of log2(1000), which is about 10. The AVL tree rebalances after every insert and its height is bounded by about 1.44 times log2(n), roughly 14, so the order of the input should not matter much.

## 2. Results

Run `python3 compare.py` and paste the table it prints here.

| n    | order    | BST height              | BST avg steps | AVL height | AVL avg steps | log2(n) |
| ---- | -------- | ----------------------- | ------------- | ---------- | ------------- | ------- |
| 100  | sorted   | 99                      | 50.50         | 6          | 5.80          | 6.6     |
| 100  | shuffled | 13                      | 7.09          | 7          | 5.85          | 6.6     |
| 500  | sorted   | 499                     | 250.50        | 8          | 8.00          | 9.0     |
| 500  | shuffled | 18                      | 11.11         | 10         | 8.18          | 9.0     |
| 1000 | sorted   | RecursionError (insert) | -             | 9          | 8.99          | 10.0    |
| 1000 | shuffled | 20                      | 11.21         | 11         | 9.20          | 10.0    |
| 2000 | sorted   | RecursionError (insert) | -             | 10         | 9.98          | 11.0    |
| 2000 | shuffled | 27                      | 13.67         | 12         | 10.23         | 11.0    |

## 3. Your BST, sorted against shuffled

Why is your BST so much taller when the values arrive sorted? What does the "BST avg steps" column say about how
long a search takes in each case, in terms of n?

When the values arrive sorted, each one is bigger than every value already in the tree, so insert always walks to the right end and attaches the new node there. The tree becomes a chain of height n - 1 (99 and 499 in the table). Searching for the k-th value visits k nodes, so the average is (1 + 2 + … + n)/n = (n + 1)/2. That is exactly the 50.50 and 250.50 in the table, so search is linear, Θ(n). With shuffled input the first values split the range roughly in half and the tree stays bushy. Average steps only grow from 7.1 to 13.7 while n grows 20 times, which is logarithmic: the averages are about 1.1 to 1.25 times log2(n).

## 4. The AVL tree

How does the AVL tree's height compare with log2(n), and with the bound from class (about 1.44 log2(n))? Why does
sorted input not hurt it? Look closely: for the AVL tree, is sorted input worse or better than shuffled? Can you
explain why?

The AVL heights stay within one or two levels of log2(n): 6 and 7 for n = 100, 8 and 10 for 500, 9 and 11 for 1,000, 10 and 12 for 2,000. That is well below the class bound of 1.44 times log2(n), about 14.4 for n = 1,000. Sorted input does not hurt it because after each insert the tree checks the balance factor on the way back up and rotates as soon as one side is two levels taller, so a chain can never form. In fact sorted input is slightly better. The sorted heights are exactly floor(log2 n), the smallest height any binary tree with n nodes can have, and sorted searches are a little shorter on average too (8.99 steps against 9.20 for n = 1,000). With increasing values every imbalance is on the right side of a right child (the right-right case), so each fix is a single left rotation and a double rotation is never needed. Each of those rotations lifts a middle value up, and the tree ends up nearly perfect. With shuffled input the AVL rule only guarantees that each node's subtrees differ by at most one level. That allowed imbalance adds up along some paths, so the tree ends a level or two taller.

## 5. Recursion

Did any row say `RecursionError`? If yes, which function raised it, at what size, and why that size? If no, explain
what would happen to a recursive `bst_insert` on these inputs and roughly at what size. Either way: why is the
AVL tree's recursive insert safe here?

Yes. `bst_insert` raised `RecursionError` for the sorted input at n = 1,000 and n = 2,000; n = 100 and 500 were fine. My insert is recursive, and inserting into a chain of k nodes takes k + 1 nested `bst_insert` calls (one per node, plus the last call that reaches `None`). Python's default recursion limit is 1,000 frames, and `compare.py` already has four on the stack (the module, `main`, `measure` and `build`), so the error comes when the chain reaches about 995 nodes, partway through the n = 1,000 run. A 500-node chain needs only about 505 frames. My `search_steps` is a loop, but that is not why the n = 500 sorted row has an average: a recursive search would also have needed only about 500 frames there. The loop would only matter at depths near 1,000, and these runs never got there because insert failed first. The AVL insert is recursive too, but its depth is the tree's height, at most about 1.44 times log2(n). For n = 2,000 that is around 16 calls, nowhere near 1,000, because the depth grows with log n instead of with n.

## 6. Where sorted data shows up

Name one realistic situation where values would arrive in sorted (or nearly sorted) order. What would you use
instead of a plain BST there?

Timestamps are a common case: log entries, sensor readings or bank transactions arrive in time order, and database rows often get auto-incrementing IDs. Indexing them in a plain BST would build exactly the chain from section 3, making every lookup linear. A self-balancing tree such as an AVL or red-black tree (what Java's `TreeMap` and C++'s `std::map` use), or a B-tree as in a database index, keeps lookups at O(log n) whatever the order. If I only need lookups by key and never need the values in order, a hash table works too.
