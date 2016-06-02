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
#           http://www.lpl-aix.fr/~bigi/sppas
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2014  Brigitte Bigi
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
# ---------------------------------------------------------------------------
# File: density.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2014  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
import os.path
from argparse import ArgumentParser
import collections

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.append(SPPAS)

import annotationdata.io
from annotationdata.transcription  import Transcription
from annotationdata.transcription  import Tier
from annotationdata.annotation     import Annotation
from annotationdata.ptime.interval import TimeInterval
from annotationdata.label.label    import Label

from calculus.infotheory.kullback import Kullback

# ----------------------------------------------------------------------------

def find_ngrams( symbols, ngram):
    return zip(*[symbols[i:] for i in range(ngram)])

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file [options]" % os.path.basename(PROGRAM), description="... a script to find phoneme reduction density areas of a tier of an annotated file.")

parser.add_argument("-i", metavar="file", required=True,  help='Input annotated file file name')
parser.add_argument("-t", metavar="value", default=1, type=int, help='Tier number (default: 1)')
parser.add_argument("-o", metavar="file", help='Output file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Extract parameters, load data...

tieridx    = args.t-1
fileinput  = args.i
fileoutput = None
if args.o: fileoutput = args.o
n = 3   # n-value of the ngram
w = 7   # window size

trs = annotationdata.io.read(fileinput)

if tieridx < 0 or tieridx > trs.GetSize():
    print 'Error: Bad tier number.\n'
    sys.exit(1)

tier = trs[tieridx]
tier.SetRadius(0.001)

# ----------------------------------------------------------------------------
# Extract areas in which there is a density of phonemes reductions

# Extract phonemes during 30ms
# ----------------------------
# We create a list of the same size than the tier, with values:
# 0: the phoneme is not during 30ms
# 1: the phoneme is during 30ms
values = []
for ann in tier:
    duration = ann.GetLocation().GetDuration() # a Duration instance
    if duration == 0.03:
        values.append(1)
    else:
        values.append(0)

# Train an ngram model with the list of values
# ---------------------------------------------

data = find_ngrams(values,n)
kl = Kullback()
kl.set_epsilon(1.0/(len(data)))
kl.set_model_from_data( data )

print "The model:"
for k,v in kl.model.items():
    print "  --> P(",k,") =",v

# Use the model:
# estimate a KL distance between the model and a window on the data
# -----------------------------------------------------------------

# Create a list of all windows (more memory, but faster than a real windowing)
windows = find_ngrams(values, w)

# Estimates the distances between the model and each window
distances = []
for i,window in enumerate(windows):
    ngramwindow = find_ngrams(window, n)
    kl.set_ngrams(ngramwindow)
    dist = kl.get()
    distances.append(dist)

# Bass-pass filter to adjust distances
ngramwindow = find_ngrams(tuple([0]*w),n)
kl.set_ngrams(ngramwindow)
basedist = kl.get()
print "Base distance for the bass-pass filter, ",ngramwindow," : ",basedist

for i,d in enumerate(distances):
    if d < basedist:
        distances[i] = 0.
    else:
        distances[i] = distances[i] - basedist

# Select the windows corresponding to interesting areas
# -----------------------------------------------------

inside = False
idxbegin = 0
areas = []
for i,d in enumerate(distances):
    if d == 0.:
        if inside is True:
            # It's the end of a block of non-zero distances
            inside = False
            areas.append((idxbegin,i-1))
        else:
            # It's the beginning of a block of zero distances
            idxbegin = i+1
            inside = True
    else:
        inside = True

# ----------------------------------------------------------------------------
# From windows to annotations

filteredtier = Tier('ReductionDensity')

for t in areas:
    idxbegin = t[0]  # index of the first interesting window
    idxend   = t[1]  # index of the last interesting window

    # Find the index of the first interesting annotation
    windowbegin = windows[idxbegin]
    i=0
    while windowbegin[i] == 0:
        i = i + 1
    annidxbegin = idxbegin+i

    # Find the index of the last interesting annotation
    windowend = windows[idxend]
    i=w-1
    while windowend[i] == 0:
        i = i - 1
    annidxend = idxend+i

    # Assign a label to the new annotation
    maxdist = round(max( distances[idxbegin:idxend+1] ),2)
    if maxdist == 0:
        print " ERROR: max dist equal to 0..."

    begin = tier[annidxbegin].GetLocation().GetBegin()
    end   = tier[annidxend].GetLocation().GetEnd()
    label = Label(maxdist,data_type="float")

    a = Annotation(TimeInterval(begin,end),label)
    filteredtier.Append( a )

#     for i in range(idxbegin,idxend+1):
#         print windows[i],distances[i]
#         for j in range (w):
#             print tier[i+j].GetLocation().GetDuration().GetValue(),tier[i+j].GetLabel().GetValue(), "/",
#     print " -> maxdist=",maxdist
#     print a
#     print

# ----------------------------------------------------------------------------
# Save result

if fileoutput is None:
    for a in filteredtier:
        print a
else:
    trs = Transcription()
    trs.Add( filteredtier )

#     t = Tier('PhonAlign30')
#     for v,a in zip(values,tier):
#         if v == 1:
#             t.Append(a)
#     trs.Add( t )

    annotationdata.io.write(fileoutput, trs)
