#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Open an annotated file and filter depending on the label.

"""

import sys
import os.path
sys.path.append(os.path.join("..", ".."))

import sppas.src.annotationdata.aio as trsaio
from sppas.src.annotationdata import Transcription
from sppas.src.annotationdata import Sel, Filter, SingleFilter


# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

filename = 'F_F_B003-P9-merge.TextGrid'
output_filename = filename.replace('.TextGrid', '.csv')

# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------


def get_tier(filename, tier_name, verbose=True):
    """ Get a tier from a file.

    :param filename: (str) Name of the annotated file.
    :param tier_name: (str) Name of the tier
    :param verbose: (bool) Print message
    :returns: (Tier)

    """
    # Read an annotated file.
    if verbose:
        print("Read file: {:s}".format(filename))
    trs = trsaio.read(filename)
    if verbose:
        print(" ... [  OK  ] ")

    # Get the expected tier
    if verbose:
        print("Get tier {:s}".format(tier_name))
    tier = trs.Find(tier_name, case_sensitive=False)
    if tier is None:
        print("Tier not found.")
        sys.exit(1)
    if verbose:
        print(" ... [  OK  ] ")

    return tier

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

if __name__ == '__main__':

    verbose = True
    tier_name = "PhonAlign"
    tier = get_tier(filename, tier_name, verbose)

    # Create a predicate on pattern 'a'"
    p1 = Sel(exact='a')

    # Create a predicate on pattern 'a' and 'e'
    p2 = Sel(icontains="a") | Sel(icontains="e")

    # Create a filter
    ftier = Filter(tier)
    f1 = SingleFilter(p1, ftier)
    f2 = SingleFilter(p2, ftier)

    # Put the annotations into tiers
    if verbose:
        print("Create a tier with 'a'")
    tier1 = f1.Filter()
    tier1.SetName('Phon-a')
    if verbose:
        print("{:s} has {:d} annotations".format(tier1.GetName(), len(tier1)))

    # solution 2: filter
    if verbose:
        print("Create a tier with 'a' and 'e'")
    tier2 = f2.Filter()
    tier2.SetName('Phon-a-e')
    if verbose:
        print("{:s} has {:d} annotations".format(tier2.GetName(), len(tier2)))

    # Save
    t = Transcription()
    t.Append(tier1)
    t.Append(tier2)
    trsaio.write(output_filename, t)
    if verbose:
        print("File {:s} saved".format(output_filename))
