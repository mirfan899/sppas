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
# File: central.py
# ----------------------------------------------------------------------------

import math

# ----------------------------------------------------------------------------

"""
@authors: Brigitte Bigi
@contact: brigitte.bigi@gmail.com
@license: GPL, v3
@summary: central estimators.

A collection of basic statistical functions for python.

Function List
=============

    - fsum
    - fmult
    - fgeometricmean
    - fharmonicmean
    - fmean
    - fmedian

"""

def fsum(items):
    """
    Estimates the sum of a list of data values.

    @param items (list) list of data values
    @return (float)
    """
    return math.fsum(items)


def fmult(items):
    """
    Estimates the product of a list of data values.

    @param items (list) list of data values
    @return (float)
    """
    return reduce(lambda x, y: x*y, items)


def fgeometricmean (items):
    """
    Calculates the geometric mean of the data values:
    n-th root of (x1 * x2 * ... * xn).
    @param items (list) list of data values
    @return (float)
    """
    if not len(items): return 0.
    one_over_n = 1./len(items)
    m = 1.
    for item in items:
        m = m * pow(item,one_over_n)
    return m


def fharmonicmean (items):
    """
    Calculates the harmonic mean of the data values:
    C{n / (1/x1 + 1/x2 + ... + 1/xn)}.
    @param items (list) list of data values
    @return (float)
    """
    if not len(items): return 0.
    # create a list with 1/xi values
    s = 0.
    for item in l:
        s = s + 1./item
    return float(len(items)) / s


def fmean (items):
    """
    Calculates the arithmetic mean of the data values:
    sum(items)/len(items)
    @param items (list) list of data values
    @return (float)
    """
    if not len(items): return 0.
    return (fsum(items) / float(len(items)))


def fmedian (items):
    """
    Calculates the 'middle' score of the data values. If there is an even
    number of scores, the mean of the 2 middle scores is returned.
    @param items (list) list of data values
    @return (float)
    """
    if not len(items): return 0.
    middle = len(items) / 2

    if len(items) % 2:
        return items[ middle ]

    newlist = sorted(items)
    return float(newlist[middle] + newlist[middle-1]) / 2.


def fmin (items):
    """
    Return the minimum of the data values.
    @param items (list) list of data values
    @return (float)
    """
    if not len(items): return 0.
    return min(items)


def fmax (items):
    """
    Return the maximum of the data values.
    @param items (list) list of data values
    @return (float)
    """
    if not len(items): return 0.
    return max(items)

# ----------------------------------------------------------------------------

if __name__=="__main__":

    import datetime

    l = [x*x for x in range(1,500)]

    print 'geometricmean:'
    print datetime.datetime.now().isoformat()
    one_over_n = 1./len(l)
    m = 1.0
    for item in l:
        m = m * pow(item,one_over_n)
    print m
    print datetime.datetime.now().isoformat()
    one_over_n = 1.0/float(len(l))
    powlist = [ pow(i,one_over_n) for i in l ]
    print fmult(powlist)
    print datetime.datetime.now().isoformat()
    print

    print 'harmonician:'
    print datetime.datetime.now().isoformat()
    s = 0
    for item in l:
        s = s + 1.0/item
    print len(l)/s
    print datetime.datetime.now().isoformat()
    print fharmonicmean(l)
    print datetime.datetime.now().isoformat()
    print

    print 'mean:'
    print datetime.datetime.now().isoformat()
    s = 0
    for item in l:
        s = s + item
    print s / float(len(l))
    print datetime.datetime.now().isoformat()
    print fmean(l)
    print datetime.datetime.now().isoformat()
    print
