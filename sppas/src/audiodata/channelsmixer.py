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
# File: channelsmixer.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Nicolas Chazeau (n.chazeau94@gmail.com), Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import struct

from audiodata.channel import Channel
from audiodata import audioutils

# ---------------------------------------------------------------------------

def unpack_data( data, sampwidth ):
    if sampwidth == 4 :
        newdata = struct.unpack("<l", data)
    elif sampwidth == 2 :
        newdata = struct.unpack("<h", data)
    else :
        newdata = struct.unpack("B",  data)
        newdata = [ s - 128 for s in data ]
    return newdata

# ---------------------------------------------------------------------------

class ChannelsMixer:
    """
    @authors: Nicolas Chazeau
    @contact: n.chazeau94@gmail.com
    @license: GPL, v3
    @summary: A channel utility class to mix several channels in one.
    """

    def __init__(self):
        """
        Constructor.

        """
        self.channels = []
        self.factors  = []

    # End __init__
    # -----------------------------------------------------------------------

    def _sampleCalculator(self, channels, pos, sampwidth, factors, attenuator):
        """
        Return the sample value, applying a factor and an attenuator.

        @param channels (Channel[]) the list of channels
        @param pos (int) the position of the sample to calculate
        @param sampwidth (int) the sample width
        @param factors (float[]) the list of factors to apply to each sample of a channel (1 channel = 1 factor)
        @param attenuator (float) a factor to apply to each sum of samples
        @return the value of the sample calculated (float)

        """
        #variables to compare the value of the result sample to avoid clipping
        minval = audioutils.get_minval(sampwidth)
        maxval = audioutils.get_maxval(sampwidth)

        #the result sample is the sum of each sample with the application of the factors
        sum = 0
        for factor,channel in zip(factors,channels):
            data = channel.frames[pos:pos+sampwidth]
            data = unpack_data(data, sampwidth)
            # without a cast, sum is a float!
            sum += data[0]*factor*attenuator

        #truncate the values if there is clipping
        if sum < 0:
            return max(sum,minval)
        elif sum > 0:
            return min(sum,maxval)
        return 0


    def append_channel(self, channel, factor = 1):
        """
        Append a channel and the factor associated in the mixer

        @param channel (Channel object) the channel to append
        @param factor (float) the factor associated to the channel

        """
        self.channels.append(channel)
        self.factors.append(factor)


    def check_channels(self):
        """
        Checking the conformity of the channels.

        """
        if len(self.channels) == 0:
            raise NameError("Error, no channel detected in the ChannelsMixer")

        sampwidth = self.channels[0].get_sampwidth()
        framerate = self.channels[0].get_framerate()
        nframes   = self.channels[0].get_nframes()

        for i in range(1, len(self.channels)):
            if self.channels[i].get_sampwidth() != sampwidth:
                raise NameError("Channels have not the same sampwidth ! Convert them before mix.")
            if self.channels[i].get_framerate() != framerate:
                raise NameError("Channels have not the same framerate ! Convert them before mix.")
            if self.channels[i].get_nframes() != nframes:
                raise NameError("Channels have not the same number of frames ! Convert them before mix.")


    def mix(self, attenuator = 1):
        """
        Mix the channels of the list in one

        @param attenuator (float) the factor to apply to each sample calculated
        @return the result Channel

        """
        # ensuring conformity
        self.check_channels()

        sampwidth = self.channels[0].get_sampwidth()
        framerate = self.channels[0].get_framerate()
        nframes   = self.channels[0].get_nframes()

        frames = ""
        if sampwidth == 4:
            for i,s in enumerate(xrange(0, len(self.channels[0].frames), sampwidth)):
                frames += struct.pack("<l", long(self._sampleCalculator(self.channels, s, sampwidth, self.factors, attenuator)))
        elif sampwidth == 2:
            for i,s in enumerate(xrange(0, len(self.channels[0].frames), sampwidth)):
                frames += struct.pack("<h", int(self._sampleCalculator(self.channels, s, sampwidth, self.factors, attenuator)))
        else:
            for i,s in enumerate(xrange(0, len(self.channels[0].frames), sampwidth)):
                frames += struct.pack("<b", int(self._sampleCalculator(self.channels, s, sampwidth, self.factors, attenuator)))

        return Channel(framerate, sampwidth, str(frames))


    def get_minmax(self):
        """
        Return a tuple with the mininum and the maximum value of all the samples calculated before beeing troncated

        @return the tuple (minvalue, maxvalue)

        """
        if len(self.channels) == 0:
            raise NameError("Error, no channel detected in the ChannelsMixer")

        sampwidth = self.channels[0].get_sampwidth()
        framerate = self.channels[0].get_framerate()
        nframes = self.channels[0].get_nframes()

        for i in xrange(1, len(self.channels)):
            if self.channels[i].get_sampwidth() != sampwidth:
                raise NameError("Channels have not the same sampwidth ! Convert them before mix.")
            if self.channels[i].get_framerate() != framerate:
                raise NameError("Channels have not the same framerate ! Convert them before mix.")
            if self.channels[i].get_nframes() != nframes:
                raise NameError("Channels have not the same number of frames ! Convert them before mix.")

        minval = 0
        maxval = 0
        sum = 0
        if sampwidth == 4:
            for i,s in enumerate(xrange(0, len(self.channels[0].frames), sampwidth)):
                sum = long(self._sampleCalculator(self.channels, s, sampwidth, self.factors, 1))
                maxval = max(sum, maxval)
                minval = min(sum, minval)

        else:
            for i,s in enumerate(xrange(0, len(self.channels[0].frames), sampwidth)):
                sum = int(self._sampleCalculator(self.channels, s, sampwidth, self.factors, 1))
                maxval = max(sum, maxval)
                minval = min(sum, minval)

        return(minval, maxval)



    def get_max(self):
        """
        Return the maximum value of all absolute values of the samples calculated before beeing troncated

        @return the absolute maximum value

        """
        if len(self.channels) == 0:
            raise NameError("Error, no channel detected in the ChannelsMixer")

        sampwidth = self.channels[0].get_sampwidth()
        framerate = self.channels[0].get_framerate()
        nframes = self.channels[0].get_nframes()

        for i in xrange(1, len(self.channels)):
            if self.channels[i].get_sampwidth() != sampwidth:
                raise NameError("Channels have not the same sampwidth ! Convert them before mix.")
            if self.channels[i].get_framerate() != framerate:
                raise NameError("Channels have not the same framerate ! Convert them before mix.")
            if self.channels[i].get_nframes() != nframes:
                raise NameError("Channels have not the same number of frames ! Convert them before mix.")

        minval = 0
        maxval = 0
        sum = 0
        if sampwidth == 4:
            for i,s in enumerate(xrange(0, len(self.channels[0].frames), sampwidth)):
                sum = long(self._sampleCalculator(self.channels, s, sampwidth, self.factors, 1))
                maxval = max(sum, maxval)
                minval = min(sum, minval)

        else:
            for i,s in enumerate(xrange(0, len(self.channels[0].frames), sampwidth)):
                sum = int(self._sampleCalculator(self.channels, s, sampwidth, self.factors, 1))
                maxval = max(sum, maxval)
                minval = min(sum, minval)

        return max(maxval, abs(minval))

