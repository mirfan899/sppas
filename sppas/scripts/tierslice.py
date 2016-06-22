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
# File: tierslice.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.append(SPPAS)

import annotationdata.io
from annotationdata import Transcription
from annotationdata import Tier
from annotationdata import TimePoint
from annotationdata import TimeInterval
from annotationdata import Label
from annotationdata import Annotation
from annotationdata.utils.trsutils import TrsUtils

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file [options]" % os.path.basename(PROGRAM), description="... a script to slice a tier of an annotated file.")

parser.add_argument("-i", metavar="file",  required=True,  help='Input annotated file name')
parser.add_argument("-o", metavar="file",  required=False, help='Output annotated file name')
parser.add_argument("-s", metavar="value", required=False, default=0, type=float, help='Start position in seconds (default=0)')
parser.add_argument("-d", metavar="value", required=False, default=4, type=float, help='Duration in seconds (default=4)')
parser.add_argument("-t", metavar="value", default=1, type=int, help='Tier number (default: 1)')
parser.add_argument("-l", metavar="value", default=0, type=float, help='Apply a shift delay to the extracted part. (default: 0)')


if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

trsinput = annotationdata.io.read(args.i)

if args.t <= 0 or args.t > trsinput.GetSize():
    print 'Error: Bad tier number. Must range in (%d,%d)\n'%(1,trsinput.GetSize())
    sys.exit(1)
tierinput = trsinput[args.t-1]

# ----------------------------------------------------------------------------

trs = Transcription(trsinput.GetName())
trs.Append( tierinput )

# ----------------------------------------------------------------------------
# Preparation

slicertier = Tier("Name")
b = TimePoint(float(args.s))
e = TimePoint(float(args.s) + float(args.d))
ann = Annotation(TimeInterval(b,e),Label('slice'))
slicertier.Append(ann)

list_transcription = TrsUtils.Split( trs, slicertier )
trsout = list_transcription[0]
TrsUtils.Shift(trsout, -trsout.GetBeginValue())

delay = float(args.l)
if delay != 0:
    TrsUtils.Shift(trsout, delay)

# ----------------------------------------------------------------------------
# Write

if args.o:
    outputf = args.o
else:
    f,e = os.path.splitext(args.i)
    outputf = f+"_"+tierinput.GetName()+e
annotationdata.io.write(outputf, trsout)

# ----------------------------------------------------------------------------
