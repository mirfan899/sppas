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
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to export annotations files.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotationdata.transcription import Transcription
import sppas.src.annotationdata.aio

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

if args.quiet is False:
    sys.stdout.write("Read input file:")
trsinput = sppas.src.annotationdata.aio.read(args.i)
if args.quiet is False:
    print(" [  OK  ]")

# ----------------------------------------------------------------------------
# Select tiers

# Take all tiers or specified tiers
tiersnumbs = []
if not args.t and not args.n:
    tiersnumbs = range(1, (trsinput.GetSize() + 1))
elif args.t:
    tiersnumbs = args.t

# Select tiers to create output
trsoutput = Transcription(name=trsinput.GetName())

# Add selected tiers into output
for i in tiersnumbs:
    if args.quiet is False:
        sys.stdout.write(" -> Tier "+str(i)+":")
    if i > 0:
        idx = i-1
    elif i < 0:
        idx = i
    else:
        idx = trsinput.GetSize()
    if idx<trsinput.GetSize():
        trsoutput.Append(trsinput[idx])
        if args.quiet is False:
            print(" [  OK  ]")
    else:
        if not args.quiet is True:
            print(" [IGNORED] Wrong tier number.")

if args.n:
    for n in args.n:
        t = trsinput.Find(n, case_sensitive=False)
        if t is not None:
            trsoutput.Append(t)
        else:
            if not args.quiet is True:
                print(" [IGNORED] Wrong tier name.")

# Set the other members
trsoutput.metadata = trsinput.metadata
#TODO: copy relevant hierarchy links

# ----------------------------------------------------------------------------
# Write

if args.quiet is False:
    sys.stdout.write("Write output file:")
sppas.src.annotationdata.aio.write(args.o, trsoutput)
if args.quiet is False:
    print(" [  OK  ]")
