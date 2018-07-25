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

    scripts.stats.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to estimates stats of a tier of an/several annotated file.

"""
import sys
import os.path
from argparse import ArgumentParser
import codecs

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas
import sppas.src.annotationdata.aio
from sppas.src.presenters.tierstats import TierStats

# ----------------------------------------------------------------------------
# Check args:

modeshelp = "Stat to estimate, in:\n"
modeshelp += "  0 = ALL,\n"
modeshelp += "  1 = Occurrences,\n"
modeshelp += '  2 = Total duration,\n'
modeshelp += '  3 = Average duration,\n'
modeshelp += '  4 = Median duration,\n'
modeshelp += '  5 = Standard deviation duration.'

parser = ArgumentParser(usage="%s -i file [options]" % os.path.basename(PROGRAM),
                        description="... a script to estimates stats of a tier of an/several annotated file.")

parser.add_argument("-i",
                    metavar="file",
                    action='append',
                    required=True,
                    help='Input annotated file name (as many as wanted)')

parser.add_argument("-t",
                    metavar="value",
                    default=1,
                    type=int,
                    help='Tier number (default: 1=first tier)')

parser.add_argument("-s",
                    metavar="stat",
                    type=int,
                    action="append",
                    help=modeshelp)

parser.add_argument("-n",
                    metavar="ngram",
                    default=1,
                    type=int,
                    help='Value of N of the Ngram sequence (default: 1)')

parser.add_argument("-o",
                    metavar="file",
                    required=False,
                    help='Output annotated file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Extrac args

tieridx = args.t-1
fileinput = args.i
filename, fileextension = os.path.splitext(fileinput[0])

ngram = args.n
mode = args.s
stats_mode = (0, 1, 2, 3, 4, 5)
if mode:
    for m in stats_mode:
        if m not in stats_mode:
            print("Unknown stat: {}".format(m))
            sys.exit(1)
else:
    mode = list()
    mode.append(0)

# ----------------------------------------------------------------------------
# Read data

tiername = None
tiers = []
for trs in args.i:

    trsinput = sppas.src.annotationdata.aio.read(trs)

    if tieridx < 0 or tieridx > trsinput.GetSize():
        print('Error: Bad tier number.')
        sys.exit(1)

    tier = trsinput[tieridx]
    if tiername is None:
        tiername = tier.GetName().replace(' ', '_')
    tiers.append(tier)

# ----------------------------------------------------------------------------
# Estimates stats

t = TierStats(tiers)
t.set_ngram(ngram)

ds = t.ds()
title = ["filename", "tier", "annotation label"]
stats = {}  # used just to get the list of keys
if 0 in mode or 1 in mode:
    occurrences = ds.len()
    title.append('occurrences')
    stats = occurrences
if 0 in mode or 2 in mode:
    total = ds.total()
    title.append('total duration')
    if not stats:
        stats = total
if 0 in mode or 3 in mode:
    mean = ds.mean()
    title.append('mean duration')
    if not stats:
        stats = mean
if 0 in mode or 4 in mode:
    median = ds.median()
    title.append('median duration')
    if not stats:
        stats = median
if 0 in mode or 5 in mode:
    stdev = ds.stdev()
    title.append('Std dev duration')
    if not stats:
        stats = stdev

# ----------------------------------------------------------------------------
# Format stats

rowdata = list()
rowdata.append(title)

for i, key in enumerate(stats.keys()):
    if len(key) == 0:  # ignore empty label
        continue
    row = [filename, tiername, key]
    if 0 in mode or 1 in mode:
        row.append(str(occurrences[key]))
    if 0 in mode or 2 in mode:
        row.append(str(round(total[key], 3)))
    if 0 in mode or 3 in mode:
        row.append(str(round(mean[key], 3)))
    if 0 in mode or 4 in mode:
        row.append(str(round(median[key], 3)))
    if 0 in mode or 5 in mode:
        row.append(str(round(stdev[key], 3)))
    rowdata.append(row)

# ----------------------------------------------------------------------------
# Save stats
if args.o:
    fileoutput = args.o
else:
    fileoutput = filename + "-" + tiername + "-stats-" + str(ngram) + ".csv"
with codecs.open(fileoutput, 'w', sppas.__encoding__) as fp:
    for row in rowdata:
        s = ','.join(row)
        fp.write(s)
        fp.write('\n')
