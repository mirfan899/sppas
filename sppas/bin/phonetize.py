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
# File: phonetize.py
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
from annotations.Phon.phon import sppasPhon
from annotations.Phon.phonetize import DictPhon
from resources.dictpron import DictPron

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

epilogue  = "!!!!!!!  if no input is given, the input is stdin and output is stdout  !!!!!!!\n"
epilogue += "!!!!!!!  if no output is given, the output is the input  !!!!!!!"

parser = ArgumentParser(usage="%s -r dict [options]" % os.path.basename(PROGRAM), prog=PROGRAM, description="Phonetization command line interface.", epilog=epilogue)

parser.add_argument("-r", "--dict", required=True, help='Pronunciation dictionary file name')
parser.add_argument("-i", metavar="file", required=False, help='Input file name')
parser.add_argument("-o", metavar="file", required=False, help='Output file name')
parser.add_argument("--nounk", action='store_true', help="Disable unknown word phonetization" )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------
# Automatic Phonetization is here:
# ----------------------------------------------------------------------------

unkopt = True
if args.nounk:
    unkopt = False

if args.i:
    p = sppasPhon( args.dict )
    p.set_unk( unkopt )
    p.run( args.i,args.o )
else:
    pdict = DictPron( args.dict )
    phonetizer = DictPhon( pdict,None )
    for line in sys.stdin:
        print phonetizer.phonetize( line, unkopt )

# ----------------------------------------------------------------------------