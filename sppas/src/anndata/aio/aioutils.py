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

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Utilities for readers and writers.

"""
import sppas
import codecs

from ..tier import sppasTier
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation
from ..annlocation.interval import sppasInterval
from ..annlocation.point import sppasPoint
from ..annlabel.label import sppasLabel
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioError
from ..anndataexc import AioEncodingError

# ---------------------------------------------------------------------------


def format_point_to_float(p):
    f = p.get_midpoint()
    return round(float(f), 4)

# ---------------------------------------------------------------------------


def load(filename, file_encoding=sppas.encoding):
    """ Load a file into lines.

    :param filename: (str)
    :param file_encoding: (str)
    :returns: list of lines (str)

    """
    try:
        with codecs.open(filename, 'r', file_encoding) as fp:
            lines = fp.readlines()
            fp.close()
    except IOError:
        raise AioError(filename)
    except UnicodeDecodeError:
        raise AioEncodingError(filename, "", file_encoding)

    return lines

# ---------------------------------------------------------------------------


def check_gaps(tier, min_loc=None, max_loc=None):
    """ Check if there are holes between annotations.

    :param tier: (sppasTier)
    :param min_loc: (sppasPoint)
    :param max_loc: (sppasPoint)
    :returns: (bool)

    """
    if tier.is_empty():
        return False

    if min_loc is not None and format_point_to_float(tier.get_first_point()) > format_point_to_float(min_loc):
        return True
    if max_loc is not None and format_point_to_float(tier.get_last_point()) < format_point_to_float(max_loc):
        return True

    prev = None
    for ann in tier:
        if prev is not None:
            prev_end = prev.get_highest_localization()
            ann_begin = ann.get_lowest_localization()
            if prev_end < ann_begin:
                return True
        prev = ann

    return False

# ---------------------------------------------------------------------------


def fill_gaps(tier, min_loc=None, max_loc=None):
    """ Return the tier in which the temporal gaps between annotations are
    filled with an un-labelled annotation.

    :param tier: (Tier) A tier with intervals.
    :param min_loc: (sppasPoint)
    :param max_loc: (sppasPoint)
    :returns: (sppasTier)

    """
    # find gaps only if the tier is an IntervalTier
    if tier.is_interval() is False:
        return tier

    # There's no reason to do anything if the tier is already without gaps!
    if check_gaps(tier, min_loc, max_loc) is False:
        return tier

    # Right, we have things to do...
    new_tier = tier.copy()

    # Check firstly the begin/end
    if min_loc is not None and format_point_to_float(tier.get_first_point()) > format_point_to_float(min_loc):
        interval = sppasInterval(min_loc, tier.get_first_point())
        new_tier.add(sppasAnnotation(sppasLocation(interval)))

    if max_loc is not None and format_point_to_float(tier.get_last_point()) < format_point_to_float(max_loc):
        interval = sppasInterval(tier.get_last_point(), max_loc)
        new_tier.add(sppasAnnotation(sppasLocation(interval)))

    # There's no reason to go further if the tier is already without gaps!
    if check_gaps(new_tier, min_loc, max_loc) is False:
        return new_tier

    # Right, we have to check all annotations
    prev = None
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

    return new_tier

# ---------------------------------------------------------------------------


def serialize_labels(labels, separator="\n", empty="", alt=True):
    """ Convert labels into a string.

    :param labels: (list of sppasLabel)
    :param separator: (str) String to separate labels.
    :param empty: (str) The text to return if a tag is empty or not set.
    :param alt: (bool) Include alternative tags
    :returns: (str)

    """
    if len(labels) == 0:
        return empty

    if len(labels) == 1:
        return serialize_label(labels[0], empty, alt)

    c = list()
    for label in labels:
        c.append(serialize_label(label, empty, alt))

    return separator.join(c)

# -----------------------------------------------------------------------


def serialize_label(label, empty="", alt=True):
    """ Convert a label into a string, including or not alternative tags.

    BNF to represent alternative tags:
        ALTERNATE :== "{" TEXT ALT+ "}"
        ALT :== "|" TEXT
        TEXT :== tag content | empty

    Scores of the tags are not returned.

    :param label: (sppasLabel)
    :param empty: (str) The text to return if a tag is empty or not set.
    :param alt: (bool) Include alternative tags
    :returns: (str)

    """
    if isinstance(label, sppasLabel) is False:
        raise AnnDataTypeError(label, "sppasLabel")

    if label is None:
        return empty

    if label.get_best() is None:
        return empty

    if alt is False:
        if label.get_best().is_empty():
            return empty
        return label.get_best().get_content()

    # we store the alternative tags into a list.
    # empty tags are replaced by the empty item.
    tag_contents = list()
    for tag, score in label:
        content = tag.get_content()
        if len(content) > 0:
            tag_contents.append(content)
        else:
            tag_contents.append(empty)

    if len(tag_contents) == 1:
        return tag_contents[0]

    # we return the alternative tags
    return "{ " + " / ".join(tag_contents) + " }"

# -----------------------------------------------------------------------


def unfill_gaps(tier):
    """ Return the tier in which un-labelled annotations are removed.

    An un_labelled annotation means that:

        - the annotation has no labels,
        - or the tags of each label are an empty string.

    The hierarchy is not copied to the new tier.

    :param tier: (Tier)
    :returns: (sppasTier)

    """
    new_tier = sppasTier(tier.get_name()+"-unfill")
    new_tier.set_ctrl_vocab(tier.get_ctrl_vocab())
    new_tier.set_media(tier.get_media())
    for key in tier.get_meta_keys():
        new_tier.set_meta(key, tier.get_meta(key))

    for i, ann in enumerate(tier):
        if ann.label_is_filled() is True:
            content = serialize_labels(ann.get_labels())
            if len(content) > 0:
                new_tier.append(ann.copy())

    return new_tier

# ---------------------------------------------------------------------------


def check_overlaps(tier):
    """ Check whether some annotations are overlapping or not.

    :param tier: (sppasTier)
    :returns: (bool)

    """
    if tier.is_empty():
        return False
    prev = None
    for ann in tier:
        if prev is not None:
            prev_end = prev.get_highest_localization()
            ann_begin = ann.get_lowest_localization()
            if ann_begin < prev_end:
                return True
        prev = ann

    return False

# ---------------------------------------------------------------------------


def merge_overlapping_annotations(tier):
    """ Merge overlapping annotations.

    The labels of 2 overlapping annotations are appended.

    :param tier: (Tier)
    :returns: (sppasTier)

    """
    if tier.is_interval() is False:
        return tier
    if tier.is_empty():
        return tier
    if len(tier) == 1:
        return tier

    if check_overlaps(tier) is False:
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

        new_labels = list()
        for ann in anns:
            new_labels.extend(ann.get_labels())
        new_ann.set_labels(new_labels)

    return new_tier

# ------------------------------------------------------------------------


def point2interval(tier, radius=0.001):
    """ Convert a PointTier into an IntervalTier.

    Ensure the radius to be always >= 1 millisecond and the newly created
    tier won't contain overlapped intervals.

    Do not convert alternatives localizations.
    Do not share the hierarchy.

    :param tier: (Tier)
    :param radius: (float) the radius to use for all intervals
    :returns: (sppasTier) or None if tier was not converted.

    """
    # check the type of the tier!
    if tier.is_point() is False:
        return None

    # create the new tier and share information (except 'id' and hierarchy)
    new_tier = sppasTier(tier.get_name())
    for key in tier.get_meta_keys():
        if key != 'id':
            new_tier.set_meta(key, tier.get_meta(key))
    new_tier.set_media(tier.get_media())
    new_tier.set_ctrl_vocab(tier.get_ctrl_vocab())

    # create the annotations with intervals
    end_midpoint = 0.
    for ann in tier:

        # get the point with the best score for this annotation
        point = ann.get_location().get_best()
        m = point.get_midpoint()
        r = max(radius, point.get_radius())

        # fix begin/end new points. Provide overlaps.
        begin_midpoint = max(m - r, end_midpoint)
        begin = sppasPoint(begin_midpoint, r)
        end_midpoint = m + r
        end = sppasPoint(end_midpoint, r)

        # create the new annotation with an interval
        new_ann = sppasAnnotation(sppasLocation(sppasInterval(begin, end)),
                                  [label.copy() for label in ann.get_labels()])
        # new annotation shares original annotation's metadata, except the 'id'
        for key in new_ann.get_meta_keys():
            if key != 'id':
                new_ann.set_meta(key, ann.get_meta(key))
        new_tier.append(new_ann)

    return new_tier
