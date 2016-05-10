#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://www.lpl-aix.fr/~bigi/sppas
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2014  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# File: highpassfilter.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

from argparse import ArgumentParser
import os
import sys
import struct, math

PROGRAM = os.path.abspath(__file__)
WAVETOASTER = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ))
SRC = os.path.join(WAVETOASTER, "src" )
sys.path.append(SRC)

import audiodata
from audiodata.channel import Channel
from audiodata.audio import AudioPCM

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -o output file [options]" % os.path.basename(PROGRAM), description="A script to apply high-pass filter (development version)")

parser.add_argument("-i", metavar="file", required=True,  help='Audio Input file name')
parser.add_argument("-o", metavar="file", required=True,  help='Audio Output file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

audioin = audiodata.open( args.i )
SAMPLE_RATE = audioin.get_framerate()

# ----------------------------------------------------------------------------

# IIR filter coefficients
freq = 2000 # Hz
r = 0.98
a1 = -2.0 * r * math.cos(freq / (SAMPLE_RATE / 2.0) * math.pi)
a2 = r * r
filter = [a1, a2]
print filter

n = audioin.get_nframes()
original = struct.unpack('%dh' % n, audioin.read_frames(n))
original = [s / 2.0**15 for s in original]

result = [ 0 for i in range(0, len(filter)) ]
biggest = 1
for sample in original:
        for cpos in range(0, len(filter)):
            sample -= result[len(result) - 1 - cpos] * filter[cpos]
        result.append(sample)
        biggest = max(abs(sample), biggest)

result = [ sample / biggest for sample in result ]
result = [ int(sample * (2.0**15 - 1)) for sample in result ]

# ----------------------------------------------------------------------------

audioout = AudioPCM()
channel = Channel(framerate=SAMPLE_RATE, sampwidth=audioin.get_sampwidth(), frames=struct.pack('%dh' % len(result), *result) )
audioout.append_channel( channel )
audiodata.save( args.o, audioout)

# ----------------------------------------------------------------------------
