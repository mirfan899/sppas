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

    src.anndata.annloc.timedisjoint.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Localization of a serie of intervals in time.

"""
from ..anndataexc import AnnDataTypeError

from .localization import sppasBaseLocalization
from .timepoint import sppasTimePoint
from .timeinterval import sppasTimeInterval
from .duration import sppasDuration

# ---------------------------------------------------------------------------


class sppasTimeDisjoint(sppasBaseLocalization):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Representation of a serie of intervals in time.

    """
    def __init__(self, intervals):
        """ Creates a new sppasTimeDisjoint instance.

        :param intervals: (list of sppasTimeInterval)

        """
        sppasBaseLocalization.__init__(self)

        self.__intervals = list()
        self.set_intervals(intervals)

    # -----------------------------------------------------------------------

    def set(self, other):
        """ Set self members from another sppasTimeDisjoint instance.

        :param other: (sppasTimeDisjoint)

        """
        if isinstance(other, (sppasTimeDisjoint, sppasTimeInterval)) is False:
            raise AnnDataTypeError(other, "sppasTimeDisjoint, sppasTimeInterval")

        if isinstance(other, sppasTimeInterval) is False:
            self.set_intervals([other])
        else:
            self.set_intervals(other.get_intervals())

    # -----------------------------------------------------------------------

    def is_disjoint(self):
        """ Return True because self is representing a disjoint intervals. """

        return True

    # -----------------------------------------------------------------------

    def is_time_disjoint(self):
        """ Return True because self is an instance of sppasTimeDisjoint. """

        return True

    # -----------------------------------------------------------------------

    def copy(self):
        """ Return a deep copy of self. """

        intervals = list()
        for i in self.get_intervals():
            intervals.append(i.copy())

        return sppasTimeDisjoint(intervals)

    # -----------------------------------------------------------------------

    def get_begin(self):
        """ Return the first sppasTimePoint instance. """

        return min(interval.get_begin() for interval in self.__intervals)

    # -----------------------------------------------------------------------

    def set_begin(self, tp):
        """ Set the begin sppasTimePoint instance to new sppasTimePoint.

        :param tp: (sppasTimePoint)

        """
        _min = self.get_begin()
        for interval in self.__intervals:
            if interval.get_begin() == _min:
                interval.set_begin(tp)

    # -----------------------------------------------------------------------

    def get_end(self):
        """ Return the last sppasTimePoint instance. """

        return max(interval.get_end() for interval in self.__intervals)

    # -----------------------------------------------------------------------

    def set_end(self, tp):
        """ Set the end sppasTimePoint instance to new sppasTimePoint.

        :param tp: (sppasTimePoint)

        """
        _max = self.get_end()
        for interval in self.__intervals:
            if interval.get_end() == _max:
                interval.set_end(tp)

    # -----------------------------------------------------------------------

    def append_interval(self, interval):
        """ Return the sppasTimeInterval at the given index.

        :param interval: (sppasTimeInterval)

        """
        if isinstance(interval, sppasTimeInterval) is False:
            raise AnnDataTypeError(interval, "sppasTimeInterval")
        self.__intervals.append(interval)

    # -----------------------------------------------------------------------

    def get_interval(self, index):
        """ Return the sppasTimeInterval at the given index.

        :param index: (int)

        """
        return self.__intervals[index]

    # -----------------------------------------------------------------------

    def get_intervals(self):
        """ Return the list of intervals. """

        return self.__intervals

    # -----------------------------------------------------------------------

    def set_intervals(self, intervals):
        """ Set a new list of intervals.

        :param intervals: list of sppasTimeInterval.

        """
        self.__intervals = list()
        for interval in intervals:
            self.append_interval(interval)

    # -----------------------------------------------------------------------

    def duration(self):
        """ Return the sppasDuration.
         Make the sum of all interval' durations. """

        value = sum(interval.duration().get_value() for interval in self.get_intervals())
        vagueness = sum(interval.duration().get_margin() for interval in self.get_intervals())

        return sppasDuration(value, vagueness)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return "sppasTimeDisjoint: {:s}".format("".join([str(i) for i in self.get_intervals()]))

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """ Equal is required to use '==' between 2 sppasTimeDisjoint instances.
        Two disjoint instances are equals iff all its intervals are equals.

        :param other: (sppasTimeDisjoint) is the other time disjoint to compare with.

        """
        if not isinstance(other, sppasTimeDisjoint):
            return False

        if len(self) != len(other):
            return False

        return all(self.get_interval(i) == other.get_interval(i)
                   for i in range(len(self)))

    # -----------------------------------------------------------------------

    def __lt__(self, other):
        """ LowerThan is required to use '<' between 2 sppasTimeDisjoint instances.

        :param other: (sppasTimeDisjoint) is the other time point to compare with.

        """
        if isinstance(other, (sppasTimePoint, float, int)):
            return self.get_end() < other

        if isinstance(other, (sppasTimeInterval, sppasTimeDisjoint)) is False:
            return False

        return self.get_begin() < other.get_begin()

    # -----------------------------------------------------------------------

    def __gt__(self, other):
        """
        GreaterThan is required to use '>' between 2 TimeDisjoint instances.

        :param other: (sppasTimeDisjoint) is the other time point to compare with.

        """
        if isinstance(other, (int, float, sppasTimePoint)):
            return self.get_begin() > other

        if isinstance(other, (sppasTimeInterval, sppasTimeDisjoint)) is False:
            return False

        return self.get_begin() > other.get_begin()

    # -----------------------------------------------------------------------

    def __iter__(self):
        for a in self.__intervals:
            yield a

    # -----------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__intervals[i]

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__intervals)

