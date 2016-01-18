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
# File: wavcut.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2014  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.append(SPPAS)

from signals.wav import Wave
import utils.fileutils


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -w file [options]" % os.path.basename(PROGRAM), description="... a script to extract a part of a wav file.")

parser.add_argument("-w", metavar="file", required=True,  help='Input wav file name')
parser.add_argument("-o", metavar="file",  help='Output file name')
parser.add_argument("-s", metavar="value", default=0, type=float, help='Requested start time in seconds (default: 0)')
parser.add_argument("-d", metavar="value", type=float, help='Requested duration in seconds (default: wav file duration)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------

wavspeech = Wave(args.w,0.01)

if not args.o:
    outputfile = utils.fileutils.set_tmpfilename()+".wav"
    sys.stderr.write(outputfile+"\n")
else:
    outputfile = args.o

if not args.d:
    reqDuration = wavspeech.get_duration()
else:
    reqDuration = args.d

wavspeech.write_segment(outputfile,args.s,reqDuration)

# ----------------------------------------------------------------------------
