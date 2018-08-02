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

    bin.tga.py
    ~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      TGA automatic annotation.

"""
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotations.TGA import sppasTGA

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -r config [options]"
                              "".format(os.path.basename(PROGRAM)),
                        prog=PROGRAM,
                        description="TGA automatic annotation.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input file name (time-aligned syllables)')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output file name')

parser.add_argument("-s",
                    metavar="string",
                    required=False,
                    help='Time groups prefix label')

parser.add_argument("--original", dest="original", action='store_true')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Automatic TGA is here:
# ----------------------------------------------------------------------------

tga = sppasTGA()

if args.original:
    tga.set_intercept_slope_original(True)
    tga.set_intercept_slope_annotationpro(False)
if args.s:
    tga.set_tg_prefix_label(args.s)

tga.run(args.i, args.o)
