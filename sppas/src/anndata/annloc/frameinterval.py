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

    src.anndata.annloc.frameinterval.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Localization of an interval in number of frames or rank.

"""
import logging
from ..anndataexc import AnnDataTypeError
from ..anndataexc import IntervalBoundsError

from .localization import sppasBaseLocalization
from .framepoint import sppasFramePoint
from .duration import sppasDuration

# ---------------------------------------------------------------------------


class sppasFrameInterval(sppasBaseLocalization):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Representation of a localization as an interval.

    """
    def __init__(self, begin, end):
        """ Create a new sppasFrameInterval instance.

        :param begin: (sppasFramePoint) start frame
        :param end: (sppasFramePoint) end frame

        """
        sppasBaseLocalization.__init__(self)

        if isinstance(begin, sppasFramePoint) is False:
            AnnDataTypeError(begin, "sppasFramePoint")

        if isinstance(end, sppasFramePoint) is False:
            AnnDataTypeError(end, "sppasFramePoint")

        if begin.get_midpoint() >= end.get_midpoint() or (
                begin.get_midpoint() - begin.get_radius() >
                end.get_midpoint() - end.get_radius()):
            raise IntervalBoundsError(begin, end)
        elif begin >= end:
            logging.info('[WARNING] begin >= end with ({!s:s}, {!s:s})'.format(begin, end))

        self.__begin = begin
        self.__end = end

    # -----------------------------------------------------------------------

    def set(self, other):
        """ Set self members from another sppasFramePoint instance.

        :param other: (sppasFramePoint)

        """
        if isinstance(other, sppasFrameInterval) is False:
            raise AnnDataTypeError(other, "sppasFrameInterval")

        self.set_begin(other.get_begin())
        self.set_end(other.get_end())

    # -----------------------------------------------------------------------

    def is_interval(self):
        """ Overrides. Return True, because self is representing an interval. """

        return True

    # -----------------------------------------------------------------------

    def is_frame_interval(self):
        """ Overrides. Return True, because self is an interval of frames. """

        return True

    # -----------------------------------------------------------------------

    def copy(self):
        """ Return a deep copy of self. """

        b = self.get_begin()
        e = self.get_end()
        return sppasFrameInterval(b, e)

    # -----------------------------------------------------------------------

    def get_begin(self):
        """ Return the begin sppasTimePoint instance. """

        return self.__begin

    # -----------------------------------------------------------------------

    def set_begin(self, tp):
        """ Set the begin of the interval instance to a new sppasFramePoint.
        Attention: it is a reference assignment.

        :param tp: (sppasFramePoint)

        """
        if isinstance(tp, sppasFramePoint) is False:
            raise AnnDataTypeError(tp, "sppasFramePoint")

        if tp.get_midpoint() >= self.__end.get_midpoint() or \
                (tp.get_midpoint() - tp.get_radius() >
                self.__end.get_midpoint() - self.__end.get_radius()):
            raise IntervalBoundsError(tp, self.__end)

        self.__begin = tp  # assign the reference

    # -----------------------------------------------------------------------

    def get_end(self):
        """ Return the end sppasFramePoint instance. """

        return self.__end

    # -----------------------------------------------------------------------

    def set_end(self, tp):
        """ Set the end of the interval to a new sppasFramePoint.
        Attention: it is a reference assignment.

        :param tp: (sppasTimePoint)

        """
        if isinstance(tp, sppasFramePoint) is False:
            raise AnnDataTypeError(tp, "sppasFramePoint")

        if self.__begin.get_midpoint() >= tp.get_midpoint() or \
                (self.__begin.get_midpoint() - self.__begin.get_radius() >
                tp.get_midpoint() - tp.get_radius()):
            raise IntervalBoundsError(self.__begin, tp)

        # assign the reference
        self.__end = tp

    # -----------------------------------------------------------------------

    def combine(self, other):
        """ Return a sppasFrameInterval, the combination of two intervals.

        :param other: (sppasFrameInterval) is the other interval
        to be combined with.

        """
        if isinstance(other, sppasFrameInterval) is False:
            AnnDataTypeError(other, "sppasFrameInterval")

        if self > other:
            other, self = self, other

        if self.__end <= other.get_begin():
            return sppasFrameInterval(self.__begin, other.get_end())

        return sppasFrameInterval(other.get_begin(), self.__end)

    # -----------------------------------------------------------------------

    def union(self, other):
        """ Return a sppasFrameInterval representing the union of two intervals.

        :param other: (sppasFrameInterval) is the interval to merge with.

        """
        if isinstance(other, sppasFrameInterval) is False:
            AnnDataTypeError(other, "sppasFrameInterval")

        if self > other:
            other, self = self, other

        return sppasFrameInterval(self.__begin, other.get_end())

    # -----------------------------------------------------------------------

    def duration(self):
        """ Overrides. Return the duration of the interval in number of frames.

        :returns: (sppasDuration) Duration and its vagueness.

        """
        # duration is the difference between the midpoints
        value = self.get_end().get_midpoint() - self.get_begin().get_midpoint()
        # vagueness of the duration is based on begin/end radius values
        vagueness = self.get_begin().get_radius() + self.get_end().get_radius()

        return sppasDuration(value, vagueness)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return "sppasFrameInterval: [{:s},{:s}]".format(self.get_begin(), self.get_end())

    def __str__(self):
        return "[{:s},{:s}]".format(self.get_begin(), self.get_end())

    # -----------------------------------------------------------------------

    def __contains__(self, tp):
        """ Return True if the given time point is contained in the interval.

        :param tp: the time point to verify.

        """
        if isinstance(tp, (sppasFrameInterval, sppasFramePoint, int,)) is False:
            raise AnnDataTypeError(tp, "sppasFrameInterval, sppasFramePoint, int")

        if isinstance(tp, sppasFrameInterval):
            return (self.__begin <= tp.get_begin() and
                    tp.get_end() <= self.__end)

        return self.__begin <= tp <= self.__end

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """ Equal.

        :param other: (sppasFrameInterval) the other interval to compare with.

        """
        if isinstance(other, sppasFrameInterval) is False:
            return False

        return (self.__begin == other.get_begin() and
                self.__end == other.get_end())

    # -----------------------------------------------------------------------

    def __lt__(self, other):
        """ LowerThan.

        :param other: (sppasFrameInterval, sppasFramePoint, int) the other to compare with.

        """
        if isinstance(other, (sppasFramePoint, int)):
            return self.__end < other

        if isinstance(other, sppasFrameInterval) is False:
            return False

        return self.__begin < other.get_begin()

    # -----------------------------------------------------------------------

    def __gt__(self, other):
        """ GreaterThan.

        :param other: (sppasFrameInterval, sppasFramePoint, int) the other to compare with.

        """
        if isinstance(other, (int, sppasFramePoint)):
            return self.__begin > other

        if isinstance(other, sppasFrameInterval) is False:
            return False

        return self.__begin > other.get_begin()
