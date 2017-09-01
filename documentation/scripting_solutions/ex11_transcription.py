#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Open an annotated file, select tiers and save into a new file.

"""  

# ----------------------------------------------------------------------------
# Get SPPAS API
# ----------------------------------------------------------------------------
import sys
import os.path
SPPAS_IS_HERE = os.path.join("..", "..")
sys.path.append(SPPAS_IS_HERE)

import sppas.src.annotationdata.aio as trsaio
from sppas.src.annotationdata import Transcription

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

# The input file name
filename = 'F_F_B003-P9-merge.TextGrid'

# The list of tiers we want to select
tier_names = ['PhonAlign', 'TokensAlign', 'toto']

# The output file name
output_filename = 'F_F_B003-P9-selection.TextGrid'

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file.
print("Read the file {:s}".format(filename))
trs = trsaio.read(filename)
print("   Number of tiers: {:d}.".format(trs.GetSize()))

# Create a new Transcription to add selected tiers.
new_trs = Transcription()

# Select some tiers, add into the new Transcription
for name in tier_names:
    tier = trs.Find(name, case_sensitive=False)
    if tier is not None:
        new_trs.Append(tier)
        print("    Tier {:s} successfully added.".format(tier.GetName()))
    else:
        print("    Error: the file does not contain a tier with name = {:s}".format(name))

# Save the Transcription into a file.
trsaio.write(output_filename, new_trs)
if os.path.exists(output_filename) is True:
    print("The file {:s} was successfully saved.".format(output_filename))
else:
    print("The file {:s} wasn't saved.".format(output_filename))
