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
# File: tierstats.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------

from calculus.descriptivesstats import DescriptiveStatistics

# ----------------------------------------------------------------------------

class TierStats( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Estimates descriptives statistics of annotations of a tier.

    Map a tier into a dictionary where:
    - key is a label
    - value is the list of observed durations for this label

    """

    def __init__(self, tier=None, n=1, withradius=0, withalt=False):
        """
        Create a new TierStats instance.

        @param tier (either Tier or list of tiers)
        @param n (int): n-gram value
        @param withradius (int): 0 means to use Midpoint, negative value means to use R-, positive radius means to use R+
        @param withalt (boolean): Use or not use of alternative labels

        """
        self.tier         = tier
        self.__withradius = withradius
        self.__withalt    = withalt
        self.__n          = n

    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_ngram(self):
        return self.__n

    def get_withradius(self):
        return self.__withradius

    def get_withalt(self):
        return self.__withalt

    def get_tier(self):
        return self.tier

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------

    def set_withradius(self, withradius):
        """
        Set the withradius option, used to estimate the duration:
            - 0 means to use Midpoint,
            - negative value means to use R-,
            - positive radius means to use R+
        """
        self.__withradius = int(withradius)

    def set_withalt(self, withalt):
        """
        Set the withalt option, used to select the labels
            - False means to use only the label with the higher score of each annotation
            - True means to use all labels of each annotation
        """
        self.__withalt = withalt

    def set_ngram(self, n):
        """
        Set the n value of the n-grams, used to fix the history size (at least =1).
        """
        if int(n) < 1:
            raise ValueError('An n-gram must be at least of size 1, got %d'%n)
        self.__n = int(n)


    # ------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------

    def ds(self):
        """
        Create then return the DescriptiveStatistic object corresponding to the tier.
        """
        ltup  = self.__tiers_to_tuple()
        ngrams = list()
        for t in ltup:
            ngrams.extend( self.__ngrams( t ) )
        items = self.__tuple_to_dict(ngrams)
        return DescriptiveStatistics(items)

    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def __tiers_to_tuple(self):
        """
        Return a list of tuples of label/duration pairs.
        """
        tiers = self.tier
        if not isinstance(self.tier,list):
            tiers = [self.tier]

        return [ self.__tier_to_tuple(tier) for tier in tiers ]


    def __tier_to_tuple(self, tier):
        """
        Return a tuple of label/duration pairs for a given tier.
        """
        l = list()
        for a in tier:
            if self.__withalt is False:
                textes = [ a.GetLabel().GetValue() ]
            else:
                textes = [ t.GetValue() for t in a.GetLabels() ]

            duration = a.GetLocation().GetDuration().GetValue()
            if a.GetLocation().IsInterval():
                if self.__withradius < 0:
                    duration = duration + a.GetLocation().GetDuration().GetMargin()
                elif self.__withradius > 0:
                    duration = duration - a.GetLocation().GetDuration().GetMargin()

            for texte in textes:
                l.append( (texte,duration) )

        return tuple(l)


    def __ngrams(self,items):
        """
        Yield a sequences of ngrams.
        """
        l = list()
        size = len(items)
        if (size - self.__n) > 0:
            limit = size - self.__n + 1
            for i in range(limit):
                l.append( items[i:i + self.__n] )
        return l


    def __tuple_to_dict(self,items):
        """
        Convert into a dictionary.
        @param items (tuple) the ngram items
        @return: dictionary key=text, value=list of durations.
        """
        d = {}
        for item in items:
            dur = sum([i[1] for i in item])
            text = " ".join([i[0] for i in item])
            if not text in d:
                d[text] = []
            d[text].append(dur)
        return d
