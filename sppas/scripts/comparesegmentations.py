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
#       Copyright (C) 2011-2016  Brigitte Bigi
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
# File: comparesegmentations.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2014  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
import codecs
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.append(SPPAS)

from   annotationdata.transcription import Transcription
import annotationdata.io

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -fr file -fh file [options]" % os.path.basename(PROGRAM), description="... a script to compare two segmentations, in the scope of evaluating an hypothesis vs a reference.")

parser.add_argument("-fr", metavar="file", required=True,  help='Input annotated file name of the reference.')
parser.add_argument("-fh", metavar="file", required=True,  help='Input annotated file name of the hypothesis.')
parser.add_argument("-tr", metavar="file", required=False,  help='Tier number of the reference (default=1).')
parser.add_argument("-th", metavar="file", required=False,  help='Tier number of the hypothesis (default=1).')
parser.add_argument("-o",  metavar="path", required=False,  help='Path for the output files.')

parser.add_argument("--quiet", action='store_true', help="Disable the verbosity." )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Load and check data

trsinputr = annotationdata.io.read( args.fr )
idxtier = 0
if args.tr: idxtier = args.tr - 1
if idxtier < 0 or idxtier > trsinputr.GetSize():
    print "Bad tier number for reference."
    sys.exit(1)
reftier = trsinputr[ idxtier ]

trsinputh = annotationdata.io.read( args.fh )
idxtier = 0
if args.tr: idxtier = args.tr - 1
if idxtier < 0 or idxtier > trsinputh.GetSize():
    print "Bad tier number for reference."
    sys.exit(1)
hyptier = trsinputh[ idxtier ]

if reftier.GetSize() != hyptier.GetSize():
    print "reference and hypothesis tiers don't have the same number of intervals."
    sys.exit(1)

# ----------------------------------------------------------------------------
# Output files

hypfilename,extension = os.path.splitext( args.fh )
outbasename = os.path.basename( hypfilename )
if args.o:
    outpath = args.o
else:
    outpath = os.path.dirname( hypfilename )
outname = os.path.join( outpath, outbasename )

fpb = codecs.open( os.path.join(outname)+"-posS.txt", "w", 'utf8')
fpe = codecs.open( os.path.join(outname)+"-posE.txt", "w", 'utf8')
fpm = codecs.open( os.path.join(outname)+"-posM.txt", "w", 'utf8')
fpd = codecs.open( os.path.join(outname)+"-dur.txt", "w", 'utf8')

# ----------------------------------------------------------------------------
# Compare boundaries and durations of annotations.

i = 0
imax = reftier.GetSize()-1

for rann,hann in zip(reftier,hyptier):
    etiquette = rann.GetLabel().GetValue()
    # begin
    rb = rann.GetLocation().GetBegin().GetValue()
    hb = hann.GetLocation().GetBegin().GetValue()
    # end
    re = rann.GetLocation().GetEnd().GetValue()
    he = hann.GetLocation().GetEnd().GetValue()
    # middle
    rm = rb + (re-rb)/2.
    hm = hb + (he-hb)/2.
    # duration
    rd = rann.GetLocation().GetDuration().GetValue()
    hd = hann.GetLocation().GetDuration().GetValue()

    if i>0:
        fpb.write("%f %s %s\n"%((rb-hb),etiquette,outname))
    if i<imax:
        fpe.write("%f %s %s\n"%((re-he),etiquette,outname))
    fpm.write("%f %s %s\n"%((rm-hm),etiquette,outname))
    fpd.write("%f %s %s\n"%((rd-hd),etiquette,outname))

    i = i + 1

# ----------------------------------------------------------------------------

fpb.close()
fpe.close()
fpm.close()
fpd.close()
