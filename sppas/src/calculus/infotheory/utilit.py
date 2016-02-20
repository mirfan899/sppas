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
# File: utilit.py
# ----------------------------------------------------------------------------

import math

# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

log2 = lambda x:math.log(x)/math.log(2)
MAX_NGRAM = 8

# ----------------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------------

def find_ngrams( symbols, ngram):
    """
    Return a list of ngrams from a list of symbols.

    @param symbols (list)
    @param ngram (int) n value for the ngrams
    @return list of tuples

    Example:
        >>>symbols=[0,1,0,1,1,1,0]
        >>>ngrams=find_ngrams(symbols,2)
        >>>print ngrams
        >>>[(0, 1), (1, 0), (0, 1), (1, 1), (1, 1), (1, 0)]

    """
    return zip(*[symbols[i:] for i in range(ngram)])


def symbols_to_items( symbols, ngram ):
    """
    Convert a list of symbols into a dictionary of items.

    @return dictionary with key=symbol, value=number of occurrences

    """
    nsymbols = find_ngrams(symbols, ngram)
    exr = {}
    for each in nsymbols:
        v = 1 + exr.get(each,0)
        exr[each] = v

    return exr
