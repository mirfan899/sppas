#!/usr/bin/env python
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

    bin.syllabify.py
    ~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Syllabification automatic annotation.

"""
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotations.Syll.sppassyll import sppasSyll


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -r config [options]"
                              "".format(os.path.basename(PROGRAM)),
                        prog=PROGRAM,
                        description="Syllabification automatic annotation.")

parser.add_argument("-r",
                    "--config",
                    required=True,
                    help='Rules configuration file name')

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input file name (time-aligned phonemes)')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output file name')

parser.add_argument("-t",
                    metavar="string",
                    required=False,
                    help='Reference tier name to syllabify between intervals')

parser.add_argument("--nophn",
                    action='store_true',
                    help="Disable the output of the result that does not "
                         "use the reference tier")

parser.add_argument("--noclass",
                    action='store_true',
                    help="Disable the creation of the tier with syllable "
                         "classes")


if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

if args.nophn and not args.t:
    print("Warning. The option --nophn will not have any effect! "
          "It must be used with -t option.")


# ----------------------------------------------------------------------------
# Automatic Syllabification is here:
# ----------------------------------------------------------------------------

syll = sppasSyll(args.config)

if args.t:
    syll.set_usesintervals(True)
    syll.set_tiername(args.t)
    if args.noclass:
        syll.set_create_tier_classes(False)
    if args.nophn:
        syll.set_usesphons(False)

syll.run(args.i, args.o)
