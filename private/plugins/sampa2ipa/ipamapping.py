#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2017  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# this program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# this program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# trsmapping.py
# ---------------------------------------------------------------------------

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.getenv('SPPAS')
if SPPAS is None:
    SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))

if os.path.exists(SPPAS) is False:
    print("ERROR: SPPAS not found.")
    sys.exit(1)
sys.path.append(SPPAS)

import sppas.src.annotationdata.aio as aio
from sppas.src.presenters.tiermapping import TierMapping
from sppas.src.annotationdata.transcription import Transcription


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -m table" %
                        os.path.basename(PROGRAM),
                        description="... a program to convert labels.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name.')

parser.add_argument("-m",
                    metavar="file",
                    required=True,
                    help='Mapping table file name.')

parser.add_argument("-n",
                    metavar="tiername",
                    required=True,
                    type=str,
                    help='One or several tier name separated by commas.')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Load input data

mapping = TierMapping(args.m)
mapping.set_reverse(False)    # from sampa to ipa direction
mapping.set_keep_miss(True)   # keep unknown entries as given
mapping.set_miss_symbol("")   # not used!
mapping.set_delimiters([])    # longest matching

# read content
trs_input = aio.read(args.i)

# ----------------------------------------------------------------------------
# Convert input file

trs = Transcription(name=trs_input.GetName()+"-IPA")

for n in args.n.split(','):
    print(" -> Tier {:s}:".format(n))
    tier = trs_input.Find(n, case_sensitive=False)
    if tier is not None:
        new_tier = mapping.map_tier(tier)
        new_tier.SetName(n+"-IPA")
        new_tier.metadata = tier.metadata
        trs.Append(new_tier)
    else:
        print(" [IGNORED] Wrong tier name.")

# Set the other members
trs.metadata = trs_input.metadata

# ----------------------------------------------------------------------------
# Write converted tiers

if trs.GetSize() == 0:
    print("No tier converted. No file created.")
    sys.exit(1)

infile, inext = os.path.splitext(args.i)
filename = infile + "-ipa" + inext
aio.write(filename, trs)
print("File {:s} created.".format(filename))
