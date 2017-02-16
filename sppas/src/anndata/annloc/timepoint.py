# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.anndata.annloc.timepoint.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Localization of a point in time.

"""
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AnnDataNegValueError

from .localization import sppasBaseLocalization
from .duration import sppasDuration

# ---------------------------------------------------------------------------


class sppasTimePoint(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Point in time.
    Represents a time point identified by a time value and a radius value.
    Generally, time is represented in seconds, as a float value.

    In the sppasTimePoint instance, the 3 relations <, = and > take into
    account a radius value, that represents the uncertainty of the
    localization. For a point x, with a radius value of dx, and a point y
    with a radius value of dy, these relations are defined as:
        - x = y iff |x - y| <= dx + dy
        - x < y iff not(x = y) and x < y
        - x > y iff not(x = y) and x > y

    Examples:

        - Strictly equals:

            - x = 1.000, dx=0.
            - y = 1.000, dy=0.
            - x = y is true

            - x = 1.00000000000, dx=0.
            - y = 0.99999999675, dy=0.
            - x = y is false

        - Using the radius:

            - x = 1.0000000000, dx=0.0005
            - y = 1.0000987653, dx=0.0005
            - x = y is true  (accept a margin of 1ms between x and y)

            - x = 1.0000000, dx=0.0005
            - y = 1.0011235, dx=0.0005
            - x = y is false

    """
    def __init__(self, time_value, radius=0.0):
        """ Create a sppasLocTimePoint instance.

        :param time_value: (float) time value in seconds.
        :param radius: (float) represents the vagueness of the point.

        """
        self.__midpoint = 0.
        self.__radius = 0.

        self.set_midpoint(time_value)
        self.set_radius(radius)

    # -----------------------------------------------------------------------

    def get_midpoint(self):
        """ Return the time value (float) of the midpoint. """

        return self.__midpoint

    # -----------------------------------------------------------------------

    def set_midpoint(self, value):
        """ Set the time point to a new midpoint value.

        :param value: (float) is the new time to set the midpoint.

        """
        try:
            self.__midpoint = float(value)
            if self.__midpoint < 0.:
                self.__midpoint = 0.
                raise AnnDataNegValueError(value)
        except TypeError:
            raise AnnDataTypeError(value, "float")

    # -----------------------------------------------------------------------

    def get_radius(self):
        """ Return the radius value (float). """

        return self.__radius

    # -----------------------------------------------------------------------

    def set_radius(self, value):
        """ Fix the radius value, ie. the vagueness of the TimePoint.

        :param value: (float) the radius value

        """
        try:
            value = float(value)
            if value < 0.:
                raise AnnDataNegValueError(value)
        except TypeError:
            raise AnnDataTypeError(value, "float")

        if self.__midpoint < value:
            value = self.__midpoint

        self.__radius = value

    # -----------------------------------------------------------------------

    def duration(self):
        """ Overrides. Return the duration of the time point.

        :returns: (sppasDuration) Duration and its vagueness.

        """
        return sppasDuration(0., 2.0*self.get_radius())

    # -----------------------------------------------------------------------

    def __repr__(self):
        return "sppasTimePoint: {:f}, {:f}".format(self.get_midpoint(), self.get_radius())

    # -----------------------------------------------------------------------

    def __str__(self):
        return "({:f}, {:f})".format(self.get_midpoint(), self.get_radius())

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """ Equal is required to use '==' between 2 TimePoint instances or
        between a TimePoint and an other object representing time.
        This relationship takes into account the radius.

        :param other: (sppasTimePoint, float, int) is the other time point to compare with.

        """
        if isinstance(other, (int, float, sppasTimePoint)) is False:
            return False

        if isinstance(other, sppasTimePoint) is True:
            delta = abs(self.__midpoint - other.get_midpoint())
            radius = self.__radius + other.get_radius()
            return delta <= radius

        if isinstance(other, (int, float)):
            delta = abs(self.__midpoint - other)
            radius = self.__radius
            return delta <= radius

    # -----------------------------------------------------------------------

    def __lt__(self, other):
        """
        LowerThan is required to use '<' between 2 TimePoint instances
        or between a TimePoint and an other time object.

        :param other: (sppasTimePoint, float, int) is the other time point to compare with.

        """
        if isinstance(other, sppasTimePoint) is True:
            return self != other and self.__midpoint < other.get_midpoint()

        return (self != other) and (self.__midpoint < other)

    # -----------------------------------------------------------------------

    def __gt__(self, other):
        """ GreaterThan is required to use '>' between 2 TimePoint instances
        or between a TimePoint and an other time object.

        :param other: (sppasTimePoint, float, int) is the other time point to compare with.

        """
        if isinstance(other, sppasTimePoint) is True:
            return self != other and self.__midpoint > other.get_midpoint()

        return (self != other) and (self.__midpoint > other)

    # ------------------------------------------------------------------------

    def __ne__(self, other):
        """ Not equals. """
        return not (self == other)

    # ------------------------------------------------------------------------

    def __le__(self, other):
        """ Lesser or equal. """
        return (self < other) or (self == other)

    # ------------------------------------------------------------------------

    def __ge__(self, other):
        """ Greater or equal. """
        return (self > other) or (self == other)

# ---------------------------------------------------------------------------


class sppasLocTimePoint(sppasBaseLocalization, sppasTimePoint):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Representation of a localization as a single time point.

    """
    def __init__(self, time_value, radius=0.0, score=1.):
        """ Create a sppasLocTimePoint instance.

        :param time_value: (float) time value in seconds.
        :param radius: (float) represents the vagueness of the point.
        :param score: (float) localization score.

        """
        sppasBaseLocalization.__init__(self, score)
        sppasTimePoint.__init__(self, time_value, radius)

    # -----------------------------------------------------------------------

    def get(self):
        """ Return myself. """

        return self

    # -----------------------------------------------------------------------

    def set(self, other):
        """ Set self members from another sppasTimePoint instance.

        :param other: (sppasLocTimePoint)

        """
        if isinstance(other, sppasLocTimePoint) is False:
            raise AnnDataTypeError(other, "sppasLocTimePoint")

        self.set_midpoint(other.get_midpoint())
        self.set_radius(other.get_radius())
        self.set_score(other.get_score())

    # -----------------------------------------------------------------------

    def is_point(self):
        """ Overrides. Return True, because self is representing a point. """

        return True

    # -----------------------------------------------------------------------

    def is_time_point(self):
        """ Overrides. Return True, because self is a point as time value. """

        return True

    # -----------------------------------------------------------------------

    def copy(self):
        """ Return a deep copy of self. """

        t = self.get_midpoint()
        r = self.get_radius()
        s = self.get_score()
        return sppasLocTimePoint(t, r, s)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return "sppasLocTimePoint: {:f}, {:f} (score={:f})".format(self.get_midpoint(),
                                                                   self.get_radius(),
                                                                   self.get_score())

    # -----------------------------------------------------------------------

    def __str__(self):
        return "({:f}, {:f}, {:f})".format(self.get_midpoint(),
                                           self.get_radius(),
                                           self.get_score())

    # -----------------------------------------------------------------------
