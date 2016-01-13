#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
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


from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation
from annotationdata.tier import Tier
from annotationdata.transcription import Transcription


def fill_gaps(tier):
    """ Fill the temporal gaps between annotations.
        Parameters:
            - tier
        Exception:   none
        Return:      Tier
    """
    new_tier = tier.Copy()
    prev = None
    for a in new_tier:
        if prev and prev.End < a.Begin:
            time = TimeInterval(TimePoint(prev.EndValue),
                                TimePoint(a.BeginValue))
            annotation = Annotation(time)
            new_tier.Add(annotation)
            prev = annotation
        else:
            prev = a
    return new_tier

# End fill_gaps
# ------------------------------------------------------------------------


def merge_overlapping_annotations(tier, separator=' '):
    """ Merge overlapping annotations to one annotation in the given tier.
        The values of the labels are concatenated.
        Parameters:
            - tier
        Exception:   none
        Return:      Tier
    """
    new_tier = Tier(tier.Name)
    prev = None
    for a in tier:
        # test whether prev overlaps with a
        if prev and prev.Begin < a.End and a.Begin < prev.End:
            prev.TextValue += separator + a.TextValue
            prev.EndValue = a.EndValue
        else:
            new_tier.Append(a)
            prev = a
    return new_tier

# End merge_overlapping_annotations
# ------------------------------------------------------------------------
