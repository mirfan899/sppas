#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
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
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: tierutils.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------

from annotationdata.tier import Tier
from annotationdata.annotation import Annotation
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.label.label import Label

# ---------------------------------------------------------------------------

DEFAULT_SEP = ["sil", "#", "+", "@@", "gb", "*", "dummy"]

# ---------------------------------------------------------------------------


def align2phon(aligntier, separators=DEFAULT_SEP):
    """
    Return the phonetization of a time-aligned tier.

    """
    phontier = Tier("Phonetization")
    b = TimePoint(aligntier.GetBegin().GetMidpoint())
    e = b
    l = ""
    for ann in aligntier:
        if ann.GetLabel().IsSilence() is True or ann.GetLabel().GetValue() in separators:
            if len(l) > 0 and e > b:
                at = Annotation(TimeInterval(b, e), Label(l))
                phontier.Add(at)
            phontier.Add(ann)
            b = ann.GetLocation().GetEnd()
            e = b
            l = ""
        else:
            e = ann.GetLocation().GetEnd()
            label = ann.GetLabel().GetValue()
            if ann.GetLabel().IsEmpty() is False:
                l = l + " " + label

    if e > b:
        ann = aligntier[-1]
        label = ann.GetLabel().GetValue()
        l = label.replace("-", " ")
        at = Annotation(TimeInterval(b, e), Label(l))
        phontier.Add(at)

    return phontier
