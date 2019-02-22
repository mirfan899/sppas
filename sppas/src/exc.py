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

    src.annotations.sppasexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Global exceptions for sppas.

"""

from sppas.src.config import globals_translation

# -----------------------------------------------------------------------

_ = globals_translation.gettext

# -----------------------------------------------------------------------

NEG_VALUE_ERROR = ":ERROR 010: "
INTERVAL_RANGE_ERROR = ":ERROR 012: "
RANGE_INDEX_ERROR = ":ERROR 014: "

IO_EXTENSION_ERROR = ":ERROR 110: "

# -----------------------------------------------------------------------


class NegativeValueError(ValueError):
    """:ERROR 010: NEG_VALUE_ERROR.

    Expected a positive value. Got {value}.

    """

    def __init__(self, value):
        self.parameter = NEG_VALUE_ERROR + \
                         (_(NEG_VALUE_ERROR)).format(value=value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class RangeBoundsException(ValueError):
    """:ERROR 012: INTERVAL_RANGE_ERROR.

    Min value {} is bigger than max value {}.'

    """

    def __init__(self, min_value, max_value):
        self.parameter = INTERVAL_RANGE_ERROR + \
                         (_(INTERVAL_RANGE_ERROR)).format(
                             min_value=min_value,
                             max_value=max_value)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class IndexRangeException(IndexError):
    """:ERROR 014: RANGE_INDEX_ERROR.

    List index {} out of range [{},{}].

    """

    def __init__(self, value, min_value, max_value):
        self.parameter = INTERVAL_RANGE_ERROR + \
                         (_(INTERVAL_RANGE_ERROR)).format(
                             value=value,
                             min_value=min_value,
                             max_value=max_value)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class IOExtensionException(IOError):
    """:ERROR 110: IO_EXTENSION_ERROR.

    Unknown extension for filename {:s}'

    """

    def __init__(self, filename):
        self.parameter = INTERVAL_RANGE_ERROR + \
                         (_(INTERVAL_RANGE_ERROR)).format(filename)

    def __str__(self):
        return repr(self.parameter)

