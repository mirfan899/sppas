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
# File: patterns.py
# ----------------------------------------------------------------------------

import math

# ----------------------------------------------------------------------------

class Patterns( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Pattern matching.

    Pattern matching aims at of checking a given sequence of tokens for
    the presence of the constituents of some pattern. In contrast to pattern
    recognition, the match usually has to be exact.

    """
    MAX_GAP   = 4
    MAX_NGRAM = 4

    # ------------------------------------------------------------------------

    def __init__(self):
        """

        """
        self._ngram = 3
        self._score = 1.
        self._gap   = 2
        self._interstice = 4

    # ------------------------------------------------------------------------

    def get_score(self):
        return self._score

    def get_ngram(self):
        return self._ngram

    def get_gap(self):
        return self._gap

    # ------------------------------------------------------------------------

    def set_ngram(self, n):
        n = int(n)
        if n > 0 and n < Patterns.MAX_NGRAM:
            self._ngram = n
        else:
            raise ValueError("n value of n-grams pattern matching must range [1;%d]. Got %d."%(Patterns.MAX_NGRAM,n))

    # ------------------------------------------------------------------------

    def set_gap(self, g):
        g = int(g)
        if g >= 0 and g < Patterns.MAX_GAP:
            self._gap = g
            self._interstice = 2*g
        else:
            raise ValueError("gap value of pattern matching must range [0;%d]. Got %d."%(Patterns.MAX_GAP,g))

    # ------------------------------------------------------------------------

    def set_score(self, s):
        s = float(s)
        if s >= 0. and s <= 1.:
            self._score = s
        else:
            raise ValueError("score value of unigrams pattern matching must range [0;1]. Got %f."%s)

    # ------------------------------------------------------------------------
    # Matching search methods
    # ------------------------------------------------------------------------

    def ngram_matchings(self, ref, hyp):
        """
        n-gram alignment of ref and hyp.

        The algorithm is based on the finding of matching n-grams, in the
        range of a given gap. If 1-gram, keep only hypothesis items with a
        high confidence score. A gap of search has to be fixed.
        An interstice value ensure the gap between an item in the ref and
        in the hyp won't be too far.

        @param ref (list of tokens - IN) List of references
        @param hyp (list of tuples - IN) List of hypothesis with their scores
        The scores are supposed to range in [0;1] values.
        @return List of matching indexes as tuples (i_ref,i_hyp),

        Example:

        ref:  w0  w1  w2  w3  w4  w5  w6  w7  w8  w9  w10  w11  w12
               |   |   |   |       |   |          |
               |   |   |    \      |   |         /
               |   |   |      \    |   |        /
        hyp:  w0  w1  w2  wX  w3  w5  w6  wX  w9

        returned matchings:
         - n=3: [ (0,0), (1,1), (2,2) ]
         - n=2: [(0, 0), (1, 1), (2, 2), (5, 5), (6, 6)]
         - n=1 depends on the scores in hyp and the value of the gap.

        """
        matching = []

        # create n-gram sequences of the reference
        nman = zip(*[ref[i:] for i in range(self._ngram)])

        # create n-gram sequences of the hypothesis
        # if ngram=1, keep only items with a high confidence score
        if self._ngram > 1:
            tab = [ token for (token,score) in hyp ]
            nasr = zip(*[tab[i:] for i in range(self._ngram)])
        else:
            nasr = []
            for (token,score) in hyp:
                if score >= self._score:
                    nasr.append( (token,) )
                else:
                    nasr.append( ("<>",) )

        lastidxa = len(nasr)
        lastidxm = len(nman)
        lastidx = min(lastidxa,lastidxm)

        idxa = 0
        idxm = 0
        interstice = 0

        while idxa < lastidxa and idxm < (lastidx+self._gap-1):

            found = False

            # matching
            if idxm < lastidxm and nasr[idxa] == nman[idxm]:
                for i in range(self._ngram):
                    matching.append( (idxm+i,idxa+i) )
                found = True

            # matching, supposing deletions in hyp
            if idxm < lastidxm:
                for gap in range(self._gap):
                    if not found and idxm < (lastidxm-gap-1):
                        if nasr[idxa] == nman[idxm+gap+1]:
                            idxm = idxm + gap + 1
                            for i in range(self._ngram):
                                matching.append( (idxm+i,idxa+i) )
                            found = True

            # matching, supposing insertions in hyp
            if idxm > 0:
                for gap in range(self._gap):
                    if not found and idxm > (gap+1):
                        if nasr[idxa] == nman[idxm-gap-1]:
                            idxm = idxm - gap - 1
                            for i in range(self._ngram):
                                matching.append( (idxm+i,idxa+i) )
                            found = True

            idxa = idxa + 1
            idxm = idxm + 1

            # in case that idx in ref and idx in hyp are too far away...
            interstice = math.fabs( idxm - idxa )
            if interstice > self._interstice:
                vmax = max(idxa,idxm)
                idxa = vmax
                idxm = vmax

        return sorted(list(set(matching)))

    # ------------------------------------------------------------------------

    def dp_matching(self, ref, hyp):
        """
        Dynamic Programming alignment of ref and hyp.

        The DP alignment algorithm performs a global minimization of a
        Levenshtein distance function which weights the cost of correct words,
        insertions, deletions and substitutions as 0, 3, 3 and 4 respectively.

         See:
         TIME WARPS, STRING EDITS, AND MACROMOLECULES: THE THEORY AND PRACTICE OF SEQUENCE COMPARISON,
         by Sankoff and Kruskal, ISBN 0-201-07809-0

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------
