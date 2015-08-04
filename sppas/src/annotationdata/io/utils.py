#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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

from annotationdata.ptime.point    import TimePoint
from annotationdata.label.label    import Label
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.interval import TimePoint
from annotationdata.annotation     import Annotation
from annotationdata.tier           import Tier

import random
import string

# ---------------------------------------------------------------------------

def random_char(y, lowercase=True):
    if lowercase:
        return ''.join(random.choice(string.ascii_lowercase) for x in range(y))
    return ''.join(random.choice(string.ascii_letters) for x in range(y))

def random_int(y):
    return ''.join(str(random.randint(0,9)) for x in range(y))

# ---------------------------------------------------------------------------

def indent(elem, level=0):
    """
    pretty indent.
    http://effbot.org/zone/element-lib.htm#prettyprint
    """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# End indent
# -----------------------------------------------------------------

def gen_id( ):
    """
    Generate a unique ID.
    """
    s = ''
    s += random_int(1)
    s += random_char(1)
    s += random_int(3)
    s += random_char(1)
    s += random_int(1)
    s += random_char(1)
    s += "-"
    s += random_int(1)
    s += random_char(1)
    s += random_int(2)
    s += "-"
    s += random_int(1)
    s += random_char(1)
    s += random_int(2)
    s += "-"
    s += random_int(1)
    s += random_char(2)
    s += random_int(1)
    s += "-"
    s += random_int(4)
    s += random_char(2)
    s += random_int(1)
    s += random_char(1)
    s += random_int(3)
    s += random_char(1)

    return s

# End gen_id
# -----------------------------------------------------------------

def format_float( f ):
    return round(float(f),4)

# End format_float
# -----------------------------------------------------------------

def fill_gaps(tier, mintime, maxtime):
    """
    Return the tier in which the temporal gaps between annotations are filled with an un-labelled annotation.

    @param tier: (Tier)

    """

    new_tier = tier.Copy()
    prev = None

    if mintime is not None and format_float(tier.GetBeginValue()) > format_float(mintime):
        time = TimeInterval(TimePoint(mintime), TimePoint(tier.GetBeginValue()))
        annotation = Annotation(time)
        new_tier.Add(annotation)

    for a in new_tier:
        if prev is not None and prev.GetLocation().GetEnd() < a.GetLocation().GetBegin():
            time = TimeInterval(TimePoint(prev.GetLocation().GetEndMidpoint()), TimePoint(a.GetLocation().GetBeginMidpoint()))
            annotation = Annotation(time)
            new_tier.Add(annotation)
            prev = annotation
        else:
            prev = a

    if maxtime is not None and format_float(tier.GetEndValue()) < format_float(maxtime):
        time = TimeInterval(TimePoint(tier.GetEndValue()), TimePoint(maxtime))
        annotation = Annotation(time)
        new_tier.Add(annotation)

    return new_tier

# End fill_gaps
# ------------------------------------------------------------------------

def merge_overlapping_annotations(tier, separator=' '):
    """
    Merge overlapping annotations.
    The values of the labels are concatenated.

    Do not pay attention to alternatives.

    @param tier: (Tier)
    @return Tier

    """
    if tier.IsInterval() is False:
        return tier

    new_tier = Tier(tier.GetName())
    prev = None

    for a in tier:

        if prev is None:
            new_tier.Append(a)
            prev = a
            continue

        # test whether prev overlaps with a
        #if prev and prev.Begin < a.End and a.Begin < prev.End:
            # Interval containing both prev and a
            #prev.TextValue += separator + a.TextValue
            #prev.EndValue = max((prev.EndValue, a.EndValue))

        if a.GetLocation().GetBegin() < prev.GetLocation().GetBegin():
            # TODO
            # it happens if more than 2 annotations are starting at the same time
            #print "IGNORED: ",a
            continue

        # a is after prev: normal.
        if a.GetLocation().GetBegin() >= prev.GetLocation().GetEnd():
            new_tier.Append(a)
            prev = a

        # prev and a start at the same time
        elif a.GetLocation().GetBegin() == prev.GetLocation().GetBegin():

            if a.GetLocation().GetEnd() > prev.GetLocation().GetEnd():
                a.GetLocation().SetBegin( prev.GetLocation().GetEnd() )
                prev.GetLabel().SetValue( prev.GetLabel().GetValue() + separator + a.GetLabel().GetValue())
                new_tier.Append(a)
                prev = a

            elif a.GetLocation().GetEnd() < prev.GetLocation().GetEnd():
                a2 = Annotation(TimeInterval(a.GetLocation().GetEnd(),prev.GetLocation().GetEnd()),Label(prev.GetLabel().GetValue()))
                prev.GetLocation().SetEnd( a.GetLocation().GetEnd() )
                prev.GetLabel().SetValue( prev.GetLabel().GetValue() + separator + a.GetLabel().GetValue())
                new_tier.Append(a2)
                prev = a2

            else:
                prev.GetLabel().SetValue( prev.GetLabel().GetValue() + separator + a.GetLabel().GetValue())

        # a starts inside prev
        elif a.GetLocation().GetBegin() < prev.GetLocation().GetEnd():

            if a.GetLocation().GetEnd() < prev.GetLocation().GetEnd():
                a2 = Annotation(TimeInterval(a.GetLocation().GetEnd(),prev.GetLocation().GetEnd()),Label(prev.GetLabel().GetValue()))
                a.GetLabel().SetValue( a.GetLabel().GetValue() + separator + prev.GetLabel().GetValue() )
                prev.GetLocation().SetEnd( a.GetLocation().GetBegin() )
                new_tier.Append(a)
                new_tier.Append(a2)
                prev = a2

            elif a.GetLocation().GetEnd() > prev.GetLocation().GetEnd():
                a2 = Annotation(TimeInterval(a.GetLocation().GetBegin(),prev.GetLocation().GetEnd()),Label(prev.GetLabel().GetValue() + separator + a.GetLabel().GetValue()))
                prev.GetLocation().SetEnd( a2.GetLocation().GetBegin() )
                a.GetLocation().SetBegin(  a2.GetLocation().GetEnd() )
                new_tier.Append(a2)
                new_tier.Append(a)
                prev = a

            else:
                a.GetLabel().SetValue( a.GetLabel().GetValue() + separator + prev.GetLabel().GetValue() )
                prev.GetLocation().SetEnd( a.GetLocation().GetBegin() )
                new_tier.Append(a)
                prev = a

    return new_tier

# End merge_overlapping_annotations
# ------------------------------------------------------------------------

def point2interval(tier, fixradius=None):
    """
    Convert localization.
    Ensure the radius to be always >= 1 millisecond.

    Do not convert alternatives.

    @param tier: (Tier)
    @return Tier

    """
    if tier.IsInterval():
        return tier.Copy()

    new_tier = Tier(tier.GetName())
    new_tier.metadata = tier.metadata
    new_tier.SetMedia( tier.GetMedia() )
    new_tier.SetCtrlVocab( tier.GetCtrlVocab() )
    new_tier.SetDataType( tier.GetDataType() )
    #new_tier.SetTranscription( tier.GetTranscription() ) # no need
    new_tier.metadata['TIER_TYPE']="TimePoint"

    for a in tier:
        # get point with the best score for this annotation
        point = a.GetLocation().GetPoint()
        midpoint = point.GetMidpoint()
        radius = fixradius if fixradius is not None else point.GetRadius()
        if radius < 0.001:
            radius = 0.001

        begin = TimePoint(midpoint-radius,radius)
        end   = TimePoint(midpoint+radius,radius)

        new_a=Annotation(TimeInterval(begin,end),Label(a.GetLabel().GetValue()))
        new_a.metadata = a.metadata
        new_tier.Append( new_a )

    return new_tier

# ------------------------------------------------------------------------
