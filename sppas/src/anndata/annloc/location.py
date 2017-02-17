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

    """
    def __init__(self, localization, score=None):
        """ Create a new sppasLocation instance and add the entry.

        :param localization: (Localization or list of Localization)

        """
        self.__locations = list()
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

        """
        if isinstance(sppasBaseLocalization) is False:
            raise AnnDataTypeError(localization, "sppasBaseLocalization")

        if localization not in self.__locations:
            self.__locations.append((localization, score))

    # -----------------------------------------------------------------------

    def get_best(self):
        """ Return the best Localization, i.e.
        the localization with the better score.

        :returns: a localization

        """
        if len(self.__locations) == 0:
            return self.__locations[0][0]

        best = max([x for x in self.__locations if x[1] is not None])
        return best[0]

    # -----------------------------------------------------------------------

    def get(self):
        """ Return the list of localizations and their scores. """

        return self.__locations

    # -----------------------------------------------------------------------

    def __repr__(self, *args, **kwargs):
        return "Locations: {:s}".format("; ".join([str(i) for i in self.__locations]))

    # ------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "{:s}".format("; ".join([str(i) for i in self.__locations]))

    # -----------------------------------------------------------------------

    def __iter__(self):
        for a in self.__locations:
            yield a

    # -----------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__locations[i]

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__locations)
