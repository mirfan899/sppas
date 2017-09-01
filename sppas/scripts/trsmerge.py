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

    scripts.trsmerge.py
    ~~~~~~~~~~~~~~~~~~~

    ... a script to merge annotation files.

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
                        description="... a script to merge annotation files.")

parser.add_argument("-i",
                    metavar="file",
                    action='append',
                    required=True,
                    help='Input annotated file name (as many as wanted)')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output annotated file name')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

trs_output = Transcription("SPPAS Merge")

for trs_input_file in args.i:

    if not args.quiet:
        print("Read input annotated file:")
    trs_input = sppas.src.annotationdata.aio.read(trs_input_file)

    # Take all tiers
    for i in range(trs_input.GetSize()):
        if not args.quiet:
            sys.stdout.write(" -> Tier "+str(i+1)+": ")
        trs_output.Append(trs_input[i])
        if not args.quiet:
            print(" [  OK  ]")

if not args.quiet:
    sys.stdout.write("Write output file: ")
sppas.src.annotationdata.aio.write(args.o, trs_output)
if not args.quiet:
    print(" [  OK  ]")
