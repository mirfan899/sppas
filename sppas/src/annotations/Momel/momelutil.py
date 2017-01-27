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
# File: momelutil.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

from random import randrange


def quicksortcib(ciblist):
    """ Implement quicksort (ie "partition-exchange" sort).
        that makes on average, O(n log n) comparisons to sort n items.
        This solution benefits from "list comprehensions", which keeps
        the syntax concise and easy to read.
        Quicksort dedicated to a list of Targets.
    """
    # an empty list is already sorted, so just return it
    if ciblist == []:
        return ciblist

    # Select a random pivot value and remove it from the list
    pivot = ciblist.pop( randrange(len(ciblist)) )
    # Filter all items less than the pivot and quicksort them
    lesser = quicksortcib([l for l in ciblist if l.get_x() < pivot.get_x()])
    # Filter all items greater than the pivot and quicksort them
    greater = quicksortcib([l for l in ciblist if l.get_x() >= pivot.get_x()])
    # Return the sorted results
    return lesser + [pivot] + greater

# ----------------------------------------------------------------------


def compare(val1, val2, seuil=0.05):
    """ Comparaison selon cle de 2 val de cibles.
        Return:
            - 0 si val1 et val2 sont considerees comme egales
            - 1 si val1 > val2
            - -1 si val1 < val2
    """
    if (val1 - val2)/val1 > seuil:
        return 1
    elif (val2 - val1)/val1 > seuil:
        return -1

    return 0

# ----------------------------------------------------------------------
