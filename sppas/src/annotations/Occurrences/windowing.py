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


class sppasWindow(object):

    def __init__(self, trs):
        """Return an instance of a sppaswindow

        :param trs: (sppasTier) Tier to analyze
        """
        if not isinstance(trs, sppasTier):
            raise sppasTypeError(trs, sppasTier)
        else:
            self.__tier = trs

    # -------------------------------------------------------------------------

    def time_split(self, start_time, end_time, step, delta=0.5):
        """Return list of annotation within a time window with the given values

        :param start_time: (float) the time of the beginning of the window
        :param end_time: (float) the time of the end of the window
        :param step: (float) time period between two windows
        :param delta: (float) percentage of confidence for an overlapping label
        :return: (list) list of sppasAnnotation
        """
        args = (start_time, end_time, step, delta)

        ann_set = sppasAnnSet()
        ann_set_list = list()

        for item in args:
            if not isinstance(item, float):
                raise sppasTypeError(item, float)

        def drange(x, y, jump):
            x = decimal.Decimal(x)
            y = decimal.Decimal(y)
            while x < y:
                yield float(x)
                x += decimal.Decimal(jump)

        total_time = 0.0
        for ann in self.__tier:
            curr_dur = ann.get_location().get_best().duration().get_value()
            total_time += curr_dur
            for dur in drange(start_time, end_time, step):
                if dur <= ann.get_location().get_best().get_begin().get_midpoint() < end_time:
                    ann_set.append(ann, list())

            ann_set_list.append(ann_set)

            if self.__tier.is_point() is False:
                if total_time >= start_time:
                    if delta < (total_time - start_time) / curr_dur < 1.0:
                        ann_set.append(ann, list())

        return ann_set_list

    # ---------------------------------------------------------------------------

    def anchor_split(self, separators):
        """Return list of annotation within a window decided by the given separator

        :param separators: (list) list of separators
        :return: (list) list of sppasAnnotation
        """
        if not isinstance(separators, list):
            raise sppasTypeError(separators, list)

        intervals = sppasAnnSet()
        begin = self.__tier.get_first_point()
        end = begin
        prev_ann = None

        for ann in self.__tier:
            tag = None
            if ann.label_is_filled():
                tag = ann.get_best_tag()

            if prev_ann is not None:
                # if no tag or stop tag or hole between prev_ann and ann
                if tag is None or \
                        tag.get_typed_content() in separators or \
                        prev_ann.get_highest_localization() < ann.get_lowest_localization():
                    if end > begin:
                        intervals.append(sppasAnnotation(sppasLocation(
                            sppasInterval(begin,
                                          prev_ann.get_highest_localization()))), list())

                    if tag is None or tag.get_typed_content() in separators:
                        begin = ann.get_highest_localization()
                    else:
                        begin = ann.get_lowest_localization()
            else:
                # phonemes can start with a non-labelled interval!
                if tag is None or tag.get_typed_content() in separators:
                    begin = ann.get_highest_localization()

            end = ann.get_highest_localization()
            prev_ann = ann

        if end > begin:
            ann = self.__tier[-1]
            end = ann.get_highest_localization()
            intervals.append(sppasAnnotation(sppasLocation(sppasInterval(begin, end))), list())

        return intervals

# ---------------------------------------------------------------------------
