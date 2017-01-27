#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Open an annotated file and print information about tiers.
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

filename='F_F_B003-P9-merge.TextGrid'

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file.
trs = aio.read(filename)

for tier in trs:

    # Get the tier type
    if tier.IsPoint() is True:
       tiertype = "Point"
    elif tier.IsInterval() is True:
       tiertype = "Interval"
    else:
        tiertype = "Unknown"

    # Print all informations
    print(" * Name: {:s}".format(tier.GetName()))
    print("    - Type: {:s}".format(tiertype))
    print("    - Number of annotations: {:d}".format(len(tier)))
    print("    - From time: {:.4f}".format(tier.GetBeginValue()))
    print("    - To time: {:.4f} ".format(tier.GetEndValue()))

# ----------------------------------------------------------------------------
