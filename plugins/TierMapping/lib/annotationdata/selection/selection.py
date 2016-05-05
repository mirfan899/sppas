#!/usr/bin/env python2
# -*- coding: utf8 -*-
#
# Copyright (C) 2013  Brigitte Bigi
#
# This file is part of SPPAS.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.


from annotationdata.utils.tierutils import TierUtils
from constraintlabel import ConstraintLabel
from constrainttime import ConstraintTime
from annotationdata.tier import Tier


def selection(tier, labels=[], modes=[], options=[], relations=[],
              minduration=0.0, maxduration=0.0,
              mintime=0.0, maxtime=0.0, delta=0.001):

    """ Create a new tier with selected items.

         Parameters:

             - labels (list of unicode) The patterns to find.
             - modes (array of SearchMode) Fix the modes search, in:
                 - MD_EXACT:      the labels must strictly correspond,
                 - MD_CONTAINS:   the label of the tier contains the given label,
                 - MD_STARTSWITH: the label of the tier starts with the given label,
                 - MD_ENDSWITH:   the label of the tier ends with the given label
                 - MD_REGEXP      Regular expression
             - options (array of strings) can contain:
                 - REVERSE          Used to reverse the result (negative search)
                 - CASE_SENSITIVE   Research parameter is case sensitive
                 - SILENCES         Replace empty labels by '#' in the result
                 - MERGE            ONLY IF ALLEN RELATIONS ARE USED
         Return:
             - a tier or None
    """
    if tier.IsEmpty():
        return None

    if maxtime == 0.0:
        maxtime = tier.GetEnd()

    newtier = TierUtils.Select(tier, ConstraintLabel(labels, modes, options))
    if newtier is None:
        return None

    newtier = TierUtils.Select(newtier, ConstraintTime(minduration=minduration,
                                                      maxduration=maxduration,
                                                      mintime=mintime,
                                                      maxtime=maxtime))

    if newtier is None:
        return None

    if "REVERSE" in options:
        reversedtier = Tier()
        for a in tier:
            match = False
            for x in newtier:
                if a.Time == x.Time:
                    match = True
            if not match:
                reversedtier.Add(a)
        newtier = reversedtier

    if "SILENCES" in options:
        for a in newtier:
            if a.Text.IsEmpty():
                a.TextValue = "#"

    return newtier
