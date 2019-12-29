#!/usr/bin/env python3

import argparse

from collections import defaultdict
from itertools import cycle, combinations


def spaced_out(sequence, space, num_spaces, output_type=tuple):
    """
    >>> list(spaced_out('test', ' ', 2, ''.join))
    ['  test', ' t est', ' te st', ' tes t', ' test ', 't  est', 't e st', 't es t', 't est ', 'te  st', 'te s t', 'te st ', 'tes  t', 'tes t ', 'test  ']
    """
    total_len = len(sequence) + num_spaces
    space_positions = combinations(range(total_len), num_spaces)
    for positions in space_positions:
        positions = set(positions)
        seq_iter = iter(sequence)
        yield output_type(next(seq_iter) if i not in positions else space for i in range(total_len))


def to_pairs(word):
    """
    >>> to_pairs('test')
    ('te', 'st')
    """
    return tuple(word[i:i+2] for i in range(0, len(word), 2))


def despace(paired_word):
    return tuple(p for p in paired_word if p.strip())


def spaced_out_words_of_right_length(paired_words, length):
    """
    >>> list(spaced_out_words_of_right_length([('te', 'st'), ('hi',), ('lo', 'ng', 'er')], 3))
    [('  ', 'te', 'st'), ('te', '  ', 'st'), ('te', 'st', '  ')]
    """
    half_length = length // 2
    for word in paired_words:
        spaces_needed = length - len(word)
        if 1 <= spaces_needed <= half_length:
            yield from spaced_out(word, '  ', spaces_needed)


def build_next_prefixes(words):
    """
    >>> next_prefixes = build_next_prefixes(['test', 'text'])
    >>> next_prefixes == {'t': {'e'},
    ...                   'te': {'x', 's'},
    ...                   'tes': {'t'},
    ...                   'tex': {'t'}}
    True
    """
    next_prefixes = defaultdict(set)
    for word in words:
        for i in range(0, len(word)-1):
            prefix, next_prefix = word[0:i+1], word[i+1]
            next_prefixes[prefix].add(next_prefix)
    return next_prefixes


def build_infix_positions(words):
    """
    >>> infix_positions = build_infix_positions(['test', 'text'])
    >>> infix_positions == {(0, 't'): {'text', 'test'},
    ...                     (1, 'e'): {'text', 'test'},
    ...                     (2, 's'): {'test'},
    ...                     (2, 'x'): {'text'},
    ...                     (3, 't'): {'text', 'test'}}
    True
    """
    infix_positions = defaultdict(set)
    for word in words:
        for i in range(0, len(word)):
            infix = word[i]
            infix_positions[(i, infix)].add(word)
    return infix_positions


def column_words(solution, width):
    """
    >>> list(column_words([('te', 'st')], 2))
    [('te',), ('st',)]
    >>> list(column_words([('te', 'st'), ('xt', 'ar')], 2))
    [('te', 'xt'), ('st', 'ar')]
    """
    for col in range(width):
        yield tuple(row[col] for row in solution)


def extract_words(solution, width):
    """
    >>> list(extract_words([('te', 'st'), ('xt', 'ar')], 2))
    [('te', 'st'), ('xt', 'ar'), ('te', 'xt'), ('st', 'ar')]
    """
    for row in solution:
        yield despace(row)
    for col in column_words(solution, width):
        yield despace(col)


def has_duplicate_words(solution, width):
    """
    >>> has_duplicate_words([('te', 'st'), ('xt', 'ar')], 2)
    False
    >>> has_duplicate_words([('te', 'st'), ('st', 'ar')], 2)
    True
    >>> has_duplicate_words([('te', 'st', ' '), ('  ', 'st', 'ar'), ('st', '  ', 'ay')], 3)
    True
    >>> has_duplicate_words([('te', 'xt', ' '), ('  ', 'st', 'ay'), ('st', '  ', 'ay')], 3)
    True
    """
    words = list(extract_words(solution, width))
    return len(words) != len(set(words))

from functools import reduce
def possible_next_words_at_position(infix_positions, prefixes, i):
    """
    >>> infix_positions = build_infix_positions(['test', 'text', 'tag', 'tig', 'tog'])
    >>> next_words = possible_next_words_at_position(infix_positions, ['a', 'e'], 1)
    >>> next_words == {'tag', 'test', 'text'}
    True
    """
    possible = set()
    for prefix in prefixes:
        possible.update(infix_positions[(i, prefix)])
    return possible


def possible_next_words(column_next_prefixes, row_infix_positions, prefixes):
    """
    >>> next_prefixes = build_next_prefixes(['hat', 'are', 'dis', 'bit'])
    >>> infix_positions = build_infix_positions(['test', 'text', 'tag', 'tig', 'tog'])
    >>> next_words = possible_next_words(next_prefixes, infix_positions, ['ha', 'ar', 'di', 'bi'])
    >>> next_words == {'test'}
    True
    >>> next_words = possible_next_words(next_prefixes, infix_positions, ['h', 'a', 'd', 'b'])
    >>> next_words == set()
    True
    """
    next_prefixes = (column_next_prefixes[prefix] for prefix in prefixes)
    for i, prefixes in enumerate(next_prefixes):
        next_possible = possible_next_words_at_position(row_infix_positions, prefixes, i)
        if i == 0:
            possible_words = next_possible
        else:
            possible_words.intersection_update(next_possible)
        if len(possible_words) == 0:
            break
    return possible_words


def backtrack(solution, column_next_prefixes, row_infix_positions, width, height):
    if len(solution) == height:
        if has_duplicate_words(solution, width):
             verbose("Skipping as has duplicate words")
             return
        else:
            yield solution

    prefixes = column_words(solution, width)
    possible_words = possible_next_words(column_next_prefixes, row_infix_positions, prefixes)

    for word in sorted(possible_words):
        next_solution = solution + [word]
        yield from backtrack(next_solution, column_next_prefixes, row_infix_positions, width, height)


def find_word_square(paired_words, width, height):
    """
    >>> words = ['past', 'near', 'edge', 'need', 'page', 'star']
    >>> find_word_square([to_pairs(word) for word in words], 3, 3)
      past
    ne  ar
    edge  
    >>> words = ['with', 'here', 'deal', 'that', 'wide', 'health', 'threat']
    >>> find_word_square([to_pairs(word) for word in words], 3, 4)
    wi  th
      here
    deal  
      that
    """
    row_words = list(spaced_out_words_of_right_length(paired_words, width))
    column_words = set(spaced_out_words_of_right_length(paired_words, height))

    verbose('Considering', len(row_words), 'word + space combinations for rows')
    verbose('Considering', len(column_words), 'word + space combinations for columns')

    column_next_prefixes = build_next_prefixes(column_words)
    row_infix_positions = build_infix_positions(row_words)

    for word in row_words:
        for solution in backtrack([word], column_next_prefixes, row_infix_positions, width, height):
            for row in solution:
                print(''.join(row))
            return


def main(args):
    verbose('Width', args.width, 'Height', args.height)
    with args.words_file:
        max_word_length = 2 * (max(args.width, args.height) - 1)
        lower_cased = (word.strip().lower() for word
                       in args.words_file.readlines())
        paired_words = list(sorted(set(to_pairs(word) for word in lower_cased
                         if len(word) % 2 == 0 and len(word) <= max_word_length)))
        verbose('Total words selected from file file', len(paired_words))
        if args.randomise:
            import random
            random.shuffle(paired_words)
        find_word_square(paired_words, args.width, args.height)


def verbose(*arg, **kw):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--self-test', action='store_true',
                        help='run doc tests')
    parser.add_argument('--words-file', type=argparse.FileType('r'), default='/usr/share/dict/words')
    parser.add_argument('--width', type=int, default=3)
    parser.add_argument('--height', type=int, default=3)
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--profile', action='store_true',
                        help='run with profiling enabled')
    parser.add_argument('--randomise', action='store_true',
                        help='randomise word order when searching')

    args = parser.parse_args()

    if args.self_test:
        import doctest
        doctest.testmod(verbose=args.verbose)
    else:
        if args.verbose:
            verbose = print
        if args.profile:
            import cProfile
            cProfile.run('main(args)')
        else:
            main(args)
