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
# File: trsmerge.py
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

from   annotationdata.transcription import Transcription
import annotationdata.aio

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM), description="... a script to merge annotations files.")

parser.add_argument("-i", metavar="file", action='append', required=True,  help='Input annotated file name (as many as wanted)')
parser.add_argument("-o", metavar="file",  required=True,  help='Output annotated file name')
parser.add_argument("--quiet", action='store_true', help="Disable the verbosity" )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------

trsoutput = Transcription()

for trsinputfile in args.i:

    if not args.quiet: print "Read input file:"
    trsinput = annotationdata.aio.read(trsinputfile)

    # Take all tiers
    for i in range(trsinput.GetSize()):
        if not args.quiet: sys.stdout.write( " -> Tier "+str(i+1)+": ")
        trsoutput.Append(trsinput[i])
        if not args.quiet: print " [  OK  ]"

if not args.quiet: sys.stdout.write( "Write output file: ")
annotationdata.aio.write(args.o, trsoutput)
if not args.quiet: print " [  OK  ]"

# ----------------------------------------------------------------------------
