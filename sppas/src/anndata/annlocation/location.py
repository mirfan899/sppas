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

    src.anndata.annloc.location.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from ..anndataexc import AnnDataTypeError
from .localization import sppasBaseLocalization

# ---------------------------------------------------------------------------


class sppasLocation(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Represents the location of an Annotation.

    The location is a set of alternative localizations.

    """
    def __init__(self, localization, score=None):
        """ Create a new sppasLocation instance and add the entry.

        :param localization: (Localization)
        :param score: (float)

        """
        self.__localizations = list()
        self.__fct = max

        self.append(localization, score)

    # -----------------------------------------------------------------------

    def get_function_score(self):
        """ Return the function used to compare scores. """

        return self.__fct

    # -----------------------------------------------------------------------

    def set_function_score(self, fct_name):
        """ Set a new function to compare scores.

        :param fct_name: one of min or max.

        """
        if fct_name not in (min, max):
            raise AnnDataTypeError(fct_name, "min, max")

        self.__fct = fct_name

    # -----------------------------------------------------------------------

    def append(self, localization, score=None):
        """ Add a localization into the list.

        :param localization: (Localization) the localization to append
        :param score: (float)

        """
        if isinstance(localization, sppasBaseLocalization) is False:
            raise AnnDataTypeError(localization, "sppasBaseLocalization")

        if localization not in self.__localizations:
            # check types consistency.
            if len(self.__localizations) > 0:
                if self.is_point() != localization.is_point():
                    raise AnnDataTypeError(localization, "sppasPoint")
                if self.is_interval() != localization.is_interval():
                    raise AnnDataTypeError(localization, "sppasInterval")
                if self.is_disjoint() != localization.is_disjoint():
                    raise AnnDataTypeError(localization, "sppasDisjoint")

            self.__localizations.append((localization, score))

    # -----------------------------------------------------------------------

    def get_best(self):
        """ Return the best Localization, i.e.
        the localization with the better score.

        :returns: a localization

        """
        if len(self.__localizations) == 1:
            return self.__localizations[0][0]

        _maxt = self.__localizations[0][0]
        _maxscore = self.__localizations[0][1]
        for (t, s) in reversed(self.__localizations):
            if _maxscore is None or (s is not None and s > _maxscore):
                _maxscore = s
                _maxt = t

        return _maxt

    # -----------------------------------------------------------------------

    def is_point(self):
        """ Return True if the location is made of sppasPoint localizations. """

        l = self.__localizations[0][0]
        return l.is_point()

    # -----------------------------------------------------------------------

    def is_interval(self):
        """ Return True if the location is made of sppasInterval localizations. """

        l = self.__localizations[0][0]
        return l.is_interval()

    # -----------------------------------------------------------------------

    def is_disjoint(self):
        """ Return True if the location is made of sppasDisjoint localizations. """

        l = self.__localizations[0][0]
        return l.is_disjoint()

    # -----------------------------------------------------------------------

    def contains(self, point):
        """ Return True if the localization is in the list. """

        if self.is_point():
            return any([point == l[0] for l in self.__localizations])
        else:
            return any([l[0].is_bound(point) for l in self.__localizations])

    # -----------------------------------------------------------------------

    def __repr__(self, *args, **kwargs):
        st = ""
        for t, s in self.__localizations:
            st += "sppasLocalization({!s:s}, score={:s}), ".format(t, s)
        return st

    # ------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        st = ""
        for t, s in self.__localizations:
            st += "{!s:s}, {:s} ; ".format(t, s)
        return st

    # -----------------------------------------------------------------------

    def __iter__(self):
        for l in self.__localizations:
            yield l

    # -----------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__localizations[i]

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__localizations)

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        if len(self.__localizations) != len(other):
            return False
        for (l1, l2) in zip(self.__localizations, other):
            if l1[0] != l2[0] or l1[1] != l2[1]:
                return False
        return True
