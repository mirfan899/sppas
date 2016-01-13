# ----------------------------------------------------------------------------
# Author: Brigitte Bigi
# Date: 17 avril 2015
# Brief: Open an annotated file and print information about tiers.
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Get SPPAS API
# ----------------------------------------------------------------------------

import sys
import os
from os.path import *
sys.path.append( join("..","..", "sppas", "src") )

import annotationdata.io
from annotationdata import Transcription


# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

filename='F_F_B003-P9-merge.TextGrid'


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


# Read an annotated file.
trs = annotationdata.io.read(filename)

for tier in trs:

    # Get the tier type
    if tier.IsPoint() is True:
       tiertype = "Point"
    elif tier.IsInterval() is True:
       tiertype = "Interval"
    else:
        tiertype = "Unknown"

    # Print all informations
    print " * Name: ", tier.GetName()
    print "    - Type: ", tiertype
    print "    - Number of annotations: ", len(tier)
    print "    - From time: ", tier.GetBegin()
    print "    - To time: ", tier.GetEnd()

# ----------------------------------------------------------------------------
