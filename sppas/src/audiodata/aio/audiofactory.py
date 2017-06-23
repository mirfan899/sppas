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

    src.audiodata.aio.audiofactory.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Factory class for creating an AudioPCM.

"""
from .waveio import WaveIO
from .aiffio import AiffIO
from .sunauio import SunauIO

# ----------------------------------------------------------------------------


class AudioFactory(object):
    """
    :author:       Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Factory for AudioPCM.

    """
    AUDIO_TYPES = {
        "wav": WaveIO,
        "wave": WaveIO,
        "aif": AiffIO,
        "aiff": AiffIO,
        "au": SunauIO
        }

    @staticmethod
    def new_audio_pcm(audio_type):
        """ Return a new AudioPCM according to the format.

        :param audio_type: (str) a file extension.
        :returns: AudioPCM

        """
        try:
            return AudioFactory.AUDIO_TYPES[audio_type.lower()]()
        except KeyError:
            raise Exception("Unrecognized AudioPCM type: %s" % audio_type)
