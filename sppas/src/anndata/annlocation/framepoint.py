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

    src.anndata.annloc.framepoint.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Localization of a point in number of frames or rank.

"""
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AnnDataNegValueError

from .localization import sppasBaseLocalization
from .duration import sppasDuration

# ---------------------------------------------------------------------------


class sppasFramePoint(sppasBaseLocalization):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Point in number of frames or rank.
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

            - x = 3, dx=0.
            - y = 3, dy=0.
            - x = y is true

            - x = 3, dx=0.
            - y = 2, dy=0.
            - x = y is false

        - Using the radius:
            - x = 3, dx=1.
            - y = 2, dy=0.
            - x = y is true (due to a vagueness of 1 frame around x)

    """
    def __init__(self, frame_value, radius=0):
        """ Create a sppasFramePoint instance.

        :param frame_value: (int) value of the rank or frame.
        :param radius: (int) represents the vagueness of the point.

        """
        sppasBaseLocalization.__init__(self)

        self.__midpoint = 0
        self.__radius = 0

        self.set_midpoint(frame_value)
        self.set_radius(radius)

    # -----------------------------------------------------------------------

    def set(self, other):
        """ Set self members from another sppasFramePoint instance.

        :param other: (sppasFramePoint)

        """
        if isinstance(other, sppasFramePoint) is False:
            raise AnnDataTypeError(other, "sppasFramePoint")

        self.set_midpoint(other.get_midpoint())
        self.set_radius(other.get_radius())

    # -----------------------------------------------------------------------

    def is_point(self):
        """ Overrides. Return True, because self is representing a point. """

        return True

    # -----------------------------------------------------------------------

    def is_frame_point(self):
        """ Overrides. Return True, because self is a point as rank value. """

        return True

    # -----------------------------------------------------------------------

    def copy(self):
        """ Return a deep copy of self. """

        t = self.get_midpoint()
        r = self.get_radius()
        return sppasFramePoint(t, r)

    # -----------------------------------------------------------------------

    def get_midpoint(self):
        """ Return the value (int) of the midpoint. """

        return self.__midpoint

    # -----------------------------------------------------------------------

    def set_midpoint(self, value):
        """ Set the midpoint value.

        :param value: (int) new rank to set the midpoint.

        """
        try:
            self.__midpoint = int(value)
            if self.__midpoint < 0:
                self.__midpoint = 0
                raise AnnDataNegValueError(value)
        except TypeError:
            raise AnnDataTypeError(value, "int")

    # -----------------------------------------------------------------------

    def get_radius(self):
        """ Return the radius value (int). """

        return self.__radius

    # -----------------------------------------------------------------------

    def set_radius(self, value):
        """ Fix the radius value, ie. the vagueness of the point.

        :param value: (float) the radius value

        """
        try:
            value = int(value)
            if value < 0:
                raise AnnDataNegValueError(value)
        except TypeError:
            raise AnnDataTypeError(value, "int")

        if self.__midpoint < value:
            value = self.__midpoint

        self.__radius = value

    # -----------------------------------------------------------------------

    def duration(self):
        """ Overrides. Return the duration of the point.

        :returns: (sppasDuration) Duration and its vagueness.

        """
        return sppasDuration(0, 2*self.get_radius())

    # -----------------------------------------------------------------------

    def __repr__(self):
        return "sppasFramePoint: {:d}, {:d}".format(self.get_midpoint(), self.get_radius())

    # -----------------------------------------------------------------------

    def __str__(self):
        return "({:d}, {:d})".format(self.get_midpoint(), self.get_radius())

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """ Equal is required to use '==' between 2 sppasFramePoint instances or
        between a sppasFramePoint and an other object representing a rank or a frame.
        This relationship takes into account the radius.

        :param other: (sppasFramePoint, int) the other point to compare with.

        """
        if isinstance(other, sppasFramePoint) is True:
            delta = abs(self.get_midpoint() - other.get_midpoint())
            radius = self.get_radius() + other.get_radius()
            return delta <= radius

        if isinstance(other, int):
            delta = abs(self.get_midpoint() - other)
            radius = self.get_radius()
            return delta <= radius

        return False

    # -----------------------------------------------------------------------

    def __lt__(self, other):
        """ LowerThan is required to use '<' between 2 sppasFramePoint instances
        or between a sppasFramePoint and an other rank value.

        :param other: (sppasFramePoint, int) the other point to compare with.

        """
        if isinstance(other, sppasFramePoint) is True:
            return self != other and self.__midpoint < other.get_midpoint()

        return (self != other) and (self.__midpoint < other)

    # -----------------------------------------------------------------------

    def __gt__(self, other):
        """ GreaterThan is required to use '>' between 2 sppasFramePoint instances
        or between a sppasFramePoint and an other rank value.

        :param other: (sppasFramePoint, int) the other point to compare with.

        """
        if isinstance(other, sppasFramePoint) is True:
            return self != other and self.__midpoint > other.get_midpoint()

        return (self != other) and (self.__midpoint > other)

