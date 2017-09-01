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

    scripts.dendity.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to find phoneme reduction density areas of a tier of an annotated file.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.annotationdata.aio
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.transcription import Tier
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.label.label import Label

from sppas.src.calculus.infotheory.kullbackleibler import sppasKullbackLeibler
from sppas.src.calculus.infotheory.utilit import find_ngrams

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file [options]" % os.path.basename(PROGRAM), 
                        description="... a script to find phoneme reduction density areas "
                                    "of a tier of an annotated file.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file file name')

parser.add_argument("-t",
                    metavar="value",
                    default=1,
                    type=int,
                    help='Tier number (default: 1)')

parser.add_argument("-o",
                    metavar="file",
                    help='Output file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Extract parameters, load data...

tier_idx = args.t-1
file_input = args.i
file_output = None
if args.o:
    file_output = args.o
n = 3   # n-value of the ngram
w = 7   # window size

trs = sppas.src.annotationdata.aio.read(file_input)

if tier_idx < 0 or tier_idx > trs.GetSize():
    print('Error: Bad tier number.\n')
    sys.exit(1)

tier = trs[tier_idx]
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
    duration = ann.GetLocation().GetDuration()  # a Duration instance
    if duration == 0.03:
        values.append(1)
    else:
        values.append(0)

# Train an ngram model with the list of values
# ---------------------------------------------

data = find_ngrams(values, n)
kl = sppasKullbackLeibler()
kl.set_epsilon(1.0/(len(data)))
kl.set_model_from_data(data)

print("The model:")
for k, v in kl.model.items():
    print("  --> P({}) = {}".format(k, v))

# Use the model:
# estimate a KL distance between the model and a window on the data
# -----------------------------------------------------------------

# Create a list of all windows (more memory, but faster than a real windowing)
windows = find_ngrams(values, w)

# Estimates the distances between the model and each window
distances = []
for i, window in enumerate(windows):
    ngram_window = find_ngrams(window, n)
    kl.set_observations(ngram_window)
    dist = kl.eval_kld()
    distances.append(dist)

# Bass-pass filter to adjust distances
ngram_window = find_ngrams(tuple([0]*w),n)
kl.set_observations(ngram_window)
base_dist = kl.eval_kld()
print("Base distance for the bass-pass filter {}: {}".format(ngram_window, base_dist))

for i, d in enumerate(distances):
    if d < base_dist:
        distances[i] = 0.
    else:
        distances[i] = distances[i] - base_dist

# Select the windows corresponding to interesting areas
# -----------------------------------------------------

inside = False
idx_begin = 0
areas = []
for i, d in enumerate(distances):
    if d == 0.:
        if inside is True:
            # It's the end of a block of non-zero distances
            inside = False
            areas.append((idx_begin, i-1))
        else:
            # It's the beginning of a block of zero distances
            idx_begin = i+1
            inside = True
    else:
        inside = True

# ----------------------------------------------------------------------------
# From windows to annotations

filtered_tier = Tier('ReductionDensity')

for t in areas:
    idx_begin = t[0]  # index of the first interesting window
    idx_end = t[1]  # index of the last interesting window

    # Find the index of the first interesting annotation
    window_begin = windows[idx_begin]
    i = 0
    while window_begin[i] == 0:
        i = i + 1
    ann_idx_begin = idx_begin + i

    # Find the index of the last interesting annotation
    window_end = windows[idx_end]
    i = w - 1
    while window_end[i] == 0:
        i = i - 1
    ann_idx_end = idx_end + i

    # Assign a label to the new annotation
    max_dist = round(max(distances[idx_begin:idx_end+1]), 2)
    if max_dist == 0:
        print(" ERROR: max dist equal to 0...")

    begin = tier[ann_idx_begin].GetLocation().GetBegin()
    end = tier[ann_idx_end].GetLocation().GetEnd()
    label = Label(max_dist, data_type="float")

    a = Annotation(TimeInterval(begin, end), label)
    filtered_tier.Append(a)

#     for i in range(idxbegin,idxend+1):
#         print windows[i],distances[i]
#         for j in range (w):
#             print tier[i+j].GetLocation().GetDuration().GetValue(),tier[i+j].GetLabel().GetValue(), "/",
#     print " -> maxdist=",maxdist
#     print a
#     print

# ----------------------------------------------------------------------------
# Save result

if file_output is None:
    for a in filtered_tier:
        print(a)
else:
    trs = Transcription()
    trs.Add(filtered_tier)

#     t = Tier('PhonAlign30')
#     for v,a in zip(values,tier):
#         if v == 1:
#             t.Append(a)
#     trs.Add(t)

    sppas.src.annotationdata.aio.write(file_output, trs)
