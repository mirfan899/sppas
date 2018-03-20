#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
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

    scripts.trsconvert.py
    ~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      a script to export annotations files based on anndata API.

"""
import sys
import os.path
from argparse import ArgumentParser
import pickle
import time

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to export annotations files.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output annotated file name')

parser.add_argument("-t",
                    metavar="value",
                    required=False,
                    action='append',
                    type=int,
                    help='A tier number (use as many -t options as wanted). '
                         'Positive or negative value: 1=first tier, -1=last tier.')

parser.add_argument("-n",
                    metavar="tiername",
                    required=False,
                    action='append',
                    type=str,
                    help='A tier name (use as many -n options as wanted).')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Read

parser = sppasRW(args.i)

if args.quiet is False:
    print("Read input:")

start_time = time.time()
trs_input = parser.read()
end_time = time.time()

if args.quiet is False:
    print("  - elapsed time for reading: {:f} seconds".format(end_time - start_time))
    pickle_string = pickle.dumps(trs_input)
    print("  - memory usage of the transcription: {:d} bytes".format(sys.getsizeof(pickle_string)))

# ----------------------------------------------------------------------------
# Select tiers

if args.quiet is False:
    print("Tier selection:")

# Take all tiers or specified tiers
tier_numbers = []
if not args.t and not args.n:
    tier_numbers = range(1, (len(trs_input) + 1))
elif args.t:
    tier_numbers = args.t

# Select tiers to create output
trs_output = sppasTranscription(name=trs_input.get_name())

# Add selected tiers into output
for i in tier_numbers:
    if args.quiet is False:
        sys.stdout.write("  - Tier " + str(i) + ": ")
    if i > 0:
        idx = i-1
    elif i < 0:
        idx = i
    else:
        idx = len(trs_input)
    if idx < len(trs_input):
        trs_output.append(trs_input[idx])
        if args.quiet is False:
            print("{:s}.".format(trs_input[idx].get_name()))
    else:
        if not args.quiet:
            print("Ignored. Wrong tier number {:d}.".format(i))

if args.n:
    for n in args.n:
        t = trs_input.find(n, case_sensitive=False)
        if t is not None:
            trs_output.append(t)
        else:
            if not args.quiet:
                print("Ignored. Wrong tier name {:s}.".format(n))

# Set the other members
for key in trs_input.get_meta_keys():
    trs_output.set_meta(key, trs_input.get_meta(key))

# TODO: copy relevant hierarchy links

# ----------------------------------------------------------------------------
# Write

parser = sppasRW(args.o)
if args.quiet is False:
    print("Write output file:")

start_time = time.time()
parser.write(trs_output)
end_time = time.time()

if args.quiet is False:
    print("  - elapsed time for writing: {:f} seconds".format(end_time - start_time))
    print("Done.")
