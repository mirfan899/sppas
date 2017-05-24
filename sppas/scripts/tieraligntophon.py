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

    scripts.tieraligntophon.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to a time-aligned phonemes tier to its phonetization tier.

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
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.annotation import Annotation

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to convert time-aligned phonemes into their phonetization.")

parser.add_argument("-i", metavar="file", required=True, help='Input annotated file name')
parser.add_argument("-o", metavar="file", required=True, help='Output file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Read

trsinput = sppas.src.annotationdata.aio.read(args.i)
aligntier = trsinput.Find("PhonAlign", case_sensitive=False)
if aligntier is None:
    print("ERROR: PhonAlign tier not found.")
    sys.exit(1)

trsout = Transcription()

# ----------------------------------------------------------------------------
# Transform the alignment tier to a phonetization tier 

#separators = ['#', '@@', 'euh', 'fp', 'gb', '##', '*', 'dummy']
separators = ['#', 'sil']

phontier = trsout.NewTier("Phonetization")
b = aligntier.GetBegin()
e = b
l = ""
for a in aligntier:
	if a.GetLabel().IsSilence() is True or a.GetLabel().GetValue() in separators:
		if len(l) > 0 and e > b:
			at = Annotation(TimeInterval(b,e), Label(l))
			phontier.Add(at)
		phontier.Add(a)
		b = a.GetLocation().GetEnd()
		e = b
		l = ""
	else:
		e = a.GetLocation().GetEnd()
		label = a.GetLabel().GetValue()
		label = label.replace('.', ' ')
		if a.GetLabel().IsEmpty() is False:
			l = l + " " + label

if e > b:
	a = aligntier[-1]
	label = a.GetLabel().GetValue()
	label = label.replace('.', ' ')
	at = Annotation(TimeInterval(b,e), Label(l))
	phontier.Add(at)


# ----------------------------------------------------------------------------
# Write

sppas.src.annotationdata.aio.write(args.o, trsout)
