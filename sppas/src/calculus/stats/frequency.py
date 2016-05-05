#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: frequency.py
# ----------------------------------------------------------------------------

import math

# ----------------------------------------------------------------------------

"""
@author:       Brigitte Bigi
@organization: Laboratoire Parole et Langage, Aix-en-Provence, France
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2011-2016  Brigitte Bigi
@summary:      Frequency estimators.

A collection of basic statistical functions for python.

Function List
=============
    - frequency
    - percentage
    - hapax
    - occranks
    - ranks
    - zipf
    - tfidf

"""

# ---------------------------------------------------------------------------

def frequency(mylist, item):
    """
    Return the relative frequency of an item of a list.

    @param mylist (list) list of elements
    @param item (any) an element of the list (or not!)
    @return frequency (float) of item in mylist

    """
    return float(mylist.count(item)) / float(len(mylist))

# ---------------------------------------------------------------------------

def percentage(mylist, item):
    """
    Return the percentage of an item of a list.

    @param mylist (list) list of elements
    @param item (any) an element of the list (or not!)
    @return percentage (float) of item in mylist

    """
    return 100.0 * frequency(mylist,item)


# ---------------------------------------------------------------------------
# NLP functions related to frequency
# ---------------------------------------------------------------------------

def hapax(counter):
    """
    Return a list of hapax (keys with values=1).

    @param counter (collections.Counter)
    @return list

    """
    return [k for k in counter.keys() if counter[k]==1]

# ---------------------------------------------------------------------------

def occranks(counter):
    """
    Return a dictionary with key=occurrence, value=rank.

    @param counter (collections.Counter)
    @return dict

    """
    occ = {}
    for k in counter.keys():
        v = counter[k]
        if v in occ:
            occ[v] += 1
        else:
            occ[v] = 1

    ocdict = {}
    for r,o in enumerate(reversed(sorted(occ.keys()))):
        ocdict[o] = r+1

    return ocdict

# ---------------------------------------------------------------------------

def ranks(counter):
    """
    Return a dictionary with key=token, value=rank.

    @param counter (collections.Counter)
    @return dict

    """
    r = {}
    oclist = occranks(counter)
    for k in counter.keys():
        occ = counter[k]
        r[k] = oclist[occ]
    return r

# ---------------------------------------------------------------------------

def zipf(ranks, item):
    """
    Return the Zipf Law value of an item.
    Zipf's law states that given some corpus of natural language utterances,
    the frequency of any word is inversely proportional to its rank in the
    frequency table. Thus the most frequent word will occur approximately
    twice as often as the second most frequent word, three times as often
    as the third most frequent word, etc.

    @param ranks (dict) is a dictionary with key=entry, value=rank.
    @param item (any) is an entry of the ranks dictionary
    @return Zipf value or -1 if the entry is missing

    """
    if ranks.has_key(item):
        return 0.1 / ranks[item]
    return -1

# ---------------------------------------------------------------------------

def tfidf(documents, item):
    """
    Return the tf.idf of an item.
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
    if dw == 0.:
        return 0.
    return tf * (math.log(D / dw))

# ---------------------------------------------------------------------------
