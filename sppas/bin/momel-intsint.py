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
# File: momel-intsint.py
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
from annotations.Momel.momel import sppasMomel


# ----------------------------------------------------------------------------
# Verify and extract args:
# ------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file [options]" % os.path.basename(PROGRAM), description="Momel-INTSINT command line interface.")

parser.add_argument("-i", required=True, metavar="file", help='Input file name (extension: .hz or .PitchTier)')

parser.add_argument("-o", metavar="file", help="Output file name (default: stdout)")
parser.add_argument("--win1",   type=int,   default=30,   help="Target window length (default: 30)")
parser.add_argument("--lo",     type=float, default=50,   help="f0 threshold (default:  50)")
parser.add_argument("--hi",     type=int,   default=600,  help="f0 ceiling (default: 600)")
parser.add_argument("--maxerr", type=float, default=1.04, help="Maximum error (default:   1.04)")
parser.add_argument("--win2",   type=int,   default=20,   help="Reduct window length (default:  20)")
parser.add_argument("--mind",   type=int,   default=5,    help="Minimal distance (default:   5)")
parser.add_argument("--minr",   type=float, default=0.05, help="Minimal frequency ratio (default: 0.05)")
parser.add_argument("--non-elim-glitch", dest="nonglitch", action='store_true' )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ------------------------------------------------------------------------
# Momel and INTSINT are here
# ------------------------------------------------------------------------

melodie = sppasMomel()

if args.win1:      melodie.set_option_win1( args.win1 )
if args.lo:        melodie.set_option_lo( args.lo )
if args.hi:        melodie.set_option_hi( args.hi )
if args.maxerr:    melodie.set_option_maxerr( args.maxerr )
if args.win2:      melodie.set_option_win2( args.win2 )
if args.mind:      melodie.set_option_mind( args.mind )
if args.minr:      melodie.set_option_minr( args.minr )
if args.nonglitch: melodie.set_option_elim_glitch(False)

melodie.run(args.i, args.o, outputfile=None)

# ----------------------------------------------------------------------------
