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
# File: baseplacement.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__ = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

class BasePlacement(object):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, version 3
    @summary: This class represents a Generic Placement of an annotation.

    """

    def __init__(self):
        """
        Must be overridden.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------

    def __eq__(self, other):
        """
        Equal is required to use '==' between 2 placement instances.
        Two location instances are equals iff they are of the same instance
        and their values are equals.

        @param other is the other placement to compare with.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------

    def __lt__(self, other):
        """
        LowerThan is required to use '<' between 2 placement instances.

        @param  other is the other placement to compare with.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------

    def __gt__(self, other):
        """
        GreaterThan is required to use '>' between 2 placement instances.

        @param other is the other placement to compare with.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------

    def __ne__(self, other):
        return not self == other

    # ---------------------------------------------------------------------

    def __le__(self, other):
        return self < other or self == other

    # ---------------------------------------------------------------------

    def __ge__(self, other):
        return self > other or self == other

    # ---------------------------------------------------------------------

    def Duration(self):
        """
        Return the duration of this object.
        Must be overridden.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------

    def IsTimePoint(self):
        """
        Return True if this object is an instance of TimePoint.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def IsTimeInterval(self):
        """
        Return True if this object is an instance of TimeInterval.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def IsTimeDisjoint(self):
        """
        Return True if this object is an instance of TimeDisjoint.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def IsFramePoint(self):
        """
        Return True if this object is an instance of FramePoint.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def IsFrameInterval(self):
        """
        Return True if this object is an instance of FrameInterval.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def IsFrameDisjoint(self):
        """
        Return True if this object is an instance of FrameDisjoint.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------
