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

    scripts.tierfiller.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to fill empty labels of a tier of an annotated file.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.annotationdata.aio
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.aio.utils import fill_gaps

# ----------------------------------------------------------------------------


def fct_fill(tier, filler):
    """
    Fill empty annotations with a specific filler.
    
    """
    labelfiller = Label(filler)
    i = tier.GetSize()-1
    while i >= 0:
        ann = tier[i]
        while ann.GetLabel().IsEmpty() and i >= 0:
            print " * Fill interval number", i+1,":",ann.GetLocation().GetBegin().GetValue(),ann.GetLocation().GetEnd().GetValue()
            ann.GetLabel().Set(labelfiller)
            # the next annotation is labelled with our filler
            if i<tier.GetSize()-1 and tier[i+1].GetLabel().GetValue() == labelfiller.GetValue():
                print " * Merge:",tier[i+1].GetLocation().GetBegin().GetValue(),tier[i+1].GetLocation().GetEnd().GetValue()
                print "   with:",ann.GetLocation().GetBegin().GetValue(),ann.GetLocation().GetEnd().GetValue()
                end = tier[i+1].GetLocation().GetEnd()
                tier.Pop(i+1)
                ann.GetLocation().SetEnd(end)
                print "   gives:",ann.GetLocation().GetBegin().GetValue(),ann.GetLocation().GetEnd().GetValue()
            i = i - 1
            if i >= 0:
                ann = tier[i]
        
        if i>0 and ann.GetLabel().GetValue() == labelfiller.GetValue():
            # the previous annotation is labelled with our filler
            if i>0 and tier[i-1].GetLabel().GetValue() == labelfiller.GetValue() and ann.GetLabel().GetValue() == labelfiller.GetValue():
                print " * Merge:",tier[i-1].GetLocation().GetBegin().GetValue(),tier[i-1].GetLocation().GetEnd().GetValue()
                print "   with:",ann.GetLocation().GetBegin().GetValue(),ann.GetLocation().GetEnd().GetValue()
                i = i - 1
                ann = tier[i]
                end = tier[i+1].GetLocation().GetEnd()
                tier.Pop(i+1)
                ann.GetLocation().SetEnd(end)
                print "   gives:",ann.GetLocation().GetBegin().GetValue()
            # the next annotation is labelled with our filler
            elif i<tier.GetSize()-1 and tier[i+1].GetLabel().GetValue() == labelfiller.GetValue():
                print " * Merge:",tier[i+1].GetLocation().GetBegin().GetValue(),tier[i+1].GetLocation().GetEnd().GetValue()
                print "   with:",ann.GetLocation().GetBegin().GetValue(),ann.GetLocation().GetEnd().GetValue()
                end = tier[i+1].GetLocation().GetEnd()
                tier.Pop(i+1)
                ann.GetLocation().SetEnd(end)
                print "   gives:",ann.GetLocation().GetBegin().GetValue(),ann.GetLocation().GetEnd().GetValue()
        i = i - 1

    return tier

# ----------------------------------------------------------------------------


def fct_clean(tier, filler, duration):
    """
    Merge too short intervals with the previous one if filler match.
    
    """
    i = tier.GetSize()-1
    while i > 0:
        ann = tier[i]
        labelfiller = Label(filler)
        if ann.GetLabel().GetValue() == labelfiller.GetValue():
            annduration = ann.GetLocation().GetDuration().GetValue()
            if annduration < duration:
                print " * Merge:",tier[i-1].GetLocation().GetBegin().GetValue(),tier[i-1].GetLocation().GetEnd().GetValue(),"label:",tier[i-1].GetLabel().GetValue()
                print "   with:",ann.GetLocation().GetBegin().GetValue(),ann.GetLocation().GetEnd().GetValue(),"label:",ann.GetLabel().GetValue()
                i = i - 1
                ann = tier[i]
                end = tier[i+1].GetLocation().GetEnd()
                tier.Pop(i+1)
                ann.GetLocation().SetEnd(end)
                print "   gives:",ann.GetLocation().GetBegin().GetValue(),ann.GetLocation().GetEnd().GetValue(),"label:",ann.GetLabel().GetValue()

        i = i - 1

    return tier

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to fill empty labels of a tier of an annotated file.")

parser.add_argument("-i", metavar="file", required=True,  help='Input annotated file name')
parser.add_argument("-t", metavar="value", required=False, action='append', type=int, help='A tier number (use as many -t options as wanted). Positive or negative value: 1=first tier, -1=last tier.')
parser.add_argument("-o", metavar="file", required=True, help='Output file name')
parser.add_argument("-f", metavar="text", required=False, default="#", help='Text to fill with (default:#)')
parser.add_argument("-d", metavar="duration", required=False, default=0.02, type=float, help='Minimum duration of a filled interval (default:0.02)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Read

trsinput = sppas.src.annotationdata.aio.read( args.i )

# Take all tiers or specified tiers
tiersnumbs = list()
if not args.t:
    tiersnumbs = range(1, (trsinput.GetSize() + 1))
elif args.t:
    tiersnumbs = args.t

# ----------------------------------------------------------------------------
# Fill

trsout = Transcription()

for i in tiersnumbs:
    tier = trsinput[i-1]

    tier = fill_gaps(tier, trsinput.GetMinTime(), trsinput.GetMaxTime())
    ctrlvocab = tier.GetCtrlVocab()
    if ctrlvocab is not None:
        if ctrlvocab.Contains(args.f) is False:
            ctrlvocab.Append( args.f, descr="Filler" )

    print "Tier: ", tier.GetName()
    print "Fill empty intervals with", args.f, "(and merge with previous or following if any)"
    tier = fct_fill(tier, args.f)
    print "Merge intervals during less than",args.d
    tier = fct_clean(tier, args.f, args.d)
    print()
    trsout.Append(tier)

# ----------------------------------------------------------------------------
# Write

sppas.src.annotationdata.aio.write(args.o, trsout)

# ----------------------------------------------------------------------------
