#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Open an annotated file and filter depending on the duration/time.

"""

import sys
import os.path
sys.path.append(os.path.join("..", ".."))

import sppas.src.annotationdata.aio as trsaio
from sppas.src.annotationdata import Transcription
from sppas.src.annotationdata import Sel, Filter, SingleFilter
from ex15_annotations_label_filter import get_tier

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

filename = 'F_F_B003-P9-merge.TextGrid'
tier_name = "PhonAlign"
output_filename = filename.replace('.TextGrid', '.csv')
verbose = True

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

if __name__ == '__main__':

    tier = get_tier(filename, tier_name, verbose)

    # Create predicates
    p1 = Sel(duration_gt=0.1) & (Sel(startswith='a') | Sel(startswith='e'))
    p2 = Sel(end_le=5)

    # Create the tier with filtered annotations
    ft = Filter(tier)
    tier1 = SingleFilter(p1, ft).Filter()
    if verbose:
        print("{:s} has {:d} annotations".format(tier1.GetName(), len(tier1)))
    tier2 = SingleFilter(p2, ft).Filter()
    if verbose:
        print("{:s} has {:d} annotations".format(tier2.GetName(), len(tier2)))
    # both tiers will have the name

    # Save
    t = Transcription()
    t.Append(tier1)
    t.Append(tier2)  # tier is automatically renamed with "-2" at the end of the name
    trsaio.write(output_filename, t)
    if verbose:
        print("File {:s} saved".format(output_filename))
