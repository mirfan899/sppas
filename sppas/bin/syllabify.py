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
# File: syllabify.py
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
from annotations.Syll.sppassyll import sppasSyll


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

epilogue = "!!!!!!!  if no output is given, the output is the input  !!!!!!!"

parser = ArgumentParser(usage="%s -r config [options]" % os.path.basename(PROGRAM), prog=PROGRAM, description="Automatic Syllabification command line interface.", epilog=epilogue)

parser.add_argument("-r", "--config", required=True, help='Rules configuration file name')
parser.add_argument("-i", metavar="file", required=True, help='Input file name (time-aligned phonemes)')
parser.add_argument("-o", metavar="file", required=True, help='Output file name')
parser.add_argument("-t", metavar="string", required=False, help='Reference tier name to syllabify between intervals')
parser.add_argument("--nophn", action='store_true', help="Disable the output of the result that does not use the reference tier" )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

if args.nophn and not args.t:
    print "Warning. The option --nophn will not have any effect! It must be used with -t option."


# ----------------------------------------------------------------------------
# Automatic Syllabification is here:
# ----------------------------------------------------------------------------


syll = sppasSyll( args.config )

if args.t:
    syll.set_usesintervals( True )
    syll.set_tiername( args.t )
    if args.nophn: syll.set_usesphons( False )

syll.run( args.i, args.o )

# --------------------------------------------------------------------------
