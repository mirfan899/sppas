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

    src.anndata.annloc.localization.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from ..anndataexc import AnnDataTypeError

# ---------------------------------------------------------------------------


class sppasLocalization(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Represents a Localization of an Annotation.

    """
    def __init__(self, score=1.):
        """ Create a sppasLocalization instance.

        :param score: (float) Score of the localization.

        """
        self.__score = 1.
        self.set_score(score)

    # -----------------------------------------------------------------------

    def get_score(self):
        """ Return the score of the localization. """

        return self.__score

    # -----------------------------------------------------------------------

    def set_score(self, score):
        """ Set a new score.

        :param score: (float)

        """
        try:
            self.__score = float(score)
        except Exception:
            raise AnnDataTypeError(score, "float")

    # -----------------------------------------------------------------------

    def strict_equal(self, other):
        """ Return True if self is strictly equal to other.

        :param other: (sppasLocalization) to compare with.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def duration(self):
        """ Return the duration of this localization.
        Must be overridden.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------

    def is_point(self):
        """ Return True if this object is an instance of sppasTimePoint or sppasFramePoint.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def is_interval(self):
        """ Return True if this object is an instance of sppasTimeInterval or sppasFrameInterval.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def is_time_point(self):
        """ Return True if this object is an instance of sppasTimePoint.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def is_time_interval(self):
        """ Return True if this object is an instance of sppasTimeInterval.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def is_time_disjoint(self):
        """ Return True if this object is an instance of sppasTimeDisjoint.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def is_frame_point(self):
        """ Return True if this object is an instance of sppasFramePoint.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def is_frame_interval(self):
        """ Return True if this object is an instance of sppasFrameInterval.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------

    def is_frame_disjoint(self):
        """ Return True if this object is an instance of sppasFrameDisjoint.
        Should be overridden.

        """
        return False

    # ---------------------------------------------------------------------
    # Overloads
    # ---------------------------------------------------------------------

    def __eq__(self, other):
        """ Equal is required to use '==' between 2 localization instances.
        Two localization instances are equals iff they are of the same instance
        and their values are equals.

        :param other: the other localization to compare with.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------

    def __lt__(self, other):
        """ LowerThan is required to use '<' between 2 localization instances.

        :param other: the other localization to compare with.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------

    def __gt__(self, other):
        """ GreaterThan is required to use '>' between 2 localization instances.

        :param other: the other localization to compare with.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------

    def __ne__(self, other):
        return not self == other

    # ---------------------------------------------------------------------

    def __le__(self, other):
        return self < other or self == other

    # ---------------------------------------------------------------------

    def __ge__(self, other):
        return self > other or self == other
