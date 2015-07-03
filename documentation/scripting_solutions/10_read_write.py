# ----------------------------------------------------------------------------
# Author: Brigitte Bigi
# Date: 17 avril 2015
# Brief: Open an annotated file and save it as CSV file.
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Get SPPAS API
# ----------------------------------------------------------------------------

# Tell python whereis SPPAS API
import sys
import os
from os.path import *
sys.path.append( join("..","..", "sppas", "src") )

# Import SPPAS API
import annotationdata.io


# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

inputfilename='F_F_B003-P9-merge.TextGrid'
outputfilename=inputfilename.replace('.TextGrid', '.csv')

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file, put content in a Transcription object.
trs = annotationdata.io.read(inputfilename)

# Save the Transcription object into a file.
annotationdata.io.write(outputfilename, trs)

# ----------------------------------------------------------------------------
