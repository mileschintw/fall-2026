# Programming Assignment 2: Analysis

Name: Tsung-Wei Chin

How to fill this in:
* Write your answer after each `ANSWER:` marker, on the same line and/or the lines below it.
  Keep it above the next heading. Delete the "(replace this ...)" text.
* Do NOT delete or rename the `ANSWER:` markers.
* Diagrams can be plain text. For example, an array with three values and one empty slot: `[ a | b | c | _ ]`
* Use your own words and your own numbers. Short, specific answers are better than long vague ones.

## Part A: On paper (do this before you write code)

### A1
Draw an array list with capacity 4 holding 'a', 'b', 'c' (size 3). Use `_` for an empty slot.
Now draw it after `array_list_insert_at(lst, 1, 'x')`. How many values were shifted, so what
should 'moves' be?

ANSWER:
Before: [ a | b | c | _ ]
After: [ a | x | b | c ]
Moves: 2

### A2
Start again from a FULL array list: capacity 4 holding 'a', 'b', 'c', 'd'. Draw the array after
`array_list_insert_at(lst, 4, 'x')`. What is the capacity now? How many values were copied?
Why can inserting at the END cost a lot sometimes, and almost nothing other times?

ANSWER:
[ a | b | c | d | x | _ | _ | _ ]
Capacity: 8
Copied: 4
Inserting at the end will trigger an enlargement that make capacity double, which is costly. If the array is not full, inserting at the end will cost almost nothing.

### A3
Draw the linked list a -> b -> c (show 'head', 'size', and the nodes with their links). Draw it
again after `linked_list_insert_at(lst, 1, 'x')`. Which links changed? How many?

ANSWER:
Before: head -> a -> b -> c, size = 3
After: head -> a -> x -> b -> c, size = 4
Links changed: x.next = b, a.next = x
Number of links changed: 2

### A4
Which structure does less work to remove the value at index 0: the array list or the linked
list? Which does less work to get the value at index 2? Explain in a sentence or two.

ANSWER:
Linked list is better for removing at index 0 as it can simply make the head point to the next node.
Array list is better for getting the value at index 2 as it can access it directly using indexing.

## Part D: Timing

### Step 1: Predictions (write these BEFORE you run timing.py)
You will not lose points for a wrong prediction. The point is to notice when you are surprised.

### P1
At n = 100,000, which is faster at inserting a value at the FRONT: Python's built-in list or your
linked list? About how many times faster?

ANSWER:
Linked list should be faster, because it only needs to change the head and Python list has to shift everything. My guess is about 50 times faster.

### P2
At n = 100,000, which is faster at getting the MIDDLE value: your array list or your linked
list? About how many times faster?

ANSWER:
Array list is faster since it can go to index n // 2 directly. Linked list has to walk through 50,000 nodes. I think about 1000 times faster.

### P3
Python's list and array.array can both hold 1,000 whole numbers. Which one do you think uses less
memory, and about how many times less?

ANSWER:
array.array uses less memory because it stores the numbers directly. My guess is about 2 times less.

### Step 2: Time it yourself (my_timing.py)

### T1
Run `python3 my_timing.py` and paste the table it printed. Then explain: for small n, which of the
two columns (stopwatch or timeit) do you trust more, and why does running something many times
and averaging help?

ANSWER:
n = 1,000: stopwatch 95.3, timeit 98.3
n = 10,000: stopwatch 537.6, timeit 558.2
n = 100,000: stopwatch 6489.0, timeit 6315.7
I trust timeit more for small n. The stopwatch only times one insert, so if the computer is doing something else at that moment the number can be off a lot, and when the whole thing is only around 100 microseconds that matters. timeit runs it 20 times and takes the average, so one bad run doesn't change much. I ran it twice and the n = 1,000 timeit still went from 98.3 to 60.7, so 20 times is still not that many. At n = 100,000 the two columns are close.

### Step 3: The experiment (timing.py)
Run `python3 timing.py` and paste ALL of its output between the lines of backticks below.

### Your results

```text
Python 3.13.3
Sizes: 100, 1,000, 10,000, 100,000
  timing your array_list ...
  timing your linked_list ...
  timing Python list ...
  timing array.array ...
  timing deque ...

Insert a value at the FRONT (index 0)
  microseconds per operation
  structure                  n=100       n=1,000      n=10,000     n=100,000
  your array_list             4.64         95.84        904.97      7,305.79
  your linked_list            0.16          0.17          0.59          0.51
  Python list                 0.04          0.15          9.85        108.64
  array.array                 0.04          0.07          7.86         69.74
  deque                       0.02          0.02          0.02          0.03

Get the MIDDLE value (index n // 2)
  microseconds per operation
  structure                  n=100       n=1,000      n=10,000     n=100,000
  your array_list             0.08          0.16          0.14          0.76
  your linked_list            0.86          8.21        164.40      1,073.56
  Python list                 0.03          0.04          0.04          0.06
  array.array                 0.04          0.05          0.10          0.08
  deque                       0.04          0.05          0.12          2.36

Insert a value at the END
  microseconds per operation
  structure                  n=100       n=1,000      n=10,000     n=100,000
  your array_list             0.17          0.40          0.21          0.53
  your linked_list            1.71         18.35        302.54      1,958.79
  Python list                 0.02          0.02          0.02          0.03
  array.array                 0.03          0.03          0.07          0.04
  deque                       0.02          0.02          0.02          0.03

Memory for 1,000 whole numbers (0 .. 999)
  Python list:  8,056 bytes for the list itself
               + about 28,000 bytes for the int objects it points to
  array.array:  4,200 bytes (the numbers are stored directly in the array)

Copy ALL of this output into analysis.md.
```

### Q1
Pick ONE operation on ONE of YOUR structures (for example, get the middle value of your linked
list). How did its time change as n went from 1,000 to 10,000 to 100,000? Does the change match
its Big-O? Give the numbers and the ratio.

ANSWER:
I picked insert at the front of my array list.
1,000: 95.84 us
10,000: 904.97 us
100,000: 7,305.79 us
10x more values made it about 9.4x slower, then about 8.1x slower. That is close to 10x each time, which matches O(n), because inserting at index 0 has to shift all n values.

### Q2
For inserting at the front, at about what n does your linked list become faster than Python's
built-in list? (Look between the sizes in the table.) Why does Python's list win for small n,
even though its Big-O is worse?

ANSWER:
Around n = 1,000. At n = 100 Python's list was faster (0.04 vs 0.16 us), at 1,000 they were about the same (0.15 vs 0.17), and at 10,000 my linked list was much faster (0.59 vs 9.85). Big-O doesn't count the constant. Python's list shifts with one memmove in C, which is really fast when there are only a few hundred values. My linked list runs Python code and makes a new dict for every node, and that costs about 0.16 us every time no matter what n is.

### Q3
Inserting at the front of Python's list and of your array list are both O(n), but Python's is much
faster. Why?

ANSWER:
My array list moves the values one by one in a Python for loop, and it also adds 1 to moves every step. Python's list is written in C and moves the whole block at once with memmove. At n = 100,000 it was 7,305.79 us vs 108.64 us, so about 67 times faster for the same amount of shifting.

### Q4
array.array and Python's list are both O(n) at the front, but array.array is a few times faster.
Use the memory numbers to explain why.

ANSWER:
For 1,000 numbers the list itself is 8,056 bytes (an 8 byte pointer for each number) plus about 28,000 bytes for the int objects, so around 36,000 bytes. array.array only needs 4,200 bytes because each number is 4 bytes stored right in the array. When we shift for a front insert, array.array moves 4 bytes per value and list moves 8, so array.array moves half as much memory. In my run it was 69.74 vs 108.64 us at n = 100,000, about 1.6x faster. That's less than "a few times" on my computer, but it's still faster.

### Q5
Getting the middle value of a deque and of your linked list are both O(n), but the deque is far
faster at large n. What do you think is different about how they are built?

ANSWER:
My linked list is one Python dict per value, and to get to the middle it runs a Python loop through 50,000 next links. That took 1,073.56 us. I think deque is written in C and stores values in blocks (64 values per block), so it can jump a whole block at a time instead of visiting every value. It can also start from whichever end is closer. It only took 2.36 us, around 450 times faster.

### Q6
Which of the five structures would you choose for (a) 1,000,000 values that are read by index all
day and almost never changed, and (b) a line of tasks where new ones are added at the back and
finished ones are removed from the FRONT, millions of times? Explain each.

ANSWER:
(a) array.array, or Python's list. Getting by index is O(1), and get middle stayed under 0.1 us for both at every n. The data almost never changes so the slow front insert doesn't matter, and array.array would use around 4 MB for 1,000,000 numbers instead of around 36 MB.
(b) deque. Adding at the back and removing from the front are both O(1). In my table deque front insert was 0.03 us at n = 100,000, while Python's list took 108.64 us because it shifts everything every time.

### Q7
What surprised you most in these results, and what does it tell you about predicting performance?

ANSWER:
Python's list beating my linked list at the front for small n surprised me, since linked list is O(1) there. I also didn't expect my linked list to be so slow at inserting at the end (1,958.79 us at n = 100,000). It has no tail pointer so it walks the whole list every time. So Big-O only tells me how the time grows when n gets bigger. Which one is faster at a certain n also depends on things like C vs Python and how much memory gets moved, so I should time it instead of guessing.
