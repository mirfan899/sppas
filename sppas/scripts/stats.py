#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr00800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ----------------------------------------------------------------------------
# File: stats.py
# ----------------------------------------------------------------------------
# Author: Brigitte Bigi
# Date: November, 25, 2015
# Brief: Produce a csv file with stats of one tier of a file.
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
import os.path
from argparse import ArgumentParser
import codecs

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.append(SPPAS)

import annotationdata.io
from calculus.descriptivesstats  import DescriptiveStatistics
from presenters.tierstats import TierStats


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

modeshelp =  "Stat to estimate, in:\n"
modeshelp += "  0 = ALL,\n"
modeshelp += "  1 = Occurrences,\n"
modeshelp += '  2 = Total duration,\n'
modeshelp += '  3 = Average duration,\n'
modeshelp += '  4 = Median duration,\n'
modeshelp += '  5 = Standard deviation duration.'

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM), description="... a script to estimates stats of a tier of an annotated file.")

parser.add_argument("-i", metavar="file",  required=True,  help='Input annotated file file name')
parser.add_argument("-t", metavar="value", default=1, type=int, help='Tier number (default: 1=first tier)')
parser.add_argument("-s", metavar="stat",  type=int, action="append", help=modeshelp)
parser.add_argument("-n", metavar="ngram", default=1, type=int, help='Value of N of the Ngram sequence (default: 1)')


if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

tieridx    = args.t-1
fileinput  = args.i
filename, fileextension = os.path.splitext(fileinput)
ngram      = args.n
mode       = args.s
stats_mode = (0, 1, 2, 3, 4, 5)
if mode:
    for m in stats_mode:
        if m not in stats_mode:
            print "Unknown stat:", m
            sys.exit(1)
else:
    mode = []
    mode.append(0)

# ----------------------------------------------------------------------------

trs = annotationdata.io.read(fileinput)

if tieridx < 0 or tieridx > trs.GetSize():
    print 'Error: Bad tier number.\n'
    sys.exit(1)

tier = trs[tieridx]

# ----------------------------------------------------------------------------

t = TierStats( tier )
t.set_ngram( ngram )

ds = t.ds()
title = [ "annotation label" ]
stats = {} # used just to get the list of keys
if 0 in mode or 1 in mode:
    occurrences = ds.len()
    title.append('occurrences')
    stats = occurrences
if 0 in mode or 2 in mode:
    total = ds.total()
    title.append('total duration')
    if not stats: stats = total
if 0 in mode or 3 in mode:
    mean = ds.mean()
    title.append('mean duration')
    if not stats: stats = mean
if 0 in mode or 4 in mode:
    median = ds.median()
    title.append('median duration')
    if not stats: stats = median
if 0 in mode or 5 in mode:
    stdev = ds.stdev()
    title.append('Std dev duration')
    if not stats: stats = stdev

# ----------------------------------------------------------------------------

rowdata = []
rowdata.append(title)

for i,key in enumerate(stats.keys()):
    if len(key)==0: # ignore empty label
        continue
    row = [ key ]
    if 0 in mode or 1 in mode:
        row.append( str(occurrences[key]) )
    if 0 in mode or 2 in mode:
        row.append( str(round(total[key],3)) )
    if 0 in mode or 3 in mode:
        row.append( str(round(mean[key],3)) )
    if 0 in mode or 4 in mode:
        row.append( str(round(median[key],3)) )
    if 0 in mode or 5 in mode:
        row.append( str(round(stdev[key],3)) )
    rowdata.append( row )

tiername = tier.GetName().replace (' ','_')
fileoutput = filename + "-" + tiername + "-stats-" + str(ngram)+ ".csv"
with codecs.open(fileoutput, 'w', encoding="utf-8") as fp:
    for row in rowdata:
        s = ','.join( row )
        fp.write( s )
        fp.write('\n')

# ----------------------------------------------------------------------------
