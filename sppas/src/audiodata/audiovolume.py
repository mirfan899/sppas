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
# File: audiovolume.py
# ---------------------------------------------------------------------------

from audioframes import AudioFrames
from basevolume  import BaseVolume

# ----------------------------------------------------------------------------

class AudioVolume( BaseVolume ) :
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      A class to estimates stats of the volume of an audio channel.

    The volume is the estimation of RMS values, sampled with a window of 10ms.

    """
    def __init__(self, audio, winlen=0.01):
        """
        Constructor.

        @param audio (AudioPCM) The audio to work on.
        @param winlen (float) Window length to estimate the volume.

        """
        BaseVolume.__init__(self)
        self.winlen = winlen

        # Remember current position
        pos = audio.tell()

        # Rewind to the beginning
        audio.rewind()

        # Find the rms values (explore all frames)
        nbframes = int(winlen * audio.get_framerate())

        while audio.tell() < audio.get_nframes():
            frames = audio.read_frames( nbframes )
            a = AudioFrames(frames, audio.get_sampwidth(), audio.get_nchannels())
            self.volumes.append( a.rms() )

        # Returns to the position where we was before
        audio.seek(pos)

        self.rms = audio.rms()

    # -----------------------------------------------------------------------
