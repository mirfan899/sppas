#!/usr/bin/env python2
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

    scripts.audioformat.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to reformat audio files.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

# ----------------------------------------------------------------------------

import sppas.src.audiodata
from sppas.src.audiodata.channelformatter import ChannelFormatter
from sppas.src.audiodata.audio import AudioPCM

parser = ArgumentParser(usage="%s -w input file -o output file [options]" % os.path.basename(PROGRAM),
                        description="... a script to reformat audio files.")

parser.add_argument("-w", metavar="file", required=True,  help='Audio Input file name')
parser.add_argument("-o", metavar="file", required=True,  help='Audio Output file name')
parser.add_argument("-s", metavar="value", type=int, help='Sample width for the output file. Possible values are 1,2,4')
parser.add_argument("-c", metavar="value", default=1, type=int, help='the channel to extract (default: 1)')
parser.add_argument("-r", metavar="value", type=int, help='The framerate expected of the output audio file')
parser.add_argument("-m", metavar="value", type=int, help='Multiply the frames of the channel by the factor')
parser.add_argument("-b", metavar="value", type=int, help='Bias the frames of the channel by the factor')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

audio = sppas.src.audiodata.open(args.w)

# Get the expected channel
idx = audio.extract_channel(args.c-1)

# Do the job (do not modify the initial channel).
formatter = ChannelFormatter(audio.get_channel(idx))

if args.r:
    formatter.set_framerate(args.r)
else:
    formatter.set_framerate(audio.get_framerate())

if args.b:
    if args.b not in [1, 2, 4]:
        print "Wrong bitrate value"
        sys.exit(1)
    formatter.set_sampwidth(args.b)
else:
    formatter.set_sampwidth(audio.get_sampwidth())

formatter.convert()

# no more need of input data, can close
audio.close()

if args.m:
    formatter.mul(args.m)

if args.b:
    formatter.bias(args.b)

# Save the converted channel
audio_out = AudioPCM()
audio_out.append_channel(formatter.channel)
sppas.src.audiodata.save(args.o, audio_out)
