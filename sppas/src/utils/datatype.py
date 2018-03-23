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

    src.utils.sppasType.py
    ~~~~~~~~~~~~~~~~~~~~~~

    Utilities to check data types.

"""


class sppasType(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Utility class to check data type.

    """

    @staticmethod
    def is_number(entry):
        """ Check if the entry is numeric.

        :param entry: (any type)
        :returns: (bool)

        """
        try:
            float(entry)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(entry)
            return True
        except (TypeError, ValueError):
            pass

        return False

    # -----------------------------------------------------------------------

    @staticmethod
    def is_dict(entry):
        """ Check if the entry is of any type of dictionary.

        :param entry: (any type)
        :returns: (bool)

        """
        if type(entry) is dict:
            return True

        if "collections." in str(type(entry)):
            return True

        return False
