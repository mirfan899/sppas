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
# File: descriptivesstats.py
# ----------------------------------------------------------------------------

import stats.central
import stats.variability
import stats.moment
from types import FunctionType

# ----------------------------------------------------------------------------

class DescriptiveStatistics( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Descriptives statistics estimator class.

    This class estimates descriptives statistics on a set of data values,
    stored in a dictionary:
    - key is the name of the data set;
    - value is the list of data values for this data set.

    >>> d = { 'apples':[1,2,3,4] , 'peers':[2,3,3,5] }
    >>> s = DescriptiveStatistics(d)
    >>> total = s.total()
    >>> print total
    >>> (('peers', 13.0), ('apples', 10.0))

    """

    def __init__(self, dictitems):
        """
        Descriptive statistics.

        @param dictitems: a dict of tuples (key, [values])
        """
        self.items = dictitems

    # -----------------------------------------------------------------------

    def len(self):
        """
        Estimates the number of occurrences of data values.
        @return (dict): a dictionary of (key, len)
        """
        return dict( (key, len(values)) for key,values in self.items.iteritems() )


    def total(self):
        """
        Estimates the sum of data values.
        @return (dict): a dictionary of (key, total) of float values
        """
        return dict( (key, stats.central.fsum(values)) for key,values in self.items.iteritems() )


    def min(self):
        """
        Returns the minimum of data values.
        @return (dict): a dictionary of (key, min) of float values
        """
        return dict( (key, stats.central.fmin(values)) for key,values in self.items.iteritems() )


    def max(self):
        """
        Returns the maximum of data values.
        @return (dict): a dictionary of (key, max) of float values
        """
        return dict( (key, stats.central.fmax(values)) for key,values in self.items.iteritems() )


    def mean(self):
        """
        Estimates the arithmetic mean of data values.
        @return (dict): a dictionary of (key, mean) of float values
        """
        return dict( (key, stats.central.fmean(values)) for key,values in self.items.iteritems() )


    def median(self):
        """
        Estimates the 'middle' score of the data values.
        @return (dict): a dictionary of (key, mean) of float values
        """
        return dict( (key, stats.central.fmedian(values)) for key,values in self.items.iteritems() )


    def variance(self):
        """
        Estimates the unbiased sample variance of data values.
        @return (dict): a dictionary of (key, variance) of float values
        """
        return dict( (key, stats.variability.lvariance(values)) for key,values in self.items.iteritems() )


    def stdev(self):
        """
        Estimates the standard deviation of data values.
        @return (dict): a dictionary of (key, stddev) of float values
        """
        return dict( (key, stats.variability.lstdev(values)) for key,values in self.items.iteritems() )


    def coefvariation(self):
        """
        Estimates the coefficient of variation of data values (given as a percentage).
        @return (dict): a dictionary of (key, coefvariation) of float values
        """
        return dict( (key, stats.moment.lvariation(values)) for key,values in self.items.iteritems() )

    # -----------------------------------------------------------------------

    def zscore(self):
        """
        Estimates the z-scores of data values.
        The z-score determines the relative location of a data value.
        @return (dict): a dictionary of (key, [z-scores]) of float values
        """
        return dict( (key, stats.variability.lzs(values)) for key,values in self.items.iteritems() )


# ----------------------------------------------------------------------------
