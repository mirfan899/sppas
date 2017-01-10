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
# File: wavinfo.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2014  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
import time
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.append(SPPAS)

import audiodata.aio
from audiodata.channelformatter import ChannelFormatter
from audiodata.audio import AudioPCM

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -w input file -o output file [options]" % os.path.basename(PROGRAM), description="A script to reformat audio file")

parser.add_argument("-w", metavar="file", required=True,  help='Audio Input file name')
parser.add_argument("-o", metavar="file", required=True,  help='Audio Output file name')
parser.add_argument("-b", metavar="value", type=int, help='Possible values are 1,2,4')
parser.add_argument("-c", metavar="value", default=1, type=int, help='the channel to extract (default: 1)')
parser.add_argument("-r", metavar="value", type=int, help='Value of the new framerate')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if not args.b in [1,2,4]:
    print "Wrong bitrate value"
    sys.exit(1)

# ----------------------------------------------------------------------------

print (time.strftime("%H:%M:%S"))
audio = audiodata.aio.open(args.w)

# Get the expected channel
idx = audio.extract_channel(args.c-1)
# no more need of input data, can close
audio.close()
print (time.strftime("%H:%M:%S"))

# Do the job (do not modify the initial channel).
formatter = ChannelFormatter( audio.get_channel(idx) )
if args.r:
    formatter.set_framerate(args.r)
if args.b:
    formatter.set_sampwidth(args.b)
formatter.convert()
print (time.strftime("%H:%M:%S"))

# Save the converted channel
audio_out = AudioPCM()
audio_out.append_channel( formatter.channel )
audiodata.save( args.o, audio_out )
print (time.strftime("%H:%M:%S"))

# ----------------------------------------------------------------------------

