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
# File: audioutils.py
# ---------------------------------------------------------------------------

import struct
import audioop
import math

# ----------------------------------------------------------------------------

def samples2frames(samples, sampwidth, nchannel=1):
    """
    Turn samples into frames

    @param samples (int[][]) samples list, first index is the index of the channel, second is the index of the sample.
    @param sampwidth (int) sample width of the frames.
    @param nchannel (int) number of channels in the samples
    @return frames

    """
    nframes = len(samples[0])
    frames = ""

    if sampwidth == 4 :
        for i in xrange(nframes):
            for j in xrange(nchannel):
                frames = frames + struct.pack("<l", samples[j][i])

    elif sampwidth == 2 :
        for i in xrange(nframes):
            for j in xrange(nchannel):
                frames = frames + struct.pack("<h", samples[j][i])

    else :
        for i in xrange(nframes):
            for j in xrange(nchannel):
                frames = frames + struct.pack("<b", samples[j][i])
    return frames

# ----------------------------------------------------------------------------

def resample(frames, sampwidth, nchannels, rate, newrate):
    """
    Resample frames with a new framerate

    @param frames (string) input frames.
    @param sampwidth (int) sample width of the frames.
    @param nchannels (int) number of channels in the samples
    @param rate (int) current framerate of the frames
    @param newrate (int) new framerate of the frames
    @return converted frames

    """
    return audioop.ratecv(frames, sampwidth, nchannels, rate, newrate, None)[0]

# ----------------------------------------------------------------------------

def changesampwidth(frames, sampwidth, newsampwidth):
    """
    Change the number of bytes used to encode the frames

    @param frames (string) input frames.
    @param current sampwidth (int) sample width of the frames. (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)
    @param newsampwidth (int) new sample width of the frames. (1 for 8 bits, 2 for 16 bits, 4 for 32 bits)
    @return converted frames

    """
    return audioop.lin2lin(frames, sampwidth, newsampwidth)

# ----------------------------------------------------------------------------

def get_maxval(size, signed=True):
    """
    Return the max value for a sampwidth given

    @param size (int) the sampwidth
    @param signed (bool) if the values will be signed or not
    @return the max value

    """
    if signed and size == 1:
        return 0x7f
    elif size == 1:
        return 0xff
    elif signed and size == 2:
        return 0x7fff
    elif size == 2:
        return 0xffff
    elif signed and size == 4:
        return 0x7fffffff
    elif size == 4:
        return 0xffffffff

# ----------------------------------------------------------------------------

def get_minval(size, signed=True):
    """
    Return the min value for a sampwidth given

    @param size (int) the sampwidth
    @param signed (bool) if the values will be signed or not
    @return the min value

    """
    if not signed:
        return 0
    elif size == 1:
        return -0x80
    elif size == 2:
        return -0x8000
    elif size == 4:
        return -0x80000000

# ----------------------------------------------------------------------------

def db2mel(value):
    """
    Return the equivalent value in a mel scale

    @param value (int) the value in db to convert
    @return the value in mel

    """
    return 2595*math.log10(1+float(value)/700)

# ----------------------------------------------------------------------------

def mel2db(value):
    """
    Return the equivalent value in a db scale

    @param value (int) the value in mel to convert
    @return the value in db

    """
    return 700*(10**(float(value)/2595)-1)

# ----------------------------------------------------------------------------

def bias(fragment, sampwidth, bias):
    """
    Return a fragment that is the original fragment with a bias added to each sample. Samples wrap around in case of overflow.

    @param fragment (string) input frames.
    @param sampwidth (int) sample width of the frames.
    @param bias (int) the bias which will be applied to each sample.
    @return converted frames

    """
    return audioop.bias(fragment, sampwidth, bias)

# ----------------------------------------------------------------------------

def mul(fragment, sampwidth, factor):
    """
    Return a fragment that has all samples in the original fragment multiplied by the floating-point value factor. Samples are truncated in case of overflow.

    @param fragment (string) input frames.
    @param sampwidth (int) sample width of the frames.
    @param factor (int) the factor which will be applied to each sample.
    @return converted frames

    """
    return audioop.mul(fragment, sampwidth, factor)

# ----------------------------------------------------------------------------

def cross(fragment, sampwidth):
    """
    Return the number of zero crossings in the fragment passed as an argument.

    @param fragment (string) input frames.
    @param sampwidth (int) sample width of the frames.
    @return number of zero crossing

    """
    return audioop.cross(fragment, sampwidth)

# ----------------------------------------------------------------------------

def avg(fragment, sampwidth):
    """
    Return the average of all the samples.

    @param fragment (string) input frames.
    @param sampwidth (int) sample width of the frames.
    @return the average

    """
    return audioop.avg(fragment, sampwidth)

# ----------------------------------------------------------------------------

def get_rms(frames, sampwidth, nchannels = 1):
    """
    Return the root mean square of the frames

    @param frames (string) input frames.
    @param sampwidth (int) sample width of the frames.
    @param nchannels (int) number of channels in the frames
    @return the root mean square

    """
    if nchannels == 1:
        return audioop.rms(frames, sampwidth)
    else:
        sum = 0
        for i in xrange(nchannels):
            newFrames = ""
            for j in xrange(i*sampwidth, len(frames), sampwidth*nchannels):
                for k in xrange(sampwidth):
                    newFrames = newFrames + frames[j+k]
            sum = sum + audioop.rms(newFrames, sampwidth)
        return sum/nchannels

# ----------------------------------------------------------------------------

def get_clipping_rate(frames, sampwidth, factor):
    """
    Return the clipping rate of the frames

    @param frames (string) input frames.
    @param sampwidth (int) sample width of the frames.
    @param factor (float) An interval to be more precise on clipping rate. It will consider that all frames outside the interval are clipped. Factor has to be between 0 and 1.
    @return the clipping rate

    """
    if sampwidth == 4 :
        data = struct.unpack("<%ul" % (len(frames) / 4), frames)
    elif sampwidth == 2 :
        data = struct.unpack("<%uh" % (len(frames) / 2), frames)
    else :
        data = struct.unpack("%uB"  %  len(frames),      frames)
        data = [ s - 128 for s in data ]

    maxval = get_maxval(sampwidth)*(factor/2.)
    minval = get_minval(sampwidth)*(factor/2.)

    nbclipping = 0

    for i in xrange(len(data)):
        if data[i] >= maxval or data[i] <= minval:
            nbclipping = nbclipping + 1

    return float(nbclipping)/len(data)

# ----------------------------------------------------------------------------