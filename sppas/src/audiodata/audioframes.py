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

    src.audiodata.audioframes.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import audioop
import struct

from .audioutils import get_maxval as audio_get_maxval
from .audioutils import get_minval as audio_get_minval

# ---------------------------------------------------------------------------


class AudioFrames(object):
    """
    :author:      Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    :summary:      An utility for frames of audio frames.

    """
    def __init__(self, frames="", sampwidth=2, nchannels=1):
        """ Constructor.

        :param frames: (str) input frames.
        :param sampwidth: (int) sample width of the frames.
        :param nchannels: (int) number of channels in the samples

        """
        self._frames = frames
        self._sampwidth = sampwidth
        self._nchannels = nchannels

    # -----------------------------------------------------------------------

    def resample(self, rate, new_rate=16000):
        """ Return re-sampled frames.

        :param rate: (int) current frame rate of the frames
        :param new_rate: (int) new frame rate of the frames
        :returns: (str) converted frames

        """
        return audioop.ratecv(self._frames, self._sampwidth, self._nchannels, rate, new_rate, None)[0]

    # -----------------------------------------------------------------------

    def change_sampwidth(self, new_sampwidth):
        """ Return frames with the given number of bytes.

        :param new_sampwidth: (int) new sample width of the frames.
            (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)
        :returns: (str) converted frames

        """
        return audioop.lin2lin(self._frames, self._sampwidth, new_sampwidth)

    # -----------------------------------------------------------------------

    def bias(self, bias_value):
        """ Return frames that is the original fragment with a bias added to each sample.
        Samples wrap around in case of overflow.

        :param bias_value: (int) the bias which will be applied to each sample.
        :returns: (str) converted frames

        """
        return audioop.bias(self._frames, self._sampwidth, bias_value)

    # -----------------------------------------------------------------------

    def mul(self, factor):
        """ Return frames for which all samples are multiplied by factor.
        Samples are truncated in case of overflow.

        :param factor: (int) the factor which will be applied to each sample.
        :returns: (str) converted frames

        """
        return audioop.mul(self._frames, self._sampwidth, factor)

    # -----------------------------------------------------------------------

    def cross(self):
        """ Return the number of zero crossings in frames.

        :returns: number of zero crossing

        """
        return audioop.cross(self._frames, self._sampwidth)

    # -----------------------------------------------------------------------

    def minmax(self):
        """ Return the (minimum,maximum) of the values of all frames.

        :returns (min,max)

        """
        return audioop.minmax(self._frames, self._sampwidth)

    # -----------------------------------------------------------------------

    def min(self):
        """ Return the minimum of the values of all frames. """

        return audioop.minmax(self._frames, self._sampwidth)[0]

    # -----------------------------------------------------------------------

    def max(self):
        """ Return the maximum of the values of all frames. """

        return audioop.minmax(self._frames, self._sampwidth)[1]

    # -----------------------------------------------------------------------

    def avg(self):
        """ Return the average of all the frames. """

        return audioop.avg(self._frames, self._sampwidth)

    # -----------------------------------------------------------------------

    def rms(self):
        """ Return the root mean square of the frames. """

        if self._nchannels == 1:
            return audioop.rms(self._frames, self._sampwidth)
        else:
            rms_sum = 0
            for i in range(self._nchannels):
                new_frames = ""
                for j in range(i*self._sampwidth, len(self._frames), self._sampwidth*self._nchannels):
                    for k in range(self._sampwidth):
                        new_frames = new_frames + self._frames[j+k]
                rms_sum += audioop.rms(new_frames, self._sampwidth)

            return rms_sum/self._nchannels

    # -----------------------------------------------------------------------

    def clipping_rate(self, factor):
        """ Return the clipping rate of the frames.

        :param factor: (float) An interval to be more precise on clipping rate.
        It will consider that all frames outside the interval are clipped.
        Factor has to be between 0 and 1.
        :returns: (float) the clipping rate

        """
        if self._sampwidth == 4:
            data = struct.unpack("<%ul" % (len(self._frames) / 4), self._frames)
        elif self._sampwidth == 2:
            data = struct.unpack("<%uh" % (len(self._frames) / 2), self._frames)
        else:
            data = struct.unpack("%uB" % len(self._frames), self._frames)
            data = [s - 128 for s in data]

        max_val = audio_get_maxval(self._sampwidth)*(factor/2.)
        min_val = audio_get_minval(self._sampwidth)*(factor/2.)

        nb_clipping = 0
        for i in range(len(data)):
            if data[i] >= max_val or data[i] <= min_val:
                nb_clipping += 1

        return float(nb_clipping)/len(data)
