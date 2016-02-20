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
# File: entropy.py
# ----------------------------------------------------------------------------

import math

from utilit import log2
from utilit import MAX_NGRAM
from utilit import symbols_to_items

# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Class Entropy
# ----------------------------------------------------------------------------

class Entropy:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Entropy estimation.

    Entropy is a measure of unpredictability of information content.
    Entropy is one of several ways to measure diversity.

    If we want to look at the entropy on a large serie, we could also compute
    the entropy for windows to measure the evenness or uncertainties.
    By looking at the definition, one could predict the areas that have a
    lot of variance would result in a higher entropy and the areas that have
    lower variance would result in lower entropy.

    """

    def __init__(self, symbols, ngram=1):
        """
        Create a Entropy instance with a list of symbols.

        @param symbols is a vector of symbols of any type
        @param ngram (integer) is 1..8

        """
        self.set_symbols(symbols)
        self.set_ngram(ngram)

    # -----------------------------------------------------------------------

    def set_symbols(self, symbols):
        """
        Set the list of symbols.

        @param symbols (list) List of symbols of any type.

        """
        if symbols is None or len(symbols)==0:
            raise ValueError('To estimate entropy, the input vector must contain at least one symbols.')
        self.symbols = symbols

    # -----------------------------------------------------------------------

    def set_ngram(self, n):
        """
        Set the n value of n-grams.

        @param n (int) Value ranging from 1 to MAX_GRAM

        """
        if n > 0 and n < MAX_NGRAM:
            self.ngram = n
        else:
            raise ValueError('The ngram value must be between 1 and 8. Got %d'%n)

    # -----------------------------------------------------------------------

    def get(self):
        """
        Estimates the Shannon entropy of a vector of symbols.

        Shannon's entropy measures the information contained in a message as
        opposed to the portion of the message that is determined
        (or predictable).

        @return float value

        """

        exr = symbols_to_items(self.symbols, self.ngram)
        total = len(self.symbols) - self.ngram + 1
        entropy = 0

        for symbol,occurrences in exr.items():
            probability = 1.0*occurrences/total
            self_information = log2(1.0/probability)
            entropy += (probability * self_information)

        return entropy

    # -----------------------------------------------------------------------

if __name__ == "__main__":

    entropy = Entropy( list("1223334444") )
    print round(entropy.get(),5), round(entropy.get(),5) == 1.84644

    entropy.set_symbols( list("0000000000") )
    print "0: ",round(entropy.get(),5)

    entropy.set_symbols( list("1000000000") )
    print "1: ",round(entropy.get(),5)

    entropy.set_symbols( list("1100000000") )
    print "2: ",round(entropy.get(),5)

    entropy.set_symbols( list("1110000000") )
    print "3: ",round(entropy.get(),5)

    entropy.set_symbols( list("1111000000") )
    print "4: ",round(entropy.get(),5)

    entropy.set_symbols( list("1111100000") )
    print "5: ",round(entropy.get(),5)

    entropy.set_symbols( list("1111111111") )
    print "10: ",round(entropy.get(),5)

    entropy.set_symbols( list("1111000000") )
    entropy.set_ngram(1)
    print "1111000000, ngram = 1: ",round(entropy.get(),5)
    entropy.set_ngram(2)
    print "1111000000, ngram = 2: ",round(entropy.get(),5)

    entropy.set_symbols( list("1010101010") )
    print "1010101010: ngram=2",round(entropy.get(),5)
    entropy.set_symbols( list("1111100000") )
    print "1111100000: ngram=2",round(entropy.get(),5)
