#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Open an annotated file and filter to answer the following request:
               get tokens followed by a silence.
"""

import sys
import os.path
sys.path.append(os.path.join("..",".."))

import sppas.src.annotationdata.aio as aio
from sppas.src.annotationdata import Transcription
from sppas.src.annotationdata import Sel, Rel, Filter, SingleFilter, RelationFilter

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

filename='F_F_B003-P9-merge.TextGrid'

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file.
trs = aio.read(filename)

# Get the expected tier
tier = trs.Find("TokensAlign", case_sensitive=False)
if tier is None:
    print "No tier", tiername, " in file ", filename
    sys.exit(1)

tier.SetRadius(0.005)

# Create filters
ft = Filter(tier)
fX = SingleFilter(~Sel(exact='#'),ft)
fY = SingleFilter(Sel(exact="#"),ft)

# print the list of silences:
#for a in fY.Filter():
#    print a

# Create relations
relation = Rel('meets')

# Create the filter
frel = RelationFilter(relation,fX,fY)

# Create a tier
filteredtier = frel.Filter()

# Print filtered annotations
for ann in filteredtier:
    print ann

# ----------------------------------------------------------------------------
