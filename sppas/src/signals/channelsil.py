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
# File: channelsil.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import signals
from signals import audioutils

# ----------------------------------------------------------------------------

class ChannelSil:
    """
    @authors: Brigitte Bigi, Nicolas Chazeau
    @contact: brigitte.bigi@gmail.com, n.chazeau94@gmail.com
    @license: GPL
    @summary: This class implements the silence finding on channels.

    """
    def __init__(self, channel, m=0.3):
        """
        Create a ChannelSil audio instance.

        @param channel (Channel) the input channel object
        @param m (float) is the minimum track duration (in seconds)

        """
        self.channel = channel
        self.silence   = None
        self.minlenght = m

    # ------------------------------------------------------------------

    def set_mintrack(self, m):
        """
        Set a new minimum track duration.

        @param m (float): duration (in seconds)

        """
        self.minlenght = float(m)

    # ------------------------------------------------------------------
    # Silence detection
    # ------------------------------------------------------------------

    def tracks(self):
        """
        Yield tuples (from,to) of the tracks.

        """
        from_pos = 0
        if self.silence is None or len(self.silence)==0:
        # No silence: Only one track!
            yield 0,self.channel.get_nframes()
            return
        # At least one silence
        for to_pos, next_from in self.silence:
            if (to_pos - from_pos) >= (self.minlenght * self.channel.get_framerate()):
                # Track is long enough to be considered a track.
                yield int(from_pos), int(to_pos)
            from_pos = next_from

        # Last track after the last silence
        # (if the silence does not end at the end of the channel)
        to_pos = self.channel.get_nframes()
        if (to_pos - from_pos) >= (self.minlenght * self.channel.get_framerate()):
            yield int(from_pos), int(to_pos)

    # ------------------------------------------------------------------

    def track_data(self, tracks):
        """
        Get the track data: a set of frames for each track.

        """
        nframes = self.channel.get_nframes()
        for from_pos, to_pos in tracks:
            if nframes < from_pos:
                # Accept a "DELTA" of 10 frames, in case of corrupted data.
                if nframes < from_pos-10:
                    raise ValueError("Position %d not in range(%d)" % (from_pos, nframes))
                else:
                    from_pos = nframes
            # Go to the provided position
            self.channel.seek(from_pos)
            # Keep in mind the related frames
            yield self.channel.get_frames(to_pos - from_pos)

    # ------------------------------------------------------------------

    def get_silence(self, p=0.250, v=150, s=0.0):
        """
        Get silences from an audio file.

        @param p (float) Minimum silence duration in seconds
        @param v (int) Expected minimum volume (rms value)
        @param s (float) Shift delta duration in seconds
        @return a set of frames corresponding to silences.

        """
        self.silence = []

        # Once silence has been found, continue searching in this interval
        afterloop_frames = int((self.channel.get_frameduration()/2) * self.channel.get_framerate())
        initpos = i = self.channel.tell()

        # This scans the file in steps of frames whether a section's volume
        # is lower than silence_cap, if it is it is written to silence.
        while i < self.channel.get_nframes():

            curframe = self.channel.get_frames(self.channel.nbreadframes)
            volume   = audioutils.get_rms(curframe, self.channel.get_sampwidth())

            if volume < v:

                # Continue searching in smaller steps whether the silence is
                # longer than read frames but smaller than read frames * 2.
                while volume < v and self.channel.tell() < self.channel.get_nframes():
                    curframe = self.channel.get_frames(afterloop_frames)
                    volume   = audioutils.get_rms(curframe, self.channel.get_sampwidth())

                # If the last sequence of silence ends where the new one starts
                # it's a continuous range.
                if self.silence and self.silence[-1][1] == i:
                    self.silence[-1][1] = self.channel.tell()
                else:
                # append if silence is long enough
                    duree = self.channel.tell() - i
                    nbmin = int( (p+s) * self.channel.get_framerate())
                    if duree > nbmin:
                        # Adjust silence start-pos
                        __startpos = i + ( s * self.channel.get_framerate() )
                        # Adjust silence end-pos
                        __endpos = self.channel.tell() - ( s * self.channel.get_framerate() )
                        self.silence.append([__startpos, __endpos])

            i = self.channel.tell()

        # Return the position in the file to where it was when we got it.
        self.channel.seek(initpos)

    # ------------------------------------------------------------------

    def set_silence(self, silence):
        self.silence = silence

# ----------------------------------------------------------------------
