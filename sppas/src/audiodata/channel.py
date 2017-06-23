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

    src.audiodata.channel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from .audioframes import AudioFrames
from .audiodataexc import IntervalError, SampleWidthError

# ----------------------------------------------------------------------------


class Channel(object):
    """
    :author:       Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      A class to manage frames of an audio channel.

    """
    def __init__(self, framerate=0, sampwidth=0, frames=''):
        """ Constructor.

        :param framerate: (int) The frame rate of this channel, in Hertz.
        The recommended framerate value is 48,000;
        :param sampwidth: (int) 1 for 8 bits, 2 for 16 bits, 4 for 32 bits
        :param frames: (str) The frames represented by a string.

        """
        self._frames = frames
        self._framerate = framerate
        self._sampwidth = sampwidth
        self._position = 0

    # ----------------------------------------------------------------------
    # Setters
    # ----------------------------------------------------------------------

    def set_frames(self, frames):
        """ Set new frames to the channel.
        It is supposed the sampwidth and framerate are the same as the 
        current ones.

        :param frames: (str) the new frames

        """
        self._frames = frames

    # ----------------------------------------------------------------------

    def set_sampwidth(self, sampwidth):
        """ Set a new sampwidth to the channel.

        :param sampwidth: (int)

        """
        sampwidth = int(sampwidth)
        if sampwidth not in [1, 2, 4]:
            raise SampleWidthError(sampwidth)
        self._sampwidth = sampwidth

    # ----------------------------------------------------------------------

    def set_framerate(self, framerate):
        """ Set a new framerate to the channel.

        :param framerate: (int)

        """
        framerate = int(framerate)
        self._framerate = framerate

    # ----------------------------------------------------------------------
    # Getters
    # ----------------------------------------------------------------------

    def get_frames(self, chunck_size=None):
        """ Return some frames from the current position.

        :param chunck_size: (int) the size of the chunk to return
        :returns: (str) the frames

        """
        if chunck_size is None:
            return self._frames

        chunck_size = int(chunck_size)
        p = self._position
        m = len(self._frames)
        s = p*self._sampwidth
        e = min(m, s + chunck_size*self._sampwidth )
        f = ''.join(self._frames[i] for i in range(s, e))
        self._position = p + chunck_size

        return f

    # -----------------------------------------------------------------------

    def get_nframes(self):
        """ Return the number of frames.
        A frame has a length of (sampwidth) bytes.

        :returns: (int) the total number of frames

        """
        return len(self._frames)/self._sampwidth

    # -----------------------------------------------------------------------

    def get_framerate(self):
        """ Return the frame rate, in Hz.

        :returns: (int) the frame rate of the channel

        """
        return self._framerate

    # -----------------------------------------------------------------------

    def get_sampwidth(self):
        """ Return the sample width.

        :returns: (int) the sample width of the channel

        """
        return self._sampwidth

    # -----------------------------------------------------------------------

    def get_cross(self):
        """ Return the number of zero crossings.

        :returns: (int) number of zero crossing

        """
        a = AudioFrames(self._frames, self._sampwidth, 1)
        return a.cross()

    # -----------------------------------------------------------------------

    def rms(self):
        """ Return the root mean square of the channel.

        :returns: (int) the root mean square of the channel

        """
        a = AudioFrames(self._frames, self._sampwidth, 1)
        return a.rms()

    # -----------------------------------------------------------------------

    def clipping_rate(self, factor):
        """ Return the clipping rate of the frames.

        :param factor: (float) An interval to be more precise on clipping rate.
        It will consider that all frames outside the interval are clipped.
        Factor has to be between 0 and 1.
        :returns: (float) the clipping rate

        """
        a = AudioFrames(self._frames, self._sampwidth, 1)
        return a.clipping_rate(factor)

    # -----------------------------------------------------------------------

    def get_duration(self):
        """ Return the duration of the channel, in seconds.

        :returns: (float) the duration of the channel

        """
        return float(self.get_nframes())/float(self.get_framerate())

    # -----------------------------------------------------------------------

    def extract_fragment(self, begin=None, end=None):
        """ Extract a fragment between the beginning and the end.

        :param begin: (int: number of frames) the beginning of the fragment to extract
        :param end: (int: number of frames) the end of the fragment to extract

        :returns: (Channel) the fragment extracted.

        """
        nframes = self.get_nframes()
        if begin is None:
            begin = 0
        if end is None:
            end = nframes

        begin = int(begin)
        end = int(end)
        if end < 0 or end > nframes:
            end = nframes

        if begin > nframes:
            return Channel(self._framerate, self._sampwidth, "")
        if begin < 0:
            begin = 0

        if begin == 0 and end == nframes:
            return Channel(self._framerate, self._sampwidth, self._frames)

        if begin > end:
            raise IntervalError(begin, end)

        pos_begin = int(begin*self._sampwidth)
        if end == self.get_nframes():
            frames = self._frames[pos_begin:]
        else:
            pos_end = int(end*self._sampwidth)
            frames = self._frames[pos_begin:pos_end]

        return Channel(self._framerate, self._sampwidth, frames)

    # -----------------------------------------------------------------------
    # Manage position
    # -----------------------------------------------------------------------

    def tell(self):
        """ Return the current position.

        :returns: (int) the current position

        """
        return self._position

    # ------------------------------------------------------------------------

    def rewind(self):
        """ Set the position to 0. """

        self._position = 0

    # ------------------------------------------------------------------------

    def seek(self, position):
        """ Fix the current position.

        :param position: (int)

        """
        self._position = max(0, min(position, len(self._frames)/self._sampwidth))

    # ------------------------------------------------------------------------

    def __str__(self):
        return "Channel: framerate %d, sampleswidth %d, position %d, nframes %d" % \
               (self._framerate, self._sampwidth, self._position, len(self._frames))
