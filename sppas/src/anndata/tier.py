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

    src.anndata.tier.py
    ~~~~~~~~~~~~~~~~~~~

    A tier is a set of annotations that are sorted depending on their location.

"""
from sppas.src.utils.fileutils import sppasGUID
from sppas.src.utils.makeunicode import sppasUnicode

from .anndataexc import AnnDataTypeError
from .anndataexc import IntervalBoundsError
from .anndataexc import CtrlVocabContainsError

from .annotation import sppasAnnotation
from .metadata import sppasMetaData
from .ctrlvocab import sppasCtrlVocab
from .media import sppasMedia
#from .filter.filters import Sel

# ----------------------------------------------------------------------------


class sppasTier(sppasMetaData):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Representation of a tier.

    A Tier is made of:
        - a name,
        - an array of annotations,
        - a set of metadata,
        - a controlled vocabulary,
        - a media.

    """
    def __init__(self, name=None, ctrl_vocab=None, media=None):
        """ Creates a new sppasTier instance.

        :param name: (str) Name of the tier. It is used as identifier.
        :param ctrl_vocab: (sppasCtrlVocab or None)
        :param media: (sppasMedia)

        """
        super(sppasTier, self).__init__()

        self.__name = None
        self.__ann = []
        self.__ctrl_vocab = None
        self.__media = None
        self.__parent = None
        self.__reference_tier = None

        self.set_name(name)
        self.set_ctrl_vocab(ctrl_vocab)
        self.set_media(media)

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_name(self):
        """ Return the identifier name of the tier. """

        return self.__name

    # -----------------------------------------------------------------------

    def get_ctrl_vocab(self):
        """ Return the controlled vocabulary of the tier. """

        return self.__ctrl_vocab

    # -----------------------------------------------------------------------

    def get_media(self):
        """ Return the media of the tier. """

        return self.__media

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_name(self, name=None):
        """ Set the name of the tier.

        :param name: (str or None) The identifier name or None.
        :returns: the name

        """
        if name is None:
            name = sppasGUID().get()
        su = sppasUnicode(name)
        self.__name = su.to_strip()

        return self.__name

    # -----------------------------------------------------------------------

    def set_ctrl_vocab(self, ctrl_vocab=None):
        """ Set a controlled vocabulary to this tier.

        :param ctrl_vocab: (sppasCtrlVocab or None)
        :raises: AnnDataTypeError, CtrlVocabContainsError

        """
        # In case we just want to disable the controlled vocabulary
        if ctrl_vocab is not None:
            if isinstance(ctrl_vocab, sppasCtrlVocab) is False:
                raise AnnDataTypeError(ctrl_vocab, "sppasCtrlVocab")

            # Check all annotation tags to validate the ctrl_vocab before assignment
            for annotation in self.__ann:
                for tag in annotation.get_label():
                    if ctrl_vocab.contains(tag) is False:
                        raise CtrlVocabContainsError(tag)

        self.__ctrl_vocab = ctrl_vocab

    # -----------------------------------------------------------------------

    def set_media(self, media):
        """ Set a media to the tier.

        :param media: (sppasMedia)

        """
        if media is not None:
            if isinstance(media, sppasMedia) is False:
                raise AnnDataTypeError(media, "sppasMedia")

        self.__media = media

    # -----------------------------------------------------------------------
    # Annotations
    # -----------------------------------------------------------------------

    def is_empty(self):
        """ Return True if the tier does not contain annotations. """

        return len(self.__ann) == 0

    # -----------------------------------------------------------------------

    def append(self, annotation):
        """ Append the given annotation to the end of the tier.

        :param annotation: (sppasAnnotation)
        :raises:

        """
        self.validate_annotation(annotation)

        if len(self.__ann) > 0:
            end = self.__ann[-1].get_highest_localization()
            new = annotation.get_lowest_localization()
            print(" ... ... current end={:s}, new={:s}".format(end, new))
            if end > new:
                raise ValueError("Can't append annotation. Current end {!s:s} is highest than {!s:s}.".format(end, new))

        self.__ann.append(annotation)

    # -----------------------------------------------------------------------

    def add(self, annotation):
        """ Add an annotation to the tier in sorted order.

        :param annotation: (sppasAnnotation)

        """
        self.validate_annotation(annotation)
        print("Add annotation: {:s}".format(annotation))
        try:
            self.append(annotation)
            print(" ... append success.")
        except Exception:
            index = self.__find(annotation.get_lowest_localization(), direction=-1)
            print(" ... prev is at index={:d}.".format(index))
            if index == -1:
                self.__ann.insert(0, annotation)

            elif annotation.location_is_point():
                self.__ann.insert(index+1, annotation)

            else:
                tmp = index
                for ann in self.__ann[tmp:]:
                    if ann.get_lowest_localization() > annotation.get_lowest_localization():
                        break
                    if ann.get_highest_localization() < annotation.get_highest_localization():
                        index += 1
                print(" ... insert at index={:d}.".format(index+1))
                self.__ann.insert(index+1, annotation)
        for ann in self.__ann:
            print(ann)

    # -----------------------------------------------------------------------

    def remove(self, begin, end, overlaps=False):
        """ Remove intervals between begin and end.

        :param begin: (sppasPoint)
        :param end:   (sppasPoint)
        :param overlaps: (bool)
        :returns: the number of removed annotations

        """
        if end <= begin:
            raise IntervalBoundsError(begin, end)

        annotations = self.find(begin, end, overlaps)
        for a in annotations:
            self.__ann.remove(a)

        return len(annotations)

    # -----------------------------------------------------------------------

    def pop(self, i=-1):
        """ Remove the annotation at the given position in the tier,
        and return it. If no index is specified, pop() removes
        and returns the last annotation in the tier.

        :param i: (int) Index of the annotation to remove.

        """
        try:
            return self.__ann.pop(i)
        except IndexError:
            raise IndexError("Can not pop annotation at index %d." % i)

    # -----------------------------------------------------------------------
    # Localizations
    # -----------------------------------------------------------------------

    def get_all_points(self):
        """ Return the list of all points of the tier. """

        if len(self.__ann) == 0:
            return []

        points = list()

        if self.is_point():
            for ann in self.__ann:
                for localization in ann.get_location():
                    points.append(localization.get_point())

        elif self.is_interval():
            for ann in self.__ann:
                for localization in ann.get_location():
                    points.append(localization.get_begin())
                    points.append(localization.get_end())

        elif self.is_disjoint():
            for ann in self.__ann:
                for localization in ann.get_location():
                    for interval in localization.get_intervals():
                        points.append(interval.get_begin())
                        points.append(interval.get_end())

        return points

    # -----------------------------------------------------------------------

    def get_first_point(self):
        """ Return the first point of the first annotation. """

        if len(self.__ann) == 0:
            return None

        if self.__ann[0].get_location().get_best().is_point() is True:
            return self.__ann[0].get_location().get_best()

        # Interval or Disjoint
        return self.__ann[0].get_location().get_best().get_begin()

    # -----------------------------------------------------------------------

    def get_last_point(self):
        """ Return the last point of the last location. """

        if len(self.__ann) == 0:
            return None

        if self.__ann[-1].get_location().get_best().is_point() is True:
            return self.__ann[-1].get_location().get_best()

        # Interval or Disjoint
        return self.__ann[-1].get_location().get_best().get_begin()

    # -----------------------------------------------------------------------

    def has_point(self, point):
        """ Return True if the tier contains a given point.

        :param point: (sppasPoint) The point to find in the tier.
        :returns: Boolean

        """
        return point in self.get_all_points()

    # -----------------------------------------------------------------------

    def is_superset(self, other):
        """ Return True if this tier contains all points of the other tier.

        :param other: (sppasTier)
        :returns: Boolean

        """
        if len(self.__ann) == 0:
            return False

        if self.is_point() is True:
            for ann in other:
                for localization in ann.get_location().get():
                    i = self.index(localization)
                    if i == -1:
                        return False
        else:
            for ann in other:
                for localization in ann.get_location().get():
                        i = self.lindex(localization.get_begin())
                        if i == -1:
                            return False
                        i = self.rindex(localization.get_end())
                        if i == -1:
                            return False

        return True

    # -----------------------------------------------------------------------

    def is_disjoint(self):
        """ Return True if the tier is made of disjoint localizations. """

        if len(self.__ann) == 0:
            return False

        return self.__ann[0].get_location().get_best().is_disjoint()

    # -----------------------------------------------------------------------

    def is_interval(self):
        """ Return True if the tier is made of interval localizations. """

        if len(self.__ann) == 0:
            return False

        return self.__ann[0].get_location().get_best().is_interval()

    # -----------------------------------------------------------------------

    def is_point(self):
        """ Return True if the tier is made of point localizations. """

        if len(self.__ann) == 0:
            return False

        return self.__ann[0].get_location().get_best().is_point()

    # -----------------------------------------------------------------------

    def find(self, begin, end, overlaps=True):
        """ Return a list of annotations between begin and end.

        :param begin: sppasPoint or None to start from the beginning of the tier
        :param end: sppasPoint or None to end at the end of the tier
        :param overlaps: (bool)

        """
        if len(self.__ann) == 0:
            return []

        if begin is None:
            begin = self.get_first_point()

        if end is None:
            end = self.get_last_point()

        # Out of interval!
        if begin > self.get_last_point() or end < self.get_first_point():
            return []

        is_point = self.is_point()

        if overlaps is True:
            index = self.__find(begin)
            anns = list()
            for ann in self.__ann[index:]:
                if is_point is True and ann.get_location().get_best() > end:
                    return anns
                if is_point is False and ann.get_location().get_best().get_begin() >= end:
                    return anns
                anns.append(ann)
            return anns

        if is_point is True:
            lo = self.index(begin)
            hi = self.index(end)
            if -1 in (lo, hi):
                return []
            for i in range(hi, len(self.__ann)):
                a = self.__ann[i]
                if a.get_location().get_best() == end:
                    tmp = i
                else:
                    break
            hi = tmp
        else:
            lo = self.lindex(begin)
            hi = self.rindex(end)
            if -1 in (lo, hi):
                return []
            for i in range(hi, len(self.__ann)):
                a = self.__ann[i]
                if a.get_location().get_best().get_end() == end:
                    tmp = i
                else:
                    break
            hi = tmp

        return [] if -1 in (lo, hi) else self.__ann[lo:hi+1]

    # -----------------------------------------------------------------------

    def get_annotations_start_at(self, moment):
        """ Return a list of annotations, starting at the specified moment.

        :param moment: A moment in time, frame, rank, etc. (i.e. a midpoint value).

        """
        annotations = list()
        if self.is_point():
            index = self.index(moment)
            if index == -1:
                return annotations
            for i in range(index, len(self.__ann)):
                a = self._ann[i]
                if moment in [p.get_point() for p in a.get_location().get()]:
                    annotations.append(a)
                else:
                    break
        else:
            index = self.lindex(moment)
            if index == -1:
                return []
            for i in range(index, len(self.__ann)):
                a = self.__ann[i]
                if moment in [p.get_begin() for p in a.get_location().get()]:
                    annotations.append(a)
                else:
                    break

        return annotations

    # -----------------------------------------------------------------------

    def get_annotations_end_at(self, moment):
        """ Return a list of annotations, ending at the specified moment.

        :param moment: A moment in time, frame, rank, etc. (i.e. a midpoint value).

        """
        annotations = []
        if self.is_point():
            return self.get_annotations_start_at(moment)

        index = self.rindex(moment)
        if index == -1:
            return []

        for i in range(index, len(self.__ann)):
            a = self.__ann[i]
            if moment in [p.get_end() for p in a.get_location().get()]:
                annotations.append(a)
            else:
                return annotations

        return annotations

    # -----------------------------------------------------------------------

    def index(self, moment):
        """ Return the index of the moment (int), or -1.
        Only for tier with points.

        :param moment: (sppasPoint)

        """
        if self.is_point() is False:
            return -1

        lo = 0
        hi = len(self.__ann)
        found = False
        while lo < hi:
            mid = (lo + hi) // 2
            a = self.__ann[mid]
            if moment < min([p for p in a.get_location().get()]):
                hi = mid
            elif moment > max([p for p in a.get_location().get()]):
                lo = mid + 1
            else:
                found = True
                break

        if not found:
            return -1

        # if the tier contains more than one annotation with the same point value,
        # the method returns the first one
        first = mid
        for i in range(mid, -1, -1):
            a = self.__ann[i]
            if moment in [p for p in a.get_location().get()]:
                first = i
            else:
                break

        return first

    # ------------------------------------------------------------------------

    def lindex(self, moment):
        """ Return the index of the interval starting at the given moment, or -1.
        Only for tier with intervals or disjoint.

        :param moment: (sppasPoint)

        """
        if self.is_point() is True:
            return -1

        lo = 0
        hi = len(self.__ann)
        found = False
        while lo < hi:
            mid = (lo + hi) // 2
            a = self.__ann[mid]
            if moment < min([p.get_begin() for p in a.get_location().get()]):
                hi = mid
            elif moment > max([p.get_begin() for p in a.get_location().get()]):
                lo = mid + 1
            else:
                found = True
                break

        if not found:
            return -1

        # if the tier contains more than one annotation with the same begin value,
        # the method returns the first one
        first = mid
        for i in range(mid, -1, -1):
            a = self.__ann[i]
            if moment in [p.get_begin() for p in a.get_location().get()]:
                first = i
            else:
                break
        return first

    # ------------------------------------------------------------------------

    def mindex(self, moment, direction):
        """ Return the index of the interval containing the given moment, or -1.
        Only for tier with intervals or disjoint.
        ATTENTION: Only on the localization with the best score.

        :param moment: (sppasPoint)
        :param direction: (int)

        """
        if self.is_point() is True:
            return -1

        for i, a in enumerate(self.__ann):
            b = a.get_location().get_best().get_begin()
            e = a.get_location().get_best().get_end()
            if direction == -1:
                if b <= moment < e:
                    return i
            elif direction == 1:
                if b < moment <= e:
                    return i
            else:
                if b < moment < e:
                    return i

        return -1

    # ------------------------------------------------------------------------

    def rindex(self, moment):
        """ Return the index of the interval ending at the given moment.
        Only for tier with intervals or disjoint.

        :param moment: (sppasPoint)

        """
        if self.is_point() is True:
            return -1

        lo = 0
        hi = len(self.__ann)
        found = False

        while lo < hi:
            mid = (lo + hi) // 2
            a = self.__ann[mid]
            if moment < min([p.get_end() for p in a.get_location().get()]):
                hi = mid
            elif moment > max([p.get_end() for p in a.get_location().get()]):
                lo = mid + 1
            else:
                found = True
                break

        if not found:
            return -1

        # if the tier contains more than one annotation with the same end value,
        # the method returns the first one
        first = mid
        for i in range(mid, -1, -1):
            a = self.__ann[i]
            if moment in [p.get_end() for p in a.get_location().get()]:
                first = i
            else:
                break

        return first

    # ------------------------------------------------------------------------

    def near(self, moment, direction=1):
        """ Return the index of the annotation whose localization is
        closest to the given moment.

        :param moment: (sppasPoint)
        :param direction: (int)
                - near 0
                - forward 1
                - backward -1

        """
        if len(self.__ann) == 0:
            return -1
        if len(self.__ann) == 1:
            return 0

        index = self.__find(moment, direction)
        if index == -1:
            return -1

        a = self.__ann[index]

        # POINTS
        # TODO: Not Implemented
        if self.is_point():
            return index

        # INTERVALS

        # forward
        if direction == 1:
            if moment < a.get_lowest_localization():
                return index
            if index + 1 < len(self.__ann):
                return index + 1
            return -1

        # backward
        elif direction == -1:
            print(" ... ... found index={:d}".format(index))
            if moment > a.get_highest_localization():
                return index
            if index-1 > 0:
                return index-1
            return -1

        # direction == 0 (select the nearest)

        # if time is during an annotation
        a = self.__ann[index]
        if a.get_lowest_localization() <= moment <= a.get_highest_localization():
            return index

        # then, the nearest is either the current or the next annotation
        _next = index + 1
        if _next >= len(self.__ann):
            # no next
            return index

        time = moment.get_midpoint()
        prev_time = max([p.get_end().get_midpoint() for p in self.__ann[index].get_location()])
        next_time = min([p.get_begin().get_midpoint() for p in self.__ann[_next].get_location()])
        if abs(time - prev_time) > abs(next_time - time):
            return _next

        return index

    # -----------------------------------------------------------------------
    # Labels
    # -----------------------------------------------------------------------

    def search(self, patterns, function='exact', pos=0, forward=True, reverse=False):
        """ Return the index in the tier of the first annotation whose tag matches patterns.

        :param patterns: (list) is the list of strings to search
        :param pos: (int)
        :param forward: (bool)
        :param reverse: (bool)
        :param function: (str) is:
                -    exact (str): exact match
                -    iexact (str): Case-insensitive exact match
                -    startswith (str):
                -    istartswith (str): Case-insensitive startswith
                -    endswith (str):
                -    iendswith: Case-insensitive endswith
                -    contains (str):
                -    icontains: Case-insensitive contains
                -    regexp (str): regular expression

        """
        hi = len(self.__ann)
        lo = -1

        if pos < 0 or pos > hi - 1:
            raise IndexError("Tier index out of range")

        p = patterns.pop(0)
        match = Sel(**{function:p})
        for p in patterns:
            match = match | Sel(**{function:p})

        if reverse:
            match = ~match

        inc = 1 if forward else -1
        while pos not in (lo, hi):
            annotation = self.__ann[pos]
            if match(annotation):
                return pos
            pos += inc
        return -1

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __find(self, x, direction=1):
        """ Return the index of the annotation whose moment value contains x.
        ATTENTION: only compare to the localization with the highest score

        :param x: (sppasPoint)

        """
        is_point = self.is_point()
        lo = 0
        hi = len(self.__ann)  # - 1
        mid = (lo + hi) // 2
        while lo < hi:
            mid = (lo + hi) // 2
            a = self.__ann[mid]
            if is_point is True:
                p = a.get_location().get_best()
                if p == x:
                    return mid
                if x < p:
                    hi = mid
                else:
                    lo = mid + 1
            else:  # Interval or Disjoint
                b = a.get_lowest_localization()
                e = a.get_highest_localization()
                if b == x or b < x < e:
                    return mid
                if x < e:
                    hi = mid
                else:
                    lo = mid + 1

        # We failed to find an annotation at time=x. return the closest...
        if direction == 1:
            return min(hi, len(self.__ann) - 1)
        return mid

    # -----------------------------------------------------------------------

    def validate_annotation(self, annotation):
        """ Validate the annotation, set its parent to this tier.

        :param annotation:
        :raises: AnnDataTypeError, CtrlVocabContainsError, HierarchyContainsError, HierarchyTypeError

        """
        # Check instance:
        if isinstance(annotation, sppasAnnotation) is False:
            raise AnnDataTypeError(annotation, "sppasAnnotation")

        # Check if annotation is relevant for this tier
        #  - same localization type?
        #  - label consistency
        #  - location consistency
        if len(self.__ann) > 0:
            if annotation.location_is_point() is True and self.is_point() is False:
                raise AnnDataTypeError(annotation, "sppasPoint")
            if annotation.location_is_interval() is True and self.is_interval() is False:
                raise AnnDataTypeError(annotation, "sppasInterval")
            if annotation.location_is_disjoint() is True and self.is_disjoint() is False:
                raise AnnDataTypeError(annotation, "sppasDisjoint")

        # Assigning a parent will validate the label and the location
        if self.__ctrl_vocab is not None or self.__parent is not None:
            annotation.set_parent(self)

    # -----------------------------------------------------------------------

    def validate_annotation_label(self, label):
        """ Validate the label of an annotation.

        :param label: (sppasLabel)
        :raises: CtrlVocabContainsError

        """
        # Check if controlled vocabulary
        if self.__ctrl_vocab is not None:
            for tag in label:
                if tag.is_empty() is False and self.__ctrl_vocab.contains(tag) is False:
                    raise CtrlVocabContainsError(tag)

    # -----------------------------------------------------------------------

    def validate_annotation_location(self, location):
        """ Validate the location of an annotation.

        :param location: (sppasLocation)
        :raises: HierarchyContainsError, HierarchyTypeError

        """
        if self.__parent is not None:
            if self.__reference_tier is not None:
                refpoints = self.__reference_tier.get_all_points()

            if len(self.__ann) == 0:
                if self.__reference_tier is not None:
                    if location.get_best().is_point():
                        for localization in location:
                            if localization not in refpoints:
                                raise ValueError(
                                    "Attempt to append an annotation in a child tier, but the reference tier has no corresponding localization: {:s}".format(
                                        localization))
                    else:
                        for localization in location:
                            if localization.get_begin() not in refpoints:
                                raise ValueError(
                                    "Attempt to append an annotation in a child tier, but the reference tier has no corresponding localization: {:s}".format(
                                        localization.get_begin()))
                            if localization.get_end() not in refpoints:
                                raise ValueError(
                                    "Attempt to append an annotation in a child tier, but the reference tier has no corresponding localization: {:s}".format(
                                        localization.get_end()))

            hierarchy = self.__parent().GetHierarchy()

            # if current tier is a child
            parent_tier = hierarchy.get_parent(self)
            if parent_tier is not None:
                link_type = hierarchy.get_hierarchy_type(self)
                if link_type == "TimeAssociation":
                    raise Exception("Attempt a modification in a Tier that invalidates its hierarchy.")
                if link_type == "TimeAlignment":
                    # The parent must have such location...
                    if location.get_best().is_point():
                        i = parent_tier.index(location.get_best())
                        if i == -1:
                            raise Exception("Attempt a modification in a Tier that invalidates its hierarchy.")
                    else:
                        l = parent_tier.lindex(location.get_best().get_begin())
                        if l == -1:
                            raise Exception("Attempt a modification in a Tier that invalidates its hierarchy.")

                        r = parent_tier.rindex(location.get_best().get_end())
                        if r == -1:
                            raise Exception("Attempt a modification in a Tier that invalidates its hierarchy.")

            # if current tier is a parent
            for child_tier in hierarchy.get_children(self):
                link_type = hierarchy.get_hierarchy_type(child_tier)
                if link_type == "TimeAssociation":
                    raise Exception("Attempt a modification in a Tier that invalidates its hierarchy.")

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __iter__(self):
        for a in self.__ann:
            yield a

    def __getitem__(self, i):
        return self.__ann[i]

    def __len__(self):
        return len(self.__ann)

# ---------------------------------------------------------------------------
