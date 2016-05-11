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
# File: channel.py
# ----------------------------------------------------------------------------

from audiodata import audioutils

# ----------------------------------------------------------------------------

class Channel:
    """
    @authors:      Nicolas Chazeau, Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      A class to manage frames of an audio channel.

    """
    def __init__(self, framerate=0, sampwidth=0, frames=''):
        """
        Constructor.

        @param framerate (int) The frame rate of this channel, in Hertz.
        The recommended framerate value is 48,000;
        @param sampwidth (int)
        @param frames (str) The frames represented by a string.

        """
        self.frames    = frames
        self.framerate = framerate
        self.sampwidth = sampwidth
        self.position  = 0

        self.frameduration = 0.01 # for rms estimation
        self.nbreadframes = int(self.frameduration*self.framerate)

    # ----------------------------------------------------------------------
    # Setters
    # ----------------------------------------------------------------------

    def set_frames(self, frames):
        """
        Set new frames to the channel.
        It is supposed the sampwidth and framerate are the same as the current ones.

        @param frames (string) the new frames

        """
        self.frames = frames

    # ----------------------------------------------------------------------
    # Getters
    # ----------------------------------------------------------------------

    def get_frames(self, chuncksize):
        """
        Return chuncksize frames from the current position.

        @param chuncksize (int) the size of the chunk to return
        @return the frames

        """
        p = self.position
        m = len(self.frames)
        f = ''.join( self.frames[i] for i in range( p*self.sampwidth,min(m, p*self.sampwidth + chuncksize*self.sampwidth ) ) )
        self.position = p + chuncksize

        return f

    # -----------------------------------------------------------------------

    def get_nframes(self):
        """
        Return the number of frames (a frame has a length of (sampwidth) bytes).

        @return the total number of frames

        """
        return len(self.frames)/self.sampwidth

    # -----------------------------------------------------------------------

    def get_framerate(self):
        """
        Return the frame rate.

        @return the frame rate of the channel

        """
        return self.framerate

    # -----------------------------------------------------------------------

    def get_sampwidth(self):
        """
        Return the sample width.

        @return the sample width of the channel

        """
        return self.sampwidth

    # -----------------------------------------------------------------------

    def get_cross(self):
        """
        Return the number of zero crossings.

        @return number of zero crossing

        """
        return audioutils.cross( self.frames, self.sampwidth )
        #audioop.cross( self.frames )

    # -----------------------------------------------------------------------

    def get_rms(self):
        """
        Return the root mean square of the channel.

        @return the root mean square of the channel

        """
        return audioutils.get_rms( self.frames, self.sampwidth )

    # -----------------------------------------------------------------------

    def get_frameduration(self):
        """
        Return the frame-duration set by default used to perform windowing method.

        @return the frame duration

        """
        return self.frameduration

    # -----------------------------------------------------------------------

    def get_clipping_rate(self, factor):
        """
        Return the clipping rate of the frames

        @param factor (float) An interval to be more precise on clipping rate. It will consider that all frames outside the interval are clipped. Factor has to be between 0 and 1.
        @return the clipping rate

        """
        return audioutils.get_clipping_rate(self.frames, self.sampwidth, factor)

    # -----------------------------------------------------------------------

    def get_duration(self):
        """
        Return the duration of the channel.

        @return the duration of the channel

        """
        return float(self.get_nframes())/float(self.get_framerate())

    # -----------------------------------------------------------------------
    # Manage position
    # -----------------------------------------------------------------------

    def tell(self):
        """
        Return the current position.

        @return the current position

        """
        return self.position


    def rewind(self):
        """
        Return at the beginning of the frames.

        """
        self.position = 0


    def seek(self, position):
        """
        Fix the current position.

        @param the position to set

        """
        self.position = max(0, min(position, len(self.frames)/self.sampwidth))

    # ------------------------------------------------------------------------

    def __str__(self):
        return "Channel: framerate %d, sampleswidth %d, position %d, nframes %d"%( self.framerate,self.sampwidth,self.position,len(self.frames) )

# ----------------------------------------------------------------------------
