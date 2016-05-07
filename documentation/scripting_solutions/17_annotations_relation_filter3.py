#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Open an annotated file and filter to answer the following request:
               get tokens preceded by AND followed by a silence.

"""

import sys
import os
from os.path import *
sys.path.append( join("..","..", "sppas", "src") )

import annotationdata.io
from annotationdata import Transcription
from annotationdata import Sel, Rel, Filter, SingleFilter, RelationFilter

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

filename='F_F_B003-P9-merge.TextGrid'

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file.
trs = annotationdata.io.read(filename)

# Get the expected tier
tier = trs.Find("TokensAlign", case_sensitive=False)
if tier is None:
    print "No tier", tiername, " in file ", filename
    sys.exit(1)

# Fix a radius, just to be sure that relations will be efficient!
tier.SetRadius(0.005)

# Create filters

# all tokens, except silences
# Caution: it also includes short pauses, laught, etc.
ft = Filter(tier)
fX = SingleFilter(~Sel(exact='#'),ft)
fY = SingleFilter(Sel(exact="#"),ft)

# Create relations (preceded by => meets) AND (followed by => metby)
relation1 = Rel('meets')
relation2 = Rel('metby')

# Create the filters
frel1 = RelationFilter(relation1,fX,fY)
frel2 = RelationFilter(relation2,frel1,fY)

# Create a filtered tier.
filteredtier = frel2.Filter(replace=False)

# Print filtered annotations
for ann in filteredtier:
    print ann

# ----------------------------------------------------------------------------
