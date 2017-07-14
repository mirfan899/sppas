#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Open an annotated file and filter to answer the following request:
               get tokens either preceded by OR followed by a silence.
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

# Read an annotated file.
tier = get_tier(filename, "TokensAlign")
tier.SetRadius(0.005)

# Create filters

# all tokens, except silences
# Caution: it also includes short pauses, laught, etc.
# Create filters
ft = Filter(tier)
fX = SingleFilter(~Sel(exact='#'), ft)
fY = SingleFilter(Sel(exact="#"), ft)

# Create relations (preceded by => meets) OR (followed by => metby)
relation = Rel('meets') | Rel('metby')

# Create the filter
frel = RelationFilter(relation, fX, fY)

# Create a tier with relations meets OR met by.
# Replace the label of the token by the name of the relation
# If both relations are true, relation' names are concatenated.
filtered_tier = frel.Filter(annotformat="{rel}")

# Print filtered annotations
for ann in filtered_tier:
    print("{:s}".format(ann))
