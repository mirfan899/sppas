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
# File: distances.py
# ----------------------------------------------------------------------------

"""
@author:       Brigitte Bigi
@organization: Laboratoire Parole et Langage, Aix-en-Provence, France
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2011-2016  Brigitte Bigi
@summary:      Distance estimators.

A collection of basic distance functions for python.

Function List
=============
    - squared_euclidian

"""

def squared_euclidian(x, y):
    """
    Estimates the Squared Euclidian distance between two tuples.

    @param x is a tuple of float values
    @param y is a tuple of float values

    x and y must have the same length.

    >>> x=(1.0,0.0)
    >>> y=(0.0,1.0)
    >>> squared_euclidian(x,y)
    >>> 2.0

    """
    if len(x) != len(y):
        raise Exception('Both x and y must have the same length (got respectively %d and %d).'%(len(x),len(y)))

    return sum( [(a-b)**2 for (a,b) in zip(x,y)] )

# -----------------------------------------------------------------------
