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
ANN_DATA_EQ_TYPE_ERROR = ":ERROR 1105: "
ANN_DATA_NEG_VALUE_ERROR = ":ERROR 1110: "
INTERVAL_BOUNDS_ERROR = ":ERROR 1120: "
CTRL_VOCAB_CONTAINS_ERROR = ":ERROR 1130: "

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
        self.parameter = ANN_DATA_TYPE_ERROR + \
                         (t.gettext(ANN_DATA_TYPE_ERROR)).format(rtype, expected)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataEqTypeError(TypeError):
    """ :ERROR 1105: {!s:s} is not of the same type as {!s:s}. """

    def __init__(self, obj, obj_ref):
        self.parameter = ANN_DATA_EQ_TYPE_ERROR + \
                         (t.gettext(ANN_DATA_EQ_TYPE_ERROR)).format(obj, obj_ref)

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


class IntervalBoundsError(ValueError):
    """ :ERROR 1120: The begin must be strictly lesser than the end in an interval. Got: [{:s};{:s}]. """

    def __init__(self, begin, end):
        self.parameter = INTERVAL_BOUNDS_ERROR + \
                         (t.gettext(INTERVAL_BOUNDS_ERROR)).format(begin, end)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class CtrlVocabContainsError(ValueError):
    """ :ERROR 1130: {:s} is not part of the controlled vocabulary. """

    def __init__(self, tag):
        self.parameter = CTRL_VOCAB_CONTAINS_ERROR + \
                         (t.gettext(CTRL_VOCAB_CONTAINS_ERROR)).format(tag)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------
