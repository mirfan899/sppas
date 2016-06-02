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
import math


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

def get_maxval(size, signed=True):
    """
    Return the max value for a given sampwidth.

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
    Return the min value for a given sampwidth.

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
    Return the equivalent value in a mel scale, from a dB value.

    @param value (int) the value in dB to convert
    @return the value in mel

    """
    return 2595*math.log10(1+float(value)/700)

# ----------------------------------------------------------------------------

def mel2db(value):
    """
    Return the equivalent value in a dB scale, from a mel value.

    @param value (int) the value in mel to convert
    @return the value in dB

    """
    return 700*(10**(float(value)/2595)-1)

# ----------------------------------------------------------------------------

def amp2db(value):
    """
    Return the equivalent value in a dB scale, from an amplitude value.

    @param value (int) the amplitude value to convert
    @return the value in dB

    """
    if value < 3:
        return 0.
    return round( 10. * math.log10(value), 2)

# ----------------------------------------------------------------------------
