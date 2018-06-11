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
# File: tierutils.py
# ---------------------------------------------------------------------------

import collections

from sppas import SYMBOLS
from ..tier import Tier
from ..annotation import Annotation
from ..ptime.interval import TimeInterval
from ..ptime.point import TimePoint
from ..label.label import Label

# ---------------------------------------------------------------------------


def normalize_text(text):
    return text.lower().strip()


def normalize_annotation(ann):
    """
    Create a list of tuples (label,score) from an annotation, with normalized labels.
    Raise an exception if scores of labels can not be interpreted.

    @param ann (Annotation)
    @return List of tuples
    """
    # Put all scores in a list
    scores = [t.Score for t in ann.GetLabel().GetLabels()]
    # Put all normalized labels in a list
    labels = [normalize_text(t.Value) for t in ann.GetLabel().GetLabels()]

    # Check if scores are relevant (probabilities or percentages),
    # and return the list of tuples (label,score) if they are
    probas = all( list((v >= 0. and v <= 1.) for v in scores)) and sum(scores) == 1.
    if probas:
        return [(labels[i],scores[i]) for i in range(len(scores))]

    percentage = all( list((v >= 0. and v <= 100.) for v in scores)) and sum(scores) == 100.
    if percentage:
        return [(labels[i], float(scores[i])/100.) for i in range(len(scores))]

    # hum... scores wasn't appropriate...
    raise TypeError('Expect scores as probabilities or percentages.')

# ----------------------------------------------------------------------------


def has_bound(tier, bound):
    """
    Return True if bound is part of one of the best localizations
    (alternative localizations are not tested).
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

# ---------------------------------------------------------------------------


def align2phon(aligntier, separators=SYMBOLS):
    """ Return the phonetization of a time-aligned tier.

    :param aligntier: (sppasTier)
    :param separators: (list)

    """
    phontier = Tier("Phones")
    b = TimePoint(aligntier.GetBegin().GetMidpoint())
    e = b
    l = ""
    for ann in aligntier:
        if ann.GetLabel().IsSilence() is True or ann.GetLabel().GetValue() in separators:
            if len(l) > 0 and e > b:
                at = Annotation(TimeInterval(b, e), Label(l))
                phontier.Add(at)
            phontier.Add(ann)
            b = ann.GetLocation().GetEnd()
            e = b
            l = ""
        else:
            e = ann.GetLocation().GetEnd()
            label = ann.GetLabel().GetValue()
            if ann.GetLabel().IsEmpty() is False:
                l = l + " " + label

    if e > b:
        ann = aligntier[-1]
        label = ann.GetLabel().GetValue()
        l = label.replace("-", " ")
        at = Annotation(TimeInterval(b, e), Label(l))
        phontier.Add(at)

    return phontier

# ---------------------------------------------------------------------------


class TierConverter:

    def __init__(self, tier):
        self.tier = tier

    # -----------------------------------------------------------------------

    def tier_to_counter(self):
        """
        Return a counter with label/count, with normalized labels.
        """
        labels = list()
        for ann in self.tier:
            texts = ann.GetLabel().GetLabels()
            labels.extend( normalize_text(t.GetValue()) for t in texts )

        return collections.Counter(labels)

    # -----------------------------------------------------------------------

    def tier_to_items(self):
        """
        Return the list of normalized labels.
        """
        c = self.tier_to_counter()
        return c.keys()

    # -----------------------------------------------------------------------

    def labels_to_vector(self, items):
        """
        Create a vector of tuples from the annotations of a tier.

        @param items: list of normalized labels to be used for the tuples
        @return list of tuples like for example [ (1.0,0.0), (1.0,0.0), (0.0,1.0) ] if there are 2 possible items in 3 annotations
        """
        nb = len(items)
        v = []

        for ann in self.tier:
            # sc will be the tuple for this annotation.
            # however, tuples are immutable so we use a list and we will convert later.
            sc = [0.]*nb
            # get a list of tuples label/score with normalized labels
            adata = normalize_annotation(ann)
            # assign real scores
            for l,s in adata:
                i = items.index(l)
                sc[i] = s
            # add into the vector of tuples (then, sc is converted to a tuple)
            v.append( tuple(sc) )

        return v

    # -----------------------------------------------------------------------

    def bounds_to_vector(self, othertier):
        """
        Create two vectors of tuples from the boundaries of a tier and another one.
        NOT VALIDATED.

        @param tier (Tier)
        @return p,q
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
