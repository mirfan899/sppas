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

    src.anndata.annlocation.localization.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sppas.src.utils.datatype import sppasType

from ..anndataexc import AnnDataTypeError
from ..basecompare import sppasBaseCompare

from .point import sppasPoint
from .interval import sppasInterval
from .disjoint import sppasDisjoint


# ---------------------------------------------------------------------------


class sppasLocalizationCompare(sppasBaseCompare):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Comparison methods for sppasBaseLocalization.

    """
    def __init__(self):
        """ Create a sppasLocalizationCompare instance. """

        sppasBaseCompare.__init__(self)

        self.methods['rangefrom'] = sppasLocalizationCompare.rangefrom
        self.methods['rangeto'] = sppasLocalizationCompare.rangeto

    # -----------------------------------------------------------------------

    @staticmethod
    def rangefrom(localization, x):
        """ Return True if localization is starting at x or after.

        :param localization: (sppasBaseLocalization)
        :param x: (int, float, sppasPoint)
        :returns: (bool)

        """
        if (sppasType().is_number(x) or isinstance(x, sppasPoint)) is False:
            raise AnnDataTypeError(x, "int/float/sppasBaseLocalization")

        return sppasLocalizationCompare.__get_begin(localization) >= x

    # -----------------------------------------------------------------------

    @staticmethod
    def rangeto(localization, x):
        """ Return True if localization is ending at x or before.

        :param localization: (sppasBaseLocalization)
        :param x: (int, float, sppasPoint)
        :returns: (bool)

        """
        if (sppasType().is_number(x) or isinstance(x, sppasPoint)) is False:
            raise AnnDataTypeError(x, "int/float/sppasBaseLocalization")

        return sppasLocalizationCompare.__get_end(localization) <= x

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def __get_begin(localization):
        """ Return the begin point of a localization. """

        if isinstance(localization, sppasPoint):
            return localization
        elif isinstance(localization, (sppasInterval, sppasDisjoint)):
            return localization.get_begin()

        raise AnnDataTypeError(localization, "sppasBaseLocalization")

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_end(localization):
        """ Return the end point of a localization. """

        if isinstance(localization, sppasPoint):
            return localization
        elif isinstance(localization, (sppasInterval, sppasDisjoint)):
            return localization.get_end()

        raise AnnDataTypeError(localization, "sppasBaseLocalization")
