#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:       Open an annotated file and print information about annotations
                of a given tier.

"""

import sys
import os
from os.path import *
sys.path.append( join("..","..", "sppas", "src") )

import annotationdata.io
from annotationdata import Transcription

import sys

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

filename='F_F_B003-P9-merge.TextGrid'
tiername="PhonAlign"

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file.
trs = annotationdata.io.read(filename)
tier = trs.Find(tiername, case_sensitive=False)

if tier is None:
    print "No tier", tiername, " in file ", filename
    sys.exit(1)

# Check the tier type
if tier.IsPoint() == True:
   tier_type = "Point"
else:
   tier_type = "Interval"

# Get the number of silences
nb_silence = len([a for a in tier if a.GetLabel().IsSilence()])

# Get the number of empty labels
nb_empty = len([a for a in tier if a.GetLabel().IsEmpty()])

# Get the duration of silences
dur_silence = sum(a.GetLocation().GetDuration().GetValue() for a in tier if a.GetLabel().IsSilence())

# Get the duration of empty labels
dur_empty = sum(a.GetLocation().GetDuration() for a in tier if a.GetLabel().IsEmpty())

# Print all informations
print "Tier name: ", tier.GetName()
print "Tier type: ", tier_type
print "Tier size: ", len(tier)
print "   - Number of silences:         ", nb_silence
print "   - Number of empty intervals:  ", nb_empty
print "   - Number of speech intervals: ", len(tier) - (nb_empty + nb_silence)
print "   - silence duration: ", dur_silence
print "   - empties duration: ", dur_empty
print "   - speech duration:  ", (tier[-1].GetLocation().GetEnd().GetValue() - tier[0].GetLocation().GetBegin().GetValue() - (dur_empty + dur_silence))

# ----------------------------------------------------------------------------
