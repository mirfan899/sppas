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

    src.anndata.aio.aioutils.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Utilities for readers and writers.

"""
from ..tier import sppasTier
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag

# ------------------------------------------------------------------------


def format_point_to_float(p):
    f = p.get_midpoint()
    return round(float(f), 4)

# ------------------------------------------------------------------------


def fill_gaps(tier, min_loc=None, max_loc=None):
    """ Return the tier in which the temporal gaps between annotations are
    filled with an un-labelled annotation.

    :param tier: (Tier)
    :param min_loc: (sppasPoint)
    :param max_loc: (sppasPoint)

    """
    new_tier = tier.copy()
    prev = None

    if min_loc is not None and format_point_to_float(tier.get_first_point()) > format_point_to_float(min_loc):
        interval = sppasInterval(min_loc, tier.get_first_point())
        new_tier.add(sppasAnnotation(sppasLocation(interval)))

    for a in new_tier:
        if prev is not None and prev.get_highest_localization() < a.get_lowest_localization():
            interval = sppasInterval(prev.get_highest_localization(), a.get_lowest_localization())
            annotation = sppasAnnotation(sppasLocation(interval))
            new_tier.add(annotation)
            prev = annotation
        elif prev is not None and prev.get_highest_localization() < a.get_lowest_localization():
            a.get_lowest_localization().set(prev.get_highest_localization())
            prev = a
        else:
            prev = a

    if max_loc is not None and format_point_to_float(tier.get_last_point()) < format_point_to_float(max_loc):
        interval = sppasInterval(tier.get_last_point(), max_loc)
        new_tier.add(sppasAnnotation(sppasLocation(interval)))

    return new_tier

# ------------------------------------------------------------------------


def unfill_gaps(tier):
    """ Return the tier in which un-labelled annotations are removed.
    An un_labelled annotation means that:
        - either the label is None,
        - or the best tag of the label is an empty string.

    :param tier: (Tier)
    :returns: tier

    """
    new_tier = tier.copy()
    to_pop = list()
    for i, ann in enumerate(new_tier):
        if ann.get_label() is None or ann.get_label().get_best().is_empty():
            to_pop.append(i)

    for i in reversed(to_pop):
        new_tier.pop(i)

    return new_tier

# ------------------------------------------------------------------------


def merge_overlapping_annotations(tier, separator=' '):
    """ Merge overlapping annotations.
    The values of the tags are concatenated.
    Do not pay attention to alternatives.

    :param tier: (Tier)
    :param separator: (char)
    :returns: Tier

    """
    if tier.is_interval() is False:
        return tier

    new_tier = sppasTier(tier.get_name())
    for key in tier.get_meta_keys():
        new_tier.set_meta(key, tier.get_meta(key))
    new_tier.set_parent(tier.get_parent())
    new_tier.set_ctrl_vocab(tier.get_ctrl_vocab())
    new_tier.set_media(tier.get_media())

    prev = None

    for a in tier:
        if prev is None:
            new_tier.append(a)
            prev = a
            continue

        if a.get_lowest_localization() < prev.get_lowest_localization():
            # normally it can't happen!
            continue

        # a is after prev: normal.
        if a.get_lowest_localization() >= prev.get_highest_localization():
            new_tier.append(a)
            prev = a

        # prev and a, both start at the same time
        elif a.get_lowest_localization() == prev.get_lowest_localization():
            new_tier.set_ctrl_vocab(None)
            # must disable CtrlVocab or, eventually, add new labels in its entries...

            if a.get_highest_localization() > prev.get_highest_localization():
                a.get_location().get_best().set_begin(prev.get_highest_localization())
                #prev_content = prev.get_label().get_best().get_content() + \
                #               separator + \
                #               a.get_label().get_best().get_content()
                #prev.get_label().get_best().set_content(prev_content)
                new_tier.append(a)
                prev = a

            elif a.get_highest_localization() < prev.get_highest_localization():
                a2 = sppasAnnotation(
                        sppasLocation(sppasInterval(a.get_highest_localization(), prev.get_highest_localization())),
                        sppasLabel(prev.get_label())
                )
                #prev.get_highest_localization().set(a.get_highest_localization())
                #prev_content = prev.get_label().get_best().get_content() + \
                #               separator + \
                #               a.get_label().get_best().get_content()
                #prev.get_label().get_best().set_content(prev_content)
                new_tier.append(a2)
                prev = a2

            else:
                prev_content = prev.get_label().get_best().get_content() + \
                               separator + \
                               a.get_label().get_best().get_content()
                prev.get_label().get_best().set_content(prev_content)

        # a starts inside prev
        elif a.get_lowest_localization() < prev.get_highest_localization():
            new_tier.set_ctrl_vocab(None)
            # must disable CtrlVocab or, eventually, add new labels in its entries...

            if a.get_highest_localization() < prev.get_highest_localization():
                a2 = sppasAnnotation(
                            sppasLocation(sppasInterval(a.get_highest_localization(), prev.get_highest_localization())),
                            sppasLabel(prev.get_label().get_best())
                )
                a_content = a.get_label().get_best().get_content() + \
                            separator + \
                            prev.get_label().get_best().get_content()
                a.get_label().get_best().set_content(a_content)
                #prev.GetLocation().SetEnd( a.get_lowest_localization() )
                new_tier.append(a)
                new_tier.append(a2)
                prev = a2

            elif a.get_highest_localization() > prev.get_highest_localization():
                a2_content = prev.get_label().get_best().get_content() + \
                            separator + \
                            a.get_label().get_best().get_content()
                a2 = sppasAnnotation(
                            sppasLocation(sppasInterval(a.get_lowest_localization(), prev.get_highest_localization())),
                            sppasLabel(sppasTag(a2_content))
                )
                #prev.GetLocation().SetEnd( a2.get_lowest_localization() )
                a.get_lowest_localization().set(a2.get_highest_localization())
                new_tier.append(a2)
                new_tier.append(a)
                prev = a

            else:
                a_content = a.get_label().get_best().get_content() + \
                            separator + \
                            prev.get_label().get_best().get_content()
                a.get_label().get_best().set_content(a_content)
                #prev.GetLocation().SetEnd( a.get_lowest_localization() )
                new_tier.append(a)
                prev = a

    return new_tier
