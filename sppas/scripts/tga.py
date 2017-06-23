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

    scripts.tga.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to estimates TGA of syllables from a tier of an annotated file.

"""
import sys
import os.path
from argparse import ArgumentParser
import codecs

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.annotationdata.aio
from sppas.src.presenters.tiertga import TierTGA

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to estimates TGA of syllables from a tier of an annotated file.")

parser.add_argument("-i", metavar="file",      required=True,  help='Input annotated file file name')
parser.add_argument("-o", metavar="file",      required=True,  help='Output file name (csv or annotated file)')
parser.add_argument("-t", metavar="value",     default=1, type=int, help='Tier number (default: 1=first tier)')
parser.add_argument("-s", metavar="separator", type=str, action="append", help="Add a Time Group separator (already included: silence,dummy,laughter,noise)")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

tieridx = args.t-1
fileinput = args.i
fileoutput = args.o
filename, fileextension = os.path.splitext(fileinput)
separators = ['*', 'gb','@@', '+']
if args.s:
    separators = set(separators + args.s)

# ----------------------------------------------------------------------------

trs = sppas.src.annotationdata.aio.read(fileinput)

if tieridx < 0 or tieridx > trs.GetSize():
    print 'Error: Bad tier number.\n'
    sys.exit(1)

tier = trs[tieridx]

# ----------------------------------------------------------------------------

tg = TierTGA(tier)
for s in separators:
    tg.append_separator(s)

ds = tg.tga()
ls = tg.labels()

occurrences = ds.len()
total = ds.total()
mean = ds.mean()
median = ds.median()
stdev = ds.stdev()
npvi = ds.nPVI()
regressp = ds.intercept_slope_original()
regresst = ds.intercept_slope()

# ----------------------------------------------------------------------------

filename, fileextension = os.path.splitext(fileoutput)

if fileextension.lower() == '.csv':
    title = ["Filename", "Tier", "TG name", "TG segments", "Length", "Total", "Mean", "Median", "Std dev.", "nPVI", "Intercept-Pos","Slope-Pos", "Intercept-Time","Slope-Time"]

    rowdata = list()
    rowdata.append(title)

    for i,key in enumerate(sorted(ls)):
        if len(key) == 0:  # ignore empty label
            continue
        segs = " ".join(ls[key])
        row = list()
        row.append(fileinput)
        row.append(tier.GetName())
        row.append(key)
        row.append(" ".join(ls[key]))
        row.append(str(occurrences[key]))
        row.append(str(round(total[key],       3)))
        row.append(str(round(mean[key],        3)))
        row.append(str(round(median[key],      3)))
        row.append(str(round(stdev[key],       3)))
        row.append(str(round(npvi[key],        3)))
        row.append(str(round(regressp[key][0], 3)))
        row.append(str(round(regressp[key][1], 3)))
        row.append(str(round(regresst[key][0], 3)))
        row.append(str(round(regresst[key][1], 3)))
        rowdata.append(row)

    with codecs.open(fileoutput, 'w', encoding="utf-8") as fp:
        for row in rowdata:
            s = ','.join(row)
            fp.write(s)
            fp.write('\n')

else:
    trs = tg.tga_as_transcription()
    sppas.src.annotationdata.aio.write(fileoutput,trs)
