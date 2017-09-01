#!/usr/bin/env python2
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

    bin.momel-intsint.py
    ~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Run the momel and intsint automatic annotations

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotations.Momel.sppasmomel import sppasMomel
from sppas.src.annotations.Intsint.sppasintsint import sppasIntsint


# ----------------------------------------------------------------------------
# Verify and extract args:
# ------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file [options]" % os.path.basename(PROGRAM), 
                        description="Momel-INTSINT automatic annotations.")

parser.add_argument("-i", 
                    required=True, 
                    metavar="file", 
                    help='Input file name (extension: .hz or .PitchTier)')

parser.add_argument("-o", 
                    metavar="file",
                    help="Momel output file name (default: stdout)")

parser.add_argument("-O", 
                    metavar="file", 
                    help="Intsint output file name")

parser.add_argument("--win1",   type=int,   default=30,   help="Target window length (default: 30)")
parser.add_argument("--lo",     type=float, default=50,   help="f0 threshold (default:  50)")
parser.add_argument("--hi",     type=int,   default=600,  help="f0 ceiling (default: 600)")
parser.add_argument("--maxerr", type=float, default=1.04, help="Maximum error (default:   1.04)")
parser.add_argument("--win2",   type=int,   default=20,   help="Reduct window length (default:  20)")
parser.add_argument("--mind",   type=int,   default=5,    help="Minimal distance (default:   5)")
parser.add_argument("--minr",   type=float, default=0.05, help="Minimal frequency ratio (default: 0.05)")
parser.add_argument("--non-elim-glitch", dest="nonglitch", action='store_true')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ------------------------------------------------------------------------
# Momel and INTSINT are here
# ------------------------------------------------------------------------

melodie = sppasMomel()

if args.win1:
    melodie.momel.set_option_win1(args.win1)
if args.lo:
    melodie.momel.set_option_lo(args.lo)
if args.hi:
    melodie.momel.set_option_hi(args.hi)
if args.maxerr:
    melodie.momel.set_option_maxerr(args.maxerr)
if args.win2:
    melodie.momel.set_option_win2(args.win2)
if args.mind:
    melodie.momel.set_option_mind(args.mind)
if args.minr:
    melodie.momel.set_option_minr(args.minr)
if args.nonglitch:
    melodie.momel.set_option_elim_glitch(False)

melodie.run(args.i, args.o, outputfile=None)

if args.O:
    intsint = sppasIntsint()
    intsint.run(args.o, args.O)
