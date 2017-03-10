#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Open an annotated file and filter depending on the label.

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

# Create a filter
if verbose: print "Create a predicate on pattern 'a'"
p1 = Sel(exact='a')

if verbose: print "Create a predicate on pattern 'a' and 'e'"
p2 = Sel(icontains="a") | Sel(icontains="e")

ftier = Filter(tier)
f1 = SingleFilter(p1, ftier)
f2 = SingleFilter(p2, ftier)

# Put the annotations into tiers
if verbose: print "Create a tier with 'a'"
tier1 = f1.Filter()
tier1.SetName('Phon-a')
if verbose: print tier1.GetName(),"has",len(tier1),"annotations."

# solution 2: filter
if verbose: print "Create a tier with 'a' and 'e'"
tier2 = f2.Filter()
tier2.SetName('Phon-a-e')
if verbose: print tier2.GetName(),"has",len(tier2),"annotations."

# Save
t = Transcription()
t.Append(tier1)
t.Append(tier2)
annotationdata.aio.write(outputfilename, t)
if verbose: print outputfilename," saved."

# ----------------------------------------------------------------------------
