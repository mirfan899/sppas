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

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.append(SPPAS)

from annotations.Phon.sppasphon import sppasPhon
from annotations.Phon.phonetize import DictPhon
from resources.dictpron         import DictPron
from resources.mapping          import Mapping
from utils.fileutils            import setup_logging

from sp_glob import UNKSTAMP

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -r dict [options]" % os.path.basename(PROGRAM), prog=PROGRAM, description="Phonetization automatic annotation.")

parser.add_argument("-r", "--dict", required=True, help='Pronunciation dictionary file name (HTK-ASCII format).')
parser.add_argument("-m", "--map", required=False, help='Pronunciation mapping table. It is used to generate new pronunciations by mapping phonemes of the dictionary.')

parser.add_argument("-i", metavar="file", required=False, help='Input file name')
parser.add_argument("-o", metavar="file", required=False, help='Output file name (required only if -i is fixed)')

parser.add_argument("--nounk", action='store_true', help="Disable unknown word phonetization." )
parser.add_argument("--quiet",  action='store_true', help="Disable verbose." )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if not args.quiet:
    setup_logging(1,None)

# ----------------------------------------------------------------------------
# Automatic Phonetization is here:
# ----------------------------------------------------------------------------

unkopt = True
if args.nounk:
    unkopt = False

mapfile = None
if args.map:
    mapfile = args.map

if args.i:
    p = sppasPhon( args.dict, mapfile )
    p.set_unk( unkopt )
    p.set_usestdtokens( False )
    p.run( args.i,args.o )
else:
    pdict    = DictPron( args.dict, unkstamp=UNKSTAMP, nodump=False )
    maptable = Mapping()
    if mapfile is not None:
        maptable = Mapping( mapfile )
    phonetizer = DictPhon( pdict, maptable )
    for line in sys.stdin:
        print phonetizer.phonetize( line, unkopt )

# ----------------------------------------------------------------------------
