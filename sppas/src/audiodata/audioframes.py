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
# File: audioframes.py
# ---------------------------------------------------------------------------

import audioop
import struct

import audiodata.audioutils as audioutils

# ---------------------------------------------------------------------------

class AudioFrames( object ):
    """
    @authors:      Nicolas Chazeau, Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      An utility for frames of audio frames.

    """
    def __init__(self, frames="", sampwidth=2, nchannels=1):
        """
        Constructor.

        @param frames (string) input frames.
        @param sampwidth (int) sample width of the frames.
        @param nchannels (int) number of channels in the samples

        """
        self.frames    = frames
        self.sampwidth = sampwidth
        self.nchannels = nchannels

    # -----------------------------------------------------------------------

    def resample(self, rate, newrate):
        """
        Return resampled frames.

        @param rate (int) current framerate of the frames
        @param newrate (int) new framerate of the frames
        @return converted frames

        """
        return audioop.ratecv(self.frames, self.sampwidth, self.nchannels, rate, newrate, None)[0]

    # -----------------------------------------------------------------------

    def changesampwidth(self, newsampwidth):
        """
        Return frames with the given number of bytes.

        @param newsampwidth (int) new sample width of the frames. (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)
        @return converted frames

        """
        return audioop.lin2lin(self.frames, self.sampwidth, newsampwidth)

    # -----------------------------------------------------------------------

    def bias(self, biasvalue):
        """
        Return frames that is the original fragment with a bias added to each sample.
        Samples wrap around in case of overflow.

        @param biasvalue (int) the bias which will be applied to each sample.
        @return converted frames

        """
        return audioop.bias(self.frames, self.sampwidth, biasvalue)

    # -----------------------------------------------------------------------

    def mul(self, factor):
        """
        Return frames that has all samples are multiplied by factor.
        Samples are truncated in case of overflow.

        @param factor (int) the factor which will be applied to each sample.
        @return converted frames

        """
        return audioop.mul(self.frames, self.sampwidth, factor)

    # -----------------------------------------------------------------------

    def cross(self):
        """
        Return the number of zero crossings in frames.

        @return number of zero crossing

        """
        return audioop.cross(self.frames, self.sampwidth)

    # -----------------------------------------------------------------------

    def minmax(self):
        """
        Return the (minimum,maximum) of the values of all frames.

        @return (min,max)

        """
        return audioop.minmax(self.frames, self.sampwidth)

    # -----------------------------------------------------------------------

    def min(self):
        """
        Return the minimum of the values of all frames.

        @return the minimum

        """
        return audioop.minmax(self.frames, self.sampwidth)[0]

    # -----------------------------------------------------------------------

    def max(self):
        """
        Return the maximum of the values of all frames.

        @return the maximum

        """
        return audioop.minmax(self.frames, self.sampwidth)[1]

    # -----------------------------------------------------------------------

    def avg(self):
        """
        Return the average of all the frames.

        @return the average

        """
        return audioop.avg(self.frames, self.sampwidth)

    # -----------------------------------------------------------------------

    def rms(self):
        """
        Return the root mean square of the frames.

        @return the root mean square

        """
        if self.nchannels == 1:
            return audioop.rms(self.frames, self.sampwidth)
        else:
            rmssum = 0
            for i in xrange(self.nchannels):
                newFrames = ""
                for j in xrange(i*self.sampwidth, len(self.frames), self.sampwidth*self.nchannels):
                    for k in xrange(self.sampwidth):
                        newFrames = newFrames + self.frames[j+k]
                rmssum += audioop.rms(newFrames, self.sampwidth)

            return rmssum/self.nchannels

    # -----------------------------------------------------------------------

    def clipping_rate(self, factor):
        """
        Return the clipping rate of the frames.

        @param factor (float) An interval to be more precise on clipping rate.
        It will consider that all frames outside the interval are clipped.
        Factor has to be between 0 and 1.
        @return the clipping rate

        """
        if self.sampwidth == 4 :
            data = struct.unpack("<%ul" % (len(self.frames) / 4), self.frames)
        elif self.sampwidth == 2 :
            data = struct.unpack("<%uh" % (len(self.frames) / 2), self.frames)
        else :
            data = struct.unpack("%uB"  %  len(self.frames),      self.frames)
            data = [ s - 128 for s in data ]

        maxval = audioutils.get_maxval(self.sampwidth)*(factor/2.)
        minval = audioutils.get_minval(self.sampwidth)*(factor/2.)

        nbclipping = 0

        for i in xrange(len(data)):
            if data[i] >= maxval or data[i] <= minval:
                nbclipping = nbclipping + 1

        return float(nbclipping)/len(data)

    # -----------------------------------------------------------------------
