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

    src.anndata.filter.allen.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This class was inspired by the "Allen's Interval Algebra" and INDU.

    James Allen, in 1983, proposed an algebraic framework named Interval
    Algebra (IA), for qualitative reasoning with time intervals where the
    binary relationship between a pair of intervals is represented  by a
    subset of 13 atomic relation, that are:

      - distinct because no pair of definite intervals can be related
      by more than one of the relationships;

      - exhaustive because any pair of definite intervals are described
      by one of the relations;

      - qualitative (rather than quantitative) because no numeric time
      spans are considered.

    These relations and the operations on them form "Allen's Interval Algebra".
    Using this calculus, given facts can be formalized and then used for
    automatic reasoning.

    Pujari, Kumari and Sattar proposed INDU in 1999: an Interval & Duration
    network. They extended the IA to model qualitative information about
    intervals and durations in a single binary constraint network.
    INDU comprises of 25 basic relations between a pair of two intervals.

    List of relations implemented in this class:

            'before'
            'before_eq'
            'before_ge'
            'before_gt'
            'before_le'
            'before_lt'
            'after'
            'after_eq'
            'after_ge'
            'after_gt'
            'after_le'
            'after_lt'
            'meets'
            'meets_eq'
            'meets_ge'
            'meets_gt'
            'meets_le'
            'meets_lt'
            'metby'
            'metby_eq'
            'metby_ge'
            'metby_gt'
            'metby_le'
            'metby_lt'
            'overlaps'
            'overlaps_eq'
            'overlaps_ge'
            'overlaps_gt'
            'overlaps_le'
            'overlaps_lt'
            'overlappedby'
            'overlappedby_eq'
            'overlappedby_ge'
            'overlappedby_gt'
            'overlappedby_le'
            'overlappedby_lt'
            'starts'
            'startedby'
            'contains'
            'during'
            'finishes'
            'finishedby'
            'disjoint'
            'convergent'
            'equals'

"""
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AnnDataValueError
from ..anndataexc import AnnDataNegValueError
from ..basecompare import sppasBaseCompare

from .point import sppasPoint
from .interval import sppasInterval
from .disjoint import sppasDisjoint

# ---------------------------------------------------------------------------


class sppasIntervalCompare(sppasBaseCompare):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS implementation of interval'comparisons.

    Includes "Allen's Interval Algebra", with several options.

    """
    def __init__(self):
        """ Create a sppasIntervalCompare instance. """

        sppasBaseCompare.__init__(self)

        self.methods['before'] = sppasIntervalCompare.before
        self.methods['before_eq'] = sppasIntervalCompare.before_eq
        self.methods['after'] = sppasIntervalCompare.after
        self.methods['meets'] = sppasIntervalCompare.meets
        self.methods['metby'] = sppasIntervalCompare.metby
        self.methods['overlaps'] = sppasIntervalCompare.overlaps
        self.methods['overlappedby'] = sppasIntervalCompare.overlappedby
        self.methods['starts'] = sppasIntervalCompare.starts
        self.methods['startedby'] = sppasIntervalCompare.startedby
        self.methods['finishes'] = sppasIntervalCompare.finishes
        self.methods['finishedby'] = sppasIntervalCompare.finishedby
        self.methods['during'] = sppasIntervalCompare.during
        self.methods['contains'] = sppasIntervalCompare.contains
        self.methods['equals'] = sppasIntervalCompare.equals

    # ---------------------------------------------------------------------------

    @staticmethod
    def before(i1, i2, *args):
        """ Return True if i1 precedes i2.

        :param i1:  |-------|
        :param i2:                  |-------|
        :param *args:
            - max_delay: (int/float/sppasDuration) Maximum delay between the
            end of i1 and the beginning of i2.

        """
        max_delay = None
        if len(args) > 0:
            try:
                max_delay = float(args[0])
                if max_delay < 0.:
                    raise AnnDataNegValueError(max_delay)
            except (TypeError, ValueError):
                raise AnnDataTypeError(args[0], "float")

        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        is_before = x2 < y1
        if is_before is True and max_delay is not None:
            delay = sppasInterval(x2, y1)
            return delay.duration() < max_delay

        return is_before

    # ---------------------------------------------------------------------------

    @staticmethod
    def before_eq(i1, i2, *args):
        return sppasIntervalCompare.before(i1, i2, *args) and i1.duration() == i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def after(i1, i2, *args):
        """ Return True if i1 follows i2.

        :param i1:                  |--------|
        :param i2:  |-------|
        :param *args:
            - max_delay: (int/float/sppasDuration) Maximum delay between
            the end of i2 and the beginning of i1.

        """
        max_delay = None
        if len(args) > 0:
            try:
                max_delay = float(args[0])
                if max_delay < 0.:
                    raise AnnDataNegValueError(max_delay)
            except (TypeError, ValueError):
                raise AnnDataTypeError(args[0], "float")

        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        is_after = y2 < x1
        if is_after and max_delay is not None:
            interval = sppasInterval(y2, x1)
            return interval.duration() < max_delay

        return is_after

    # ---------------------------------------------------------------------------

    @staticmethod
    def meets(i1, i2, *args):
        """ Return True if i1 meets i2.

        :param i1:  |-------|
        :param i2:          |-------|
        :param *args:

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return not sppasIntervalCompare.equals(i1, i2) and x2 == y1

    # ---------------------------------------------------------------------------

    @staticmethod
    def metby(i1, i2, *args):
        """ Return True if i1 is met by i2.

        :param i1:          |-------|
        :param i2:  |-------|
        :param *args:

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return not sppasIntervalCompare.equals(i1, i2) and x1 == y2

    # ---------------------------------------------------------------------------

    @staticmethod
    def overlaps(i1, i2, *args):
        """ Return True if i1 overlaps with i2.

        :param i1:  |-------|
        :param i2:      |------|
        :param *args:
            - min_dur: (int/float/sppasDuration) Minimum duration of the
            overlap between i1 and i2.
            - percent: (bool) The min_dur parameter is a percentage of i1,
            instead of an absolute duration.

        """
        min_dur = None
        percent = False
        if len(args) > 0:
            try:
                min_dur = float(args[0])
                if min_dur < 0.:
                    raise AnnDataNegValueError(min_dur)
            except (TypeError, ValueError):
                raise AnnDataTypeError(args[0], "float")
            if len(args) > 1:
                percent = args[1]

        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        is_overlap = x1 < y1 < x2 < y2

        if is_overlap and min_dur is not None:
            overlap_interval = sppasInterval(y1, x2)
            if percent is True:
                # relative duration (min_dur parameter represents a percentage of i1)
                duration = i1.duration() * float(min_dur) / 100.
            else:
                # absolute duration
                duration = min_dur
            return overlap_interval.duration() > duration

        return is_overlap

    # ---------------------------------------------------------------------------

    @staticmethod
    def overlappedby(i1, i2, *args):
        """ Return True if i1 overlapped by i2.

        :param i1:      |-------|
        :param i2:  |-------|
        :param *args:

        """
        min_dur = None
        percent = False
        if len(args) > 0:
            try:
                min_dur = float(args[0])
                if min_dur < 0.:
                    raise AnnDataNegValueError(min_dur)
            except (TypeError, ValueError):
                raise AnnDataTypeError(args[0], "float")
            if len(args) > 1:
                percent = args[1]

        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        is_overlap = y1 < x1 < y2 < x2

        if is_overlap and min_dur is not None:
            # create an interval of the overlap part.
            overlap_interval = sppasInterval(i1.get_begin(), i2.get_end())
            if percent is True:
                if min_dur < 0. or min_dur > 100.:
                    raise AnnDataValueError("min_dur/percentage", min_dur)
                # relative duration (min_dur parameter represents a percentage of i1)
                duration = i1.duration() * float(min_dur) / 100.
            else:
                # absolute duration (min_dur parameter represents the minimum duration)
                duration = min_dur
            return overlap_interval.duration() > duration

        return is_overlap

    # ---------------------------------------------------------------------------

    @staticmethod
    def starts(i1, i2, *args):
        """ Return True if i1 starts at the start of i2 and finishes within it.

        :param i1:  |----|
        :param i2:  |----------|
        :param *args:

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return x1 == y1 and x2 < y2

    # ---------------------------------------------------------------------------

    @staticmethod
    def startedby(i1, i2, *args):
        """ Return True if i1 is started at the start of i2 interval.

        :param i1:  |----------|
        :param i2:  |----|
        :param *args:

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return x1 == y1 and y2 < x2

    # ---------------------------------------------------------------------------

    @staticmethod
    def finishes(i1, i2, *args):
        """ Return True if i1 finishes the same and starts within of i2.

        :param i1:       |----|
        :param i2:  |---------|
        :param *args:

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return y1 < x1 and x2 == y2

    # ---------------------------------------------------------------------------

    @staticmethod
    def finishedby(i1, i2, *args):
        """ Return True if i1 finishes the same and starts before of i2.

        :param i1:  |---------|
        :param i2:       |----|
        :param *args:

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return x1 < y1 and x2 == y2

    # ---------------------------------------------------------------------------

    @staticmethod
    def during(i1, i2, *args):
        """ Return True if i1 is located during i2.

        :param i1:      |----|
        :param i2:  |------------|
        :param *args:

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return y1 < x1 and x2 < y2

    # ---------------------------------------------------------------------------

    @staticmethod
    def contains(i1, i2, *args):
        """ Return True if i1 contains i2.

        :param i1:  |------------|
        :param i2:      |----|
        :param *args:

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return x1 < y1 and y2 < x2

    # ---------------------------------------------------------------------------

    @staticmethod
    def equals(i1, i2, *args):
        """ Return True if i1 equals i2.

        :param i1:  |-------|
        :param i2:  |-------|
        :param *args:

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return x1 == y1 and x2 == y2

    # ---------------------------------------------------------------------------
    # Private
    # ---------------------------------------------------------------------------

    @staticmethod
    def _unpack(localization):
        """ Return the 2 extremities of a localization. """

        if isinstance(localization, (sppasInterval, sppasDisjoint)):
            return localization.get_begin(), localization.get_end()

        elif isinstance(localization, sppasPoint):
            return localization, localization

        raise AnnDataTypeError(localization, "sppasBaseLocalization")
