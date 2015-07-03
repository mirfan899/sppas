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
# File: moment.py
# ----------------------------------------------------------------------------

import central
import variability

# ----------------------------------------------------------------------------

"""
@authors: Brigitte Bigi
@contact: brigitte.bigi@gmail.com
@license: GPL, v3
@summary: Moment estimators.

A collection of basic statistical functions for python.

Function List
=============

    - lmoment
    - lvariation
    - lskew
    - lkurtosis

"""

def lmoment(items,moment=1):
    """
    Calculates the r-th moment about the mean for a sample:
    1/n * SUM((items(i)-mean)**r)
    @param items (list) list of data values
    @return (float)
    """
    if moment == 1:
        return 0.
    mn = central.lmean(items)
    momentlist = [ (i-mn)**moment for i in items ]
    return sum(momentlist) / float(len(items))


def lvariation(items):
    """
    Calculates the coefficient of variation of data values.
    It shows the extent of variability in relation to the mean.
    It's a standardized measure of dispersion: stdev / mean and returned as a percentage.
    @param items (list) list of data values
    @return (float)
    """
    return variability.lstdev(items) / float(central.lmean(items)) * 100.


def lskew(items):
    """
    Calculates the skewness of a distribution.
    The skewness represents a measure of the asymmetry: an understanding
    of the skewness of the dataset indicates whether deviations from the
    mean are going to be positive or negative.
    @param items (list) list of data values
    @return (float)
    """
    return lmoment(items,3) / pow(lmoment(items,2),1.5)


def lkurtosis(items):
    """
    Returns the kurtosis of a distribution.
    The kurtosis represents a measure of the "peakedness":
    a high kurtosis distribution has a sharper peak and fatter tails,
    while a low kurtosis distribution has a more rounded peak and thinner
    tails.
    @param items (list) list of data values
    @return (float)
    """
    return lmoment(items,4) / pow(lmoment(items,2),2.0)


# ----------------------------------------------------------------------------

if __name__=="__main__":

    import datetime

    l = [x*x for x in range(1,500)]

    print 'moment:'
    print datetime.datetime.now().isoformat()
    moment = 10
    mn = central.lmean(l)
    s = 0
    for x in l:
        s = s + (x-mn)**moment
    print s/float(len(l))

    print datetime.datetime.now().isoformat()
    print lmoment(l,moment)
    print datetime.datetime.now().isoformat()
    print

