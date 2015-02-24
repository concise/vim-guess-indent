#!/usr/bin/env python3

import collections
import re
import sys


MIX_NG_THRESHOLD = 0.2

USAGE = '''
Usage:
        simple-guess.py <filename>

Standard output:
        A digit character of 0, 1, 2, 3, 4, and 8
        0: Cannot make any guess
        1: Tab indentation
        2: 2-space indentation
        3: 3-space indentation
        4: 4-space indentation
        8: 8-space indentation
'''


def main():
    filename = get_filename_from_argument()
    filecontent_lines = get_filecontent_lines(filename)
    buffer_descriptor = get_buffer_descriptor(filecontent_lines)
    guessers = [
            (1, tab_indent_guesser(buffer_descriptor)),
            (2, space_indent_guesser(buffer_descriptor, CODING_STYLE=2, INDENT_NG_THRESHOLD=0.2)),
            (4, space_indent_guesser(buffer_descriptor, CODING_STYLE=4, INDENT_NG_THRESHOLD=0.3)),
            (8, space_indent_guesser(buffer_descriptor, CODING_STYLE=8)),
            (3, space_indent_guesser(buffer_descriptor, CODING_STYLE=3)),
            (0, messedup_guesser(buffer_descriptor)),
            ]

    def _first_matched_clause(func, list_):
        for item in list_:
            if func(item):
                return item
        # We shall never get here as long as you have
        # a guarding tuple at the end of the list
        return (0, True)

    def _is_true_clause(pair):
        value, boolean = pair
        return boolean

    print(_first_matched_clause(_is_true_clause, guessers)[0], end='')


def get_filename_from_argument():
    if len(sys.argv) != 2:
        print(USAGE, file=sys.stderr)
        print(0)
        sys.exit(1)
    filename = sys.argv[1]
    return filename


def get_filecontent_lines(filename):
    try:
        with open(filename) as f:
            return f.readlines()
    except OSError:
        print('Cannot successfully read the file', file=sys.stderr)
        return []


def get_buffer_descriptor(filecontent_lines):
    FileDescriptor = collections.namedtuple('FileDescriptor',
            'nlines_total, nlines_tabbed, nlines_spaced, space_counts')
    nlines_total = len(filecontent_lines)
    nlines_tabbed = 0
    nlines_spaced = 0
    space_counts = collections.defaultdict(int)
    for line in filecontent_lines:
        if len(line) == 0:
            continue
        elif line[0] == '\t':
            nlines_tabbed += 1
        elif line[0] == ' ':
            nlines_spaced += 1
            starting_spaces = re.match('^ +', line).group(0)
            space_counts[len(starting_spaces)] += 1

    # Convert a defaultdict to a list
    # {            } -> [0]
    # { 4: 3       } -> [4, 0, 0, 0, 3]
    # { 2: 7, 4: 6 } -> [4, 0, 7, 0, 6]
    _size = len(space_counts.keys())
    if _size == 0:
        _space_counts = [0]
    else:
        _max = max(space_counts.keys())
        _space_counts = [0] * (_max+1)
        _space_counts[0] = _max
        for nspace in space_counts:
            _space_counts[nspace] = space_counts[nspace]

    return FileDescriptor(
            nlines_total, nlines_tabbed, nlines_spaced, _space_counts)


def score_tab(descriptor):
    nlines_tabbed = descriptor.nlines_tabbed
    nlines_spaced = descriptor.nlines_spaced
    nlines_indented = nlines_tabbed + nlines_spaced
    if nlines_tabbed == 0:
        return 0
    if nlines_tabbed < 0.8 * nlines_indented:
        return 0
    return 1


def space_indent_guesser(descriptor, CODING_STYLE=2, INDENT_NG_THRESHOLD=0.5):
    MAX_INDENT_LEVEL = 10
    MAX_INDENT_COLUMN = 40

    if CODING_STYLE not in (2, 3, 4, 8):
        print('CODING_STYLE must be one of 2, 3, 4, or 8', file=sys.stderr)
        print(0)
        sys.exit(1)
        return False

    if not 0 <= INDENT_NG_THRESHOLD <= 1:
        print('INDENT_NG_THRESHOLD must be 0.0 ~ 1.0', file=sys.stderr)
        print(0)
        sys.exit(1)
        return False

    '''

    Considering a program that uses the 2-space indentation style.

    Let us assume that we never have nested levels more than half the
    screen width (80 columns), so the indentation frames will be:

        level            1   2   3   4    ...   17  18  19  20
        n_pre_spaces     2   4   6   8    ...   34  36  38  40

    And there should be many lines that each will match a slot above.

    Yet there would also be some lines that do not fit into any of the
    slots because they are continuation lines or something that are
    prefixed with a number of whitespaces for alignment purpose only.



    For example, let us say that a script has the following statistics.

        level            1   2   3   4    ...   17  18  19  20  N/A
        n_pre_spaces     2   4   6   8    ...   34  36  38  40  OTHERS
        n_lines         49  23  10   2    ...    0  17   0   0  30

    Now, what's the max indentation level of this buffer?  1, 2, ..., 18?



    Because the first zero occurs at level == 5, so the max indentation
    level is 4.

    By the way, if the first zero occurs at level == 1, the program
    should just return the conclusion that 2-space indentation is not
    suitable for this text buffer immediately.  The rule is simple.

    After concluding that the max indentation level is 4, we have to sum
    all the trailing n_lines[i] counts into `OTHERS`.  And now we have
    this:

        level            1   2   3   4   N/A
        n_pre_spaces     2   4   6   8   OTHERS
        n_lines         49  23  10   2   47

    Now check if the ratio is larger than (1/3).

            ( Number of lines considered matching this style )
            --------------------------------------------------
                ( Number of lines starting with spaces )

    If it is, returns that the coding style is good.
    If it is not, returns that the coding style is not good.



    Some configurable parameters are listed below.

            coding_style :: 2-space | 3-space | 4-space | 8-space | tab
            max_indent_level :: 10
            max_indent_column :: 40
            indent_ng_threshold :: 1/3

    '''

    # No line starts with spaces
    if descriptor.nlines_spaced == 0:
        return False

    # There are too many lines starting with tabs...
    if descriptor.nlines_tabbed > MIX_NG_THRESHOLD * descriptor.nlines_spaced:
        return False

    levels = range(1, 1 + max(
            MAX_INDENT_LEVEL, MAX_INDENT_COLUMN//CODING_STYLE))


    #
    # descriptor.space_counts =
    #
    #      0   1   2   3   4   5   6   7   8   9  10  ...  34  35  36
    #              |       |       |       |       |        |       |
    #              v       v       v       v       v        v       v
    #   [ 36,  0, 49,  0, 23, 21, 10,  0,  2,  9,  0, ...   0,  0, 17 ]
    #
    #                               除了 0 以外 idx 無法被 2 整除的數值總和為 30
    #
    def index_not_zero(pair):
        index, value = pair
        return index != 0
    source = filter(index_not_zero, enumerate(descriptor.space_counts))
    #
    # source = [
    #           ( 1,  0), ( 2, 49),
    #           ( 3,  0), ( 4, 23),
    #           ( 5, 21), ( 6, 10),
    #           ( 7,  0), ( 8,  2),
    #           ( 9,  9), (10,  0),
    #           (11,  0), (12,  0),
    #
    #                   ...
    #
    #           (33,  0), (34,  0),
    #           (35,  0), (36, 17),
    #          ]
    #
    result = [0] * (1 + descriptor.space_counts[0]//CODING_STYLE)
    for n_pre_spaces, n_lines in source:
        if n_pre_spaces % CODING_STYLE != 0:
            result[0] += n_lines
        else:
            result[n_pre_spaces // CODING_STYLE] += n_lines
    #
    # result = [
    #           30,     # 0
    #           49,     # 1
    #           23,     # 2
    #           10,     # 3
    #            2,     # 4
    #            0,     # 5
    #            0,     # 6
    #
    #           ...
    #
    #            0,     # 17
    #           17,     # 18
    #          ]
    #
    counter = 0
    for i in range(1, len(result)):
        if result[i] == 0:
            break
        else:
            counter += result[i]
    #print('')
    #print(result)
    return counter > INDENT_NG_THRESHOLD * descriptor.nlines_spaced


def tab_indent_guesser(descriptor):

    # No line starts with tabs
    if descriptor.nlines_tabbed == 0:
        return False

    # There are too many lines starting with spaces...
    if descriptor.nlines_spaced > MIX_NG_THRESHOLD * descriptor.nlines_tabbed:
        return False

    return True


def messedup_guesser(*_args, **_kwargs):
    return True


if __name__ == '__main__':
    main()
