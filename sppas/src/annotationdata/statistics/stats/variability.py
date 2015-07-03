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
# File: variability.py
# ----------------------------------------------------------------------------

import math
import central

# ----------------------------------------------------------------------------

"""
@authors: Brigitte Bigi
@contact: brigitte.bigi@gmail.com
@license: GPL, v3
@summary: Variability estimators.

A collection of basic statistical functions for python.

Function List
=============
    - lvariance
    - lstdev
    - lsterr
    - lz
    - lzs

"""

def lvariance (items):
    """
    Calculates the unbiased sample variance of the data values,
    using N-1 for the denominator.
    The variance is a measure of dispersion near the mean.
    @param items (list) list of data values
    @return (float)
    """
    if len(items)<2:
        return 0.
    mn = central.lmean(items)
    return sum(pow(i-mn, 2) for i in items) / (len(items)-1)


def lstdev (items):
    """
    Calculates the standard deviation of the data values, using N-1 for the denominator.
    The standard deviation is the positive square root of the variance.
    @param items (list) list of data values
    @return (float)
    """
    if len(items)<2:
        return 0.
    return math.sqrt(lvariance(items))


def lsterr(items):
    """
    Calculates the standard error of the data values.
    @param items (list) list of data values
    @return (float)
    """
    return lstdev(items) / float(math.sqrt(len(items)))


def lz (items, score):
    """
    Calculates the z-score for a given input score, given that score and the
    data values from which that score came.
    The z-score determines the relative location of a data value.
    @param items (list) list of data values
    @return (float)
    """
    return (score - central.lmean(items)) / lstdev(items)


def lzs (items):
    """
    Calculates a list of z-scores, one for each score in the data values.
    @param items (list) list of data values
    @return (list)
    """
    return [ lz(items,i) for i in items ]

# ----------------------------------------------------------------------------

if __name__=="__main__":

    import datetime

    l = [x*x for x in range(1,11)]
    print l
    print 'mean:'
    print central.lmean(l)

    print 'median:'
    print central.lmedian(l)

    print 'variance:'
    print lvariance(l)

    print 'standard deviation:'
    print lstdev(l)

