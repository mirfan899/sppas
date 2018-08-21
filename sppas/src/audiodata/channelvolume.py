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

    src.audiodata.channelvolume.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from .audioframes import sppasAudioFrames
from .basevolume import sppasBaseVolume

# ----------------------------------------------------------------------------


class sppasChannelVolume(sppasBaseVolume):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    :summary:      A class to estimates stats of the volume of an audio channel.

    The volume is the estimation of RMS values, sampled with a window of 10ms.

    """
    def __init__(self, channel, win_len=0.01):
        """Constructor.

        :param channel: (sppasChannel) The channel to work on.
        :param win_len: (float) Window length to estimate the volume.

        """
        sppasBaseVolume.__init__(self, win_len)

        # Remember current position
        pos = channel.tell()

        # Rewind to the beginning
        channel.rewind()

        # Constants
        nbframes = int(win_len * channel.get_framerate())
        nbvols = int(channel.get_duration()/win_len) + 1
        self._volumes = [0]*nbvols

        for i in range(nbvols):
            frames = channel.get_frames(nbframes)
            a = sppasAudioFrames(frames, channel.get_sampwidth(), 1)
            self._volumes[i] = a.rms()

        if self._volumes[-1] == 0:
            self._volumes.pop()

        # Returns to the position where we was before
        channel.seek(pos)

        self._rms = channel.rms()
