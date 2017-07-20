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

    bin.phonetize.py
    ~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Phonetization automatic annotation.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotations.Phon.sppasphon import sppasPhon
from sppas.src.annotations.Phon.phonetize import sppasDictPhonetizer
from sppas.src.resources.dictpron import sppasDictPron
from sppas.src.resources.mapping import sppasMapping
from sppas.src.utils.fileutils import setup_logging


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -r dict [options]" % os.path.basename(PROGRAM),
                        prog=PROGRAM,
                        description="Phonetization automatic annotation.")

parser.add_argument("-r", "--dict",
                    required=True,
                    help='Pronunciation dictionary file name (HTK-ASCII format).')

parser.add_argument("-m", "--map",
                    required=False,
                    help='Pronunciation mapping table. '
                         'It is used to generate new pronunciations by mapping phonemes of the dictionary.')

parser.add_argument("-i",
                    metavar="file",
                    required=False,
                    help='Input file name')

parser.add_argument("-o",
                    metavar="file",
                    required=False,
                    help='Output file name (required only if -i is fixed)')

parser.add_argument("--nounk",
                    action='store_true',
                    help="Disable unknown word phonetization.")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable verbose.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if not args.quiet:
    setup_logging(1, None)

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
    p = sppasPhon(args.dict, mapfile)
    p.set_unk(unkopt)
    p.set_usestdtokens(False)
    p.run(args.i, args.o)
else:
    pdict = sppasDictPron(args.dict, nodump=False)
    maptable = sppasMapping()
    if mapfile is not None:
        maptable = sppasMapping(mapfile)
    phonetizer = sppasDictPhonetizer(pdict, maptable)
    for line in sys.stdin:
        print("{:s}".format(phonetizer.phonetize(line, unkopt)))
