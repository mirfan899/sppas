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
# File: variability.py
# ----------------------------------------------------------------------------

import math

from .central import fmean
from .central import fsum
from .central import fmedian

# ----------------------------------------------------------------------------

"""
@author:       Brigitte Bigi
@organization: Laboratoire Parole et Langage, Aix-en-Provence, France
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2011-2016  Brigitte Bigi
@summary:      Variability estimators.

A collection of basic statistical functions for python.

Function List
=============
    - lvariance
    - lstdev
    - lsterr
    - lz
    - lzs

"""

# ----------------------------------------------------------------------------

def lunbiasedvariance (items):
    """
    Calculates the unbiased sample variance of the data values,
    using N-1 for the denominator.
    The variance is a measure of dispersion near the mean.

    @param items (list) list of data values
    @return (float)

    """
    if len(items) < 2:
        return 0.
    mn = fmean(items)
    return fsum(pow(i-mn, 2) for i in items) / (len(items)-1)

# ----------------------------------------------------------------------------

def lvariance (items):
    """
    Calculates the variance of the data values,
    using N for the denominator.
    The variance is a measure of dispersion near the mean.

    @param items (list) list of data values
    @return (float)

    """
    if len(items)<2:
        return 0.
    mn = fmean(items)
    return fsum(pow(i-mn, 2) for i in items) / (len(items))

# ----------------------------------------------------------------------------

def lunbiasedstdev (items):
    """
    Calculates the standard deviation of the data values, using N-1 for the denominator.
    The standard deviation is the positive square root of the variance.

    @param items (list) list of data values
    @return (float)

    """
    if len(items)<2:
        return 0.
    return math.sqrt(lunbiasedvariance(items))

# ----------------------------------------------------------------------------

def lstdev (items):
    """
    Calculates the standard deviation of the data values, using N for the denominator.
    The standard deviation is the positive square root of the variance.

    @param items (list) list of data values
    @return (float)

    """
    if len(items)<2:
        return 0.
    return math.sqrt(lvariance(items))

# ----------------------------------------------------------------------------

def lsterr(items):
    """
    Calculates the standard error of the data values.

    @param items (list) list of data values
    @return (float)

    """
    return lstdev(items) / float(math.sqrt(len(items)))

# ----------------------------------------------------------------------------

def lz (items, score):
    """
    Calculates the z-score for a given input score, given that score and the
    data values from which that score came.
    The z-score determines the relative location of a data value.

    @param items (list) list of data values
    @param score (float) a score of any items
    @return (float)

    """
    if len(items)<2:
        return 0.
    return (score - fmean(items)) / lstdev(items)

# ----------------------------------------------------------------------------

def lzs (items):
    """
    Calculates a list of z-scores, one for each score in the data values.

    @param items (list) list of data values
    @return (list)

    """
    return [ lz(items,i) for i in items ]

# ----------------------------------------------------------------------------

def rPVI(items):
    """
    Calculates the Raw Pairwise Variability Index.

    @param items (list) list of data values
    @return (float)

    """
    if len(items)<2:
        return 0.
    n = len(items)-1
    sumd = fsum( [ math.fabs(items[i]-items[i+1]) for i in range(n) ]  )
    return sumd / n

# ----------------------------------------------------------------------------

def nPVI(items):
    """
    Calculates the Normalized Pairwise Variability Index.

    @param items (list) list of data values
    @return (float)

    """
    if len(items)<2:
        return 0.
    n = len(items)-1
    sumd = 0.
    for i in range(n):
        d1 = items[i]
        d2 = items[i+1]
        delta = math.fabs(d1 - d2)
        meand = (d1 + d2) / 2.
        sumd += delta / meand

    return 100. * sumd / n

# ----------------------------------------------------------------------------

if __name__=="__main__":

    l = [x*x for x in range(1,11)]
    print(l)
    print('mean:',fmean(l))
    print('median:',fmedian(l))
    print('variance:',lvariance(l))
    print('standard deviation:',lstdev(l))
    print('rPVI:',rPVI(l))
    print('nPVI:',nPVI(l))
