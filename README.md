# Puzzler 2019

* Generate word squares of size M x N cells
* Each cell must contain two letters or no letters
* Each row and column must spell a word
* 50% or more of the cells in each row and column must be filled
* At least one cell in each row and column must be blank
* Don’t repeat words anywhere
* Use uncapitalised words from /usr/share/dict/words
* Any language, output format, etc. is fine

## Usage

```
$ ./puzzler.py --help
usage: puzzler.py [-h] [--self-test] [--words-file WORDS_FILE] [--width WIDTH]
                  [--height HEIGHT] [--verbose] [--profile] [--randomise]

optional arguments:
  -h, --help            show this help message and exit
  --self-test           run doc tests
  --words-file WORDS_FILE
  --width WIDTH
  --height HEIGHT
  --verbose
  --profile             run with profiling enabled
  --randomise           randomise word order when searching
```

## Examples

Default width and height are 3:
```
$ ./puzzler.py 
  aani
ab  as
baru  
```

Different word file (top 1000 English words):

```
$ ./puzzler.py --words-file 1000.txt 
  base
fa  ll
cell  
```

Larger size:
```
$ ./puzzler.py --width 5 --height 5
  aaronite
    amober
yard    er
kava  ic  
larker    
```

With a randomised initial word ordering (which can help get a solution quickly
sometimes):
```
$ ./puzzler.py --width 5 --height 5 --randomise
    fixate
    buntal
beli    li
memp  hite
allylate  
```

It's not super-speedy, but earlier iterations (without the smarter indexing)
couldn't generate more than a 4x4 grid in a reasonable time:
```
$ time ./puzzler.py --width 5 --height 5 --randomise
    enlace
    abbasi
abra    um
rastle    
shik  ra  

real	0m6.276s
user	0m5.950s
sys	0m0.282s
```

With a bit of extra logging when running:
```
$ time ./puzzler.py --width 6 --height 5 --verbose --randomise
Width 6 Height 5
Total words selected from file file 83261
Considering 981814 word + space combinations for rows
Considering 323830 word + space combinations for columns
    cosharer
      abanic
abderian    
dentin    al
stin    go  

real	0m21.632s
user	0m20.542s
sys	0m0.985s
```

Running tests:
```
$ ./puzzler.py --self-test --verbose
Trying:
    infix_positions = build_infix_positions(['test', 'text'])
Expecting nothing
ok
Trying:
    infix_positions == {(0, 't'): {'text', 'test'},
                        (1, 'e'): {'text', 'test'},
                        (2, 's'): {'test'},
                        (2, 'x'): {'text'},
                        (3, 't'): {'text', 'test'}}
Expecting:
    True
ok
...
27 tests in 16 items.
27 passed and 0 failed.
Test passed.
```

## How it works

This is a fairly brute force algorithm, but does do some smartish things.

Initially it loads the words from the word file and splits them into a set of
words for the rows and the columns.  At this point it also generates all the
variations of those words (with the extra spaces added in) and turns them into
sequences of pairs of characters (one pair for each square).

Then it creates two indexes.

The first index is for the "next prefix" for the columns.  This let's us have a
partial word and determine what the next possible pair of characters/square
could be.  e.g. if we have the words "test", "tester" and "text", then we'd have
an index like:
```
    te -> st, ster, xt
    test -> er
```

(Nb. a prefix tree could have been used for this, but when you have a hammer...)

The second index maps pairs of characters at a specific position to the matching
words. e.g. for "test" and "text" we'd have:
```
    (0, te) -> test, text
    (1, st) -> test
    (1, xt) -> text
```

Then it iterates through all of the row words looking for possible solutions.
For each row word it uses a recursive backtracking algorithm (relying on the
call stack to maintain previous state).

During backtracking it does the following:
* Take the current partial column words in the solution
* Look those up in the prefix index
* For each of those it then uses the position index to find row words that are possible for each position
* The combined intersection of all of those possible row words is used do drive the next level of searching
* Once we reach the desired depth/height we yield a solution

Currently we only output the first solution, but as all of this is done with
generators it would be easy to make it output all solutions (in principle).

## Things it could do better

Currently it isn't smart about avoiding row words that already appear in the
solution, so this might lead to unneccesary searching.

It might be possible to reject solutions earlier.

Maybe could use some heuristic for selecting order of words to search - some
word orders lead to massively longer searchers than others.

