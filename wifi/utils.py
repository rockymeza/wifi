

def match(needle, haystack):
    """
    Command-T-style string matching.
    """
    score = 1
    j = 0
    last_match = 0
    needle = needle.lower()
    haystack = haystack.lower()

    for c in needle:
        while j < len(haystack) and haystack[j] != c:
            j += 1
        if j >= len(haystack):
            return 0
        score += 1 / (last_match + 1.)
        last_match = j
        j += 1
    return score


def print_table(matrix):
    """
    Prints a left-aligned table of elements.
    """
    lengths = [max(map(len, column)) for column in zip(*matrix)]
    format = '  '.join('{{{0}:<{1}}}'.format(i, length) for i, length in enumerate(lengths))

    for row in matrix:
        print(format.format(*row))
