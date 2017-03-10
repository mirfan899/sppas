#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Open an annotated file and filter depending on the duration/time.

"""

import sys
import os
from os.path import *
sys.path.append( join("..","..", "sppas", "src") )

import annotationdata.aio
from annotationdata import Transcription
from annotationdata import Sel, Filter, SingleFilter

import sys

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

filename='F_F_B003-P9-merge.TextGrid'
tiername="PhonAlign"
outputfilename=filename.replace('.TextGrid', '.csv')
verbose=True

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


# Read an annotated file.
if verbose: print "Read file: ",filename
trs = annotationdata.io.read(filename)
if verbose: print " ... [  OK  ] "

# Get the expected tier
if verbose: print "Get",tiername
tier = trs.Find(tiername, case_sensitive=False)
if tier is None:
    print "No tier", tiername, " in file ", filename
    sys.exit(1)
if verbose: print " ... [  OK  ] "

# Create filters
if verbose: print "Create predicates:"
p1 = Sel(duration_gt=0.1) & (Sel(startswith='a') | Sel(startswith='e'))
p2 = Sel(end_le=5)

# Create the tier with filtered annotations
ft = Filter(tier)
tier1 = SingleFilter(p1,ft).Filter()
if verbose: print tier1.GetName(),"has",len(tier1),"annotations."
tier2 = SingleFilter(p2,ft).Filter()
if verbose: print tier2.GetName(),"has",len(tier2),"annotations."

# both tiers will have the name: "NoName"

# Save
t = Transcription()
t.Append(tier1)
t.Append(tier2)
annotationdata.aio.write(outputfilename, t)
if verbose: print outputfilename," saved."

# ----------------------------------------------------------------------------
