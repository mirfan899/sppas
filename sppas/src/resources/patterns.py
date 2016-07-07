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
    def __init__(self):
        """

        """
        self._ngram = 3
        self._score = 1.
        self._interstice = 2


    def set_ngram(self, n):
        """
        """
        n = int(n)
        if n > 0 and n < 20:
            self._ngram = n
        else:
            raise ValueError("n value of n-grams pattern matching must range [0;20]. Got %d."%n)


    def set_interstice(self, i):
        """
        """
        i = int(i)
        if i < 0 and i < 10:
            self._interstice = i
        else:
            raise ValueError("interstice value of pattern matching must range [0;10]. Got %d."%i)


    def set_score(self, s):
        """
        """
        s = float(s)
        if s >= 0. and s <= 1.:
            self._score = s
        else:
            raise ValueError("score value of unigrams pattern matching must range [0;1]. Got %f."%s)


    def matchings(self, ref, hyp):
        """
        Return items that are both aligned in ref and hyp.

        @param ref (list of tokens - IN) List of references
        @param hyp (list of tuples - IN) List of hypothesis with their scores
        The scores are supposed to range in [0;1] values.
        @return List of matching indexes (ref,hyp)

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
                    nasr.append( token )
                else:
                    nasr.append( "<>" )

        lastidx = min(len(nasr),len(nman))
        idxa = 0
        idxm = 0
        interstice = 0

        while idxa<lastidx and idxm<lastidx and interstice<self._interstice:
            found = False

            if nasr[idxa] == nman[idxm]:
                print "Matching exact with n=",self._ngram, range(idxa,idxa+self._ngram)
                for i in range(self._ngram):
                    matching.append( (idxm+i,idxa+i) )
                found = True

            if not found and idxm < lastidx:
                if nasr[idxa] == nman[idxm+1]:
                    idxm = idxm + 1
                    print "Matching shift+1 with n=",self._ngram, range(idxa,idxa+self._ngram)
                    for i in range(self._ngram):
                        matching.append( (idxm+i,idxa+i) )
                    found = True

            if not found and idxm > 0:
                if nasr[idxa] == nman[idxm-1]:
                    idxm = idxm - 1
                    print "Matching shift-1 with n=",self._ngram, range(idxa,idxa+self._ngram)
                    for i in range(self._ngram):
                        matching.append( (idxm+i,idxa+i) )

            idxa = idxa + 1
            idxm = idxm + 1

            interstice = math.fabs( idxm - idxa )

        return sorted(list(set(matching)))
