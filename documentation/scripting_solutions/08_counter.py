#!/usr/bin python
"""

:author:       Brigitte Bigi
:date:         2016-May-07
:contact:      brigitte.bigi@gmail.com
:license:      GPL, v3
:copyright:    Copyright (C) 2016  Brigitte Bigi

:summary:      Simple script to compare 2 sets of data using NLP techniques.

"""

import codecs
import collections
import math

# ---------------------------------------------------------------------------
# Declarations
# ---------------------------------------------------------------------------

# The corpus to deal with
corpus1 = 'corpus1.txt'
corpus2 = 'corpus2.txt'

# ---------------------------------------------------------------------------
# General functions
# ---------------------------------------------------------------------------


def read_file(filename):
    """ Read the whole file, return lines into a list.

    :param filename: (str) Name of the file to read, including path.
    :returns: List of lines

    """
    my_list = list()
    with codecs.open(filename, 'r', encoding="utf8") as fp:
        for l in fp.readlines():
            my_list.append(l.strip())

    return my_list

# ---------------------------------------------------------------------------


def total(my_list, item):
    """ Return the number of occurrences of an item in the list.

    :param my_list: (list) list of items
    :param item: (any) an item of the list (or not!)
    :returns: (int) number of occurrences of an item in my list

    """
    return my_list.count(item)

# ---------------------------------------------------------------------------


def frequency(my_list, item):
    """ Return the relative frequency of an item of a list.

    :param my_list: (list) list of items
    :param item: (any) an item of the list (or not!)
    :returns: (float) frequency of an item in my list

    """
    return float(my_list.count(item)) / float(len(my_list))

# ---------------------------------------------------------------------------


def percentage(my_list, item):
    """ Return the percentage of an item of a list.

    :param my_list: (list) list of items
    :param item: (any) an item of the list (or not!)
    :returns: (float) percentage of an item in my list

    """
    return 100.0 * frequency(my_list, item)

# ---------------------------------------------------------------------------
# NLP functions
# ---------------------------------------------------------------------------


def get_occranks(counter):
    """ Return a dictionary with key=occurrence, value=rank.

    :param counter: (Counter)
    :returns: dict

    """
    occ = {}
    for k in counter.keys():
        v = counter[k]
        if v in occ:
            occ[v] += 1
        else:
            occ[v] = 1

    occranks = {}
    for r,o in enumerate(reversed(sorted(occ.keys()))):
        occranks[o] = r+1

    return occranks

# ---------------------------------------------------------------------------


def get_ranks(counter):
    """ Return a dictionary with key=token, value=rank.

    :param counter: (Counter)
    :returns: dict

    """
    ranks = {}
    occranks = get_occranks(counter)
    for k in counter.keys():
        occ = counter[k]
        ranks[k] = occranks[occ]
    return ranks

# ---------------------------------------------------------------------------


def zipf(ranks, item):
    """ Return the Zipf Law value of an item.
    Zipf's law states that given some corpus of natural language utterances,
    the frequency of any word is inversely proportional to its rank in the
    frequency table. Thus the most frequent word will occur approximately
    twice as often as the second most frequent word, three times as often
    as the third most frequent word, etc.

    @param ranks (dict) is a dictionary with key=entry, value=rank.
    @param item (any) is an entry of the ranks dictionary
    @return Zipf value or -1 if the entry is missing

    """
    if item in ranks:
        return 0.1 / ranks[item]
    return -1

# ---------------------------------------------------------------------------


def tfidf(documents, item):
    """ Return the tf.idf of an item.
    Term frequency–inverse document frequency, is a numerical statistic
    that is intended to reflect how important a word is to a document in a
    collection or corpus. The tf.idf value increases proportionally to the
    number of times a word appears in the document, but is offset by the
    frequency of the word in the corpus, which helps to control for the fact
    that some words are generally more common than others.

    @param documents is a list of list of entries.

    """
    # Estimate tf of item in the corpus
    alltokens = []
    for d in documents:
        alltokens.extend( d )
    tf = frequency(alltokens,item)

    # number of documents in the corpus
    D = len(documents)

    # number of documents with at least one occurrence of item
    dw = 0.0
    for d in documents:
        if item in d:
            dw += 1.0
    if dw == 0.0:
        return 0.0
    return tf * (math.log(D / dw))

# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------

if __name__ == '__main__':

    phones1 = read_file( corpus1 )
    phones2 = read_file( corpus2 )

    counter1 = collections.Counter(phones1)
    counter2 = collections.Counter(phones2)

    # Hapax
    hapax1 = [k for k in counter1.keys() if counter1[k]==1]
    hapax2 = [k for k in counter2.keys() if counter2[k]==1]
    print("Corpus 1, Number of hapax: {:d}.".format(len(hapax1)))
    print("Corpus 2, Number of hapax: {:d}.".format(len(hapax2)))

    # Zipf law
    ranks1 = get_ranks(counter1)
    ranks2 = get_ranks(counter2)
    for t in ['@', 'e', "E"]:
        print("Corpus 1: {:s} {:d} {:f} {:d} {:f}".format(t,total(phones1,t),frequency(phones1,t),ranks1.get(t,-1),zipf(ranks1,t)))
        print("Corpus 2: {:s} {:d} {:f} {:d} {:f}".format(t,total(phones2,t),frequency(phones2,t),ranks2.get(t,-1),zipf(ranks2,t)))

    # TF.IDF
    print("TF.IDF @: {0}".format(tfidf([phones1,phones2], '@')))
    print("TF.IDF e: {0}".format(tfidf([phones1,phones2], 'e')))
    print("TF.IDF E: {0}".format(tfidf([phones1,phones2], 'E')))

