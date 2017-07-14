#!/usr/bin python2
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Open an annotated file and save it as CSV file.

""" 
import sys
import os.path
SPPAS_IS_HERE = os.path.join("..", "..")
sys.path.append(SPPAS_IS_HERE)

import sppas.src.annotationdata.aio as trsaio

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

input_filename = 'F_F_B003-P9-merge.TextGrid'
output_filename = input_filename.replace('.TextGrid', '.csv')

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

if __name__ == '__main__':

    # Read an annotated file, put content in a Transcription object.
    trs = trsaio.read(input_filename)

    # Save the Transcription object into a file.
    trsaio.write(output_filename, trs)
