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
import copy

from .annlabel.label import sppasLabel
from .annlocation.location import sppasLocation
from .metadata import sppasMetaData
from .anndataexc import AnnDataTypeError

# ----------------------------------------------------------------------------


class sppasAnnotation(sppasMetaData):
    """
    :author:       Brigitte Bigi, Jibril Saffi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Represents an annotation.

    A sppasAnnotation() is a container for:
        - a sppasLocation()
        - a sppasLabel()

    >>> p = sppasLocation(sppasTimePoint(1.5, radius=0.01))
    >>> l = sppasLabel(sppasText("foo"))
    >>> ann = sppasAnnotation(t, p)
    >>> ann.get_location().get_best().get_point()
    1.5
    >>> ann.get_label().get_best().get_content()
    foo

    """
    def __init__(self, location, label=None):
        """ Creates a new sppasAnnotation instance.

        :param location (sppasLocation) the location(s) where the annotation happens
        :param label (sppasLabel) the label(s) to stamp this annotation

        """
        super(sppasAnnotation, self).__init__()

        if isinstance(location, sppasLocation) is False:
            raise AnnDataTypeError(location, "sppasLocation")

        if label is not None:
            if isinstance(label, sppasLabel) is False:
                raise AnnDataTypeError(label, "sppasLabel")

        self.__label = label

        # Assign the location
        self.__location = location

    # -----------------------------------------------------------------------

    def get_label(self):
        """ Return the sppasLabel instance. """

        if self.__label is not None:
            return self.__label

        return sppasLabel("")

    # -----------------------------------------------------------------------

    def get_location(self):
        """ Return the sppasLocation instance. """

        return self.__location

    # -----------------------------------------------------------------------

    def copy(self):
        """ Return a deep copy of the annotation. """

        return copy.deepcopy(self)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __str__(self):
        return "Annotation: {:s} {:s}".format(self.__location, self.__label)

    def __repr__(self):
        return "{:s} {:s}".format(self.__location, self.__label)
