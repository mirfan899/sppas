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

    scripts.trsbehavior.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to annotate behavior of tiers of an annotated file.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.annotationdata.aio
from sppas.src.annotationdata import Tier
from sppas.src.annotationdata import Annotation
from sppas.src.annotationdata import Label
from sppas.src.annotationdata import TimePoint
from sppas.src.annotationdata import TimeInterval

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to annotate behavior of tiers of an annotated file.")

parser.add_argument("-i", metavar="file",  required=True,  help='Input annotated file name')
parser.add_argument("-t", metavar="value", required=False, action='append', type=int, help='A tier number (use as many -t options as wanted). Positive or negative value: 1=first tier, -1=last tier.')
parser.add_argument("-o", metavar="file",  required=True,  help='Output file name')
parser.add_argument("-d", metavar="delta", required=False, default=0.04, type=float, help='Framerate to create intervals (default:0.04)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Read

trsinput = sppas.src.annotationdata.aio.read( args.i )

# Take all tiers or specified tiers
tiersnumbs = []
if not args.t:
    tiersnumbs = range(1, (trsinput.GetSize() + 1))
elif args.t:
    tiersnumbs = args.t

# ----------------------------------------------------------------------------

delta = args.d
start = int(trsinput.GetMinTime() / delta)
finish = int(trsinput.GetMaxTime() / delta)

btier = Tier("Behavior")

for i in range(start, finish):
    texts = []
    b = (i+start)*delta
    e = b+delta

    for t in tiersnumbs:
        tier = trsinput[t-1]
        # get only ONE annotation in our range
        anns = tier.Find(b, e, overlaps=True)
        if len(anns) > 1:
            anni = tier.Near(b+int(delta/2.), direction=0)
            ann = tier[anni]
        else:
            ann = anns[0]
        texts.append(ann.GetLabel().GetValue())

    # Append in new tier
    ti = TimeInterval(TimePoint(b, 0.0001), TimePoint(e, 0.0001))
    if len(texts) > 1:
        missing = False
        for t in texts:
            if len(t.strip()) == 0:
                # missing annotation label...
                missing = True
        if missing is True:
            text = ""
        else:
            text = ";".join(texts)
    else:
        text = str(texts[0])
    ann = Annotation(ti, Label(text))
    btier.Append(ann)

# ----------------------------------------------------------------------------

stier = Tier("Synchronicity")
for ann in btier:
    sann = ann.Copy()
    if sann.GetLabel().IsEmpty() is False:
        text = sann.GetLabel().GetValue()
        values = text.split(';')
        v1 = values[0].strip()
        v2 = values[1].strip()
        if v1 == "0" or v2 == "0":
            if v1 == "0" and v2 == "0":
                sann.GetLabel().SetValue("-1")
            else:
                sann.GetLabel().SetValue("0")
        else:
            if v1 != v2:
                sann.GetLabel().SetValue("1")
            else:
                sann.GetLabel().SetValue("2")
    stier.Append(sann)

# ----------------------------------------------------------------------------
# Write

trsinput.Append(btier)
trsinput.Append(stier)

sppas.src.annotationdata.aio.write(args.o, trsinput)

# ----------------------------------------------------------------------------
