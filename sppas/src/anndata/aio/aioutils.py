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
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag
from ..anndataexc import TierAppendError

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

    # At a first stage, we create the annotations without labels
    for a in tier:

        # first interval
        if prev is None:
            a2 = sppasAnnotation(
                    sppasLocation(sppasInterval(a.get_lowest_localization(),
                                                a.get_highest_localization())))
            new_tier.append(a2)
            prev = a2
            continue

        if a.get_lowest_localization() < prev.get_lowest_localization():
            # normally it can't happen:
            # annotations are sorted by "append" and "add" methods.
            continue

        # a is after prev
        if a.get_lowest_localization() >= prev.get_highest_localization():
            # either:   |   prev   |  a   |
            # or:       |   prev   |   |  a  |

            a2 = sppasAnnotation(
                    sppasLocation(sppasInterval(a.get_lowest_localization(),
                                                a.get_highest_localization())))
            new_tier.append(a2)
            prev = a2

        # prev and a, both start at the same time
        elif a.get_lowest_localization() == prev.get_lowest_localization():

            # we must disable CtrlVocab because new entries are created...
            new_tier.set_ctrl_vocab(None)

            if a.get_highest_localization() > prev.get_highest_localization():
                #   |   prev  |
                #   |   a        |

                a2 = sppasAnnotation(
                    sppasLocation(sppasInterval(prev.get_highest_localization(),
                                                a.get_highest_localization())))
                new_tier.append(a2)
                prev = a2

            elif a.get_highest_localization() < prev.get_highest_localization():
                #   |   prev    |
                #   |   a    |

                a2 = sppasAnnotation(
                        sppasLocation(sppasInterval(a.get_highest_localization(),
                                                    prev.get_highest_localization())))
                prev_loc = prev.get_location().get_best()
                prev_loc.set_end(a.get_highest_localization())
                prev.set_best_localization(prev_loc)
                new_tier.append(a2)
                prev = a2

            else:
                #   |   prev   |
                #   |   a      |
                continue

        # a starts inside prev
        elif a.get_lowest_localization() < prev.get_highest_localization():

            # we must disable CtrlVocab because new entries are created...
            new_tier.set_ctrl_vocab(None)

            if a.get_highest_localization() < prev.get_highest_localization():
                #  |      prev       |
                #      |   a      |

                a2 = sppasAnnotation(
                            sppasLocation(sppasInterval(a.get_highest_localization(),
                                                        prev.get_highest_localization())))
                prev_loc = prev.get_location().get_best()
                prev_loc.set_end(a.get_lowest_localization())
                prev.set_best_localization(prev_loc)
                new_tier.append(a)
                new_tier.append(a2)
                prev = a2

            elif a.get_highest_localization() > prev.get_highest_localization():
                #  |  prev   |
                #       |   a    |

                a2 = sppasAnnotation(
                            sppasLocation(sppasInterval(a.get_lowest_localization(),
                                                        prev.get_highest_localization())))
                prev_loc = prev.get_location().get_best()
                prev_loc.set_end(a2.get_lowest_localization())
                prev.set_best_localization(prev_loc)
                new_tier.append(a2)

                a3 = sppasAnnotation(
                       sppasLocation(sppasInterval(a2.get_highest_localization(),
                                                   a.get_highest_localization())))
                new_tier.append(a3)
                prev = a3

            else:
                # |    prev   |
                #    |   a    |

                prev_loc = prev.get_location().get_best()
                prev_loc.set_end(a.get_lowest_localization())
                prev.set_best_localization(prev_loc)
                a2 = sppasAnnotation(
                            sppasLocation(sppasInterval(a.get_lowest_localization(),
                                                        a.get_highest_localization())))
                new_tier.append(a2)
                prev = a2

    # At a second stage, we assign the labels to the new tier
    for new_ann in new_tier:

        begin = new_ann.get_lowest_localization()
        end = new_ann.get_highest_localization()
        anns = tier.find(begin, end, overlaps=True)
        new_content = []
        for ann in anns:
            new_content.append(ann.get_label().get_best().get_content())

        new_ann.set_best_tag(sppasTag(separator.join(new_content)))

    return new_tier
