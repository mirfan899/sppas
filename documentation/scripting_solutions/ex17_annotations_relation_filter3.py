#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Open an annotated file and filter to answer the following request:
               get tokens preceded by AND followed by a silence.

"""

import sys
import os.path
sys.path.append(os.path.join("..",".."))

from sppas.src.annotationdata import Sel, Rel, Filter, SingleFilter, RelationFilter
from ex15_annotations_label_filter import get_tier

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

filename = 'F_F_B003-P9-merge.TextGrid'

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file.
tier = get_tier(filename, "TokensAlign")
tier.SetRadius(0.005)

# Create filters

# all tokens, except silences
# Caution: it also includes short pauses, laugth, etc.
ft = Filter(tier)
fX = SingleFilter(~Sel(exact='#'), ft)
fY = SingleFilter(Sel(exact="#"), ft)

# Create relations (preceded by => meets) AND (followed by => metby)
relation1 = Rel('meets')
relation2 = Rel('metby')

# Create the filters
frel1 = RelationFilter(relation1, fX, fY)
frel2 = RelationFilter(relation2, frel1, fY)

# Create a filtered tier.
filtered_tier = frel2.Filter(annotformat="{x}")

# Print filtered annotations
for ann in filtered_tier:
    print("{:s}".format(ann))
