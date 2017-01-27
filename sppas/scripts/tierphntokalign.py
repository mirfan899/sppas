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

    scripts.tierphntokalign.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to append the tier PhnTokAlign in a time-aligned file.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.annotationdata.aio
from sppas.src.annotationdata import Tier

# ----------------------------------------------------------------------------
# 0. Verify and extract args:

parser = ArgumentParser(usage="%s -i file [options]" % os.path.basename(PROGRAM),
                        description="... a script to append the tier PhnTokAlign in a time-aligned file.")
parser.add_argument("-i", metavar="file", required=True,  help='Input annotated file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------
# 1. Read input data file

trs = sppas.src.annotationdata.aio.read(args.i)

tierphon = trs.Find('PhonAlign')
if tierphon is None:
    print "Error: can't find the tier PhonAlign."
    sys.exit(1)

tiertoken = trs.Find('TokensAlign')
if tiertoken is None:
    print "Error: can't find the tier TokensAlign."
    sys.exit(1)


# ----------------------------------------------------------------------------
# 2. Create the expected data

newtier = Tier('PhnTokAlign')

for anntoken in tiertoken:

    # Create the sequence of phonemes
    beg = anntoken.GetLocation().GetBegin()
    end = anntoken.GetLocation().GetEnd()
    annphons = tierphon.Find(beg, end)
    l = "-".join(ann.GetLabel().GetValue() for ann in annphons)

    # Append in the new tier
    newann = anntoken.Copy()
    newann.GetLabel().SetValue(l)
    newtier.Add(newann)

# ----------------------------------------------------------------------------
# 3. Save new version of the file

trs.Append(newtier)
sppas.src.annotationdata.aio.write(args.i, trs)
