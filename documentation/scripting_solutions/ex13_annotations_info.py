#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Open an annotated file and print information about annotations
                of a given tier.

"""

import sys
import os.path
sys.path.append(os.path.join("..", ".."))

import sppas.src.annotationdata.aio as trsaio
from sppas.src.annotationdata import Transcription


# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

filename = 'F_F_B003-P9-merge.TextGrid'
tiername = "PhonAlign"

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file.
print("Take a look at file {:s}:".format(filename))
trs = trsaio.read(filename)
tier = trs.Find(tiername, case_sensitive=False)

if tier is None:
    print("No tier {:s} in file {:s} ".format(tiername, filename))
    sys.exit(1)

# Check the tier type
tier_type = "Unknown"
if tier.IsPoint() is True:
    tier_type = "Point"
elif tier.IsInterval() is True:
    tier_type = "Interval"

# Get the number of silences
nb_silence = len([a for a in tier if a.GetLabel().IsSilence()])

# Get the number of empty labels
nb_empty = len([a for a in tier if a.GetLabel().IsEmpty()])

# Get the duration of silences
dur_silence = sum(a.GetLocation().GetDuration().GetValue() for a in tier if a.GetLabel().IsSilence())

# Get the duration of empty labels
dur_empty = sum(a.GetLocation().GetDuration() for a in tier if a.GetLabel().IsEmpty())

# Print all information
print(" Tier: {:s}".format(tier.GetName()))
print("    - Type: {:s}".format(tier_type))
print("    - Number of annotations:      {:d}".format(len(tier)))
print("    - Number of silences:         {:d}".format(nb_silence))
print("    - Number of empty intervals:  {:d}".format(nb_empty))
print("    - Number of speech intervals: {:d}".format(len(tier) - (nb_empty + nb_silence)))
print("    - Silence duration: {:.3f}".format(dur_silence))
print("    - Empties duration: {:.3f}".format(dur_empty))
print("    - Speech duration:  {:.3f}".format((tier[-1].GetLocation().GetEnd().GetValue() - tier[0].GetLocation().GetBegin().GetValue() - (dur_empty + dur_silence))))
