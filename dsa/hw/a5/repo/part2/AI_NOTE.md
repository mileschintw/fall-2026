# AI note

Part 2 allows AI assistants. This note is how you tell us what you did. Nothing here lowers
your grade: the 10 points are for filling it in, honestly, whether you used AI or not.

Write your answer on the line after "Answer:" (two to five sentences is plenty), and delete
"(write here)". "I did not use AI" is a complete answer if it is true.

## 1. Which AI assistant did you use for this part, if any?

Answer: Claude Code (Claude Opus 5.5), working inside part2/ only. It did not read or edit part1/.

## 2. What did you ask it to do? Summarize your prompts.

Answer: I asked what Part 2 required, then asked it to write tests from the specification in
bst_reference.py and the README. It wrote 53 tests and checked them against p1 to p4 and 26 extra
mutants it made itself. I then asked which tests were redundant and whether fuzzing fit, asked whether
the speed tests could be more deterministic than relying on a timeout, and finally asked it to fill
in this note and commit and push.

## 3. What did you change, add or throw away after reading what it gave you?

Answer: The first version had 53 tests, many overlapping (each practice mutant was caught by 5 to 8
of them). I had it cut them to 23: three model-based fuzz tests (random operations checked step by
step against a Python set) plus hand-written edge, delete, 5,000-deep chain and speed tests, then
re-ran all 30 mutants to confirm none were missed after the cut. I also had the speed tests changed
so an O(n) version fails within a second instead of only timing out.

## 4. Pick one of the four practice mutants (p1 to p4) and explain, in your own words, which test of yours catches it and why that test matters.

Answer: p2 breaks bst_delete: when the node to delete has only a left child, the function returns
early and deletes nothing. My test_delete_node_with_one_child catches it. It builds a tree from 50,
30, 20, 70, 60, where 30 and 70 each have only a left child, deletes both, and checks that the tree
is now 50 with children 20 and 60. On p2 neither delete changes anything, so that check fails. The
bug is easy to miss because a node's single child can be on either side, and a test that only
deletes nodes with a right child would pass on p2, which is why the same test also deletes from a
tree where 30 and 70 have only right children.
