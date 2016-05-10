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
# File: monofragment.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Nicolas Chazeau (n.chazeau94@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import audioutils
import cmath

# ---------------------------------------------------------------------------

class MonoFragment:
    """
    @authors: Nicolas Chazeau
    @contact: n.chazeau94@gmail.com
    @license: GPL, v3
    @summary: An utilitary for monochannel frames.
    """

    def __init__(self, frames = ""):
        """
        Constructor.
        frames must be MONO channel ONLY.
        """
        self.frames = frames

    # End __init__
    # -----------------------------------------------------------------------

    def create_silence(self, nframes):
        """
        Create nframes of silence and append it to the frames

        @param the number of frames of silence to create

        """
        silence = ""
        for i in range(nframes):
            silence += " \x00"
        self.frames += silence

    # ----------------------------------------------------------------------------

    def resample(self, sampwidth, rate, newrate):
        """
        Resample the frames with a new frame rate

        @param sampwidth (int) sample width of the frames.
        @param rate (int) current frame rate of the frames
        @param newrate (int) new frame rate of the frames

        """
        self.frames = audioutils.resample(self.frames, sampwidth, 1, rate, newrate)

    # ----------------------------------------------------------------------------

    def changesampwidth(self, sampwidth, newsampwidth):
        """
        Change the number of bytes used to encode the frames

        @param current sampwidth (int) sample width of the frames. (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)
        @param newsampwidth (int) new sample width of the frames. (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)

        """
        self.frames = audioutils.changesampwidth(self.frames, sampwidth, newsampwidth)

    # ----------------------------------------------------------------------------

    def get_frames(self):
        """
        Return the frames

        @return the frames

        """
        return self.frames

    # ----------------------------------------------------------------------------

    def set_frames(self, frames):
        """
        Set the frames of the MonoFragment

        @param the frames to set

        """
        self.frames = frames

    # ----------------------------------------------------------------------------
        # ----------------------------------------------------------------------------