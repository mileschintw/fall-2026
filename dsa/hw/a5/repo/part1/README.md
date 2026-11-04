# Part 1: A binary search tree, and how it compares with an AVL tree (50 points)

In class we built a binary search tree out of node dicts. Here you write it yourself, then measure it against an
AVL tree (provided) to see why balance matters. Starting from the code we wrote in class is fine. Make sure you
understand every line you hand in. Everything for this part is in this folder, `part1/`.

Part 2 includes a correct tree (`part2/bst_reference.py`). Don't copy it: writing your own is the point of this part,
and the exams ask you to write this code on paper.

**No AI assistant for this part** (Part 2 allows one, in `part2/` only). The midterm and final are on paper, without AI, and they
will ask you to do what this part practices: trace inserts, searches and deletes, write tree code, and explain why
a tree's shape decides how fast it is. Use this part to make sure you can do that yourself.

A tree is a node, `{'payload': value, 'left': node_or_None, 'right': node_or_None}`, or `None` for the
empty tree. `tree_tools.py` has `create_tree_node` and a few helpers; you do not edit it.

## What to write (in `bst.py`)

| Function | What it does |
| --- | --- |
| `bst_insert(root, value)` | Put `value` in the tree and return the root. `None` in gives a new node out. A value that is already there is ignored. |
| `bst_search(root, value)` | Return the **node** holding `value`, or `None`. |
| `bst_min(root)` | Return the node with the smallest value, or `None` for an empty tree. |
| `bst_max(root)` | Return the node with the largest value, or `None` for an empty tree. |
| `bst_delete(root, value)` | Remove `value` and return the root of what is left. A value that is not there changes nothing. |
| `search_steps(root, value)` | Search the way `bst_search` does, and return how many nodes you looked at. |

**The three cases for delete.** The node holding `value` has no children (remove it), one child (the child
takes its place), or two children (copy the smallest value of the right subtree, its *successor*, into the
node, then delete that successor from the right subtree). The root can change: deleting the only node gives
`None`, and deleting a root with one child returns that child. We drew these on the board in class; turning
the pictures into code is your job here.

**Loops or recursion: your choice.** Thinking recursively is a useful skill, and a tree is a natural place to
practice it. The comparison below will show you something about that choice, so pay attention to what it
prints.

## The comparison

`avl.py` is an AVL tree (insert and search), and `compare.py` puts the same values into your BST and into the
AVL tree, in sorted order and shuffled, for n = 100, 500, 1,000 and 2,000. For each it reports the height and
the average number of steps a search takes (using your `search_steps`). You do not edit either file.

1. Fill in section 1 of `ANALYSIS.md` (your predictions) **before** you run anything.
2. Run `python3 compare.py` and paste the table into section 2.
3. Answer sections 3 to 6.

If a row says `RecursionError` instead of a number, the script did not crash: that is a result, and section 5
asks you about it.

## Run the tests

In PyCharm, right-click `bst_test.py` and choose Run, or in a terminal, from the `part1` folder:

```
cd part1
python3 -m unittest bst_test -v
```

If PyCharm says `ModuleNotFoundError: No module named 'bst'`, right-click the `part1` folder and choose
**Mark Directory as > Sources Root**.

Run one group while you work, for example `python3 -m unittest bst_test.SearchTest`. At the start every
test fails with `NotImplementedError`; that is the starting line, not a broken repo. The tests check that your
tree is probably right. They do not check every corner, and passing them is not proof that it is correct.

## Points

When you push, GitHub runs the tests and shows the score on the Actions tab (Part 1's tests are 35 of the 75
points it shows). `ANALYSIS.md` is graded by hand.

| Part | Points |
| --- | --- |
| Insert | 8 |
| Search | 8 |
| Min and max | 4 |
| Delete | 10 |
| Search steps | 5 |
| `ANALYSIS.md` (by hand) | 15 |
| **Total** | **50** |

## Submit

See the README at the top of the repo: one push, both parts. Include `ANALYSIS.md`. Do not edit `bst_test.py`,
`tree_tools.py`, `avl.py` or `compare.py`; the instructor runs the original files.
