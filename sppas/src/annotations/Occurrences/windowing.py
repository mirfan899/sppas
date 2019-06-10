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
"""

import decimal

from sppas import sppasTier, sppasAnnotation, sppasTypeError
from sppas import sppasAnnSet
from sppas import sppasLocation, sppasInterval

# ---------------------------------------------------------------------------


class sppasTierWindow(object):
    """Windowing system on a tier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    Support windows in the time domain or with tag separators, both with or
    with overlaps among windows.

    """

    def __init__(self, tier):
        """Create an instance of a sppaswindow.

        :param tier: (sppasTier) Tier to analyze

        """
        if isinstance(tier, sppasTier) is False:
            raise sppasTypeError(tier, "sppasTier")

        self.__tier = tier

        if tier.is_disjoint():
            raise NotImplementedError('sppasWindow does not support disjoint interval tiers.')

    # -----------------------------------------------------------------------
    # Utilitiy methods
    # -----------------------------------------------------------------------

    @staticmethod
    def drange(x, y, jump):
        """Mimics 'range' with either float or int values.

        :param x: start value
        :param y: end value
        :param jump: step value

        """
        if isinstance(jump, int):
            x = int(x)
            y = int(y)
            while x < y:
                yield x
                x += jump

        elif isinstance(jump, float):
            x = decimal.Decimal(x)
            y = decimal.Decimal(y)
            while x < y:
                yield float(x)
                x += decimal.Decimal(jump)

    # -----------------------------------------------------------------------
    # Split methods
    # -----------------------------------------------------------------------

    def time_split(self, duration, step, delta=0.6):
        """Return a set of annotations within a time window.

        :param duration: (float) the duration of a window
        :param step: (float) the step duration
        :param delta: (float) percentage of confidence for an overlapping label
        :returns: (sppasAnnSet) Set of sppasAnnotation
        :raises: sppasTypeError, ValueError

        """
        if self.__tier.is_int() is True and isinstance(duration, int) is False:
            raise sppasTypeError(duration, "int")
        if self.__tier.is_float() is True and isinstance(duration, float) is False:
            raise sppasTypeError(duration, "float")

        # todo: test duration > step

        ann_set_list = list()
        start_time = self.__tier.get_first_point().get_midpoint()
        end_time = self.__tier.get_last_point().get_midpoint()

        for i in sppasTierWindow.drange(start_time, end_time, step):
            #print(i, i+duration)
            ann_set = sppasAnnSet()
            # find annotations on the current time interval
            anns = self.__tier.find(i, i+duration, overlaps=True)
            if len(anns) > 0:
                # remove overlapping annotations if not overlapping enough
                if self.__tier.is_interval():
                    for ann in reversed(anns):
                        begin = ann.get_location().get_best().get_begin().get_midpoint()
                        dur = ann.get_location().get_best().duration().get_value()
                        overlap_point = float(begin) + (float(dur) * delta)
                        if overlap_point < float(i) or overlap_point > float((i+duration)):
                            anns.remove(ann)

                # add annotations in the set, add the set in the list
                if len(anns) > 0:
                    for ann in anns:
                        ann_set.append(ann, list())
                    ann_set_list.append(ann_set)

        return ann_set_list

    # -----------------------------------------------------------------------

    def continuous_anchor_split(self, separators):
        """Return all time intervals within a window given by separators.

        :param separators: (list) list of separators
        :returns: (List of intervals)

        """
        if isinstance(separators, list) is False:
            raise sppasTypeError(separators, list)

        begin = self.__tier.get_first_point()
        end = begin
        prev_ann = None
        intervals = list()
        # is_point = self.__tier.is_point()

        for ann in self.__tier:

            tag = None
            if ann.label_is_filled():
                tag = ann.get_best_tag()

            if prev_ann is not None:
                # if no tag or stop tag or hole between prev_ann and ann
                if tag.get_typed_content() in separators:
                    # tag is None or prev_ann.get_highest_localization() < ann.get_lowest_localization():
                    if end > begin:
                        intervals.append((begin, prev_ann.get_highest_localization()))

                    if tag is None or tag.get_typed_content() in separators:
                        begin = ann.get_highest_localization()
                    else:
                        begin = ann.get_lowest_localization()
            else:
                # can start with a non-labelled interval!
                # if tag is None or \
                if tag.get_typed_content() in separators:
                    begin = ann.get_highest_localization()

            end = ann.get_highest_localization()
            prev_ann = ann

        if end > begin:
            ann = self.__tier[-1]
            end = ann.get_highest_localization()
            intervals.append((begin, end))

        return intervals

    # -----------------------------------------------------------------------

    def anchor_split(self, duration, step, separators):
        """Return all time intervals within a window given by separators.

        :param duration: (int) the duration of a window - number of intervals
        :param step: (int) the step duration - number of intervals
        :param separators: (list) list of separators
        :returns: (List of sppasAnnSet)

        """
        ann_set_list = list()
        intervals = self.continuous_anchor_split(separators)
        for i in range(0, len(intervals)+1, step):
            ann_set = sppasAnnSet()
            # find annotations on the current time interval
            end = min(i+duration-1, len(intervals)-1)
            anns = self.__tier.find(intervals[i][0],
                                    intervals[end][1],
                                    overlaps=True)
            for a in anns:
                if a.label_is_filled():
                    tag = a.get_best_tag().get_typed_content()
                    if tag not in separators:
                        ann_set.append(a, list())
                else:
                    ann_set.append(a, list())

            ann_set_list.append(ann_set)

            if end == len(intervals)-1:
                break

        return ann_set_list

