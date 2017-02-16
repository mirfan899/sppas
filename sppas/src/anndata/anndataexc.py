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

    src.anndata.anndataexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for anndata package.

"""
from . import t

ANN_DATA_ERROR = ":ERROR 1000: "
ANN_DATA_TYPE_ERROR = ":ERROR 1100: "
ANN_DATA_NEG_VALUE_ERROR = ":ERROR 1110: "

# -----------------------------------------------------------------------


class AnnDataError(Exception):
    """ :ERROR 1000: No annotated data file is defined. """

    def __init__(self):
        self.parameter = ANN_DATA_ERROR + (t.gettext(ANN_DATA_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataTypeError(TypeError):
    """ :ERROR 1100: {!s:s} is not of the expected type '{:s}'. """

    def __init__(self, rtype, expected):
        self.parameter = ANN_DATA_TYPE_ERROR + (t.gettext(ANN_DATA_TYPE_ERROR)).format(rtype, expected)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataNegValueError(ValueError):
    """ :ERROR 1110: Expected a positive value. Got '{:f}'. """

    def __init__(self, value):
        self.parameter = ANN_DATA_NEG_VALUE_ERROR + \
                         (t.gettext(ANN_DATA_NEG_VALUE_ERROR)).format(value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------
