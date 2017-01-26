#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
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
# File: acmerge.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""


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

from models.acm.acmodel import AcModel

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file1/dir1 -I file2/dir2 -g gamma -o file" % os.path.basename(PROGRAM), description="... a script to merge 2 hmmdefs files.")

parser.add_argument("-i", metavar="file", required=True,  help='Input file/directory name')
parser.add_argument("-I", metavar="file", required=True,  help='Input file/directory name')
parser.add_argument("-g", metavar="value", type=float, default=0.5, help='Gamma coefficient, for the file of -i option')
parser.add_argument("--quiet", action='store_true', help="Disable the verbosity" )

mxg = parser.add_mutually_exclusive_group(required=True)
mxg.add_argument("-o", metavar="file", required=False,  help='Output file name')
mxg.add_argument("-O", metavar="file", required=False,  help='Output directory name')


if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if not args.quiet is True:
    print "Loading AC 1:",
acmodel1 = AcModel()
if os.path.isfile( args.i ):
    acmodel1.load_htk( args.i )
else:
    acmodel1.load( args.i )
if not args.quiet is True:
    print "... done"

if not args.quiet is True:
    print "Loading AC 2:",
acmodel2 = AcModel()
if os.path.isfile( args.I ):
    acmodel2.load_htk( args.I )
else:
    acmodel2.load( args.I )
if not args.quiet is True:
    print "... done"

(appended,interpolated,keeped,changed) = acmodel1.merge_model(acmodel2,gamma=args.g)
if not args.quiet is True:
    print "Number of appended HMMs:     ",appended
    print "Number of interpolated HMMs: ",interpolated
    print "Number of keeped HMMs:       ",keeped
    print "Number of changed HMMs:      ",changed

if args.o:
    acmodel1.save_htk( args.o )
if args.O:
    acmodel1.save( args.O )

# ----------------------------------------------------------------------------
