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
# File: descriptives.py
# ----------------------------------------------------------------------------

import stats.central
import stats.variability
import stats.moment

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
    >>> total = s.total(d)
    >>> print total['apples']
    >>> 10
    >>> print total['peers']
    >>> 13

    """

    def __init__(self, dictitems):
        """
        Descriptive statistics.

        @param dictitems (list): a list of tuple (key, values)
        """
        self.items = dictitems

    # End __init__
    # -----------------------------------------------------------------------


    def len(self):
        """
        Estimates the number of occurrences of data values.
        @return (tuple): a tuple of (key, len)
        """
        return tuple( (key, len(values)) for key,values in self.items.iteritems() )


    def total(self):
        """
        Estimates the sum of data values.
        @return (tuple): a tuple of (key, total)
        """
        return tuple( (key, sum(values)) for key,values in self.items.iteritems() )


    def mean(self):
        """
        Estimates the arithmetic mean of data values.
        @return (tuple): a tuple of (key, mean)
        """
        return tuple( (key, stats.central.lmean(values)) for key,values in self.items.iteritems() )


    def median(self):
        """
        Estimates the 'middle' score of the data values.
        @return (tuple): a tuple of (key, mean)
        """
        return tuple( (key, stats.central.lmedian(values)) for key,values in self.items.iteritems() )


    def variance(self):
        """
        Estimates the unbiased sample variance of data values.
        @return (tuple): a tuple of (key, variance)
        """
        return tuple( (key, stats.variability.lvariance(values)) for key,values in self.items.iteritems() )


    def stdev(self):
        """
        Estimates the standard deviation of data values.
        @return (tuple): a tuple of (key, stddev)
        """
        return tuple( (key, stats.variability.lstdev(values)) for key,values in self.items.iteritems() )


    def coefvariation(self):
        """
        Estimates the coefficient of variation of data values (given as a percentage).
        @return (tuple): a tuple of (key, coefvariation)
        """
        return tuple( (key, stats.moment.lvariation(values)) for key,values in self.items.iteritems() )

    # -----------------------------------------------------------------------

    def __str__(self):
        return str(self.items)
