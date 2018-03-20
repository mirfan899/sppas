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

    src.anndata.annotation.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from .anndataexc import AnnDataTypeError
from .annlabel.tag import sppasTag
from .annlabel.label import sppasLabel
from .annlocation.location import sppasLocation
from .metadata import sppasMetaData

# ----------------------------------------------------------------------------


class sppasAnnotation(sppasMetaData):
    """
    :author:       Brigitte Bigi, Jibril Saffi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Represents an annotation.

    A sppasAnnotation() is a container for:
        - a sppasLocation()
        - a sppasLabel()

    >>> location = sppasLocation(sppasPoint(1.5, radius=0.01))
    >>> label = sppasLabel(sppasTag("foo"))
    >>> ann = sppasAnnotation(location, label)

    """
    def __init__(self, location, label=None):
        """ Creates a new sppasAnnotation instance.

        :param location: (sppasLocation) the location(s) where the annotation happens
        :param label: (sppasLabel) the label(s) to stamp this annotation

        """
        super(sppasAnnotation, self).__init__()

        if isinstance(location, sppasLocation) is False:
            raise AnnDataTypeError(location, "sppasLocation")

        if label is not None:
            if isinstance(label, sppasLabel) is False:
                raise AnnDataTypeError(label, "sppasLabel")

        self.__parent = None
        self.__location = location
        self.__label = label

    # -----------------------------------------------------------------------

    def get_label(self):
        """ Return the sppasLabel instance.

        It could be None if no label were previously assigned.

        """
        return self.__label

    # -----------------------------------------------------------------------

    def get_location(self):
        """ Return the sppasLocation instance. """

        return self.__location

    # -----------------------------------------------------------------------

    def copy(self):
        """ Return a deep copy of the annotation. """

        location = self.__location.copy()
        if self.__label is not None:
            label = self.__label.copy()
        else:
            label = None
        other = sppasAnnotation(location, label)
        other.set_parent(self.__parent)
        return other

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_parent(self, parent=None):
        """ Set a parent tier.

        :param parent: (sppasTier) The parent tier of this annotation.

        """
        if parent is not None:
            parent.validate_annotation_location(self.__location)
            if self.__label is not None:
                parent.validate_annotation_label(self.__label)

        self.__parent = parent

    # -----------------------------------------------------------------------

    def validate(self):
        """ Validate the annotation.
        Check if the annotation matches the requirements of its parent.

        :raises: CtrlVocabContainsError, HierarchyContainsError, HierarchyTypeError

        """
        if self.__parent is not None:
            if self.__label is not None:
                self.__parent.validate_annotation_label(self.__label)
            self.__parent.validate_annotation_location(self.__location)

    # -----------------------------------------------------------------------
    # Tags
    # -----------------------------------------------------------------------

    def get_best_tag(self):
        """ Return the tag with the highest score.

        If no label was previously assigned, returns an empty tag.

        """
        # No label defined
        if self.__label is None:
            return sppasTag("")
        # No tag in the label
        tag = self.__label.get_best()
        if tag is None:
            return sppasTag("")

        return tag

    # -----------------------------------------------------------------------

    def set_best_tag(self, tag):
        """ Set the best tag of the label.
        It will replace the tag with the highest score by the given one,
        and do not change the score.

        :param tag: (sppasTag)

        """
        if self.__label is None:
            self.__label = sppasLabel(sppasTag(""))

        if self.__parent is not None:
            old_tag = self.get_best_tag().copy()
            self.__label.get_best().set(tag)
            try:
                self.__parent.validate_annotation_label(self.__label)
            except Exception:
                self.__label.get_best().set(old_tag)
                raise
        else:
            self.__label.get_best().set(tag)

    # -----------------------------------------------------------------------

    def add_tag(self, tag, score=None):
        """ Append an alternative tag in the label.

        :param tag: (sppasTag)
        :param score: (float)
        :raises: AnnDataTypeError

        """
        if self.__label is None:
            self.__label = sppasLabel()

        self.__label.append(tag, score)
        if self.__parent is not None:
            try:
                self.__parent.validate_annotation_label(self.__label)
            except Exception:
                self.__label.remove(tag)
                raise

    # -----------------------------------------------------------------------

    def remove_tag(self, tag):
        """ Remove an alternative tag of the label.

        :param tag: (sppasTag) the tag to be removed of the list.

        """
        if self.__label is not None:
            self.__label.remove(tag)

    # -----------------------------------------------------------------------

    def contains_tag(self, tag, function='exact', reverse=False):
        """ Return True if the given tag is in the label.

        :param tag: (sppasTag)
        :param function: Search function
        :param reverse: Reverse the function.

        """
        r = self.__label.contains(tag, function)
        if reverse is False:
            return r
        return not r

    # -----------------------------------------------------------------------

    def label_is_string(self):
        """ Return True if the type of the tags of a label are str or unicode. """

        if self.__label is None:
            return False
        return self.__label.is_string()

    # -----------------------------------------------------------------------

    def label_is_float(self):
        """ Return True if the tags are float values """

        if self.__label is None:
            return False
        return self.__label.is_float()

    # -----------------------------------------------------------------------

    def label_is_int(self):
        """ Return True if the tags are integer values """

        if self.__label is None:
            return False
        return self.__label.is_int()

    # -----------------------------------------------------------------------

    def label_is_bool(self):
        """ Return True if the tags are integer values """

        if self.__label is None:
            return False
        return self.__label.is_bool()

    # -----------------------------------------------------------------------

    def validate_label(self):
        """ Validate the label of the annotation.

        :raises: CtrlVocabContainsError

        """
        if self.__parent is not None:
            self.__parent.validate_annotation_label(self.__label)

    # -----------------------------------------------------------------------
    # Localization
    # -----------------------------------------------------------------------

    def set_best_localization(self, localization):
        """ Set the best localization of the location.

        :param localization: (sppasBaseLocalization)

        """
        old_loc = self.__location.get_best().copy()
        self.__location.get_best().set(localization)
        if self.__parent is not None:
            try:
                self.__parent.validate_annotation_location(self.__location)
            except Exception:
                self.__location.get_best().set(old_loc)
                raise

    # -----------------------------------------------------------------------

    def location_is_point(self):
        """ Return True if the location is made of sppasPoint localizations. """

        return self.__location.is_point()

    # -----------------------------------------------------------------------

    def location_is_interval(self):
        """ Return True if the location is made of sppasInterval localizations. """

        return self.__location.is_interval()

    # -----------------------------------------------------------------------

    def location_is_disjoint(self):
        """ Return True if the location is made of sppasDisjoint localizations. """

        return self.__location.is_disjoint()

    # -----------------------------------------------------------------------

    def get_highest_localization(self):
        """ Return a copy of the sppasPoint with the highest localization. """

        if self.__location.is_point():
            max_localization = max([l[0] for l in self.__location])
        else:
            max_localization = max([l[0].get_end() for l in self.__location])

        # We return a copy to be sure the original localization won't be modified
        return max_localization.copy()

    # -----------------------------------------------------------------------

    def get_lowest_localization(self):
        """ Return a copy of the sppasPoint with the lowest localization. """

        if self.__location.is_point():
            min_localization = min([l[0] for l in self.__location])
        else:
            min_localization = min([l[0].get_begin() for l in self.__location])

        # We return a copy to be sure the original localization won't be modified
        return min_localization.copy()

    # -----------------------------------------------------------------------

    def get_all_points(self):
        """ Return the list of a copy of all points of this annotation. """

        points = list()
        if self.__location.is_point():
            for localization, score in self.__location:
                points.append(localization.copy())

        elif self.__location.is_interval():
            for localization, score in self.__location:
                points.append(localization.get_begin().copy())
                points.append(localization.get_end().copy())

        elif self.__location.is_disjoint():
            for localization, score in self.__location:
                for interval in localization.get_intervals():
                    points.append(interval.get_begin().copy())
                    points.append(interval.get_end().copy())

        return points

    # -----------------------------------------------------------------------

    def contains_localization(self, localization):
        """ Return True if the given localization is in the location. """

        return self.__location.contains(localization)

    # -----------------------------------------------------------------------

    def validate_location(self):
        """ Validate the location of the annotation.

        :raises: 

        """
        if self.__parent is not None:
            self.__parent.validate_annotation_location(self.__location)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return "Annotation: {:s} {:s}".format(self.__location, self.__label)

    def __str__(self):
        return "{:s} {:s}".format(self.__location, self.__label)

    def __eq__(self, other):
        return self.__location == other.get_location() and self.__label == other.get_label()
