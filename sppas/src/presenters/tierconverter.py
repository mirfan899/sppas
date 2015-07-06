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
# File: tierconverter.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

import collections

# ----------------------------------------------------------------------------

def normalize_text(text):
    return text.lower().strip()

def normalize_annotation(ann):
    scores = [ t.Score for t in ann.GetLabel().GetLabels() ]
    labels = [ normalize_text(t.Value) for t in ann.GetLabel().GetLabels() ]

    probas = all( list( (v>=0. and v<=1.) for v in scores) ) and sum(scores)==1.
    if probas: return [ (labels[i],scores[i]) for i in range(len(scores)) ]

    percentage = all( list( (v>=0. and v<=100.) for v in scores)) and sum(scores)==100.
    if percentage: return [ (labels[i],float(scores[i])/100.) for i in range(len(scores)) ]

    raise TypeError('Expect scores as probabilities or percentages.')


def has_bound(tier, bound):
    """
    Return True if bound is part of one of the best localizations.
    """
    if tier.IsPoint():
        i = tier.Index( bound )
        if i == -1:
            return False
        return True

    for a in tier:
        if a.GetLocation().GetBegin() == bound or a.GetLocation().GetEnd() == bound:
            return True
    return False

# ----------------------------------------------------------------------------


class TierConverter:

    def __init__(self, tier):
        self.tier = tier

    # -----------------------------------------------------------------------

    def tier_to_counter(self):
        """
        Return a counter with label/count.
        """
        labels = list()
        for a in self.tier:
            texts = a.GetLabel().GetLabels()
            labels.extend(normalize_text(t.GetValue()) for t in texts )

        return collections.Counter(labels)

    # -----------------------------------------------------------------------

    def tier_to_items(self):
        c = self.tier_to_counter()
        return c.keys()

    # -----------------------------------------------------------------------

    def labels_to_vector(self, items):
        """
        Create a vector of tuples from the annotations of a tier.

        @param items: list of normalized labels to be used for the tuples

        """
        nb = len(items)
        v = []

        for a in self.tier:
            # because tuples are immutable, we use a list.
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

    # -----------------------------------------------------------------------

    def bounds_to_vector(self, othertier):
        """
        Create two vectors of tuples from the boundaries of a tier and another one.

        """
        p = []
        q = []

        listone = self.tier.GetAllPoints()
        listtwo = othertier.GetAllPoints()

        for point in list(set(listone + listtwo)):
            b1 = float( has_bound( self.tier, point ) )
            b2 = float( has_bound( othertier, point ) )
            p.append( (b1,1.-b1) )
            q.append( (b2,1.-b2) )

        return (p,q)

# ----------------------------------------------------------------------------
