#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# File: perplexity.py
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

class Perplexity:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Perplexity estimation.

    Perplexity is a measurement of how well a probability distribution or
    probability model predicts a sample.

    The perplexity of a discrete probability distribution p is defined as:

    2^{H(p)}=2^{-\sum_x p(x)\log_2 p(x)}

    where H(p) is the entropy of the distribution and x ranges over events.

    """

    def __init__(self, model, ngram=1):
        """
        Create a Entropy instance with a list of symbols.

        @param model is a dictionary of probabilities representing a probability distribution.
        @param ngram (integer) is 1..8

        """
        self.set_model(model)
        self.set_ngram(ngram)

    # -----------------------------------------------------------------------

    def set_model(self, model):
        """
        Set the probability distribution o the model.

        @param model (dict) Dictionary with symbols as keys and values as probabilities.

        """
        if model is None or len(model)==0:
            raise ValueError('To estimate perplexity, the input model must contain at least one symbols.')
        psum = round( sum( proba for proba in model.values()), 6)
        if psum != 1.:
            raise ValueError('To estimate perplexity, the input model must contain probabilities.')

        self.model = model

        self.epsilon = 0.000001
        pmin = round( min( proba for proba in model.values()), 6)
        if pmin < self.epsilon:
            self.epsilon = pmin/3.

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

    def get(self, symbols):
        """
        Estimates the perplexity of a vector of symbols.

        @return float value

        """
        exr = symbols_to_items(symbols, self.ngram)
        entropy = 0

        for symbol,occurrences in exr.items():

            realsymbol=" ".join(symbol).strip()
            probability = self.model.get(realsymbol, self.epsilon)
            self_information = log2(1.0/probability)
            entropy += ((probability * self_information) * occurrences)

        return pow(2,entropy)


    # -----------------------------------------------------------------------

if __name__ == "__main__":

    model = {}
    model["1"] = 0.1
    model["2"] = 0.2
    model["3"] = 0.3
    model["4"] = 0.4
    pp = Perplexity( model )

    print round(pp.get(list("1234")),5), round(pp.get(list("1234")),5) == 1.84644
    print round(pp.get(list("1223334444")),5)

    print "Everything is equal:"
    model = {}
    model["0"] = 0.5
    model["1"] = 0.5
    pp = Perplexity( model )
    print "0000: ",round(pp.get(list("0000")),5)
    print "0100: ",round(pp.get(list("0100")),5)
    print "1111: ",round(pp.get(list("1111")),5)

    print "Close to real model:"
    model = {}
    model["0"] = 0.8
    model["1"] = 0.2
    pp = Perplexity( model )
    print "0000: ngram=1: ",round(pp.get(list("0000")),5)
    print "0100: ngram=1: ",round(pp.get(list("0100")),5)
    print "0101: ngram=1: ",round(pp.get(list("0101")),5)
    print "0110: ngram=1: ",round(pp.get(list("0110")),5)
    print "1111: ngram=1: ",round(pp.get(list("1111")),5)

    model = {}
    model["0 0"] = 0.75
    model["0 1"] = 0.1
    model["1 0"] = 0.1
    model["1 1"] = 0.05
    pp = Perplexity( model , ngram=2)
    print "00000000: ngram=2: ",round(pp.get(list("0000")),5)
    print "01000000: ngram=2: ",round(pp.get(list("0100")),5)
    print "01010000: ngram=2: ",round(pp.get(list("0101")),5)
    print "01100000: ngram=2: ",round(pp.get(list("0110")),5)
    print "11110000: ngram=2: ",round(pp.get(list("1111")),5)
