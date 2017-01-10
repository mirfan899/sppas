#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Tatsuya Watanabe
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
from annotationdata.transcription import Transcription
from annotationdata.tier import Tier
import annotationdata.aio


def overlaps(a1, a2):
    """
    Return True if a1 overlaps with a2.
    This means that "the localization of a with the highest score"
    of a1 overlaps "the localization of a with the highest score"
    of a2.

    @param a1 (Annotation)
    @param a2 (Annotation)

    """
    if a1.GetLocation().IsInterval():
        s1 = a1.GetLocation().GetBegin()
        e1 = a1.GetLocation().GetEnd()
    else:
        s1 = a1.GetLocation().GetPoint()
        e1 = a1.GetLocation().GetPoint()
    if a2.GetLocation().IsInterval():
        s2 = a2.GetLocation().GetBegin()
        e2 = a2.GetLocation().GetEnd()
    else:
        s2 = a2.GetLocation().GetPoint()
        e2 = a2.GetLocation().GetPoint()

    return s2 < e1 and s1 < e2


class TrsUtils(object):

    """
    Provides utility methods for Transcription instances.
    """

    @staticmethod
    def Split(transcription, ref_tier):
        """
        Split a transcription into multiple small transcriptions.

        @param transcription (Transcription)
        @param ref_tier (Tier)

        Return: list of transcription
        """
        result = []
        for a1 in ref_tier:
            if a1.GetLabel().IsEmpty():
                continue
            new_trs = Transcription(mintime=transcription.GetMaxTime())
            for tier in transcription:
                new_tier = TierUtils.Select(tier, lambda x: overlaps(a1, x))
                if new_tier is not None:
                    if new_tier[0].GetLocation().IsInterval():
                        new_tier[0].GetLocation().SetBegin( a1.GetLocation().GetBegin() )
                        new_tier[-1].GetLocation().SetEnd( a1.GetLocation().GetEnd() )
                    new_trs.Append(new_tier)

            if not new_trs.IsEmpty():
                result.append(new_trs)
        return result


    @staticmethod
    def Shift(transcription, n):
        """
        Shift all time points by n in the transcription.

        @param transcription (Transcription)
        @param n (float)

        TODO: APPLY TO ALL LOCATIONS OF EACH ANNOTATION.
        """
        n = float(n)
        if n == 0.:
            return

        for tier in transcription:
            if tier.IsInterval():
                for a in tier:
                    begin = max(0., a.GetLocation().GetBegin().GetMidpoint() + n)
                    end = a.GetLocation().GetEnd().GetMidpoint() + n
                    if end <= 0.:
                        tier.Remove(a.GetLocation().GetBegin().GetMidpoint(), a.GetLocation().GetEnd().GetMidpoint())
                    else:
                        a.GetLocation().GetBegin().SetMidpoint( begin ) #
                        a.GetLocation().GetEnd().SetMidpoint( end )
            else: # PointTier
                for a in tier:
                    time = a.GetLocation().GetPoint().GetMidpoint() + n
                    if time > 0:
                        a.GetLocation().GetPoint().SetMidpoint( time )
                    else:
                        # Remove
                        pass

        transcription.SetMinTime( max(0., transcription.GetMinTime() + n) )
        if n<0:
            transcription.SetMaxTime( transcription.GetMaxTime() + n )
        else:
            # transcription.GetMaxTime() automatically adjusts maxtime value
            transcription.SetMaxTime( transcription.GetMaxTime() )

