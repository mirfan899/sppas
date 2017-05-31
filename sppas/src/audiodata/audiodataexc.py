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

AUDIO_ERROR = ":ERROR 2000: "
IO_ERROR = ":ERROR 2010: "
DATA_ERROR = ":ERROR 2015: "
INDEX_ERROR = ":ERROR 2020: "
INTERVAL_ERROR = ":ERROR 2025: "
CHANNEL_ERROR = ":ERROR 2050: "
MIX_SAMPLEWIDTH = ":ERROR 2060: "
MIX_FRAMERATE = ":ERROR 2061: "
MIX_NFRAMES = ":ERROR 2062: "
SAMPLEWIDTH_ERROR = ":ERROR 2070: "

# -----------------------------------------------------------------------


class AudioError(Exception):
    """ :ERROR 2000: No audio file is defined. """

    def __init__(self):
        self.parameter = AUDIO_ERROR + (t.gettext(AUDIO_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AudioIOError(IOError):
    """ :ERROR 2010: Opening, reading or writing error. """

    def __init__(self, message="", filename=None):
        if filename:
            self.parameter = IO_ERROR + \
                             (t.gettext(IO_ERROR)).format(filename=filename, message=message)
        else:
            self.parameter = IO_ERROR + \
                             (t.gettext(IO_ERROR)).format(filename="", message=message)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AudioDataError(Exception):
    """ :ERROR 2015: No data or corrupted data in the audio file {filename}. """

    def __init__(self, filename):
        self.parameter = DATA_ERROR + \
                         (t.gettext(DATA_ERROR)).format(filename=filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ChannelIndexError(ValueError):
    """ :ERROR 2020: {number} is not a right index of channel. """

    def __init__(self, index):
        index = int(index)
        self.parameter = INDEX_ERROR + (t.gettext(INDEX_ERROR)).format(number=index)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class IntervalError(ValueError):
    """ :ERROR 2025: From {value1} to {value2} is not a proper interval. """

    def __init__(self, value1, value2):
        value1 = int(value1)
        value2 = int(value2)
        self.parameter = INTERVAL_ERROR + \
                         (t.gettext(INTERVAL_ERROR)).format(value1=value1, value2=value2)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ChannelError(Exception):
    """ :ERROR 2050: No channel defined. """

    def __init__(self):
        self.parameter = CHANNEL_ERROR + (t.gettext(CHANNEL_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class MixChannelError(ValueError):
    """ :ERROR 2060 to 2062: """

    def __init__(self, value=0):
        value = int(value)
        if value == 1:
            self.parameter = MIX_SAMPLEWIDTH + (t.gettext(MIX_SAMPLEWIDTH))
        elif value == 2:
            self.parameter = MIX_FRAMERATE + (t.gettext(MIX_FRAMERATE))
        elif value == 3:
            self.parameter = MIX_NFRAMES + (t.gettext(MIX_NFRAMES))
        else:
            self.parameter = CHANNEL_ERROR + (t.gettext(CHANNEL_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class SampleWidthError(ValueError):
    """ :ERROR 2070: Invalid sample width {value}. """

    def __init__(self, value):
        value = int(value)
        self.parameter = SAMPLEWIDTH_ERROR +\
                         (t.gettext(SAMPLEWIDTH_ERROR)).format(value=value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------
