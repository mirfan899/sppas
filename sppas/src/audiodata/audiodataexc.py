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

    src.audiodata.audiodataexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for audiodata package.

"""
from . import t

ERROR = ":ERROR 2000: "
IO_ERROR = ":ERROR 2010: "
DATA_ERROR = ":ERROR 2015: "
INDEX_ERROR = ":ERROR 2020: "


class AudioError(Exception):
    """ :ERROR 2000: No audio file is defined. """

    def __init__(self):
        self.parameter = ERROR + (t.ugettext(ERROR))

    def __str__(self):
        return repr(self.parameter)


class AudioIOError(IOError):
    """ :ERROR 2010: Opening, reading or writing error. """

    def __init__(self, message="", filename=None):
        if filename:
            self.parameter = IO_ERROR + \
                             (t.gettext(IO_ERROR)).format((filename, message))
        else:
            self.parameter = IO_ERROR + \
                             (t.gettext(IO_ERROR)).format(message)

    def __str__(self):
        return repr(self.parameter)


class AudioDataError(Exception):
    """ :ERROR 2015: No data or corrupted data in the audio file. """

    def __init__(self, filename):
        self.parameter = ERROR + \
                         (t.gettext(ERROR)).format(filename)

    def __str__(self):
        return repr(self.parameter)


class AudioValueError(ValueError):
    """ :ERROR 2020: {:d} is not a right index of channel." """

    def __init__(self, index):
        self.parameter = INDEX_ERROR + \
                         (t.gettext(INDEX_ERROR)).format(index)

    def __str__(self):
        return repr(self.parameter)
