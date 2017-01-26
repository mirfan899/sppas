# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.calculus.infotheory.perplexity.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Perplexity is a measurement of how well a probability distribution or
    probability model predicts a sample.
    The perplexity of a discrete probability distribution p is defined as:

    2^{H(p)}=2^{-\sum_x p(x)\log_2 p(x)}

    where H(p) is the entropy of the distribution and x ranges over events.

"""
from .utilit import log2
from .utilit import MAX_NGRAM
from .utilit import symbols_to_items

# ----------------------------------------------------------------------------


class Perplexity(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Perplexity estimation.

    A model is represented as a distribution of probabilities: the key is
    representing the symbol and the value is the the probability.

    >>>model = {}
    >>>model["peer"] = 0.1
    >>>model["pineapple"] = 0.2
    >>>model["tomato"] = 0.3
    >>>model["apple"] = 0.4
    >>>pp = Perplexity(model)

    The observation on which the perplexity must be estimated on is
    represented as a list:
    >>>observed=['apple', 'pineapple', 'apple', 'peer']
    >>>pp.eval_perplexity(observed)
    >>>3.61531387398

    A higher adequacy between the model and the observed sequence implies an
    higher perplexity value:
    >>>observed=['apple', 'pineapple', 'apple', 'tomato']
    >>>pp.eval_perplexity(observed)
    >>>4.12106658324

    It is possible that an observed item isn't in the model... Then, the
    perplexity value is lower (because of an higher entropy). An epsilon
    probability is assigned to missing symbols.
    >>>observed=['apple', 'grapefruit', 'apple', 'peer']
    >>>pp.eval_perplexity(observed)
    >>>2.62034217479

    Perplexity is commonly used to compare models on the same list of
    symbols - this list of symbols is "representing" the problem we are
    facing one. The higher perplexity, the better model.

    """
    DEFAULT_EPSILON = 0.000001

    def __init__(self, model, ngram=1):
        """ Creates a Perplexity instance with a list of symbols.

        :param model: a dictionary of probabilities representing a probability distribution.
        :param ngram: (int) the n value, in the range 1..8

        """
        self.model = None
        self.ngram = None
        self.epsilon = self.DEFAULT_EPSILON

        self.set_model(model)
        self.set_ngram(ngram)

    # -----------------------------------------------------------------------

    def set_epsilon(self, eps=0.):
        """ Set a value for epsilon.
        This value must be significantly lower than the minimum value in the
        model.

        :param eps: new epsilon value.
        If eps is set to 0, a default value will be assigned.

        """
        eps = float(eps)
        if self.epsilon < 0. or self.epsilon > 0.01:
            raise ValueError("Expected an epsilon value in range [0, 0.01]. Got %f." % eps)

        if self.model is not None:
            # Find the minimum...
            pmin = round(min(proba for proba in model.values()), 6)
            if eps > pmin/2.:
                eps = pmin/3.

        if eps == 0.:
            self.epsilon = self.DEFAULT_EPSILON
        else:
            self.epsilon = eps

    # -----------------------------------------------------------------------

    def set_model(self, model):
        """ Set the probability distribution to the model.
        Notice that the epsilon value is re-assigned.

        :param model: (dict) Dictionary with symbols as keys and values as probabilities.

        """
        # check the model before assigning to the member
        if model is None:
            raise TypeError('A model must be assigned. Got NoneType.')

        if len(model) == 0:
            raise ValueError('A model must contain at least one symbols.')
        
        p_sum = sum(model.values())
        if round(p_sum, 6) != 1.:
            raise ValueError("A model must contain probabilities.")

        self.model = model
        self.set_epsilon()

    # -----------------------------------------------------------------------

    def set_ngram(self, n):
        """
        Set the n value of n-grams.

        :param n: (int) Value ranging from 1 to MAX_GRAM

        """
        if 0 < n <= MAX_NGRAM:
            self.ngram = n
        else:
            raise ValueError("The ngram value must be between 1 and 8. Got %d" % n)

    # -----------------------------------------------------------------------

    def eval_perplexity(self, symbols):
        """ Estimates the perplexity of a list of symbols.

        :returns: float value

        """
        exr = symbols_to_items(symbols, self.ngram)
        entropy = 0.

        for symbol, occurrences in exr.items():

            real_symbol = " ".join(symbol).strip()
            probability = self.model.get(real_symbol, self.epsilon)
            self_information = log2(1.0/probability)

            entropy += ((probability * self_information) * occurrences)

        return pow(2, entropy)

# ---------------------------------------------------------------------------

if __name__ == "__main__":

    model = {}
    model["1"] = 0.1
    model["2"] = 0.2
    model["3"] = 0.3
    model["4"] = 0.4
    pp = Perplexity(model)

    print round(pp.eval_perplexity(list("1234")), 5), round(pp.eval_perplexity(list("1234")), 5) == 1.84644
    print round(pp.eval_perplexity(list("1223334444")), 5)
    print round(pp.eval_perplexity(list("1111")), 5)

    print "Everything is equal:"
    model = {}
    model["0"] = 0.5
    model["1"] = 0.5
    pp = Perplexity(model)
    print "0000: ", round(pp.eval_perplexity(list("0000")),5)
    print "0100: ", round(pp.eval_perplexity(list("0100")),5)
    print "1111: ", round(pp.eval_perplexity(list("1111")),5)

    print "Close to real model:"
    model = {}
    model["0"] = 0.8
    model["1"] = 0.2
    pp = Perplexity(model)
    print "0000: ngram=1: ", round(pp.eval_perplexity(list("0000")),5)
    print "0100: ngram=1: ", round(pp.eval_perplexity(list("0100")),5)
    print "0101: ngram=1: ", round(pp.eval_perplexity(list("0101")),5)
    print "0110: ngram=1: ", round(pp.eval_perplexity(list("0110")),5)
    print "1111: ngram=1: ", round(pp.eval_perplexity(list("1111")),5)

    model = {}
    model["0 0"] = 0.75
    model["0 1"] = 0.1
    model["1 0"] = 0.1
    model["1 1"] = 0.05
    pp = Perplexity(model, ngram=2)
    print "00000000: ngram=2: ", round(pp.eval_perplexity(list("0000")),5)
    print "01000000: ngram=2: ", round(pp.eval_perplexity(list("0100")),5)
    print "01010000: ngram=2: ", round(pp.eval_perplexity(list("0101")),5)
    print "01100000: ngram=2: ", round(pp.eval_perplexity(list("0110")),5)
    print "11110000: ngram=2: ", round(pp.eval_perplexity(list("1111")),5)

    print
    print "the given example:"
    model = {}
    model["peer"] = 0.1
    model["pineapple"] = 0.2
    model["tomato"] = 0.3
    model["apple"] = 0.4
    pp = Perplexity(model, ngram=1)
    observed = ['apple', 'pineapple', 'apple', 'peer']
    print pp.eval_perplexity(observed)

    observed = ['apple', 'grapefruit', 'apple', 'peer']
    print pp.eval_perplexity(observed)

    observed = ['peer', 'pineapple', 'tomato', 'apple']
    print pp.eval_perplexity(observed)

    observed = ['apple', 'pineapple', 'tomato', 'apple']
    print pp.eval_perplexity(observed)
