#!/usr/bin/env python
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

    bin.selfrepetition.py
    ~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Self-Repetitions automatic annotation.

"""
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotations.SelfRepet.sppasrepet import sppasSelfRepet
from sppas.src.utils.fileutils import setup_logging

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

p = sppasSelfRepet()
dft_span = p.get_option('span')
dft_alpha = p.get_option('alpha')

parser = ArgumentParser(usage="{:s} -i file [options]"
                              "".format(os.path.basename(PROGRAM)),
                        description="Automatic self-repetitions detection.")

parser.add_argument("-i", metavar="file",
                    required=True,
                    help='Input file name with time-aligned tokens')

parser.add_argument("-r", metavar="file",
                    help='List of stop-words')

parser.add_argument("--span",
                    type=int, default=dft_span,
                    help="Span window length in number of IPUs "
                         "(default: {:d}).".format(dft_span))

parser.add_argument("--stopwords",
                    action='store_true',
                    help='Add stop-words estimated from the given data (advised)')

parser.add_argument("--alpha",
                    type=int, default=dft_alpha,
                    help="Coefficient to add specific stop-words in the list "
                         "(default: {:f}).".format(dft_alpha))

parser.add_argument("-o", metavar="file",
                    help='Output file name')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable verbose.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if not args.quiet:
    setup_logging(0, None)
else:
    setup_logging(30, None)

# ----------------------------------------------------------------------------
# Automatic detection is here:
# ----------------------------------------------------------------------------

if args.r:
    p = sppasSelfRepet(args.r)

p.set_alpha(args.alpha)
p.set_span(args.span)
if args.stopwords:
    p.set_use_stopwords(True)
else:
    p.set_use_stopwords(False)

trs_result = p.run(args.i, args.o)

# print result
if not args.o and not args.quiet:
    for tier in trs_result:
        print(tier.get_name())
        for s in tier:
            print(s)
