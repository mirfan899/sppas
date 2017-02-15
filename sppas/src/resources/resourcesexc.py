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

    src.calculus.resourcesexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for resources package.

"""
from . import t

# -----------------------------------------------------------------------

FILE_IO_ERROR = ":ERROR 5010: "
FILE_FORMAT_ERROR = ":ERROR 5015: "
NGRAM_RANGE_ERROR = ":ERROR 5020: "
GAP_RANGE_ERROR = ":ERROR 5022: "
SCORE_RANGE_ERROR = ":ERROR 5024: "
DUMP_EXTENSION_ERROR = ":ERROR 5030: "

# -----------------------------------------------------------------------


class FileIOError(Exception):
    """ :ERROR 5010: Error while trying to open and read the file: {:s}. """

    def __init__(self, filename):
        self.parameter = FILE_IO_ERROR + (t.gettext(FILE_IO_ERROR)).format(filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class FileFormatError(ValueError):
    """ :ERROR 5015: Read file failed due to the following error at line number {:d}: {:s}. """

    def __init__(self, line, filename):
        line = int(line)
        self.parameter = FILE_FORMAT_ERROR + (t.gettext(FILE_FORMAT_ERROR)).format(line, filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class NgramRangeError(ValueError):
    """ :ERROR 5020: The n value of n-grams pattern matching must range [1;{:d}]. Got {:d}. """

    def __init__(self, maxi, value):
        maxi = int(maxi)
        value = int(value)
        self.parameter = NGRAM_RANGE_ERROR + (t.gettext(NGRAM_RANGE_ERROR)).format(maxi, value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class GapRangeError(ValueError):
    """ :ERROR 5022: The gap value of pattern matching must range [0;{:d}]. Got {:d}. """

    def __init__(self, maxi, value):
        maxi = int(maxi)
        value = int(value)
        self.parameter = GAP_RANGE_ERROR + (t.gettext(GAP_RANGE_ERROR)).format(maxi, value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ScoreRangeError(ValueError):
    """ :ERROR 5024: The score value of unigrams pattern matching must range [0;1]. Got {:f}. """

    def __init__(self, value):
        value = float(value)
        self.parameter = SCORE_RANGE_ERROR + (t.gettext(SCORE_RANGE_ERROR)).format(value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class DumpExtensionError(ValueError):
    """ :ERROR 5030: The dump file can't have the same extension as the ASCII file ({:s}). """

    def __init__(self, extension):
        self.parameter = DUMP_EXTENSION_ERROR + (t.gettext(DUMP_EXTENSION_ERROR)).format(extension)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------
