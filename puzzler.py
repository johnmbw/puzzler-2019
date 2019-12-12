#!/usr/bin/env python3

import argparse

from itertools import cycle, permutations


def spaced_out(sequence, space, num_spaces, output_type=tuple):
    """
    >>> list(sorted(spaced_out('test', ' ', 2, ''.join)))
    ['  test', ' t est', ' te st', ' tes t', ' test ', 't  est', 't e st', 't es t', 't est ', 'te  st', 'te s t', 'te st ', 'tes  t', 'tes t ', 'test  ']
    """
    item = cycle(sequence).__next__
    spaces_and_items = ([item] * len(sequence)) + ([lambda: space] * num_spaces)
    for combination in set(permutations(spaces_and_items, len(spaces_and_items))):
        yield output_type(i() for i in combination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--self-test', action='store_true')

    args = parser.parse_args()

    if args.self_test:
        import doctest
        doctest.testmod(verbose=True)
