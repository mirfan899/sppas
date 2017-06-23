#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Open an annotated file, select tiers and save into a new file.

"""  

# ----------------------------------------------------------------------------
# Get SPPAS API
# ----------------------------------------------------------------------------
import sys
import os.path
sys.path.append(os.path.join("..",".."))

import sppas.src.annotationdata.aio as aio
from sppas.src.annotationdata import Transcription

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

# The input file name
filename='F_F_B003-P9-merge.TextGrid'

# The list of tiers we want to select
tiernames=['PhonAlign','TokensAlign', 'toto']

# The output file name
outputfilename='F_F_B003-P9-selection.TextGrid'

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file.
trs = aio.read(filename)
print("Number of tiers: {:d}.".format(trs.GetSize()))

# Create a new Transcription to add selected tiers.
newtrs = Transcription()

# Select some tiers, add into the new Transcription
for name in tiernames:
    tier = trs.Find(name, case_sensitive=False)
    if tier is not None:
        newtrs.Append(tier)
        print("Tier {:s} successfully added.".format(tier.GetName()))
    else:
        print("Error: the file does not contain a tier with name = {:s}".format(name))

# Save the Transcription into a file.
aio.write(outputfilename, newtrs)

# ----------------------------------------------------------------------------
