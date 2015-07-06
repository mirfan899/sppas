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
# File: kappa.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------

import sys
import os
import os.path
import collections

from stats.distances import squared_euclidian as sq

# ----------------------------------------------------------------------------

def normalize_text(text):
    return text.lower().strip()


def tier_to_counter(tier):
    """
    Return a counter with label/count.
    """
    labels = list()
    for a in tier:
        texts = a.GetLabel().GetLabels()
        labels.extend(normalize_text(t.GetValue()) for t in texts )

    return collections.Counter(labels)


def tier_to_items(tier):
    c = tier_to_counter(tier)
    return c.keys()


def normalize_annotation(ann):
    scores = [ t.Score for t in ann.GetLabel().GetLabels() ]
    labels = [ normalize_text(t.Value) for t in ann.GetLabel().GetLabels() ]

    probas    = all( list( (v>=0. and v<=1.) for v in scores) ) and sum(scores)==1.
    if probas: return [ (labels[i],scores[i]) for i in range(len(scores)) ]

    percentage = all( list( (v>=0. and v<=100.) for v in scores)) and sum(scores)==100.
    if percentage: return [ (labels[i],float(scores[i])/100.) for i in range(len(scores)) ]

    raise TypeError('Kappa.py. Expect scores as probabilities or percentages.')


# ----------------------------------------------------------------------------


class DataConverter:

    def __init__(self):
        pass


    def TierToVector(self, tier, items):
        """
        Create a vector of tuples from scores of annotations of a tier.
        @param items : list of normalized labels
        """
        nb = len(items)
        v = list()

        for a in tier:
            # as tuples are imutables, we use a list.
            sc = [0.]*nb

            # get a list of tuples label/score with normalized scores
            adata = normalize_annotation(a)

            # assign real scores
            for l,s in adata:
                i = items.index(l)
                sc[i] = s

            # add into the vector of tuples
            v.append( tuple(sc) )

        return v


# ----------------------------------------------------------------------------

class Kappa:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Inter-observer variation estimation.

    Inter-observer variation can be measured in any situation in which
    two or more independent observers are evaluating the same thing.
    The Kappa statistic seems the most commonly used measure of inter-rater
    agreement in Computational Linguistics.

    Kappa is intended to give the reader a quantitative measure of the
    magnitude of agreement between observers.
    The calculation is based on the difference between how much agreement is
    actually present (“observed” agreement) compared to how much agreement
    would be expected to be present by chance alone (“expected” agreement).

    >>> p = [ (1.0,0.0) , (0.0,1.0) , (0.0,1.0) , (1.0,0.0) , (1.0,0.0) ]
    >>> q = [ (1.0,0.0) , (0.0,1.0) , (1.0,0.0) , (1.0,0.0) , (1.0,0.0) ]
    >>> kappa = Kappa(p,q)
    >>> print p, "is ok? (expect true):", kappa.check_vector(p)
    >>> print q, "is ok? (expect true):", kappa.check_vector(q)
    >>> print "Kappa value:",kappa.evaluate()

    """

    def __init__(self, p,q):
        """
        Create a Kappa instance with two lists of tuples p and q.

        Example: p=[ (1.0,0.0), (1.0,0.0), (0.8,0.2) ]
        """
        self.p = p
        self.q = q

    # End __init__
    # -----------------------------------------------------------------------


    def sqv(self):
        """
        Estimates the Euclidian distance between two vectors.

        @param p is a vector of tuples of float values
        @param q is a vector of tuples of float values
        @return v

        """

        if len(self.p) != len(self.q):
            raise Exception('Both vectors p and q must have the same length (got respectively %d and %d).'%(len(self.p),len(self.q)))

        return sum([sq(x,y) for (x,y) in zip(self.p,self.q)])

    # -----------------------------------------------------------------------

    def sqm(self):
        """
        Estimates the Euclidian distance between two vectors.
        @return row and col
        """

        if len(self.p) != len(self.q):
            raise Exception('Both vectors p and q must have the same length (got respectively %d and %d).'%(len(self.p),len(self.q)))

        row = list()
        for x in self.p:
            row.append( sum( sq(x,y) for y in self.q) )

        col = list()
        for y in self.q:
            col.append( sum( sq(y,x) for x in self.p) )

        return row,col

    # -----------------------------------------------------------------------

    def check_vector(self, v):
        """
        Check if the vector is correct to be used.

        @param v is a vector of tuples of probabilities.

        """
        # Must contain data!
        if v is None or len(v)==0:
            return False

        for t in v:
            # Must contain tuples only.
            if not type(t) is tuple:
                return False
            # All tuples have the same size (more than 1).
            if len(t) != len(v[0]) or len(t) < 2:
                return False
            # Tuple values are probabilities.
            s = 0
            for p in t:
                if p<0.0 or p>1.0:
                    return False
                s += p
            if s != 1.0: return False


        return True

    # -----------------------------------------------------------------------

    def check(self):
        """
        Check if the given p and q vectors are correct to be used.
        @return boolean

        """
        return self.check_vector(self.p) and self.check_vector(self.q)

    # -----------------------------------------------------------------------

    def evaluate(self):
        """
        Estimates the Kappa between two lists of tuples p and q.

        The tuple size corresponds to the number of categories, each value is
        the score assigned to each category for a given sample.

        """
        v = self.sqv() / float(len(self.p))
        row,col = self.sqm()
        if sum(row) != sum(col):
            raise Exception('Hum... error while estimating euclidian distances.')
        r = sum(row) / float(len(self.p)**2)

        return 1.0 - v/r

    # End evaluate
    # -----------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Tests:

if __name__ == "__main__":

    p = [ (1.0,0.0) , (0.0,1.0) , (0.0,1.0) , (1.0,0.0) , (1.0,0.0) ]
    q = [ (1.0,0.0) , (0.0,1.0) , (1.0,0.0) , (1.0,0.0) , (1.0,0.0) ]

    kappa = Kappa(p,q)
    print p, "is ok? (expect true):", kappa.check_vector(p)
    print q, "is ok? (expect true):", kappa.check_vector(q)
    print "expect false:", kappa.check_vector([ (1.0,0.0) , (0.0,2.0) , (1.0,0.0) , (1.0,0.0) , (1.0,0.0) ])
    print "expect false:", kappa.check_vector([ (1.0,0.0) , (0.0,-2.0) , (1.0,0.0) , (1.0,0.0) , (1.0,0.0) ])
    print "expect false:", kappa.check_vector([ (1.0,0.0) , (0.0) , (1.0,0.0) , (1.0,0.0) , (1.0,0.0) ])
    print "expect false:", kappa.check_vector([])

    print kappa.sqv()
    r,c = kappa.sqm()
    print "row",r
    print "col",c
    print "Kappa value:",kappa.evaluate()

    quit()
    # real life example:
    SPPAS = os.path.join(os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__) )) ), "sppas")
    sys.path.append(SPPAS)
    import annotationdata.io

    trs=annotationdata.io.read("/home/bigi/Workspace/sppas/datatest/Grenelle-Phonetic.TextGrid")
    items1 = tier_to_items( trs[4] )
    items2 = tier_to_items( trs[4] ) # ... !!! with same tier, expect kappa=1
    items = sorted(list(set(items1+items2)))
    print items

    d = DataConverter()
    k = Kappa()
    p = d.TierToVector( trs[4], items )
    q = d.TierToVector( trs[4], items )

    if k.check_vector(p) and k.check_vector(q):
        print "Grenelle: ",k.evaluate(p,q)


# ---------------------------------------------------------------------------

