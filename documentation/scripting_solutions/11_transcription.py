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
# Variables
# ----------------------------------------------------------------------------

# The input file name
filename='F_F_B003-P9-merge.TextGrid'

# The list of tiers we want to select
tiernames=['PhonAlign','TokensAlign', 'toto']

# The output file name
outputfilename='F_F_B003-P9-selection.TextGrid'


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
# Main
# ----------------------------------------------------------------------------

# Read an annotated file.
trs = annotationdata.io.read(filename)
print "Number of tiers: ",len(trs)

# Create a new Transcription to add selected tiers.
newtrs = Transcription()

# Select some tiers, add into the new Transcription
for name in tiernames:
    tier = trs.Find(name, case_sensitive=False)
    if tier is not None:
        newtrs.Append( tier )
        print "Tier ",tier.GetName(),"successfully added."
    else:
        print "Error: the file does not contain a tier with name =",name

# Save the Transcription into a file.
annotationdata.io.write(outputfilename, newtrs)

# ----------------------------------------------------------------------------
