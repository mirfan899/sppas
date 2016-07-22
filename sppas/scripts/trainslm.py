#!/usr/bin/env python2
# -*- coding:utf-8 -*-
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
# File: trainslm.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.append(SPPAS)

from resources.slm.ngramsmodel  import NgramsModel
from resources.slm.arpaio       import ArpaIO

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file " % os.path.basename(PROGRAM), description="... a script to train a statistical language model.")
parser.add_argument("-i", metavar="input",  required=True,  action='append', help='Input file name of the training corpus.')
parser.add_argument("-r", metavar="vocab",  required=False, help='List of known words.')
parser.add_argument("-n", metavar="order",  required=False, default=3, type=int,  help='N-gram order value (default=1).')
parser.add_argument("-m", metavar="method", required=False, default="logml", type=str, help='Method to estimates probabilities (one of: raw, lograw, ml, logml).')
parser.add_argument("-o", metavar="output", required=True,  help='Output file name.')

parser.add_argument("--quiet", action='store_true', help="Disable the verbosity." )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------------

# ---------------------------------
# 1. Create a NgramsModel

model = NgramsModel( args.n )
if args.r:
    model.set_vocab( args.r )

# ---------------------------------
# 2. Estimate counts of each n-gram

model.count( *(args.i) )

# ---------------------------------
# 3. Estimate probabilities

probas = model.probabilities( args.m )

# ---------------------------------
# 4. Write in an ARPA file

arpaio = ArpaIO()
arpaio.set( probas )
arpaio.save( args.o )

# ---------------------------------------------------------------------------
