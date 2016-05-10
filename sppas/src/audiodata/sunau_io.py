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
# File: sunau_io.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import sunau
from audio import AudioPCM
from audio import NO_AUDIO_MSG

# ---------------------------------------------------------------------------

class SunauIO( AudioPCM ):
    """
    @authors: Nicolas Chazeau, Brigitte Bigi
    @contact: n.chazeau94@gmail.com, brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: An Sun AU file open/save utility class.

    """

    def __init__(self):
        """
        Constructor.

        """
        AudioPCM.__init__(self)

    # ------------------------------------------------------------------------

    def open(self, filename):
        """
        Get an audio from a Audio Interchange File Format file.

        @param filename (string) input file name.

        """

        # Use the standard wave library to load the wave file
        # open method returns a Wave_read() object
        self.audiofp = sunau.open( filename, "r")

        # Find out how many frames the frameduration second value is
        self.nbreadframes = int(self.frameduration * self.audiofp.getframerate())

    # -----------------------------------------------------------------------

    def save(self, filename):
        """
        Write an audio content as a Audio Interchange File Format file.

        @param filename (string) output filename.

        """
        if self.audiofp:
            self.save_fragment( filename, self.audiofp.readframes(self.audiofp.getnframes()) )

        elif len(self) == 1:
            channel = self.channels[0]
            f = sunau.Au_write( filename )
            f.setnchannels(1)
            f.setsampwidth(channel.get_sampwidth())
            f.setframerate(channel.get_framerate())
            try:
                f.writeframes( channel.frames )
            finally:
                f.close()

        else:
            self.verify_channels()

            frames = ""
            for i in xrange(0, self.channels[0].get_nframes()*self.channels[0].get_sampwidth(), self.channels[0].get_sampwidth()):
                for j in xrange(len(self.channels)):
                        frames += self.channels[j].frames[i:i+self.channels[0].get_sampwidth()]

            f = sunau.Au_write( filename )
            f.setnchannels(len(self.channels))
            f.setsampwidth(self.channels[0].get_sampwidth())
            f.setframerate(self.channels[0].get_framerate())
            try:
                f.writeframes( frames )
            finally:
                f.close()

    # -----------------------------------------------------------------------


    def save_fragment(self, filename, frames):
        """
        Write an audio content as a Audio Interchange File Format file.

        @param filename (string) output filename.
        @param frames (string) the frames to write

        """
        f = sunau.Au_write( filename )
        f.setnchannels(self.get_nchannels())
        f.setsampwidth(self.get_sampwidth())
        f.setframerate(self.get_framerate())
        try:
            f.writeframes( frames )
        finally:
            f.close()

# ---------------------------------------------------------------------------