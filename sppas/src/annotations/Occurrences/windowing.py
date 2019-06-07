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

    def __init__(self, tier):
        """Return an instance of a sppaswindow.

        :param tier: (sppasTier) Tier to analyze

        """
        if isinstance(tier, sppasTier) is False:
            raise sppasTypeError(tier, sppasTier)

        self.__tier = tier

        if tier.is_disjoint():
            raise NotImplementedError('sppasWindow does not support disjoint interval tiers.')

    # -------------------------------------------------------------------------

    def time_split(self, start_time, end_time, step, delta=0.5):
        """Return set of annotations within a time window.

        :param start_time: (float) the time of the beginning of the window
        :param end_time: (float) the time of the end of the window
        :param step: (float) time period between two windows
        :param delta: (float) percentage of confidence for an overlapping label
        :returns: (sppasAnnSet) Set of sppasAnnotation

        """
        for item in (start_time, end_time, step, delta):
            if isinstance(item, (int, float)) is False:
                raise sppasTypeError(item, "float")

        ann_set = sppasAnnSet()
        ann_set_list = list()

        for i in sppasWindow.drange(start_time, end_time, step):
            # find annotations on the current time intervals
            anns = self.__tier.find(i, i+step, overlaps=True)
            if len(anns) > 0:
                # remove overlapping annotations if not overlapping enough
                if self.__tier.is_interval():
                    for ann in reversed(anns):
                        begin = ann.get_location().get_best().get_begin().get_midpoint()
                        dur = ann.get_location().get_best().duration().get_value()
                        overlap_point = begin + (dur * delta)
                        if overlap_point < i or overlap_point > (i+step):
                            anns.remove(ann)

                # add annotations in the set
                for ann in anns:
                    ann_set.append(ann, list())

        return ann_set_list

    # ---------------------------------------------------------------------------

    # ---------------------------------------------------------------------------

    @staticmethod
    def drange(x, y, jump):
        """Mimics 'range' with float values.

        :param x: start value
        :param y: end value
        :param jump: step value

        """
        x = decimal.Decimal(x)
        y = decimal.Decimal(y)
        while x < y:
            yield float(x)
            x += decimal.Decimal(jump)

    # ---------------------------------------------------------------------------

    def anchor_split(self, separators):
        """Return set of annotations within a window given by a separator.

        :param separators: (list) list of separators
        :returns: (sppasAnnSet) list of sppasAnnotation

        """
        if isinstance(separators, list) is False:
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
                # can start with a non-labelled interval!
                if tag is None or tag.get_typed_content() in separators:
                    begin = ann.get_highest_localization()

            end = ann.get_highest_localization()
            prev_ann = ann

        if end > begin:
            ann = self.__tier[-1]
            end = ann.get_highest_localization()
            intervals.append(sppasAnnotation(sppasLocation(sppasInterval(begin, end))), list())

        return intervals
