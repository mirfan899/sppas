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
# File: acsplit.py
# ---------------------------------------------------------------------------

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

from models.acm.acmodel import AcModel

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i hmmdef -o dir" % os.path.basename(PROGRAM), description="... a script to split a hmmdef file into hmms.")

parser.add_argument("-i", metavar="file", required=True,  help='Input file name')
parser.add_argument("-o", metavar="dir", required=True,  help='Output directory name')
parser.add_argument("--quiet", action='store_true', help="Disable the verbosity" )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if not os.path.isdir( args.o ):
    print "Error:",args.o,"must be an existing directory."
    sys.exit(1)

if not os.path.isfile( args.i ):
    print "Error:",args.i,"must be an acoutic model file (HTK-ASCII format)."
    sys.exit(1)

if not args.quiet is True:
    print "Loading AC:",
acmodel1 = AcModel()
acmodel1.load_htk( args.i )
if not args.quiet is True:
    print "... done"

# ----------------------------------------------------------------------------

acmodel = acmodel1.extract_monophones()

for hmm in acmodel.hmms:
   
    filename = os.path.join( args.o, hmm.name )
    filename = filename + ".hmm"
    if not args.quiet is True:
        print hmm.name,filename
    hmm.save( filename )

# ----------------------------------------------------------------------------
