#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Open an annotated file and filter to answer the following request:
               get tokens just followed by a silence.
"""

import sys
import os.path
sys.path.append(os.path.join("..", ".."))

from sppas.src.annotationdata import Sel, Rel, Filter, SingleFilter, RelationFilter
from ex15_annotations_label_filter import get_tier

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

filename = 'F_F_B003-P9-merge.TextGrid'

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

tier = get_tier(filename, "TokensAlign")

# Create filters
ft = Filter(tier)
fX = SingleFilter(~Sel(exact='#'), ft)
fY = SingleFilter(Sel(exact="#"), ft)

# Create relations
relation = Rel('meets')

# Create the filter
frel = RelationFilter(relation, fX, fY)

# Create a tier
filtered_tier = frel.Filter()

# Print filtered annotations
for ann in filtered_tier:
    print("{:s}".format(ann))
