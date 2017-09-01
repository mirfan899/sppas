#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Open an annotated file and print information about tiers.

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

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file.
print("Take a look at file {:s}:".format(filename))
trs = trsaio.read(filename)

for tier in trs:

    # Get the tier type
    tier_type = "Unknown"
    if tier.IsPoint() is True:
        tier_type = "Point"
    elif tier.IsInterval() is True:
        tier_type = "Interval"

    # Print all information
    print(" * Tier: {:s}".format(tier.GetName()))
    print("    - Type: {:s}".format(tier_type))
    print("    - Number of annotations: {:d}".format(len(tier)))
    print("    - From time: {:.4f}".format(tier.GetBeginValue()))
    print("    - To time: {:.4f} ".format(tier.GetEndValue()))
