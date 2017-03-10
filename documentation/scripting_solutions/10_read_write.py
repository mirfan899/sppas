#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Open an annotated file and save it as CSV file.

""" 

# Tell python whereis SPPAS API
import sys
import os
from os.path import *
sys.path.append( join("..","..", "sppas", "src") )

# Import SPPAS API
import annotationdata.aio


# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

inputfilename='F_F_B003-P9-merge.TextGrid'
outputfilename=inputfilename.replace('.TextGrid', '.csv')

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file, put content in a Transcription object.
trs = annotationdata.aio.read(inputfilename)

# Save the Transcription object into a file.
annotationdata.aio.write(outputfilename, trs)

# ----------------------------------------------------------------------------
