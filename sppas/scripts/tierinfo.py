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

    scripts.tierinfo.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to get information about a tier of an annotated file.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.annotationdata.aio

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file [options]" % os.path.basename(PROGRAM),
                        description="... a script to get information about a tier of an annotated file.")

parser.add_argument("-i", metavar="file", required=True,  help='Input annotated file name')
parser.add_argument("-t", metavar="value", default=1, type=int, help='Tier number (default: 1)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

trs = sppas.src.annotationdata.aio.read(args.i)

if args.t <= 0 or args.t > trs.GetSize():
    print 'Error: Bad tier number.\n'
    sys.exit(1)
tier = trs[args.t-1]

if tier.IsPoint() is True:
    tier_type = "Point"
elif tier.IsInterval() is True:
    tier_type = "Interval"
elif tier.IsDisjoint() is True:
    tier_type = "Disjoint"
else:
    tier_type = "Unknown"

nb_silence = len([a for a in tier if a.GetLabel().IsSilence()])
nb_empty = len([a for a in tier if a.GetLabel().IsEmpty()])
dur_silence = sum(a.GetLocation().GetValue().Duration().GetValue() for a in tier if a.GetLabel().IsSilence())
dur_empty = sum(a.GetLocation().GetValue().Duration().GetValue() for a in tier if a.GetLabel().IsEmpty())

print "Tier name: ", tier.GetName()
print "Tier type: ", tier_type
print "Tier size: ", tier.GetSize()
print "   - Number of silences:         ", nb_silence
print "   - Number of empty intervals:  ", nb_empty
print "   - Number of speech intervals: ", tier.GetSize() - (nb_empty + nb_silence)
print "   - silence duration: ", dur_silence
print "   - empties duration: ", dur_empty
print "   - speech duration:  ", (tier.GetEndValue() - tier.GetBeginValue()) - (dur_empty + dur_silence)

# ----------------------------------------------------------------------------
