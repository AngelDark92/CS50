from nltk.tokenize import sent_tokenize


def lines(a, b):
    """Return lines in both a and b"""

    # both lists are a set of unique elements
    # they will be sorted in compare anyway
    lista = set(a.splitlines())
    listb = set(b.splitlines())
    # returns a list of the lines after intersecting two sets
    return list(lista.intersection(listb))


def sentences(a, b):
    """Return sentences in both a and b"""

    # same as above but for sentences
    lista = set(sent_tokenize(a))
    listb = set(sent_tokenize(b))
    # intersection same as above
    # the \n and \r will be stripped in compare anyway
    return list(lista.intersection(listb))


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""

    # n is still in scope because it's a function inside a function, no need to create another arg
    def substr(file):
        '''Returns a list of non unique substrings'''

        substring = []
        # file - n because I can call the rest of the characters with i + n
        # + 1 because range starts from 0
        for i in range(len(file) - n + 1):
            substring.append(file[i:i + n])
        return substring

    lista = substr(a)
    listb = substr(b)

    # returning the compared unique sets of substrings directly into a list
    return list(set(lista) & set(listb))
