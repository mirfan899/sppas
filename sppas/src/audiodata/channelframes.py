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
# File: channelframes.py
# ---------------------------------------------------------------------------

from audioframes import AudioFrames

# ---------------------------------------------------------------------------

class ChannelFrames( object ):
    """
    @authors:      Nicolas Chazeau, Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      An utility for frames of one channel only.

    """
    def __init__(self, frames=""):
        """
        Constructor.

        @param frames (str) Frames that must be MONO ONLY.

        """
        self.frames = frames

    # -----------------------------------------------------------------------

    def get_frames(self):
        """
        Return the frames

        @return the frames

        """
        return self.frames

    # ----------------------------------------------------------------------------

    def set_frames(self, frames):
        """
        Set the frames.

        @param the frames to set

        """
        self.frames = frames

    # ----------------------------------------------------------------------------

    def append_silence(self, nframes):
        """
        Create n frames of silence and append it to the frames.

        @param nframes (int) the number of frames of silence to append

        """
        nframes = int(nframes)
        if nframes < 0:
            raise ValueError("Expected a number of frames. Got %s"%nframes)
        if nframes == 0:
            return

        self.frames += " \x00"*nframes

    # ----------------------------------------------------------------------------

    def resample(self, sampwidth, rate, newrate):
        """
        Resample the frames with a new frame rate.

        @param sampwidth (int) sample width of the frames.
        @param rate (int) current frame rate of the frames
        @param newrate (int) new frame rate of the frames

        """
        a = AudioFrames( self.frames, sampwidth, 1)
        self.frames = a.resample(rate, newrate)

    # ----------------------------------------------------------------------------

    def change_sampwidth(self, sampwidth, newsampwidth):
        """
        Change the number of bytes used to encode the frames.

        @param current sampwidth (int) sample width of the frames.
        (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)
        @param newsampwidth (int) new sample width of the frames.
        (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)

        """
        a = AudioFrames( self.frames, sampwidth, 1)
        self.frames = a.changesampwidth(newsampwidth)

    # ----------------------------------------------------------------------------
