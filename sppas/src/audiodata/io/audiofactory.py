#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: audiofactory.py
# ----------------------------------------------------------------------------

from waveio  import WaveIO
from aiff    import AiffIO
from sunau   import SunauIO

# ----------------------------------------------------------------------------

class AudioFactory(object):
    """
    @authors:      Nicolas Chazeau, Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Factory for AudioPCM.

    """

    AUDIO_TYPES = {
        "wav" : WaveIO,
        "wave": WaveIO,
        "aiff": AiffIO,
        "au"  : SunauIO
        }


    @staticmethod
    def NewAudio(audio_type):
        """
        Return a new AudioPCM according to the format.

        @param audio_type (str) a file extension.
        @return AudioPCM

        """
        try:
            return AudioFactory.AUDIO_TYPES[audio_type.lower()]()
        except KeyError:
            raise Exception("Unrecognized AudioPCM type: %s" % audio_type)

# ----------------------------------------------------------------------------
